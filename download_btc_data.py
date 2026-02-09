"""
Download Real Daily Bitcoin OHLC Data
=====================================

Helper script to download actual daily Bitcoin OHLC data for use with the
Gann algorithm backtester.  Run this on a machine with internet access,
then place the resulting ``btc_real_daily.csv`` in the same directory as
``backtest_bitcoin.py`` to use real data when APIs are unavailable.

Data sources (tried in order):
  1. Binance public API  (BTCUSDT klines — no API key required)
  2. CoinGecko free API  (bitcoin market_chart/range — no API key required)

No external packages are required — only standard-library ``urllib``
and ``json`` are used.

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
from datetime import datetime

from backtest_bitcoin import download_btc_binance, download_btc_coingecko


def download_and_save() -> None:
    """Download BTC daily OHLC and save as CSV."""
    start = "2021-02-01"
    end = datetime.now().strftime("%Y-%m-%d")
    bars = None

    # 1. Try Binance
    print("Attempting Binance public API ...")
    try:
        bars = download_btc_binance(start=start, end=end)
        print(f"  ✓ Downloaded {len(bars)} daily bars from Binance")
    except Exception as exc:
        print(f"  ⚠ Binance failed: {exc}")

    # 2. Try CoinGecko
    if bars is None:
        print("Attempting CoinGecko free API ...")
        try:
            bars = download_btc_coingecko(start=start, end=end)
            print(f"  ✓ Downloaded {len(bars)} daily bars from CoinGecko")
        except Exception as exc:
            print(f"  ⚠ CoinGecko failed: {exc}")

    if bars is None or len(bars) == 0:
        print("ERROR: Could not download data from any source.")
        print("Check your internet connection and try again.")
        sys.exit(1)

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
                int(b.volume),
            ])

    print(f"\nSaved {len(bars)} daily bars to {output}")
    print(f"  Period: {bars[0].date.strftime('%Y-%m-%d')} to "
          f"{bars[-1].date.strftime('%Y-%m-%d')}")
    print(f"  Start:  ${bars[0].close:,.2f}")
    print(f"  End:    ${bars[-1].close:,.2f}")
    print()
    print("To backtest with this data:")
    print("  >>> from backtest_engine import GannBacktester, BacktestConfig")
    print(f'  >>> result = GannBacktester(BacktestConfig()).run("{output}")')


if __name__ == "__main__":
    download_and_save()
