import yfinance as yf
import pandas as pd
import requests

_session = requests.Session()
_session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
})


def fetch(ticker: str) -> dict:
    try:
        t = yf.Ticker(ticker, session=_session)
        info = t.info
    except Exception as e:
        raise ValueError(f"Failed to retrieve data for '{ticker}': {e}")

    if not info or info.get("quoteType") is None:
        raise ValueError(f"'{ticker}' returned empty data from Yahoo Finance. This may be a rate limit issue — try again in a moment.")

    quote_type = info.get("quoteType", "")
    if quote_type not in ("EQUITY", "ETF"):
        raise ValueError(f"'{ticker}' is a {quote_type}, not a stock or ETF. Try a ticker like AAPL or NVDA.")

    hist = t.history(period="1y")
    price_change_1y = None
    price_history = []
    if not hist.empty:
        price_change_1y = round(
            (hist["Close"].iloc[-1] - hist["Close"].iloc[0]) / hist["Close"].iloc[0] * 100, 2
        )
        h = hist.reset_index()
        price_history = [
            {"date": str(row["Date"].date()), "close": round(float(row["Close"]), 2)}
            for _, row in h.iterrows()
        ]

    financials = t.financials  # annual income statement, columns = dates
    balance = t.balance_sheet
    cashflow = t.cashflow

    def latest(df, *row_names):
        for name in row_names:
            if df is not None and name in df.index and not df.empty:
                val = df.loc[name].iloc[0]
                if pd.notna(val):
                    return int(val)
        return None

    revenue = latest(financials, "Total Revenue")
    net_income = latest(financials, "Net Income")
    operating_cf = latest(cashflow, "Operating Cash Flow", "Total Cash From Operating Activities")
    capex = latest(cashflow, "Capital Expenditure")
    free_cash_flow = (operating_cf + capex) if (operating_cf and capex) else None

    total_debt = latest(balance, "Total Debt", "Long Term Debt")
    equity = latest(balance, "Stockholders Equity", "Total Stockholder Equity")
    debt_to_equity = round(total_debt / equity, 2) if (total_debt and equity and equity != 0) else None

    def trend(df, *row_names):
        for name in row_names:
            if df is not None and not df.empty and name in df.index:
                row = df.loc[name]
                result = []
                for col in sorted(row.index, reverse=True)[:4]:
                    val = row[col]
                    if pd.notna(val):
                        result.append({"year": str(col.year), "value": round(float(val), 2)})
                return result[::-1]
        return []

    revenue_trend = trend(financials, "Total Revenue")
    for item in revenue_trend:
        item["value"] = round(item["value"] / 1e9, 2)

    eps_trend = trend(financials, "Diluted EPS", "Basic EPS")

    return {
        "ticker": ticker.upper(),
        "name": info.get("longName") or info.get("shortName", ticker),
        "sector": info.get("sector", "N/A"),
        "industry": info.get("industry", "N/A"),
        "description": (info.get("longBusinessSummary") or "")[:1000],
        "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
        "currency": info.get("currency", "USD"),
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "pb_ratio": info.get("priceToBook"),
        "dividend_yield": info.get("dividendYield"),
        "52w_high": info.get("fiftyTwoWeekHigh"),
        "52w_low": info.get("fiftyTwoWeekLow"),
        "price_change_1y_pct": price_change_1y,
        "revenue": revenue,
        "net_income": net_income,
        "eps_trailing": info.get("trailingEps"),
        "eps_forward": info.get("forwardEps"),
        "free_cash_flow": free_cash_flow,
        "debt_to_equity": debt_to_equity,
        "return_on_equity": info.get("returnOnEquity"),
        "profit_margin": info.get("profitMargins"),
        "analyst_target_price": info.get("targetMeanPrice"),
        "recommendation": info.get("recommendationKey"),
        "beta": info.get("beta"),
        "price_history": price_history,
        "revenue_trend": revenue_trend,
        "eps_trend": eps_trend,
    }
