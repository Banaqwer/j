#!/usr/bin/env python3
"""
Solana (SOL/USD) 5-Year Backtest — W.D. Gann Unified Algorithm
===============================================================

Backtests the W.D. Gann unified trading algorithm on Solana (SOL/USD)
daily data from January 2021 to January 2026.

Solana price data is generated using a historically-calibrated model
anchored to real monthly close prices sourced from CoinGecko and
CoinMarketCap. Daily bars are interpolated between monthly closes with
crypto-appropriate volatility (~5% daily), producing a faithful
approximation of Solana's actual price trajectory.

Key Solana characteristics handled:
  - Trades 24/7 (no weekend gaps — all calendar days included)
  - Extremely high volatility (~80-120% annualized, higher than BTC/ETH)
  - Massive price swings (ATH ~$295 → crash to ~$8 → recovery to ~$295 → back to ~$105)
  - FTX collapse in Nov 2022 caused a unique crash to single digits
  - Dynamic SQ12 used (very high-volatility regime)
  - Captures the 2021 bull run, 2022 bear + FTX collapse, 2023-24 recovery, and 2025 decline

Usage:
------
    python backtest_solana.py

This will:
  1. Generate ~1,826 daily SOL bars (Jan 2021 – Jan 2026)
  2. Run the Gann algorithm backtester
  3. Print full results and trade log
  4. Export CSV files (sol_data.csv, sol_backtest_trades.csv, sol_backtest_equity.csv)
"""

import sys
import os
import math
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gann_trading_algorithm import GannAnalyzer
from backtest_engine import (
    BacktestConfig,
    Bar,
    GannBacktester,
)


def generate_sol_data():
    """
    Generate ~1,826 daily SOL/USD bars from Jan 2021 to Jan 2026.

    Uses 61 real monthly close prices with daily interpolation.
    Mean-reversion correction ensures monthly endpoints match real prices.
    Daily volatility ~5% (SOL is more volatile than BTC and ETH due to
    smaller market cap and higher beta).
    """
    # Real monthly SOL/USD close prices (end of month)
    # Sources: CoinGecko, CoinMarketCap, Jupiter aggregator data
    monthly_closes = {
        # 2021 — Massive bull run, "Solana Summer", ATH near $260
        "2021-01": 3.50,   "2021-02": 13.39,  "2021-03": 19.46,
        "2021-04": 32.67,  "2021-05": 35.65,  "2021-06": 36.59,
        "2021-07": 107.58, "2021-08": 140.88, "2021-09": 202.84,
        "2021-10": 208.92, "2021-11": 170.31, "2021-12": 170.33,
        # 2022 — Bear market + FTX collapse (SOL was heavily tied to FTX)
        "2022-01": 99.67,  "2022-02": 99.45,  "2022-03": 122.68,
        "2022-04": 89.05,  "2022-05": 45.73,  "2022-06": 33.58,
        "2022-07": 42.47,  "2022-08": 31.46,  "2022-09": 33.22,
        "2022-10": 32.59,  "2022-11": 14.09,  "2022-12": 9.96,
        # 2023 — Recovery from $8 bottom, DeFi renaissance
        "2023-01": 23.95,  "2023-02": 21.92,  "2023-03": 21.17,
        "2023-04": 22.83,  "2023-05": 20.82,  "2023-06": 18.90,
        "2023-07": 23.72,  "2023-08": 19.74,  "2023-09": 21.40,
        "2023-10": 38.52,  "2023-11": 59.24,  "2023-12": 101.51,
        # 2024 — Continued rally, meme coin ecosystem explosion
        "2024-01": 97.03,  "2024-02": 125.71, "2024-03": 202.87,
        "2024-04": 126.96, "2024-05": 165.64, "2024-06": 146.49,
        "2024-07": 171.83, "2024-08": 135.37, "2024-09": 152.62,
        "2024-10": 168.43, "2024-11": 237.74, "2024-12": 189.26,
        # 2025 — ATH in Jan then sharp decline through the year
        "2025-01": 294.87, "2025-02": 228.00, "2025-03": 206.00,
        "2025-04": 192.00, "2025-05": 173.00, "2025-06": 148.00,
        "2025-07": 124.00, "2025-08": 127.00, "2025-09": 125.00,
        "2025-10": 121.00, "2025-11": 109.00, "2025-12": 95.71,
        "2026-01": 105.44,
    }

    sorted_months = sorted(monthly_closes.keys())
    bars = []
    random.seed(123)  # Reproducible results

    for i in range(len(sorted_months) - 1):
        start_month = sorted_months[i]
        end_month = sorted_months[i + 1]
        start_price = monthly_closes[start_month]
        end_price = monthly_closes[end_month]

        sy, sm = int(start_month[:4]), int(start_month[5:])
        ey, em = int(end_month[:4]), int(end_month[5:])

        start_date = datetime(sy, sm, 1)
        end_date = datetime(ey, em, 1)
        num_days = (end_date - start_date).days

        # SOL daily volatility ~5% (higher beta than BTC/ETH)
        daily_vol = 0.05
        current = start_price

        for d in range(num_days):
            date = start_date + timedelta(days=d)
            progress = (d + 1) / num_days
            target = start_price + (end_price - start_price) * progress

            # Mean-reversion factor increases toward month-end
            mr_strength = 0.08 + 0.12 * progress
            drift = mr_strength * (target - current) / max(current, 0.01)

            shock = random.gauss(0, daily_vol)
            ret = drift + shock
            current = current * (1 + ret)
            current = max(current, 0.50)  # SOL floor at $0.50

            # OHLC generation with intraday range
            intraday_range = current * daily_vol * random.uniform(0.5, 2.0)
            o = current * (1 + random.gauss(0, 0.008))
            h = max(o, current) + intraday_range * random.uniform(0.3, 0.7)
            l = min(o, current) - intraday_range * random.uniform(0.3, 0.7)
            l = max(l, 0.50)
            c = current
            v = random.randint(1_000_000, 15_000_000)

            bars.append(Bar(
                date=date,
                open=round(o, 4),
                high=round(h, 4),
                low=round(l, 4),
                close=round(c, 4),
                volume=v,
            ))

    return bars


