"""
SMA Checker - Daily trading tool for XLE, GME, SOFI
======================================================
Features:
  - Fetches max available daily closing prices (Yahoo Finance, no extra libs)
  - Computes every SMA from period 1 to 999
  - Shows current price vs each SMA (above/below)
  - Prints alerts when price crosses key SMAs
  - Exports all SMA data to a timestamped CSV log
  - Condensed daily summary table

Dependencies: requests only (no pandas / yfinance needed)
Usage:        python3 sma_checker.py
"""

import csv
import os
import time
import requests
from datetime import datetime

# ---------------------------------------------------------------------------
# Configuration – edit these to suit your needs
# ---------------------------------------------------------------------------

TICKERS = ["XLE", "GME", "SOFI"]   # Add any ticker here
SMA_RANGE = range(1, 1000)          # SMA periods 1-999

# SMAs shown in the condensed summary table and checked for alerts
KEY_PERIODS = [5, 10, 20, 50, 100, 200, 500, 999]

# Alerts fire when price crosses above OR below any of these SMAs
ALERT_PERIODS = [20, 50, 100, 200]

# CSV log directory (created automatically if it doesn't exist)
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sma_logs")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

# ---------------------------------------------------------------------------
# Data fetching
# ---------------------------------------------------------------------------

def fetch_close_prices(ticker: str) -> list[float]:
    """
    Download the full daily closing-price history for *ticker* from
    Yahoo Finance's v8 chart API. Returns a list ordered oldest-first.
    """
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        f"?interval=1d&range=max"
    )
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    result = data.get("chart", {}).get("result")
    if not result:
        error = data.get("chart", {}).get("error", {})
        raise ValueError(f"Yahoo Finance error for {ticker}: {error}")

    closes: list[float | None] = result[0]["indicators"]["quote"][0]["close"]
    cleaned = [c for c in closes if c is not None]
    if not cleaned:
        raise ValueError(f"No closing price data returned for {ticker}")
    return cleaned

# ---------------------------------------------------------------------------
# SMA computation (pure Python, no pandas)
# ---------------------------------------------------------------------------

def compute_all_smas(closes: list[float]) -> dict[int, float | None]:
    """
    Compute the most-recent SMA for every period 1-999.
    Returns None for periods that need more data than is available.
    """
    n = len(closes)
    results: dict[int, float | None] = {}
    for period in SMA_RANGE:
        if n >= period:
            window = closes[-period:]
            results[period] = round(sum(window) / len(window), 4)
        else:
            results[period] = None
    return results

# ---------------------------------------------------------------------------
# Alerts
# ---------------------------------------------------------------------------

def check_alerts(
    ticker: str,
    price: float,
    sma_data: dict[int, float | None],
) -> list[str]:
    """
    Return a list of alert strings for every ALERT_PERIODS SMA where
    price is within 0.5% of the SMA (near a cross) or has just crossed.
    """
    alerts = []
    for period in ALERT_PERIODS:
        sma = sma_data.get(period)
        if sma is None:
            continue
        pct_diff = ((price - sma) / sma) * 100
        if abs(pct_diff) <= 0.5:
            direction = "ABOVE" if price >= sma else "BELOW"
            alerts.append(
                f"  *** ALERT [{ticker}] Price ${price:.2f} is within 0.5% "
                f"of SMA{period} (${sma:.2f}) – currently {direction} ***"
            )
        elif pct_diff > 0:
            pass  # Price comfortably above – no alert
        else:
            pass  # Price comfortably below – no alert
    return alerts

# ---------------------------------------------------------------------------
# CSV export
# ---------------------------------------------------------------------------

def export_to_csv(
    ticker: str,
    price: float,
    sma_data: dict[int, float | None],
    run_date: str,
) -> str:
    """
    Append (or create) a daily CSV log for *ticker* inside LOG_DIR.
    Each row = one SMA period, written only for the current date.
    Returns the file path written.
    """
    os.makedirs(LOG_DIR, exist_ok=True)
    filepath = os.path.join(LOG_DIR, f"{ticker}_sma_log.csv")
    file_exists = os.path.isfile(filepath)

    with open(filepath, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["date", "ticker", "close_price", "sma_period", "sma_value"])
        for period, value in sma_data.items():
            writer.writerow([run_date, ticker, round(price, 4), period, value if value is not None else ""])

    return filepath

# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def display_full_table(
    ticker: str,
    price: float,
    sma_data: dict[int, float | None],
) -> None:
    """Print all 999 SMA values with price-vs-SMA direction for *ticker*."""
    print(f"\n{'='*68}")
    print(f"  {ticker}  |  Latest Close: ${price:.4f}")
    print(f"{'='*68}")
    print(f"{'Period':>8}  {'SMA Value':>12}  {'vs Price':>10}  {'% Diff':>8}")
    print(f"{'-'*8}  {'-'*12}  {'-'*10}  {'-'*8}")

    for period, value in sma_data.items():
        if value is not None:
            direction = "ABOVE" if price >= value else "BELOW"
            pct = ((price - value) / value) * 100
            print(f"{period:>8}  {value:>12.4f}  {direction:>10}  {pct:>+7.2f}%")
        else:
            print(f"{period:>8}  {'N/A':>12}  {'—':>10}  {'—':>8}")

    print(f"{'='*68}")


def print_summary(
    all_results: dict[str, dict[int, float | None]],
    prices: dict[str, float],
) -> None:
    """Condensed table: latest price + key SMA values with above/below tags."""
    print("\n" + "=" * 90)
    print("  DAILY SUMMARY  –  Latest Price vs Key SMAs")
    print("  " + datetime.now().strftime("%Y-%m-%d  %H:%M ET"))
    print("=" * 90)

    col_w = 9
    header = f"{'Ticker':<7}  {'Price':>8}" + "".join(
        f"  {'SMA'+str(p):>{col_w}}" for p in KEY_PERIODS
    )
    print(header)
    print("-" * len(header))

    for ticker, sma_data in all_results.items():
        price = prices[ticker]
        row = f"{ticker:<7}  {price:>8.2f}"
        for p in KEY_PERIODS:
            val = sma_data.get(p)
            if val is None:
                row += f"  {'N/A':>{col_w}}"
            else:
                tag = "▲" if price >= val else "▼"
                row += f"  {tag}{val:>{col_w-1}.2f}"
        print(row)

    print("=" * 90)
    print("  ▲ = price is ABOVE that SMA   ▼ = price is BELOW that SMA")
    print("=" * 90)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    run_date = datetime.now().strftime("%Y-%m-%d")

    print("=" * 68)
    print("  SMA Checker  |  Periods 1-999  |  Tickers:", ", ".join(TICKERS))
    print(f"  Run date: {run_date}")
    print("=" * 68)
    print("Fetching historical price data from Yahoo Finance...\n")

    all_results: dict[str, dict[int, float | None]] = {}
    prices: dict[str, float] = {}
    all_alerts: list[str] = []

    for ticker in TICKERS:
        print(f"[{ticker}] Downloading...", end=" ", flush=True)
        try:
            closes = fetch_close_prices(ticker)
            price = closes[-1]
            prices[ticker] = price
            print(f"{len(closes)} days of data.  Latest close: ${price:.4f}")

            sma_data = compute_all_smas(closes)
            all_results[ticker] = sma_data

            # Alerts
            alerts = check_alerts(ticker, price, sma_data)
            all_alerts.extend(alerts)

            # Full per-ticker table
            display_full_table(ticker, price, sma_data)

            # CSV export
            csv_path = export_to_csv(ticker, price, sma_data, run_date)
            print(f"  CSV log updated: {csv_path}")

        except Exception as exc:
            print(f"\n  ERROR – {exc}")

        time.sleep(0.5)  # polite delay between API calls

    # Summary table
    if all_results:
        print_summary(all_results, prices)

    # Print all alerts at the end so they're easy to spot
    if all_alerts:
        print("\n" + "!" * 68)
        print("  PRICE-CROSS ALERTS")
        print("!" * 68)
        for alert in all_alerts:
            print(alert)
        print("!" * 68)
    else:
        print("\n  No key SMA crossings detected today.")


if __name__ == "__main__":
    main()
