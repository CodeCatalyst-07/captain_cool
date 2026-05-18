"""
captain_cool.orchestrator
~~~~~~~~~~~~~~~~~~~~~~~~~~

The debate engine for captain-cool.

:func:`run_debate` drives a **5-round sequential debate** between four
specialised ADK agents and returns a structured result dict that the Gradio
UI and tests can consume directly.

Round-by-round flow
-------------------
1. **StatsAnalyst** — fetches live match + weather data, emits JSON summary
2. **Strategist**   — reads summary, calls win-probability tool, proposes
   tactical decision
3. **DevilsAdvocate** — challenges the proposal with exactly 2 objections
4. **Strategist** (second turn) — defends or revises against the challenges
5. **Commentator**  — narrates the final decision as live commentary

Context threading
-----------------
Each round's full output is appended to a running ``transcript`` string,
which is prepended to the next round's user message.  This keeps every
agent fully informed without requiring a shared session between agents.

Win-probability bookending
--------------------------
``compute_win_probability`` is called directly (not via an agent) before
Round 1 and after Round 4 to capture the probability delta that the
Strategist's decision is expected to cause.  The Strategist agent may call
the same function internally with revised parameters; the orchestrator's
direct calls use the raw ``match_state`` values for consistency.
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Any

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from captain_cool.agents.commentator import commentator_agent
from captain_cool.agents.devils_advocate import devils_advocate_agent
from captain_cool.agents.stats_analyst import stats_analyst_agent
from captain_cool.agents.strategist import strategist_agent
from captain_cool.tools.win_probability import compute_win_probability

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Application-level constants
# ---------------------------------------------------------------------------

_APP_NAME: str = "captain-cool"
_USER_ID: str = "orchestrator"

# ---------------------------------------------------------------------------
# Response cache
# ---------------------------------------------------------------------------

_DEBATE_CACHE: dict[str, dict[str, Any]] = {}
"""Module-level in-process cache for debate results.

