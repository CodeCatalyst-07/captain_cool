"""
captain_cool.api.server
~~~~~~~~~~~~~~~~~~~~~~~~

FastAPI application exposing the captain-cool debate engine over HTTP.

Endpoints
---------
GET  /api/health          — Liveness check
POST /api/strategy        — Run the 5-round agent debate and return results

The server is designed to be run with::

    uvicorn captain_cool.api.server:app --reload --port 8000

from the project root (captain-cool/).
"""

from __future__ import annotations

import logging
import traceback
import uuid
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from captain_cool.orchestrator import run_debate
from captain_cool.config.settings import GEMINI_API_KEY, GEMINI_MODEL

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Captain Cool API",
    description="IPL multi-agent tactical debate engine powered by Gemini + ADK",
    version="1.0.0",
)

# Allow all origins so the Vite dev server (localhost:5173) can talk to
# the FastAPI server (localhost:8000) without CORS errors.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------


class StrategyRequest(BaseModel):
    """Incoming match state from the React frontend."""

    innings: int = Field(default=1, ge=1, le=2, description="Current innings (1 or 2)")
    over: int = Field(default=0, ge=0, le=20, description="Current over number (0-based)")
    score: str = Field(default="0/0", description='Score string, e.g. "134/4"')
    batting_team: str = Field(default="", description="Name/code of batting team")
    bowling_team: str = Field(default="", description="Name/code of bowling team")
    striker: str = Field(default="", description="Batsman on strike")
    non_striker: str = Field(default="", description="Batsman at non-striker's end")
    bowlers_remaining: str = Field(
        default="",
        description='Comma-separated bowler:overs_left, e.g. "Bumrah:2,Chahar:3"',
    )
    pitch_type: str = Field(default="Flat", description="Pitch type (Flat/Sticky/Dusty/Green)")
    dew_factor: bool = Field(default=False, description="Dew expected? True = high dew risk")
    venue: str = Field(default="", description="Venue / city name for weather lookup")
    target: int = Field(default=0, ge=0, description="Target runs (0 if first innings)")
    impact_player_available: bool = Field(default=False, description="Impact Player substitution still available")
    cricbuzz_url: str = Field(default="", description="Optional Cricbuzz match URL for context")

    model_config = {"json_schema_extra": {"example": {
        "innings": 1,
        "over": 14,
        "score": "134/4",
        "batting_team": "MI",
        "bowling_team": "CSK",
        "striker": "Hardik Pandya",
        "non_striker": "Tilak Varma",
        "bowlers_remaining": "Bumrah:2,Chahar:3",
        "pitch_type": "Flat",
        "dew_factor": True,
        "venue": "Wankhede Stadium Mumbai",
        "target": 0,
        "impact_player_available": True,
        "cricbuzz_url": "",
    }}}


class StrategyResponse(BaseModel):
    """Structured result returned to the frontend after the debate."""

    stats_summary: str
    initial_proposal: str
    devils_challenge: str
    final_decision: str
    commentary: str
    win_probability_before: dict[str, Any]
    win_probability_after: dict[str, Any]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_score(score_str: str) -> tuple[int, int]:
    """Parse a score string like '134/4' into (runs, wickets).

    Falls back to (0, 0) on any parsing error so the API never crashes on
    unexpected input from the frontend.
    """
    try:
        parts = score_str.split("/")
        runs = int(parts[0].strip())
        wickets = int(parts[1].strip()) if len(parts) > 1 else 0
        return runs, wickets
    except (ValueError, IndexError):
        logger.warning("Could not parse score string: %r — defaulting to 0/0", score_str)
        return 0, 0


def _parse_bowlers_remaining(raw: str) -> dict[str, float]:
    """Parse 'Bumrah:2,Chahar:3' into {'Bumrah': 2.0, 'Chahar': 3.0}."""
    result: dict[str, float] = {}
    for token in raw.split(","):
        token = token.strip()
        if ":" in token:
            name, overs = token.split(":", 1)
            try:
                result[name.strip()] = float(overs.strip())
            except ValueError:
                pass
    return result


