"""
captain_cool.tools.weather_tool
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Fetches current weather at a cricket venue using the **OpenWeatherMap**
free-tier API and computes a *dew-risk* label relevant to pitch conditions.

Dew forms on outfields in the second innings of day-night matches and makes
the ball harder to grip, typically favouring batsmen.  The risk label is
derived purely from relative humidity.

Free-tier endpoint used
-----------------------
``GET https://api.openweathermap.org/data/2.5/weather``

Query parameters
~~~~~~~~~~~~~~~~
- ``q``      — venue / city name (e.g. ``"Mumbai"``)
- ``appid``  — OpenWeatherMap API key (from settings)
- ``units``  — always ``"metric"`` so temperatures are in °C
"""

from __future__ import annotations

import logging
from typing import Any, Literal

import requests
from google.genai import types as genai_types

from captain_cool.config.settings import OPENWEATHERMAP_API_KEY, OWM_BASE_URL

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Network constants
# ---------------------------------------------------------------------------

_TIMEOUT_SECONDS: int = 10
"""Hard timeout for every outbound HTTP request."""

# ---------------------------------------------------------------------------
# Type alias
# ---------------------------------------------------------------------------

DewRisk = Literal["high", "medium", "low"]
"""Three-level dew-risk classification used by agents downstream."""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _classify_dew_risk(humidity_pct: float) -> DewRisk:
    """Map a humidity percentage to a coarse dew-risk label.

    Research Rule of Thumb
    ----------------------
    - **≥ 70 %** → ``"high"``   — significant dew almost certain after sundown
    - **≥ 50 %** → ``"medium"`` — moderate moisture, conditions-dependent
    - **< 50 %** → ``"low"``    — negligible dew impact

    Parameters
    ----------
    humidity_pct:
        Relative humidity in percent (0–100).

    Returns
    -------
    DewRisk
        One of ``"high"``, ``"medium"``, or ``"low"``.
    """
    if humidity_pct >= 70:
        return "high"
    if humidity_pct >= 50:
        return "medium"
    return "low"


# ---------------------------------------------------------------------------
# Public function
# ---------------------------------------------------------------------------


def _extract_city(venue: str) -> str:
    """Extract a bare city name from a full venue string.

    OpenWeatherMap resolves city names reliably only when no stadium or
    ground words are present.  This function handles two common formats:

    - ``"Eden Gardens, Kolkata"``  → ``"Kolkata"``   (comma-split, last part)
    - ``"Wankhede Stadium Mumbai"`` → ``"Mumbai"``    (space-split, last word)
    - ``"Mumbai"``                  → ``"Mumbai"``    (already bare, unchanged)

    Parameters
    ----------
    venue:
        Raw venue string as typed by the user or returned by an API.

    Returns
    -------
    str
        The extracted city name, stripped of leading/trailing whitespace.
    """
    # Prefer comma-split: "Eden Gardens, Kolkata" → "Kolkata"
    if "," in venue:
        return venue.split(",")[-1].strip()
    # Fall back to last word: "Wankhede Stadium Mumbai" → "Mumbai"
    parts = venue.strip().split()
    return parts[-1] if parts else venue


def get_pitch_weather(venue: str) -> dict[str, Any]:
    """Fetch current weather conditions at a cricket venue.

    Uses the OpenWeatherMap *current weather* free-tier endpoint.  The
    venue string is cleaned to a bare city name before the API call so
    OWM can resolve it reliably (e.g. "Wankhede Stadium Mumbai" → "Mumbai").

    Parameters
    ----------
    venue:
        Human-readable venue / city name (e.g. ``"Eden Gardens, Kolkata"``
        or simply ``"Kolkata"``).  Multi-word stadium names are handled
        automatically — only the city portion is sent to OWM.

    Returns
    -------
    dict
        On success:

        - ``venue`` (str) — original venue string echoed back
        - ``temp_c`` (float) — temperature in degrees Celsius
        - ``humidity_pct`` (float) — relative humidity (0–100)
        - ``dew_risk`` (str) — ``"high"`` | ``"medium"`` | ``"low"``
        - ``conditions`` (str) — OWM weather description, e.g.
          ``"overcast clouds"``

        On failure, a dict with a single ``"error"`` key and a
        descriptive message.
    """
    city: str = _extract_city(venue)
    logger.debug("Resolved venue %r → city %r for OWM lookup", venue, city)

    params: dict[str, str] = {
        "q": city,
        "appid": OPENWEATHERMAP_API_KEY,
        "units": "metric",   # return temperatures in °C
    }

    try:
        response = requests.get(OWM_BASE_URL, params=params, timeout=_TIMEOUT_SECONDS)
        response.raise_for_status()
        payload: dict[str, Any] = response.json()
    except requests.exceptions.Timeout:
        logger.warning("OWM request timed out for venue='%s'", venue)
        return {"error": f"Request timed out after {_TIMEOUT_SECONDS}s (venue={venue!r})"}
    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code
        # 404 → OWM couldn't resolve the city name
        if status == 404:
            logger.warning("OWM could not find venue='%s'", venue)
            return {"error": f"Venue not found by OpenWeatherMap: {venue!r}"}
        logger.error("OWM HTTP error %s for venue='%s': %s", status, venue, exc)
        return {"error": f"HTTP {status}: {exc.response.text[:200]}"}
    except requests.exceptions.RequestException as exc:
        logger.error("OWM network error for venue='%s': %s", venue, exc)
        return {"error": f"Network error: {exc}"}

    # ------------------------------------------------------------------
    # Parse OWM response structure:
    #   payload["main"]["temp"]       → temperature (°C with units=metric)
    #   payload["main"]["humidity"]   → relative humidity (%)
    #   payload["weather"][0]["description"] → textual condition
    # ------------------------------------------------------------------
    main: dict[str, Any] = payload.get("main", {})
    temp_c: float = float(main.get("temp", 0.0))
    humidity_pct: float = float(main.get("humidity", 0.0))

    weather_entries: list[dict[str, Any]] = payload.get("weather", [{}])
    conditions: str = weather_entries[0].get("description", "unknown") if weather_entries else "unknown"

    dew_risk: DewRisk = _classify_dew_risk(humidity_pct)

    return {
        "venue": venue,
        "temp_c": round(temp_c, 1),
        "humidity_pct": humidity_pct,
        "dew_risk": dew_risk,
        "conditions": conditions,
    }


# ---------------------------------------------------------------------------
# Gemini FunctionDeclaration
# ---------------------------------------------------------------------------

weather_tool_declaration = genai_types.FunctionDeclaration(
    name="get_pitch_weather",
    description=(
        "Fetches current weather at a cricket venue using OpenWeatherMap. "
        "Returns temperature, humidity, a dew-risk classification "
        "('high' | 'medium' | 'low'), and a plain-language weather description. "
        "Dew risk is crucial for second-innings batting strategy in day-night matches."
    ),
    parameters=genai_types.Schema(
        type=genai_types.Type.OBJECT,
        properties={
            "venue": genai_types.Schema(
                type=genai_types.Type.STRING,
                description=(
                    "Cricket venue or city name to look up, e.g. "
                    "'Kolkata', 'Mumbai', 'Chennai'. "
                    "City-only names resolve most reliably."
                ),
            )
        },
        required=["venue"],
    ),
)
"""Gemini ``FunctionDeclaration`` for :func:`get_pitch_weather`."""
