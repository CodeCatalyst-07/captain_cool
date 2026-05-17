"""
captain_cool.agents.stats_analyst
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Defines the **StatsAnalyst** ``LlmAgent``.

Role
----
StatsAnalyst receives raw match-state JSON and — by calling the cricket API
and weather tools — synthesises a clean structured summary that every
downstream agent depends on.

Output contract (natural-language JSON block)
---------------------------------------------
The agent is instructed to return a JSON object with:

``phase``
    Current game phase: ``"powerplay"`` (overs 1–6), ``"middle"`` (7–15),
    or ``"death"`` (16–20).
``key_matchups``
    List of strings, each describing a batter vs. bowler matchup.
``bowlers_remaining``
    Dict mapping bowler name → overs they still have available.
``batting_depth_rating``
    Float in [0.0, 1.0] rating the quality of the batting side's
    remaining resources.
``weather_summary``
    Plain-language one-liner on conditions + dew risk.
``run_rate_context``
    One-liner comparing current run rate vs. required run rate.
"""

from __future__ import annotations

from google.adk.agents import LlmAgent

from captain_cool.config.settings import GEMINI_MODEL
from captain_cool.tools.cricket_api import get_live_cricket_state
from captain_cool.tools.weather_tool import get_pitch_weather

# ---------------------------------------------------------------------------
# System instruction
# ---------------------------------------------------------------------------

_INSTRUCTION: str = """
You are StatsAnalyst — the data engine of an IPL captaincy brain trust.

Your sole job is to consume raw match-state JSON and live API data, then
produce a clean, structured JSON summary for the Strategist and DevilsAdvocate.

## Workflow
1. Use the `get_live_cricket_state` tool to fetch fresh match data for the
   match_id present in the input.
2. Use the `get_pitch_weather` tool to fetch conditions for the venue
   present in the input.
3. Synthesise both responses into a single JSON object — no prose, no
   markdown fences, **only** the raw JSON.

## Output format (strict)
Return ONLY this JSON structure (no extra keys, no explanation):

{
  "phase": "<powerplay|middle|death>",
  "key_matchups": ["<batter> vs <bowler>: <one-line context>", ...],
  "bowlers_remaining": {"<bowler_name>": <overs_left: float>, ...},
  "batting_depth_rating": <0.0-1.0>,
  "weather_summary": "<one-line conditions + dew risk>",
  "run_rate_context": "<CRR vs RRR one-liner>"
}

## Phase boundaries (T20)
- Powerplay : overs 1–6
- Middle     : overs 7–15
- Death      : overs 16–20

## Batting depth rating heuristic
- 1.0 : 5+ recognised batters still to come
- 0.7 : 3–4 batters remaining
- 0.5 : 2 batters remaining
- 0.3 : 1 batter remaining (tail exposed)
- 0.0 : tail end only

## Rules
- Never invent data not present in the API responses.
- If a tool call returns an error dict, include the error under the
  relevant JSON field as a string beginning with "ERROR:".
- No ML jargon. Use cricket terminology only.
""".strip()

# ---------------------------------------------------------------------------
# Agent definition
# ---------------------------------------------------------------------------

stats_analyst_agent = LlmAgent(
    name="StatsAnalyst",
    model=GEMINI_MODEL,
    instruction=_INSTRUCTION,
    description=(
        "Fetches live cricket state and venue weather, then produces a "
        "structured JSON summary covering game phase, key matchups, bowler "
        "overs remaining, batting depth rating, and weather context."
    ),
    # ADK wraps Python callables as tools automatically; it reads their
    # docstrings and type hints to build the function schema.
    tools=[get_live_cricket_state, get_pitch_weather],
)
"""The StatsAnalyst LlmAgent instance — import and pass to the orchestrator."""
