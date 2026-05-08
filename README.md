# fintel-agent

AI-powered equity research tool. Enter any stock ticker and get a full analyst-style report — financials, valuation, risks, and outlook — generated in real time using Claude.

![Dark UI with metrics dashboard and streaming AI report](https://raw.githubusercontent.com/jadenbchu/fintel-agent/main/screenshot.png)

---

## What It Does

- Pulls 20+ live data points from Yahoo Finance (price, P/E, revenue, EPS, free cash flow, etc.)
- Renders an interactive metrics dashboard and 3 Plotly charts (price history, annual revenue, EPS trend)
- Streams a structured analyst report via Claude with adaptive thinking enabled
- Lets you download the report as a `.md` file

---

## Tech Stack

| Layer | Tool |
|---|---|
| AI | Claude API (`claude-opus-4-7`) — streaming, adaptive thinking, prompt caching |
| Data | yfinance — live Yahoo Finance data, no API key needed |
| UI | Streamlit — dark theme, Space Grotesk font |
| Charts | Plotly — interactive price history, revenue, EPS |

---

## Run Locally

**1. Clone and install dependencies**

```bash
git clone https://github.com/jadenbchu/fintel-agent.git
cd fintel-agent
pip install -r requirements.txt
```

**2. Set your Anthropic API key**

```bash
export ANTHROPIC_API_KEY=your_key_here
```

**3. Launch the web app**

```bash
streamlit run app.py
```

Open `http://localhost:8501`, enter a ticker like `AAPL` or `NVDA`, and click **Generate Report**.

---

## CLI Mode

```bash
python main.py AAPL
```

Saves the report as a `.md` file in the `reports/` folder.

---

## Project Structure

```
fintel-agent/
├── app.py           # Streamlit web UI
├── fetcher.py       # Pulls live data from Yahoo Finance
├── reporter.py      # Claude API integration — streaming + adaptive thinking
├── main.py          # CLI entry point
└── requirements.txt
```

---

## Why Claude?

Most AI finance tools use OpenAI. This project is built on the Anthropic SDK with features that matter for deep analysis:

- **Adaptive thinking** — Claude reasons through the data before writing
- **Prompt caching** — the system prompt is cached to reduce latency and cost on repeat runs
- **Streaming** — the report appears token by token, not all at once

---

*Built by [Jaden Chu](https://github.com/jadenbchu)*
