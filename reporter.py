import anthropic

_SYSTEM = """You are a senior equity research analyst with deep expertise in financial modeling, fundamental analysis, and market dynamics. You produce rigorous, structured analyst reports in markdown format.

Your reports are data-driven, objective, and written for a sophisticated investor audience. You draw clear distinctions between fact and inference, and you never fabricate data points.

Always structure your report with these exact sections:
1. **Overview** — Company snapshot, business model, competitive position
2. **Financials** — Key metrics, revenue trends, profitability, balance sheet health
3. **Trends** — Price performance, analyst sentiment, macro tailwinds/headwinds
4. **Risks** — Top risks to the investment thesis (regulatory, competitive, macro, execution)
5. **Outlook** — Forward-looking view, catalysts, price target context, overall stance

Be concise but comprehensive. Use bullet points within sections where appropriate. If a data point is unavailable, note it briefly rather than speculating."""


def _fmt(val, prefix="", suffix="", decimals=2, scale=None):
    if val is None:
        return "N/A"
    if scale == "B":
        return f"{prefix}{val / 1e9:.{decimals}f}B{suffix}"
    if scale == "M":
        return f"{prefix}{val / 1e6:.{decimals}f}M{suffix}"
    if suffix == "%":
        return f"{prefix}{round(val * 100, decimals)}{suffix}"
    return f"{prefix}{round(val, decimals)}{suffix}"


def _build_prompt(data: dict) -> str:
    d = data
    lines = [
        f"Generate a complete analyst report for **{d['ticker']} — {d['name']}**.",
        "",
        "## Raw Data",
        f"- **Sector / Industry:** {d['sector']} / {d['industry']}",
        f"- **Business Description:** {d['description']}",
        "",
        "### Valuation & Price",
        f"- Current Price: {_fmt(d['current_price'], prefix=d['currency'] + ' ')}",
        f"- Market Cap: {_fmt(d['market_cap'], scale='B', prefix='$')}",
        f"- 52-Week High / Low: {_fmt(d['52w_high'], prefix='$')} / {_fmt(d['52w_low'], prefix='$')}",
        f"- 1-Year Price Change: {_fmt(d['price_change_1y_pct'], suffix='%')}",
        f"- Trailing P/E: {_fmt(d['pe_ratio'])}",
        f"- Forward P/E: {_fmt(d['forward_pe'])}",
        f"- P/B Ratio: {_fmt(d['pb_ratio'])}",
        f"- Dividend Yield: {_fmt(d['dividend_yield'], suffix='%')}",
        f"- Beta: {_fmt(d['beta'])}",
        "",
        "### Fundamentals",
        f"- Revenue (TTM): {_fmt(d['revenue'], scale='B', prefix='$')}",
        f"- Net Income (TTM): {_fmt(d['net_income'], scale='B', prefix='$')}",
        f"- Free Cash Flow (TTM): {_fmt(d['free_cash_flow'], scale='B', prefix='$')}",
        f"- EPS (Trailing / Forward): {_fmt(d['eps_trailing'])} / {_fmt(d['eps_forward'])}",
        f"- Return on Equity: {_fmt(d['return_on_equity'], suffix='%')}",
        f"- Profit Margin: {_fmt(d['profit_margin'], suffix='%')}",
        f"- Debt-to-Equity: {_fmt(d['debt_to_equity'])}",
        "",
        "### Analyst Consensus",
        f"- Mean Target Price: {_fmt(d['analyst_target_price'], prefix='$')}",
        f"- Recommendation: {(d['recommendation'] or 'N/A').upper()}",
        "",
        "Now write the full analyst report using only the data above. Do not invent any numbers.",
    ]
    return "\n".join(lines)


def _stream_params(data: dict) -> dict:
    return dict(
        model="claude-opus-4-7",
        max_tokens=4096,
        thinking={"type": "adaptive"},
        system=[{"type": "text", "text": _SYSTEM, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": _build_prompt(data)}],
    )


def generate_report(data: dict) -> str:
    client = anthropic.Anthropic()
    full_text = ""

    with client.messages.stream(**_stream_params(data)) as stream:
        for chunk in stream.text_stream:
            full_text += chunk

    return full_text


def stream_report(data: dict):
    """Generator that yields text chunks — for use with st.write_stream()."""
    client = anthropic.Anthropic()

    with client.messages.stream(**_stream_params(data)) as stream:
        for chunk in stream.text_stream:
            yield chunk
