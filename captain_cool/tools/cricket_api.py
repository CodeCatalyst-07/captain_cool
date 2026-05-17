"""
captain_cool.tools.cricket_api
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Fetches live match state from the **CricketData.org** free-tier REST API
(100 calls / day) and normalises the response into a flat, agent-friendly
dict.

Also exposes ``cricket_tool_declaration`` — a Gemini
``FunctionDeclaration`` that lets the ADK orchestrator call
:func:`get_live_cricket_state` as a tool.

Free-tier endpoint used
------------------------
``GET https://api.cricketdata.org/api/v1/match_info``

Query parameters
~~~~~~~~~~~~~~~~
- ``apikey`` — CricketData.org API key (from settings)
- ``id``     — match UUID supplied by the caller
"""

from __future__ import annotations

import logging
from typing import Any

import requests
from google.genai import types as genai_types

from captain_cool.config.settings import CRICKETDATA_API_KEY, CRICKETDATA_BASE_URL

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Network constants
# ---------------------------------------------------------------------------

_TIMEOUT_SECONDS: int = 10
"""Hard timeout for every outbound HTTP request."""

_MATCH_INFO_PATH: str = "/match_info"
"""Path segment appended to CRICKETDATA_BASE_URL."""


# ---------------------------------------------------------------------------
# Public function
# ---------------------------------------------------------------------------


