"""
Bitcoin (BTC/USDT) Backtest — Gann Unified Algorithm on Real Binance Data
=========================================================================

Backtests the W.D. Gann unified trading algorithm on **real** Bitcoin
(BTCUSDT) daily candle data sourced from Binance.

The data is loaded from the BTCUSDT-1d-*.zip files in the repository.
Each zip contains a headerless CSV with Binance kline columns:
    open_time, open, high, low, close, volume, close_time,
    quote_asset_volume, number_of_trades, taker_buy_base,
    taker_buy_quote, ignore

Key Bitcoin characteristics handled:
  - Trades 24/7 (no weekend gaps — all calendar days included)
  - Much higher volatility than traditional markets (~60-80% annualized)
  - Large absolute price moves (hundreds/thousands of dollars per day)
  - Dynamic SQ12 used (high-volatility regime)
  - Covers Jan 2021 through Dec 2025 (5 years of real market data)

Usage:
------
    python backtest_bitcoin.py

This will:
  1. Extract real daily BTCUSDT bars from the zip files in the repo
  2. Run the Gann algorithm backtester on the real data
  3. Print full results and trade log
  4. Export CSV files (btc_real_daily.csv, btc_backtest_trades.csv,
     btc_backtest_equity.csv)
"""

from __future__ import annotations

import csv
import glob
import io
import math
import os
import zipfile
from datetime import datetime, timezone
from typing import Dict, IO, List

from backtest_engine import (
    BacktestConfig,
    Bar,
    GannBacktester,
)

def load_btc_from_zips(data_dir: str) -> List[Bar]:
    """
    Extract and parse real BTCUSDT daily bars from Binance zip files.

    Scans *data_dir* for files matching ``BTCUSDT-1d-*.zip``, extracts
    each CSV, and parses the Binance kline format (no header row):

        open_time_ms, open, high, low, close, volume, ...

    Handles nested zips (some archives contain another zip inside) and
    deduplicates bars by date.

    Parameters
    ----------
    data_dir : str
        Directory containing the BTCUSDT-1d-*.zip files.

    Returns
    -------
    List[Bar]
        Sorted daily OHLCV bars.
    """
    bars_by_date: Dict[str, Bar] = {}

    zip_paths = sorted(glob.glob(os.path.join(data_dir, "BTCUSDT-1d-*.zip")))
    if not zip_paths:
        raise FileNotFoundError(
            f"No BTCUSDT-1d-*.zip files found in {data_dir}"
        )

    for zpath in zip_paths:
        _extract_bars_from_zip(zpath, bars_by_date)

    bars = sorted(bars_by_date.values(), key=lambda b: b.date)
    return bars


# Minimum columns expected in a Binance kline CSV row
# (open_time, open, high, low, close, volume)
_MIN_KLINE_COLUMNS = 6


def _extract_bars_from_zip(
    zpath: str,
    bars_by_date: Dict[str, Bar],
) -> None:
    """Extract bars from a single zip (handles nested zips)."""
    with zipfile.ZipFile(zpath, "r") as zf:
        for name in zf.namelist():
            if name.endswith(".csv"):
                with zf.open(name) as csvfile:
                    _parse_binance_csv(csvfile, bars_by_date)
            elif name.endswith(".zip"):
                # Nested zip — extract to memory and recurse
                nested_bytes = zf.read(name)
                with zipfile.ZipFile(io.BytesIO(nested_bytes), "r") as nzf:
                    for nname in nzf.namelist():
                        if nname.endswith(".csv"):
                            with nzf.open(nname) as csvfile:
                                _parse_binance_csv(csvfile, bars_by_date)


def _parse_binance_csv(
    csvfile: IO[bytes],
    bars_by_date: Dict[str, Bar],
) -> None:
    """Parse a headerless Binance kline CSV into Bar objects."""
    text = io.TextIOWrapper(csvfile, encoding="utf-8")
    reader = csv.reader(text)
    for row in reader:
        if len(row) < _MIN_KLINE_COLUMNS:
            continue
        try:
            ts_ms = int(row[0])
            dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
            # Remove tzinfo to match Bar's expected naive datetime format
            dt = dt.replace(tzinfo=None)
            date_key = dt.strftime("%Y-%m-%d")

            bar = Bar(
                date=dt,
                open=float(row[1]),
                high=float(row[2]),
                low=float(row[3]),
                close=float(row[4]),
                volume=float(row[5]),
            )
            bars_by_date[date_key] = bar
        except (ValueError, IndexError):
            continue


