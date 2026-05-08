import os
from datetime import date
import streamlit as st
import plotly.graph_objects as go
from fetcher import fetch
from reporter import stream_report

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")

st.set_page_config(page_title="fintel-agent", page_icon="📈", layout="centered")

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
    html, body, [class*="css"], [data-testid], p, span, div, label, h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif !important;
    }
    .hero-tag {
        display: inline-block;
        background-color: #00C85120;
        color: #00C851;
        border: 1px solid #00C85150;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 16px;
        letter-spacing: 0.3px;
    }
    .hero-title {
        font-size: 3.2rem;
        font-weight: 800;
        letter-spacing: -1.5px;
        margin: 0 0 14px 0;
        line-height: 1.1;
        color: #E6EDF3;
    }
    .hero-sub {
        font-size: 1.1rem;
        color: #8B949E;
        line-height: 1.65;
        max-width: 580px;
        margin-bottom: 8px;
        font-weight: 400;
    }
    .section-label {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.8px;
        text-transform: uppercase;
        color: #8B949E;
        margin-bottom: 8px;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.15rem !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.72rem !important;
        color: #8B949E !important;
    }
    hr { border-color: #30363D !important; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="hero-tag">AI-Powered &nbsp;·&nbsp; Live Data</div>', unsafe_allow_html=True)
st.markdown('<p style="font-size:3.2rem;font-weight:800;letter-spacing:-1.5px;margin:0 0 14px 0;line-height:1.1;color:#E6EDF3;font-family:Space Grotesk,sans-serif">📈 fintel-agent</p>', unsafe_allow_html=True)
st.markdown('<p style="font-size:1.1rem;color:#8B949E;line-height:1.65;max-width:580px;margin-bottom:8px;font-family:Space Grotesk,sans-serif">Stop guessing. Start researching. Enter any ticker and get a full equity research report — financials, risks, outlook, and analyst consensus — generated in real time.</p>', unsafe_allow_html=True)

st.divider()

ticker_input = st.text_input("Ticker", placeholder="Enter a stock ticker — e.g. AAPL, NVDA, TSLA", label_visibility="collapsed").strip().upper()

if st.button("Generate Report", type="primary", disabled=not ticker_input):
    with st.spinner("Pulling live market data..."):
        try:
            data = fetch(ticker_input)
        except ValueError as e:
            st.error(str(e))
            st.stop()
        except Exception as e:
            st.error(f"Something went wrong fetching data. Please try again. ({e})")
            st.stop()

    st.divider()
    st.markdown(f"### {data['ticker']} &nbsp;·&nbsp; {data['name']}")
    st.markdown(f"<span style='color:#8B949E; font-size:13px'>{data['sector']} &nbsp;/&nbsp; {data['industry']}</span>", unsafe_allow_html=True)
    st.markdown("")

    def fmt(val, prefix="$", suffix="", scale=None, pct=False):
        if val is None:
            return "N/A"
        if pct:
            return f"{val * 100:+.1f}%"
        if scale == "B":
            return f"{prefix}{val / 1e9:.2f}B"
        return f"{prefix}{val:.2f}{suffix}"

    ret = data["price_change_1y_pct"]
    ret_delta = f"{ret:+.1f}%" if ret else None
    ret_color = "normal" if (ret and ret >= 0) else "inverse"

    st.markdown('<p class="section-label">Market Snapshot</p>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Price", fmt(data["current_price"]))
    c2.metric("Market Cap", fmt(data["market_cap"], scale="B"))
    c3.metric("1Y Return", f"{ret:+.1f}%" if ret else "N/A", delta=ret_delta, delta_color=ret_color)
    c4.metric("Beta", fmt(data["beta"], prefix=""))

    st.markdown('<p class="section-label">Valuation</p>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("P/E (TTM)", fmt(data["pe_ratio"], prefix=""))
    c2.metric("Forward P/E", fmt(data["forward_pe"], prefix=""))
    c3.metric("P/B Ratio", fmt(data["pb_ratio"], prefix=""))
    c4.metric("Div. Yield", fmt(data["dividend_yield"], prefix="", pct=True) if data["dividend_yield"] else "N/A")

    st.markdown('<p class="section-label">Fundamentals</p>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Revenue (TTM)", fmt(data["revenue"], scale="B"))
    c2.metric("Free Cash Flow", fmt(data["free_cash_flow"], scale="B"))
    c3.metric("Profit Margin", fmt(data["profit_margin"], prefix="", pct=True) if data["profit_margin"] else "N/A")
    c4.metric("ROE", fmt(data["return_on_equity"], prefix="", pct=True) if data["return_on_equity"] else "N/A")

    st.markdown('<p class="section-label">Per Share & Leverage</p>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("EPS (TTM)", fmt(data["eps_trailing"]))
    c2.metric("EPS (Forward)", fmt(data["eps_forward"]))
    c3.metric("Debt / Equity", fmt(data["debt_to_equity"], prefix=""))
    c4.metric("Analyst Target", fmt(data["analyst_target_price"]))

    st.divider()
    st.markdown('<p class="section-label">Charts</p>', unsafe_allow_html=True)

    chart_layout = dict(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=30, b=0),
        height=280,
        font=dict(family="Space Grotesk, sans-serif", color="#8B949E"),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#21262D", zeroline=False),
    )

    # Price chart
    if data["price_history"]:
        dates = [p["date"] for p in data["price_history"]]
        closes = [p["close"] for p in data["price_history"]]
        color = "#00C851" if (data["price_change_1y_pct"] or 0) >= 0 else "#FF4444"
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates, y=closes, mode="lines",
            line=dict(color=color, width=2),
            fill="tozeroy", fillcolor=color.replace(")", ", 0.08)").replace("rgb", "rgba"),
            hovertemplate="$%{y:.2f}<extra></extra>",
        ))
        fig.update_layout(**chart_layout, title=dict(text="1-Year Price History", font=dict(size=13, color="#E6EDF3")))
        st.plotly_chart(fig, use_container_width=True)

    # Revenue and EPS side by side
    col1, col2 = st.columns(2)

    if data["revenue_trend"]:
        years = [r["year"] for r in data["revenue_trend"]]
        values = [r["value"] for r in data["revenue_trend"]]
        fig = go.Figure(go.Bar(
            x=years, y=values,
            marker_color="#00C851",
            hovertemplate="$%{y:.2f}B<extra></extra>",
        ))
        fig.update_layout(**chart_layout, title=dict(text="Annual Revenue (B)", font=dict(size=13, color="#E6EDF3")))
        col1.plotly_chart(fig, use_container_width=True)

    if data["eps_trend"]:
        years = [r["year"] for r in data["eps_trend"]]
        values = [r["value"] for r in data["eps_trend"]]
        bar_colors = ["#00C851" if v >= 0 else "#FF4444" for v in values]
        fig = go.Figure(go.Bar(
            x=years, y=values,
            marker_color=bar_colors,
            hovertemplate="$%{y:.2f}<extra></extra>",
        ))
        fig.update_layout(**chart_layout, title=dict(text="Earnings Per Share (EPS)", font=dict(size=13, color="#E6EDF3")))
        col2.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.markdown('<p class="section-label">AI Analyst Report</p>', unsafe_allow_html=True)

    def escaped_stream(data):
        for chunk in stream_report(data):
            yield chunk.replace("$", r"\$")

    try:
        escaped_text = st.write_stream(escaped_stream(data))
        report_text = escaped_text.replace(r"\$", "$")
    except Exception as e:
        st.error(f"Report generation failed. Check your API key and try again. ({e})")
        st.stop()

    os.makedirs(REPORTS_DIR, exist_ok=True)
    filename = f"{data['ticker']}_{date.today().isoformat()}.md"
    filepath = os.path.join(REPORTS_DIR, filename)
    with open(filepath, "w") as f:
        f.write(report_text)

    st.divider()
    col1, col2 = st.columns([3, 1])
    col1.caption("This report is for informational purposes only and does not constitute financial advice.")
    col2.download_button(
        label="Download (.md)",
        data=report_text,
        file_name=filename,
        mime="text/markdown",
    )
