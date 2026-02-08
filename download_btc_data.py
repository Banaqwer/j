"""
Download Real Daily Bitcoin OHLC Data
=====================================

Helper script to download actual daily Bitcoin OHLC data for use with the
Gann algorithm backtester.  Run this on a machine with internet access,
then place the resulting ``btc_real_daily.csv`` in the same directory as
``backtest_bitcoin.py`` to use real data instead of interpolated data.

Requirements:
    pip install yfinance

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


def download_with_yfinance() -> None:
    """Download BTC daily OHLC via yfinance and save as CSV."""
    try:
        import yfinance as yf  # noqa: WPS433
    except ImportError:
        print("ERROR: yfinance is not installed.")
        print("Install it with:  pip install yfinance")
        sys.exit(1)

    print("Downloading BTC-USD daily data (Feb 2021 – present) ...")
    btc = yf.Ticker("BTC-USD")
    hist = btc.history(start="2021-02-01", end=datetime.now().strftime("%Y-%m-%d"))

    if hist.empty:
        print("ERROR: No data returned. Check your internet connection.")
        sys.exit(1)

    output = "btc_real_daily.csv"
    with open(output, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "open", "high", "low", "close", "volume"])
        for date, row in hist.iterrows():
            writer.writerow([
                date.strftime("%Y-%m-%d"),
                f"{row['Open']:.2f}",
                f"{row['High']:.2f}",
                f"{row['Low']:.2f}",
                f"{row['Close']:.2f}",
                int(row["Volume"]),
            ])

    print(f"Saved {len(hist)} daily bars to {output}")
    print(f"  Period: {hist.index[0].strftime('%Y-%m-%d')} to "
          f"{hist.index[-1].strftime('%Y-%m-%d')}")
    print(f"  Start:  ${hist.iloc[0]['Close']:,.2f}")
    print(f"  End:    ${hist.iloc[-1]['Close']:,.2f}")
    print()
    print("To backtest with this data:")
    print("  >>> from backtest_engine import GannBacktester, BacktestConfig")
    print(f'  >>> result = GannBacktester(BacktestConfig()).run("{output}")')


if __name__ == "__main__":
    download_with_yfinance()