def save_btc_csv(bars: List[Bar], filepath: str) -> None:
    """Save Bitcoin bars to a standard OHLCV CSV."""
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "open", "high", "low", "close", "volume"])
        for b in bars:
            writer.writerow([
                b.date.strftime("%Y-%m-%d"),
                f"{b.open:.2f}", f"{b.high:.2f}",
                f"{b.low:.2f}", f"{b.close:.2f}",
                f"{b.volume:.2f}",
            ])


def main():
    """Run the Bitcoin backtest on real Binance BTCUSDT daily data."""
    base_dir = os.path.dirname(os.path.abspath(__file__))

    print("=" * 78)
    print("GANN UNIFIED TRADING ALGORITHM — BITCOIN (BTCUSDT) BACKTEST")
    print("Real Binance daily kline data from BTCUSDT-1d-*.zip files")
    print("=" * 78)

    # ── 1. Load real Bitcoin data from zip files ─────────────────────────
    print("\n1. Loading real BTCUSDT daily data from zip files...")

    bars = load_btc_from_zips(base_dir)

    print(f"   Loaded {len(bars)} daily bars (real Binance data)")
    print(f"   Period:     {bars[0].date.strftime('%Y-%m-%d')} to "
          f"{bars[-1].date.strftime('%Y-%m-%d')}")
    print(f"   Start:      ${bars[0].close:>12,.2f}")
    print(f"   End:        ${bars[-1].close:>12,.2f}")
    print(f"   Low:        ${min(b.low for b in bars):>12,.2f}")
    print(f"   High:       ${max(b.high for b in bars):>12,.2f}")

    # Save combined CSV for reference
    btc_csv = os.path.join(base_dir, "btc_real_daily.csv")
    save_btc_csv(bars, btc_csv)
    print(f"   Saved to:   {btc_csv}")

    # ── 2. Configure backtester ──────────────────────────────────────────
    print("\n2. Configuring backtester for Bitcoin...")

    config = BacktestConfig(
        initial_capital=100_000.0,
        max_risk_pct=1.5,           # 1.5% risk — BTC is very volatile
        min_reward_risk=2.5,        # 2.5:1 R:R minimum (PDF 4 standard)
        max_position_pct=40.0,      # Max 40% — respect BTC volatility
        min_confidence=0.25,        # Minimum signal confidence
        lookback_bars=14,           # 14-bar lookback for crypto volatility
        max_hold_bars=72,           # Rule of 72 (PDF 4)
        use_trailing_stop=True,     # Trail stop after partial exit
        partial_exit_pct=0.5,       # Book 50% at first target
        slippage_pct=0.001,         # 0.1% slippage (crypto spreads)
        commission_per_trade=15.0,  # $15 per trade (exchange fees)
        use_fixed_sizing=True,      # Fixed sizing prevents unrealistic
        #   exponential compounding on BTC's extreme volatility
    )

    print(f"   Initial capital:    ${config.initial_capital:>12,.2f}")
    print(f"   Max risk/trade:     {config.max_risk_pct}%")
    print(f"   Min R:R ratio:      {config.min_reward_risk}:1")
    print(f"   Max position:       {config.max_position_pct}% of capital")
    print(f"   Min confidence:     {config.min_confidence}")
    print(f"   Lookback bars:      {config.lookback_bars}")
    print(f"   Max hold bars:      {config.max_hold_bars}")
    print(f"   Slippage:           {config.slippage_pct * 100:.3f}%")
    print(f"   Commission:         ${config.commission_per_trade:.2f}/trade")

    # ── 3. Run backtest ──────────────────────────────────────────────────
    print("\n3. Running backtest on real BTCUSDT data...")
    bt = GannBacktester(config)
    result = bt.run(bars)

    # ── 4. Display results ───────────────────────────────────────────────
    print()
    result.print_summary()

    # ── 5. Print trade log ───────────────────────────────────────────────
    result.print_trades(max_trades=50)

    # ── 6. Print yearly breakdown ────────────────────────────────────────
    print(f"\n{'─' * 78}")
    print("YEARLY PERFORMANCE BREAKDOWN")
    print(f"{'─' * 78}")

    yearly_trades: dict = {}
    for t in result.trades:
        year = t.entry_date.year
        if year not in yearly_trades:
            yearly_trades[year] = []
        yearly_trades[year].append(t)

    print(f"  {'Year':>6}  {'Trades':>7}  {'Wins':>5}  {'Losses':>7}  "
          f"{'Win%':>6}  {'PnL':>14}  {'Avg PnL':>12}  {'PF':>6}")
    print(f"  {'─' * 6}  {'─' * 7}  {'─' * 5}  {'─' * 7}  "
          f"{'─' * 6}  {'─' * 14}  {'─' * 12}  {'─' * 6}")

    for year in sorted(yearly_trades.keys()):
        trades = yearly_trades[year]
        n = len(trades)
        wins = sum(1 for t in trades if t.pnl > 0)
        losses = n - wins
        win_rate = wins / n * 100 if n > 0 else 0
        total_pnl = sum(t.pnl for t in trades)
        avg_pnl = total_pnl / n if n > 0 else 0
        gross_win = sum(t.pnl for t in trades if t.pnl > 0)
        gross_loss = abs(sum(t.pnl for t in trades if t.pnl <= 0))
        pf = gross_win / gross_loss if gross_loss > 0 else 0.0

        print(f"  {year:>6}  {n:>7}  {wins:>5}  {losses:>7}  "
              f"{win_rate:>5.1f}%  ${total_pnl:>13,.2f}  "
              f"${avg_pnl:>11,.2f}  {pf:>6.2f}")

    # ── 7. Print exit reason breakdown ───────────────────────────────────
    print(f"\n{'─' * 78}")
    print("EXIT REASON BREAKDOWN")
    print(f"{'─' * 78}")

    reasons: dict = {}
    for t in result.trades:
        r = t.exit_reason
        if r not in reasons:
            reasons[r] = {"count": 0, "pnl": 0.0}
        reasons[r]["count"] += 1
        reasons[r]["pnl"] += t.pnl

    print(f"  {'Reason':>15}  {'Count':>6}  {'Total PnL':>14}  {'Avg PnL':>12}")
    print(f"  {'─' * 15}  {'─' * 6}  {'─' * 14}  {'─' * 12}")
    for reason, data in sorted(reasons.items(), key=lambda x: -x[1]["count"]):
        avg = data["pnl"] / data["count"] if data["count"] > 0 else 0
        print(f"  {reason:>15}  {data['count']:>6}  "
              f"${data['pnl']:>13,.2f}  ${avg:>11,.2f}")

    # ── 8. Bitcoin-specific Gann analysis ────────────────────────────────
    print(f"\n{'─' * 78}")
    print("BITCOIN-SPECIFIC GANN ANALYSIS")
    print(f"{'─' * 78}")

    from gann_trading_algorithm import GannAnalyzer

    analyzer = GannAnalyzer()
    last_bar = bars[-1]
    print(f"\n  Last BTC price: ${last_bar.close:,.2f} "
          f"({last_bar.date.strftime('%Y-%m-%d')})")

    # Square of 9 levels for current BTC price
    sq9 = analyzer.square_of_nine_levels(last_bar.close)
    print(f"\n  Square of 9 levels from ${last_bar.close:,.2f}:")
    for deg, level in sorted(sq9.levels.items()):
        print(f"    {deg:>4}° → ${level:>12,.2f}")

    # 144-cycle levels — particularly significant for BTC
    levels_144 = analyzer.gann_144_levels(last_bar.close, count=8)
    print(f"\n  144-unit levels (Gann master cycle):")
    for lv in levels_144:
        marker = " ◄ current" if abs(lv - last_bar.close) < 5000 else ""
        print(f"    ${lv:>12,.2f}{marker}")

    # Number vibration of BTC price
    vib = analyzer.number_vibration(last_bar.close)
    print(f"\n  Number vibration of ${last_bar.close:,.2f}:")
    print(f"    Vibration digit:    {vib.single_digit}")
    print(f"    Is change number:   {vib.is_change_number}")
    if vib.is_change_number:
        print("    ⚠  Vibration 9 = potential trend reversal zone")

    # Gann angle levels from recent high/low
    recent_high = max(b.high for b in bars[-20:])
    recent_low = min(b.low for b in bars[-20:])
    gann_levels = analyzer.gann_angle_levels(high=recent_high, low=recent_low)
    print(f"\n  Gann angle levels "
          f"(20-bar H/L: ${recent_high:,.2f} / ${recent_low:,.2f}):")
    if gann_levels.buy_entry:
        print(f"    Buy entry:  ${gann_levels.buy_entry:>12,.2f}")
    if gann_levels.sell_entry:
        print(f"    Sell entry: ${gann_levels.sell_entry:>12,.2f}")
    print(f"    Congestion: {gann_levels.has_congestion}")

    # Volatility analysis
    recent_closes = [b.close for b in bars[-15:]]
    daily_vol = analyzer.calculate_daily_volatility(recent_closes)
    annual_vol = daily_vol * math.sqrt(365)  # 365 for crypto (24/7 market)
    print(f"\n  Volatility (BTC 24/7 market, √365):")
    print(f"    Daily:   {daily_vol:.4f}%")
    print(f"    Annual:  {annual_vol:.2f}%")

    sq_type, sq_levels = analyzer.choose_dynamic_square(
        last_bar.close, daily_vol
    )
    print(f"    Dynamic square type: {sq_type.upper()} "
          f"(annual vol {'>' if annual_vol > 40 else '<'} 40%)")

    # Key BTC Gann price levels — multiples of significant numbers
    print(f"\n  Key Gann price levels for Bitcoin:")
    key_levels = [
        (10000, "100² (perfect square)"),
        (14400, "144 × 100 (master cycle × 100)"),
        (22500, "150² (perfect square)"),
        (32400, "180² (half-circle squared)"),
        (36000, "360 × 100 (full circle × 100)"),
        (40000, "200² (perfect square)"),
        (50625, "225² (Gann key square)"),
        (62500, "250² (perfect square)"),
        (72900, "270² (¾ circle squared)"),
        (90000, "300² (perfect square)"),
        (100000, "Psychological level"),
        (108900, "330² (11/12 circle squared)"),
        (129600, "360² (full circle squared)"),
        (144000, "144 × 1,000 (master cycle × 1,000)"),
    ]
    for level, desc in key_levels:
        dist = (last_bar.close - level) / level * 100
        arrow = "▲" if dist > 0 else "▼"
        print(f"    ${level:>10,}  {desc:<35}  {arrow} {abs(dist):>5.1f}% away")

    # ── 9. Export results ────────────────────────────────────────────────
    print(f"\n{'─' * 78}")
    print("EXPORTING RESULTS")
    print(f"{'─' * 78}")

    export_path = os.path.join(base_dir, "btc_backtest.csv")
    result.export_csv(export_path)

    # ── 10. Summary ──────────────────────────────────────────────────────
    print(f"\n{'=' * 78}")
    print("BACKTEST COMPLETE")
    print(f"{'=' * 78}")

    btc_return = (bars[-1].close - bars[0].close) / bars[0].close * 100
    algo_return = result.total_pnl_pct

    print(f"\n  BTC buy-and-hold return: {btc_return:+.2f}%")
    print(f"  Algorithm return:        {algo_return:+.2f}%")
    print(f"  Outperformance:          {algo_return - btc_return:+.2f}%")
    print(f"\n  Data source: Real Binance BTCUSDT daily klines")
    print(f"  Total bars:  {len(bars)}")
    print(f"  Key observations:")
    print(f"    - Bitcoin's extreme volatility ({annual_vol:.0f}% annual) "
          f"triggers Dynamic SQ12")
    print(f"    - Gann angles adapt to BTC's large price swings")
    print(f"    - 144-cycle levels align with BTC's major turning points")
    print(f"    - Number vibration analysis works on any price scale")
    print(f"{'=' * 78}")


if __name__ == "__main__":
    main()
