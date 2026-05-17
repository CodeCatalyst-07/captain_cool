"""
tests/test_agents.py
~~~~~~~~~~~~~~~~~~~~~
Integration tests for captain_cool.orchestrator.run_debate.

Strategy: patch _run_agent_turn (the ADK I/O boundary) and
InMemorySessionService so no real Gemini API calls are made.
All five round outputs are controlled via side_effect.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from captain_cool.orchestrator import run_debate

# ─── Fixtures ────────────────────────────────────────────────────────────────

SAMPLE_MATCH_STATE = {
    "match_id": "TEST-001",
    "venue": "Mumbai",
    "target": 185,
    "runs": 100,
    "wickets": 4,
    "overs": 12.0,
    "dew_risk": "high",
    "batting_depth_rating": 6.0,
    "batting_team": "MI",
    "bowling_team": "CSK",
}

# One mock output per round (order matters)
ROUND_OUTPUTS = [
    # Round 1 — StatsAnalyst (valid JSON so depth mapping works)
    '{"phase": "middle", "batting_depth_rating": 0.6, '
    '"bowlers_remaining": {}, "key_matchups": [], '
    '"weather_summary": "28°C, high dew", "run_rate_context": "CRR 8.0 vs RRR 9.5"}',
    # Round 2 — Strategist initial proposal
    "DECISION: Bring on Bumrah now.\n"
    "RATIONALE: Hard ball, best to strike before dew sets.\n"
    "FIELD SETUP: Slip in, third man up.\n"
    "CONTINGENCY: Switch if two sixes conceded.",
    # Round 3 — DevilsAdvocate
    "OBJECTION 1: Bumrah is more effective in the death overs.\n"
    "OBJECTION 2: High dew risk will negate his wrist position.",
    # Round 4 — Strategist defence
    "DECISION: Bumrah now — seize the moment before dew peaks.\n"
    "RATIONALE: Wicket in the middle changes everything.\n"
    "FIELD SETUP: Fine leg back, mid-on up.\n"
    "CONTINGENCY: Swap if conditions deteriorate.",
    # Round 5 — Commentator
    "And Rohit points to Bumrah — the crowd erupts, Wankhede on its feet!",
]

EXPECTED_KEYS = {
    "stats_summary",
    "initial_proposal",
    "devils_challenge",
    "final_decision",
    "commentary",
    "win_probability_before",
    "win_probability_after",
}


def _session_service_mock():
    """Lightweight mock for InMemorySessionService."""
    m = MagicMock()
    m.create_session = AsyncMock(return_value=None)
    return m


def _run(coro):
    """Execute an async coroutine synchronously (no pytest-asyncio needed)."""
    return asyncio.run(coro)


# ─── Tests ───────────────────────────────────────────────────────────────────

class TestRunDebate:

    def _debate(self, side_effect=None):
        """Run run_debate with mocked _run_agent_turn and session service."""
        outputs = side_effect or ROUND_OUTPUTS
        with patch("captain_cool.orchestrator._run_agent_turn",
                   new_callable=AsyncMock) as mock_turn, \
             patch("captain_cool.orchestrator.InMemorySessionService",
                   return_value=_session_service_mock()), \
             patch("captain_cool.orchestrator.Runner"):
            mock_turn.side_effect = list(outputs)
            result = _run(run_debate(SAMPLE_MATCH_STATE))
        return result, mock_turn

    # ── Key presence ────────────────────────────────────────────────────────

    def test_returns_all_seven_keys(self):
        """Result dict must have exactly the 7 documented keys."""
        result, _ = self._debate()
        assert set(result.keys()) == EXPECTED_KEYS

    def test_no_extra_keys(self):
        """No undocumented keys should leak into the result."""
        result, _ = self._debate()
        assert set(result.keys()) - EXPECTED_KEYS == set()

    # ── Round execution ─────────────────────────────────────────────────────

    def test_five_rounds_executed(self):
        """_run_agent_turn must be called exactly once per round."""
        _, mock_turn = self._debate()
        assert mock_turn.call_count == 5, (
            f"Expected 5 rounds, got {mock_turn.call_count}"
        )

    def test_round_outputs_mapped_correctly(self):
        """Each mock output must appear in its designated result key."""
        result, _ = self._debate()
        assert result["stats_summary"]    == ROUND_OUTPUTS[0]
        assert result["initial_proposal"] == ROUND_OUTPUTS[1]
        assert result["devils_challenge"] == ROUND_OUTPUTS[2]
        assert result["final_decision"]   == ROUND_OUTPUTS[3]
        assert result["commentary"]       == ROUND_OUTPUTS[4]

    # ── Win-probability bookending ──────────────────────────────────────────

    def test_win_probability_before_is_dict(self):
        result, _ = self._debate()
        wp = result["win_probability_before"]
        assert isinstance(wp, dict)
        assert "win_probability" in wp

    def test_win_probability_after_is_dict(self):
        result, _ = self._debate()
        wp = result["win_probability_after"]
        assert isinstance(wp, dict)
        assert "win_probability" in wp

    def test_win_probability_before_in_unit_interval(self):
        result, _ = self._debate()
        p = result["win_probability_before"]["win_probability"]
        assert 0.0 <= p <= 1.0, f"Before probability out of range: {p}"

    def test_win_probability_after_in_unit_interval(self):
        result, _ = self._debate()
        p = result["win_probability_after"]["win_probability"]
        assert 0.0 <= p <= 1.0, f"After probability out of range: {p}"

    def test_win_probability_keys(self):
        result, _ = self._debate()
        for label in ("win_probability_before", "win_probability_after"):
            assert {"win_probability", "required_run_rate",
                    "balls_remaining"} == set(result[label].keys()), (
                f"Unexpected keys in {label}: {result[label].keys()}"
            )

    # ── Debate loop ordering ────────────────────────────────────────────────

    def test_stats_summary_appears_in_strategist_prompt(self):
        """The StatsAnalyst output must be threaded into the Strategist prompt."""
        with patch("captain_cool.orchestrator._run_agent_turn",
                   new_callable=AsyncMock) as mock_turn, \
             patch("captain_cool.orchestrator.InMemorySessionService",
                   return_value=_session_service_mock()), \
             patch("captain_cool.orchestrator.Runner"):
            mock_turn.side_effect = list(ROUND_OUTPUTS)
            _run(run_debate(SAMPLE_MATCH_STATE))

        # Round 2 is call index 1; its first positional arg is the runner,
        # second is the session_id, third is user_message
        r2_message = mock_turn.call_args_list[1].args[2]
        assert "StatsAnalyst" in r2_message, (
            "Strategist prompt should contain StatsAnalyst context"
        )

    def test_proposal_appears_in_devil_prompt(self):
        """The Strategist proposal must be threaded into DevilsAdvocate prompt."""
        with patch("captain_cool.orchestrator._run_agent_turn",
                   new_callable=AsyncMock) as mock_turn, \
             patch("captain_cool.orchestrator.InMemorySessionService",
                   return_value=_session_service_mock()), \
             patch("captain_cool.orchestrator.Runner"):
            mock_turn.side_effect = list(ROUND_OUTPUTS)
            _run(run_debate(SAMPLE_MATCH_STATE))

        r3_message = mock_turn.call_args_list[2].args[2]
        assert "Strategist" in r3_message, (
            "DevilsAdvocate prompt should contain Strategist context"
        )

    def test_all_context_in_commentator_prompt(self):
        """Commentator must receive the complete transcript."""
        with patch("captain_cool.orchestrator._run_agent_turn",
                   new_callable=AsyncMock) as mock_turn, \
             patch("captain_cool.orchestrator.InMemorySessionService",
                   return_value=_session_service_mock()), \
             patch("captain_cool.orchestrator.Runner"):
            mock_turn.side_effect = list(ROUND_OUTPUTS)
            _run(run_debate(SAMPLE_MATCH_STATE))

        r5_message = mock_turn.call_args_list[4].args[2]
        # All four prior outputs should appear in the final prompt
        assert "StatsAnalyst" in r5_message
        assert "Strategist" in r5_message
        assert "DevilsAdvocate" in r5_message