def _build_match_state(req: StrategyRequest) -> dict[str, Any]:
    """Map the frontend request payload to the match_state dict that
    ``run_debate`` expects.

    The orchestrator's ``compute_win_probability`` calls need:
    - target, runs, wickets, overs, dew_risk, batting_depth_rating

    Everything else is passed through as extra context so the agents
    have full situational awareness.
    """
    runs, wickets = _parse_score(req.score)

    # Dew risk: boolean from the frontend mapped to the three-level enum
    dew_risk: str
    if req.dew_factor:
        dew_risk = "high"
    else:
        dew_risk = "low"

    # Batting depth: derived from wickets in hand on a 0–10 scale
    # (10 - wickets) gives wickets remaining; scale to 0–10 directly
    batting_depth_rating: float = float(max(0, 10 - wickets))

    # Synthesise a match ID — we don't have a real CricketData UUID from the
    # form, so generate a readable one.  Agents that call get_live_cricket_state
    # will attempt the API call; if it fails, they fall back to form context.
    match_id: str = f"FORM-{req.batting_team}-vs-{req.bowling_team}-{uuid.uuid4().hex[:6]}"

    return {
        # ── Core fields consumed by compute_win_probability ──────────────
        "match_id": match_id,
        "venue": req.venue,
        "target": int(req.target),        # runs to win (0 in 1st innings)
        "runs": runs,                      # parsed from score string
        "wickets": wickets,                # parsed from score string
        "overs": float(req.over),          # overs completed (whole number from form)
        "dew_risk": dew_risk,              # "high" | "medium" | "low"
        "batting_depth_rating": batting_depth_rating,
        # ── Match identification & phase ─────────────────────────────────
        "innings": int(req.innings),       # 1 or 2
        "over": int(req.over),             # current over (redundant alias kept for agents)
        "score": req.score,                # "134/4" — raw display string
        "batting_team": req.batting_team,
        "bowling_team": req.bowling_team,
        # ── Batting & bowling personnel ───────────────────────────────────
        "striker": req.striker,
        "non_striker": req.non_striker,
        "bowlers_remaining": _parse_bowlers_remaining(req.bowlers_remaining),
        "bowlers_remaining_raw": req.bowlers_remaining,
        # ── Pitch & conditions ────────────────────────────────────────────
        "pitch_type": req.pitch_type,
        "dew_factor": req.dew_factor,
        "impact_player_available": req.impact_player_available,
        "cricbuzz_url": req.cricbuzz_url,
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/api/health", summary="Health check")
async def health() -> dict[str, str]:
    """Returns ``{"status": "ok"}`` when the server is running."""
    return {"status": "ok"}


@app.get("/api/test", summary="Gemini API smoke test (no ADK)")
async def test_gemini() -> JSONResponse:
    """Make a minimal Gemini generate_content call to confirm the API key works
    completely independently of ADK.  Returns the model's response text.
    """
    try:
        from google.genai import Client

        client = Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents="Say exactly: CAPTAIN COOL API KEY OK",
        )
        reply = response.text.strip() if response.text else "(no text returned)"
        return JSONResponse({"status": "ok", "gemini_reply": reply})
    except Exception as exc:
        tb = traceback.format_exc()
        logger.error("Gemini smoke test failed:\n%s", tb)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": str(exc), "traceback": tb},
        )


@app.post(
    "/api/strategy",
    response_model=StrategyResponse,
    summary="Run the captain-cool 5-round agent debate",
)
async def get_strategy(body: StrategyRequest) -> StrategyResponse:
    """Accept a match-state payload and run the full 5-round debate.

    The endpoint is async and typically takes 30–90 seconds depending on
    Gemini response times.

    Returns
    -------
    StrategyResponse
        All five round outputs plus win-probability before/after.
    """
    match_state = _build_match_state(body)
    logger.info(
        "Strategy request: %s vs %s, over=%s, score=%s",
        body.batting_team,
        body.bowling_team,
        body.over,
        body.score,
    )

    try:
        result: dict[str, Any] = await run_debate(match_state)
    except Exception as exc:
        tb = traceback.format_exc()
        logger.error("run_debate raised an exception:\n%s", tb)
        # Return the full traceback in the JSON body so the frontend / curl
        # can display exactly what went wrong without needing server log access.
        return JSONResponse(
            status_code=500,
            content={
                "detail": f"Agent debate failed: {exc!s}",
                "error_type": type(exc).__name__,
                "traceback": tb,
            },
        )

    return StrategyResponse(**result)


# ---------------------------------------------------------------------------
# Entry point for direct uvicorn invocation
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("captain_cool.api.server:app", host="0.0.0.0", port=8000, reload=True)
