"""
Download Daily Kline Data from the Binance Public API
=====================================================

Downloads ETHUSDT and SOLUSDT (or any symbol) 1-day kline data from the
Binance public ``/api/v3/klines`` endpoint.  **No API key is required.**

Each month of data is saved as a zip file containing a CSV, matching the
exact same format used for the BTCUSDT-1d-*.zip files already in this
repository:

    open_time, open, high, low, close, volume, close_time,
    quote_volume, count, taker_buy_base, taker_buy_quote, ignore

Requirements:
    Python 3.8+ (uses only the standard library — no pip install needed)

Usage:
------
    # Download both Ethereum and Solana (past 5 years):
    python download_binance_data.py

    # Download only Ethereum:
    python download_binance_data.py --symbols ETHUSDT

    # Download Solana for a specific date range:
    python download_binance_data.py --symbols SOLUSDT --start-year 2022 --end-year 2024

    # Download to a specific directory:
    python download_binance_data.py --output-dir ./data

    # Download any Binance trading pair:
    python download_binance_data.py --symbols BNBUSDT DOGEUSDT

After downloading, the zip files can be loaded by adapting the existing
``load_binance_btc_data()`` function in ``backtest_bitcoin_real.py``
(change the glob pattern from ``BTCUSDT-1d-*.zip`` to the desired symbol).
"""

from __future__ import annotations

import csv
import io
import json
import os
import sys
import time
import zipfile
from datetime import datetime, timezone
from typing import List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# Binance public API base URL (no API key required)
BINANCE_KLINES_URL = "https://api.binance.com/api/v3/klines"

# Default symbols to download
DEFAULT_SYMBOLS = ["ETHUSDT", "SOLUSDT"]

# Default date range (2021 onwards — covers ~5 years of crypto history)
DEFAULT_START_YEAR = 2021
DEFAULT_END_YEAR = datetime.now().year


def fetch_klines(
    symbol: str,
    interval: str,
    start_ms: int,
    end_ms: int,
    limit: int = 1000,
) -> list:
    """
    Fetch kline data from the Binance public API.

    Parameters
    ----------
    symbol : str
        Trading pair (e.g. 'ETHUSDT', 'SOLUSDT').
    interval : str
        Kline interval (e.g. '1d').
    start_ms : int
        Start time in Unix milliseconds.
    end_ms : int
        End time in Unix milliseconds.
    limit : int
        Max number of klines to return (default 1000, Binance max).

    Returns
    -------
    list
        List of kline arrays from the Binance API.
    """
    url = (
        f"{BINANCE_KLINES_URL}"
        f"?symbol={symbol}"
        f"&interval={interval}"
        f"&startTime={start_ms}"
        f"&endTime={end_ms}"
        f"&limit={limit}"
    )
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=30) as resp:  # noqa: S310
        return json.loads(resp.read().decode("utf-8"))


