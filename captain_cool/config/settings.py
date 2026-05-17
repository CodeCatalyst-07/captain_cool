"""
captain_cool.config.settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Centralised configuration for the captain-cool project.

All secrets are loaded from a ``.env`` file (or the process environment)
using *python-dotenv*.  The module raises :class:`EnvironmentError` at
**import time** if any required key is absent, so misconfigured deployments
fail immediately with a clear, actionable message rather than deep inside
business logic.

Constants
---------
GEMINI_API_KEY
    Secret key for the Google Gemini generative-AI service.
CRICKETDATA_API_KEY
    Secret key for the CricketData.org live-cricket API.
OPENWEATHERMAP_API_KEY
    Secret key for the OpenWeatherMap current-weather API.
GEMINI_MODEL
    Default Gemini model identifier used across all agents.
CRICKETDATA_BASE_URL
    Base URL for the CricketData.org REST API (v1).
OWM_BASE_URL
    Base URL for the OpenWeatherMap current-weather endpoint.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load .env from the project root (two levels up from this file)
# ---------------------------------------------------------------------------

_ENV_PATH: Path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=_ENV_PATH, override=False)

# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------


def _require(key: str) -> str:
    """Return the value of an environment variable, raising if it is absent.

    Parameters
    ----------
    key:
        The name of the environment variable to read.

    Returns
    -------
    str
        The non-empty string value of the variable.

    Raises
    ------
    EnvironmentError
        If the variable is not set or is an empty string, with a message
        that tells the developer exactly how to fix the problem.
    """
    value: str | None = os.environ.get(key)
    if not value:
        raise EnvironmentError(
            f"Required environment variable '{key}' is not set.\n"
            f"  1. Copy '.env.example' to '.env' in the project root.\n"
            f"  2. Fill in a valid value for {key}.\n"
            f"  3. Restart the application.\n"
            f"  (Looked for .env at: {_ENV_PATH})"
        )
    return value


# ---------------------------------------------------------------------------
# Secrets — validated eagerly at import time
# ---------------------------------------------------------------------------

GEMINI_API_KEY: str = _require("GEMINI_API_KEY")
"""Google Gemini API secret key."""

CRICKETDATA_API_KEY: str = _require("CRICKETDATA_API_KEY")
"""CricketData.org API secret key."""

OPENWEATHERMAP_API_KEY: str = _require("OPENWEATHERMAP_API_KEY")
"""OpenWeatherMap API secret key."""

# ---------------------------------------------------------------------------
# Model & endpoint constants
# ---------------------------------------------------------------------------

GEMINI_MODEL: str = "gemini-2.5-flash"
"""Default Gemini model used by all captain-cool agents."""

CRICKETDATA_BASE_URL: str = "https://api.cricketdata.org/api/v1"
"""Base URL for the CricketData.org REST API (version 1)."""

OWM_BASE_URL: str = "https://api.openweathermap.org/data/2.5/weather"
"""Base URL for the OpenWeatherMap current-weather endpoint."""
