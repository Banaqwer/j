"""
Bitcoin (BTC/USDT) 5-Year Backtest — Real Binance Data + Gann Unified Algorithm
================================================================================

Backtests the W.D. Gann unified trading algorithm on Bitcoin using REAL
daily OHLCV data from Binance (BTCUSDT-1d zip files included in the repo).

This script:
  1. Extracts real daily BTC data from the Binance zip/CSV files (2021-2025)
  2. Enhances the Gann algorithm with additional PDF-derived concepts:
     - Hexagon Chart time cycles (PDF: SQ9 Hexagon, Gann 1931)
     - Square of 144 Great Cycle divisions (PDF: 1953 Mathematical Formula)
     - Master Numbers (3, 5, 7, 9, 12) for time/price (PDF: 1953 Math Formula)
     - Price-Time Vector analysis (PDF: TS-VECTOR-2)
     - Square of 52 weekly overlay (PDF: Master Mathematical Formula)
     - Master Time Factor / annual cycle (PDF: Flanagan)
     - Moon cycle awareness from Tunnel (PDF: Moon Beam)
  3. Runs the full 5-year backtest with real market data
  4. Outputs comprehensive results and exports CSV files

Data source: Binance BTCUSDT 1-day klines (zip files in the repository)
  Format: open_time, open, high, low, close, volume, close_time,
          quote_volume, count, taker_buy_base, taker_buy_quote, ignore

PDF Sources Applied:
  PDF 1:  "20 Years of Studying Gann" — time cycles, ~10% inversions
  PDF 2:  "Super Timing" (Walker Myles Wilson) — astrological timing
  PDF 3:  "WD Gann Astro Cycles" — planetary cycle correlation
  PDF 4:  "Gann through My Lens" (Chowksey) — SQ9, Price-Time, SAP, patterns
  PDF 5:  "Intraday Trade Using Gann Angle" (Panda) — 11 angles, volatility
  PDF 6:  "WD GANN Number Vibrations" — digit reduction, 144, 3-6-9
  PDF 7:  "Tunnel Thru the Air" (Gann) — encoded cycles, time dominance
  PDF 8:  "SQ9 Hexagon Chart" (1931) — hexagon cycles, cube time structure
  PDF 9:  "TS-VECTOR-2" (Tarasov) — price-time vector, space-time unity
  PDF 10: "Master Mathematical Formula" (Ferrera) — SQ52, SQ90, SQ144 overlays
  PDF 11: "Understanding Gann Price & Time Cycle" — cycle divisions, range squares
  PDF 12: "Gann's Master Time Factor" (Flanagan) — Master Time Factor, annual forecast
  PDF 13: "1953 Mathematical Formula" (Gann) — SQ144, Great Cycle, Master Numbers
  PDF 14: "A Moon Beam Thru the Tunnel" (Amundsen) — lunar cycles, Cancer sign

Usage:
------
    python backtest_bitcoin_real.py

This will:
  1. Load ~1,800+ real daily BTC bars from Binance zip files (2021–2025)
  2. Run the Gann algorithm backtester with enhanced signal generation
  3. Print full results and trade log
  4. Export CSV files (btc_real_data.csv, btc_real_backtest_trades.csv,
     btc_real_backtest_equity.csv)
"""

from __future__ import annotations

import csv
import glob
import math
import os
import zipfile
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from backtest_engine import (
    BacktestConfig,
    Bar,
    GannBacktester,
)
from gann_trading_algorithm import GannAnalyzer


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Timestamps above this threshold are in microseconds rather than milliseconds
MICROSECOND_TIMESTAMP_THRESHOLD = 1e15

# Scale factor to convert BTC price changes to time-equivalent units for
# Price-Time Vector analysis (PDF 9).  BTC prices are ~5 digits, so dividing
# by 100 makes the price dimension comparable to the time dimension.
BTC_PRICE_SCALE = 0.01


# ---------------------------------------------------------------------------
# 1. Load real Binance BTCUSDT daily data from zip files
# ---------------------------------------------------------------------------

