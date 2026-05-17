#!/usr/bin/env python3
"""
verify_setup.py
~~~~~~~~~~~~~~~~
Pre-flight verification script for captain-cool.

Run from the project root:
    python verify_setup.py

Checks each required environment variable is present and non-empty.
Prints "Keys OK" if all pass; prints exactly which key is missing otherwise.
"""

from __future__ import annotations

import sys
from pathlib import Path

# ── Load the .env file from the same directory as this script ────────────────
try:
    from dotenv import load_dotenv
except ImportError:
    print("ERROR: python-dotenv is not installed.")
    print("       Run: pip install python-dotenv")
    sys.exit(1)

_ENV_PATH = Path(__file__).resolve().parent / ".env"

if not _ENV_PATH.exists():
    print(f"ERROR: .env file not found at {_ENV_PATH}")
    print("       Run: cp .env.example .env  then fill in your keys.")
    sys.exit(1)

load_dotenv(dotenv_path=_ENV_PATH, override=False)

import os  # noqa: E402 — import after load_dotenv

# ── Keys to check ────────────────────────────────────────────────────────────
REQUIRED_KEYS: list[tuple[str, str]] = [
    ("GEMINI_API_KEY",         "https://aistudio.google.com/app/apikey"),
    ("CRICKETDATA_API_KEY",    "https://cricketdata.org/pricing/"),
    ("OPENWEATHERMAP_API_KEY", "https://home.openweathermap.org/users/sign_up"),
]

# ── Verify ───────────────────────────────────────────────────────────────────
missing: list[str] = []

for key, url in REQUIRED_KEYS:
    value = os.environ.get(key, "").strip()
    if not value or value.startswith("your_"):
        # "your_*" means the placeholder was never replaced
        missing.append(key)

# ── Report ───────────────────────────────────────────────────────────────────
if missing:
    print("⚠  The following required API keys are missing or still set to")
    print("   their placeholder values in .env:\n")
    for key in missing:
        url = next(u for k, u in REQUIRED_KEYS if k == key)
        print(f"   ✗  {key}")
        print(f"      Get a free key at: {url}\n")
    sys.exit(1)
else:
    print("✓  Keys OK — all three API keys are set.")
    print(f"   .env loaded from: {_ENV_PATH}")
    sys.exit(0)
