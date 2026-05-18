# 🏏 Captain Cool — AI IPL Captaincy Strategist

> **A multi-agent Gemini debate engine that simulates four expert personas arguing about the right cricket tactical decision — live, over-by-over.**

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│              CAPTAIN COOL  (full stack overview)                │
└────────────────────────────┬────────────────────────────────────┘
                             │
          ┌──────────────────▼──────────────────┐
          │   React + Vite + Tailwind (port 5173) │
          │   Match Input Form  →  Result Cards   │
          └──────────────────┬──────────────────┘
                             │  POST /api/strategy
          ┌──────────────────▼──────────────────┐
          │      FastAPI Server  (port 8000)      │
          │  /api/health   /api/strategy          │
          └──────────────────┬──────────────────┘
                             │  await run_debate(match_state)
          ┌──────────────────▼──────────────────┐
          │           Orchestrator               │
          │  (captain_cool/orchestrator.py)      │
          └───────────────┬──┬──────────────────┘
                          │  │  5-round sequential debate
       ┌──────────────────┘  └──────────────────────┐
       │                                             │
       ▼                                             ▼
┌─────────────┐  ┌─────────────┐  ┌──────────────┐  ┌────────────┐
│StatsAnalyst │  │ Strategist  │  │DevilsAdvocate│  │Commentator │
│  Round 1    │→ │  Round 2    │→ │   Round 3    │→ │  Round 5   │
│             │  │  Round 4    │  │              │  │            │
└──────┬──────┘  └──────┬──────┘  └──────────────┘  └────────────┘
       │                │
       │ tools          │ tools
       ▼                ▼
┌─────────────┐  ┌──────────────────────┐
│cricket_api  │  │ win_probability      │
│weather_tool │  │ (pure heuristic)     │
│(HTTP APIs)  │  └──────────────────────┘
└──────┬──────┘
       │
       ▼
