"""
tests/conftest.py
~~~~~~~~~~~~~~~~~~
Injects a fake settings module into sys.modules **before** any captain_cool
package is imported, so tests never hit EnvironmentError for missing API keys.
"""
import sys
from types import ModuleType

# ── Fake settings module ────────────────────────────────────────────────────
_s = ModuleType("captain_cool.config.settings")
_s.GEMINI_API_KEY = "test-gemini-key"
_s.CRICKETDATA_API_KEY = "test-cricket-key"
_s.OPENWEATHERMAP_API_KEY = "test-owm-key"
_s.GEMINI_MODEL = "gemini-2.0-flash"
_s.CRICKETDATA_BASE_URL = "https://api.cricketdata.org/api/v1"
_s.OWM_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

_cfg = ModuleType("captain_cool.config")

sys.modules.setdefault("captain_cool.config.settings", _s)
sys.modules.setdefault("captain_cool.config", _cfg)