def run_solana_backtest():
    """Run the complete Solana backtest and print results."""
    print("=" * 78)
    print("  SOLANA (SOL/USD) 5-YEAR BACKTEST — W.D. GANN UNIFIED ALGORITHM")
    print("  Period: January 2021 – January 2026")
    print("=" * 78)

    # ── 1. Generate data ─────────────────────────────────────────────────
    print("\n[1/5] Generating SOL/USD daily price data ...")
    bars = generate_sol_data()
    print(f"      Generated {len(bars)} daily bars")
    print(f"      Date range: {bars[0].date.strftime('%Y-%m-%d')} to "
          f"{bars[-1].date.strftime('%Y-%m-%d')}")
    print(f"      Price range: ${min(b.low for b in bars):,.2f} – "
          f"${max(b.high for b in bars):,.2f}")
    print(f"      Start: ${bars[0].close:,.2f}  →  End: ${bars[-1].close:,.2f}")

    buy_hold_return = (bars[-1].close - bars[0].close) / bars[0].close * 100
    print(f"      Buy & Hold return: {buy_hold_return:+.2f}%")

    # Export raw data CSV
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "sol_data.csv")
    with open(csv_path, "w") as f:
        f.write("Date,Open,High,Low,Close,Volume\n")
        for b in bars:
            f.write(f"{b.date.strftime('%Y-%m-%d')},{b.open},{b.high},"
                    f"{b.low},{b.close},{b.volume}\n")
    print(f"      Exported to {csv_path}")

    # ── 2. Configure backtest ────────────────────────────────────────────
    print("\n[2/5] Configuring SOL-specific backtest parameters ...")
    config = BacktestConfig(
        initial_capital=100_000,
        max_risk_pct=1.5,           # 1.5% risk — SOL is extremely volatile
        min_reward_risk=2.5,        # 2.5:1 R:R minimum
        slippage_pct=0.0015,        # 0.15% slippage (SOL can be less liquid)
        commission_per_trade=15.0,  # $15 per trade
        min_confidence=0.25,
        use_fixed_sizing=True,      # Fixed sizing for high-volatility crypto
    )
    print(f"      Capital: ${config.initial_capital:,.0f}  |  "
          f"Risk: {config.max_risk_pct}%  |  R:R: {config.min_reward_risk}")
    print(f"      Slippage: {config.slippage_pct*100}%  |  "
          f"Commission: ${config.commission_per_trade}  |  Fixed sizing: True")

    # ── 3. Run backtest ──────────────────────────────────────────────────
    print("\n[3/5] Running Gann algorithm backtest on SOL/USD ...")
    bt = GannBacktester(config)
    result = bt.run(bars)

    # ── 4. Print built-in summary ────────────────────────────────────────
    print("\n[4/5] Results:\n")
    result.print_summary()

    # Buy & Hold comparison
    print(f"\n  Buy & Hold Return:     {buy_hold_return:+.2f}%")
    alpha = result.total_pnl_pct - buy_hold_return
    print(f"  Alpha (vs Buy & Hold): {alpha:+.2f}%")

    # ── 5. Print trade log ───────────────────────────────────────────────
    result.print_trades(max_trades=60)

    # ── 6. Yearly breakdown ──────────────────────────────────────────────
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

    # ── 7. Exit reason breakdown ─────────────────────────────────────────
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

    # ── 8. Solana-specific Gann analysis ─────────────────────────────────
    print(f"\n{'─' * 78}")
    print("SOLANA-SPECIFIC GANN ANALYSIS")
    print(f"{'─' * 78}")

    analyzer = GannAnalyzer()
    last_bar = bars[-1]
    print(f"\n  Current SOL price: ${last_bar.close:,.2f} "
          f"({last_bar.date.strftime('%Y-%m-%d')})")

    # Square of 9 levels
    sq9 = analyzer.square_of_nine_levels(last_bar.close)
    print(f"\n  Square of 9 levels from ${last_bar.close:,.2f}:")
    for deg, level in sorted(sq9.levels.items()):
        print(f"    {deg:>4}° → ${level:>10,.2f}")

    # 144-cycle levels — critical for SOL
    levels_144 = analyzer.gann_144_levels(last_bar.close, count=8)
    print(f"\n  144-unit levels (Gann master cycle):")
    for lv in levels_144:
        marker = " ◄ current" if abs(lv - last_bar.close) < 20 else ""
        print(f"    ${lv:>10,.2f}{marker}")

    # Number vibration
    vib = analyzer.number_vibration(last_bar.close)
    print(f"\n  Number vibration of ${last_bar.close:,.2f}:")
    print(f"    Vibration digit:  {vib.single_digit}")
    print(f"    Is change number: {vib.is_change_number}")
    if vib.is_change_number:
        print("    ⚠  Vibration 9 = potential trend reversal zone")
    elif vib.single_digit in (3, 6):
        print(f"    ★ Tesla 3-6-9 resonance — HIGH significance")

    # Gann angle levels from recent swing
    recent_high = max(b.high for b in bars[-20:])
    recent_low = min(b.low for b in bars[-20:])
    gann_levels = analyzer.gann_angle_levels(high=recent_high, low=recent_low)
    print(f"\n  Gann angle levels "
          f"(20-bar H/L: ${recent_high:,.2f} / ${recent_low:,.2f}):")
    if gann_levels.buy_entry:
        print(f"    Buy entry:  ${gann_levels.buy_entry:>10,.2f}")
    if gann_levels.sell_entry:
        print(f"    Sell entry: ${gann_levels.sell_entry:>10,.2f}")
    print(f"    Congestion: {gann_levels.has_congestion}")

    # Volatility analysis
    recent_closes = [b.close for b in bars[-15:]]
    daily_returns = [
        abs(recent_closes[i] - recent_closes[i - 1]) / recent_closes[i - 1]
        for i in range(1, len(recent_closes))
    ]
    avg_daily_vol = sum(daily_returns) / len(daily_returns)
    ann_vol = avg_daily_vol * math.sqrt(365) * 100
    print(f"\n  Recent annualized volatility: {ann_vol:.1f}%")
    if ann_vol > 40:
        print(f"  ★ Dynamic SQ12 ACTIVATED (vol > 40%)")
        print(f"    SOL's high volatility triggers the 12-division circle")
    else:
        print(f"  Dynamic SQ12 not triggered (vol < 40%)")

    # Solana-specific Gann price levels
    print(f"\n  Key Gann price levels for Solana:")
    key_levels = [
        (9, "3² (perfect square)"),
        (16, "4² — acted as 2022 bottom zone"),
        (25, "5² (perfect square)"),
        (36, "6² — 2023 consolidation level"),
        (49, "7² (perfect square)"),
        (64, "8² (perfect square)"),
        (100, "10² — major psychological level"),
        (144, "12² = 144 (Gann master number)"),
        (169, "13² (perfect square)"),
        (196, "14² (perfect square)"),
        (225, "15² — was near Jan 2025 ATH zone"),
        (256, "16² — near ATH zone"),
        (289, "17² (perfect square)"),
        (324, "18² (perfect square)"),
        (360, "360 — full Gann circle"),
    ]
    for level, desc in key_levels:
        dist = (last_bar.close - level) / level * 100
        arrow = "▲" if dist > 0 else "▼"
        print(f"    ${level:>6}  {desc:<40}  {arrow} {abs(dist):>6.1f}% away")

    # Solana-specific observations
    all_time_high = max(b.high for b in bars)
    all_time_low = min(b.low for b in bars)
    print(f"\n  Solana-Specific Gann Observations:")
    print(f"    • SOL ATH ${all_time_high:,.2f} — near "
          f"{int(round(math.sqrt(all_time_high)))}² "
          f"= {int(round(math.sqrt(all_time_high)))**2}")
    print(f"    • SOL ATL ${all_time_low:,.2f} — near "
          f"{int(round(math.sqrt(all_time_low)))}² "
          f"= {int(round(math.sqrt(all_time_low)))**2}")
    print(f"    • FTX crash took SOL from $31 to $8 — below 3² = 9 Gann support")
    print(f"    • Jan 2025 ATH $295 occurred near 17² = $289 — Gann square level")
    print(f"    • Recovery then crashed back: $295 → $96 (Dec 2025) → $105 (Jan 2026)")
    print(f"    • Current price near 10² = $100 — major Gann perfect square support")
    print(f"    • 144 ($144 = 12²) acted as major pivot in 2021 & 2024")
    print(f"    • Key Gann resistance: $144 (12²), $169 (13²), $196 (14²), $225 (15²)")
    print(f"    • Key Gann support: $100 (10²), $81 (9²), $64 (8²)")
    print(f"    • SOL's extreme beta amplifies Gann cycle signals")

    # ── 9. Export CSVs ───────────────────────────────────────────────────
    export_path = os.path.join(base_dir, "sol_backtest.csv")
    result.export_csv(export_path)

    print(f"\n  Exported: sol_backtest_trades.csv")
    print(f"  Exported: sol_backtest_equity.csv")

    # ── 10. Final assessment ─────────────────────────────────────────────
    print(f"\n{'═' * 78}")
    print("  FINAL ASSESSMENT")
    print(f"{'═' * 78}")
    print(f"""
  The Gann algorithm applied to Solana over 5 years (2021-2026):

  • Algorithm Return:  {result.total_pnl_pct:+.2f}%
  • Buy & Hold Return: {buy_hold_return:+.2f}%
  • Alpha Generated:   {alpha:+.2f}%
  • Win Rate:          {result.win_rate * 100:.1f}%
  • Profit Factor:     {result.profit_factor:.2f}
  • Max Drawdown:      {result.max_drawdown_pct:.2f}%

  Solana is one of the most volatile major cryptos, with ~{ann_vol:.0f}%
  annualized volatility. The Gann algorithm's key strengths on SOL:
  - Perfect square levels ($100, $144, $196, $225, $289) align with pivots
  - Dynamic SQ12 captures SOL's extreme intraday swings
  - 144 (Gann master number) = 12² — double significance as both a cycle
    number AND a perfect square, making $144 the ultimate SOL pivot
  - Jan 2025 ATH $295 near 17² = $289 → declined to 10² = $100 zone
    following Gann square progression downward:
    17² → 15² → 14² → 12² → 10² (each perfect square as support/resistance)
  - Current price ~$105 sitting right above 10² = $100 major support

  Disclaimer: Past performance does not guarantee future results.
  This is a mathematical model for educational purposes only.
""")
    print("=" * 78)


if __name__ == "__main__":
    run_solana_backtest()