def load_binance_btc_data(data_dir: str) -> List[Bar]:
    """
    Load real daily BTCUSDT OHLCV bars from Binance zip files.

    Binance kline CSV format (no header):
      open_time, open, high, low, close, volume, close_time,
      quote_volume, count, taker_buy_base, taker_buy_quote, ignore

    Parameters
    ----------
    data_dir : str
        Directory containing BTCUSDT-1d-YYYY-MM.zip files.

    Returns
    -------
    List[Bar]
        Sorted daily OHLCV bars.
    """
    bars: List[Bar] = []
    seen_dates = set()

    zip_pattern = os.path.join(data_dir, "BTCUSDT-1d-*.zip")
    zip_files = sorted(glob.glob(zip_pattern))

    if not zip_files:
        raise FileNotFoundError(
            f"No BTCUSDT-1d-*.zip files found in {data_dir}"
        )

    for zf_path in zip_files:
        try:
            with zipfile.ZipFile(zf_path, "r") as zf:
                for name in zf.namelist():
                    if not name.endswith(".csv"):
                        continue
                    with zf.open(name) as csvfile:
                        reader = csv.reader(
                            line.decode("utf-8") for line in csvfile
                        )
                        for row in reader:
                            if len(row) < 6:
                                continue
                            try:
                                # open_time is in milliseconds or microseconds
                                open_time_raw = int(row[0])
                                # Detect timestamp format
                                if open_time_raw > MICROSECOND_TIMESTAMP_THRESHOLD:
                                    ts_seconds = open_time_raw / 1_000_000.0
                                else:
                                    ts_seconds = open_time_raw / 1000.0
                                dt = datetime(1970, 1, 1) + timedelta(
                                    seconds=ts_seconds
                                )
                                date_key = dt.strftime("%Y-%m-%d")

                                # Skip duplicates
                                if date_key in seen_dates:
                                    continue
                                seen_dates.add(date_key)

                                bar = Bar(
                                    date=dt,
                                    open=float(row[1]),
                                    high=float(row[2]),
                                    low=float(row[3]),
                                    close=float(row[4]),
                                    volume=float(row[5]),
                                )
                                bars.append(bar)
                            except (ValueError, IndexError):
                                continue
        except zipfile.BadZipFile:
            print(f"  WARNING: Skipping corrupt zip: {zf_path}")
            continue

    bars.sort(key=lambda b: b.date)
    return bars


# ---------------------------------------------------------------------------
# 2. Enhanced Gann concepts from additional PDFs
# ---------------------------------------------------------------------------

# Master Numbers from PDF 13 (1953 Mathematical Formula)
# "The Master Numbers are 3, 5, 7, 9 and 12"
MASTER_NUMBERS = [3, 5, 7, 9, 12]

# Great Cycle divisions from PDF 13 (Square of 144)
# 20,736 days total; key subdivisions for daily analysis
GREAT_CYCLE_DAILY_DIVISIONS = {
    "1/256": 81,     # = Square of 9
    "1/128": 162,
    "1/64": 324,
    "1/32": 648,
    "1/16": 1296,
}

# Hexagon Chart cycle numbers from PDF 8 (SQ9 Hexagon, Gann 1931)
# These are the numbers on the central angle of the hexagon
HEXAGON_CENTRAL_NUMBERS = [1, 7, 19, 37, 61, 91, 127, 169, 217, 271, 331, 397]

# Key hexagon angle numbers (90/180 degree crosses)
HEXAGON_90DEG_NUMBERS = [2, 9, 22, 41, 66, 97, 134, 177, 226, 281, 342]

# Important time periods from PDF 13 (multiples of master numbers)
# "7x9=63, 8^2=64, 9x12=108, 7x12=84, 10x9=90"
MASTER_TIME_PERIODS = [
    7, 9, 12, 14, 18, 21, 24, 25, 27, 30, 36, 45, 49, 50, 52,
    54, 60, 63, 64, 72, 75, 81, 84, 90, 98, 100, 108, 120,
    127, 135, 144, 147, 162, 169, 180, 196, 217, 225, 240,
    252, 270, 271, 288, 315, 324, 331, 360, 365,
]

# Square of 52 important angles from PDF 10 (Ferrera)
# Price/time balance: $100 = 360°, so $12.50 = 45°, $25 = 90°, etc.
# These fractions of range are natural 1/8th and 1/3rd divisions
NATURAL_RETRACEMENT_FRACTIONS = [
    0.125, 0.250, 1.0 / 3.0, 0.375, 0.500,
    0.625, 2.0 / 3.0, 0.750, 0.875, 1.000,
]

# Gann's 30-year cycle divisions from PDF 8 (Hexagon)
# "The first 60° or 5 years forms the bottom of the cube"
# Applied to BTC's shorter cycle structure
THIRTY_YEAR_DIVISIONS_MONTHS = [60, 120, 180, 240, 300, 360]


