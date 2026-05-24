import sqlite3
import json
from datetime import datetime, timedelta

DB_PATH = "cache.db"
CACHE_TTL_DAYS = 30


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS report_cache (
            ticker TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            report TEXT NOT NULL,
            generated_at TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def get_cached(ticker: str) -> dict | None:
    conn = _connect()
    row = conn.execute(
        "SELECT data, report, generated_at FROM report_cache WHERE ticker = ?",
        (ticker,)
    ).fetchone()
    conn.close()

    if not row:
        return None

    generated_at = datetime.fromisoformat(row[2])
    if datetime.now() - generated_at > timedelta(days=CACHE_TTL_DAYS):
        return None

    return {"data": json.loads(row[0]), "report": row[1], "cached": True}


def save_to_cache(ticker: str, data: dict, report: str):
    conn = _connect()
    conn.execute("""
        INSERT INTO report_cache (ticker, data, report, generated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(ticker) DO UPDATE SET
            data = excluded.data,
            report = excluded.report,
            generated_at = excluded.generated_at
    """, (ticker, json.dumps(data), report, datetime.now().isoformat()))
    conn.commit()
    conn.close()
