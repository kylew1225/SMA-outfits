"""
SMA Checker - Calculates all Simple Moving Averages (1-999) for XLE, GME, and SOFI.

Dependencies: requests (stdlib + requests only, no pandas/yfinance required)
Usage: python3 sma_checker.py
"""

import time
import requests

TICKERS = ["XLE", "GME", "SOFI"]
SMA_RANGE = range(1, 1000)  # periods 1 through 999

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
    Fetch the maximum available daily closing prices for *ticker* from
    Yahoo Finance's v8 chart API.  Returns a plain list of floats ordered
    oldest-first.
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
    # Drop any trailing None values that Yahoo sometimes appends
    cleaned = [c for c in closes if c is not None]
    if not cleaned:
        raise ValueError(f"No closing price data returned for {ticker}")
    return cleaned


# ---------------------------------------------------------------------------
# SMA computation (pure Python)
# ---------------------------------------------------------------------------

def rolling_mean(prices: list[float], period: int) -> float:
    """Return the SMA of the last *period* prices."""
    window = prices[-period:]
    return sum(window) / len(window)


def compute_all_smas(closes: list[float]) -> dict[int, float | None]:
    """
    Compute the most-recent SMA value for every period 1-999.
    Periods that require more data than available return None.
    """
    n = len(closes)
    results: dict[int, float | None] = {}
    for period in SMA_RANGE:
        if n >= period:
            results[period] = round(rolling_mean(closes, period), 4)
        else:
            results[period] = None
    return results


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def display_results(ticker: str, sma_data: dict[int, float | None]) -> None:
    """Print every SMA value for *ticker*."""
    print(f"\n{'='*62}")
    print(f"  Ticker: {ticker}")
    print(f"{'='*62}")
    print(f"{'Period':>8}  {'SMA Value':>14}")
    print(f"{'-'*8}  {'-'*14}")
    for period, value in sma_data.items():
        if value is not None:
            print(f"{period:>8}  {value:>14.4f}")
        else:
            print(f"{period:>8}  {'N/A (not enough data)':>14}")
    print(f"{'='*62}")


def print_summary(all_results: dict[str, dict[int, float | None]]) -> None:
    """Print a condensed table of commonly-watched SMA periods."""
    key_periods = [5, 10, 20, 50, 100, 200, 500, 999]
    print("\n" + "=" * 74)
    print("  SUMMARY  –  Most Recent SMA Values")
    print("=" * 74)
    header = f"{'Ticker':<7}" + "".join(f"  SMA{p:>4}" for p in key_periods)
    print(header)
    print("-" * len(header))
    for ticker, sma_data in all_results.items():
        row = f"{ticker:<7}"
        for p in key_periods:
            val = sma_data.get(p)
            row += f"  {val:>7.2f}" if val is not None else f"  {'N/A':>7}"
        print(row)
    print("=" * 74)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 62)
    print("  SMA Checker  |  Periods 1-999  |  Tickers: XLE, GME, SOFI")
    print("=" * 62)
    print("Fetching historical price data from Yahoo Finance...\n")

    all_results: dict[str, dict[int, float | None]] = {}

    for ticker in TICKERS:
        print(f"[{ticker}] Downloading data...", end=" ", flush=True)
        try:
            closes = fetch_close_prices(ticker)
            print(f"{len(closes)} trading days available.")
            sma_data = compute_all_smas(closes)
            all_results[ticker] = sma_data
            display_results(ticker, sma_data)
        except Exception as exc:
            print(f"\n  ERROR – {exc}")
        # Be polite to the API between requests
        time.sleep(0.5)

    if all_results:
        print_summary(all_results)


if __name__ == "__main__":
    main()
