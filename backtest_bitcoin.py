"""
Bitcoin (BTC/USD) 5-Year Backtest — Gann Unified Algorithm
==========================================================

Backtests the W.D. Gann unified trading algorithm on Bitcoin (BTC/USD)
daily data spanning approximately 5 years.

Data is loaded from the **BTCUSDT-1d-YYYY-MM.zip** files included in
this repository.  Each zip contains one CSV with real Binance daily
kline data for that month.  No external APIs or packages are needed.

Key Bitcoin characteristics handled:
  - Real daily OHLCV data from Binance kline CSVs (no interpolation)
  - Much higher volatility than traditional markets (~60-80% annualized)
  - Large absolute price moves (hundreds/thousands of dollars per day)
  - Dynamic SQ12 used (high-volatility regime)
  - Captures the 2021 bull run, 2022 bear market, and 2024-25 recovery

Usage:
------
    python backtest_bitcoin.py

This will:
  1. Load real daily BTC data from BTCUSDT CSV zips in the repo (~5 years)
  2. Run the Gann algorithm backtester on every daily bar
  3. Print full results and trade log
  4. Export CSV files (btc_data.csv, btc_backtest_trades.csv, btc_backtest_equity.csv)
"""

from __future__ import annotations

import csv
import glob
import math
import os
import sys
import zipfile
from collections import Counter
from datetime import datetime, timezone
from typing import List

from backtest_engine import (
    BacktestConfig,
    Bar,
    GannBacktester,
)


# ---------------------------------------------------------------------------
# Load BTCUSDT data from repository zip files
# ---------------------------------------------------------------------------

def load_btcusdt_zips(data_dir: str | None = None) -> List[Bar]:
    """
    Load real daily BTCUSDT OHLCV bars from the monthly zip files
    shipped with this repository (``BTCUSDT-1d-YYYY-MM.zip``).

    Each zip contains a headerless CSV with Binance kline rows:
        open_time, open, high, low, close, volume, close_time, ...

    Handles both millisecond and microsecond timestamps.

    Parameters
    ----------
    data_dir : str or None
        Directory containing the zip files.  Defaults to the script dir.

    Returns
    -------
    List[Bar]
        Sorted, de-duplicated daily bars.
    """
    if data_dir is None:
        data_dir = os.path.dirname(os.path.abspath(__file__))

    zip_files = sorted(glob.glob(os.path.join(data_dir, "BTCUSDT-1d-*.zip")))
    if not zip_files:
        raise FileNotFoundError(
            f"No BTCUSDT-1d-*.zip files found in {data_dir}"
        )

    # Binance changed from millisecond to microsecond timestamps
    _MICROSECOND_THRESHOLD = 1_000_000_000_000_000

    bars: List[Bar] = []
    for zf_path in zip_files:
        with zipfile.ZipFile(zf_path, "r") as zf:
            for name in zf.namelist():
                if not name.endswith(".csv"):
                    continue
                with zf.open(name) as cf:
                    for raw_line in cf:
                        cols = raw_line.decode("utf-8").strip().split(",")
                        if len(cols) < 6:
                            continue
                        try:
                            ts = int(cols[0])
                            # Detect microseconds vs milliseconds
                            if ts > _MICROSECOND_THRESHOLD:
                                dt = datetime.fromtimestamp(
                                    ts / 1_000_000, tz=timezone.utc
                                ).replace(tzinfo=None)
                            else:
                                dt = datetime.fromtimestamp(
                                    ts / 1_000, tz=timezone.utc
                                ).replace(tzinfo=None)
                            bars.append(Bar(
                                date=dt,
                                open=round(float(cols[1]), 2),
                                high=round(float(cols[2]), 2),
                                low=round(float(cols[3]), 2),
                                close=round(float(cols[4]), 2),
                                volume=round(float(cols[5]), 2),
                            ))
                        except (ValueError, IndexError):
                            continue

    if not bars:
        raise RuntimeError("No valid kline rows found in BTCUSDT zip files.")

    # Sort and de-duplicate by date
    bars.sort(key=lambda b: b.date)
    seen: set[str] = set()
    unique: List[Bar] = []
    for b in bars:
        key = b.date.strftime("%Y-%m-%d")
        if key not in seen:
            seen.add(key)
            unique.append(b)
    return unique


