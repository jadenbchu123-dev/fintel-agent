# fintel-agent

AI-powered equity research tool. Enter any stock ticker and get a full analyst-style report — financials, valuation, risks, and outlook — generated using Claude.

**Live app:** [fintel-agent.vercel.app](https://fintel-agent.vercel.app)

![Dark UI with metrics dashboard and AI report](https://raw.githubusercontent.com/jadenbchu123-dev/fintel-agent/main/screenshot.png)

---

## What It Does

- Pulls 20+ live data points from Yahoo Finance (price, P/E, revenue, EPS, free cash flow, etc.)
- Renders an interactive metrics dashboard with 3 charts (price history, annual revenue, EPS trend)
- Generates a structured analyst report via Claude with adaptive thinking enabled
- Caches reports for 30 days to reduce API costs

---

## Tech Stack

| Layer | Tool |
|---|---|
| AI | Claude API (`claude-opus-4-7`) — adaptive thinking, prompt caching |
| Data | yfinance — live Yahoo Finance data |
| Backend | FastAPI — REST API with SQLite caching |
| Frontend | React + Vite — recharts for data visualization |
| Deployment | Render (backend) · Vercel (frontend) |

---

## Architecture

```
React frontend (Vercel)
    ↓ GET /report/{ticker}
FastAPI backend (Render)
    ↓ cache miss
fetcher.py → yfinance
reporter.py → Claude API
    ↓
SQLite cache (30-day TTL)
```

---

## Run Locally

**1. Clone the repo**

```bash
git clone https://github.com/jadenbchu123-dev/fintel-agent.git
cd fintel-agent
```

**2. Start the backend**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here
uvicorn api:app --reload
```

**3. Start the frontend**

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`, enter a ticker like `AAPL` or `NVDA`, and click **Generate Report**.

---

## Project Structure

```
fintel-agent/
├── api.py           # FastAPI backend — REST endpoints, CORS
├── fetcher.py       # Pulls live data from Yahoo Finance
├── reporter.py      # Claude API integration — adaptive thinking, prompt caching
├── cache.py         # SQLite caching layer — 30-day TTL
├── frontend/        # React + Vite UI
│   └── src/
│       ├── App.jsx  # Main UI component
│       └── App.css  # Styles
└── requirements.txt
```

---

## Why Claude?

- **Adaptive thinking** — Claude reasons through the data before writing
- **Prompt caching** — system prompt is cached to reduce latency and cost
- **Data-grounded** — report is generated from live financial data, not training knowledge

---

*Built by [Jaden Chu](https://github.com/jadenbchu123-dev) · [LinkedIn](https://www.linkedin.com/in/jaden-chu-68b52b34b/)*
