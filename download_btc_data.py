"""
Extract BTCUSDT Daily Data to CSV
==================================

Helper script to extract the BTCUSDT-1d-*.zip files (real Binance daily
kline data) shipped with this repository into a single merged CSV file,
``btc_real_daily.csv``.

No external packages or API keys are needed — data is read entirely
from the local zip files.

Usage:
    python download_btc_data.py

This creates ``btc_real_daily.csv`` which can be fed directly into the
backtester:

    >>> from backtest_engine import GannBacktester, BacktestConfig
    >>> bt = GannBacktester(BacktestConfig())
    >>> result = bt.run("btc_real_daily.csv")
"""

from __future__ import annotations

import csv
import sys

from backtest_bitcoin import load_btcusdt_zips


def extract_and_save() -> None:
    """Extract BTC daily OHLC from BTCUSDT zips and save as CSV."""
    print("Extracting BTCUSDT data from repository zip files ...")
    try:
        bars = load_btcusdt_zips()
    except Exception as exc:
        print(f"  ✗ Failed: {exc}")
        print("  Ensure BTCUSDT-1d-*.zip files are in the repository.")
        sys.exit(1)

    print(f"  ✓ Loaded {len(bars)} daily bars")

    output = "btc_real_daily.csv"
    with open(output, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "open", "high", "low", "close", "volume"])
        for b in bars:
            writer.writerow([
                b.date.strftime("%Y-%m-%d"),
                f"{b.open:.2f}",
                f"{b.high:.2f}",
                f"{b.low:.2f}",
                f"{b.close:.2f}",
                f"{b.volume:.2f}",
            ])

    print(f"\nSaved {len(bars)} daily bars to {output}")
    print(f"  Period: {bars[0].date.strftime('%Y-%m-%d')} to "
          f"{bars[-1].date.strftime('%Y-%m-%d')}")
    print(f"  Start:  ${bars[0].close:,.2f}")
    print(f"  End:    ${bars[-1].close:,.2f}")


if __name__ == "__main__":
    extract_and_save()