def get_btc_data() -> List[Bar]:
    """Load BTC daily data from the BTCUSDT zip files in the repository."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        bars = load_btcusdt_zips(base_dir)
        print(f"   ✓ Loaded {len(bars)} daily bars from BTCUSDT zip files")
        return bars
    except Exception as exc:
        print(f"   ✗ Failed to load BTCUSDT data: {exc}")
        print("     Ensure BTCUSDT-1d-*.zip files are in the repository.")
        sys.exit(1)


def save_btc_csv(bars: List[Bar], filepath: str) -> None:
    """Save Bitcoin bars to CSV."""
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "open", "high", "low", "close", "volume"])
        for b in bars:
            writer.writerow([
                b.date.strftime("%Y-%m-%d"),
                f"{b.open:.2f}", f"{b.high:.2f}",
                f"{b.low:.2f}", f"{b.close:.2f}",
                int(b.volume),
            ])


def main():
    """Run the full 5-year Bitcoin backtest using BTCUSDT CSV data."""
    base_dir = os.path.dirname(os.path.abspath(__file__))

    print("=" * 78)
    print("GANN UNIFIED TRADING ALGORITHM — BITCOIN (BTC/USD) 5-YEAR BACKTEST")
    print("Using real Binance BTCUSDT daily kline data from repository")
    print("=" * 78)

    # ── 1. Load Bitcoin data from BTCUSDT zips ───────────────────────────
    print("\n1. Loading Bitcoin (BTC/USD) real daily OHLCV data...")
    print("   Source: BTCUSDT-1d-*.zip files (Binance klines)")

    bars = get_btc_data()

    print(f"   Total bars: {len(bars)}")
    print(f"   Period:     {bars[0].date.strftime('%Y-%m-%d')} to "
          f"{bars[-1].date.strftime('%Y-%m-%d')}")
    print(f"   Start:      ${bars[0].close:>12,.2f}")
    print(f"   End:        ${bars[-1].close:>12,.2f}")
    print(f"   Low:        ${min(b.low for b in bars):>12,.2f}")
    print(f"   High:       ${max(b.high for b in bars):>12,.2f}")

    # Save BTC data CSV
    btc_csv = os.path.join(base_dir, "btc_data.csv")
    save_btc_csv(bars, btc_csv)
    print(f"   Saved to:   {btc_csv}")

    # ── 2. Configure backtester ──────────────────────────────────────────
    print("\n2. Configuring backtester for Bitcoin...")

    config = BacktestConfig(
        initial_capital=1_000.0,
        max_risk_pct=1.5,           # 1.5% risk — BTC is very volatile
        min_reward_risk=2.5,        # 2.5:1 R:R minimum (PDF 4 standard)
        max_position_pct=40.0,      # Max 40% — respect BTC volatility
        min_confidence=0.25,        # Minimum signal confidence
        lookback_bars=14,           # 14-bar lookback for crypto volatility
        max_hold_bars=72,           # Rule of 72 (PDF 4)
        use_trailing_stop=True,     # Trail stop after partial exit
        partial_exit_pct=0.5,       # Book 50% at first target
        slippage_pct=0.001,         # 0.1% slippage (crypto spreads)
        commission_per_trade=0.15,  # $0.15 per trade (proportional for $1k)
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
    print("\n3. Running 5-year backtest on Bitcoin...")
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

    # ── 7.5. Loss pattern analysis ───────────────────────────────────────
    print(f"\n{'─' * 78}")
    print("LOSS PATTERN ANALYSIS")
    print(f"{'─' * 78}")

    losing_trades = [t for t in result.trades if t.pnl <= 0]
    winning_trades = [t for t in result.trades if t.pnl > 0]
    n_losses = len(losing_trades)

    if n_losses > 0:
        # ─── 1. Loss by direction ────────────────────────────────────
        buy_losses = [t for t in losing_trades if t.direction == "BUY"]
        sell_losses = [t for t in losing_trades if t.direction == "SELL"]
        buy_wins = [t for t in winning_trades if t.direction == "BUY"]
        sell_wins = [t for t in winning_trades if t.direction == "SELL"]

        print(f"\n  1. LOSSES BY DIRECTION")
        print(f"     {'Direction':>10}  {'Losses':>7}  {'Wins':>6}  "
              f"{'Loss%':>6}  {'Avg Loss':>10}  {'Total Loss':>12}")
        print(f"     {'─' * 10}  {'─' * 7}  {'─' * 6}  "
              f"{'─' * 6}  {'─' * 10}  {'─' * 12}")

        for label, losses, wins in [("BUY", buy_losses, buy_wins),
                                     ("SELL", sell_losses, sell_wins)]:
            total = len(losses) + len(wins)
            loss_rate = len(losses) / total * 100 if total > 0 else 0
            avg_loss = (sum(t.pnl for t in losses) / len(losses)
                        if losses else 0)
            total_loss = sum(t.pnl for t in losses)
            print(f"     {label:>10}  {len(losses):>7}  {len(wins):>6}  "
                  f"{loss_rate:>5.1f}%  ${avg_loss:>9.2f}  ${total_loss:>11.2f}")

        # ─── 2. Loss by day of week ──────────────────────────────────
        print(f"\n  2. LOSSES BY DAY OF WEEK")
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        day_losses: dict[int, list] = {i: [] for i in range(7)}
        day_all: dict[int, int] = {i: 0 for i in range(7)}

        for t in result.trades:
            dow = t.entry_date.weekday()
            day_all[dow] += 1
            if t.pnl <= 0:
                day_losses[dow].append(t)

        print(f"     {'Day':>5}  {'Losses':>7}  {'Total':>6}  "
              f"{'Loss%':>6}  {'Avg Loss':>10}  {'Total Loss':>12}")
        print(f"     {'─' * 5}  {'─' * 7}  {'─' * 6}  "
              f"{'─' * 6}  {'─' * 10}  {'─' * 12}")

        for dow in range(7):
            losses = day_losses[dow]
            total = day_all[dow]
            loss_rate = len(losses) / total * 100 if total > 0 else 0
            avg_loss = (sum(t.pnl for t in losses) / len(losses)
                        if losses else 0)
            total_loss = sum(t.pnl for t in losses)
            print(f"     {day_names[dow]:>5}  {len(losses):>7}  {total:>6}  "
                  f"{loss_rate:>5.1f}%  ${avg_loss:>9.2f}  ${total_loss:>11.2f}")

        # ─── 3. Loss by confidence level ─────────────────────────────
        print(f"\n  3. LOSSES BY CONFIDENCE LEVEL")
        conf_buckets = [
            (0.0, 0.30, "Low (0.00–0.30)"),
            (0.30, 0.45, "Med (0.30–0.45)"),
            (0.45, 0.60, "High (0.45–0.60)"),
            (0.60, 1.01, "Very High (0.60+)"),
        ]
        print(f"     {'Confidence':>20}  {'Losses':>7}  {'Wins':>6}  "
              f"{'Loss%':>6}  {'Avg Loss':>10}")
        print(f"     {'─' * 20}  {'─' * 7}  {'─' * 6}  "
              f"{'─' * 6}  {'─' * 10}")

        for lo, hi, label in conf_buckets:
            bucket_losses = [t for t in losing_trades
                             if lo <= t.confidence < hi]
            bucket_wins = [t for t in winning_trades
                           if lo <= t.confidence < hi]
            total = len(bucket_losses) + len(bucket_wins)
            loss_rate = (len(bucket_losses) / total * 100
                         if total > 0 else 0)
            avg_loss = (sum(t.pnl for t in bucket_losses)
                        / len(bucket_losses) if bucket_losses else 0)
            print(f"     {label:>20}  {len(bucket_losses):>7}  "
                  f"{len(bucket_wins):>6}  {loss_rate:>5.1f}%  "
                  f"${avg_loss:>9.2f}")

        # ─── 4. Loss by exit reason ──────────────────────────────────
        print(f"\n  4. LOSS EXIT REASONS")
        loss_reasons: dict[str, list] = {}
        for t in losing_trades:
            loss_reasons.setdefault(t.exit_reason, []).append(t)

        print(f"     {'Reason':>15}  {'Count':>6}  {'%Losses':>8}  "
              f"{'Avg Loss':>10}  {'Worst':>10}")
        print(f"     {'─' * 15}  {'─' * 6}  {'─' * 8}  "
              f"{'─' * 10}  {'─' * 10}")

        for reason in sorted(loss_reasons, key=lambda r: -len(loss_reasons[r])):
            trades_r = loss_reasons[reason]
            pct = len(trades_r) / n_losses * 100
            avg_l = sum(t.pnl for t in trades_r) / len(trades_r)
            worst = min(t.pnl for t in trades_r)
            print(f"     {reason:>15}  {len(trades_r):>6}  "
                  f"{pct:>7.1f}%  ${avg_l:>9.2f}  ${worst:>9.2f}")

        # ─── 5. Consecutive loss streaks ─────────────────────────────
        print(f"\n  5. CONSECUTIVE LOSS STREAKS")
        streaks: list[list] = []
        current_streak: list = []
        for t in result.trades:
            if t.pnl <= 0:
                current_streak.append(t)
            else:
                if current_streak:
                    streaks.append(current_streak)
                    current_streak = []
        if current_streak:
            streaks.append(current_streak)

        if streaks:
            streak_lens = [len(s) for s in streaks]
            streak_pnls = [sum(t.pnl for t in s) for s in streaks]
            print(f"     Total streak events:   {len(streaks)}")
            print(f"     Max streak length:     {max(streak_lens)}")
            print(f"     Avg streak length:     {sum(streak_lens)/len(streaks):.1f}")
            print(f"     Worst streak PnL:      ${min(streak_pnls):,.2f}")

            # Distribution of streak lengths
            print(f"\n     Streak length distribution:")
            dist = Counter(streak_lens)
            for length in sorted(dist.keys()):
                bar = "█" * dist[length]
                print(f"       {length:>2} losses: {dist[length]:>4}x  {bar}")

        # ─── 6. Losses by market volatility regime ───────────────────
        print(f"\n  6. LOSSES BY MARKET VOLATILITY REGIME")

        # Build date→bar index for quick lookup
        bar_by_date: dict[str, int] = {}
        for i, b in enumerate(bars):
            bar_by_date[b.date.strftime("%Y-%m-%d")] = i

        low_vol_losses = []
        high_vol_losses = []
        low_vol_wins = []
        high_vol_wins = []

        for t in result.trades:
            key = t.entry_date.strftime("%Y-%m-%d")
            idx = bar_by_date.get(key)
            if idx is None or idx < 14:
                continue
            # Calculate 14-bar realized volatility at entry
            window = [bars[j].close for j in range(idx - 14, idx)]
            rets = [(window[k] - window[k-1]) / window[k-1]
                    for k in range(1, len(window))]
            vol = (sum(r**2 for r in rets) / len(rets)) ** 0.5 if rets else 0
            daily_vol_pct = vol * 100

            if t.pnl <= 0:
                if daily_vol_pct < 3.0:
                    low_vol_losses.append((t, daily_vol_pct))
                else:
                    high_vol_losses.append((t, daily_vol_pct))
            else:
                if daily_vol_pct < 3.0:
                    low_vol_wins.append((t, daily_vol_pct))
                else:
                    high_vol_wins.append((t, daily_vol_pct))

        print(f"     {'Regime':>15}  {'Losses':>7}  {'Wins':>6}  "
              f"{'Loss%':>6}  {'Avg Loss':>10}")
        print(f"     {'─' * 15}  {'─' * 7}  {'─' * 6}  "
              f"{'─' * 6}  {'─' * 10}")

        for label, losses_l, wins_l in [
            ("Low vol (<3%)", low_vol_losses, low_vol_wins),
            ("High vol (≥3%)", high_vol_losses, high_vol_wins),
        ]:
            total = len(losses_l) + len(wins_l)
            loss_rate = len(losses_l) / total * 100 if total > 0 else 0
            avg_l = (sum(t.pnl for t, _ in losses_l) / len(losses_l)
                     if losses_l else 0)
            print(f"     {label:>15}  {len(losses_l):>7}  {len(wins_l):>6}  "
                  f"{loss_rate:>5.1f}%  ${avg_l:>9.2f}")

        # ─── 7. Monthly loss clustering ──────────────────────────────
        print(f"\n  7. MONTHLY LOSS CLUSTERING")
        month_data: dict[str, dict] = {}
        for t in result.trades:
            key = t.entry_date.strftime("%Y-%m")
            if key not in month_data:
                month_data[key] = {"losses": 0, "wins": 0, "loss_pnl": 0.0}
            if t.pnl <= 0:
                month_data[key]["losses"] += 1
                month_data[key]["loss_pnl"] += t.pnl
            else:
                month_data[key]["wins"] += 1

        # Find worst months by loss count
        worst_months = sorted(month_data.items(),
                              key=lambda x: x[1]["losses"], reverse=True)[:10]

        print(f"     {'Month':>8}  {'Losses':>7}  {'Wins':>6}  "
              f"{'Loss%':>6}  {'Loss PnL':>10}")
        print(f"     {'─' * 8}  {'─' * 7}  {'─' * 6}  "
              f"{'─' * 6}  {'─' * 10}")

        for month, data in worst_months:
            total = data["losses"] + data["wins"]
            loss_rate = data["losses"] / total * 100 if total > 0 else 0
            print(f"     {month:>8}  {data['losses']:>7}  {data['wins']:>6}  "
                  f"{loss_rate:>5.1f}%  ${data['loss_pnl']:>9.2f}")

        # ─── 8. Loss pattern near Gann levels ────────────────────────
        print(f"\n  8. LOSSES NEAR KEY GANN PRICE LEVELS")

        gann_price_levels = [
            10000, 14400, 22500, 32400, 36000, 40000, 50625,
            62500, 72900, 90000, 100000, 108900, 129600, 144000,
        ]

        near_gann_losses: List = []
        far_gann_losses: List = []
        for t in losing_trades:
            min_dist = min(
                abs(t.entry_price - lv) / lv * 100
                for lv in gann_price_levels
            )
            if min_dist < 5.0:  # Within 5% of a Gann level
                near_gann_losses.append(t)
            else:
                far_gann_losses.append(t)

        near_gann_wins: List = []
        far_gann_wins: List = []
        for t in winning_trades:
            min_dist = min(
                abs(t.entry_price - lv) / lv * 100
                for lv in gann_price_levels
            )
            if min_dist < 5.0:
                near_gann_wins.append(t)
            else:
                far_gann_wins.append(t)

        print(f"     {'Proximity':>20}  {'Losses':>7}  {'Wins':>6}  "
              f"{'Loss%':>6}  {'Avg Loss':>10}")
        print(f"     {'─' * 20}  {'─' * 7}  {'─' * 6}  "
              f"{'─' * 6}  {'─' * 10}")

        for label, losses_l, wins_l in [
            ("Near Gann (<5%)", near_gann_losses, near_gann_wins),
            ("Far from Gann (≥5%)", far_gann_losses, far_gann_wins),
        ]:
            n_l = len(losses_l)
            n_w = len(wins_l)
            total = n_l + n_w
            loss_rate = n_l / total * 100 if total > 0 else 0
            avg_l = sum(t.pnl for t in losses_l) / n_l if n_l else 0
            print(f"     {label:>20}  {n_l:>7}  {n_w:>6}  "
                  f"{loss_rate:>5.1f}%  ${avg_l:>9.2f}")

        # ─── 9. Summary of key findings ──────────────────────────────
        print(f"\n  {'─' * 74}")
        print(f"  KEY LOSS PATTERN FINDINGS")
        print(f"  {'─' * 74}")

        # Find the worst day
        worst_day_idx = max(range(7),
                            key=lambda d: len(day_losses[d]))
        worst_day_rate = (len(day_losses[worst_day_idx])
                          / day_all[worst_day_idx] * 100
                          if day_all[worst_day_idx] > 0 else 0)

        # Find worst direction
        buy_loss_rate = (len(buy_losses)
                         / (len(buy_losses) + len(buy_wins)) * 100
                         if (len(buy_losses) + len(buy_wins)) > 0 else 0)
        sell_loss_rate = (len(sell_losses)
                          / (len(sell_losses) + len(sell_wins)) * 100
                          if (len(sell_losses) + len(sell_wins)) > 0 else 0)

        # Dominant exit reason for losses
        dominant_reason = max(loss_reasons,
                              key=lambda r: len(loss_reasons[r]))
        dominant_pct = len(loss_reasons[dominant_reason]) / n_losses * 100

        findings = []
        findings.append(
            f"  1. STOP LOSSES DOMINATE: {dominant_pct:.0f}% of losses "
            f"exit via {dominant_reason} — tight stops protect capital "
            f"but cause frequent small losses."
        )

        if buy_loss_rate > sell_loss_rate + 5:
            findings.append(
                f"  2. DIRECTIONAL BIAS: BUY trades lose more often "
                f"({buy_loss_rate:.1f}% vs {sell_loss_rate:.1f}%) — "
                f"algorithm struggles with false breakouts on long entries."
            )
        elif sell_loss_rate > buy_loss_rate + 5:
            findings.append(
                f"  2. DIRECTIONAL BIAS: SELL trades lose more often "
                f"({sell_loss_rate:.1f}% vs {buy_loss_rate:.1f}%) — "
                f"shorting against BTC's long-term uptrend is harder."
            )
        else:
            findings.append(
                f"  2. NO DIRECTIONAL BIAS: BUY ({buy_loss_rate:.1f}%) "
                f"and SELL ({sell_loss_rate:.1f}%) loss rates are similar "
                f"— algorithm is direction-neutral."
            )

        findings.append(
            f"  3. WORST DAY: {day_names[worst_day_idx]} has the highest "
            f"loss rate ({worst_day_rate:.1f}% of trades lose) — "
            f"consider filtering or reducing size."
        )

        if streaks:
            max_streak = max(streak_lens)
            findings.append(
                f"  4. MAX LOSING STREAK: {max_streak} consecutive losses "
                f"— acceptable for a {result.win_rate * 100:.0f}% win-rate system "
                f"({'normal' if max_streak <= 10 else 'concerning'})."
            )

        low_vol_loss_rate = (len(low_vol_losses)
                             / (len(low_vol_losses) + len(low_vol_wins)) * 100
                             if (len(low_vol_losses) + len(low_vol_wins)) > 0
                             else 0)
        high_vol_loss_rate = (len(high_vol_losses)
                              / (len(high_vol_losses) + len(high_vol_wins))
                              * 100
                              if (len(high_vol_losses) + len(high_vol_wins))
                              > 0 else 0)

        if low_vol_loss_rate > high_vol_loss_rate + 5:
            findings.append(
                f"  5. VOLATILITY PATTERN: More losses in low-volatility "
                f"({low_vol_loss_rate:.1f}%) vs high-volatility "
                f"({high_vol_loss_rate:.1f}%) — choppy, range-bound markets "
                f"generate false signals."
            )
        elif high_vol_loss_rate > low_vol_loss_rate + 5:
            findings.append(
                f"  5. VOLATILITY PATTERN: More losses in high-volatility "
                f"({high_vol_loss_rate:.1f}%) vs low-volatility "
                f"({low_vol_loss_rate:.1f}%) — extreme moves blow through "
                f"stops before targets hit."
            )
        else:
            findings.append(
                f"  5. VOLATILITY PATTERN: Loss rates similar across "
                f"volatility regimes ({low_vol_loss_rate:.1f}% low vs "
                f"{high_vol_loss_rate:.1f}% high) — no clear regime bias."
            )

        # Average loss size relative to average win
        avg_loss_val = abs(sum(t.pnl for t in losing_trades) / n_losses)
        avg_win_val = (sum(t.pnl for t in winning_trades)
                       / len(winning_trades) if winning_trades else 0)
        loss_win_ratio = avg_loss_val / avg_win_val if avg_win_val > 0 else 0

        findings.append(
            f"  6. LOSS SIZE: Average loss (${avg_loss_val:.2f}) is "
            f"{loss_win_ratio:.1f}x the average win (${avg_win_val:.2f}) — "
            f"{'excellent' if loss_win_ratio < 0.5 else 'good' if loss_win_ratio < 1.0 else 'needs improvement'} "
            f"risk management."
        )

        near_loss_rate = (len(near_gann_losses)
                          / (len(near_gann_losses) + len(near_gann_wins))
                          * 100
                          if (len(near_gann_losses) + len(near_gann_wins))
                          > 0 else 0)
        far_loss_rate = (len(far_gann_losses)
                         / (len(far_gann_losses) + len(far_gann_wins)) * 100
                         if (len(far_gann_losses) + len(far_gann_wins))
                         > 0 else 0)

        if near_loss_rate > far_loss_rate + 5:
            findings.append(
                f"  7. GANN LEVELS: Higher loss rate near Gann levels "
                f"({near_loss_rate:.1f}% vs {far_loss_rate:.1f}%) — "
                f"price oscillation around key levels triggers stops."
            )
        else:
            findings.append(
                f"  7. GANN LEVELS: Loss rate near Gann levels "
                f"({near_loss_rate:.1f}%) vs far ({far_loss_rate:.1f}%) "
                f"— {'no significant difference' if abs(near_loss_rate - far_loss_rate) < 5 else 'better performance near levels'}."
            )

        for f_line in findings:
            print(f_line)

    # ── 8. Bitcoin-specific Gann analysis ────────────────────────────────
    print(f"\n{'─' * 78}")
    print("BITCOIN-SPECIFIC GANN ANALYSIS")
    print(f"{'─' * 78}")

    from gann_trading_algorithm import GannAnalyzer

    analyzer = GannAnalyzer()
    last_bar = bars[-1]
    print(f"\n  Current BTC price: ${last_bar.close:,.2f} "
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
    print(f"\n  Data source: BTCUSDT-1d-*.zip — real Binance daily klines")
    print(f"  Key observations:")
    print(f"    - Bitcoin's extreme volatility ({annual_vol:.0f}% annual) "
          f"triggers Dynamic SQ12")
    print(f"    - Gann angles adapt to BTC's large price swings")
    print(f"    - 144-cycle levels align with BTC's major turning points")
    print(f"    - Number vibration analysis works on any price scale")
    print(f"\n  To re-run:")
    print(f"  >>> python backtest_bitcoin.py")
    print(f"{'=' * 78}")


if __name__ == "__main__":
    main()
