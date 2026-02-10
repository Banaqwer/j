# W.D. Gann PDF Analysis — Compte Rendu & Algorithm Documentation

## Table of Contents

1. [Individual PDF Summaries (Compte Rendu)](#individual-pdf-summaries)
2. [Cross-Document Similarities](#cross-document-similarities)
3. [Merged Knowledge — Algorithm Design](#merged-knowledge--algorithm-design)
4. [Algorithm Usage Guide](#algorithm-usage-guide)

---

## Individual PDF Summaries

### PDF 1: "20 Years of Studying Gann" (27 pages)

**About:** A comprehensive autobiographical guide written by a researcher who spent 20 years studying W.D. Gann's methods. The author shares their journey from novice to experienced Gann trader, offering practical guidance on how to decode Gann's works, particularly "The Tunnel Thru the Air."

**Key Teachings (Beneficial for Algorithm):**

- **Time Cycles are Primary:** ALL of Gann's systems start with TIME cycles. Without accurate time cycles, geometry and price analysis are useless. Time cycles must show a High-Low-High-Low sequence with approximately 10% inversions.
- **Cycles of Repetition:** All of Gann's cycles work off repeats of the past (Ecclesiastes 1:9). Cycles have specific lengths measured in planetary degrees or calendar days.
- **Law of Vibration (L.O.V.):** Everything in the universe has a specific resonant frequency. Markets vibrate at specific frequencies; matching those frequencies allows accurate forecasting.
- **Numerology System:** A=1, B=2, C=3... Z=8. Numbers govern vibration. Name numbers and birth numbers create harmonic or disharmonic frequencies.
- **Vibrational Trading Range:** Each trader has a personal frequency range for position sizing. Exceeding this range (e.g., doubling position size) typically leads to losses. Never trade more than 10% of account per trade.
- **Instrument Specificity:** About 1 in 30 instruments will be naturally profitable for a given trader. Finding your "lucky instrument" is critical.
- **Inversions:** Inversions (where expected highs become lows or vice versa) occur ~10% of the time. They are nature's way of keeping cycles in sync.
- **Testing Cycles:** Set up repeating spreadsheets of planetary degree cycles. Going DOWN a column should show H-L-H-L sequence. Going ACROSS columns shows vibrational repeats at specific degree values.

---

### PDF 2: "Super Timing — W.D. Gann's Astrological Method" by Walker Myles Wilson (image-based)

**About:** A detailed guide on Gann's astrological/astronomical methods for market timing. The PDF is image-based and could not be text-extracted, but is known to cover planetary aspects, transits, and their correlation with market turning points.

**Key Teachings:**

- Planetary cycles and aspects (conjunctions, squares, oppositions, trines) time market turns.
- The heliocentric and geocentric positions of planets create repeating market patterns.
- Specific planetary pairs govern specific markets/commodities.

---

### PDF 3: "WD Gann Astro Cycles" (77 pages, image-based)

**About:** A visual/graphical document showing the relationship between astronomical cycles and market price movements. Image-based, no text could be extracted.

**Key Teachings:**

- Charts demonstrating the correlation between planetary cycles and price movements.
- Visual demonstrations of how to overlay planetary positions onto price charts.
- Cycle lengths derived from planetary orbital periods.

---

### PDF 4: "Gann through My Lens" by Raju Chowksey (52 pages)

**About:** A practical presentation explaining how to apply Gann's methods to real-world trading, particularly in the Indian stock market (Nifty). Covers Square of 9, price-time squaring, patterns, SAP, and ATM trading rules.

**Key Teachings (Beneficial for Algorithm):**

- **Natural Squares:** Price moves from one odd square to the next (1, 9, 25, 49, 81, 121...). The distance between consecutive odd squares is exactly 360°.
- **Square of 9 Roadmap:** Divide the range between consecutive odd squares into 8 equal parts (each = 45°). Example: 49 to 81: range = 32, step = 4, roadmap = 49-53-57-61-65-69-73-77-81.
- **Dynamic Square of Gann:** From a significant high or low, take √price and add increments:
  - 360° level: (√price + 2)²
  - 180° level: (√price + 1)²
  - 90° level: (√price + 0.5)²
  - 45° level: (√price + 0.25)²
- **Price-Time Squaring (P = T²):** "When Price & Time coordinates balance each other, a change in trend is imminent." T = √P. This is the "Da Vinci Code" of the presentation.
- **Da Vinci Code Decoding Method:**
  1. Calculate Range = High - Low
  2. Time Window: T = √Range (in days), project multiples (1T, 2T, 3T)
  3. Price Windows: Use 4-digit and 3-digit methods with 180°, 360°, 720° offsets
  4. When time and price windows converge = high-probability turning point
- **Semi-Annual Pivot (SAP):** Calculate twice yearly (Jan & Jul) using OHLC from 1st-14th. Trade on the side of SAP and close to SAP number.
- **Patterns:** 2-B (double bottom) and 2-T (double top) are favorites. A combination of Gann level + Pattern + Small SL = "A-A-A" (best trade).
- **ATM Trade Rules:**
  1. Sell options, don't buy them
  2. Look for at-the-money or just in-the-money options
  3. Draw nearest perfect Gann square horizontal lines after first 1-5 minutes
  4. Look for combinations of Gann square + patterns
  5. Small SL (5-7 points)
  6. Minimum risk-reward 1:2.5/3, book 50% at target, trail balance
  7. Use 30/36 period moving average for directional bias
- **Trading Rules:**
  1. "Small is beautiful" — small positions, small stop losses
  2. Rule of 72: When tempted to take profits, book only 25%, let balance run for next 24-48-72 hours
  3. Trade on levels, not beliefs
  4. Most of the time you'll be wrong — quit with small losses
  5. When right, follow Rule of 72

---

### PDF 5: "Intraday Trade Using Gann Angle" by Soumya Ranjan Panda (19 pages)

**About:** A detailed mathematical guide to using Gann angles for intraday trading. Provides exact formulas, calculation tables, and worked examples with SBI stock.

**Key Teachings (Beneficial for Algorithm):**

- **11 Gann Angle Trend Lines:** 1X1, 1X2, 2X1, 1X3, 3X1, 1X4, 4X1, 1X8, 8X1, 1X16, 16X1
- **Geometric Angles:**
  - 1X1 = 45°, 2X1 = 63.75°, 1X2 = 26.25°
  - 3X1 = 71.25°, 1X3 = 18.75°, 4X1 = 75°, 1X4 = 15°
  - 8X1 = 82.5°, 1X8 = 7.5°, 16X1 = 86.25°, 1X16 = 3.75°
- **Degree Factors:** 180° = factor 1 (one day of solar motion). Each angle has a degree factor = angle/180.
- **Core Formulas:**
  - Support = (√high − degree_factor)²
  - Resistance = (√low + degree_factor)²
- **Trading Rules:**
  - Rule a: The 3rd support/resistance is important
  - Rule b: 1X1 (45°) support break favors sellers; 1X1 resistance break favors buyers (when annual volatility > 50%)
  - Rule c: In low/medium volatile markets (< 50%), use 1X4 (15°) resistance and 4X1 support for entries
  - Rule d: If sell entry > buy entry = error → recalculate from midpoint
  - Rule e: For 4-digit prices, need minimum 5-unit difference between buy/sell entries
  - Rule f: For 3-digit prices, need minimum 3.5-unit difference
  - Rule g: Convert 2-digit/1-digit prices to 4-digit by multiplying by 10/100/1000
  - Rule h: Use 5-minute or 15-minute high/low after opening (ignore auction periods)
  - Rule i: If stop loss triggers, do not re-enter in same direction
- **Trend Confirmation:**
  - 1X4 / 4X1 crossover = preliminary trend confirmation
  - 1X1 crossover = strong breakout
  - Trend terminates at 16X1 / 1X16 price points
- **Daily Volatility Calculation:**
  1. Take 10 days of closing prices
  2. Calculate absolute returns: LN(current/previous)
  3. Calculate squared returns
  4. Variance = mean(squared returns) − mean(returns)²
  5. Daily volatility % = √variance × 100
- **Dynamic Square of 9:** Step = expected_range / 81. Seed = last_price + step. Each subsequent number = previous + step.
- **Dynamic Square of 12:** Step = expected_range / 144. Use when annual volatility > 40%, else use Square of 9.
- **Annual Volatility:** daily_vol × √365. If > 40% → Square of 12, else Square of 9.

---

### PDF 6: "WD GANN Number Vibrations" (3 pages)

**About:** An exploration of Gann's numerology applied to price analysis, focusing on digit reduction and the significance of the number 144.

**Key Teachings (Beneficial for Algorithm):**

- **Digit Reduction:** Reduce any number to a single digit by summing its digits repeatedly. Example: 2417 → 2+4+1+7 = 14 → 1+4 = 5. The number "dances to the vibration of 5."
- **360° Circle Pattern:** Breaking 360° into 30° increments (30, 60, 90, ..., 360) and reducing to single digits gives the pattern 3-6-9-3-6-9-3-6-9-3-6-9 — perfect symmetry.
- **Cardinal Points (0, 90, 180, 270, 360):** All reduce to 9 → change numbers.
- **Trine Points (45, 135, 225, 315):** All reduce to 9 → change points.
- **The Number 144:** 1+4+4 = 9 (change number). All multiples of 9 up to 144 (18, 27, 36, 45, 54, 63, 72, 81, 90, 99, 108, 117, 126, 135, 144) reduce to 9.
- **144 as Trading Cycle:** Look for price levels at multiples of 144. If 144 is too large, use subdivisions: 18, 36, 54, 72.
- **Percentage Vibration Table:** The standard percentage increments (3.125%, 6.25%, ..., 100%) when reduced to single digits create a perfect Yin-Yang pattern alternating even-odd digits: 2-4-6-8-1-3-5-7-9, repeating.
- **Application:** When a stock is at a price, add/subtract 144 (or subdivisions) to find next support/resistance. Back-test these numbers on historical data.

---

### PDF 7: "Tunnel Thru the Air" by W.D. Gann (432 pages)

**About:** W.D. Gann's 1927 novel, considered his magnum opus. Written as a romance/adventure story, it encodes Gann's complete trading methodology in "veiled language." The story follows Robert Gordon from rural Texas to becoming Supreme Commander, with inventions and events representing coded market analysis techniques.

**Key Teachings (Beneficial for Algorithm):**

- **The book's threefold purpose:** (1) Entertainment, (2) Moral lessons proving natural laws from the Bible, (3) Demonstrating the value of science, foreknowledge, and preparedness.
- **Hidden Cycles:** Dates, city references, and invention mentions in the book encode specific time cycle lengths (measured in days). The distance between repeated mentions of the same "invention" reveals cycle lengths.
- **Inventions as Metaphors:** Each invention (Marie the Angel of Mercy, Tele-Talk, Pocket Radio, Silent Muffler, etc.) represents a different aspect of Gann's trading system.
- **Numbers and Repetition:** Important elements are mentioned specific numbers of times (e.g., "Charity" appears 5 times, linking to concepts where 5 is significant).
- **Key Principles Stated Explicitly:**
  - Time is the most important factor
  - History repeats itself
  - Study cycles and their repetition
  - The Bible contains natural laws applicable to markets
  - Truth is stranger than fiction — the story encodes real events
- **The 110-Story Building:** A hub in the book's coding, used in at least 3 different calculations.
- **Cities and Coordinates:** Every city mentioned has significance; their longitude and latitude should be noted.
- **Love as Metaphor:** Robert Gordon's devotion to Marie Stanton represents the dedication required for mastering Gann's methods.

---

## Cross-Document Similarities

### 1. Time Dominance (PDFs 1, 4, 5, 7)
All documents agree: **Time is the most important factor.** Price is secondary and follows time. Gann's system starts with time cycles, and without accurate time cycles, all other analysis is meaningless.

### 2. Square Root Price Relationships (PDFs 4, 5)
Both PDF 4 and PDF 5 use the **square root of price** as the foundation for calculating support, resistance, and future price levels. The core formula √price ± offset appears in both the Square of 9 and Gann Angle calculations.

### 3. The 360° Circle and Its Divisions (PDFs 4, 5, 6)
The full circle (360°) and its standard divisions (45, 90, 120, 180, 270) are fundamental across all three mathematical PDFs:
- PDF 4: Square of 9 uses 360° to define one complete spiral
- PDF 5: 180° = factor 1 in degree calculations
- PDF 6: Circle divisions create the 3-6-9 numerological pattern

### 4. The Number 9 and 144 (PDFs 1, 4, 6)
The number 9 appears repeatedly as the "change number." 144 (which reduces to 9) is a key cycle length. The Square of 12 (12 × 12 = 144) connects PDF 5's dynamic method to PDF 6's numerology.

### 5. Volatility Integration (PDFs 4, 5)
Both practical PDFs emphasize that static Gann methods must be made **dynamic** through volatility:
- PDF 5: Explicitly calculates daily volatility and uses it to project expected ranges
- PDF 4: Uses range-based calculations that implicitly account for recent price movement

### 6. Pattern Recognition (PDFs 4, 5)
Both trading-focused PDFs emphasize looking for **combinations** of Gann levels with price patterns (2B/2T, congestion resolution) for highest-probability trades.

### 7. Risk Management (PDFs 1, 4)
Consistent risk management principles:
- Small stop losses ("Small is beautiful" — PDF 4)
- Maximum 10% of account per trade (PDFs 1, 4)
- Minimum 1:2.5 risk-reward ratio (PDF 4)
- Position sizing within "vibrational range" (PDF 1)

### 8. Cycles of Repetition (PDFs 1, 7)
Both the guide and the novel emphasize that ALL cycles work off **historical repetition.** What happened before will happen again. The length of the cycle determines when.

---

## Merged Knowledge — Algorithm Design

The algorithm (`gann_trading_algorithm.py`) merges all extractable mathematical and strategic knowledge from the seven PDFs into a unified `GannAnalyzer` class with the following components:

| Component | Source PDFs | Method |
|-----------|------------|--------|
| Gann Angle Support/Resistance | 4, 5 | `gann_angle_levels()` |
| Square of 9 Price Levels | 4, 5 | `square_of_nine_levels()` |
| Square of 9 Roadmap | 4 | `square_of_nine_roadmap()` |
| Daily Volatility Calculation | 5 | `calculate_daily_volatility()` |
| Dynamic Gann Levels | 5 | `dynamic_gann_levels()` |
| Dynamic Square of 9 | 5 | `dynamic_square_of_nine()` |
| Dynamic Square of 12 | 5 | `dynamic_square_of_twelve()` |
| Number Vibration Analysis | 6, 1 | `number_vibration()` |
| 144-Cycle Levels | 6 | `gann_144_levels()` |
| Price-Time Squaring | 4 | `price_time_square()` |
| Cycle Detection | 1, 7 | `detect_cycles()` |
| Semi-Annual Pivot | 4 | `semi_annual_pivot()` |
| Trend Confirmation | 5 | `trend_status()` |
| Unified Signal Generation | ALL | `generate_signal()` |

---

## Algorithm Usage Guide

### Installation

No external dependencies beyond Python's standard library are required. The algorithm uses only `math`, `dataclasses`, `datetime`, and `typing`.

### Quick Start

```python
from gann_trading_algorithm import GannAnalyzer

analyzer = GannAnalyzer()

# 1. Calculate Gann Angle support/resistance levels
levels = analyzer.gann_angle_levels(high=3238.35, low=3214.10)
print(f"Buy at: {levels.buy_entry}, Sell at: {levels.sell_entry}")

# 2. Get Square of 9 price levels
sq9 = analyzer.square_of_nine_levels(7540)
for deg, price in sorted(sq9.levels.items()):
    print(f"  {deg}° -> {price}")

# 3. Dynamic levels with volatility
prices = [1880, 1875.35, 1883, 1885.5, 1885, 1909.25, 1933.9, 1949, 1911, 1842.25]
dynamic = analyzer.dynamic_gann_levels(prices)
print(f"Expected range: {dynamic.expected_low} - {dynamic.expected_high}")

# 4. Number vibration
vib = analyzer.number_vibration(2417)
print(f"Vibration of {vib.original} = {vib.single_digit}")

# 5. Price-Time Square
pts = analyzer.price_time_square(8627, 7961, "2014-12-04", "2014-12-17")
for label, dt in pts.time_windows:
    print(f"  {label}: {dt.strftime('%Y-%m-%d')}")

# 6. Full trading signal
signal = analyzer.generate_signal(
    high=3238.35, low=3214.10,
    current_price=3225.0,
    prices_history=prices,
    account_size=100000.0
)
print(f"Signal: {signal.direction} at {signal.entry_price}")
print(f"Stop: {signal.stop_loss}, Targets: {signal.targets}")
print(f"Confidence: {signal.confidence}")
```

### Running the Demo

```bash
python gann_trading_algorithm.py
```

This runs the complete demonstration with examples from the PDF documents.

---

## Tunnel Thru the Air — Decryption Results

The `tunnel_decoder.py` module performs systematic decryption of the novel using the techniques described in all companion PDFs (especially PDF 1 "20 Years of Studying Gann").

### Decoded Elements

#### 1. Dates (85 extracted)
- **Robert Gordon's birth:** June 9, 1906
- **Narrative span:** 1906 to 1932
- **40 exact dates** and 45 approximate dates
- Key narrative dates cluster around January-June 1927, matching the cotton campaign Gann described

#### 2. Inventions (7 decoded)
Each invention represents a different aspect of Gann's trading system:

| Invention | Mentions | Vibration | Line Span | Decoded Role |
|-----------|----------|-----------|-----------|-------------|
| Marie the Angel of Mercy | 24 | 6 | 6,158 lines | The complete trading system / airship |
| Tunnel Machine | 14 | 5 | 1,906 lines | Market analysis / cycle detection apparatus |
| Pocket Radio | 6 | 6 | 2,093 lines | Communication / real-time data feed |
| Radium Ray | 4 | 4 | 40 lines | Scanning / screening tool |
| Water Bicycle | 2 | 2 | 20 lines | Early prototype / foundational concept |
| Silent Muffler | 1 | 1 | 0 lines | Risk management / noise reduction |
| Tele-Talk | 0* | — | — | Distant communication |

#### 3. Time Cycles (13 matching Gann numbers)
Intervals between narrative dates reveal encoded cycle lengths:

| Cycle Length | Occurrences | Gann Number Match | Vibration |
|-------------|-------------|-------------------|-----------|
| ~30 days | 9× | 30 (1/12 of 360°) | 3 |
| ~123 days | 6× | 120 (trine, 1/3 of 360°) | 6 |
| ~61 days | 6× | 60 (sextile, 1/6 of 360°) | 7 |
| ~9 days | 6× | 7 (week cycle) | 9 |
| ~36 days | 3× | 36 (144/4 subdivision) | 9 |
| ~365 days | 2× | 365 (solar year) | 5 |
| ~89 days | 2× | 90 (square, 1/4 of 360°) | 8 |
| ~46 days | 2× | 45 (1/8 of 360°) | 1 |
| ~50 days | 2× | 49 (7² completion) | 5 |
| ~182 days | 1× | 180 (opposition) | 2 |
| ~228 days | 1× | 225 (5/8 of 360°) | 3 |

#### 4. Robert Gordon's Trades
The novel encodes specific cotton, wheat, and corn trades at actual historical prices, validating the Gann angle and Square of 9 calculations from PDFs 4 and 5.

#### 5. Cities (14 referenced)
Each city has encoded geographical significance (longitude/latitude noted per PDF 1's instructions).

#### 6. Key Principles
Six core principles extracted directly from the novel text:
1. Cycle theory — past cycles predict future events
2. History repeats itself (Ecclesiastes 1:9)
3. There is no new thing under the sun
4. Know the cause to predict the effect
5. Wheel within a wheel — cycles within cycles (Ezekiel)
6. Time is the great factor that proves all things

### Running the Decoder

```bash
python tunnel_decoder.py
```

---

## Backtesting Engine

The `backtest_engine.py` module makes the entire algorithm backtestable by running the unified Gann signal generator bar-by-bar against historical OHLC price data.

### Features

- **Bar-by-bar simulation:** Processes each bar sequentially, generating signals from the Gann algorithm
- **Full trade management:** Entry, exit, stop loss, targets, partial exits, trailing stops
- **Risk management:** Position sizing (max 10% risk), minimum 2.5:1 reward-to-risk ratio, position value caps
- **Multiple exit types:** Target hit, stop loss, trailing stop, timeout (72-bar max), partial profit booking
- **Performance metrics:** Win rate, PnL, profit factor, max drawdown, Sharpe ratio, consecutive streaks
- **CSV import/export:** Load any OHLC CSV file, export trade logs and equity curves

### Quick Start

```python
from backtest_engine import GannBacktester, BacktestConfig

# Configure
config = BacktestConfig(
    initial_capital=100000.0,
    max_risk_pct=10.0,        # Max 10% risk per trade
    min_reward_risk=2.5,      # Min 2.5:1 reward-to-risk
    min_confidence=0.25,      # Min signal confidence
    lookback_bars=10,         # Bars for volatility calc
    max_hold_bars=72,         # Max bars to hold (Rule of 72)
    use_trailing_stop=True,   # Trail stop after partial exit
    partial_exit_pct=0.5,     # Book 50% at first target
)

# Run backtest
bt = GannBacktester(config)
result = bt.run("your_data.csv")  # CSV: date,open,high,low,close

# View results
result.print_summary()
result.print_trades()
result.export_csv("output.csv")
```

### Data Format

CSV file with columns: `date`, `open`, `high`, `low`, `close`, `volume` (volume optional)

```csv
date,open,high,low,close,volume
2024-01-02,5000.00,5050.00,4980.00,5030.00,250000
2024-01-03,5030.00,5070.00,5010.00,5055.00,280000
```

### Running the Demo

```bash
python backtest_engine.py
```

This generates 252 bars of sample data, runs a full backtest, and exports results.

---

*This analysis, algorithm, Tunnel decryption, and backtesting engine were synthesized from ALL FOURTEEN W.D. Gann PDF documents, extracting and merging all quantifiable mathematical techniques and strategic principles into a unified, executable, and backtestable trading analysis system. The `generate_signal()` method integrates concepts from every PDF: Gann angles (PDFs 4, 5), Square of 9 (PDFs 4, 5, 8), number vibrations (PDF 6), dynamic volatility (PDF 5), hexagon chart timing (PDF 8), master time periods (PDFs 12, 13), natural 1/8th retracement levels (PDFs 10, 11, 13), price-time vectors (PDF 9), Gann time counts (PDFs 7, 11), lunar cycles (PDF 14), seasonal dates (PDFs 10, 11), 144-cycle levels (PDFs 6, 13), and astrological framework (PDFs 2, 3).*