def datetime_to_ms(year: int, month: int, day: int = 1) -> int:
    """Convert a UTC date to Unix milliseconds."""
    dt = datetime(year, month, day, tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


def download_symbol(
    symbol: str,
    interval: str = "1d",
    start_year: int = DEFAULT_START_YEAR,
    end_year: int = DEFAULT_END_YEAR,
    output_dir: str = ".",
) -> int:
    """
    Download all monthly kline zip files for a single symbol.

    Parameters
    ----------
    symbol : str
        Trading pair (e.g. 'ETHUSDT').
    interval : str
        Kline interval (default '1d').
    start_year : int
        First year to download.
    end_year : int
        Last year to download.
    output_dir : str
        Directory to write zip files.

    Returns
    -------
    int
        Total number of bars downloaded.
    """
    os.makedirs(output_dir, exist_ok=True)

    total_bars = 0
    total_files = 0
    now = datetime.now(timezone.utc)

    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            # Calculate month boundaries
            start_ms = datetime_to_ms(year, month)
            if month == 12:
                end_ms = datetime_to_ms(year + 1, 1) - 1
            else:
                end_ms = datetime_to_ms(year, month + 1) - 1

            # Skip future months
            month_start = datetime(year, month, 1, tzinfo=timezone.utc)
            if month_start > now:
                continue

            month_str = f"{month:02d}"
            csv_name = f"{symbol}-{interval}-{year}-{month_str}.csv"
            zip_name = f"{symbol}-{interval}-{year}-{month_str}.zip"
            zip_path = os.path.join(output_dir, zip_name)

            print(f"  Downloading {year}-{month_str} ... ", end="", flush=True)

            try:
                klines = fetch_klines(symbol, interval, start_ms, end_ms)
            except (HTTPError, URLError, OSError) as exc:
                print(f"ERROR: {exc}")
                time.sleep(1)
                continue

            if not klines:
                print("no data (skipped)")
                continue

            # Write CSV into a zip file (matches Binance format, no header)
            csv_buffer = io.StringIO()
            writer = csv.writer(csv_buffer)
            for kline in klines:
                writer.writerow(kline)

            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.writestr(csv_name, csv_buffer.getvalue())

            bar_count = len(klines)
            total_bars += bar_count
            total_files += 1
            print(f"{bar_count} bars -> {zip_name}")

            # Small delay to respect rate limits (250ms)
            time.sleep(0.25)

    print(f"  {symbol}: {total_files} files, {total_bars} total bars")
    return total_bars


def main(
    symbols: Optional[List[str]] = None,
    start_year: int = DEFAULT_START_YEAR,
    end_year: int = DEFAULT_END_YEAR,
    output_dir: str = ".",
) -> None:
    """Download kline data for the specified symbols."""
    if symbols is None:
        symbols = DEFAULT_SYMBOLS

    print("=" * 64)
    print("  Binance Daily Kline Downloader")
    print("=" * 64)
    print(f"  Symbols:  {', '.join(symbols)}")
    print(f"  Interval: 1d (daily)")
    print(f"  Period:   {start_year}-01 to {end_year}-12")
    print(f"  Output:   {os.path.abspath(output_dir)}")
    print()

    grand_total = 0
    for symbol in symbols:
        print(f"{'─' * 64}")
        print(f"  {symbol}")
        print(f"{'─' * 64}")
        bars = download_symbol(
            symbol=symbol,
            start_year=start_year,
            end_year=end_year,
            output_dir=output_dir,
        )
        grand_total += bars
        print()

    print("=" * 64)
    print("  Download complete!")
    print(f"  Grand total: {grand_total} bars across {len(symbols)} symbols")
    print("=" * 64)
    print()
    print("To use this data in a backtest, adapt the loader in")
    print("backtest_bitcoin_real.py — change the glob pattern from")
    print("  BTCUSDT-1d-*.zip  to  ETHUSDT-1d-*.zip  (or SOLUSDT)")
    print()
    print("Or use the PowerShell script for Windows:")
    print("  .\\download_eth_data.ps1 -Symbol ETHUSDT")
    print("  .\\download_eth_data.ps1 -Symbol SOLUSDT")


def parse_args() -> dict:
    """Parse command-line arguments (stdlib only, no argparse dependency)."""
    args = {
        "symbols": None,
        "start_year": DEFAULT_START_YEAR,
        "end_year": DEFAULT_END_YEAR,
        "output_dir": ".",
    }
    argv = sys.argv[1:]
    i = 0
    while i < len(argv):
        if argv[i] in ("--symbols", "-s"):
            symbols = []
            i += 1
            while i < len(argv) and not argv[i].startswith("-"):
                symbols.append(argv[i].upper())
                i += 1
            args["symbols"] = symbols
        elif argv[i] == "--start-year":
            i += 1
            args["start_year"] = int(argv[i])
            i += 1
        elif argv[i] == "--end-year":
            i += 1
            args["end_year"] = int(argv[i])
            i += 1
        elif argv[i] in ("--output-dir", "-o"):
            i += 1
            args["output_dir"] = argv[i]
            i += 1
        elif argv[i] in ("--help", "-h"):
            print(__doc__)
            sys.exit(0)
        else:
            print(f"Unknown argument: {argv[i]}")
            print("Use --help for usage information.")
            sys.exit(1)
    return args


if __name__ == "__main__":
    parsed = parse_args()
    main(**parsed)