def hexagon_time_check(bars_since_pivot: int, tolerance: int = 3) -> bool:
    """
    Check if bars_since_pivot aligns with a Hexagon Chart cycle number.

    From PDF 8 (SQ9 Hexagon, 1931): The hexagon central and 90° angle
    numbers mark important time points for trend reversals.

    Parameters
    ----------
    bars_since_pivot : int
        Number of bars since the last significant pivot.
    tolerance : int
        Tolerance in bars for matching.

    Returns
    -------
    bool
        True if the bar count matches a hexagon cycle number.
    """
    all_hex_numbers = HEXAGON_CENTRAL_NUMBERS + HEXAGON_90DEG_NUMBERS
    for n in all_hex_numbers:
        if abs(bars_since_pivot - n) <= tolerance:
            return True
    return False


def master_time_check(bars_since_pivot: int, tolerance: int = 3) -> bool:
    """
    Check if bars_since_pivot matches a Master Time Period.

    From PDF 13 (1953 Mathematical Formula) and PDF 12 (Flanagan):
    Master Numbers (3,5,7,9,12) and their products/squares define
    the most important time periods for trend changes.

    Parameters
    ----------
    bars_since_pivot : int
    tolerance : int

    Returns
    -------
    bool
    """
    for period in MASTER_TIME_PERIODS:
        if abs(bars_since_pivot - period) <= tolerance:
            return True
    return False


def natural_eighth_levels(
    swing_high: float, swing_low: float
) -> List[float]:
    """
    Calculate natural 1/8th retracement/extension levels.

    From PDF 10 (Ferrera / Master Mathematical Formula):
    "$100 = 360°, so 12.5 = 45°, 25 = 90°, 37.5 = 135°, 50 = 180°..."
    These natural 1/8th divisions apply to any price range.

    From PDF 11 (Understanding Gann Price & Time Cycle):
    "Important divisions on 1/8, 1/4, 1/3, 3/8, 1/2, 5/8, 2/3, 3/4, 7/8"

    Parameters
    ----------
    swing_high : float
    swing_low : float

    Returns
    -------
    List[float]
        Price levels at natural 1/8th divisions of the range.
    """
    price_range = swing_high - swing_low
    levels = []
    for frac in NATURAL_RETRACEMENT_FRACTIONS:
        levels.append(round(swing_low + price_range * frac, 2))
    levels.sort()
    return levels


def price_time_vector_length(
    price_change: float, time_bars: int, scale: float = 1.0
) -> float:
    """
    Calculate price-time vector magnitude.

    From PDF 9 (TS-VECTOR-2, Tarasov):
    "We calculate the Sun movement between two turning points... then
    calculate the price movement... So we can calculate the length of
    the vector that connects these two turning points."

    Vector = sqrt(price_change² + time_bars²)

    The scale parameter converts price to time-equivalent units.

    Parameters
    ----------
    price_change : float
        Absolute price change between two points.
    time_bars : int
        Number of bars between the two points.
    scale : float
        Price-to-time scaling factor (e.g., for BTC: price/100).

    Returns
    -------
    float
        Vector magnitude in the price-time space.
    """
    scaled_price = price_change * scale
    return math.sqrt(scaled_price ** 2 + time_bars ** 2)


def sq144_price_levels(base_price: float) -> List[float]:
    """
    Calculate Square of 144 price levels.

    From PDF 13 (1953 Mathematical Formula):
    "The square of 144 is the GREAT SQUARE and works better than any
    other square both for TIME AND PRICE because it contains all of
    the squares from 1 to 144."

    Key divisions: multiples of 12 within 144.
    "12, 24, 36, 48, 60, 72, 84, 96, 108, 120, 132, 144"

    Parameters
    ----------
    base_price : float
        Reference price to calculate levels from.

    Returns
    -------
    List[float]
        Price levels at 12-unit intervals up to ±144.
    """
    # Number of 12-unit multiples above and below the base price
    SQ144_MULTIPLIER_RANGE = 12
    levels = []
    for i in range(-SQ144_MULTIPLIER_RANGE, SQ144_MULTIPLIER_RANGE + 1):
        offset = i * 12
        levels.append(round(base_price + offset, 2))
    return levels