def get_live_cricket_state(match_id: str) -> dict[str, Any]:
    """Fetch and normalise the live state of a CricketData.org match.

    Calls the free-tier ``match_info`` endpoint and extracts the fields
    that the captain-cool agents care about.  On any network or API
    error the function returns an *error dict* (never raises) so that
    agents can handle degraded data gracefully.

    Parameters
    ----------
    match_id:
        The CricketData.org UUID for the match (e.g.
        ``"a3e1f2c0-1234-5678-abcd-ef0123456789"``).

    Returns
    -------
    dict
        On success, a dict with the following keys:

        - ``match_id`` (str) — echoed back for traceability
        - ``status`` (str) — e.g. ``"Live"``, ``"Result"``
        - ``teams`` (list[str]) — the two competing teams
        - ``score`` (str) — current score string, e.g. ``"245/6"``
        - ``overs`` (float) — overs completed
        - ``wickets`` (int) — wickets fallen in the current innings
        - ``batting_team`` (str) — team currently batting
        - ``bowling_team`` (str) — team currently bowling
        - ``current_batsmen`` (list[dict]) — each with ``name`` and ``runs``
        - ``current_bowler`` (dict) — ``name`` and ``overs`` bowled
        - ``required_run_rate`` (float) — RRR for chasing team (0.0 if N/A)
        - ``current_run_rate`` (float) — CRR for batting team

        On failure, a dict with a single ``"error"`` key and a
        human-readable message string.
    """
    url = f"{CRICKETDATA_BASE_URL}{_MATCH_INFO_PATH}"
    params: dict[str, str] = {"apikey": CRICKETDATA_API_KEY, "id": match_id}

    try:
        response = requests.get(url, params=params, timeout=_TIMEOUT_SECONDS)
        response.raise_for_status()
        payload: dict[str, Any] = response.json()
    except requests.exceptions.Timeout:
        logger.warning("CricketData request timed out for match_id=%s", match_id)
        return {"error": f"Request timed out after {_TIMEOUT_SECONDS}s (match_id={match_id})"}
    except requests.exceptions.HTTPError as exc:
        logger.error("CricketData HTTP error: %s", exc)
        return {"error": f"HTTP {exc.response.status_code}: {exc.response.text[:200]}"}
    except requests.exceptions.RequestException as exc:
        logger.error("CricketData network error: %s", exc)
        return {"error": f"Network error: {exc}"}

    # CricketData wraps everything under a top-level "data" key when the
    # request succeeds; the presence of "status" == "failure" signals an
    # API-level error (e.g. bad key, unknown match id).
    if payload.get("status") == "failure":
        reason = payload.get("reason", "Unknown API error")
        logger.warning("CricketData API error for match_id=%s: %s", match_id, reason)
        return {"error": f"CricketData API error: {reason}"}

    data: dict[str, Any] = payload.get("data", {})

    # ------------------------------------------------------------------
    # Score / innings extraction
    # CricketData nests innings under data["score"] as a list of dicts.
    # We pick the *last* element which represents the current innings.
    # ------------------------------------------------------------------
    score_entries: list[dict[str, Any]] = data.get("score", [])
    current_innings: dict[str, Any] = score_entries[-1] if score_entries else {}

    raw_score: str = (
        f"{current_innings.get('r', 0)}/{current_innings.get('w', 0)}"
    )
    overs_completed: float = float(current_innings.get("o", 0.0))
    wickets_fallen: int = int(current_innings.get("w", 0))

    # ------------------------------------------------------------------
    # Team identification
    # ------------------------------------------------------------------
    team_info: list[dict[str, Any]] = data.get("teamInfo", [])
    teams: list[str] = [t.get("name", "Unknown") for t in team_info]

    batting_team: str = current_innings.get("inning", "").split(" Inning")[0].strip()
    # Derive bowling team as the *other* team
    bowling_team: str = next(
        (t for t in teams if t != batting_team), "Unknown"
    )

    # ------------------------------------------------------------------
    # Current batsmen — CricketData returns them under data["players"]
    # filtered by role "bat" and status "not out".
    # ------------------------------------------------------------------
    all_players: list[dict[str, Any]] = data.get("players", [])
    current_batsmen: list[dict[str, str | int]] = [
        {"name": p.get("name", ""), "runs": int(p.get("r", 0))}
        for p in all_players
        if p.get("role") == "bat" and p.get("dismissal", "") == ""
    ][:2]  # maximum two batsmen at the crease

    # ------------------------------------------------------------------
    # Current bowler — first player with role "bowl" and overs > 0
    # ------------------------------------------------------------------
    current_bowler_raw: dict[str, Any] = next(
        (p for p in all_players if p.get("role") == "bowl" and float(p.get("o", 0)) > 0),
        {},
    )
    current_bowler: dict[str, str | float] = {
        "name": current_bowler_raw.get("name", "Unknown"),
        "overs": float(current_bowler_raw.get("o", 0.0)),
    }

    # ------------------------------------------------------------------
    # Run rates — CricketData may or may not include these directly.
    # Fall back to computing CRR from score/overs when absent.
    # ------------------------------------------------------------------
    rrr: float = float(data.get("rrr", 0.0))
    crr: float = (
        float(data.get("crr", 0.0))
        or (
            round(int(current_innings.get("r", 0)) / overs_completed, 2)
            if overs_completed > 0
            else 0.0
        )
    )

    return {
        "match_id": match_id,
        "status": data.get("status", "Unknown"),
        "teams": teams,
        "score": raw_score,
        "overs": overs_completed,
        "wickets": wickets_fallen,
        "batting_team": batting_team,
        "bowling_team": bowling_team,
        "current_batsmen": current_batsmen,
        "current_bowler": current_bowler,
        "required_run_rate": rrr,
        "current_run_rate": crr,
    }


# ---------------------------------------------------------------------------
# Gemini FunctionDeclaration
# ---------------------------------------------------------------------------

cricket_tool_declaration = genai_types.FunctionDeclaration(
    name="get_live_cricket_state",
    description=(
        "Fetches the live state of a cricket match from CricketData.org. "
        "Returns current score, run rates, batting and bowling sides, and "
        "individual player information."
    ),
    parameters=genai_types.Schema(
        type=genai_types.Type.OBJECT,
        properties={
            "match_id": genai_types.Schema(
                type=genai_types.Type.STRING,
                description=(
                    "The CricketData.org UUID for the match "
                    "(e.g. 'a3e1f2c0-1234-5678-abcd-ef0123456789')."
                ),
            )
        },
        required=["match_id"],
    ),
)
"""Gemini ``FunctionDeclaration`` for :func:`get_live_cricket_state`."""
