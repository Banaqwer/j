"""
W.D. Gann Unified Trading Algorithm
====================================

This algorithm synthesizes the teachings from twenty-one W.D. Gann PDF documents:

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

8. "144 Square" - The 144 Square as a lattice mapping a multidimensional market
   into 2D; time-price configurations, gravity centers, stacking squares.

9. "1931 Usage of Gann SQ9 Hexagon Chart" - Hexagonal number arrangement, circle
   completions (1,7,19,37,61,...), the 20-year cycle as a cube.

10. "TS Vector 2" (Sergey Tarasov) - Price-time Universe with Euclidean metric,
    vector distance as harmonic angles (360°, 720°, 1080°).

11. "Gann's Master Mathematical Formula" (Daniel T. Ferrera) - Square of 52,
    fractal/musical octave nesting of squares at seasonal cardinal points.

12. "Understanding Gann Price and Time Cycle" - Range percentage divisions (1/8ths
    and 1/3rds), price-as-time squaring, important day/week/month counts.

13. "Gann's Master Time Factor" (Flanagan) - The $3,000 Master Time Factor =
    annual forecast from 7/10/20/30/60-year major time cycles.

14. "George Bayer Book III" - Astro-cycles, market natal charts, eclipses closing
    markets, ephemerides from 1536 validating centuries of cycle repetition.

15. "A Moon Beam Thru the Tunnel" (Amundsen) - Lunar Return as the hidden key
    to the Tunnel novel; Venus-Mars conjunctions in Cancer as timing mechanism.

16. "Jenkins UnEncrypted" (Michael S. Jenkins) - Complete trading course covering
    angles, arcs, Square of Nine, P=t^2 proof, mirror image foldbacks, 60-year cycle.

17. "1953 Mathematical Formula for Market Predictions" (W.D. Gann) - Great Cycle
    of 144^2 = 20,736; Master Numbers (3,5,7,9,12); strongest resistance fractions.

18. "Charles Shephard Gann Cycles Course" - Swing chart mechanical trading method,
    Gann percentage levels, sections/waves, squaring price/time from different points.

19. "1978 Astro-Cycles and Speculative Markets" (L.J. Jensen) - Law of Vibration
    as universal principle; planetary cycles as economic causes; arithmetic scale
    charting; 84-year Uranus epoch cycle; Jupiter-Saturn 20-year conjunction cycle;
    Moon's Node 18.6-year business cycle; five-phase intermediate trend structure;
    vectorial 45°+60° price-time projection; Mercury 88-day harmonics.

20. "W.D. Gann — The Basis of My Forecasting Method" - Gann's foundational paper
    on mathematical forecasting (image-based).

21. "The Law of Vibration" (Tony Plummer) - Formal treatment of vibration theory
    applied to financial markets (image-based).

22. "Sephariel — The Numbers Book" - Complete numerology system: unit system
    (1-9 with planetary rulers), Hebrew Kabalistic system (1-22 with zodiac),
    Numbers and Speculation chapter for stocks/shares: planetary rulership of
    sectors, number timing for trade entries, winning = odd, losing = even.

23. "Using Planetary Harmonics to Find Key Reversals" (Thomas Long) - Converting
    planetary longitude to price: 1 degree = price unit scaled by market range;
    mirror lines (360-degree inversion); harmonic divisions (360/1, /2=180,
    /3=120, /4=90); conjunction = most powerful reversal geometry.

24. "Gann Wheel" (Dave "Gann Wheel Man") - TIME is more important than price;
    time windows and time patterns; all markets turn at same time aspects;
    musical scale-planet-number correspondence table; 45° and 144° on the wheel
    convert date to price and vice versa; "zero drawdown point" exists.

25. "Spiral Chart — Gann Mysteries" - Complete Square of Nine construction;
    Futia's universal angular formula: A = MOD(180 × sqrt(P-1) - 225, 360);
    Octagon Chart (8th harmonic); odd squares on 315° axis, even on 45°;
    zodiacal overlay: 0°=Aries, 90°=Cancer, 180°=Libra, 270°=Capricorn.

26. "Advanced WD Gann Group" - Forum compilation: SQ9 as square root calculator;
    summation formula n/2×(n+1) for triangular numbers; planetary geocentric
    averaging for composite cycle; death zone concept; Saros 1260 cycle;
    "squaring price with time is the ONLY tool you need."

27. "Short-Term Market Forecasting via Astrology" - Multiple authors: biblical
    cycles (1260, 2520, 3.5 years); Saros eclipse cycles (6585.33 days);
    Gann-Fibonacci unification (Granville Cooley): master numbers, death zone,
    Great Cycle of Enoch; range expansion bias 75%+ (Toby Crabel).

Key Cross-Document Similarities / Merged Concepts:
---------------------------------------------------
- TIME is the dominant factor; price follows time (all documents).
- Square root relationships underpin price level calculations (PDFs 4, 5, 9, 12, 16).
- The number 360 (full circle) and its divisions (90, 180, 45, etc.) are
  fundamental across all mathematical PDFs (4, 5, 6, 8, 9, 10, 11, 12, 17).
- The Square of 9 wheel arranges prices in a spiral; key levels occur at
  cardinal (0/90/180/270) and diagonal (45/135/225/315) cross points (PDFs 4, 5).
- Gann angles define support/resistance using degree factors derived from
  the ratio of price-to-time units (PDF 5 primary, PDF 4 confirms).
- Volatility integration makes static Gann methods dynamic for intraday
  use (PDF 5). Higher prices → faster swings (PDF 8).
- Number vibrations (digit reduction to single digit) reveal hidden symmetry
  in price and percentage moves; the 3-6-9 pattern and 144 cycle (PDF 6).
- Price-Time Squaring: when P = T^2 or T = sqrt(P), trend changes are
  imminent (PDFs 4, 11, 12, 16, 17, 18).
- Cycle analysis: repeating time intervals from historical pivots predict
  future turning points; ~10% inversion rate expected (PDFs 1, 7, 13, 16, 18).
- Range percentage divisions (1/8ths and 1/3rds) apply to BOTH price AND time
  (PDFs 11, 12, 17, 18). The 50% level is the "center of gravity."
- Fractal/nested structure: inner squares are musical octaves (half size) at
  solstice points; markets are self-similar across timeframes (PDFs 8, 11, 17).
- Seasonal cardinal timing: year begins March 21; equinoxes and solstices
  define primary timing framework (PDFs 11, 12, 19).
- 192-day Master Time Factor: the diatonic octave cycle governing when the
  wheel returns to origin; Fa/La shock points invert price (PDF 6, pp.5-8).
- Third-Time Test Rule: the 3rd touch of any S/R zone is the dangerous/
  breakout time (PDF 10, p.2).
- Minor Trend Turns: 3rd/4th day from pivot = minor trend change; 14th day
  most significant, 21 next; also 7, 42, 45, 49 (PDFs 10, 16).
- Risk management: small stop-losses, max 10% account per trade, minimum
  1:2.5 reward-to-risk ratio (PDFs 1, 4, 18).
- Planetary longitude → price conversion: degree × scale_factor gives key
  S/R levels; conjunctions are the strongest reversals (PDFs 23, 26).
- Futia's SQ9 Angular Formula: A = MOD(180 × √(P-1) - 225, 360) converts
  any price to its angular position on the Square of Nine (PDF 25).
- Range Expansion: when daily range > previous day's range, next day has
  75%+ probability of continuing in expansion direction (PDF 27, Crabel).
- Saros Eclipse Cycle: 6585.33 days = 1260 years; Biblical 3.5 × 360 = 1260
  days links Gann's time counts to eclipse periodicity (PDFs 26, 27).
- Summation (triangular) numbers: n/2 × (n+1) = 1, 3, 6, 10, 15, 21, 28,
  36, 45, 55, 66, 78, 91, ..., 561 — function as natural S/R (PDF 26).
- Sephariel numerology: unit system (1-9) maps numbers to Sun/Moon/planets;
  Kabalistic system (1-22) extends mapping to zodiac signs (PDF 22).

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

# Hexagon chart circle completion values (from Gann SQ9 Hexagon Chart PDF)
HEXAGON_CIRCLES = [1, 7, 19, 37, 61, 91, 127, 169, 217, 271, 331, 397]

# Gann percentage divisions for range analysis (from Understanding Gann Price & Time)
GANN_PERCENTAGES = [0.125, 0.25, 0.333, 0.375, 0.5, 0.625, 0.666, 0.75, 0.875, 1.0]

# Master numbers (from 1953 Mathematical Formula PDF)
MASTER_NUMBERS = [3, 5, 7, 9, 12]

# Great Cycle of 144 squared = 20736 (from 1953 Mathematical Formula PDF)
GREAT_CYCLE = 20736

# Seasonal cardinal dates (month, day) - Gann's year starts March 21
CARDINAL_DATES = [(3, 21), (6, 21), (9, 21), (12, 21)]

# Square of 52 octave nesting dates (month, day) from Master Mathematical Formula
OCTAVE_DATES = [(2, 5), (5, 6), (8, 5), (11, 5)]

# ---------------------------------------------------------------------------
# NEW Constants discovered from page-by-page study (see PDF_STUDY_LOG.md)
# ---------------------------------------------------------------------------

# Shephard's Key Cycle Numbers — the MOST critical cycles (PDF 18, pp.85–86, 130, 148)
# These are the primary time cycles that cause major market reversals.
# 1260 = "a time, times, and half a time" = 360 + 720 + 180 (biblical, p.85)
# 1290 = 1260 + leap month of 30 days (p.86)
# 1336 = 3.6525 × 365.25 — Earth cycle squared (p.148)
# 631/668 = half-cycles of 1262/1336 (p.86)
# 840 = 1/3 of 2520 = 33.3% of 360 weeks (p.86)
SHEPHARD_KEY_CYCLES = [631, 668, 840, 1260, 1262, 1290, 1336]

# Planetary cycle lengths in days (PDF 18, pp.67, 71, 75, 108)
# Mars orbit = 687 days — appears frequently in S&P 500 and Australian SPI
# Venus synodic = 224 days — 672 = 3 × 224 = 4 × 168
# Week hours = 168 — "the hours of our week" — appears as symbolic number
MARS_CYCLE = 687
VENUS_CYCLE = 224
WEEK_HOURS = 168

# Divisions of 168 (hours in a week) — important S/R levels (PDF 18, p.75)
WEEK_HOUR_DIVISIONS = [21, 42, 63, 84, 105, 126, 147, 168, 336, 504, 672, 840]

# Gann's Fatal Number and its multiples (PDF 18, pp.86, 100; PDF 12, p.6)
# 49 = 7² — "Gann's Fatal Number" — major trend change trigger
# 343 = 7 × 49, 392 = 8 × 49, 490 = 10 × 49
FATAL_NUMBER = 49
FATAL_MULTIPLES = [49, 98, 147, 196, 245, 294, 343, 392, 441, 490]

# Biblical/symbolic numbers that appear at market reversals (PDF 18, p.85)
BIBLICAL_NUMBERS = [390, 430, 490, 666, 888, 1150, 2300]

# Wheel within a Wheel — extending 360° cycle to 2520° (PDF 18, p.73, p.85)
# 360 weeks = 2520 days. Key divisions: 630°, 840°, 900°, 1260°
WHEEL_CYCLE = 2520
WHEEL_DIVISIONS = [90, 120, 180, 240, 270, 360, 450, 480, 540, 630, 720,
                   840, 900, 1080, 1260, 1290, 1336, 1440, 1800, 2160, 2520]

# Important time counts in calendar days from highs/lows (PDF 12, p.3)
IMPORTANT_CALENDAR_DAYS = [30, 45, 60, 90, 135, 150, 180, 210, 225, 315, 330, 360]

# Important time counts in trading days (PDF 12, p.3)
IMPORTANT_TRADING_DAYS = [11, 22, 33, 45, 56, 67, 78, 90, 101, 112, 123, 135,
                          146, 157, 168, 180]

# Important week counts (PDF 12, p.4)
IMPORTANT_WEEKS = [7, 13, 26, 39, 45, 52, 78]

# ---------------------------------------------------------------------------
# Constants discovered from deep page-by-page study (session 5)
# ---------------------------------------------------------------------------

# 192 Calendar Day Master Time Factor (PDF 6 "144 Square", pages 5–8)
# The time factor governing when the wheel returns to its origin.
# Discovered via diatonic octave analysis: 24 octaves × 8 days = 192 CD.
# Robert Gordon born June 9 1906; discovered master time factor June 19 1927
# = 7680 days = 40 × 192.  Marie left June 5 1927, returned Aug 30 1932
# = 1913 days ≈ 10 × 192 − 7 (one diatonic octave).
# 144 square fits within 192 CD octave: 192 − 144 = 48 = 4 octaves of 12.
MASTER_TIME_FACTOR = 192

# 2556 = 7-year cycle in calendar days (PDF 16 "Shephard", p.142)
# When divided by 16ths, 32nds and 12ths gives S&P reversal dates.
SEVEN_YEAR_CYCLE_DAYS = 2556

# Third-time rule: the 3rd test of any S/R zone is the dangerous time
# (PDF 10 "Understanding Gann", p.2). Also: 1st, 2nd, 3rd, 4th, 7th, 9th,
# 12th squares of the low are significant.
SIGNIFICANT_SQUARES_OF_LOW = [1, 2, 3, 4, 7, 9, 12]

# Minor trend turn watch: 3.5 day / 7 / 14 / 21 days from pivot
# (PDF 10, p.2; PDF 16, p.50). 14th day is most significant, 21 next.
MINOR_TREND_DAYS = [3, 4, 7, 14, 21, 42, 45, 49]

# Gann percentage vibration pattern (PDF 4 "Number Vibrations", pages 1–2)
# When price percentage moves (3.125, 6.25, 9.375, ..., 100) are digit-reduced,
# they follow an exact yin-yang pattern: 2-4-6-8-1-3-5-7-9 repeating.
# This proves market percentages are governed by numerological law.
PERCENTAGE_VIBRATION_PATTERN = [2, 4, 6, 8, 1, 3, 5, 7, 9]

# 192-day multiples for long-range cycle timing (PDF 6, pages 5–8)
MASTER_TIME_FACTOR_MULTIPLES = [192, 384, 576, 768, 960, 1152, 1344,
                                 1536, 1728, 1920]

# Diatonic octave note positions as fractions of the 192-day cycle
# Do=0, Re=1/8, Mi=2/8, Fa=3/8, So=4/8, La=5/8, Ti=6/8, Do=7/8
# The Fa (3/8) and La (5/8) are "shock points" where trend may invert.
# (PDF 6, p.6: "Do, Fa, La vibration — deny, consolidate, shock price levels")
DIATONIC_FRACTIONS = {
    "Do": 0.0, "Re": 0.125, "Mi": 0.25, "Fa": 0.375,
    "So": 0.5, "La": 0.625, "Ti": 0.75, "Do2": 0.875,
}

# ---------------------------------------------------------------------------
# Constants from L.J. Jensen "Astro-Cycles and Speculative Markets" (1978)
# Book_1978_Gann_Astro Cycles And Speculative methods.pdf
# (Previously image-only, newly OCR-readable with 258K chars, 139 text pages)
# ---------------------------------------------------------------------------

# Uranus 84-year epoch cycle — North American economic epochs align with
# Uranus returning to 8-9° Gemini (Jensen, Section I, Chapter 5, pp.17-20)
# 1523 → 1607 → 1691 → 1775 → 1859 → 1943 → 2027
URANUS_CYCLE_YEARS = 84
URANUS_EPOCH_YEARS = [1523, 1607, 1691, 1775, 1859, 1943, 2027]

# Jupiter-Saturn conjunction cycle ~20 years (Jensen, pp.11-16)
# When in earth signs → political upheaval, credit problems
# Election years: 1840, 1860, 1880, 1900, 1920, 1940, 1960, 1980, 2000, 2020
JUPITER_SATURN_CYCLE_YEARS = 20

# Planetary aspect angles and their market effects (Jensen, pp.35-40, 68-69)
# Favorable (bullish/expansion): 60° sextile, 120° trine
# Unfavorable (bearish/compression): 90° square, 180° opposition
# Intermediate: 30° semi-sextile, 45° semi-square, 150° quincunx
BULLISH_ASPECTS = [60, 120]
BEARISH_ASPECTS = [90, 180]

# Moon's Node 18.6-year cycle (Jensen, pp.69-73)
# Square aspects mark major lows; interacts with 8-9° Gemini critical point
MOON_NODE_CYCLE_YEARS = 18.6

# Five-phase intermediate trend structure (Jensen, Section IV, pp.121-122)
# 3 directional waves + 2 corrective waves = complete intermediate trend
INTERMEDIATE_TREND_PHASES = 5

# Jensen's key timing principle: count from major high or low in calendar
# days/weeks/months for critical areas at harmonics of 90 (Jensen, p.108-110)
# "Always use every calendar day — forces operate 7 days a week, 24 hours"
JENSEN_CRITICAL_POINTS = [
    7.5, 11.25, 15, 22.5, 30, 45, 60, 67.5, 75, 90,
    105, 120, 135, 150, 165, 180, 225, 270, 315, 360
]

# Vectorial price-time angles for projection (Jensen, Section IV, pp.124-126)
# 45° is the average velocity of Dow Jones Industrials
# 60° is the associated price resistance factor
# Convergence of 45° from first low + 60° from second low = exhaustion point
JENSEN_VELOCITY_ANGLE = 45
JENSEN_RESISTANCE_ANGLE = 60

# Mercury cycles (harmonics of 90): 88, 44, 22 day cycles (Jensen, p.108)
MERCURY_CYCLE_DAYS = 88

# ---------------------------------------------------------------------------
# Constants from pdf24_ocrPdf.zip — 6 new PDFs (PDFs 22-27)
# ---------------------------------------------------------------------------

# Futia's Square of Nine angular formula constants (PDF 25 "Spiral Chart")
# A = MOD(180 × sqrt(P - 1) - 225, 360)
# Odd perfect squares fall on 315° axis, even squares on 45° axis.
FUTIA_OFFSET = 225  # degrees
FUTIA_SCALE = 180   # degrees per sqrt unit

# Sephariel's numerology: planet-number mappings (PDF 22 "The Numbers Book")
# Unit system: each digit 1-9 maps to a planetary ruler
# Positive numbers (winning/rising): 1, 3, 5, 7, 9
# Negative numbers (losing/falling): 2, 4, 6, 8
SEPHARIEL_POSITIVE_NUMBERS = [1, 3, 5, 7, 9]
SEPHARIEL_NEGATIVE_NUMBERS = [2, 4, 6, 8]

# Planetary sector rulership for stocks (PDF 22, pp.63-64)
# SUN: govt, gold; MOON: silver, property; MERCURY: transport, newspapers
# VENUS: banks, copper; MARS: iron/steel, engineering; JUPITER: shipping, insurance
# SATURN: coal, building materials; URANUS: electrical, scientific; NEPTUNE: oil
SEPHARIEL_SECTOR_NUMBERS = {
    1: "transport/newspapers/aluminium",
    2: "tea/coffee/cocoa/cereals/food",
    3: "diamonds/luxury/watches/perfumes",
    4: "chemicals/drugs/breweries/rubber",
    5: "shipping/overseas/tin/publishing",
    6: "copper/currency/tobacco/entertainment",
    7: "insurance/shipping/tin/paper",
    8: "government/mines/coal/building",
    9: "aircraft/musical/television/cables",
}

# Planetary harmonic conversion (PDF 23 "Planetary Harmonics")
# 1 degree longitude = price unit (scaled by market range)
# Harmonic divisions of the 360° wheel
HARMONIC_DIVISIONS = {
    1: 360,   # conjunction (full wheel)
    2: 180,   # opposition (half wheel)
    3: 120,   # trine (third)
    4: 90,    # square (quarter)
    6: 60,    # sextile (sixth)
    8: 45,    # semi-square (eighth)
}

# Musical-planet-number correspondence table (PDF 24 "Gann Wheel", p.7)
# Planet → (musical note, color, number, perfect square)
MUSICAL_PLANET_TABLE = {
    "Sun":     ("C", "Yellow", 4, 36),
    "Moon":    ("F", "Violet", 7, 81),
    "Mars":    ("G", "Red",    9, 25),
    "Mercury": ("E", "Orange", 5, 64),
    "Jupiter": ("B", "Blue",   3, 16),
    "Venus":   ("A", "Green",  6, 49),
    "Saturn":  ("D", "Indigo", 8, 9),
}

# Triangular (summation) numbers: n(n+1)/2 — natural S/R levels (PDF 26, p.21)
# These numbers appear as natural market turning points
TRIANGULAR_NUMBERS = [1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66, 78, 91,
                      105, 120, 136, 153, 171, 190, 210, 231, 253, 276,
                      300, 325, 351, 378, 406, 435, 465, 496, 528, 561]

# Saros eclipse cycle (PDF 27, pp.6-7)
# Complete eclipse repetition: 6585.33 days (18 years, 11.33 days)
# 360° × biblical 3.5 = 1260 days; complete Saros series = 1260 years
SAROS_ECLIPSE_DAYS = 6585.33
BIBLICAL_HALF_WEEK = 1260  # days (3.5 × 360)

# Range expansion threshold (PDF 27 "Short-Term Forecasting", Toby Crabel, p.11)
# When daily range > previous day range, 75%+ continuation bias next day
RANGE_EXPANSION_BIAS_PCT = 75


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
class HexagonResult:
    """Result of Gann Hexagon chart analysis."""
    seed_price: float
    circle_levels: Dict[int, float]  # circle_number -> price level
    angle_levels: Dict[int, float]   # angle_degrees -> price level


@dataclass
class RangePercentageResult:
    """Result of range percentage division analysis."""
    high: float
    low: float
    price_range: float
    support_levels: Dict[float, float]     # percentage -> price (below current)
    resistance_levels: Dict[float, float]  # percentage -> price (above current)
    extension_levels: Dict[float, float]   # percentage -> price (beyond range)


@dataclass
class SquareOfPriceResult:
    """Result of squaring price with time."""
    price: float
    is_high: bool
    base_date: str
    square_dates: Dict[float, str]  # percentage -> projected date


@dataclass
class MasterTimeResult:
    """Result from the Great Cycle / Master 144 Square analysis."""
    price: float
    great_cycle_days: int
    subdivision_dates: Dict[str, int]  # label -> days from reference
    key_resistance_points: List[float]


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


@dataclass
class CycleAlignmentResult:
    """Result from Shephard key cycle alignment check.

    Source: PDF 18, pp.85-86, 130 — "When multiple time counts cluster
    on the same date = cluster date = higher probability reversal."
    """
    reference_date: str
    target_date: str
    days_elapsed: int
    matching_cycles: List[Tuple[str, int, float]]  # (cycle_name, cycle_value, deviation_pct)
    cluster_strength: int  # number of matching cycles


@dataclass
class FatalNumberResult:
    """Result from Gann's Fatal Number (49) analysis.

    Source: PDF 18, pp.86, 100; PDF 12, p.6 — "49 = 7² is the 'Fatal
    Number' — it and its multiples mark major trend change points."
    """
    price: float
    nearby_fatal_levels: List[Tuple[int, float]]  # (multiple, price_level)
    time_fatal_levels: List[int]  # days that are multiples of 49


@dataclass
class MasterTimeFactorResult:
    """Result from the 192-day Master Time Factor analysis.

    Source: PDF 6 "144 Square", pages 5-8.  The author proves the 192
    calendar-day cycle is the interval after which "the wheel returns
    to its origin."  Robert Gordon discovered this on day 7680 of his
    life (= 40 × 192).  The 144 square fits within the 192-day octave:
    192 − 144 = 48 = 4 × 12.
    """
    reference_date: str
    current_date: str
    days_elapsed: int
    current_octave: int          # which 192-day octave we are in
    position_in_octave: int      # 0-191: position within current octave
    diatonic_note: str           # Do/Re/Mi/Fa/So/La/Ti
    is_shock_point: bool         # True at Fa (3/8) or La (5/8)
    next_octave_reset: str       # date of next 192-day boundary
    nearby_multiples: List[Tuple[int, int]]  # (multiple_N, days_away)


@dataclass
class ThirdTimeTestResult:
    """Result from the Third-Time Support/Resistance Test rule.

    Source: PDF 10 "Understanding Gann", page 2.
    "The third time against any support or resistance zone is the
    dangerous time."  Also: the 1st, 2nd, 3rd, 4th, 7th, 9th and
    12th squares of the low are significant.
    """
    price: float
    zone_price: float
    zone_kind: str           # "support" or "resistance"
    test_count: int          # how many times price has tested this zone
    is_third_test: bool      # True when test_count >= 3
    is_dangerous: bool       # True when test_count == 3


@dataclass
class MinorTrendTurnResult:
    """Result from the 3.5-day minor trend turn analysis.

    Source: PDF 10, page 2; PDF 16 "Shephard", page 50.
    "Watch 3.5 day i.e. the 3rd/4th day from the important top/bottom
    for change in minor trend.  14th day is most significant, 21 next."
    """
    pivot_date: str
    current_date: str
    days_from_pivot: int
    matching_day: Optional[int]     # e.g. 3, 4, 7, 14, 21, 42, 45, 49
    is_minor_turn_window: bool      # True if within ±1 day of a key count
    significance: str               # "high", "medium", "low"


@dataclass
class JensenCriticalResult:
    """Result from Jensen's critical-point time analysis.

    Source: L.J. Jensen "Astro-Cycles" (1978), Section III, pp.108-113.
    "Count from a major high or low in calendar days, weeks or months
    for critical areas in time at harmonics of 90."
    """
    reference_date: str
    current_date: str
    elapsed_days: int
    nearest_critical: float   # nearest critical point value
    distance_days: float      # how many days away from critical point
    is_critical_window: bool  # within ±2 days of a critical point
    cycle_label: str          # e.g. "90-day", "180-day", "360-day"


@dataclass
class FivePhaseTrendResult:
    """Result from Jensen's five-phase intermediate trend analysis.

    Source: Jensen Section IV, pp.121-122.
    "An intermediate trend usually has five phases: three in its
    direction and two corrective minor trends."
    """
    current_phase: int         # 1-5 (1,3,5 = directional; 2,4 = corrective)
    phase_label: str           # "directional_1", "corrective_1", etc.
    trend_direction: str       # "UP" or "DOWN"
    is_blowoff_phase: bool     # True if in phase 5 (most dangerous)
    swing_count: int           # total number of swings detected


@dataclass
class VectorialProjection:
    """Result from Jensen's vectorial price-time projection.

    Source: Jensen Section IV, pp.124-126.
    "A 45° angle from the first low and a 60° angle from the second
    low; the convergence estimates exhaustion in time and price."
    """
    projected_price: float
    projected_days: int        # calendar days from second low to convergence
    angle_45_origin: float     # price of first low
    angle_60_origin: float     # price of second low
    days_between_lows: int     # calendar days between first and second low


@dataclass
class FutiaAngularResult:
    """Result from Futia's SQ9 angular formula.

    Source: PDF 25 "Spiral Chart — Gann Mysteries"
    A = MOD(180 × √(P-1) - 225, 360)
    """
    price: float
    angular_position: float    # degrees on the SQ9 wheel
    nearest_cardinal: int      # nearest cardinal degree (0/90/180/270)
    distance_to_cardinal: float  # degrees to nearest cardinal
    is_near_cardinal: bool     # within 5° of a cardinal/ordinal axis


@dataclass
class RangeExpansionResult:
    """Result from range expansion analysis.

    Source: PDF 27 "Short-Term Market Forecasting" (Toby Crabel, p.11)
    75%+ continuation bias after range expansion.
    """
    is_expanding: bool
    expansion_ratio: float     # current range / previous range
    bias_direction: str        # "bullish" or "bearish" or "neutral"
    confidence: float          # 0.0-1.0


@dataclass
class TriangularNumberResult:
    """Result from triangular number proximity analysis.

    Source: PDF 26 "Advanced Group" (p.21)
    Triangular numbers = n(n+1)/2 act as natural S/R levels.
    """
    price: float
    nearest_triangular: int
    distance: float
    is_near_level: bool        # within 1% of a triangular number


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

        # Check if percentage vibrations follow the yin-yang pattern
        # (PDF 4 "Number Vibrations", pp.1-2: the pattern is 2-4-6-8-1-3-5-7-9)
        pattern_matches = 0
        for i, (_, vib) in enumerate(pct_vibrations):
            expected = PERCENTAGE_VIBRATION_PATTERN[i % len(PERCENTAGE_VIBRATION_PATTERN)]
            if vib == expected:
                pattern_matches += 1

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
    # 10. HEXAGON CHART LEVELS
    #     Source: "1931 Usage of Gann SQ9 Hexagon Chart"
    #     The Hexagon chart arranges numbers in concentric hexagonal
    #     rings. Each ring completion is a key support/resistance level.
    #     Gann: "The cube or hexagon proves exactly the law which works
    #     because of time and space in the market."
    # ------------------------------------------------------------------

    def hexagon_levels(self, seed_price: float) -> HexagonResult:
        """
        Calculate Hexagon chart price levels from a seed price.

        The Hexagon chart places numbers in concentric rings of 6.
        Circle completions: 1, 7, 19, 37, 61, 91, 127, 169, 217, 271, 331, 397.
        Key angle levels occur at 60°, 120°, 180°, 240°, 300°, 360° positions.

        Parameters
        ----------
        seed_price : float
            Reference price (major high or low).

        Returns
        -------
        HexagonResult
        """
        circle_levels: Dict[int, float] = {}
        for i, hex_val in enumerate(HEXAGON_CIRCLES):
            # Hexagon circles added/subtracted as absolute offsets from seed
            # For low-priced instruments (≤100), scale offsets proportionally
            # to preserve meaningful relative distances
            if seed_price > 100:
                circle_levels[i] = seed_price + hex_val
                circle_levels[-i] = max(0, seed_price - hex_val)
            else:
                circle_levels[i] = seed_price + hex_val * (seed_price / 100.0)
                circle_levels[-i] = max(0, seed_price - hex_val * (seed_price / 100.0))

        # Key angle levels on the hexagon (every 60°)
        angle_levels: Dict[int, float] = {}
        sqrt_p = math.sqrt(seed_price)
        for deg in [60, 120, 180, 240, 300, 360]:
            offset = deg / 180.0
            angle_levels[deg] = round((sqrt_p + offset) ** 2, 4)
            angle_levels[-deg] = round(max(0, (sqrt_p - offset) ** 2), 4)

        return HexagonResult(
            seed_price=seed_price,
            circle_levels=circle_levels,
            angle_levels=angle_levels,
        )

    # ------------------------------------------------------------------
    # 11. RANGE PERCENTAGE DIVISIONS
    #     Source: "Understanding Gann Price and Time Cycle",
    #             "Charles Shephard Gann Cycles Course"
    #     Divide any range by Gann percentages (1/8ths and 1/3rds)
    #     to find support, resistance, and extension levels.
    #     "The 50% level of price and time ranges was of great
    #     importance to Gann and is the first division applied."
    # ------------------------------------------------------------------

    def range_percentage_levels(
        self,
        high: float,
        low: float,
    ) -> RangePercentageResult:
        """
        Divide a price range by Gann's standard percentages.

        Gann percentages: 12.5%, 25%, 33.3%, 37.5%, 50%, 62.5%, 66.6%, 75%, 87.5%, 100%.
        Provides retracement levels (support/resistance within range) and
        extension levels (projections beyond range).

        Parameters
        ----------
        high : float
            The higher price of the range.
        low : float
            The lower price of the range.

        Returns
        -------
        RangePercentageResult
        """
        price_range = abs(high - low)

        # Retracement levels (from the high going down)
        support_levels: Dict[float, float] = {}
        for pct in GANN_PERCENTAGES:
            support_levels[pct] = round(high - price_range * pct, 4)

        # Resistance levels (from the low going up)
        resistance_levels: Dict[float, float] = {}
        for pct in GANN_PERCENTAGES:
            resistance_levels[pct] = round(low + price_range * pct, 4)

        # Extension levels (beyond the high)
        extension_levels: Dict[float, float] = {}
        for pct in GANN_PERCENTAGES:
            extension_levels[pct] = round(high + price_range * pct, 4)

        return RangePercentageResult(
            high=high,
            low=low,
            price_range=price_range,
            support_levels=support_levels,
            resistance_levels=resistance_levels,
            extension_levels=extension_levels,
        )

    # ------------------------------------------------------------------
    # 12. SQUARING PRICE WITH TIME
    #     Source: "Understanding Gann Price and Time Cycle",
    #             "Charles Shephard Gann Cycles Course",
    #             "Gann's Master Mathematical Formula" (Ferrera)
    #     Project a price value into time by dividing it by Gann
    #     percentages and converting to calendar days/weeks/months.
    #     "A high price of 100 would square out time 100 days
    #     forward from the date of the high."
    # ------------------------------------------------------------------

    def square_price_in_time(
        self,
        price: float,
        base_date: str,
        is_high: bool = True,
        date_fmt: str = "%Y-%m-%d",
    ) -> SquareOfPriceResult:
        """
        Project a price level into future time using Gann squaring.

        Takes a significant price (high or low), treats it as a number
        of time units (days), and projects forward at Gann percentage
        divisions: 12.5%, 25%, 33.3%, 37.5%, 50%, 62.5%, 66.6%, 75%,
        87.5%, and 100% of the price value.

        Parameters
        ----------
        price : float
            Significant high or low price to square.
        base_date : str
            Date of the high or low.
        is_high : bool
            True if price is a high, False if a low.
        date_fmt : str
            Date string format.

        Returns
        -------
        SquareOfPriceResult
        """
        dt = datetime.strptime(base_date, date_fmt)
        square_dates: Dict[float, str] = {}

        for pct in GANN_PERCENTAGES:
            days_forward = int(round(price * pct))
            projected = dt + timedelta(days=days_forward)
            label = f"{pct*100:.1f}%"
            square_dates[pct] = projected.strftime(date_fmt)

        return SquareOfPriceResult(
            price=price,
            is_high=is_high,
            base_date=base_date,
            square_dates=square_dates,
        )

    # ------------------------------------------------------------------
    # 13. MASTER 144 SQUARE / GREAT CYCLE
    #     Source: "1953 Mathematical Formula for Market Predictions"
    #     The Great Cycle = 144² = 20,736 time units.
    #     Its subdivisions (1/2, 1/4, 1/8, ..., 1/256) define key
    #     time resistance points. The Master Numbers are 3, 5, 7, 9, 12.
    #     "The square of 12 is always important... the square of 144
    #     is the GREAT SQUARE and works better than any other."
    # ------------------------------------------------------------------

    def master_144_square(
        self,
        price: float,
    ) -> MasterTimeResult:
        """
        Calculate key time and price resistance points from the Master
        144 Square (Great Cycle = 20,736).

        Subdivisions: 1/2, 1/4, 1/8, 1/16, 1/32, 1/64, 1/128, 1/256.
        Also calculates the strongest resistance points at fractions
        of 144: 1/4, 1/3, 3/8, 1/2, 5/8, 2/3, 3/4, 7/8.

        Parameters
        ----------
        price : float
            Reference price level.

        Returns
        -------
        MasterTimeResult
        """
        # Subdivisions of the Great Cycle in days
        subdivisions: Dict[str, int] = {}
        gc = GREAT_CYCLE
        for power in range(1, 9):  # 1/2 through 1/256
            divisor = 2 ** power
            label = f"1/{divisor}"
            subdivisions[label] = gc // divisor

        # Key resistance fractions of 144
        key_fractions = [
            (0.25, "1/4 of 144 = 36"),
            (1/3, "1/3 of 144 = 48"),
            (0.375, "3/8 of 144 = 54"),
            (0.5, "1/2 of 144 = 72"),
            (0.625, "5/8 of 144 = 90"),
            (2/3, "2/3 of 144 = 96"),
            (0.75, "3/4 of 144 = 108"),
            (0.875, "7/8 of 144 = 126"),
        ]

        key_resistance: List[float] = []
        sqrt_p = math.sqrt(price) if price > 0 else 0
        for frac, _label in key_fractions:
            # Each fraction of 144 maps to a sqrt-space offset:
            # full 144 = 360° = offset of 2.0 in sqrt-space (360/180)
            # so fraction f of 144 = offset of f * 2.0
            offset = frac * 2.0
            level = (sqrt_p + offset) ** 2
            key_resistance.append(round(level, 4))

        return MasterTimeResult(
            price=price,
            great_cycle_days=gc,
            subdivision_dates=subdivisions,
            key_resistance_points=key_resistance,
        )

    # ------------------------------------------------------------------
    # 14. PRICE-TIME VECTOR DISTANCE
    #     Source: "TS Vector 2" (Sergey Tarasov)
    #     In the price-time Universe, the distance between two turning
    #     points is calculated as: D = √((ΔPrice)² + (ΔTime)²)
    #     When this distance is a "good" angle (180, 360, 720...),
    #     it indicates harmonic resonance between price and time.
    #     "For a properly scaled chart, the distance between important
    #     turning points should form 'good' angles."
    # ------------------------------------------------------------------

    @staticmethod
    def pricetime_vector_distance(
        price1: float,
        price2: float,
        time_days1: int,
        time_days2: int,
        scale: float = 1.0,
    ) -> Dict[str, float]:
        """
        Calculate the price-time vector distance between two turning points.

        Uses the Euclidean metric in price-time space where both
        dimensions are treated equally (signature +,+).

        Parameters
        ----------
        price1 : float
            Price at the first turning point.
        price2 : float
            Price at the second turning point.
        time_days1 : int
            Solar degrees (or days) at first point.
        time_days2 : int
            Solar degrees (or days) at second point.
        scale : float
            Price-to-time scaling factor (default 1.0 = 1 point per degree).

        Returns
        -------
        Dict with distance, nearest_harmonic, deviation_pct.
        """
        delta_price = (price2 - price1) / scale
        delta_time = float(time_days2 - time_days1)
        distance = math.sqrt(delta_price ** 2 + delta_time ** 2)

        # Check nearest harmonic (multiple of 360)
        harmonics = [180, 360, 540, 720, 1080, 1440]
        nearest = min(harmonics, key=lambda h: abs(distance - h))
        deviation = abs(distance - nearest) / nearest * 100 if nearest else 0

        return {
            "distance": round(distance, 4),
            "delta_price": round(delta_price, 4),
            "delta_time": delta_time,
            "nearest_harmonic": nearest,
            "deviation_pct": round(deviation, 4),
            "is_harmonic": deviation < 5.0,  # within 5% = harmonic
        }

    # ------------------------------------------------------------------
    # 15. SEASONAL CARDINAL TIMING
    #     Source: "Gann's Master Mathematical Formula" (Ferrera),
    #             "Understanding Gann Price and Time Cycle",
    #             "1978 Astro-Cycles and Speculative Markets"
    #     Gann's year begins at March 21 (Vernal Equinox).
    #     Cardinal points: Mar 21, Jun 21, Sep 21, Dec 21.
    #     "Musical octave" nesting: squares within squares at
    #     solstice points and 45-degree sub-intervals.
    # ------------------------------------------------------------------

    @staticmethod
    def seasonal_cardinal_check(
        date_str: str,
        date_fmt: str = "%Y-%m-%d",
        tolerance_days: int = 3,
    ) -> Dict[str, object]:
        """
        Check if a date is near a Gann seasonal cardinal or octave point.

        Cardinal points: Equinoxes and Solstices (Mar 21, Jun 21, Sep 21, Dec 21).
        Octave points: Feb 5, May 6, Aug 5, Nov 5 (inner square nesting from
        the Master Mathematical Formula).

        Parameters
        ----------
        date_str : str
            Date to check.
        date_fmt : str
            Date string format.
        tolerance_days : int
            Number of days tolerance for matching.

        Returns
        -------
        Dict with is_cardinal, is_octave, nearest_cardinal, days_from_cardinal.
        """
        dt = datetime.strptime(date_str, date_fmt)
        year = dt.year

        # Build cardinal and octave dates for this year
        cardinal_list = []
        for m, d in CARDINAL_DATES:
            try:
                cardinal_list.append(datetime(year, m, d))
            except ValueError:
                pass

        octave_list = []
        for m, d in OCTAVE_DATES:
            try:
                octave_list.append(datetime(year, m, d))
            except ValueError:
                pass

        # Check cardinals
        is_cardinal = False
        nearest_cardinal = None
        min_cardinal_dist = 999
        for cd in cardinal_list:
            dist = abs((dt - cd).days)
            if dist < min_cardinal_dist:
                min_cardinal_dist = dist
                nearest_cardinal = cd.strftime(date_fmt)
            if dist <= tolerance_days:
                is_cardinal = True

        # Check octave points
        is_octave = False
        for od in octave_list:
            if abs((dt - od).days) <= tolerance_days:
                is_octave = True
                break

        return {
            "is_cardinal": is_cardinal,
            "is_octave": is_octave,
            "nearest_cardinal": nearest_cardinal,
            "days_from_cardinal": min_cardinal_dist,
        }

    # ------------------------------------------------------------------
    # 16. SWING CHART TREND ANALYSIS
    #     Source: "Charles Shephard Gann Cycles Course"
    #     Mechanical trading method using swing highs/lows.
    #     "Trade only with the trend. Higher swing tops and higher
    #     swing bottoms ARE an UPTREND."
    #     Entries at point C (reaction), stop below C.
    # ------------------------------------------------------------------

    @staticmethod
    def swing_trend(
        highs: List[float],
        lows: List[float],
    ) -> Dict[str, object]:
        """
        Determine trend using Gann's mechanical swing chart method.

        Identifies higher highs + higher lows (uptrend) or lower highs
        + lower lows (downtrend). Returns sections/waves count.

        Parameters
        ----------
        highs : List[float]
            Sequence of swing high prices (chronological).
        lows : List[float]
            Sequence of swing low prices (chronological).

        Returns
        -------
        Dict with trend, sections_count, last_swing_high, last_swing_low.
        """
        if len(highs) < 2 or len(lows) < 2:
            return {
                "trend": "NEUTRAL",
                "sections_count": 0,
                "last_swing_high": highs[-1] if highs else 0,
                "last_swing_low": lows[-1] if lows else 0,
            }

        # Count consecutive higher highs / higher lows
        hh_count = sum(
            1 for i in range(1, len(highs)) if highs[i] > highs[i - 1]
        )
        hl_count = sum(
            1 for i in range(1, len(lows)) if lows[i] > lows[i - 1]
        )
        lh_count = sum(
            1 for i in range(1, len(highs)) if highs[i] < highs[i - 1]
        )
        ll_count = sum(
            1 for i in range(1, len(lows)) if lows[i] < lows[i - 1]
        )

        n_highs = len(highs) - 1
        n_lows = len(lows) - 1
        n = min(n_highs, n_lows)
        trend = "NEUTRAL"
        if n > 0:
            if hh_count / n_highs > 0.5 and hl_count / n_lows > 0.5:
                trend = "UP"
            elif lh_count / n_highs > 0.5 and ll_count / n_lows > 0.5:
                trend = "DOWN"

        # Sections count (wave analysis)
        sections = 1
        if len(highs) >= 3:
            for i in range(2, min(len(highs), len(lows))):
                if trend == "UP" and highs[i] > highs[i - 1]:
                    sections += 1
                elif trend == "DOWN" and lows[i] < lows[i - 1]:
                    sections += 1

        return {
            "trend": trend,
            "sections_count": sections,
            "last_swing_high": highs[-1],
            "last_swing_low": lows[-1],
            "higher_highs": hh_count,
            "higher_lows": hl_count,
        }

    # ------------------------------------------------------------------
    # 17. MASTER TIME FACTOR PROJECTION
    #     Source: "Gann's Master Time Factor" (Flanagan)
    #     The Master Time Factor is the annual forecast based on major
    #     time cycles. The 60-year cycle is the master key—all seven
    #     visible planets return to the same positions.
    #     Also integrates the 20-year, 10-year, and 7-year cycles.
    # ------------------------------------------------------------------

    @staticmethod
    def master_time_cycles(
        reference_year: int,
    ) -> Dict[str, List[int]]:
        """
        Project major Gann time cycle years from a reference year.

        Cycles from Flanagan's Master Time Factor analysis:
        - 7-year cycle (sacred number, square of 7 = 49)
        - 10-year decennial pattern
        - 20-year Jupiter-Saturn conjunction cycle
        - 30-year (360 months, completing the "cube")
        - 60-year (all planets return, master cycle)

        Parameters
        ----------
        reference_year : int
            A significant year (e.g., year of a major high or low).

        Returns
        -------
        Dict mapping cycle name to list of projected years.
        """
        cycles = {
            "7_year": [reference_year + 7 * i for i in range(1, 11)],
            "10_year": [reference_year + 10 * i for i in range(1, 7)],
            "20_year": [reference_year + 20 * i for i in range(1, 4)],
            "30_year": [reference_year + 30 * i for i in range(1, 3)],
            "60_year": [reference_year + 60],
        }
        return cycles

    # ------------------------------------------------------------------
    # 18. SHEPHARD KEY CYCLE ALIGNMENT
    #     Source: PDF 18 "Charles Shephard Gann Cycles Course"
    #     Pages: 85-86, 130, 148
    #     WHY: The page-by-page study revealed that Shephard identifies
    #     specific cycle numbers (631, 668, 840, 1260, 1262, 1290, 1336)
    #     as THE most critical for major reversals. When multiple cycles
    #     cluster on the same date, reversal probability is highest.
    #     These were completely missing from the algorithm.
    # ------------------------------------------------------------------

    @staticmethod
    def shephard_cycle_alignment(
        reference_date: str,
        target_date: str,
        date_fmt: str = "%Y-%m-%d",
        tolerance_pct: float = 2.0,
    ) -> CycleAlignmentResult:
        """
        Check if the elapsed time between two dates aligns with
        Shephard's key cycle numbers.

        From PDF 18, p.130: "The main or weekly high and low points can
        be determined by the important cycle numbers: 631, 668, 840,
        1262, 1290, 1336 days and degrees."

        From PDF 18, p.85: "1260 = a time, times, and half a time
        (360 + 720 + 180). 1290 = 1260 + leap month. 1336 = 3.6525 ×
        365.25."

        Parameters
        ----------
        reference_date : str
            Date of a known pivot (high or low).
        target_date : str
            Date to check for cycle alignment.
        date_fmt : str
            Date format string.
        tolerance_pct : float
            Percentage tolerance for matching (default 2%).

        Returns
        -------
        CycleAlignmentResult
        """
        dt_ref = datetime.strptime(reference_date, date_fmt)
        dt_tgt = datetime.strptime(target_date, date_fmt)
        days = abs((dt_tgt - dt_ref).days)

        # Check all cycle numbers including planetary and biblical
        all_cycles = {
            "Shephard_631 (half of 1262)": 631,
            "Shephard_668 (half of 1336)": 668,
            "Shephard_840 (1/3 of 2520)": 840,
            "Biblical_1260 (time+times+half)": 1260,
            "Shephard_1262 (1260 in days)": 1262,
            "Biblical_1290 (1260+30 leap)": 1290,
            "Shephard_1336 (Earth cycle²)": 1336,
            "7yr_2556 (7-year cycle days)": SEVEN_YEAR_CYCLE_DAYS,
            "Mars_687 (orbit cycle)": MARS_CYCLE,
            "Venus_224 (synodic cycle)": VENUS_CYCLE,
            "Week_168 (hours in week)": WEEK_HOURS,
            "Wheel_2520 (360 weeks)": WHEEL_CYCLE,
            "Fatal_49 (7² fatal num)": FATAL_NUMBER,
            "Fatal_343 (7 × 49)": 343,
            "Fatal_490 (10 × 49)": 490,
        }

        matching: List[Tuple[str, int, float]] = []
        for name, cycle_val in all_cycles.items():
            if cycle_val == 0:
                continue
            # Check direct match and multiples up to 5×
            for mult in range(1, 6):
                expected = cycle_val * mult
                if expected > 0:
                    deviation = abs(days - expected) / expected * 100
                    if deviation <= tolerance_pct:
                        label = f"{name} ×{mult}" if mult > 1 else name
                        matching.append((label, expected, round(deviation, 2)))

        return CycleAlignmentResult(
            reference_date=reference_date,
            target_date=target_date,
            days_elapsed=days,
            matching_cycles=matching,
            cluster_strength=len(matching),
        )

    # ------------------------------------------------------------------
    # 19. GANN'S FATAL NUMBER ANALYSIS
    #     Source: PDF 18, pp.86, 100; PDF 12, p.6
    #     WHY: The page-by-page study of Shephard (p.86) revealed that
    #     "49 was often quoted by WD Gann as the Fatal Number." The
    #     number 49 and its multiples (98, 147, 196, 245, 294, 343,
    #     392, 441, 490) appear repeatedly in time and price ranges at
    #     major reversals. This was NOT previously implemented.
    # ------------------------------------------------------------------

    @staticmethod
    def fatal_number_analysis(
        price: float,
        days_from_pivot: int = 0,
    ) -> FatalNumberResult:
        """
        Analyze a price and time for proximity to Gann's Fatal Number.

        From PDF 18, p.86: "343 + 343 years. 343 is 7 times 49, the
        number 49 was often quoted by WD Gann as the Fatal Number."

        From PDF 18, p.100: "147 is 3 × 49 – Gann's fatal number."

        From PDF 12, p.6: "The square of 49 = 2401. The square of 7
        (49) is very important for trend changes."

        Parameters
        ----------
        price : float
            Current price level to check.
        days_from_pivot : int
            Days elapsed from last significant pivot.

        Returns
        -------
        FatalNumberResult
        """
        # Find nearby fatal price levels
        nearby_levels: List[Tuple[int, float]] = []
        for mult in FATAL_MULTIPLES:
            # Check price proximity to multiples of 49
            if price > 0:
                ratio = price / mult
                nearest_mult = round(ratio)
                if nearest_mult > 0:
                    level = mult * nearest_mult
                    deviation_pct = abs(price - level) / price * 100
                    if deviation_pct < 3.0:  # Within 3%
                        nearby_levels.append((mult, level))

        # Find time-based fatal alignments
        time_levels: List[int] = []
        for mult in FATAL_MULTIPLES:
            if days_from_pivot > 0 and mult > 0:
                deviation = abs(days_from_pivot - mult) / mult * 100
                if deviation < 5.0:
                    time_levels.append(mult)
            # Also check if days is an exact multiple
            if days_from_pivot > 0 and days_from_pivot % FATAL_NUMBER == 0:
                if days_from_pivot not in time_levels:
                    time_levels.append(days_from_pivot)

        return FatalNumberResult(
            price=price,
            nearby_fatal_levels=nearby_levels,
            time_fatal_levels=time_levels,
        )

    # ------------------------------------------------------------------
    # 20. PLANETARY CYCLE TIME WINDOWS
    #     Source: PDF 18, pp.67, 71, 75, 108; PDF 19, pp.46-97
    #     WHY: The page-by-page study revealed that specific planetary
    #     cycles (Mars=687, Venus=224, Week=168) and their Gann
    #     percentage divisions create precise time windows for reversals.
    #     "168 hours in our week... consequently 168 can symbolically
    #     appear in any other time period" (Shephard, p.71).
    #     This calculation was completely absent from the algorithm.
    # ------------------------------------------------------------------

    @staticmethod
    def planetary_cycle_windows(
        reference_date: str,
        date_fmt: str = "%Y-%m-%d",
    ) -> Dict[str, List[Tuple[str, str]]]:
        """
        Project future reversal dates based on planetary cycle
        divisions from a reference pivot date.

        From PDF 18, p.71: "The 7 year cycle... is exactly 2556 days.
        Also 2520 days or 360 weeks. The 168 can appear as 168 minutes,
        days, degrees, weeks, months or years."

        From PDF 18, p.75: "Divisions of 168 to be monitored are: 21,
        42, 63, 84, 105, 126 and 147, as well as its multiples."

        From PDF 18, p.108: "919 days or 133.3% of 687 [Mars]."

        Parameters
        ----------
        reference_date : str
            Date of a known pivot point.
        date_fmt : str
            Date format string.

        Returns
        -------
        Dict mapping cycle name to list of (label, projected_date).
        """
        dt = datetime.strptime(reference_date, date_fmt)

        cycles_config = {
            "Mars (687 days)": MARS_CYCLE,
            "Venus (224 days)": VENUS_CYCLE,
            "Week Hours (168 days)": WEEK_HOURS,
            "Wheel (2520 days)": WHEEL_CYCLE,
        }

        result: Dict[str, List[Tuple[str, str]]] = {}

        for cycle_name, base_days in cycles_config.items():
            windows: List[Tuple[str, str]] = []
            for pct in GANN_PERCENTAGES:
                days_forward = int(round(base_days * pct))
                projected = dt + timedelta(days=days_forward)
                label = f"{pct*100:.1f}% = {days_forward}d"
                windows.append((label, projected.strftime(date_fmt)))

            # Add the 133.3% and higher extensions (PDF 18, p.108)
            for ext_pct in [1.25, 1.333, 1.5, 1.666, 2.0, 3.0]:
                days_forward = int(round(base_days * ext_pct))
                projected = dt + timedelta(days=days_forward)
                label = f"{ext_pct*100:.1f}% = {days_forward}d"
                windows.append((label, projected.strftime(date_fmt)))

            result[cycle_name] = windows

        return result

    # ------------------------------------------------------------------
    # 21. CUMULATIVE RANGE ANALYSIS
    #     Source: PDF 18, pp.96, 110, 135
    #     WHY: Shephard demonstrates that when you ADD consecutive price
    #     ranges together, the cumulative total often equals a key cycle
    #     number. Example (p.110): "186 + 58 + 93 = 337 which is 2×168
    #     and 50% of 687." This provides a hidden confirmation signal
    #     that was not in the algorithm.
    # ------------------------------------------------------------------

    @staticmethod
    def cumulative_range_check(
        price_ranges: List[float],
        tolerance_pct: float = 2.0,
    ) -> List[Tuple[float, str, float]]:
        """
        Check if cumulative sums of consecutive price ranges match
        key Gann cycle numbers.

        From PDF 18, p.110: "cumulative prices (186+58+93=337 which
        is 2×168 and 50% of 687)."

        From PDF 18, p.96: "627 + 210 + 421 = 1258, almost 1260."

        Parameters
        ----------
        price_ranges : List[float]
            Consecutive price ranges (absolute values of moves).
        tolerance_pct : float
            Percentage tolerance for matching.

        Returns
        -------
        List of (cumulative_sum, matched_cycle_description, deviation_pct).
        """
        # Key cycle numbers to check against
        key_numbers = (
            SHEPHARD_KEY_CYCLES + BIBLICAL_NUMBERS +
            [MARS_CYCLE, VENUS_CYCLE, WEEK_HOURS, WHEEL_CYCLE, FATAL_NUMBER] +
            list(FATAL_MULTIPLES) + GANN_NUMBERS +
            [n * 2 for n in [168, 224, 687]] +  # 2× multiples
            [n * 3 for n in [168, 224]] +  # 3× multiples
            [n * 7 for n in [168, 49]]  # 7× multiples (PDF 18, p.73)
        )

        results: List[Tuple[float, str, float]] = []
        n = len(price_ranges)

        # Check all consecutive sub-sequences
        for start in range(n):
            cumsum = 0.0
            for end in range(start, n):
                cumsum += abs(price_ranges[end])

                # Check against all key numbers
                for key_num in key_numbers:
                    if key_num <= 0:
                        continue
                    # Also check Gann percentage multiples of key numbers
                    for pct in [0.25, 0.333, 0.5, 0.666, 0.75, 1.0, 1.25, 1.333, 1.5, 2.0]:
                        target = key_num * pct
                        if target < 5:
                            continue
                        deviation = abs(cumsum - target) / target * 100
                        if deviation <= tolerance_pct:
                            desc = (
                                f"Ranges[{start}:{end+1}] sum={cumsum:.1f} "
                                f"≈ {pct*100:.1f}% of {key_num}"
                            )
                            results.append((cumsum, desc, round(deviation, 2)))

        # Deduplicate and sort by deviation
        seen: set = set()
        unique_results: List[Tuple[float, str, float]] = []
        for item in sorted(results, key=lambda x: x[2]):
            # Use cumulative sum and the full description for dedup
            key = (round(item[0], 1), item[1])
            if key not in seen:
                seen.add(key)
                unique_results.append(item)

        return unique_results[:20]  # Top 20 matches

    # ------------------------------------------------------------------
    # 22. MASTER TIME FACTOR (192 Calendar Days)
    #     Source: PDF 6 "144 Square" (pages 5-8)
    #     The 192-day cycle is the "time factor" governing when the
    #     wheel resets.  24 diatonic octaves of 8 days = 192 CD.
    #     Key insight: the Fa (3/8 = day 72) and La (5/8 = day 120)
    #     positions within each 192-day octave are "shock points"
    #     where price may deny/consolidate/invert.
    # ------------------------------------------------------------------

    @staticmethod
    def master_time_factor_analysis(
        reference_date: str,
        current_date: str,
    ) -> MasterTimeFactorResult:
        """Check position within the 192-day Master Time Factor cycle.

        Parameters
        ----------
        reference_date : str
            Reference pivot date in ``YYYY-MM-DD`` format.
        current_date : str
            Current date in ``YYYY-MM-DD`` format.

        Returns
        -------
        MasterTimeFactorResult
        """
        ref = datetime.strptime(reference_date, "%Y-%m-%d")
        cur = datetime.strptime(current_date, "%Y-%m-%d")
        elapsed = (cur - ref).days

        if elapsed < 0:
            elapsed = abs(elapsed)

        octave_num = elapsed // MASTER_TIME_FACTOR
        position = elapsed % MASTER_TIME_FACTOR

        # Determine diatonic note
        frac = position / MASTER_TIME_FACTOR if MASTER_TIME_FACTOR else 0.0
        # Clamp frac so that position == MASTER_TIME_FACTOR maps back to "Do"
        if frac >= 1.0:
            frac = 0.0
        note = "Do"
        for n, f in DIATONIC_FRACTIONS.items():
            nxt = f + 0.125
            if f <= frac < nxt:
                note = n
                break

        is_shock = note in ("Fa", "La")

        # Next octave reset
        days_to_next = MASTER_TIME_FACTOR - position
        next_reset = (cur + timedelta(days=days_to_next)).strftime("%Y-%m-%d")

        # Find nearby 192-multiples (within ±5 days)
        nearby: List[Tuple[int, int]] = []
        for mult in MASTER_TIME_FACTOR_MULTIPLES:
            dist = abs(elapsed - mult)
            if dist <= 5:
                nearby.append((mult // MASTER_TIME_FACTOR, dist))

        return MasterTimeFactorResult(
            reference_date=reference_date,
            current_date=current_date,
            days_elapsed=elapsed,
            current_octave=octave_num,
            position_in_octave=position,
            diatonic_note=note,
            is_shock_point=is_shock,
            next_octave_reset=next_reset,
            nearby_multiples=nearby,
        )

    # ------------------------------------------------------------------
    # 23. THIRD-TIME TEST RULE
    #     Source: PDF 10 "Understanding Gann Price & Time" (page 2)
    #     "The third time against any support or resistance zone is
    #     the dangerous time."
    #     Implementation: count how many times in price history the
    #     price has touched a particular S/R zone (within tolerance).
    # ------------------------------------------------------------------

    @staticmethod
    def third_time_test(
        prices_history: List[float],
        zone_price: float,
        tolerance_pct: float = 0.5,
        zone_kind: str = "support",
    ) -> ThirdTimeTestResult:
        """Count how many times price has tested a zone and flag 3rd test.

        Parameters
        ----------
        prices_history : List[float]
            Recent price series (lows for support, highs for resistance).
        zone_price : float
            The support or resistance level to test against.
        tolerance_pct : float
            Percentage tolerance around the zone (default 0.5%).
        zone_kind : str
            ``"support"`` or ``"resistance"``.

        Returns
        -------
        ThirdTimeTestResult
        """
        if zone_price <= 0:
            return ThirdTimeTestResult(
                price=prices_history[-1] if prices_history else 0.0,
                zone_price=zone_price,
                zone_kind=zone_kind,
                test_count=0,
                is_third_test=False,
                is_dangerous=False,
            )

        tol = zone_price * tolerance_pct / 100.0
        test_count = 0
        # Avoid counting consecutive touches as separate tests
        was_in_zone = False
        for p in prices_history:
            in_zone = abs(p - zone_price) <= tol
            if in_zone and not was_in_zone:
                test_count += 1
            was_in_zone = in_zone

        return ThirdTimeTestResult(
            price=prices_history[-1] if prices_history else 0.0,
            zone_price=zone_price,
            zone_kind=zone_kind,
            test_count=test_count,
            is_third_test=test_count >= 3,
            is_dangerous=test_count == 3,
        )

    # ------------------------------------------------------------------
    # 24. MINOR TREND TURN ANALYSIS
    #     Source: PDF 10 "Understanding Gann" (page 2), PDF 16 (page 50)
    #     Watch the 3rd/4th day from an important top/bottom for change
    #     in minor trend.  14th day is most significant, 21 the next.
    #     Also: 7, 42, 45, 49 are key counts.
    # ------------------------------------------------------------------

    @staticmethod
    def minor_trend_turn(
        pivot_date: str,
        current_date: str,
    ) -> MinorTrendTurnResult:
        """Check if current date falls on a minor trend turn day count.

        Parameters
        ----------
        pivot_date : str
            Date of the important high/low in ``YYYY-MM-DD`` format.
        current_date : str
            Current date in ``YYYY-MM-DD`` format.

        Returns
        -------
        MinorTrendTurnResult
        """
        piv = datetime.strptime(pivot_date, "%Y-%m-%d")
        cur = datetime.strptime(current_date, "%Y-%m-%d")
        days = abs((cur - piv).days)

        matching: Optional[int] = None
        is_window = False
        for d in MINOR_TREND_DAYS:
            if abs(days - d) <= 1:
                matching = d
                is_window = True
                break

        sig = "low"
        if matching in (14, 21):
            sig = "high"
        elif matching in (3, 4, 7, 49):
            sig = "medium"

        return MinorTrendTurnResult(
            pivot_date=pivot_date,
            current_date=current_date,
            days_from_pivot=days,
            matching_day=matching,
            is_minor_turn_window=is_window,
            significance=sig,
        )

    # ------------------------------------------------------------------
    # Jensen's Critical-Point Time Analysis
    #   Source: L.J. Jensen "Astro-Cycles" (1978), Section III, pp.108-113
    #   "In measuring time count from a major hi or low in calendar days,
    #   weeks or months for critical areas in time."
    #   Harmonics of 90: 22.5, 45, 67.5, 90, 105, 120, 135, 180, 270, 360
    # ------------------------------------------------------------------

    def jensen_critical_points(
        self,
        reference_date: str,
        current_date: str,
    ) -> JensenCriticalResult:
        """Check if elapsed calendar days from a reference date hit a Jensen
        critical point — a harmonic of 90° time division.

        Jensen (p.108): "The 90° angle is the symbol of the meeting of force
        and resistance... all harmonical points of 90, or from 0 to 360,
        represent days, weeks or months of resistance from a major high or low.
        This coincides with the 88, 44 and 22 day cycles of Mercury."

        Parameters
        ----------
        reference_date, current_date : str  (``YYYY-MM-DD``)
        """
        ref_dt = datetime.strptime(reference_date, "%Y-%m-%d")
        cur_dt = datetime.strptime(current_date, "%Y-%m-%d")
        elapsed = (cur_dt - ref_dt).days

        best_dist = float("inf")
        best_cp = 0.0
        for cp in JENSEN_CRITICAL_POINTS:
            # Check raw and multiples of 360 (full circle repetitions).
            # We need enough multiples to cover elapsed days; dividing by
            # 300 (slightly less than 360) gives a safe upper bound for
            # the number of full-circle repetitions to check.
            full_circles = max(1, elapsed // 300) + 2
            for mult in range(0, full_circles):
                val = cp + mult * 360
                dist = abs(elapsed - val)
                if dist < best_dist:
                    best_dist = dist
                    best_cp = val

        is_window = best_dist <= 2

        if best_cp <= 0:
            label = "origin"
        elif best_cp % 360 == 0:
            label = f"{int(best_cp)}d-full-cycle"
        elif best_cp % 90 == 0:
            label = f"{int(best_cp)}d-cardinal"
        elif best_cp % 45 == 0:
            label = f"{int(best_cp)}d-diagonal"
        else:
            label = f"{best_cp}d-harmonic"

        return JensenCriticalResult(
            reference_date=reference_date,
            current_date=current_date,
            elapsed_days=elapsed,
            nearest_critical=best_cp,
            distance_days=best_dist,
            is_critical_window=is_window,
            cycle_label=label,
        )

    # ------------------------------------------------------------------
    # Jensen's Five-Phase Intermediate Trend
    #   Source: Jensen Section IV, pp.121-122
    #   "An intermediate trend usually has five phases, three in its
    #   direction and two corrective minor trends."
    # ------------------------------------------------------------------

    def five_phase_trend(
        self,
        prices: List[float],
    ) -> FivePhaseTrendResult:
        """Classify the current position within Jensen's five-phase
        intermediate trend model.

        Jensen (pp.121-122): The intermediate upward trend has:
        Phase 1 — initial upward move (small)
        Phase 2 — first corrective minor downtrend
        Phase 3 — second upswing
        Phase 4 — second corrective setback
        Phase 5 — third upswing / blowoff (largest and longest)

        "It is almost axiomatic that the third phase of an intermediate
        uptrend is the largest and longest because by that time people
        feel the future profit..."

        Parameters
        ----------
        prices : List[float]
            Recent price history (at least 20 values recommended).
        """
        n = len(prices)
        if n < 10:
            return FivePhaseTrendResult(
                current_phase=1,
                phase_label="insufficient_data",
                trend_direction="NEUTRAL",
                is_blowoff_phase=False,
                swing_count=0,
            )

        # Detect swing highs and lows (simple 3-bar pivot method)
        # Each swing is (index, type "H"/"L", price)
        swings: List[Tuple[int, str, float]] = []
        for i in range(1, n - 1):
            if prices[i] > prices[i - 1] and prices[i] > prices[i + 1]:
                swings.append((i, "H", prices[i]))
            elif prices[i] < prices[i - 1] and prices[i] < prices[i + 1]:
                swings.append((i, "L", prices[i]))

        # Determine overall direction by first and last significant prices
        direction = "UP" if prices[-1] > prices[0] else "DOWN"

        # Count directional and corrective waves
        # A directional wave moves with the trend; corrective moves against
        wave_count = 0
        prev_type = None
        for _idx, stype, _price in swings:
            if stype != prev_type:
                wave_count += 1
                prev_type = stype

        # Map wave count to phase
        phase = min(wave_count, INTERMEDIATE_TREND_PHASES)
        if phase == 0:
            phase = 1

        phase_labels = {
            1: "directional_1",
            2: "corrective_1",
            3: "directional_2",
            4: "corrective_2",
            5: "directional_3_blowoff",
        }

        return FivePhaseTrendResult(
            current_phase=phase,
            phase_label=phase_labels.get(phase, f"phase_{phase}"),
            trend_direction=direction,
            is_blowoff_phase=(phase >= 5),
            swing_count=len(swings),
        )

    # ------------------------------------------------------------------
    # Jensen's Vectorial Price-Time Projection
    #   Source: Jensen Section IV, pp.124-126
    #   "A 45° angle on the low close day and a lesser angle [60°] on the
    #   first preceding low close day; the crossing will estimate
    #   exhaustion in time and price."
    # ------------------------------------------------------------------

    @staticmethod
    def vectorial_projection(
        first_low_price: float,
        second_low_price: float,
        days_between: int,
    ) -> VectorialProjection:
        """Project a price-time exhaustion point using Jensen's dual-angle
        convergence method.

        Jensen (pp.125-126): From the first (higher) preceding low, project
        a 45° angle upward. From the second (lower) low, project a 60° angle
        upward. Where they converge is the estimated exhaustion (potential
        top) in both time and price.

        The 45° angle rises at 1 price-unit per time-unit (tan(45°) = 1).
        The 60° angle rises at tan(60°) ≈ 1.732 price-units per time-unit.

        Parameters
        ----------
        first_low_price : float
            Price at the first (earlier, usually higher) low.
        second_low_price : float
            Price at the second (later, usually lower) low.
        days_between : int
            Calendar days between the two lows.
        """
        # 45° line from first low: P = first_low + t (where t starts at 0)
        # 60° line from second low: P = second_low + tan(60°) * (t - days_between)
        # At convergence: first_low + t = second_low + 1.7321 * (t - days_between)
        tan60 = math.tan(math.radians(JENSEN_RESISTANCE_ANGLE))  # ≈ 1.7321

        denominator = tan60 - 1.0
        if abs(denominator) < 1e-10:
            # Degenerate case — parallel lines
            return VectorialProjection(
                projected_price=second_low_price,
                projected_days=0,
                angle_45_origin=first_low_price,
                angle_60_origin=second_low_price,
                days_between_lows=days_between,
            )

        # t measured from first_low date
        t_converge = (second_low_price - first_low_price
                      + tan60 * days_between) / denominator
        projected_price = first_low_price + t_converge
        # Days from second low
        projected_days_from_second = max(0, int(t_converge - days_between))

        return VectorialProjection(
            projected_price=round(projected_price, 2),
            projected_days=projected_days_from_second,
            angle_45_origin=first_low_price,
            angle_60_origin=second_low_price,
            days_between_lows=days_between,
        )

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
    # NEW METHODS from pdf24_ocrPdf.zip (PDFs 22-27)
    # ------------------------------------------------------------------

    @staticmethod
    def futia_angular_position(price: float) -> FutiaAngularResult:
        """
        Calculate the angular position of a price on the Square of Nine
        using Futia's universal formula.

        Source: PDF 25 "Spiral Chart — Gann Mysteries"
        Formula: A = MOD(180 × √(P-1) - 225, 360)

        The SQ9 spiral chart maps integers onto a square spiral. Futia's
        formula converts any number to its angular position on this spiral.
        Key levels occur at cardinal (0/90/180/270) and ordinal
        (45/135/225/315) axes.

        Why implemented: This gives a precise mathematical way to determine
        where any price sits on the Gann wheel, enabling angular distance
        calculations between prices and identification of prices that lie
        on critical axes.
        """
        if price <= 1:
            return FutiaAngularResult(
                price=price, angular_position=0.0,
                nearest_cardinal=0, distance_to_cardinal=0.0,
                is_near_cardinal=True,
            )

        angle = (FUTIA_SCALE * math.sqrt(price - 1) - FUTIA_OFFSET) % 360

        cardinals = [0, 45, 90, 135, 180, 225, 270, 315, 360]
        nearest = min(cardinals, key=lambda c: min(
            abs(angle - c), 360 - abs(angle - c)
        ))
        if nearest == 360:
            nearest = 0
        dist = min(abs(angle - nearest), 360 - abs(angle - nearest))

        return FutiaAngularResult(
            price=price,
            angular_position=round(angle, 2),
            nearest_cardinal=nearest,
            distance_to_cardinal=round(dist, 2),
            is_near_cardinal=dist <= 5.0,
        )

    @staticmethod
    def range_expansion_check(
        highs: List[float],
        lows: List[float],
        closes: List[float],
    ) -> RangeExpansionResult:
        """
        Check for range expansion — a wider daily range than the prior day.

        Source: PDF 27 "Short-Term Market Forecasting" (Toby Crabel, pp.11-12)
        "Over 75% of the time, the price pattern showed a percentage
        profitability favoring the bias of the range expansion."

        When today's range exceeds yesterday's range, the market is showing
        increased energy. The direction of that expansion (whether close is
        higher or lower) predicts next day continuation with 75%+ accuracy.

        Why implemented: Range expansion is one of the simplest and most
        statistically robust short-term signals. It detects the moment
        when volatility expands, which Gann associated with the start
        of meaningful price moves.
        """
        if len(highs) < 2 or len(lows) < 2 or len(closes) < 2:
            return RangeExpansionResult(
                is_expanding=False, expansion_ratio=1.0,
                bias_direction="neutral", confidence=0.0,
            )

        today_range = highs[-1] - lows[-1]
        yesterday_range = highs[-2] - lows[-2]

        if yesterday_range <= 0:
            return RangeExpansionResult(
                is_expanding=False, expansion_ratio=1.0,
                bias_direction="neutral", confidence=0.0,
            )

        ratio = today_range / yesterday_range
        is_expanding = ratio > 1.0

        if is_expanding:
            direction = "bullish" if closes[-1] > closes[-2] else "bearish"
            conf = min(1.0, 0.5 + (ratio - 1.0) * 0.25)
        else:
            direction = "neutral"
            conf = 0.0

        return RangeExpansionResult(
            is_expanding=is_expanding,
            expansion_ratio=round(ratio, 4),
            bias_direction=direction,
            confidence=round(conf, 4),
        )

    @staticmethod
    def triangular_number_proximity(price: float) -> TriangularNumberResult:
        """
        Check if a price is near a triangular (summation) number.

        Source: PDF 26 "Advanced Group" (p.21)
        "561 is the SUMMATION of all numbers from 1 to 33.
        The formula is n/2 × (n+1)"

        Triangular numbers (1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66, ...)
        are natural S/R levels because they represent the sum of all integers
        from 1 to n — a concept tied to the Square of Nine's accumulation
        of complete "rings" around the center.

        Why implemented: These numbers appear as natural market support and
        resistance levels. When price approaches a triangular number, the
        market often stalls, reverses, or consolidates.
        """
        # Find the nearest triangular number by solving n(n+1)/2 = price
        # n ≈ (-1 + sqrt(1 + 8*price)) / 2
        if price <= 0:
            return TriangularNumberResult(
                price=price, nearest_triangular=1,
                distance=abs(price - 1), is_near_level=False,
            )

        n_approx = (-1 + math.sqrt(1 + 8 * abs(price))) / 2
        n_low = max(1, int(n_approx))
        candidates = [
            n_low * (n_low + 1) // 2,
            (n_low + 1) * (n_low + 2) // 2,
        ]
        if n_low > 1:
            candidates.append((n_low - 1) * n_low // 2)

        nearest = min(candidates, key=lambda t: abs(price - t))
        dist = abs(price - nearest)
        threshold = max(abs(price) * 0.01, 1.0)  # 1% of price, floor of 1.0 unit

        return TriangularNumberResult(
            price=price,
            nearest_triangular=nearest,
            distance=round(dist, 2),
            is_near_level=dist <= threshold,
        )

    @staticmethod
    def planetary_harmonic_price(
        degree_longitude: float,
        price_scale: float = 1.0,
    ) -> Dict[str, float]:
        """
        Convert a planetary longitude to price levels at multiple harmonics.

        Source: PDF 23 "Using Planetary Harmonics" (Thomas Long, pp.1-3)
        "I do this simply by converting planetary positions into price.
        A conjunction between two planets is the most powerful geometric
        relationship. Conjunctions are responsible for a majority of major
        market reversals."

        The conversion is: price = degree × scale_factor
        Then harmonic levels are generated at 360° multiples above and below.
        Mirror lines are computed as 360 - degree for downtrend tracking.

        Why implemented: This provides the foundational calculation for
        converting planetary astronomy data into actionable price levels.
        When price touches a planetary harmonic line, it signals potential
        reversal — especially at conjunction points where multiple planet
        lines intersect.
        """
        base = (degree_longitude % 360) * price_scale
        mirror = ((360 - degree_longitude % 360) % 360) * price_scale

        levels: Dict[str, float] = {
            "base": round(base, 2),
            "mirror": round(mirror, 2),
        }

        # Generate harmonic levels at each division
        for harmonic, division in HARMONIC_DIVISIONS.items():
            h_degree = degree_longitude % division
            h_price = h_degree * price_scale
            levels[f"harmonic_{harmonic}"] = round(h_price, 2)

        # Multiple wheels of 360
        for wheel in range(1, 4):
            levels[f"wheel_{wheel}"] = round(base + 360 * wheel * price_scale, 2)

        return levels

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
        current_date: Optional[str] = None,
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
        current_date : Optional[str]
            Current date in ``YYYY-MM-DD`` format for time-based analysis.
            If omitted, time-cycle checks are skipped to avoid non-determinism.

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

        # Check range percentage levels (PDFs 8, 11, 15)
        range_pct = self.range_percentage_levels(high, low)
        for pct, level in range_pct.support_levels.items():
            if abs(level - current_price) / current_price < 0.003:
                confidence += 0.05
                reasons.append(
                    f"Price near Gann {pct*100:.1f}% support level ({level:.2f})"
                )
                break

        # Check Hexagon chart levels (PDF 8)
        hex_levels = self.hexagon_levels(low)
        for deg, level in hex_levels.angle_levels.items():
            if deg > 0 and abs(level - current_price) / current_price < 0.005:
                confidence += 0.05
                reasons.append(
                    f"Price near Hexagon {deg}° level ({level:.2f})"
                )
                break

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

        # Check Fatal Number proximity (PDF 18 pp.86,100 — page-by-page finding)
        fatal = self.fatal_number_analysis(current_price)
        if fatal.nearby_fatal_levels:
            mult, lvl = fatal.nearby_fatal_levels[0]
            confidence += 0.05
            reasons.append(
                f"Price near Fatal Number level: {mult}×n = {lvl:.0f} "
                f"(Gann's Fatal 49, PDF 18 p.86)"
            )

        # Check significant squares of the low (PDF 10, p.2)
        # "The 1st, 2nd, 3rd, 4th, 7th, 9th and 12th squares of the
        # low are significant."
        for sq in SIGNIFICANT_SQUARES_OF_LOW:
            sq_level = low * sq
            if abs(sq_level - current_price) / current_price < 0.005:
                confidence += 0.05
                reasons.append(
                    f"Price near {sq}× low ({sq_level:.2f}) — "
                    f"significant square of low (PDF 10, p.2)"
                )
                break

        # Check Third-Time Test rule (PDF 10, p.2 — deep study finding)
        # "The 3rd time against any S/R zone is the dangerous time."
        if prices_history and len(prices_history) >= 10:
            # Test the current midpoint as a key zone
            midpoint = (high + low) / 2.0
            third_test = self.third_time_test(
                prices_history, midpoint, tolerance_pct=0.5, zone_kind="support"
            )
            if third_test.is_dangerous:
                confidence += 0.05
                reasons.append(
                    f"Third-time test at {midpoint:.2f} zone — "
                    f"breakout/breakdown imminent (PDF 10, p.2)"
                )

        # Check 192-Day Master Time Factor shock points (PDF 6, pp.5–8)
        # Requires a deterministic current_date to avoid non-reproducibility.
        if current_date and prices_history and len(prices_history) >= 30:
            cur_dt = datetime.strptime(current_date, "%Y-%m-%d")
            ref_date_proxy = (
                cur_dt - timedelta(days=len(prices_history))
            ).strftime("%Y-%m-%d")
            mtf = self.master_time_factor_analysis(ref_date_proxy, current_date)
            if mtf.is_shock_point:
                confidence += 0.05
                reasons.append(
                    f"At diatonic '{mtf.diatonic_note}' shock point in "
                    f"192-day octave #{mtf.current_octave} "
                    f"(day {mtf.position_in_octave}/192, PDF 6 pp.5-8)"
                )

        # Check Jensen critical time points (Jensen Astro-Cycles, pp.108-113)
        # "Count from a major high or low in calendar days for critical areas."
        if current_date and prices_history and len(prices_history) >= 30:
            cur_dt = datetime.strptime(current_date, "%Y-%m-%d")
            ref_date_proxy = (
                cur_dt - timedelta(days=len(prices_history))
            ).strftime("%Y-%m-%d")
            jcp = self.jensen_critical_points(ref_date_proxy, current_date)
            if jcp.is_critical_window:
                confidence += 0.05
                reasons.append(
                    f"Jensen critical time point: {jcp.cycle_label} "
                    f"(day {jcp.elapsed_days}, Jensen pp.108-113)"
                )

        # Check Jensen five-phase intermediate trend (Jensen, pp.121-122)
        # "The 3rd directional phase is the largest and longest — blowoff."
        if prices_history and len(prices_history) >= 20:
            fpt = self.five_phase_trend(prices_history)
            if fpt.is_blowoff_phase:
                confidence += 0.05
                reasons.append(
                    f"Jensen five-phase: in blowoff phase 5 "
                    f"({fpt.swing_count} swings, trend={fpt.trend_direction}, "
                    f"Jensen pp.121-122)"
                )

        # --- NEW: Futia Angular Position (PDF 25) ---
        futia = self.futia_angular_position(current_price)
        if futia.is_near_cardinal:
            confidence += 0.05
            reasons.append(
                f"Futia SQ9 angular: price {current_price} at {futia.angular_position}° "
                f"near {futia.nearest_cardinal}° axis "
                f"(distance={futia.distance_to_cardinal}°, PDF 25)"
            )

        # --- NEW: Triangular Number Proximity (PDF 26) ---
        tri = self.triangular_number_proximity(current_price)
        if tri.is_near_level:
            confidence += 0.05
            reasons.append(
                f"Triangular S/R: price {current_price} near summation "
                f"number {tri.nearest_triangular} "
                f"(distance={tri.distance}, PDF 26 p.21)"
            )

        # --- NEW: Range Expansion (PDF 27) ---
        if prices_history and len(prices_history) >= 4:
            # Pseudo highs/lows from consecutive closes (simplified
            # approximation when actual OHLC data is unavailable)
            recent_closes = prices_history[-4:]
            pseudo_highs = [max(recent_closes[i], recent_closes[i + 1])
                            for i in range(len(recent_closes) - 1)]
            pseudo_lows = [min(recent_closes[i], recent_closes[i + 1])
                           for i in range(len(recent_closes) - 1)]
            rex = self.range_expansion_check(
                pseudo_highs[-2:], pseudo_lows[-2:], recent_closes[-2:]
            )
            if rex.is_expanding and rex.expansion_ratio > 1.2:
                confidence += 0.05
                reasons.append(
                    f"Range expansion: ratio={rex.expansion_ratio}, "
                    f"bias={rex.bias_direction} (Crabel, PDF 27 p.11)"
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
    print("Synthesized from 27 PDF documents on Gann's methods")
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
