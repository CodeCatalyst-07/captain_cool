"""
tests/test_tools.py
~~~~~~~~~~~~~~~~~~~~
Unit tests for the three tool modules.

Uses unittest.mock.patch to intercept outbound HTTP calls — no real network
requests are made. compute_win_probability is a pure function; no mocking needed.
"""

from __future__ import annotations

import pytest
import requests
from unittest.mock import MagicMock, patch

from captain_cool.tools.cricket_api import get_live_cricket_state
from captain_cool.tools.weather_tool import get_pitch_weather
from captain_cool.tools.win_probability import compute_win_probability


# ─── Fake payload factories ─────────────────────────────────────────────────

def _cd_payload(runs=134, wickets=4, overs=14.0, rrr=8.5, crr=9.57):
    """Minimal CricketData match_info success response."""
    return {
        "status": "success",
        "data": {
            "status": "Live",
            "score": [{"r": runs, "w": wickets, "o": overs,
                        "inning": "Mumbai Indians Inning 1"}],
            "teamInfo": [{"name": "Mumbai Indians"}, {"name": "Chennai Super Kings"}],
            "players": [
                {"name": "Hardik Pandya", "role": "bat", "r": 42, "dismissal": ""},
                {"name": "Tilak Varma",   "role": "bat", "r": 31, "dismissal": ""},
                {"name": "Deepak Chahar", "role": "bowl", "o": 3.0},
            ],
            "rrr": rrr,
            "crr": crr,
        },
    }


def _owm_payload(humidity, temp=28.5, description="few clouds"):
    """Minimal OpenWeatherMap current-weather response."""
    return {
        "main": {"temp": temp, "humidity": humidity},
        "weather": [{"description": description}],
    }


def _http_mock(payload):
    """Return a mock requests.Response whose .json() yields *payload*."""
    m = MagicMock()
    m.json.return_value = payload
    m.raise_for_status.return_value = None
    return m


# ─── get_live_cricket_state ──────────────────────────────────────────────────