┌──────────────────────────────┐
│ CricketData.org free tier    │  100 calls/day
│ OpenWeatherMap free tier     │  1,000 calls/day
└──────────────────────────────┘
```

---

## Getting Free API Keys

| Service | Free Tier | Sign-up URL |
|---|---|---|
| **Google Gemini** | 15 RPM / 1 M TPM | https://aistudio.google.com/app/apikey |
| **CricketData.org** | 100 calls/day | https://cricketdata.org/pricing/ |
| **OpenWeatherMap** | 1,000 calls/day | https://home.openweathermap.org/users/sign_up |

---

## Setup (step by step)

### 1 — Clone and enter the project

```bash
git clone <your-repo-url> captain-cool
cd captain-cool
```

### 2 — Python environment

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3 — Environment variables

```bash
cp .env.example .env
# Open .env and fill in your three API keys:
```

```dotenv
GEMINI_API_KEY=AIza...
CRICKETDATA_API_KEY=your_key_here
OPENWEATHERMAP_API_KEY=your_key_here
```

### 4 — Frontend dependencies

```bash
cd frontend
npm install
cd ..
```

### 5 — Run both servers

```bash
chmod +x start.sh
./start.sh
```

Then open **http://localhost:5173** in your browser.

> **Manual alternative** (two terminals):
> ```bash
> # Terminal 1
> uvicorn captain_cool.api.server:app --reload --port 8000
> # Terminal 2
> cd frontend && npm run dev
> ```

---

## Running Tests

```bash
# From the captain-cool/ directory with venv activated
pytest tests/ -v
```

Expected output:

```
tests/test_tools.py::TestGetLiveCricketState::test_all_required_keys_present PASSED
tests/test_tools.py::TestGetLiveCricketState::test_score_string_extracted PASSED
tests/test_tools.py::TestGetLiveCricketState::test_overs_extracted PASSED
tests/test_tools.py::TestGetLiveCricketState::test_teams_extracted PASSED
tests/test_tools.py::TestGetLiveCricketState::test_run_rates_extracted PASSED
tests/test_tools.py::TestGetLiveCricketState::test_current_batsmen_list PASSED
tests/test_tools.py::TestGetLiveCricketState::test_match_id_echoed PASSED
tests/test_tools.py::TestGetLiveCricketState::test_timeout_returns_error_dict PASSED
tests/test_tools.py::TestGetLiveCricketState::test_http_error_returns_error_dict PASSED
tests/test_tools.py::TestGetLiveCricketState::test_api_failure_reason_in_error PASSED
tests/test_tools.py::TestGetPitchWeather::test_dew_risk_thresholds[75-high] PASSED
tests/test_tools.py::TestGetPitchWeather::test_dew_risk_thresholds[55-medium] PASSED
tests/test_tools.py::TestGetPitchWeather::test_dew_risk_thresholds[30-low] PASSED
... (25 tests total)
```

Run only tool tests or agent tests selectively:

```bash
pytest tests/test_tools.py -v
pytest tests/test_agents.py -v
```

---

## Sample Match Scenario — Full Output

**Input** (MI chasing 185, over 14, score 100/4, high dew at Wankhede):

```json
{
  "innings": 2,
  "over": 14,
  "score": "100/4",
  "batting_team": "MI",
  "bowling_team": "CSK",
  "striker": "Hardik Pandya",
  "non_striker": "Tilak Varma",
  "bowlers_remaining": "Bumrah:2,Chahar:3",
  "pitch_type": "Flat",
  "dew_factor": true,
  "venue": "Wankhede Stadium Mumbai",
  "target": 185,
  "impact_player_available": true,
  "cricbuzz_url": ""
}
```

**Output** (abbreviated):

```json
{
  "stats_summary": {
    "phase": "death",
    "key_matchups": ["Hardik Pandya vs Deepak Chahar: Hardik averages 58 vs Chahar in T20s"],
    "bowlers_remaining": { "Bumrah": 2.0, "Chahar": 3.0 },
    "batting_depth_rating": 0.4,
    "weather_summary": "28°C, humidity 74%, high dew risk — ball slippery after over 15",
    "run_rate_context": "CRR 7.14, RRR 14.17 — extreme pressure on MI"
  },

  "initial_proposal": "DECISION: Bring Bumrah on now from the pavilion end.\nRATIONALE: Hard ball still in play, Bumrah's seam upright. Take the wicket before dew renders the ball unplayable. Field: Slip in, third man back, mid-off up.\nCONTINGENCY: If two boundaries in the over, pull Bumrah and rotate Thakur.",

  "devils_challenge": "OBJECTION 1: With 85 needed off 36 balls, Hardik can only hit boundaries — saving Bumrah for the 18th and 20th overs is textbook death-over strategy.\nOBJECTION 2: High dew already setting in: Bumrah's scrambled seam will lose effectiveness. His wicket-taking relies on movement, which is negated by a wet outfield.",

  "final_decision": "DECISION: Bumrah now — revised and defended.\nRATIONALE: The DevilsAdvocate assumes Hardik survives the over, but one good ball ends the game. Death-over preservation is a luxury we cannot afford at RRR 14. On dew — Bumrah's variation and pace are still potent even on a dewy ball; the 'save him for later' logic ignores that he will face a pinch-hitter, not Hardik.\nFIELD SETUP: Fine leg back, mid-wicket up, slip retained.\nCONTINGENCY: If Hardik hits 2 sixes, swap Bumrah out and introduce the Impact Player pacer.",

  "commentary": "And there it is — Rohit points to Bumrah, the crowd at Wankhede rising as one, and you sense this is the moment the captain has been engineering all evening. The pitch is slick, the ball slightly greasy, but Bumrah does not need conditions — he needs Hardik Pandya's outside edge, and that is exactly what he will go hunting for. The DevilsAdvocate wanted to save him; Rohit chose to use him. In T20 cricket, the best time to bowl your best bowler is right now — and Captain Cool has made his move.",

  "win_probability_before": {
    "win_probability": 0.1525,
    "required_run_rate": 14.17,
    "balls_remaining": 36
  },

  "win_probability_after": {
    "win_probability": 0.2125,
    "required_run_rate": 14.17,
    "balls_remaining": 36
  }
}
```

> **Note**: The actual LLM outputs will vary with each run. The sample above reflects the style and structure the agents are prompted to produce.

---

## Project Structure

```
captain-cool/
├── captain_cool/
│   ├── config/settings.py          ← API keys + constants
│   ├── tools/
│   │   ├── cricket_api.py          ← CricketData.org wrapper
│   │   ├── weather_tool.py         ← OpenWeatherMap wrapper
│   │   └── win_probability.py      ← Heuristic probability model
│   ├── agents/
│   │   ├── stats_analyst.py        ← Round 1 agent
│   │   ├── strategist.py           ← Rounds 2 & 4 agent
│   │   ├── devils_advocate.py      ← Round 3 agent
│   │   └── commentator.py          ← Round 5 agent
│   ├── orchestrator.py             ← 5-round debate loop
│   └── api/server.py               ← FastAPI + CORS
├── frontend/                       ← Vite + React + Tailwind UI
│   └── src/
│       ├── App.jsx
│       └── components/
│           ├── MatchForm.jsx
│           ├── ResultCards.jsx
│           ├── WinProbBar.jsx
│           └── LoadingSpinner.jsx
├── tests/
│   ├── conftest.py                 ← Mock settings injection
│   ├── test_tools.py               ← 25 tool unit tests
│   └── test_agents.py              ← 13 orchestrator tests
├── requirements.txt
├── .env.example
├── start.sh                        ← Starts both servers
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Google Gemini 2.0 Flash |
| Agent framework | Google ADK (`google-adk`) |
| Backend | FastAPI + Uvicorn |
| Frontend | React 18 + Vite 5 + Tailwind CSS 3 |
| Cricket data | CricketData.org free tier |
| Weather data | OpenWeatherMap Current Weather API |
| Testing | pytest + unittest.mock |

---

## Win Probability Model

The heuristic model (`win_probability.py`) is **not an ML model** — it is a transparent rule-based formula:

```
P = 0.50                          (base)
  + RRR bracket adjustment        (−0.25 to +0.15)
  + wickets-in-hand adjustment    (−0.20 to +0.10)
  + dew risk bonus                (+0.05 if "high")
  + batting depth adjustment      (±1% per rating point from 5.0)
  clamped to [0.0, 1.0]
```

This keeps the model fully explainable so the Commentator can narrate it in cricket language.
