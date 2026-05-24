from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fetcher import fetch
from reporter import generate_report
from cache import get_cached, save_to_cache

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/report/{ticker}")
def get_report(ticker: str):
    cached = get_cached(ticker.upper())
    if cached:
        return cached

    try:
        data = fetch(ticker)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch data: {e}")

    try:
        report = generate_report(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {e}")

    save_to_cache(ticker.upper(), data, report)
    return {"data": data, "report": report, "cached": False}
