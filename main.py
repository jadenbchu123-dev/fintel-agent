import sys
import os
from datetime import date
from fetcher import fetch
from reporter import generate_report

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")


def save_report(ticker: str, report: str) -> str:
    os.makedirs(REPORTS_DIR, exist_ok=True)
    filename = f"{ticker}_{date.today().isoformat()}.md"
    path = os.path.join(REPORTS_DIR, filename)
    with open(path, "w") as f:
        f.write(report)
    return path


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <TICKER>")
        print("Example: python main.py AAPL")
        sys.exit(1)

    ticker = sys.argv[1].upper()
    print(f"Fetching data for {ticker}...")

    data = fetch(ticker)

    print(f"Generating analyst report for {data['name']}...\n")
    report = generate_report(data)

    path = save_report(ticker, report)
    print(f"\nReport saved to: {path}")


if __name__ == "__main__":
    main()
