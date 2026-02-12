# TradingView Live Trader Setup Guide

## Pine Script Versions

| File | Components | Description |
|------|-----------|-------------|
| **`gann_complete_strategy.pine`** | **All 21** | Full algorithm — all PDF teachings implemented |
| `gann_tradingview_strategy.pine` | 9 of 21 | Original version — core Gann methods only |

> **Recommended**: Use `gann_complete_strategy.pine` for the most complete implementation.

## Gann Complete Strategy — Pine Script v5 (21 Components)

This Pine Script translates the **full** Python Gann algorithm (all 21 components from
21 PDF documents) into a TradingView strategy that can be used for **live paper trading**
(demo account) on any asset (BTC, ETH, Gold, Forex, Stocks).

---

## Quick Start (5 minutes)

### Step 1: Open TradingView
1. Go to [tradingview.com](https://www.tradingview.com)
2. Open a chart for **BTCUSD** or **ETHUSD** (any exchange: Coinbase, Binance, etc.)
3. Set timeframe to **1D** (Daily)

### Step 2: Add the Strategy
1. Click **Pine Editor** at the bottom of the screen
2. Delete any existing code
3. Copy the entire contents of **`gann_complete_strategy.pine`** (recommended) or `gann_tradingview_strategy.pine`
4. Paste into the Pine Editor
5. Click **"Add to Chart"** (or press Ctrl+Enter)

### Step 3: View Backtest Results
1. Click the **"Strategy Tester"** tab at the bottom
2. You'll see:
   - **Overview**: Net profit, win rate, profit factor
   - **Performance Summary**: Detailed statistics
   - **List of Trades**: Every entry and exit with P/L

### Step 4: Enable Paper Trading (Demo Account)
1. In the Strategy Tester, click the **three dots menu** (⋯)
2. Select **"Paper Trading"**
3. The strategy will now execute trades on your demo account
4. You'll receive alerts for each entry/exit

---

## What the Strategy Shows on Chart

| Visual Element | Color | Meaning |
|---------------|-------|---------|
| Green triangle ▲ | Green | BUY signal |
| Red triangle ▼ | Red | SELL signal |
| Solid green line | Green | 1x1 (45°) Resistance |
| Solid red line | Red | 1x1 (45°) Support |
| Blue crosses + | Blue | Square of 9 levels (up) |
| Purple crosses + | Purple | Square of 9 levels (down) |
| White step-line | White | Range 50% (center of gravity) |
| Gray step-lines | Gray | Range 25%, 33%, 66%, 75% divisions |
| Aqua crosses + | Aqua | Hexagon chart levels |
| Teal shaded area | Teal | Expected daily volatility range |
| Yellow diamonds ◆ | Yellow | Shephard key cycle alignment |
| Orange x-crosses | Orange | Fatal Number (49) time alignment |
| Blue background | Light blue | Seasonal cardinal date (equinox/solstice) |
| Purple background | Light purple | Seasonal octave date |
| Green background | Light green | Bullish trend confirmed |
| Red background | Light red | Bearish trend confirmed |

## Info Panel (Top Right) — 16-Row Dashboard

The strategy displays a real-time info panel showing:
- **Trend (C7)**: Gann angle trend direction
- **Swing (C11)**: Mechanical HH/HL vs LH/LL trend
- **Buy/Sell Confidence**: 0.00 to 1.00 score (12 factors)
- **Vibration (C3)**: Digit reduction (9 = change number)
- **SQ9 (C2)**: Price near Square of 9 level
- **Hexagon (C9)**: Price near hexagon 60° level
- **Range% (C10)**: Price near Gann percentage division
- **Fatal 49 (C14)**: Price or time near Fatal Number
- **Seasonal (C13)**: Cardinal or octave date status
- **Shephard (C15)**: Key cycle alignment warning
- **Daily/Annual Vol**: Volatility (SQ12 triggers at high vol)
- **Buy/Sell R:R**: Current reward-to-risk ratios

---

## Configurable Settings

### Main Settings
| Parameter | Default | Description |
|-----------|---------|-------------|
| Risk Per Trade (%) | 1.5% | Percentage of equity risked per trade |
| Reward:Risk Ratio | 2.5:1 | Minimum R:R to boost confidence |
| Min Confidence | 0.40 | Minimum confidence score to enter trade |
| Volatility Lookback | 20 bars | Periods for volatility calculation |
| Swing Lookback | 50 bars | Periods for swing high/low detection |

### Gann Settings
| Parameter | Default | Description |
|-----------|---------|-------------|
| Show Gann Angles | ✓ | Display 11 angle S/R levels |
| Show SQ9 Levels | ✓ | Display Square of 9 price levels |
| Show 144 Levels | ✗ | Display 144-cycle price zones |
| Show Range % Levels | ✓ | Display Gann percentage divisions |
| Show Hexagon Levels | ✗ | Display hexagon 60° angle levels |
| SQ9 Confluence (%) | 0.5% | Tolerance for SQ9 level proximity |
| SQ12 Trigger Vol | 40% | Annual vol threshold for dynamic levels |

### Trade Management
| Parameter | Default | Description |
|-----------|---------|-------------|
| Partial Exit (%) | 50% | Position to close at first target |
| Trailing Stop (%) | 2.0% | Trail distance for remaining position |
| Max Bars in Trade | 60 | Force close after N bars |

### Advanced — New Components
| Parameter | Default | Description |
|-----------|---------|-------------|
| Use Fatal Number (49) | ✓ | Check price proximity to multiples of 49 |
| Use Swing Trend | ✓ | HH/HL/LH/LL mechanical trend analysis |
| Use Seasonal Cardinal | ✓ | Equinox/solstice/octave date checks |
| Use Range % Confidence | ✓ | Range percentage level confluence |
| Use Hexagon Confidence | ✓ | Hexagon chart level confluence |
| Swing Trend Bars | 5 | Number of bars for swing trend counting |

---

## Gann Components Implemented

### `gann_complete_strategy.pine` — All 21 Components

| # | Component | Source PDFs | Method |
|---|-----------|-------------|--------|
| C1 | **Gann Angle S/R** (11 angles) | PDF 5 | `(√base ± factor)²` |
| C2 | **Square of 9** levels | PDFs 4, 5 | Spiral at 0°–360° crosses |
| C3 | **Number Vibration** | PDF 6 | Digit reduction; 9 = change |
| C4 | **Daily Volatility** | PDF 5 | Log-return std deviation |
| C5 | **Dynamic Levels** (SQ9/SQ12) | PDF 5 | Volatility-adjusted range |
| C6 | **144-Cycle Zones** | PDFs 6, 17 | Master cycle price levels |
| C7 | **Trend Confirmation** | PDF 5 | 1x1 angle breakout |
| C8 | **Price-Time Squaring** | PDFs 4, 12, 17 | P = T² projections |
| C9 | **Hexagon Chart** | PDF 9 | 60° angle levels |
| C10 | **Range % Divisions** | PDFs 12, 17, 18 | 1/8th & 1/3rd levels |
| C11 | **Swing Trend** | PDF 18 | HH/HL/LH/LL mechanical |
| C12 | **Master 144 Square** | PDF 17 | Great Cycle = 20,736 |
| C13 | **Seasonal Cardinal** | PDFs 11, 12, 19 | Equinox/solstice timing |
| C14 | **Fatal Number (49)** | PDF 18 pp.86,100 | 49 multiples in price/time |
| C15 | **Shephard Cycles** | PDF 18 pp.85-86 | 631/668/840/1260/1290/1336 |
| C16 | **Planetary Cycles** | PDF 18 pp.67-108 | Mars 687d, Venus 224d |
| C17 | **Cumulative Range** | PDF 18 pp.96,110 | Hidden cycle sums |
| C18 | **Master Time Factor** | PDFs 13, 16 | 7/10/20/30/60-year cycles |
| C19 | **Range Extensions** | PDFs 12, 17 | Projection above high |
| C20 | **Multi-Timeframe** | General Gann | Weekly trend context |
| C21 | **Confidence Scoring** | All PDFs | 12-factor scoring (0.0–1.0) |

---

## Confidence Scoring Breakdown (21-Component Version)

| Factor | Points | Condition |
|--------|--------|-----------|
| Trend confirmed (C7) | +0.30 | Price above/below 1x1 angle |
| SQ9 confluence (C2) | +0.10 | Price within 0.5% of cardinal level |
| Vibration 9 (C3) | +0.10 | Price digit sum = 9 |
| Dynamic vol confirms (C5) | +0.15 | Price within expected range |
| Range % nearby (C10) | +0.05 | Price near 1/8th or 1/3rd level |
| Hexagon nearby (C9) | +0.05 | Price near 60° hexagon level |
| Fatal 49 nearby (C14) | +0.05 | Price near multiple of 49 |
| Swing trend confirms (C11) | +0.05 | HH+HL (buy) or LH+LL (sell) |
| Seasonal date (C13) | +0.05 | Cardinal or octave date ±3 days |
| Shephard/planetary cycle (C15/16) | +0.05 | Key cycle number from pivot |
| Weekly trend confirms (C20) | +0.05 | Weekly timeframe agrees |
| R:R ≥ 2.5:1 | +0.15 | Good reward-to-risk |
| R:R 1.5–2.5:1 | +0.05 | Acceptable reward-to-risk |
| R:R < 1.5:1 | −0.10 | Poor reward-to-risk penalty |

**Maximum possible: 1.10 → capped at 1.00**
**Minimum to trade: 0.40** (configurable)

---

## Alerts Setup

The complete strategy includes **7 alert conditions**:
1. **Gann BUY Signal** — All buy conditions met
2. **Gann SELL Signal** — All sell conditions met
3. **Vibration 9 Alert** — Price digit sum = 9 (reversal watch)
4. **Shephard Cycle Alert** — Key cycle number alignment (major reversal window)
5. **Fatal 49 Alert** — Price near Fatal Number multiple
6. **Seasonal Cardinal Alert** — Cardinal/octave date (increased reversal probability)
7. **Cumulative Range Alert** — Hidden cycle sum detected

To set up alerts:
1. Right-click on the chart → "Add Alert"
2. Condition: Select "Gann Complete Strategy (21 Components)"
3. Choose the alert type
4. Set notification method (popup, email, webhook)

---

## Recommended Assets

| Asset | Timeframe | Notes |
|-------|-----------|-------|
| BTCUSD | 1D | Primary — real data backtest: 67.4% WR, +445% return, 648 trades |
| ETHUSD | 1D | Works well with Gann angle adaptation |
| SOLUSD | 1D | Crypto — SQ12 activates on high volatility |
| XAUUSD | 1D | Gold — traditional Gann asset, lower volatility uses SQ9 |
| EURUSD | 1D | Forex — Gann angles work well on majors |
| Any stock | 1D | Works on any daily chart |

> **Note**: BTC backtest was run on real Binance BTCUSDT daily klines (2021-2024).
> 648 trades, 67.4% WR, profit factor 11.10, max DD 2.78%.
> Past performance does **not** guarantee future results.
> Always validate on TradingView's built-in Strategy Tester with live market data
> before risking real capital.

---

## Disclaimer

⚠️ **This strategy is for educational and research purposes only.**
- Past backtest performance does not guarantee future results
- Always use a demo/paper account before risking real capital
- The algorithm is based on W.D. Gann's historical methods
- Cryptocurrency markets are highly volatile and risky
- Never risk more than you can afford to lose
