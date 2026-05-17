"""
captain_cool.tools.win_probability
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Implements a **heuristic win-probability model** for the second innings of
a T20 or ODI match.  The model is intentionally transparent — every
adjustment is a named constant with an inline comment — so that the
captain-cool agents can explain their reasoning to the commentator.

The formula is **not** a trained ML model; it is a rule-based approximation
grounded in cricket analytics research:

  base probability = 0.5  (coin-flip before any context is considered)

  adjustments applied in order
  ─────────────────────────────
  1. Required Run Rate (RRR) brackets
  2. Wickets in hand (more wickets left → higher probability)
  3. Dew risk        (+0.05 if high)
  4. Batting depth   (linearly scaled around a neutral rating of 5.0)

Final value is clamped to [0.0, 1.0].

All functions are pure (no I/O, no side-effects) so they can be unit-tested
without mocking.
"""

from __future__ import annotations

from typing import Literal

from google.genai import types as genai_types

# ---------------------------------------------------------------------------
# Type alias
# ---------------------------------------------------------------------------

DewRisk = Literal["high", "medium", "low"]

# ---------------------------------------------------------------------------
# Model constants — every magic number lives here with its rationale
# ---------------------------------------------------------------------------

_BASE_PROBABILITY: float = 0.50
"""Starting probability before any match-specific adjustment."""

# ── Required Run Rate adjustments ──────────────────────────────────────────
# Based on historical T20/ODI data: teams requiring < 7 rpo win ~65%,
# 7-9 rpo is roughly even, 9-11 rpo ~35%, above 11 rpo rarely won.
_RRR_EASY: float = 7.0          # RRR below this threshold is "comfortable"
_RRR_TOUGH: float = 9.0         # RRR above this threshold is "hard"
_RRR_VERY_TOUGH: float = 11.0   # RRR above this is "very hard"

_ADJ_RRR_EASY: float = +0.15    # comfortable chase → boost batting team
_ADJ_RRR_TOUGH: float = -0.10   # hard chase → slight edge to bowling team
_ADJ_RRR_VERY_TOUGH: float = -0.25  # very hard chase → strong bowling advantage

# ── Wickets in hand ────────────────────────────────────────────────────────
# Each wicket lost is worth roughly 2 % probability.  Indexed by
# wickets *fallen* (0–10); index 10 means all out (team has lost).
_WICKET_ADJUSTMENT: dict[int, float] = {
    0:  +0.10,   # all 10 in hand — huge batting advantage
    1:  +0.08,
    2:  +0.06,
    3:  +0.04,
    4:  +0.02,
    5:   0.00,   # neutral midpoint
    6:  -0.02,
    7:  -0.04,
    8:  -0.06,
    9:  -0.08,
    10: -0.20,   # all out → certain loss
}

# ── Dew risk ───────────────────────────────────────────────────────────────
# Dew makes the ball slippery; bowlers lose grip and cannot swing / spin
# as effectively.  This systematically helps the batting side chasing in
# the second innings.
_ADJ_DEW_HIGH: float = +0.05
# Medium and low dew risk carry no explicit adjustment (baked into base).

# ── Batting depth ──────────────────────────────────────────────────────────
# Rated on a 0–10 scale by the caller (e.g. based on team composition).
# 5.0 is neutral; each point above/below shifts probability by 1 %.
_BATTING_DEPTH_NEUTRAL: float = 5.0
_BATTING_DEPTH_SCALE: float = 0.01   # 1 % per rating point


# ---------------------------------------------------------------------------
# T20 match constants
# ---------------------------------------------------------------------------

_BALLS_PER_OVER: int = 6
_TOTAL_OVERS_T20: int = 20


# ---------------------------------------------------------------------------
# Public function
# ---------------------------------------------------------------------------