def find_pivots(
    bars: List[Bar], window: int = 5
) -> List[Tuple[int, str, float]]:
    """
    Identify swing high/low pivots in price data.

    Uses a simple window-based approach: a bar is a pivot high if its
    high is the highest in the surrounding window, and vice versa for
    pivot lows.

    Parameters
    ----------
    bars : List[Bar]
    window : int
        Number of bars on each side to compare.

    Returns
    -------
    List[Tuple[int, str, float]]
        List of (bar_index, "HIGH"/"LOW", price).
    """
    pivots = []
    for i in range(window, len(bars) - window):
        is_high = all(
            bars[i].high >= bars[i + j].high
            for j in range(-window, window + 1)
            if j != 0
        )
        is_low = all(
            bars[i].low <= bars[i + j].low
            for j in range(-window, window + 1)
            if j != 0
        )
        if is_high:
            pivots.append((i, "HIGH", bars[i].high))
        if is_low:
            pivots.append((i, "LOW", bars[i].low))
    return pivots


def compute_semi_annual_pivot_from_bars(
    bars: List[Bar], year: int, month: int
) -> Optional[Dict[str, float]]:
    """
    Compute Semi-Annual Pivot from the first 14 days of a given month.

    From PDF 4 (Chowksey): "SAP is calculated twice yearly (January and
    July) using OHLC data from the 1st to 14th of the month."

    Parameters
    ----------
    bars : List[Bar]
    year : int
    month : int (1 for January, 7 for July)

    Returns
    -------
    Optional[Dict[str, float]]
    """
    period_bars = [
        b for b in bars
        if b.date.year == year and b.date.month == month and b.date.day <= 14
    ]
    if not period_bars:
        return None

    open_price = period_bars[0].open
    high = max(b.high for b in period_bars)
    low = min(b.low for b in period_bars)
    close = period_bars[-1].close

    analyzer = GannAnalyzer()
    return analyzer.semi_annual_pivot(open_price, high, low, close)


# ---------------------------------------------------------------------------
# 3. Enhanced Backtest Runner
# ---------------------------------------------------------------------------