class TestGetLiveCricketState:

    def test_all_required_keys_present(self):
        with patch("captain_cool.tools.cricket_api.requests.get",
                   return_value=_http_mock(_cd_payload())):
            result = get_live_cricket_state("M-001")

        expected = {
            "match_id", "status", "teams", "score", "overs", "wickets",
            "batting_team", "bowling_team", "current_batsmen",
            "current_bowler", "required_run_rate", "current_run_rate",
        }
        assert expected.issubset(result.keys())

    def test_score_string_extracted(self):
        with patch("captain_cool.tools.cricket_api.requests.get",
                   return_value=_http_mock(_cd_payload(runs=134, wickets=4))):
            result = get_live_cricket_state("M-001")
        assert result["score"] == "134/4"
        assert result["wickets"] == 4

    def test_overs_extracted(self):
        with patch("captain_cool.tools.cricket_api.requests.get",
                   return_value=_http_mock(_cd_payload(overs=14.0))):
            result = get_live_cricket_state("M-001")
        assert result["overs"] == 14.0

    def test_teams_extracted(self):
        with patch("captain_cool.tools.cricket_api.requests.get",
                   return_value=_http_mock(_cd_payload())):
            result = get_live_cricket_state("M-001")
        assert "Mumbai Indians" in result["teams"]
        assert "Chennai Super Kings" in result["teams"]

    def test_run_rates_extracted(self):
        with patch("captain_cool.tools.cricket_api.requests.get",
                   return_value=_http_mock(_cd_payload(rrr=8.5, crr=9.57))):
            result = get_live_cricket_state("M-001")
        assert result["required_run_rate"] == 8.5
        assert result["current_run_rate"] == 9.57

    def test_current_batsmen_list(self):
        with patch("captain_cool.tools.cricket_api.requests.get",
                   return_value=_http_mock(_cd_payload())):
            result = get_live_cricket_state("M-001")
        names = [b["name"] for b in result["current_batsmen"]]
        assert "Hardik Pandya" in names

    def test_match_id_echoed(self):
        with patch("captain_cool.tools.cricket_api.requests.get",
                   return_value=_http_mock(_cd_payload())):
            result = get_live_cricket_state("UNIQUE-XYZ")
        assert result["match_id"] == "UNIQUE-XYZ"

    def test_timeout_returns_error_dict(self):
        with patch("captain_cool.tools.cricket_api.requests.get",
                   side_effect=requests.exceptions.Timeout):
            result = get_live_cricket_state("M-001")
        assert "error" in result
        assert "timed out" in result["error"].lower()

    def test_http_error_returns_error_dict(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_resp.text = "Forbidden"
        err = requests.exceptions.HTTPError(response=mock_resp)
        with patch("captain_cool.tools.cricket_api.requests.get", side_effect=err):
            result = get_live_cricket_state("M-001")
        assert "error" in result

    def test_api_failure_reason_in_error(self):
        payload = {"status": "failure", "reason": "Invalid API key"}
        with patch("captain_cool.tools.cricket_api.requests.get",
                   return_value=_http_mock(payload)):
            result = get_live_cricket_state("M-001")
        assert "error" in result
        assert "Invalid API key" in result["error"]


# ─── get_pitch_weather ───────────────────────────────────────────────────────

class TestGetPitchWeather:

    @pytest.mark.parametrize("humidity,expected_dew", [
        (75, "high"),    # ≥ 70 → high
        (55, "medium"),  # ≥ 50 → medium
        (30, "low"),     # < 50 → low
    ])
    def test_dew_risk_thresholds(self, humidity, expected_dew):
        with patch("captain_cool.tools.weather_tool.requests.get",
                   return_value=_http_mock(_owm_payload(humidity=humidity))):
            result = get_pitch_weather("Mumbai")
        assert result["dew_risk"] == expected_dew, (
            f"humidity={humidity}: expected '{expected_dew}', got '{result['dew_risk']}'"
        )

    def test_all_required_keys_present(self):
        with patch("captain_cool.tools.weather_tool.requests.get",
                   return_value=_http_mock(_owm_payload(60))):
            result = get_pitch_weather("Kolkata")
        assert set(result.keys()) == {"venue", "temp_c", "humidity_pct",
                                       "dew_risk", "conditions"}

    def test_venue_echoed(self):
        with patch("captain_cool.tools.weather_tool.requests.get",
                   return_value=_http_mock(_owm_payload(60))):
            result = get_pitch_weather("Chennai")
        assert result["venue"] == "Chennai"

    def test_conditions_extracted(self):
        with patch("captain_cool.tools.weather_tool.requests.get",
                   return_value=_http_mock(_owm_payload(60, description="overcast clouds"))):
            result = get_pitch_weather("Hyderabad")
        assert result["conditions"] == "overcast clouds"

    def test_temp_extracted(self):
        with patch("captain_cool.tools.weather_tool.requests.get",
                   return_value=_http_mock(_owm_payload(60, temp=32.4))):
            result = get_pitch_weather("Delhi")
        assert result["temp_c"] == 32.4

    def test_404_returns_error(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        err = requests.exceptions.HTTPError(response=mock_resp)
        with patch("captain_cool.tools.weather_tool.requests.get", side_effect=err):
            result = get_pitch_weather("GhostCity")
        assert "error" in result
        assert "not found" in result["error"].lower()

    def test_timeout_returns_error(self):
        with patch("captain_cool.tools.weather_tool.requests.get",
                   side_effect=requests.exceptions.Timeout):
            result = get_pitch_weather("Mumbai")
        assert "error" in result


# ─── compute_win_probability ─────────────────────────────────────────────────

class TestComputeWinProbability:
    """Pure function — no mocking required."""

    def test_already_won_returns_1(self):
        result = compute_win_probability(
            target=150, runs=150, wickets=2, overs=18.0,
            dew_risk="low", batting_depth_rating=5.0,
        )
        assert result["win_probability"] == 1.0

    def test_all_out_returns_0(self):
        result = compute_win_probability(
            target=185, runs=120, wickets=10, overs=18.0,
            dew_risk="low", batting_depth_rating=5.0,
        )
        assert result["win_probability"] == 0.0

    def test_high_rrr_gives_low_probability(self):
        # Need 150 off 5 overs (30 rpo) → RRR >> 11 → big penalty
        result = compute_win_probability(
            target=200, runs=50, wickets=5, overs=15.0,
            dew_risk="low", batting_depth_rating=5.0,
        )
        assert result["win_probability"] < 0.35, (
            f"Expected < 0.35 for impossible RRR, got {result['win_probability']}"
        )

    def test_low_wickets_boosts_probability(self):
        # 0 wickets fallen beats 8 wickets fallen — all else equal
        kwargs = dict(target=160, runs=80, overs=10.0,
                      dew_risk="low", batting_depth_rating=5.0)
        high = compute_win_probability(**kwargs, wickets=0)
        low  = compute_win_probability(**kwargs, wickets=8)
        assert high["win_probability"] > low["win_probability"]

    def test_high_dew_boosts_by_exactly_5pct(self):
        # The _ADJ_DEW_HIGH constant is +0.05; verify precisely
        kwargs = dict(target=170, runs=90, wickets=4, overs=12.0,
                      batting_depth_rating=5.0)
        with_dew    = compute_win_probability(**kwargs, dew_risk="high")
        without_dew = compute_win_probability(**kwargs, dew_risk="low")
        delta = with_dew["win_probability"] - without_dew["win_probability"]
        assert abs(delta - 0.05) < 1e-6, (
            f"Expected dew delta of 0.05, got {delta:.6f}"
        )

    def test_result_has_required_keys(self):
        result = compute_win_probability(
            target=180, runs=100, wickets=4, overs=12.0,
            dew_risk="medium", batting_depth_rating=5.0,
        )
        assert set(result.keys()) == {"win_probability", "required_run_rate",
                                       "balls_remaining"}

    def test_probability_clamped_to_unit_interval(self):
        # Pathological case: near-impossible chase
        result = compute_win_probability(
            target=300, runs=10, wickets=9, overs=19.0,
            dew_risk="low", batting_depth_rating=0.0,
        )
        assert 0.0 <= result["win_probability"] <= 1.0

    def test_balls_remaining_decimal_overs(self):
        # 14.3 = 14 overs + 3 balls → 120 - (14*6 + 3) = 120 - 87 = 33 balls
        result = compute_win_probability(
            target=180, runs=100, wickets=3, overs=14.3,
            dew_risk="low", batting_depth_rating=5.0,
        )
        assert result["balls_remaining"] == 33
