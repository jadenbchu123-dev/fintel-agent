import { useState } from 'react'
import Markdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import {
  AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, Tooltip, ResponsiveContainer
} from 'recharts'
import './App.css'

const tooltipStyle = {
  backgroundColor: '#161b22',
  border: '1px solid #30363d',
  borderRadius: '6px',
  color: '#e6edf3',
  fontSize: '12px',
}

function MetricCard({ label, value, sentiment }) {
  return (
    <div className="metric-card">
      <div className="metric-label">{label}</div>
      <div className={`metric-value ${sentiment ?? ''}`}>{value ?? 'N/A'}</div>
    </div>
  )
}

function SectionLabel({ text }) {
  return <p className="section-label">{text}</p>
}

function App() {
  const [ticker, setTicker] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    if (!ticker) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/report/${ticker.toUpperCase()}`)
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail)
      }
      const json = await res.json()
      setResult(json)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const d = result?.data
  const priceUp = (d?.price_change_1y_pct ?? 0) >= 0
  const priceColor = priceUp ? '#00c851' : '#ff4444'

  return (
    <div className="container">
      <div className="header">
        <h1>📈 fintel-agent</h1>
        <p>Enter a ticker to generate an AI-powered equity research report</p>
      </div>

      <form onSubmit={handleSubmit} className="search-form">
        <input
          type="text"
          placeholder="e.g. AAPL, NVDA, TSLA"
          value={ticker}
          onChange={e => setTicker(e.target.value)}
        />
        <button type="submit" disabled={loading || !ticker}>
          {loading ? 'Generating...' : 'Generate Report'}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      {d && (
        <div className="results">
          <div className="ticker-header">
            <h2>{d.ticker} — {d.name}</h2>
            <p className="sector">{d.sector} / {d.industry}</p>
          </div>

          <SectionLabel text="Market Snapshot" />
          <div className="metrics-grid">
            <MetricCard label="Price" value={d.current_price ? `$${d.current_price}` : null} />
            <MetricCard label="Market Cap" value={d.market_cap ? `$${(d.market_cap / 1e9).toFixed(2)}B` : null} />
            <MetricCard
              label="1Y Return"
              value={d.price_change_1y_pct ? `${d.price_change_1y_pct > 0 ? '+' : ''}${d.price_change_1y_pct}%` : null}
              sentiment={d.price_change_1y_pct >= 0 ? 'positive' : 'negative'}
            />
            <MetricCard label="Beta" value={d.beta?.toFixed(2)} />
          </div>

          <SectionLabel text="Valuation" />
          <div className="metrics-grid">
            <MetricCard label="P/E (TTM)" value={d.pe_ratio?.toFixed(2)} />
            <MetricCard label="Forward P/E" value={d.forward_pe?.toFixed(2)} />
            <MetricCard label="P/B Ratio" value={d.pb_ratio?.toFixed(2)} />
            <MetricCard label="Div. Yield" value={d.dividend_yield ? `${(d.dividend_yield * 100).toFixed(2)}%` : null} />
          </div>

          <SectionLabel text="Fundamentals" />
          <div className="metrics-grid">
            <MetricCard label="Revenue (TTM)" value={d.revenue ? `$${(d.revenue / 1e9).toFixed(2)}B` : null} />
            <MetricCard label="Free Cash Flow" value={d.free_cash_flow ? `$${(d.free_cash_flow / 1e9).toFixed(2)}B` : null} />
            <MetricCard label="Profit Margin" value={d.profit_margin ? `${(d.profit_margin * 100).toFixed(1)}%` : null} />
            <MetricCard label="ROE" value={d.return_on_equity ? `${(d.return_on_equity * 100).toFixed(1)}%` : null} />
          </div>

          <SectionLabel text="Charts" />

          {d.price_history?.length > 0 && (
            <div className="chart-card">
              <div className="chart-title">1-Year Price History</div>
              <ResponsiveContainer width="100%" height={220}>
                <AreaChart data={d.price_history}>
                  <defs>
                    <linearGradient id="priceGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={priceColor} stopOpacity={0.15} />
                      <stop offset="95%" stopColor={priceColor} stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="date" tick={{ fill: '#8b949e', fontSize: 11 }} tickLine={false} interval={60} />
                  <YAxis tick={{ fill: '#8b949e', fontSize: 11 }} tickLine={false} axisLine={false} tickFormatter={v => `$${v}`} />
                  <Tooltip contentStyle={tooltipStyle} formatter={v => [`$${v}`, 'Close']} />
                  <Area type="monotone" dataKey="close" stroke={priceColor} strokeWidth={2} fill="url(#priceGrad)" dot={false} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}

          <div className="chart-row">
            {d.revenue_trend?.length > 0 && (
              <div className="chart-card">
                <div className="chart-title">Annual Revenue</div>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={d.revenue_trend}>
                    <XAxis dataKey="year" tick={{ fill: '#8b949e', fontSize: 11 }} tickLine={false} />
                    <YAxis tick={{ fill: '#8b949e', fontSize: 11 }} tickLine={false} axisLine={false} tickFormatter={v => `$${v}B`} />
                    <Tooltip contentStyle={tooltipStyle} formatter={v => [`$${v}B`, 'Revenue']} />
                    <Bar dataKey="value" fill="#00c851" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}

            {d.eps_trend?.length > 0 && (
              <div className="chart-card">
                <div className="chart-title">Earnings Per Share</div>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={d.eps_trend}>
                    <XAxis dataKey="year" tick={{ fill: '#8b949e', fontSize: 11 }} tickLine={false} />
                    <YAxis tick={{ fill: '#8b949e', fontSize: 11 }} tickLine={false} axisLine={false} tickFormatter={v => `$${v}`} />
                    <Tooltip contentStyle={tooltipStyle} formatter={v => [`$${v}`, 'EPS']} />
                    <Bar dataKey="value" radius={[4, 4, 0, 0]} fill="#00c851" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          <SectionLabel text="AI Analyst Report" />
          <div className="report-card">
            <Markdown remarkPlugins={[remarkGfm]}>{result.report}</Markdown>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