def compute_win_probability(
    target: int,
    runs: int,
    wickets: int,
    overs: float,
    dew_risk: DewRisk,
    batting_depth_rating: float,
) -> dict[str, float | int]:
    """Compute the batting team's probability of winning the chase.

    Parameters
    ----------
    target:
        Runs required to win (e.g. 185 in a T20 chase).
    runs:
        Runs already scored by the batting team this innings.
    wickets:
        Wickets fallen so far in the current innings (0–10).
    overs:
        Overs completed, as a decimal (e.g. ``14.3`` = 14 overs, 3 balls).
    dew_risk:
        One of ``"high"``, ``"medium"``, or ``"low"`` as returned by
        :func:`~captain_cool.tools.weather_tool.get_pitch_weather`.
    batting_depth_rating:
        Subjective quality rating for the batting lineup, on a 0–10 scale.
        ``5.0`` is average; higher values indicate a stronger lower order.

    Returns
    -------
    dict
        - ``win_probability`` (float) — probability in [0.0, 1.0]
        - ``required_run_rate`` (float) — runs-per-over needed from here
        - ``balls_remaining`` (int) — balls left in the innings

    Notes
    -----
    The model assumes a T20 format (20 overs, 120 balls total).  For ODIs
    the caller should normalise ``overs`` proportionally before calling.

    If the target is already surpassed (``runs >= target``), probability
    is returned as ``1.0``.  If all wickets have fallen (``wickets >= 10``),
    it is returned as ``0.0``.
    """
    # ------------------------------------------------------------------
    # Guard rails — handle terminal states immediately
    # ------------------------------------------------------------------
    if runs >= target:
        # Chase already won
        return {
            "win_probability": 1.0,
            "required_run_rate": 0.0,
            "balls_remaining": 0,
        }

    if wickets >= 10:
        # All out
        balls_used = int(overs) * _BALLS_PER_OVER + round((overs % 1) * 10)
        balls_remaining = max(0, _TOTAL_OVERS_T20 * _BALLS_PER_OVER - balls_used)
        return {
            "win_probability": 0.0,
            "required_run_rate": 0.0,
            "balls_remaining": balls_remaining,
        }

    # ------------------------------------------------------------------
    # Derived quantities
    # ------------------------------------------------------------------
    runs_needed: int = target - runs

    # Convert decimal overs (e.g. 14.3) to a whole-ball count
    full_overs: int = int(overs)
    partial_balls: int = round((overs % 1) * 10)   # e.g. 0.3 → 3 balls
    balls_bowled: int = full_overs * _BALLS_PER_OVER + partial_balls
    balls_remaining: int = max(0, _TOTAL_OVERS_T20 * _BALLS_PER_OVER - balls_bowled)

    # Avoid division by zero if innings is somehow complete
    overs_remaining: float = balls_remaining / _BALLS_PER_OVER if balls_remaining > 0 else 0.0001
    required_run_rate: float = round(runs_needed / overs_remaining, 2)

    # ------------------------------------------------------------------
    # Probability model
    # ------------------------------------------------------------------
    probability: float = _BASE_PROBABILITY

    # 1. Required Run Rate bracket adjustment
    if required_run_rate < _RRR_EASY:
        probability += _ADJ_RRR_EASY
    elif required_run_rate < _RRR_TOUGH:
        # Between easy and tough — scale linearly between 0 and -0.10
        # so transitions are smooth rather than step-wise.
        fraction = (required_run_rate - _RRR_EASY) / (_RRR_TOUGH - _RRR_EASY)
        probability += _ADJ_RRR_EASY * (1 - fraction)
    elif required_run_rate < _RRR_VERY_TOUGH:
        probability += _ADJ_RRR_TOUGH
    else:
        probability += _ADJ_RRR_VERY_TOUGH

    # 2. Wickets in hand — clamp wickets index to valid range
    wicket_key: int = max(0, min(10, wickets))
    probability += _WICKET_ADJUSTMENT[wicket_key]

    # 3. Dew risk — only "high" carries an explicit positive adjustment
    if dew_risk == "high":
        probability += _ADJ_DEW_HIGH
    # "medium" and "low" have no explicit term (already in base)

    # 4. Batting depth — linear adjustment around neutral rating
    depth_adjustment: float = (batting_depth_rating - _BATTING_DEPTH_NEUTRAL) * _BATTING_DEPTH_SCALE
    probability += depth_adjustment

    # 5. Clamp to [0.0, 1.0]
    probability = max(0.0, min(1.0, probability))

    return {
        "win_probability": round(probability, 4),
        "required_run_rate": required_run_rate,
        "balls_remaining": balls_remaining,
    }


# ---------------------------------------------------------------------------
# Gemini FunctionDeclaration
# ---------------------------------------------------------------------------

win_prob_tool_declaration = genai_types.FunctionDeclaration(
    name="compute_win_probability",
    description=(
        "Computes the batting team's win probability for a second-innings chase "
        "using a heuristic model that factors in the required run rate, wickets "
        "in hand, dew risk, and batting depth. Returns the probability (0–1), "
        "the current required run rate, and balls remaining."
    ),
    parameters=genai_types.Schema(
        type=genai_types.Type.OBJECT,
        properties={
            "target": genai_types.Schema(
                type=genai_types.Type.INTEGER,
                description="Total runs the batting team needs to win (e.g. 185).",
            ),
            "runs": genai_types.Schema(
                type=genai_types.Type.INTEGER,
                description="Runs already scored by the batting team this innings.",
            ),
            "wickets": genai_types.Schema(
                type=genai_types.Type.INTEGER,
                description="Wickets fallen so far in the current innings (0–10).",
            ),
            "overs": genai_types.Schema(
                type=genai_types.Type.NUMBER,
                description=(
                    "Overs completed as a decimal, e.g. 14.3 means "
                    "14 overs and 3 balls."
                ),
            ),
            "dew_risk": genai_types.Schema(
                type=genai_types.Type.STRING,
                description=(
                    "Dew risk at the venue: 'high' (humidity >= 70%), "
                    "'medium' (>= 50%), or 'low' (< 50%)."
                ),
                enum=["high", "medium", "low"],
            ),
            "batting_depth_rating": genai_types.Schema(
                type=genai_types.Type.NUMBER,
                description=(
                    "Quality rating of the batting lineup's depth on a 0–10 scale. "
                    "5.0 is average; higher means a stronger lower order."
                ),
            ),
        },
        required=["target", "runs", "wickets", "overs", "dew_risk", "batting_depth_rating"],
    ),
)
"""Gemini ``FunctionDeclaration`` for :func:`compute_win_probability`."""
