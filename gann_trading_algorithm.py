"""
W.D. Gann Unified Trading Algorithm
====================================

This algorithm synthesizes the teachings from seven W.D. Gann PDF documents:

1. "20 Years of Studying Gann" - Cycles of repetition, Law of Vibration, numerology,
   the importance of time cycles with ~10% inversion rate, vibrational trading ranges.

2. "Super Timing - W.D. Gann's Astrological Method" (Walker Myles Wilson) -
   Astrological timing methods and planetary cycle correlations.

3. "WD Gann Astro Cycles" - Planetary cycle-based market timing.

4. "Gann through My Lens" (Raju Chowksey) - Natural squares, Square of 9 wheel,
   dynamic Gann square from highs/lows, price-time squaring (P = T^2),
   SAP (Semi-Annual Pivot), pattern recognition (2B/2T), ATM trade rules.

5. "Intraday Trade Using Gann Angle" (Soumya Ranjan Panda) - 11 Gann angle trend
   lines, support/resistance formulas, degree factors, volatility-based dynamic
   approach, dynamic Square of 9 and Square of 12, trend confirmation rules.

6. "WD GANN Number Vibrations" - Numerology digit reduction, 144-cycle significance,
   360-degree circle divisions, percentage vibration patterns (3-6-9 symmetry).

7. "Tunnel Thru the Air" (W.D. Gann) - The foundational novel encoding Gann's
   complete trading methodology in veiled language; cycles, inventions as metaphors,
   and the importance of time as the dominant factor.

Key Cross-Document Similarities / Merged Concepts:
---------------------------------------------------
- TIME is the dominant factor; price follows time (all documents).
- Square root relationships underpin price level calculations (PDFs 4, 5).
- The number 360 (full circle) and its divisions (90, 180, 45, etc.) are
  fundamental to both angle and price calculations (PDFs 4, 5, 6).
- The Square of 9 wheel arranges prices in a spiral; key levels occur at
  cardinal (0/90/180/270) and diagonal (45/135/225/315) cross points (PDFs 4, 5).
- Gann angles define support/resistance using degree factors derived from
  the ratio of price-to-time units (PDF 5 primary, PDF 4 confirms).
- Volatility integration makes static Gann methods dynamic for intraday
  use (PDF 5).
- Number vibrations (digit reduction to single digit) reveal hidden symmetry
  in price and percentage moves; the 3-6-9 pattern and 144 cycle (PDF 6).
- Price-Time Squaring: when P = T^2 or T = sqrt(P), trend changes are
  imminent (PDF 4).
- Cycle analysis: repeating time intervals from historical pivots predict
  future turning points; ~10% inversion rate expected (PDF 1, 7).
- Risk management: small stop-losses, max 10% account per trade, minimum
  1:2.5 reward-to-risk ratio (PDF 4).

Usage:
------
    from gann_trading_algorithm import GannAnalyzer

    analyzer = GannAnalyzer()

    # Gann Angle support/resistance from a high/low
    levels = analyzer.gann_angle_levels(high=3238.35, low=3214.10)

    # Square of 9 price levels
    sq9 = analyzer.square_of_nine_levels(price=7540)

    # Dynamic Gann levels using volatility
    dynamic = analyzer.dynamic_gann_levels(prices=[1880, 1875.35, 1883, ...])

    # Number vibration analysis
    vib = analyzer.number_vibration(2417)

    # Price-Time square check
    pts = analyzer.price_time_square(
        swing_high=8627, swing_low=7961,
        swing_high_date="2014-12-04", swing_low_date="2014-12-17"
    )

    # Full trading signal
    signal = analyzer.generate_signal(
        high=3238.35, low=3214.10, prices_history=[...],
        current_price=3225.0
    )
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple


# ---------------------------------------------------------------------------
# Constants derived from the PDFs
# ---------------------------------------------------------------------------

# Gann's 11 angle ratios (price units : time units) and their geometric angles
# Source: PDF 5 - "Intraday Trade Using Gann Angle"
GANN_ANGLES: List[Tuple[str, float, float]] = [
    # (label, angle_degrees, degree_factor)
    ("16X1", 86.25, 0.479166667),
    ("8X1",  82.50, 0.458333333),
    ("4X1",  75.00, 0.416666667),
    ("3X1",  71.25, 0.395833333),
    ("2X1",  63.75, 0.354166667),
    ("1X1",  45.00, 0.250000000),
    ("1X2",  26.25, 0.145833333),
    ("1X3",  18.75, 0.104166667),
    ("1X4",  15.00, 0.083333333),
    ("1X8",   7.50, 0.041666667),
    ("1X16",  3.75, 0.020833333),
]

# Key circle divisions (degrees) used across Gann methods
# Source: PDFs 4, 5, 6
CIRCLE_DIVISIONS = [45, 90, 120, 135, 180, 225, 240, 270, 315, 360]

# Important Gann numbers (from PDF 6 - Number Vibrations, PDF 4)
GANN_NUMBERS = [144, 72, 36, 18, 9]

# Square of 9 cardinal and ordinal degree offsets
SQ9_DEGREES = [0, 45, 90, 135, 180, 225, 270, 315, 360]


# ---------------------------------------------------------------------------
# Data classes for structured output
# ---------------------------------------------------------------------------

@dataclass
class AngleLevel:
    """A single Gann angle support or resistance level."""
    label: str
    angle_degrees: float
    degree_factor: float
    price: float
    kind: str  # "support" or "resistance"


@dataclass
class GannAngleResult:
    """Result of Gann angle support/resistance calculation."""
    high: float
    low: float
    midpoint: float
    source: str  # "high_low" or "midpoint"
    resistances: List[AngleLevel]
    supports: List[AngleLevel]
    buy_entry: Optional[float] = None
    sell_entry: Optional[float] = None
    has_congestion: bool = False


@dataclass
class SquareOfNineResult:
    """Square of 9 price levels from a seed price."""
    seed_price: float
    sqrt_seed: float
    levels: Dict[int, float]  # degree -> price


@dataclass
class DynamicGannResult:
    """Dynamic Gann levels incorporating volatility."""
    last_price: float
    daily_volatility_pct: float
    expected_high: float
    expected_low: float
    uptrend_levels: GannAngleResult
    downtrend_levels: GannAngleResult


@dataclass
class NumberVibrationResult:
    """Result of number vibration (digit reduction) analysis."""
    original: float
    single_digit: int
    is_change_number: bool  # True if vibration == 9
    percentage_vibrations: List[Tuple[float, int]]


@dataclass
class PriceTimeSquareResult:
    """Price-Time squaring analysis result."""
    swing_high: float
    swing_low: float
    price_range: float
    num_days: int
    time_windows: List[Tuple[str, datetime]]
    price_windows_4digit: Dict[int, float]
    price_windows_3digit: Dict[int, float]


@dataclass
class CyclePoint:
    """A detected cycle repetition point."""
    date: datetime
    cycle_length_days: int
    description: str


@dataclass
class TradingSignal:
    """A unified trading signal combining all Gann methods."""
    direction: str  # "BUY", "SELL", or "NEUTRAL"
    entry_price: float
    stop_loss: float
    targets: List[float]
    confidence: float  # 0.0 to 1.0
    reasons: List[str]
    vibration_digit: int
    gann_levels: GannAngleResult
    sq9_levels: SquareOfNineResult


# ---------------------------------------------------------------------------
# Core algorithm
# ---------------------------------------------------------------------------

class GannAnalyzer:
    """
    Unified W.D. Gann trading analysis engine.

    Merges techniques from all seven PDF documents into a single coherent
    algorithm for calculating support/resistance levels, generating trading
    signals, and performing cycle analysis.
    """

    # ------------------------------------------------------------------
    # 1. GANN ANGLE SUPPORT / RESISTANCE
    #    Source: PDF 5 (primary), PDF 4 (confirms)
    # ------------------------------------------------------------------

    def gann_angle_levels(
        self,
        high: float,
        low: float,
        min_diff_4digit: float = 5.0,
        min_diff_3digit: float = 3.5,
    ) -> GannAngleResult:
        """
        Calculate Gann angle support and resistance levels.

        The core formulas (from PDF 5):
            Resistance = (sqrt(low)  + degree_factor) ^ 2
            Support    = (sqrt(high) - degree_factor) ^ 2

        Trading rules applied:
        - Rule d: If sell entry (4X1 support) > buy entry (4X1 resistance),
          it is a congestion/entry error -> recalculate from midpoint.
        - Rule e/f: Minimum price difference required between buy and sell
          entries (5 units for 4-digit prices, 3.5 for 3-digit prices).

        Parameters
        ----------
        high : float
            The high price of the period.
        low : float
            The low price of the period.
        min_diff_4digit : float
            Minimum buy/sell spread for 4-digit prices (default 5.0).
        min_diff_3digit : float
            Minimum buy/sell spread for 3-digit prices (default 3.5).

        Returns
        -------
        GannAngleResult
        """
        # Determine digit category for minimum spread rule
        max_price = max(high, low)
        if max_price >= 1000:
            min_diff = min_diff_4digit
        else:
            min_diff = min_diff_3digit

        # First pass: calculate from raw high and low
        result = self._compute_angle_levels(high, low, "high_low")

        # Check for congestion (Rule d from PDF 5)
        # Buy entry = 1X4 (15°) resistance (from low); Sell entry = 1X4 (15°) support (from high)
        # If sell entry >= buy entry, it's an entry error -> recalculate from midpoint
        buy_1x4 = None
        sell_1x4 = None
        for r in result.resistances:
            if r.label == "1X4":
                buy_1x4 = r.price
        for s in result.supports:
            if s.label == "1X4":
                sell_1x4 = s.price

        if buy_1x4 is not None and sell_1x4 is not None:
            if sell_1x4 >= buy_1x4 or abs(buy_1x4 - sell_1x4) < min_diff:
                # Congestion detected -> recalculate from midpoint (Rule d, e, f)
                midpoint = (high + low) / 2.0
                result = self._compute_angle_levels(midpoint, midpoint, "midpoint")
                result.high = high
                result.low = low
                result.has_congestion = True

        # Determine entry prices
        # In non-congestion: buy at 1X4 resistance, sell at 4X1 support
        # In congestion (midpoint): buy at 1X4 resistance, sell at 4X1 support
        for r in result.resistances:
            if r.label == "1X4":
                result.buy_entry = r.price
        for s in result.supports:
            if s.label == "4X1":
                result.sell_entry = s.price

        return result

    def _compute_angle_levels(
        self, ref_high: float, ref_low: float, source: str
    ) -> GannAngleResult:
        """Compute raw angle levels from reference high and low."""
        sqrt_low = math.sqrt(ref_low)
        sqrt_high = math.sqrt(ref_high)
        midpoint = (ref_high + ref_low) / 2.0

        resistances: List[AngleLevel] = []
        supports: List[AngleLevel] = []

        for label, angle_deg, deg_factor in GANN_ANGLES:
            res_price = (sqrt_low + deg_factor) ** 2
            resistances.append(AngleLevel(
                label=label, angle_degrees=angle_deg,
                degree_factor=deg_factor, price=round(res_price, 4),
                kind="resistance",
            ))

            sup_price = (sqrt_high - deg_factor) ** 2
            supports.append(AngleLevel(
                label=label, angle_degrees=angle_deg,
                degree_factor=deg_factor, price=round(sup_price, 4),
                kind="support",
            ))

        return GannAngleResult(
            high=ref_high, low=ref_low, midpoint=midpoint,
            source=source, resistances=resistances, supports=supports,
        )

    # ------------------------------------------------------------------
    # 2. SQUARE OF 9 PRICE LEVELS
    #    Source: PDF 4 (primary), PDF 5 (dynamic extension)
    # ------------------------------------------------------------------

    def square_of_nine_levels(self, price: float) -> SquareOfNineResult:
        """
        Calculate Square of 9 price levels from a seed price.

        The method (from PDF 4):
            sqrt_price = sqrt(price)
            For each degree offset d in {0, 45, 90, ..., 360}:
                increment = d / 180  (since 180° = factor 1)
                level = (sqrt_price + increment) ^ 2

        This produces the spiral price levels on the Gann Square of 9 wheel
        where prices move from one odd square to the next in 360° increments.

        Parameters
        ----------
        price : float
            The seed/reference price (typically a significant high or low).

        Returns
        -------
        SquareOfNineResult
        """
        sqrt_p = math.sqrt(price)
        levels: Dict[int, float] = {}

        for deg in SQ9_DEGREES:
            increment = deg / 180.0
            level = (sqrt_p + increment) ** 2
            levels[deg] = round(level, 4)

        return SquareOfNineResult(
            seed_price=price, sqrt_seed=round(sqrt_p, 4), levels=levels,
        )

    def square_of_nine_roadmap(self, price: float) -> List[float]:
        """
        Generate a roadmap between consecutive odd squares.

        From PDF 4: Prices move from one odd square to the next.
        The range between them is divided into 8 equal parts (each = 45°).

        Parameters
        ----------
        price : float
            Current price.

        Returns
        -------
        List[float]
            Roadmap of 9 price points from the lower odd square to the
            upper odd square containing the given price.
        """
        sqrt_p = math.sqrt(price)
        # Find the nearest lower odd integer root
        lower_root = int(sqrt_p)
        if lower_root % 2 == 0:
            lower_root -= 1
        if lower_root < 1:
            lower_root = 1
        upper_root = lower_root + 2

        lower_sq = lower_root ** 2
        upper_sq = upper_root ** 2
        diff = upper_sq - lower_sq
        step = diff / 8.0

        return [round(lower_sq + i * step, 4) for i in range(9)]

    # ------------------------------------------------------------------
    # 3. DYNAMIC GANN (VOLATILITY-BASED)
    #    Source: PDF 5 (primary)
    # ------------------------------------------------------------------

    def calculate_daily_volatility(self, prices: List[float]) -> float:
        """
        Calculate daily volatility percentage from historical prices.

        Method (from PDF 5):
        1. Compute absolute returns using natural log: LN(P_t / P_{t-1})
        2. Compute variance = mean(return^2) - mean(return)^2
        3. Daily volatility % = sqrt(variance) * 100

        Parameters
        ----------
        prices : List[float]
            List of at least 2 closing/last-trade prices (most recent last).

        Returns
        -------
        float
            Daily volatility as a percentage.
        """
        if len(prices) < 2:
            return 0.0

        returns = []
        sq_returns = []
        for i in range(1, len(prices)):
            r = math.log(prices[i] / prices[i - 1])
            returns.append(r)
            sq_returns.append(r * r)

        n = len(returns)
        avg_return = sum(returns) / n
        avg_sq_return = sum(sq_returns) / n
        variance = avg_sq_return - avg_return ** 2
        daily_vol_pct = math.sqrt(max(variance, 0.0)) * 100.0
        return round(daily_vol_pct, 6)

    def dynamic_gann_levels(self, prices: List[float]) -> DynamicGannResult:
        """
        Calculate dynamic Gann angle levels using volatility.

        From PDF 5: Uses daily volatility to project expected high/low,
        then applies Gann angle formulas to the projected range.

        Parameters
        ----------
        prices : List[float]
            List of at least 2 recent closing prices (most recent last).

        Returns
        -------
        DynamicGannResult
        """
        daily_vol = self.calculate_daily_volatility(prices)
        last_price = prices[-1]
        price_range = last_price * daily_vol / 100.0

        expected_high = last_price + price_range
        expected_low = last_price - price_range

        # Uptrend levels (from expected_low to expected_high)
        uptrend = self.gann_angle_levels(high=expected_high, low=expected_low)
        # Downtrend levels (from last_price as high, expected_low as low)
        downtrend = self.gann_angle_levels(high=last_price, low=expected_low)

        return DynamicGannResult(
            last_price=last_price,
            daily_volatility_pct=daily_vol,
            expected_high=round(expected_high, 4),
            expected_low=round(expected_low, 4),
            uptrend_levels=uptrend,
            downtrend_levels=downtrend,
        )

    def dynamic_square_of_nine(
        self, last_price: float, daily_vol_pct: float
    ) -> List[float]:
        """
        Dynamic Square of 9 using volatility.

        From PDF 5: Step = expected_range / 81.
        Seed = last_price + step.  Each subsequent number adds step.

        Parameters
        ----------
        last_price : float
            Most recent closing price.
        daily_vol_pct : float
            Daily volatility percentage.

        Returns
        -------
        List[float]
            81 price levels forming the dynamic Square of 9.
        """
        price_range = last_price * daily_vol_pct / 100.0
        step = price_range / 81.0
        return [round(last_price + (i + 1) * step, 4) for i in range(81)]

    def dynamic_square_of_twelve(
        self, last_price: float, daily_vol_pct: float
    ) -> List[float]:
        """
        Dynamic Square of 12 using volatility.

        From PDF 5: Step = expected_range / 144.
        Use Square of 12 when annual volatility > 40%.

        Parameters
        ----------
        last_price : float
            Most recent closing price.
        daily_vol_pct : float
            Daily volatility percentage.

        Returns
        -------
        List[float]
            144 price levels forming the dynamic Square of 12.
        """
        price_range = last_price * daily_vol_pct / 100.0
        step = price_range / 144.0
        return [round(last_price + (i + 1) * step, 4) for i in range(144)]

    def choose_dynamic_square(
        self, last_price: float, daily_vol_pct: float
    ) -> Tuple[str, List[float]]:
        """
        Choose between Square of 9 or Square of 12 based on annual volatility.

        From PDF 5: annual_vol = daily_vol * sqrt(365).
        If annual_vol > 40% -> use Square of 12, else Square of 9.

        Returns
        -------
        Tuple[str, List[float]]
            ("sq9" or "sq12", list of price levels).
        """
        annual_vol = daily_vol_pct * math.sqrt(365)
        if annual_vol > 40.0:
            return ("sq12", self.dynamic_square_of_twelve(last_price, daily_vol_pct))
        else:
            return ("sq9", self.dynamic_square_of_nine(last_price, daily_vol_pct))

    # ------------------------------------------------------------------
    # 4. NUMBER VIBRATION ANALYSIS
    #    Source: PDF 6 (primary), PDF 1 (confirms)
    # ------------------------------------------------------------------

    @staticmethod
    def digit_reduction(number: float) -> int:
        """
        Reduce a number to its single-digit vibration.

        From PDF 6: Sum all digits repeatedly until a single digit remains.
        Example: 2417 -> 2+4+1+7 = 14 -> 1+4 = 5

        Parameters
        ----------
        number : float
            The number to reduce.

        Returns
        -------
        int
            Single digit vibration (1-9).
        """
        n = abs(int(number))
        while n >= 10:
            n = sum(int(d) for d in str(n))
        return n

    def number_vibration(self, price: float) -> NumberVibrationResult:
        """
        Perform full number vibration analysis on a price.

        From PDF 6: Analyzes the single-digit vibration and checks
        whether the number is a "change number" (vibration = 9).
        Also computes the vibrations of the standard Gann percentage
        table (3.125%, 6.25%, ..., 100%).

        Parameters
        ----------
        price : float
            The price to analyze.

        Returns
        -------
        NumberVibrationResult
        """
        single = self.digit_reduction(price)

        # Build percentage vibration table (from PDF 6)
        pct_vibrations: List[Tuple[float, int]] = []
        pct = 3.125
        while pct <= 100.0:
            level = price * pct / 100.0
            vib = self.digit_reduction(level)
            pct_vibrations.append((round(pct, 3), vib))
            pct += 3.125

        return NumberVibrationResult(
            original=price,
            single_digit=single,
            is_change_number=(single == 9),
            percentage_vibrations=pct_vibrations,
        )

    @staticmethod
    def gann_144_levels(base_price: float, count: int = 10) -> List[float]:
        """
        Calculate price levels at multiples of 144 from a base price.

        From PDF 6: 144 reduces to 9, signifying change. Key support/
        resistance levels occur at multiples of 144 (and subdivisions
        like 18, 36, 54, 72).

        Parameters
        ----------
        base_price : float
            Starting price.
        count : int
            Number of levels above and below.

        Returns
        -------
        List[float]
            Price levels at 144-unit intervals (below and above).
        """
        levels = []
        for i in range(-count, count + 1):
            levels.append(round(base_price + i * 144, 4))
        return levels

    @staticmethod
    def gann_144_subdivisions(base_price: float) -> Dict[int, float]:
        """
        Calculate subdivision levels within one 144-unit range.

        From PDF 6: Subdivisions at 18, 36, 54, 72, 90, 108, 126, 144
        all reduce to vibration 9.

        Returns
        -------
        Dict[int, float]
            subdivision_value -> price_level
        """
        subdivisions = [18, 36, 54, 72, 90, 108, 126, 144]
        return {s: round(base_price + s, 4) for s in subdivisions}

    # ------------------------------------------------------------------
    # 5. PRICE-TIME SQUARING
    #    Source: PDF 4 (primary), PDF 1 (confirms)
    # ------------------------------------------------------------------

    def price_time_square(
        self,
        swing_high: float,
        swing_low: float,
        swing_high_date: str,
        swing_low_date: str,
        date_fmt: str = "%Y-%m-%d",
    ) -> PriceTimeSquareResult:
        """
        Calculate Price-Time Square windows.

        From PDF 4 ("Da Vinci Code" decoding):
            Range = High - Low
            T = sqrt(Range)   (time window in days)
            Price windows at 360°, 720°, 1080° etc. using:
                4-digit: (sqrt(Low) ± degree_offset/180)^2
                3-digit: (sqrt(Low/10) ± degree_offset/180)^2 * 10

        As per Gann: "When Price & Time coordinates balance each other,
        a change in trend is imminent."  P = T^2, T = sqrt(P).

        Parameters
        ----------
        swing_high : float
        swing_low : float
        swing_high_date : str
        swing_low_date : str
        date_fmt : str

        Returns
        -------
        PriceTimeSquareResult
        """
        dt_high = datetime.strptime(swing_high_date, date_fmt)
        dt_low = datetime.strptime(swing_low_date, date_fmt)
        later_date = max(dt_high, dt_low)

        price_range = abs(swing_high - swing_low)
        num_days = abs((dt_high - dt_low).days)

        # Time windows from range
        sqrt_range = math.sqrt(price_range)
        time_windows: List[Tuple[str, datetime]] = []
        for i, label in enumerate(["Window 1", "Window 2", "Window 3"], 1):
            window_days = int(round(sqrt_range * i))
            window_date = later_date + timedelta(days=window_days)
            time_windows.append((label, window_date))

        # Price windows (4-digit method)
        sqrt_low = math.sqrt(swing_low)
        price_4d: Dict[int, float] = {}
        for deg in [180, 360, 720, 1080]:
            offset = deg / 180.0
            price_4d[deg] = round((sqrt_low + offset) ** 2, 2)

        # Price windows (3-digit method: treat as 3-digit number)
        sqrt_low_3d = math.sqrt(swing_low / 10.0)
        price_3d: Dict[int, float] = {}
        for deg in [180, 360, 720, 1080]:
            offset = deg / 180.0
            price_3d[deg] = round((sqrt_low_3d + offset) ** 2 * 10, 2)

        return PriceTimeSquareResult(
            swing_high=swing_high,
            swing_low=swing_low,
            price_range=price_range,
            num_days=num_days,
            time_windows=time_windows,
            price_windows_4digit=price_4d,
            price_windows_3digit=price_3d,
        )

    # ------------------------------------------------------------------
    # 6. CYCLE ANALYSIS
    #    Source: PDF 1 (primary), PDF 7 (Tunnel Thru the Air)
    # ------------------------------------------------------------------

    @staticmethod
    def detect_cycles(
        pivot_dates: List[str],
        date_fmt: str = "%Y-%m-%d",
        tolerance_days: int = 3,
    ) -> List[CyclePoint]:
        """
        Detect repeating time cycles from a list of historical pivot dates.

        From PDF 1: "ALL of Gann's Cycles work off of repeats of the past."
        The cycle should produce H-L-H-L sequence with ~10% inversions.

        This function finds repeating intervals between pivots and projects
        the next expected pivot date.

        Parameters
        ----------
        pivot_dates : List[str]
            Dates of known market pivots (highs and lows).
        date_fmt : str
            Date format string.
        tolerance_days : int
            Tolerance for considering two intervals as the same cycle.

        Returns
        -------
        List[CyclePoint]
            Detected cycle repetition points projected into the future.
        """
        dates = sorted(datetime.strptime(d, date_fmt) for d in pivot_dates)
        if len(dates) < 3:
            return []

        # Calculate all intervals between consecutive pivots
        intervals = []
        for i in range(1, len(dates)):
            intervals.append((dates[i] - dates[i - 1]).days)

        # Find repeating intervals (within tolerance)
        cycle_counts: Dict[int, int] = {}
        for iv in intervals:
            matched = False
            for key in list(cycle_counts.keys()):
                if abs(iv - key) <= tolerance_days:
                    cycle_counts[key] += 1
                    matched = True
                    break
            if not matched:
                cycle_counts[iv] = 1

        # Project forward from the last known pivot for significant cycles
        projections: List[CyclePoint] = []
        last_date = dates[-1]
        for cycle_len, count in sorted(cycle_counts.items(), key=lambda x: -x[1]):
            if count >= 2:  # At least 2 repetitions to be meaningful
                next_date = last_date + timedelta(days=cycle_len)
                projections.append(CyclePoint(
                    date=next_date,
                    cycle_length_days=cycle_len,
                    description=(
                        f"{cycle_len}-day cycle (observed {count} times). "
                        f"Expected ~10% inversion rate."
                    ),
                ))

        return projections

    # ------------------------------------------------------------------
    # 7. SEMI-ANNUAL PIVOT (SAP)
    #    Source: PDF 4
    # ------------------------------------------------------------------

    @staticmethod
    def semi_annual_pivot(
        open_price: float,
        high: float,
        low: float,
        close: float,
    ) -> Dict[str, float]:
        """
        Calculate Semi-Annual Pivot levels.

        From PDF 4: SAP is calculated twice yearly (January and July)
        using OHLC data from the 1st to 14th of the month.

        The pivot and its support/resistance levels guide directional
        bias for the next 6 months.

        Parameters
        ----------
        open_price, high, low, close : float
            OHLC from the first 14 days of January or July.

        Returns
        -------
        Dict[str, float]
            Pivot, support (S1, S2), and resistance (R1, R2) levels.
        """
        pivot = (high + low + close) / 3.0
        s1 = 2 * pivot - high
        r1 = 2 * pivot - low
        s2 = pivot - (high - low)
        r2 = pivot + (high - low)

        return {
            "pivot": round(pivot, 4),
            "S1": round(s1, 4),
            "S2": round(s2, 4),
            "R1": round(r1, 4),
            "R2": round(r2, 4),
            "open": open_price,
            "range": round(high - low, 4),
        }

    # ------------------------------------------------------------------
    # 8. TREND CONFIRMATION (from Gann Angle theory)
    #    Source: PDF 5
    # ------------------------------------------------------------------

    @staticmethod
    def trend_status(
        current_price: float,
        levels: GannAngleResult,
    ) -> Dict[str, object]:
        """
        Determine trend status based on Gann angle price crossovers.

        From PDF 5:
        - 1X4 / 4X1 crossover = preliminary trend confirmation
        - 1X1 crossover = strong breakout
        - 16X1 / 1X16 = trend termination zone

        Parameters
        ----------
        current_price : float
            The current market price.
        levels : GannAngleResult
            Pre-computed Gann angle levels.

        Returns
        -------
        Dict with trend assessment.
        """
        res_map = {r.label: r.price for r in levels.resistances}
        sup_map = {s.label: s.price for s in levels.supports}

        status = {
            "price": current_price,
            "trend": "NEUTRAL",
            "strength": "NONE",
            "nearest_resistance": None,
            "nearest_support": None,
        }

        # Check uptrend breakouts
        if current_price > res_map.get("1X1", float("inf")):
            status["trend"] = "UP"
            status["strength"] = "STRONG"
        elif current_price > res_map.get("1X4", float("inf")):
            status["trend"] = "UP"
            status["strength"] = "PRELIMINARY"

        # Check downtrend breakdowns
        if current_price < sup_map.get("1X1", 0):
            status["trend"] = "DOWN"
            status["strength"] = "STRONG"
        elif current_price < sup_map.get("4X1", 0):
            status["trend"] = "DOWN"
            status["strength"] = "PRELIMINARY"

        # Find nearest levels
        res_prices = sorted(r.price for r in levels.resistances)
        sup_prices = sorted((s.price for s in levels.supports), reverse=True)

        for rp in res_prices:
            if rp > current_price:
                status["nearest_resistance"] = rp
                break

        for sp in sup_prices:
            if sp < current_price:
                status["nearest_support"] = sp
                break

        return status

    # ------------------------------------------------------------------
    # 9. UNIFIED SIGNAL GENERATION
    #    Merges all methods from all PDFs
    # ------------------------------------------------------------------

    def generate_signal(
        self,
        high: float,
        low: float,
        current_price: float,
        prices_history: Optional[List[float]] = None,
        account_size: Optional[float] = None,
        max_risk_pct: float = 10.0,
    ) -> TradingSignal:
        """
        Generate a unified trading signal by combining all Gann methods.

        Combines:
        - Gann angle support/resistance (PDF 5)
        - Square of 9 levels (PDF 4)
        - Number vibration (PDF 6)
        - Volatility-based dynamic levels (PDF 5)
        - Trend confirmation (PDF 5)
        - Risk management rules (PDF 4: small SL, min 1:2.5 RR, max 10% account)

        Parameters
        ----------
        high : float
            Period high price.
        low : float
            Period low price.
        current_price : float
            Current market price.
        prices_history : Optional[List[float]]
            Recent closing prices for volatility calculation.
        account_size : Optional[float]
            Trading account size for position sizing.
        max_risk_pct : float
            Maximum percentage of account per trade (default 10%, from PDF 4).

        Returns
        -------
        TradingSignal
        """
        reasons: List[str] = []
        confidence = 0.0

        # 1. Gann Angle levels
        gann_levels = self.gann_angle_levels(high=high, low=low)
        trend = self.trend_status(current_price, gann_levels)

        # 2. Square of 9 levels
        sq9 = self.square_of_nine_levels(current_price)

        # 3. Number vibration
        vibration = self.number_vibration(current_price)

        # 4. Dynamic volatility levels (if history available)
        dynamic = None
        if prices_history and len(prices_history) >= 2:
            dynamic = self.dynamic_gann_levels(prices_history)

        # --- Decision logic ---

        direction = "NEUTRAL"
        entry_price = current_price
        stop_loss = current_price
        targets: List[float] = []

        # Check Gann angle trend
        if trend["trend"] == "UP":
            direction = "BUY"
            confidence += 0.3
            reasons.append(f"Gann angle {trend['strength']} uptrend confirmed")
            if gann_levels.buy_entry is not None:
                entry_price = gann_levels.buy_entry
            # Stop loss at 1X1 support
            for s in gann_levels.supports:
                if s.label == "1X1":
                    stop_loss = s.price
                    break
            # Targets at higher resistance levels
            for r in sorted(gann_levels.resistances, key=lambda x: x.price):
                if r.price > entry_price:
                    targets.append(r.price)

        elif trend["trend"] == "DOWN":
            direction = "SELL"
            confidence += 0.3
            reasons.append(f"Gann angle {trend['strength']} downtrend confirmed")
            if gann_levels.sell_entry is not None:
                entry_price = gann_levels.sell_entry
            # Stop loss at 1X1 resistance
            for r in gann_levels.resistances:
                if r.label == "1X1":
                    stop_loss = r.price
                    break
            # Targets at lower support levels
            for s in sorted(gann_levels.supports, key=lambda x: x.price, reverse=True):
                if s.price < entry_price:
                    targets.append(s.price)

        # Check Square of 9 confluence
        for deg, level in sq9.levels.items():
            if abs(level - current_price) / current_price < 0.005:  # within 0.5%
                confidence += 0.1
                reasons.append(f"Price near Square of 9 {deg}° level ({level:.2f})")
                break

        # Check vibration (change number = potential reversal)
        if vibration.is_change_number:
            confidence += 0.1
            reasons.append("Price vibration is 9 (change number - potential reversal)")

        # Dynamic volatility confirmation
        if dynamic:
            if direction == "BUY" and current_price < dynamic.expected_high:
                confidence += 0.15
                reasons.append(
                    f"Dynamic analysis: room to upside target {dynamic.expected_high:.2f}"
                )
            elif direction == "SELL" and current_price > dynamic.expected_low:
                confidence += 0.15
                reasons.append(
                    f"Dynamic analysis: room to downside target {dynamic.expected_low:.2f}"
                )

        # Risk-reward check (from PDF 4: minimum 1:2.5)
        if direction != "NEUTRAL" and targets:
            risk = abs(entry_price - stop_loss)
            reward = abs(targets[0] - entry_price) if targets else 0
            if risk > 0:
                rr_ratio = reward / risk
                if rr_ratio >= 2.5:
                    confidence += 0.15
                    reasons.append(f"Risk-reward ratio {rr_ratio:.1f}:1 meets minimum 2.5:1")
                else:
                    confidence -= 0.1
                    reasons.append(
                        f"Risk-reward ratio {rr_ratio:.1f}:1 below minimum 2.5:1 - caution"
                    )

        # Position sizing (from PDF 4: max 10% of account, PDF 1: vibrational range)
        if account_size and direction != "NEUTRAL":
            max_position = account_size * max_risk_pct / 100.0
            reasons.append(
                f"Max position size: {max_position:.2f} "
                f"({max_risk_pct}% of {account_size:.2f})"
            )

        # Cap confidence at 1.0
        confidence = max(0.0, min(1.0, confidence))

        if direction == "NEUTRAL":
            reasons.append("No clear directional signal - stay flat")

        return TradingSignal(
            direction=direction,
            entry_price=round(entry_price, 4),
            stop_loss=round(stop_loss, 4),
            targets=[round(t, 4) for t in targets[:3]],  # Top 3 targets
            confidence=round(confidence, 4),
            reasons=reasons,
            vibration_digit=vibration.single_digit,
            gann_levels=gann_levels,
            sq9_levels=sq9,
        )


# ---------------------------------------------------------------------------
# Demonstration / self-test
# ---------------------------------------------------------------------------

def main():
    """Demonstrate the unified Gann trading algorithm with examples from the PDFs."""
    analyzer = GannAnalyzer()

    print("=" * 78)
    print("W.D. GANN UNIFIED TRADING ALGORITHM")
    print("Synthesized from 7 PDF documents on Gann's methods")
    print("=" * 78)

    # --- Example 1: Gann Angle Levels (from PDF 5, SBI example) ---
    print("\n" + "-" * 78)
    print("1. GANN ANGLE SUPPORT / RESISTANCE")
    print("   Source: PDF 5 - SBI example (High=3238.35, Low=3214.10)")
    print("-" * 78)

    levels = analyzer.gann_angle_levels(high=3238.35, low=3214.10)
    print(f"   Source: {levels.source} | Congestion: {levels.has_congestion}")
    print(f"   Buy entry:  {levels.buy_entry}")
    print(f"   Sell entry:  {levels.sell_entry}")
    print(f"\n   {'Angle':<8} {'Resistance':>12}  {'Support':>12}")
    print(f"   {'-----':<8} {'----------':>12}  {'-------':>12}")
    for r, s in zip(levels.resistances, levels.supports):
        print(f"   {r.label:<8} {r.price:>12.4f}  {s.price:>12.4f}")

    # --- Example 2: Square of 9 (from PDF 4, seed=7540) ---
    print("\n" + "-" * 78)
    print("2. SQUARE OF 9 PRICE LEVELS")
    print("   Source: PDF 4 - Seed price 7540")
    print("-" * 78)

    sq9 = analyzer.square_of_nine_levels(7540)
    print(f"   Seed: {sq9.seed_price}  |  sqrt: {sq9.sqrt_seed}")
    for deg, price in sorted(sq9.levels.items()):
        print(f"   {deg:>4}° ->  {price:>10.4f}")

    # --- Example 3: Square of 9 Roadmap (from PDF 4) ---
    print("\n" + "-" * 78)
    print("3. SQUARE OF 9 ROADMAP")
    print("   Source: PDF 4 - Price around 7540")
    print("-" * 78)

    roadmap = analyzer.square_of_nine_roadmap(7540)
    print(f"   Roadmap: {' -> '.join(f'{p:.0f}' for p in roadmap)}")

    # --- Example 4: Dynamic Gann Levels (from PDF 5, SBI volatility) ---
    print("\n" + "-" * 78)
    print("4. DYNAMIC GANN LEVELS (Volatility-Based)")
    print("   Source: PDF 5 - SBI 10-day prices")
    print("-" * 78)

    sbi_prices = [1880, 1875.35, 1883, 1885.5, 1885, 1909.25,
                  1933.9, 1949, 1911, 1842.25]
    dynamic = analyzer.dynamic_gann_levels(sbi_prices)
    print(f"   Last price:         {dynamic.last_price}")
    print(f"   Daily volatility:   {dynamic.daily_volatility_pct:.4f}%")
    print(f"   Expected high:      {dynamic.expected_high}")
    print(f"   Expected low:       {dynamic.expected_low}")

    # --- Example 5: Number Vibration (from PDF 6) ---
    print("\n" + "-" * 78)
    print("5. NUMBER VIBRATION ANALYSIS")
    print("   Source: PDF 6 - Price 2417")
    print("-" * 78)

    vib = analyzer.number_vibration(2417)
    print(f"   Number: {vib.original}  ->  Vibration: {vib.single_digit}")
    print(f"   Is change number (=9): {vib.is_change_number}")
    print(f"\n   Percentage vibration table (first 10):")
    for pct, v in vib.percentage_vibrations[:10]:
        print(f"     {pct:>7.3f}% -> vibration {v}")

    # --- Example 6: 144 Levels (from PDF 6) ---
    print("\n" + "-" * 78)
    print("6. GANN 144-CYCLE LEVELS")
    print("   Source: PDF 6 - Base price 2999")
    print("-" * 78)

    levels_144 = GannAnalyzer.gann_144_levels(2999, count=3)
    print(f"   Levels: {', '.join(str(l) for l in levels_144)}")

    subs = GannAnalyzer.gann_144_subdivisions(2999)
    print(f"   Subdivisions: {subs}")

    # --- Example 7: Price-Time Square (from PDF 4, Da Vinci Code) ---
    print("\n" + "-" * 78)
    print("7. PRICE-TIME SQUARING")
    print("   Source: PDF 4 - Swing High 8627 (2014-12-04), Low 7961 (2014-12-17)")
    print("-" * 78)

    pts = analyzer.price_time_square(
        swing_high=8627, swing_low=7961,
        swing_high_date="2014-12-04", swing_low_date="2014-12-17",
    )
    print(f"   Range: {pts.price_range}  |  Days: {pts.num_days}")
    print(f"   Time windows:")
    for label, dt in pts.time_windows:
        print(f"     {label}: {dt.strftime('%Y-%m-%d')}")
    print(f"   Price windows (4-digit): {pts.price_windows_4digit}")
    print(f"   Price windows (3-digit): {pts.price_windows_3digit}")

    # --- Example 8: Cycle Detection (from PDF 1) ---
    print("\n" + "-" * 78)
    print("8. CYCLE ANALYSIS")
    print("   Source: PDF 1 - Detecting repeating pivot cycles")
    print("-" * 78)

    # Sample pivot dates with a ~30-day cycle embedded
    pivots = [
        "2024-01-05", "2024-02-03", "2024-03-05", "2024-04-04",
        "2024-05-03", "2024-06-02", "2024-07-02",
    ]
    cycles = GannAnalyzer.detect_cycles(pivots)
    for c in cycles:
        print(f"   Next pivot: {c.date.strftime('%Y-%m-%d')}  |  {c.description}")

    # --- Example 9: SAP (from PDF 4) ---
    print("\n" + "-" * 78)
    print("9. SEMI-ANNUAL PIVOT (SAP)")
    print("   Source: PDF 4 - Jan SAP example")
    print("-" * 78)

    sap = GannAnalyzer.semi_annual_pivot(
        open_price=8273, high=8446, low=8065, close=8277,
    )
    for k, v in sap.items():
        print(f"   {k:>6}: {v}")

    # --- Example 10: Unified Signal ---
    print("\n" + "-" * 78)
    print("10. UNIFIED TRADING SIGNAL")
    print("    Merging all methods for SBI intraday example")
    print("-" * 78)

    signal = analyzer.generate_signal(
        high=3238.35,
        low=3214.10,
        current_price=3225.0,
        prices_history=sbi_prices,
        account_size=100000.0,
    )
    print(f"   Direction:    {signal.direction}")
    print(f"   Entry price:  {signal.entry_price}")
    print(f"   Stop loss:    {signal.stop_loss}")
    print(f"   Targets:      {signal.targets}")
    print(f"   Confidence:   {signal.confidence}")
    print(f"   Vibration:    {signal.vibration_digit}")
    print(f"   Reasons:")
    for r in signal.reasons:
        print(f"     - {r}")

    print("\n" + "=" * 78)
    print("Algorithm demonstration complete.")
    print("=" * 78)


if __name__ == "__main__":
    main()