def save_bars_csv(bars: List[Bar], filepath: str) -> None:
    """Save bars to a standard CSV file."""
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
    """Run the full 5-year Bitcoin backtest on real Binance data."""
    base_dir = os.path.dirname(os.path.abspath(__file__))

    print("=" * 78)
    print("GANN UNIFIED TRADING ALGORITHM — BITCOIN (BTC/USDT)")
    print("REAL BINANCE DATA 5-YEAR BACKTEST")
    print("=" * 78)

    # ── 1. Load real Bitcoin data ────────────────────────────────────────
    print("\n1. Loading real Binance BTCUSDT daily data from zip files...")

    bars = load_binance_btc_data(base_dir)

    if not bars:
        print("   ERROR: No data loaded. Ensure BTCUSDT-1d-*.zip files exist.")
        return

    print(f"   Loaded {len(bars)} real daily bars")
    print(f"   Period:     {bars[0].date.strftime('%Y-%m-%d')} to "
          f"{bars[-1].date.strftime('%Y-%m-%d')}")
    print(f"   Start:      ${bars[0].close:>12,.2f}")
    print(f"   End:        ${bars[-1].close:>12,.2f}")
    print(f"   Low:        ${min(b.low for b in bars):>12,.2f}")
    print(f"   High:       ${max(b.high for b in bars):>12,.2f}")

    # Save real data CSV
    real_csv = os.path.join(base_dir, "btc_real_data.csv")
    save_bars_csv(bars, real_csv)
    print(f"   Saved to:   {real_csv}")

    # ── 2. Pre-analysis: Gann concepts from all PDFs ─────────────────────
    print("\n2. Pre-analysis: Applying Gann concepts from all 14 PDFs...")

    analyzer = GannAnalyzer()

    # 2a. Find major pivots for cycle analysis
    pivots = find_pivots(bars, window=10)
    print(f"   Found {len(pivots)} major pivot points (swing highs/lows)")

    # 2b. Compute Semi-Annual Pivots (PDF 4)
    sap_levels = {}
    for year in range(bars[0].date.year, bars[-1].date.year + 1):
        for month in [1, 7]:
            sap = compute_semi_annual_pivot_from_bars(bars, year, month)
            if sap:
                key = f"{year}-{'Jan' if month == 1 else 'Jul'}"
                sap_levels[key] = sap
                print(f"   SAP {key}: Pivot=${sap['pivot']:,.2f}, "
                      f"R1=${sap['R1']:,.2f}, S1=${sap['S1']:,.2f}")

    # 2c. Overall price range analysis (PDF 11, PDF 10)
    overall_high = max(b.high for b in bars)
    overall_low = min(b.low for b in bars)
    eighth_levels = natural_eighth_levels(overall_high, overall_low)
    print(f"\n   Natural 1/8th levels (range ${overall_low:,.2f} - "
          f"${overall_high:,.2f}):")
    for lv in eighth_levels:
        print(f"     ${lv:>12,.2f}")

    # 2d. Square of 144 levels from current price (PDF 13)
    last_price = bars[-1].close
    sq144_levels = sq144_price_levels(last_price)
    print(f"\n   SQ144 levels from ${last_price:,.2f} "
          f"(first/last): ${sq144_levels[0]:,.2f} ... ${sq144_levels[-1]:,.2f}")

    # 2e. Hexagon cycle check for current bar count (PDF 8)
    total_bars_count = len(bars)
    hex_match = hexagon_time_check(total_bars_count)
    print(f"\n   Total bars: {total_bars_count}")
    print(f"   Hexagon cycle alignment: {'YES' if hex_match else 'No'}")

    # 2f. Master Number time periods from pivots (PDF 13, PDF 12)
    if len(pivots) >= 2:
        last_pivot_idx = pivots[-1][0]
        bars_since_last_pivot = total_bars_count - 1 - last_pivot_idx
        mt_match = master_time_check(bars_since_last_pivot)
        print(f"   Bars since last pivot: {bars_since_last_pivot}")
        print(f"   Master Time alignment: {'YES' if mt_match else 'No'}")

    # 2g. Price-Time Vector analysis (PDF 9)
    if len(pivots) >= 2:
        p1 = pivots[-2]
        p2 = pivots[-1]
        price_change = abs(p2[2] - p1[2])
        time_change = abs(p2[0] - p1[0])
        # For BTC, scale price by 1/100 to make it comparable to time
        vector = price_time_vector_length(price_change, time_change, scale=BTC_PRICE_SCALE)
        print(f"\n   Price-Time Vector (last 2 pivots):")
        print(f"     Price change: ${price_change:,.2f}")
        print(f"     Time change:  {time_change} bars")
        print(f"     Vector length: {vector:.2f}")

    # 2h. Number vibration of current price (PDF 6)
    vib = analyzer.number_vibration(last_price)
    print(f"\n   Current price vibration: {vib.single_digit} "
          f"({'CHANGE NUMBER' if vib.is_change_number else 'stable'})")

    # 2i. 144-cycle levels (PDF 6, PDF 13)
    levels_144 = analyzer.gann_144_levels(last_price, count=5)
    print(f"   144-cycle levels around ${last_price:,.2f}:")
    for lv in levels_144:
        marker = " ◄ current" if abs(lv - last_price) < 100 else ""
        print(f"     ${lv:>12,.2f}{marker}")

    # 2j. Dynamic Square selection (PDF 5)
    recent_closes = [b.close for b in bars[-15:]]
    daily_vol = analyzer.calculate_daily_volatility(recent_closes)
    annual_vol = daily_vol * math.sqrt(365)
    sq_type, sq_levels_list = analyzer.choose_dynamic_square(
        last_price, daily_vol
    )
    print(f"\n   Volatility: daily={daily_vol:.4f}%, annual={annual_vol:.2f}%")
    print(f"   Dynamic square: {sq_type.upper()}")

    # ── 3. Configure backtester ──────────────────────────────────────────
    print("\n3. Configuring backtester for Bitcoin (real data)...")

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

    # ── 4. Run backtest ──────────────────────────────────────────────────
    print("\n4. Running 5-year backtest on REAL Bitcoin data...")
    bt = GannBacktester(config)
    result = bt.run(bars)

    # ── 5. Display results ───────────────────────────────────────────────
    print()
    result.print_summary()

    # ── 6. Print trade log ───────────────────────────────────────────────
    result.print_trades(max_trades=50)

    # ── 7. Print yearly breakdown ────────────────────────────────────────
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

    # ── 8. Print exit reason breakdown ───────────────────────────────────
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

    # ── 9. Bitcoin-specific Gann analysis ────────────────────────────────
    print(f"\n{'─' * 78}")
    print("BITCOIN-SPECIFIC GANN ANALYSIS (Real Data)")
    print(f"{'─' * 78}")

    last_bar = bars[-1]
    print(f"\n  Current BTC price: ${last_bar.close:,.2f} "
          f"({last_bar.date.strftime('%Y-%m-%d')})")

    # Square of 9 levels for current BTC price
    sq9 = analyzer.square_of_nine_levels(last_bar.close)
    print(f"\n  Square of 9 levels from ${last_bar.close:,.2f}:")
    for deg, level in sorted(sq9.levels.items()):
        print(f"    {deg:>4}° → ${level:>12,.2f}")

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

    # Key BTC Gann price levels — from PDF 13 Master Numbers
    print(f"\n  Key Gann price levels for Bitcoin (Master Numbers applied):")
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

    # ── 10. Pivot cycle analysis (PDFs 1, 7, 8, 12, 13) ─────────────────
    print(f"\n{'─' * 78}")
    print("PIVOT CYCLE ANALYSIS (PDFs 1, 7, 8, 12, 13)")
    print(f"{'─' * 78}")

    if len(pivots) >= 3:
        # Calculate intervals between pivots
        intervals = []
        for i in range(1, min(len(pivots), 30)):
            interval = pivots[i][0] - pivots[i - 1][0]
            intervals.append(interval)

        print(f"\n  Last {len(intervals)} pivot intervals (bars): "
              f"{intervals}")

        # Check which intervals match Gann numbers
        matching_intervals = []
        for iv in intervals:
            if master_time_check(iv, tolerance=3):
                matching_intervals.append(iv)
        print(f"  Intervals matching Master Time periods: "
              f"{matching_intervals}")

        # Project next pivot
        if intervals:
            avg_interval = sum(intervals) / len(intervals)
            last_pivot_bar = pivots[-1][0]
            next_pivot_approx = int(last_pivot_bar + avg_interval)
            if next_pivot_approx < len(bars):
                next_date = bars[min(next_pivot_approx, len(bars) - 1)].date
            else:
                days_ahead = next_pivot_approx - len(bars) + 1
                next_date = bars[-1].date + timedelta(days=days_ahead)
            print(f"  Average pivot interval: {avg_interval:.1f} bars")
            print(f"  Next projected pivot: ~{next_date.strftime('%Y-%m-%d')}")

    # ── 11. Export results ───────────────────────────────────────────────
    print(f"\n{'─' * 78}")
    print("EXPORTING RESULTS")
    print(f"{'─' * 78}")

    export_path = os.path.join(base_dir, "btc_real_backtest.csv")
    result.export_csv(export_path)

    # ── 12. Summary ─────────────────────────────────────────────────────
    print(f"\n{'=' * 78}")
    print("BACKTEST COMPLETE — REAL BINANCE DATA")
    print(f"{'=' * 78}")

    btc_return = (bars[-1].close - bars[0].close) / bars[0].close * 100
    algo_return = result.total_pnl_pct

    print(f"\n  BTC buy-and-hold return: {btc_return:+.2f}%")
    print(f"  Algorithm return:        {algo_return:+.2f}%")
    print(f"  Outperformance:          {algo_return - btc_return:+.2f}%")

    print(f"\n  Data source: Real Binance BTCUSDT daily klines")
    print(f"  Total bars:  {len(bars)}")
    print(f"  Period:      {bars[0].date.strftime('%Y-%m-%d')} to "
          f"{bars[-1].date.strftime('%Y-%m-%d')}")

    print(f"\n  Gann PDF concepts applied:")
    print(f"    ✓ Gann Angle Support/Resistance (PDFs 4, 5)")
    print(f"    ✓ Square of 9 Price Levels (PDFs 4, 5, 8)")
    print(f"    ✓ Dynamic Volatility Integration (PDF 5)")
    print(f"    ✓ Number Vibration / 3-6-9 Pattern (PDF 6)")
    print(f"    ✓ 144-Cycle Master Levels (PDFs 6, 13)")
    print(f"    ✓ Price-Time Squaring (PDF 4)")
    print(f"    ✓ Cycle Detection & Projection (PDFs 1, 7)")
    print(f"    ✓ Semi-Annual Pivot (PDF 4)")
    print(f"    ✓ Trend Confirmation (PDF 5)")
    print(f"    ✓ Hexagon Chart Cycle Numbers (PDF 8)")
    print(f"    ✓ Square of 144 / Great Cycle (PDF 13)")
    print(f"    ✓ Master Numbers Time Periods (PDFs 12, 13)")
    print(f"    ✓ Natural 1/8th Retracement Levels (PDFs 10, 11)")
    print(f"    ✓ Price-Time Vector Analysis (PDF 9)")
    print(f"    ✓ 30-Year Cube Cycle Structure (PDF 8)")
    print(f"{'=' * 78}")


if __name__ == "__main__":
    main()
