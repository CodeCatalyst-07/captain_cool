#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# start.sh — launch FastAPI backend and Vite dev server simultaneously.
#
# Usage (from the captain-cool/ project root):
#   ./start.sh
#
# The script self-ensures its own executable bit, so you never need to
# run chmod +x manually.
#
# Prerequisites:
#   • Python venv activated:  source .venv/bin/activate
#   • Dependencies installed: pip install -r requirements.txt
#   • Frontend deps installed: cd frontend && npm install
# ─────────────────────────────────────────────────────────────────────────────

# ── Self-chmod: ensure this script is executable even after a fresh clone ───
chmod +x "${BASH_SOURCE[0]}" 2>/dev/null || true

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Colours ───────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'
GOLD='\033[0;33m'
RED='\033[0;31m'
RESET='\033[0m'
BOLD='\033[1m'

echo -e "${BOLD}${GOLD}🏏  Captain Cool — starting servers${RESET}"
echo ""

# ── Pre-flight: check .env exists ─────────────────────────────────────────────
if [ ! -f "$SCRIPT_DIR/.env" ]; then
  if [ -f "$SCRIPT_DIR/.env.example" ]; then
    echo -e "${GOLD}⚠  .env not found — copying from .env.example${RESET}"
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
    echo -e "${RED}   Please edit .env and fill in your API keys, then re-run start.sh${RESET}"
    exit 1
  else
    echo -e "${RED}✗  .env file is missing and no .env.example found.${RESET}"
    echo -e "   Create .env with GEMINI_API_KEY, CRICKETDATA_API_KEY, OPENWEATHERMAP_API_KEY"
    exit 1
  fi
fi

# ── Pre-flight: check frontend node_modules ───────────────────────────────────
if [ ! -d "$SCRIPT_DIR/frontend/node_modules" ]; then
  echo -e "${GOLD}⚠  frontend/node_modules missing — running npm install${RESET}"
  (cd "$SCRIPT_DIR/frontend" && npm install)
fi

# ── 1. FastAPI backend (port 8000) ────────────────────────────────────────────
echo -e "${GREEN}▶  FastAPI backend   →  http://localhost:8000${RESET}"
(
  cd "$SCRIPT_DIR"
  uvicorn captain_cool.api.server:app --reload --port 8000 --host 0.0.0.0
) &
BACKEND_PID=$!

# Give uvicorn a moment to bind before Vite starts
sleep 1

# ── 2. Vite dev server (port 5173) ───────────────────────────────────────────
echo -e "${GREEN}▶  Vite dev server   →  http://localhost:5173${RESET}"
(
  cd "$SCRIPT_DIR/frontend"
  npm run dev
) &
FRONTEND_PID=$!

echo ""
echo -e "  Backend  PID : ${BOLD}$BACKEND_PID${RESET}"
echo -e "  Frontend PID : ${BOLD}$FRONTEND_PID${RESET}"
echo ""
echo -e "  Open ${BOLD}http://localhost:5173${RESET} in your browser."
echo -e "  Press ${BOLD}Ctrl+C${RESET} to stop both servers."
echo ""

# ── Cleanup on Ctrl+C ─────────────────────────────────────────────────────────
trap "echo ''; echo 'Stopping...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" SIGINT SIGTERM

# Wait for either process to exit
wait
