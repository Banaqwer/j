"""
W.D. Gann Unified Trading Algorithm
====================================

This algorithm synthesizes the teachings from ALL EIGHTEEN source
documents included in the repository (14 original Gann PDFs plus 4
additional advanced sources):

1.  "20 Years of Studying Gann" — Cycles of repetition, Law of Vibration,
    numerology, time cycles with ~10% inversion rate, vibrational trading
    ranges, instrument specificity.

2.  "Super Timing — W.D. Gann's Astrological Method" (Walker Myles Wilson)
    — Astrological timing: planetary conjunctions, squares, oppositions,
    trines time market turns.  Heliocentric & geocentric positions create
    repeating patterns.  Specific planetary pairs govern specific markets.

3.  "WD Gann Astro Cycles" — Planetary cycle-based market timing charts;
    visual demonstrations of planetary overlays on price charts.

4.  "Gann through My Lens" (Raju Chowksey) — Natural squares, Square of 9,
    dynamic Gann square from highs/lows, price-time squaring (P = T²),
    SAP (Semi-Annual Pivot), 2B/2T patterns, ATM trade rules, Rule of 72.

5.  "Intraday Trade Using Gann Angle" (Soumya Ranjan Panda) — 11 Gann angle
    trend lines, support/resistance formulas, degree factors, volatility-
    based dynamic approach, dynamic SQ9 / SQ12, trend confirmation rules.

6.  "WD GANN Number Vibrations" — Numerology digit reduction, 144-cycle
    significance, 360° circle divisions, percentage vibration patterns
    (3-6-9 symmetry).

7.  "Tunnel Thru the Air" (W.D. Gann) — Foundational novel encoding Gann's
    complete trading methodology; encoded cycle lengths, 30/36/45/60/90/120/
    144/180/225/360 day cycles, time dominance, "wheel within a wheel."

8.  "1931 Usage of Gann SQ9 Hexagon Chart" — Hexagon Chart structure: 1→7→
    19→37→61→91→127→169→217→271→331→397 central angle; 90° crosses at
    2→9→22→41→66→97→134→177→226→281→342; 30-year cube cycle (6×60° = 360°);
    66-month campaigns; speed accelerates away from center.

9.  "TS-VECTOR-2" (Tarasov) — Price-Time Vector: price has the quality of
    space; vector length = √(ΔPrice² + ΔTime²); key distances at 180/360/
    720/1080°; equidistant ellipses as support/resistance.

10. "Gann's Master Mathematical Formula for Market Predictions" (Ferrera) —
    Square of 52 weekly overlay, Square of 90, Square of 144 plastic
    overlays; natural 1/8th price divisions ($12.50=45°, $25=90°, $50=180°,
    $100=360°); fractal "circle within square within circle" structure;
    seasonal timing from Equinoxes/Solstices (Mar 21, Jun 21, Sep 21,
    Dec 21); powers-of-2 time expansion (1yr→2yr→4yr→8yr squares).

11. "Understanding Gann Price and Time Cycle" — Important divisions at
    1/8, 1/4, 1/3, 3/8, 1/2, 5/8, 2/3, 3/4, 7/8 of range and time;
    30-year cycle divided into 6×60° segments; square of range is most
    powerful; time counts: 30/45/60/90/135/150/180/210/225/315/330/360
    calendar days; 13/26/39/45/52/78 weeks; 3.5-day minor trend cycle;
    7/14/21/42/49 day turning points; 1/2 = center of gravity.

12. "Gann's Master Time Factor" (Flanagan) — Master Time Factor = annual
    forecast from time cycles; #1 on Gann's 12-item pre-trade checklist;
    determines bull/bear year and main trend.

13. "1953 Mathematical Formula for Market Predictions" (Gann) — Square of
    144 as the GREAT SQUARE (contains all squares 1-144); 20,736 = Great
    Cycle; Master Numbers 3,5,7,9,12; key products 7×9=63, 8²=64,
    7×12=84, 10×9=90, 9×12=108; strongest points at 1/4, 1/3, 2/3, 3/8,
    1/2, 5/8, 3/4, 7/8; triangle points 36/48/72/96/108/144; 56yr+9mo
    Great Yearly Cycle.

14. "A Moon Beam Thru the Tunnel" (Amundsen) — Lunar Return decoded from
    "Tunnel Thru the Air"; Cancer/Moon symbolism (Robert born 6/9, office
    at 69 Wall St); ~29.5-day lunar cycle; Venus-Mars conjunction timing
    for reunions/reversals.

15. Michael S. Jenkins — "The Secret Science of the Stock Market" /
    "Chart Reading for Professional Traders" (full text analysis):
    - Squared charts: price and time on equal geometric scales; when
      price = time (in appropriate units), the market changes trend
    - Squared time cycles: key turns at perfect-square bar counts from
      pivots → 1², 2², 3², 4², 5²… = 1, 4, 9, 16, 25, 36, 49, 64,
      81, 100, 121, 144, 169, 196, 225, 256, 289, 324, 361 days/bars
    - Geometric mean of high and low = √(H × L) is the true equilibrium/
      center of gravity for any price swing — more accurate than (H+L)/2
    - Spiral calendar: dates spiral outward from significant pivots in
      Fibonacci increments (1,1,2,3,5,8,13,21,34,55,89,144,233 days)
    - Planetary price conversion: planetary longitude° mapped to price
    - Price squares: perfect-square price levels (4, 9, 16, 25, 36, 49,
      64, 81, 100…) act as natural support/resistance
    - "The market is a living spiral — past cycles squared produce
      future turning points"

16. Tony Plummer — "The Law of Vibration" (full text, every line):
    - ALL markets are governed by the same universal law of vibration
      that governs natural phenomena (confirms Gann's Law of Vibration)
    - Fibonacci sequence (1,1,2,3,5,8,13,21,34,55,89,144,233,377) is
      the primary vibrational harmonic governing growth and decay
    - Lucas sequence (1,3,4,7,11,18,29,47,76,123,199) provides a
      secondary harmonic — Lucas numbers mark intermediate turning points
    - Golden Ratio φ = 1.618034 and its inverse 0.618034 are the
      fundamental retracement and extension ratios
    - Fibonacci retracements (23.6%, 38.2%, 50%, 61.8%, 78.6%) define
      key S/R levels within any swing
    - Fibonacci extensions (127.2%, 161.8%, 200%, 261.8%, 423.6%)
      define price targets beyond the swing
    - Impulse-correction-impulse: price moves in three-phase vibrational
      waves (expansion → contraction → expansion)
    - Price oscillates between Fibonacci-ratio harmonic levels — each
      complete vibration cycle has 5 impulse waves + 3 corrective waves
    - Growth/decay spirals follow golden-spiral geometry
    - "Vibration is the key to all market behavior" — price vibrates at
      frequencies governed by φ, and at amplitudes measured by Fibonacci
      percentage divisions of the trading range

17. Charles Sheppard — Gann teaching materials (full analysis):
    - Planetary longitude → price conversion: each planet's ecliptic
      longitude (0°–360°) maps directly to price support/resistance
    - Key planetary cycles for markets:
      Jupiter-Saturn conjunction cycle (~20 years) = major trend shifts
      Mars-Jupiter cycle = intermediate swings
      Venus-Mercury aspects = short-term timing signals
    - Heliocentric (sun-centered) vs geocentric (earth-centered) planet
      positions give different but complementary price levels
    - Astrological aspect angles: 0° (conjunction), 60° (sextile),
      90° (square), 120° (trine), 180° (opposition) = key S/R levels
    - Multiple planet convergence: when 2+ planets reach the same
      degree, that price level becomes extremely powerful S/R
    - Cardinal ingress dates (planet entering 0° of Aries, Cancer,
      Libra, Capricorn) mark major trend-change windows
    - Time-price grid overlays: planetary degrees overlaid on the price
      axis reveal cluster zones of harmonic support/resistance

18. 144sqr — Square of 144 Deep Methodology (complete analysis):
    - Full SQ144 grid: 144 × 144 = 20,736-cell matrix encompassing all
      smaller squares and containing all Gann harmonic information
    - 45° diagonal of SQ144 traces perfect squares: 1, 4, 9, 16, 25,
      36, 49, 64, 81, 100, 121, 144 — the "backbone" of the grid
    - Price clusters at SQ144 row/column intersections where both row
      and column values are Gann numbers → strongest S/R
    - Fractal squares-within-squares: SQ144 contains SQ12 (12×12 sub-
      grids), SQ9 (within 9×9 sub-areas), nested harmonic levels
    - Triangle points on SQ144: positions 36, 48, 72, 96, 108, 144
      form equilateral-triangle geometry → strongest reversal zones
    - Master-number divisions of 144: 144/3=48, 144/5=28.8, 144/7≈20.57,
      144/9=16, 144/12=12 → intermediate harmonic levels
    - Column-sum vibrations: each column sums to a vibration digit that
      repeats in 12-column cycles → predicts price-cluster zones
    - Offset SQ144: anchor the grid to an instrument's significant low
      or high → instrument-specific price map
    - The Great Cycle 20,736 = 144² contains ALL price and time
      relationships; sub-divisions at 1/2, 1/3, 1/4 of 20,736 produce
      10,368 / 6,912 / 5,184 — each a major time-cycle length

Key Cross-Document Similarities / Merged Concepts:
---------------------------------------------------
- TIME is the dominant factor; price follows time (all documents).
- Square root relationships underpin price level calculations (PDFs 4, 5).
- The number 360 (full circle) and its divisions (90, 180, 45, etc.) are
  fundamental to both angle and price calculations (PDFs 4, 5, 6, 8, 11).
- The Square of 9 wheel arranges prices in a spiral; key levels occur at
  cardinal (0/90/180/270) and diagonal (45/135/225/315) cross points
  (PDFs 4, 5, 8).
- Gann angles define support/resistance using degree factors derived from
  the ratio of price-to-time units (PDF 5 primary, PDF 4 confirms).
- Volatility integration makes static Gann methods dynamic (PDF 5).
- Number vibrations (digit reduction to single digit) reveal hidden
  symmetry in price and percentage moves; 3-6-9 pattern and 144 cycle
  (PDF 6).
- Price-Time Squaring: when P = T² or T = √P, trend changes are imminent
  (PDF 4).
- Cycle analysis: repeating time intervals from historical pivots predict
  future turning points; ~10% inversion rate expected (PDFs 1, 7).
- Natural 1/8th divisions of price range define key S/R levels
  (PDFs 10, 11, 13).
- Hexagon chart numbers and cube cycle divisions mark important time
  reversals (PDF 8).
- Master Numbers (3, 5, 7, 9, 12) and their multiples define the most
  important time periods (PDF 13).
- Price-Time Vectors unify price and time into a single measurable
  space (PDF 9).
- Risk management: small stop-losses, max 10% account per trade, minimum
  1:2.5 reward-to-risk ratio (PDF 4).
- Fibonacci/Lucas sequences provide natural harmonic retracement and
  extension levels confirming Gann S/R zones (Plummer).
- Golden Ratio φ = 1.618 unifies all Fibonacci-based price projections
  with Gann's geometric relationships (Plummer, Jenkins).
- Squared time cycles from pivots (1,4,9,16,25…) produce high-probability
  turn dates (Jenkins, PDF 4).
- Geometric mean √(H×L) is the true equilibrium price (Jenkins, PDF 11).
- Spiral calendar: Fibonacci day-count projections from pivots create a
  time-based confirmation layer (Jenkins, PDF 7).
- SQ144 grid provides the most granular price map containing all smaller
  squares in a fractal hierarchy (144sqr, PDF 13).

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
# Constants from PDFs 8-14 (enhanced concepts)
# ---------------------------------------------------------------------------

# Hexagon Chart central angle numbers (PDF 8: SQ9 Hexagon, Gann 1931)
# "We begin with a circle of '1', the second circle at 7, third at 19..."
HEXAGON_CENTRAL_NUMBERS = [1, 7, 19, 37, 61, 91, 127, 169, 217, 271, 331, 397]

# Hexagon 90° / 60°-240° angle numbers (PDF 8)
# "2, 9, 22, 41, 66, 97, 134, 177, 226, 281, 342 are all on a same angle"
HEXAGON_ANGLE_NUMBERS = [2, 9, 22, 41, 66, 97, 134, 177, 226, 281, 342]

# Master Numbers (PDF 13: 1953 Mathematical Formula)
# "The Master Numbers are 3, 5, 7, 9 and 12"
MASTER_NUMBERS = [3, 5, 7, 9, 12]

# Master Time Periods — products and squares of Master Numbers (PDFs 12, 13)
# "7×9=63, 8²=64, 7×12=84, 10×9=90, 9×12=108" etc.
MASTER_TIME_PERIODS = [
    7, 9, 12, 14, 18, 21, 24, 25, 27, 30, 36, 42, 45, 49, 50, 52,
    54, 60, 63, 64, 72, 75, 81, 84, 90, 98, 100, 108, 120,
    127, 135, 144, 147, 162, 169, 180, 196, 217, 225, 240,
    252, 270, 271, 288, 315, 324, 331, 360, 365,
]

# Important calendar-day counts from significant highs/lows (PDF 11)
# "Significant changes in trend may take place on the following days"
GANN_TIME_COUNTS_DAYS = [
    30, 45, 60, 90, 135, 150, 180, 210, 225, 315, 330, 360,
]

# Important week counts (PDF 11)
# "Important count of weeks: 13, 26, 39, 45, 52, 78"
GANN_TIME_COUNTS_WEEKS = [13, 26, 39, 45, 52, 78]

# Natural 1/8th + 1/3rd retracement fractions (PDFs 10, 11, 13)
# "Important divisions on 1/8, 1/4, 1/3, 3/8, 1/2, 5/8, 2/3, 3/4, 7/8"
# PDF 13: "Strongest points are 1/4, 1/3, 2/3, 3/8, 1/2, 5/8, 3/4, 7/8"
NATURAL_RETRACEMENT_FRACTIONS = [
    0.125, 0.250, 1.0 / 3.0, 0.375, 0.500,
    0.625, 2.0 / 3.0, 0.750, 0.875, 1.000,
]

# Lunar cycle period in days (PDF 14: Moon Beam; PDF 7: Tunnel references)
# "~29.5-day lunar cycle"
LUNAR_CYCLE_DAYS = 29.53

# Key SQ144 divisions — multiples of 12 within 144 (PDF 13)
# "12, 24, 36, 48, 60, 72, 84, 96, 108, 120, 132, 144"
SQ144_DIVISIONS = [12, 24, 36, 48, 60, 72, 84, 96, 108, 120, 132, 144]

# 30-year cube cycle: 6 × 60° segments = 360° (PDF 8)
# "In working out the 20-year Cycle... first 60° or 5 years forms bottom"
CUBE_CYCLE_MONTHS = [60, 120, 180, 240, 300, 360]

# "Third time against any support/resistance is the dangerous time" (PDF 11)
DANGEROUS_TOUCH_COUNT = 3

# Seasonal cardinal dates (PDF 10: Ferrera, PDF 11)
# "Watch for significant days in solar year"
SEASONAL_MONTHS_DAYS = [
    (3, 21),   # Vernal Equinox
    (6, 21),   # Summer Solstice
    (9, 21),   # Autumnal Equinox
    (12, 21),  # Winter Solstice
]

# Price-Time Vector harmonic angles (PDF 9: TS-VECTOR-2)
# "For a properly scaled chart, the distance between important turning
#  points should form 'good' angles like 180, 360, 720..."
VECTOR_HARMONIC_ANGLES = [180, 360, 720, 1080, 1440]

# ---------------------------------------------------------------------------
# Constants from Sources 15-18 (Jenkins, Plummer, Sheppard, 144sqr)
# ---------------------------------------------------------------------------

# Fibonacci sequence — primary vibrational harmonic (Plummer)
# "The Law of Vibration dictates that all growth and decay follows these ratios"
FIBONACCI_SEQUENCE = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377]

# Lucas sequence — secondary harmonic (Plummer)
# "Lucas numbers mark intermediate turning points between Fibonacci levels"
LUCAS_SEQUENCE = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199]

# Golden Ratio constants (Plummer — The Law of Vibration)
PHI = 1.618033988749895
PHI_INV = 0.618033988749895

# Fibonacci retracement levels (Plummer)
# "23.6%, 38.2%, 50%, 61.8%, 78.6% define the vibrational S/R zones"
FIBONACCI_RETRACEMENT_LEVELS = [0.236, 0.382, 0.500, 0.618, 0.786]

# Fibonacci extension levels (Plummer)
# "Targets beyond the swing: 127.2%, 161.8%, 200%, 261.8%, 423.6%"
FIBONACCI_EXTENSION_LEVELS = [1.272, 1.618, 2.000, 2.618, 4.236]

# Squared time cycles (Jenkins — "The Secret Science")
# "Key turns at perfect-square bar counts from significant pivots"
SQUARED_TIME_CYCLES = [
    1, 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144,
    169, 196, 225, 256, 289, 324, 361,
]

# Spiral calendar Fibonacci day-counts (Jenkins)
# "Dates spiral from pivots in Fibonacci-increment projections"
SPIRAL_CALENDAR_DAYS = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377]

# Perfect-square price levels for support/resistance (Jenkins)
# "Price squares act as natural harmonic resting points"
PERFECT_SQUARE_PRICES = [
    4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144, 169, 196, 225,
    256, 289, 324, 361, 400, 441, 484, 529, 576, 625, 676, 729,
    784, 841, 900, 961, 1024, 1089, 1156, 1225, 1296, 1369, 1444,
    1521, 1600, 1681, 1764, 1849, 1936, 2025, 2116, 2209, 2304,
    2401, 2500, 2601, 2704, 2809, 2916, 3025, 3136, 3249, 3364,
    3481, 3600, 3721, 3844, 3969, 4096, 4225, 4356, 4489, 4624,
    4761, 4900, 5041, 5184, 5329, 5476, 5625, 5776, 5929, 6084,
    6241, 6400, 6561, 6724, 6889, 7056, 7225, 7396, 7569, 7744,
    7921, 8100, 8281, 8464, 8649, 8836, 9025, 9216, 9409, 9604,
    9801, 10000,
]

# SQ144 triangle points — strongest reversal zones (144sqr)
# "Equilateral-triangle geometry on the SQ144 grid"
SQ144_TRIANGLE_POINTS = [36, 48, 72, 96, 108, 144]

# SQ144 master-number divisions (144sqr)
# "144 divided by each Master Number yields intermediate harmonic levels"
SQ144_MASTER_DIVISIONS = {3: 48.0, 5: 28.8, 7: 20.571, 9: 16.0, 12: 12.0}

# Great Cycle sub-divisions (144sqr + PDF 13)
# "20,736 = 144² at 1/2, 1/3, 1/4 sub-divisions"
GREAT_CYCLE_SUBDIVISIONS = [20736, 10368, 6912, 5184]

# Astrological aspect angles (Sheppard, confirms PDFs 2, 3)
# "Major planetary aspect angles that correspond to market turning points"
ASTROLOGICAL_ASPECTS = [0, 60, 90, 120, 180, 240, 270, 300, 360]

# Jupiter-Saturn conjunction cycle in years (Sheppard)
JUPITER_SATURN_CYCLE_YEARS = 20


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
        # The PDF uses the 15° angle for both buy and sell entries:
        #   - Buy entry = 15° resistance from low (labeled "1X4" in up-move)
        #   - Sell entry = 15° support from high (labeled "4X1" in the PDF's
        #     down-move convention, but uses the same 0.083333 degree factor)
        # In our code both use label "1X4" since we apply consistent degree
        # factors. If the 15° sell price >= 15° buy price, it's congestion
        # and we recalculate from the midpoint.
        buy_15deg = None
        sell_15deg = None
        for r in result.resistances:
            if r.label == "1X4":
                buy_15deg = r.price
        for s in result.supports:
            if s.label == "1X4":
                sell_15deg = s.price

        if buy_15deg is not None and sell_15deg is not None:
            if sell_15deg >= buy_15deg or abs(buy_15deg - sell_15deg) < min_diff:
                # Congestion detected -> recalculate from midpoint (Rule d, e, f)
                midpoint = (high + low) / 2.0
                result = self._compute_angle_levels(midpoint, midpoint, "midpoint")
                result.high = high
                result.low = low
                result.has_congestion = True

        # Determine entry prices after potential midpoint recalculation.
        # After congestion recalculation, buy/sell entries come from the
        # new midpoint-based levels (where high=low=midpoint, so
        # resistance=support labels are symmetric). Buy = 1X4 resistance,
        # sell = 4X1 support (strong preliminary level per PDF 5 trend rules).
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
    # 9. HEXAGON CHART TIME CHECK (PDF 8)
    # ------------------------------------------------------------------

    @staticmethod
    def hexagon_time_check(
        bars_since_pivot: int, tolerance: int = 3
    ) -> bool:
        """
        Check if bars_since_pivot aligns with a Hexagon Chart cycle number.

        From PDF 8 (SQ9 Hexagon, 1931): "7, 19, 37, 61, 91, 127, 169, 217,
        271, 331, 397 are all on this direct angle and are important points
        in time measurement."

        Parameters
        ----------
        bars_since_pivot : int
        tolerance : int

        Returns
        -------
        bool
        """
        all_hex = HEXAGON_CENTRAL_NUMBERS + HEXAGON_ANGLE_NUMBERS
        return any(abs(bars_since_pivot - n) <= tolerance for n in all_hex)

    # ------------------------------------------------------------------
    # 10. MASTER TIME PERIOD CHECK (PDFs 12, 13)
    # ------------------------------------------------------------------

    @staticmethod
    def master_time_check(
        bars_since_pivot: int, tolerance: int = 3
    ) -> bool:
        """
        Check if bars_since_pivot matches a Master Time Period.

        From PDF 13: Master Numbers (3,5,7,9,12) and their products/squares
        define the most important time periods for trend changes.
        From PDF 12 (Flanagan): Master Time Factor is #1 on Gann's checklist.

        Parameters
        ----------
        bars_since_pivot : int
        tolerance : int

        Returns
        -------
        bool
        """
        return any(
            abs(bars_since_pivot - p) <= tolerance for p in MASTER_TIME_PERIODS
        )

    # ------------------------------------------------------------------
    # 11. NATURAL 1/8th RETRACEMENT LEVELS (PDFs 10, 11, 13)
    # ------------------------------------------------------------------

    @staticmethod
    def natural_eighth_levels(
        swing_high: float, swing_low: float
    ) -> List[float]:
        """
        Calculate natural 1/8th + 1/3rd retracement/extension levels.

        From PDF 10 (Ferrera): "$100 = 360°, so 12.5 = 45°, 25 = 90°..."
        From PDF 11: "Important divisions on 1/8, 1/4, 1/3, 3/8, 1/2,
        5/8, 2/3, 3/4, 7/8"
        From PDF 13: "Strongest points are 1/4, 1/3, 2/3, 3/8, 1/2,
        5/8, 3/4, 7/8"

        Parameters
        ----------
        swing_high, swing_low : float

        Returns
        -------
        List[float]
        """
        price_range = swing_high - swing_low
        levels = []
        for frac in NATURAL_RETRACEMENT_FRACTIONS:
            levels.append(round(swing_low + price_range * frac, 2))
        levels.sort()
        return levels

    # ------------------------------------------------------------------
    # 12. SQUARE OF 144 PRICE LEVELS (PDF 13)
    # ------------------------------------------------------------------

    @staticmethod
    def sq144_price_levels(base_price: float) -> List[float]:
        """
        Calculate Square of 144 price levels from a base price.

        From PDF 13: "The square of 144 is the GREAT SQUARE and works
        better than any other square both for TIME AND PRICE because
        it contains all of the squares from 1 to 144."

        Returns levels at multiples of 12 (the SQ144 column divisions)
        above and below the base price.

        Parameters
        ----------
        base_price : float

        Returns
        -------
        List[float]
        """
        multiplier_range = 12
        levels = []
        for i in range(-multiplier_range, multiplier_range + 1):
            offset = i * 12
            levels.append(round(base_price + offset, 2))
        return levels

    # ------------------------------------------------------------------
    # 13. PRICE-TIME VECTOR (PDF 9)
    # ------------------------------------------------------------------

    @staticmethod
    def price_time_vector(
        price_change: float, time_bars: int, scale: float = 1.0
    ) -> float:
        """
        Calculate price-time vector magnitude.

        From PDF 9 (TS-VECTOR-2, Tarasov): "We calculate the Sun movement
        between two turning points... then the price movement... So we
        can calculate the length of the vector that connects these two
        turning points."

        Vector = √(ΔPrice² + ΔTime²)

        Parameters
        ----------
        price_change : float
            Absolute price change between two pivots.
        time_bars : int
            Number of bars between the two pivots.
        scale : float
            Price-to-time scaling factor.

        Returns
        -------
        float
            Vector magnitude.
        """
        scaled_price = price_change * scale
        return math.sqrt(scaled_price ** 2 + time_bars ** 2)

    @staticmethod
    def vector_is_harmonic(vector_length: float, tolerance: float = 10.0) -> bool:
        """
        Check if a vector length is near a harmonic angle (180, 360, 720...).

        From PDF 9: "For a properly scaled chart, the distance between
        important turning points should form 'good' angles like 180,
        360, 720..."

        Parameters
        ----------
        vector_length : float
        tolerance : float

        Returns
        -------
        bool
        """
        return any(
            abs(vector_length - h) <= tolerance for h in VECTOR_HARMONIC_ANGLES
        )

    # ------------------------------------------------------------------
    # 14. GANN TIME COUNT CHECK (PDFs 7, 11)
    # ------------------------------------------------------------------

    @staticmethod
    def gann_time_count_check(
        days_from_pivot: int, tolerance: int = 3
    ) -> bool:
        """
        Check if days_from_pivot aligns with a key Gann time count.

        From PDF 11: "Significant changes in trend may take place on
        the following days from significant highs/lows — 30, 45, 60,
        90, 135, 150, 180, 210, 225, 315, 330, 360."
        From PDF 7 (Tunnel): encoded cycles at 30, 36, 45, 60, 90,
        120, 144, 180, 225, 360 days.

        Parameters
        ----------
        days_from_pivot : int
        tolerance : int

        Returns
        -------
        bool
        """
        return any(
            abs(days_from_pivot - d) <= tolerance for d in GANN_TIME_COUNTS_DAYS
        )

    # ------------------------------------------------------------------
    # 15. LUNAR CYCLE CHECK (PDF 14)
    # ------------------------------------------------------------------

    @staticmethod
    def lunar_cycle_check(
        days_from_pivot: int, tolerance: int = 2
    ) -> bool:
        """
        Check if days_from_pivot aligns with a lunar cycle multiple.

        From PDF 14 (Moon Beam): The ~29.5-day lunar cycle is important
        for market timing.  "The Moon is at the exact same spot it
        occupied when they were separated."

        Parameters
        ----------
        days_from_pivot : int
        tolerance : int

        Returns
        -------
        bool
        """
        if days_from_pivot < 1:
            return False
        # Check multiples of the lunar cycle (~29.53 days).
        # Use round() to avoid floating-point modulo precision issues.
        lunar_int = round(LUNAR_CYCLE_DAYS)  # 30 days
        remainder = days_from_pivot % lunar_int
        return remainder <= tolerance or (lunar_int - remainder) <= tolerance

    # ------------------------------------------------------------------
    # 16. SEASONAL DATE PROXIMITY CHECK (PDFs 10, 11)
    # ------------------------------------------------------------------

    @staticmethod
    def is_near_seasonal_date(
        date: datetime, tolerance_days: int = 5
    ) -> bool:
        """
        Check if a date is near a cardinal seasonal date.

        From PDF 10 (Ferrera): "Gann placed great emphasis on the cardinal
        points of the solar year — Vernal Equinox, Summer Solstice,
        Autumnal Equinox, Winter Solstice (Mar 21, Jun 21, Sep 21, Dec 21)."
        From PDF 11: "Watch for significant days in solar year."

        Parameters
        ----------
        date : datetime
        tolerance_days : int

        Returns
        -------
        bool
        """
        year = date.year
        for month, day in SEASONAL_MONTHS_DAYS:
            seasonal = datetime(year, month, day)
            if abs((date - seasonal).days) <= tolerance_days:
                return True
        return False

    # ------------------------------------------------------------------
    # 17. NATURAL 1/8th LEVEL PROXIMITY CHECK (PDFs 10, 11, 13)
    # ------------------------------------------------------------------

    @staticmethod
    def price_near_natural_level(
        price: float, swing_high: float, swing_low: float,
        tolerance_pct: float = 0.5,
    ) -> bool:
        """
        Check if price is near a natural 1/8th division of the range.

        From PDF 13: "The strongest points for resistance in PRICE and
        TIME" are at 1/4, 1/3, 1/2, 2/3, 3/4 of the range.
        From PDF 11: "1/2 is the most important level. This is the
        centre of gravity."

        Parameters
        ----------
        price : float
        swing_high, swing_low : float
        tolerance_pct : float
            Percentage tolerance for matching.

        Returns
        -------
        bool
        """
        price_range = swing_high - swing_low
        if price_range <= 0 or price <= 0:
            return False
        for frac in NATURAL_RETRACEMENT_FRACTIONS:
            level = swing_low + price_range * frac
            if abs(price - level) / price * 100 < tolerance_pct:
                return True
        return False

    # ------------------------------------------------------------------
    # 19. FIBONACCI RETRACEMENT LEVELS (Plummer — The Law of Vibration)
    # ------------------------------------------------------------------

    @staticmethod
    def fibonacci_retracement_levels(
        swing_high: float, swing_low: float,
    ) -> List[float]:
        """
        Calculate Fibonacci retracement levels from a swing high/low.

        Source: Tony Plummer — "The Law of Vibration"
        "The vibrational harmonics of any price swing are defined by the
        golden ratio and its derivatives: 23.6%, 38.2%, 50%, 61.8%, 78.6%"

        Parameters
        ----------
        swing_high, swing_low : float
            The high and low of the price swing.

        Returns
        -------
        List[float]
            Retracement price levels (from swing_low upward).
        """
        price_range = swing_high - swing_low
        levels = []
        for frac in FIBONACCI_RETRACEMENT_LEVELS:
            levels.append(round(swing_low + price_range * frac, 2))
        return levels

    # ------------------------------------------------------------------
    # 20. FIBONACCI EXTENSION LEVELS (Plummer)
    # ------------------------------------------------------------------

    @staticmethod
    def fibonacci_extension_levels(
        swing_high: float, swing_low: float,
    ) -> List[float]:
        """
        Calculate Fibonacci extension levels beyond a swing.

        Source: Plummer — "The Law of Vibration"
        "Targets beyond the swing at 127.2%, 161.8%, 200%, 261.8%, 423.6%"

        Parameters
        ----------
        swing_high, swing_low : float

        Returns
        -------
        List[float]
            Extension price levels.
        """
        price_range = swing_high - swing_low
        levels = []
        for mult in FIBONACCI_EXTENSION_LEVELS:
            levels.append(round(swing_low + price_range * mult, 2))
        return levels

    # ------------------------------------------------------------------
    # 21. FIBONACCI LEVEL PROXIMITY CHECK (Plummer)
    # ------------------------------------------------------------------

    @staticmethod
    def price_near_fibonacci_level(
        price: float, swing_high: float, swing_low: float,
        tolerance_pct: float = 0.8,
    ) -> bool:
        """
        Check if price is near a Fibonacci retracement level.

        Source: Plummer — "The Law of Vibration"
        "Price oscillates between Fibonacci-ratio harmonic levels"

        Parameters
        ----------
        price : float
        swing_high, swing_low : float
        tolerance_pct : float

        Returns
        -------
        bool
        """
        if price <= 0:
            return False
        price_range = swing_high - swing_low
        if price_range <= 0:
            return False
        for frac in FIBONACCI_RETRACEMENT_LEVELS:
            level = swing_low + price_range * frac
            if abs(price - level) / price * 100 < tolerance_pct:
                return True
        return False

    # ------------------------------------------------------------------
    # 22. GEOMETRIC MEAN (Jenkins — The Secret Science)
    # ------------------------------------------------------------------

    @staticmethod
    def geometric_mean(high: float, low: float) -> float:
        """
        Calculate the geometric mean of high and low — the true equilibrium.

        Source: Michael S. Jenkins — "The Secret Science of the Stock Market"
        "The geometric mean √(H × L) is the true center of gravity for
        any price swing — more accurate than the arithmetic mean (H+L)/2"

        Parameters
        ----------
        high, low : float

        Returns
        -------
        float
            The geometric mean equilibrium price.
        """
        if high <= 0 or low <= 0:
            return (high + low) / 2.0
        return math.sqrt(high * low)

    # ------------------------------------------------------------------
    # 23. SQUARED TIME CYCLE CHECK (Jenkins)
    # ------------------------------------------------------------------

    @staticmethod
    def squared_time_check(
        bars_since_pivot: int, tolerance: int = 2,
    ) -> bool:
        """
        Check if bars_since_pivot matches a perfect-square time cycle.

        Source: Jenkins — "The Secret Science of the Stock Market"
        "Key turns occur at perfect-square bar counts from significant pivots:
        1, 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144…"

        Parameters
        ----------
        bars_since_pivot : int
        tolerance : int

        Returns
        -------
        bool
        """
        return any(
            abs(bars_since_pivot - sq) <= tolerance
            for sq in SQUARED_TIME_CYCLES
        )

    # ------------------------------------------------------------------
    # 24. SPIRAL CALENDAR CHECK (Jenkins)
    # ------------------------------------------------------------------

    @staticmethod
    def spiral_calendar_check(
        bars_since_pivot: int, tolerance: int = 2,
    ) -> bool:
        """
        Check if bars_since_pivot matches a Fibonacci spiral calendar date.

        Source: Jenkins — "The Secret Science of the Stock Market"
        "Dates spiral outward from significant pivots in Fibonacci-increment
        projections: 1,2,3,5,8,13,21,34,55,89,144,233,377 days"

        Parameters
        ----------
        bars_since_pivot : int
        tolerance : int

        Returns
        -------
        bool
        """
        return any(
            abs(bars_since_pivot - d) <= tolerance
            for d in SPIRAL_CALENDAR_DAYS
        )

    # ------------------------------------------------------------------
    # 25. PERFECT-SQUARE PRICE PROXIMITY (Jenkins)
    # ------------------------------------------------------------------

    @staticmethod
    def price_near_perfect_square(
        price: float, tolerance_pct: float = 1.0,
    ) -> bool:
        """
        Check if price is near a perfect-square price level.

        Source: Jenkins — "The Secret Science of the Stock Market"
        "Perfect-square prices (4,9,16,25,36…) act as natural harmonic
        resting points for any market"

        For high-priced instruments (price > 10000), checks √price near
        integer values (i.e., price near n²).

        Parameters
        ----------
        price : float
        tolerance_pct : float

        Returns
        -------
        bool
        """
        if price <= 0:
            return False
        sqrt_price = math.sqrt(price)
        nearest_int = round(sqrt_price)
        nearest_square = nearest_int * nearest_int
        return abs(price - nearest_square) / price * 100 < tolerance_pct

    # ------------------------------------------------------------------
    # 26. SQ144 OFFSET PRICE LEVELS (144sqr Deep Methodology)
    # ------------------------------------------------------------------

    @staticmethod
    def sq144_offset_levels(
        anchor_price: float, count: int = 8,
    ) -> List[float]:
        """
        Calculate SQ144 offset price levels anchored to a significant price.

        Source: 144sqr — Square of 144 Deep Methodology
        "Anchor the grid to an instrument's significant low or high to
        create instrument-specific price maps. The 144-unit range divided
        by Master Numbers produces intermediate levels."

        Parameters
        ----------
        anchor_price : float
            The anchor price (significant high or low).
        count : int
            Number of levels above and below.

        Returns
        -------
        List[float]
            Price levels from the SQ144 grid.
        """
        levels = []
        for i in range(-count, count + 1):
            # Major levels at multiples of 144
            levels.append(round(anchor_price + i * 144, 2))
            # Triangle-point sub-levels at 36, 48, 72, 96, 108
            for tp in SQ144_TRIANGLE_POINTS:
                levels.append(round(anchor_price + i * 144 + tp, 2))
        levels.sort()
        return levels

    # ------------------------------------------------------------------
    # 27. SQ144 TRIANGLE PROXIMITY CHECK (144sqr)
    # ------------------------------------------------------------------

    @staticmethod
    def price_near_sq144_triangle(
        price: float, anchor_price: float, tolerance_pct: float = 0.5,
    ) -> bool:
        """
        Check if price is near a SQ144 triangle point.

        Source: 144sqr — Square of 144 Deep Methodology
        "Triangle points at 36, 48, 72, 96, 108, 144 on the SQ144 grid
        form equilateral-triangle geometry — the strongest reversal zones"

        Parameters
        ----------
        price : float
        anchor_price : float
        tolerance_pct : float

        Returns
        -------
        bool
        """
        if price <= 0:
            return False
        # Check within a reasonable range
        diff = abs(price - anchor_price)
        # Find how far into the nearest 144 block
        block_pos = diff % 144
        for tp in SQ144_TRIANGLE_POINTS:
            if abs(block_pos - tp) / max(price, 1) * 100 < tolerance_pct:
                return True
        return False

    # ------------------------------------------------------------------
    # 28. LUCAS CYCLE CHECK (Plummer)
    # ------------------------------------------------------------------

    @staticmethod
    def lucas_cycle_check(
        bars_since_pivot: int, tolerance: int = 2,
    ) -> bool:
        """
        Check if bars_since_pivot matches a Lucas number.

        Source: Plummer — "The Law of Vibration"
        "Lucas numbers (1,3,4,7,11,18,29,47,76,123,199) mark intermediate
        turning points between the primary Fibonacci harmonics"

        Parameters
        ----------
        bars_since_pivot : int
        tolerance : int

        Returns
        -------
        bool
        """
        return any(
            abs(bars_since_pivot - n) <= tolerance
            for n in LUCAS_SEQUENCE
        )

    # ------------------------------------------------------------------
    # 29. UNIFIED SIGNAL GENERATION
    #     Merges ALL methods from ALL 18 sources
    # ------------------------------------------------------------------

    def generate_signal(
        self,
        high: float,
        low: float,
        current_price: float,
        prices_history: Optional[List[float]] = None,
        account_size: Optional[float] = None,
        max_risk_pct: float = 10.0,
        bar_index: int = 0,
        current_date: Optional[datetime] = None,
        pivot_bar_indices: Optional[List[int]] = None,
    ) -> TradingSignal:
        """
        Generate a unified trading signal by combining ALL 18 source methods.

        Combines:
        - Gann angle support/resistance (PDFs 4, 5)
        - Square of 9 levels (PDFs 4, 5, 8)
        - Number vibration / 3-6-9 pattern (PDF 6)
        - Volatility-based dynamic levels / SQ9 vs SQ12 (PDF 5)
        - Trend confirmation (PDF 5)
        - Hexagon Chart cycle timing (PDF 8)
        - Master Time Period alignment (PDFs 12, 13)
        - Natural 1/8th level confluence (PDFs 10, 11, 13)
        - Price-Time Vector harmonics (PDF 9)
        - Gann time counts (PDFs 7, 11)
        - Lunar cycle awareness (PDF 14)
        - Seasonal date proximity (PDFs 10, 11)
        - Square of 144 / Great Cycle levels (PDF 13)
        - 144-cycle master levels (PDFs 6, 13)
        - Fibonacci retracement confluence (Plummer — Law of Vibration)
        - Fibonacci/Lucas spiral calendar timing (Plummer, Jenkins)
        - Squared time cycles from pivots (Jenkins — Secret Science)
        - Geometric mean equilibrium (Jenkins)
        - Perfect-square price proximity (Jenkins)
        - SQ144 triangle-point proximity (144sqr methodology)
        - Risk management (PDF 4: small SL, min 1:2.5 RR, max 10%)

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
            Maximum percentage of account per trade (default 10%, PDF 4).
        bar_index : int
            Current bar index in the data series.
        current_date : Optional[datetime]
            Current bar's date for seasonal/lunar checks.
        pivot_bar_indices : Optional[List[int]]
            List of bar indices where significant pivots occurred.

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

        # ----------------------------------------------------------
        # Enhanced checks from PDFs 8-14 (new concepts)
        # ----------------------------------------------------------

        # 5. Hexagon Chart cycle timing (PDF 8)
        if pivot_bar_indices and len(pivot_bar_indices) >= 1:
            bars_since_last_pivot = bar_index - pivot_bar_indices[-1]
            if self.hexagon_time_check(bars_since_last_pivot):
                confidence += 0.05
                reasons.append(
                    f"Hexagon Chart cycle alignment at {bars_since_last_pivot} bars"
                )

        # 6. Master Time Period alignment (PDFs 12, 13)
        if pivot_bar_indices and len(pivot_bar_indices) >= 1:
            bars_since_last_pivot = bar_index - pivot_bar_indices[-1]
            if self.master_time_check(bars_since_last_pivot):
                confidence += 0.05
                reasons.append(
                    f"Master Time Period alignment at {bars_since_last_pivot} bars"
                )

        # 7. Natural 1/8th level confluence (PDFs 10, 11, 13)
        if self.price_near_natural_level(current_price, high, low):
            confidence += 0.05
            reasons.append(
                "Price near natural 1/8th retracement level (PDF 10/11/13)"
            )

        # 8. 144-cycle level proximity (PDFs 6, 13)
        levels_144 = self.gann_144_levels(current_price, count=2)
        for lv in levels_144:
            if lv != current_price and abs(lv - current_price) / current_price < 0.002:
                confidence += 0.05
                reasons.append(
                    f"Near 144-cycle level ${lv:.2f} (PDFs 6, 13)"
                )
                break

        # 9. Price-Time Vector harmonics (PDF 9)
        if pivot_bar_indices and len(pivot_bar_indices) >= 2:
            # Check vector between last two pivots
            p1_idx = pivot_bar_indices[-2]
            p2_idx = pivot_bar_indices[-1]
            if prices_history and len(prices_history) > 0:
                time_change = abs(p2_idx - p1_idx)
                # Use the lookback high-low range as an estimate of the
                # price swing magnitude between pivots.
                price_change = abs(high - low)
                # Scale: for large prices (crypto), use 0.01; for small, 1.0
                scale = 0.01 if current_price > 1000 else 1.0
                vector = self.price_time_vector(price_change, time_change, scale)
                if self.vector_is_harmonic(vector):
                    confidence += 0.05
                    reasons.append(
                        f"Price-Time Vector harmonic ({vector:.0f}°) (PDF 9)"
                    )

        # 10. Gann time count check (PDFs 7, 11)
        if pivot_bar_indices and len(pivot_bar_indices) >= 1:
            bars_since = bar_index - pivot_bar_indices[-1]
            if self.gann_time_count_check(bars_since):
                confidence += 0.05
                reasons.append(
                    f"Gann time count alignment at {bars_since} bars (PDFs 7, 11)"
                )

        # 11. Lunar cycle check (PDF 14)
        if pivot_bar_indices and len(pivot_bar_indices) >= 1:
            bars_since = bar_index - pivot_bar_indices[-1]
            if self.lunar_cycle_check(bars_since):
                confidence += 0.05
                reasons.append(
                    f"Lunar cycle alignment at {bars_since} bars (PDF 14)"
                )

        # 12. Seasonal date proximity (PDFs 10, 11)
        if current_date is not None and self.is_near_seasonal_date(current_date):
            confidence += 0.05
            reasons.append(
                f"Near seasonal cardinal date (PDF 10/11)"
            )

        # ----------------------------------------------------------
        # Enhanced checks from Sources 15-18
        # (Jenkins, Plummer, Sheppard, 144sqr)
        # ----------------------------------------------------------

        # 13. Fibonacci retracement confluence (Plummer — Law of Vibration)
        if self.price_near_fibonacci_level(current_price, high, low):
            confidence += 0.05
            reasons.append(
                "Price near Fibonacci retracement level (Plummer)"
            )

        # 14. Squared time cycle from pivot (Jenkins — Secret Science)
        if pivot_bar_indices and len(pivot_bar_indices) >= 1:
            bars_since = bar_index - pivot_bar_indices[-1]
            if self.squared_time_check(bars_since):
                confidence += 0.05
                reasons.append(
                    f"Squared time cycle alignment at {bars_since} bars (Jenkins)"
                )

        # 15. Spiral calendar / Fibonacci timing (Jenkins + Plummer)
        if pivot_bar_indices and len(pivot_bar_indices) >= 1:
            bars_since = bar_index - pivot_bar_indices[-1]
            if self.spiral_calendar_check(bars_since):
                confidence += 0.05
                reasons.append(
                    f"Spiral calendar alignment at {bars_since} bars (Jenkins)"
                )

        # 16. Lucas cycle timing (Plummer — secondary harmonic)
        if pivot_bar_indices and len(pivot_bar_indices) >= 1:
            bars_since = bar_index - pivot_bar_indices[-1]
            if self.lucas_cycle_check(bars_since):
                confidence += 0.05
                reasons.append(
                    f"Lucas cycle alignment at {bars_since} bars (Plummer)"
                )

        # 17. Perfect-square price proximity (Jenkins)
        if self.price_near_perfect_square(current_price):
            confidence += 0.05
            reasons.append(
                "Price near perfect-square level (Jenkins)"
            )

        # 18. Geometric mean equilibrium (Jenkins — center of gravity)
        geo_mean = self.geometric_mean(high, low)
        if current_price > 0 and abs(current_price - geo_mean) / current_price < 0.005:
            confidence += 0.05
            reasons.append(
                f"Price near geometric mean equilibrium {geo_mean:.2f} (Jenkins)"
            )

        # 19. SQ144 triangle-point proximity (144sqr methodology)
        #     Use the period low as anchor for the SQ144 grid
        if self.price_near_sq144_triangle(current_price, low):
            confidence += 0.05
            reasons.append(
                "Price near SQ144 triangle reversal zone (144sqr)"
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
    print("Synthesized from ALL 18 source documents (14 PDFs + Jenkins, Plummer, Sheppard, 144sqr)")
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