Keyed by :func:`_make_cache_key`.  Survives for the lifetime of the uvicorn
process (cleared on server restart).  Saves API quota during demo testing
when the same match situation is submitted more than once.
"""

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _make_cache_key(match_state: dict[str, Any]) -> str:
    """Build a deterministic string key from the fields that uniquely identify
    a match situation for caching purposes.

    Only the four cheapest-to-read fields are used as the key:
    ``innings``, ``over``, ``score`` (normalised), and both team names.
    Venue, bowlers, and player names are intentionally excluded so that minor
    form variations in the same situation still hit the cache.

    Parameters
    ----------
    match_state:
        Raw match_state dict passed to :func:`run_debate`.

    Returns
    -------
    str
        A ``|``-separated string suitable as a dict key.
    """
    innings   = str(match_state.get("innings", "")).strip()
    over      = str(match_state.get("overs", match_state.get("over", ""))).strip()
    score     = str(match_state.get("score", match_state.get("score_raw", ""))).replace(" ", "")
    bat_team  = str(match_state.get("batting_team", "")).strip().upper()
    bowl_team = str(match_state.get("bowling_team", "")).strip().upper()
    return f"{innings}|{over}|{score}|{bat_team}|{bowl_team}"


def _extract_win_prob_inputs(match_state: dict[str, Any]) -> dict[str, Any]:
    """Pull win-probability inputs out of a raw match-state dict.

    The match_state schema mirrors what CricketData returns (via
    ``get_live_cricket_state``), but callers may also pass a synthetic dict
    for testing.  Sensible defaults are used for any missing key.

    Parameters
    ----------
    match_state:
        Raw match state dict, typically the arg passed into ``run_debate``.

    Returns
    -------
    dict
        Keyword arguments ready to unpack into ``compute_win_probability``.
    """
    return {
        "target": int(match_state.get("target", 0)),
        "runs": int(match_state.get("runs", 0)),
        "wickets": int(match_state.get("wickets", 0)),
        "overs": float(match_state.get("overs", 0.0)),
        # Dew risk may be enriched by the weather tool later; use "low" as
        # a conservative default for the pre-debate snapshot.
        "dew_risk": str(match_state.get("dew_risk", "low")),
        "batting_depth_rating": float(match_state.get("batting_depth_rating", 5.0)),
    }


async def _run_agent_turn(
    runner: Runner,
    session_id: str,
    user_message: str,
) -> str:
    """Send one user message to a runner and collect the final response text.

    The ADK ``run_async`` method emits a stream of events.  We iterate until
    ``event.is_final_response()`` is true and then extract the text part.

    Parameters
    ----------
    runner:
        An ADK ``Runner`` already bound to a specific agent and session
        service.
    session_id:
        The session ID to send the message into.
    user_message:
        The full prompt text to hand to the agent.

    Returns
    -------
    str
        The agent's final text response, or an error string if no text was
        produced.
    """
    content = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=user_message)],
    )

    final_text: str = ""

    async for event in runner.run_async(
        user_id=_USER_ID,
        session_id=session_id,
        new_message=content,
    ):
        # is_final_response() marks the last agent turn output (not tool
        # calls / intermediate steps).
        if event.is_final_response():
            if event.content and event.content.parts:
                final_text = event.content.parts[0].text or ""
            break  # stop processing events after the final response

    return final_text.strip() or "[Agent produced no text response]"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def run_debate(match_state: dict[str, Any]) -> dict[str, Any]:
    """Run the 5-round captain-cool debate and return a structured result.

    Parameters
    ----------
    match_state:
        A dict describing the current match situation.  Required keys for
        the win-probability bookending:

        - ``match_id`` (str) — CricketData match UUID
        - ``venue`` (str) — venue / city name for weather lookup
        - ``target`` (int) — runs needed to win
        - ``runs`` (int) — runs scored so far this innings
        - ``wickets`` (int) — wickets fallen
        - ``overs`` (float) — overs completed (e.g. 14.3)
        - ``dew_risk`` (str) — ``"high"`` | ``"medium"`` | ``"low"``
        - ``batting_depth_rating`` (float) — 0–10 scale

        Optional keys are passed verbatim to agents as additional context.

    Returns
    -------
    dict
        Keys:

        - ``stats_summary`` (str) — StatsAnalyst JSON output
        - ``initial_proposal`` (str) — Strategist's first proposal
        - ``devils_challenge`` (str) — DevilsAdvocate's two objections
        - ``final_decision`` (str) — Strategist's defence / revised decision
        - ``commentary`` (str) — Commentator's one-paragraph narration
        - ``win_probability_before`` (dict) — result of compute_win_probability
          called with the raw match_state values *before* the debate
        - ``win_probability_after`` (dict) — same call made after the debate
          using the (potentially revised) dew_risk and batting_depth_rating
          extracted from the stats_summary when available
    """
    # ------------------------------------------------------------------
    # Cache lookup — avoid burning API quota for repeated demo inputs
    # ------------------------------------------------------------------
    cache_key: str = _make_cache_key(match_state)
    if cache_key in _DEBATE_CACHE:
        logger.info("Cache HIT for key=%r — returning cached result", cache_key)
        return _DEBATE_CACHE[cache_key]
    logger.info("Cache MISS for key=%r — running full debate", cache_key)

    # ------------------------------------------------------------------
    # Step 0 — Win probability snapshot BEFORE the debate
    # ------------------------------------------------------------------
    wp_inputs_before = _extract_win_prob_inputs(match_state)
    win_prob_before: dict[str, Any] = compute_win_probability(**wp_inputs_before)
    logger.info("Win probability before debate: %s", win_prob_before)

    # ------------------------------------------------------------------
    # Session service — shared by all runners but each agent gets its own
    # session so their conversation histories remain isolated.  This is
    # the recommended pattern for sequential multi-agent pipelines.
    # ------------------------------------------------------------------
    session_service = InMemorySessionService()

    # Unique session IDs per agent per debate run (supports concurrent calls)
    run_id: str = uuid.uuid4().hex[:8]
    session_ids: dict[str, str] = {
        "analyst": f"analyst-{run_id}",
        "strategist_r2": f"strategist-r2-{run_id}",
        "devil": f"devil-{run_id}",
        "strategist_r4": f"strategist-r4-{run_id}",
        "commentator": f"commentator-{run_id}",
    }

    # Create all sessions up front (ADK requires explicit session creation)
    for sid in session_ids.values():
        await session_service.create_session(
            app_name=_APP_NAME, user_id=_USER_ID, session_id=sid
        )

    # ------------------------------------------------------------------
    # Runners — one per agent (ADK best practice: one Runner per agent)
    # ------------------------------------------------------------------
    analyst_runner = Runner(
        agent=stats_analyst_agent,
        app_name=_APP_NAME,
        session_service=session_service,
    )
    strategist_runner = Runner(
        agent=strategist_agent,
        app_name=_APP_NAME,
        session_service=session_service,
    )
    devil_runner = Runner(
        agent=devils_advocate_agent,
        app_name=_APP_NAME,
        session_service=session_service,
    )
    commentator_runner = Runner(
        agent=commentator_agent,
        app_name=_APP_NAME,
        session_service=session_service,
    )

    # Running transcript — accumulated and handed to each subsequent round
    # as explicit context so every agent has full situational awareness.
    transcript: str = ""

    # ------------------------------------------------------------------
    # Round 1 — StatsAnalyst
    # ------------------------------------------------------------------
    logger.info("Round 1: StatsAnalyst analysing match state")

    # The analyst needs the match_id and venue to call its tools; we embed
    # the full match_state JSON so it can extract whatever it needs.
    r1_prompt: str = (
        "Analyse the following match state and produce your structured "
        "JSON summary using your tools.\n\n"
        f"MATCH STATE:\n{json.dumps(match_state, indent=2)}"
    )
    stats_summary: str = await _run_agent_turn(
        analyst_runner, session_ids["analyst"], r1_prompt
    )
    logger.info("Round 1 complete. StatsAnalyst output length: %d chars", len(stats_summary))

    # Append to running transcript
    transcript += f"=== StatsAnalyst Summary ===\n{stats_summary}\n\n"

    # ------------------------------------------------------------------
    # Round 2 — Strategist proposes a decision
    # ------------------------------------------------------------------
    logger.info("Round 2: Strategist proposing tactical decision")

    r2_prompt: str = (
        "You have the following match context from StatsAnalyst. "
        "Call compute_win_probability to understand the current chase "
        "dynamics, then propose your tactical decision.\n\n"
        f"{transcript}"
    )
    initial_proposal: str = await _run_agent_turn(
        strategist_runner, session_ids["strategist_r2"], r2_prompt
    )
    logger.info("Round 2 complete. Initial proposal length: %d chars", len(initial_proposal))

    transcript += f"=== Strategist Initial Proposal ===\n{initial_proposal}\n\n"

    # ------------------------------------------------------------------
    # Round 3 — DevilsAdvocate challenges the proposal
    # ------------------------------------------------------------------
    logger.info("Round 3: DevilsAdvocate raising objections")

    r3_prompt: str = (
        "You have the full match context and the Strategist's proposal below. "
        "Raise exactly 2 specific, cricket-grounded objections.\n\n"
        f"{transcript}"
    )
    devils_challenge: str = await _run_agent_turn(
        devil_runner, session_ids["devil"], r3_prompt
    )
    logger.info("Round 3 complete. Devil's challenge length: %d chars", len(devils_challenge))

    transcript += f"=== DevilsAdvocate Objections ===\n{devils_challenge}\n\n"

    # ------------------------------------------------------------------
    # Round 4 — Strategist defends or revises
    # ------------------------------------------------------------------
    logger.info("Round 4: Strategist defending / revising proposal")

    r4_prompt: str = (
        "DevilsAdvocate has raised two objections to your proposal. "
        "Defend your original decision OR revise it — but be decisive and "
        "specific. Address each objection by name.\n\n"
        f"{transcript}"
    )
    final_decision: str = await _run_agent_turn(
        # Strategist gets a fresh session (Round 4) so its context starts
        # clean — the full transcript acts as the shared memory.
        strategist_runner, session_ids["strategist_r4"], r4_prompt
    )
    logger.info("Round 4 complete. Final decision length: %d chars", len(final_decision))

    transcript += f"=== Strategist Final Decision ===\n{final_decision}\n\n"

    # ------------------------------------------------------------------
    # Round 5 — Commentator narrates
    # ------------------------------------------------------------------
    logger.info("Round 5: Commentator narrating the final decision")

    r5_prompt: str = (
        "You have the complete debate transcript below. Write one punchy "
        "paragraph of live IPL commentary narrating the final decision.\n\n"
        f"{transcript}"
    )
    commentary: str = await _run_agent_turn(
        commentator_runner, session_ids["commentator"], r5_prompt
    )
    logger.info("Round 5 complete. Commentary length: %d chars", len(commentary))

    # ------------------------------------------------------------------
    # Win probability snapshot AFTER the debate
    # Try to extract an updated batting_depth_rating from stats_summary;
    # fall back to the original value if parsing fails.
    # ------------------------------------------------------------------
    wp_inputs_after = dict(wp_inputs_before)  # start from original values
    try:
        # StatsAnalyst is instructed to return raw JSON; attempt to parse it
        # and pick up the potentially more precise batting_depth_rating.
        summary_dict: dict[str, Any] = json.loads(stats_summary)
        raw_depth: float = float(summary_dict.get("batting_depth_rating", wp_inputs_after["batting_depth_rating"]))
        # StatsAnalyst rates depth on [0.0, 1.0]; win_probability expects [0.0, 10.0]
        # Map proportionally: 0.0→0.0, 1.0→10.0
        wp_inputs_after["batting_depth_rating"] = raw_depth * 10.0
        # Also pick up dew_risk if the summary contains it (embedded in weather_summary)
        # The summary JSON does not have a direct dew_risk key, so we keep the original.
    except (json.JSONDecodeError, TypeError, ValueError):
        logger.debug("Could not parse stats_summary JSON; using original wp inputs for 'after' snapshot")

    win_prob_after: dict[str, Any] = compute_win_probability(**wp_inputs_after)
    logger.info("Win probability after debate: %s", win_prob_after)

    # ------------------------------------------------------------------
    # Assemble the structured result, cache it, then return
    # ------------------------------------------------------------------
    result: dict[str, Any] = {
        "stats_summary": stats_summary,
        "initial_proposal": initial_proposal,
        "devils_challenge": devils_challenge,
        "final_decision": final_decision,
        "commentary": commentary,
        "win_probability_before": win_prob_before,
        "win_probability_after": win_prob_after,
    }
    _DEBATE_CACHE[cache_key] = result
    logger.info("Cached debate result under key=%r (cache size now %d)", cache_key, len(_DEBATE_CACHE))
    return result


# ---------------------------------------------------------------------------
# CLI convenience entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Minimal smoke-test with a synthetic match state — useful for local
    # integration testing without a live CricketData API key.
    _sample_state: dict[str, Any] = {
        "match_id": "DEMO-MATCH-001",
        "venue": "Mumbai",
        "target": 185,
        "runs": 102,
        "wickets": 4,
        "overs": 13.2,
        "dew_risk": "high",
        "batting_depth_rating": 6.5,
    }

    result = asyncio.run(run_debate(_sample_state))
    print("\n=== DEBATE RESULT ===")
    for key, value in result.items():
        print(f"\n--- {key} ---")
        print(value)
