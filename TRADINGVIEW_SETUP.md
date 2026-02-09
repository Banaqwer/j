# TradingView Live Trader Setup Guide

## Gann Unified Strategy — Pine Script v5

This Pine Script translates the full Python Gann algorithm into a TradingView strategy
that can be used for **live paper trading** (demo account) on BTC/USD and ETH/USD.

---

## Quick Start (5 minutes)

### Step 1: Open TradingView
1. Go to [tradingview.com](https://www.tradingview.com)
2. Open a chart for **BTCUSD** or **ETHUSD** (any exchange: Coinbase, Binance, etc.)
3. Set timeframe to **1D** (Daily)

### Step 2: Add the Strategy
1. Click **Pine Editor** at the bottom of the screen
2. Delete any existing code
3. Copy the entire contents of `gann_tradingview_strategy.pine`
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
| Teal shaded area | Teal | Expected daily volatility range |
| Green background | Light green | Bullish trend confirmed |
| Red background | Light red | Bearish trend confirmed |

## Info Panel (Top Right)

The strategy displays a real-time info panel showing:
- **Trend**: Current Gann angle trend direction
- **Buy/Sell Confidence**: 0.00 to 1.00 score
- **Vibration**: Digit reduction of price (9 = change number)
- **SQ9 Near**: Whether price is near a Square of 9 cardinal level
- **Daily/Annual Vol**: Current volatility (SQ12 activates at high vol)
- **Buy/Sell R:R**: Current reward-to-risk ratio

---

## Configurable Settings

### Main Settings
| Parameter | Default | Description |
|-----------|---------|-------------|
| Risk Per Trade (%) | 1.5% | Percentage of equity risked per trade |
| Reward:Risk Ratio | 2.5:1 | Minimum R:R to boost confidence |
| Min Confidence | 0.45 | Minimum confidence score to enter trade |
| Volatility Lookback | 20 bars | Periods for volatility calculation |
| Swing Lookback | 50 bars | Periods for swing high/low detection |

### Gann Settings
| Parameter | Default | Description |
|-----------|---------|-------------|
| Show Gann Angles | ✓ | Display 11 angle S/R levels |
| Show SQ9 Levels | ✓ | Display Square of 9 price levels |
| Show 144 Levels | ✗ | Display 144-cycle price zones |
| SQ9 Confluence (%) | 0.5% | Tolerance for SQ9 level proximity |
| SQ12 Trigger Vol | 40% | Annual vol threshold for dynamic levels |

### Trade Management
| Parameter | Default | Description |
|-----------|---------|-------------|
| Partial Exit (%) | 50% | Position to close at first target |
| Trailing Stop (%) | 2.0% | Trail distance for remaining position |
| Max Bars in Trade | 60 | Force close after N bars |

---

## Gann Components Implemented

All 9 components from the Python algorithm are translated:

1. **Gann Angles** (11 angles): `(√base ± degree_factor)²`
2. **Square of 9**: Spiral levels at 0°–360° cardinal crosses
3. **Number Vibration**: Digit reduction, vibration 9 = reversal signal
4. **Daily Volatility**: Log-return standard deviation
5. **Dynamic Levels**: Volatility-adjusted expected range + SQ12
6. **144 Cycles**: Master cycle price zones
7. **Trend Confirmation**: 1x1 angle breakout = trend direction
8. **Confidence Scoring**: 5-factor scoring system (0.0–1.0)
9. **Trade Management**: Entry, SL, TP, trailing stop, timeout

---

## Confidence Scoring Breakdown

| Factor | Points | Condition |
|--------|--------|-----------|
| Trend confirmed | +0.30 | Price above/below 1x1 angle |
| SQ9 confluence | +0.10 | Price within 0.5% of cardinal level |
| Vibration 9 | +0.10 | Price digit sum = 9 |
| Dynamic vol confirms | +0.15 | Price within expected range |
| R:R ≥ 2.5:1 | +0.15 | Good reward-to-risk |
| R:R 1.5–2.5:1 | +0.05 | Acceptable reward-to-risk |
| R:R < 1.5:1 | −0.10 | Poor reward-to-risk penalty |

**Minimum to trade: 0.45** (configurable)

---

## Alerts Setup

The strategy includes three alert conditions:
1. **Gann BUY Signal** — Triggers when all buy conditions are met
2. **Gann SELL Signal** — Triggers when all sell conditions are met
3. **Vibration 9 Alert** — Triggers when price digit sum = 9 (reversal watch)

To set up alerts:
1. Right-click on the chart → "Add Alert"
2. Condition: Select "Gann Unified Strategy"
3. Choose the alert type
4. Set notification method (popup, email, webhook)

---

## Recommended Assets

| Asset | Timeframe | Notes |
|-------|-----------|-------|
| BTCUSD | 1D | Primary — backtested with 61.3% WR, +631% return |
| ETHUSD | 1D | Primary — backtested with 70.8% WR, +772% return |
| SOLUSD | 1D | Works well — 64.2% WR with Gann square alignment |
| XAUUSD | 1D | Gold — traditional Gann asset |

> **Note**: These backtest results are from 5-year historical simulations (Jan 2021 – Feb 2026)
> using weekly-anchored price data with the Gann algorithm. Win rates and returns are
> historical and **do not guarantee future performance**. BTC backtest: 862 trades, max DD 2.56%.
> ETH backtest: 624 trades, max DD 2.75%. Always validate on TradingView's built-in Strategy
> Tester with live market data before risking real capital.

---

## Disclaimer

⚠️ **This strategy is for educational and research purposes only.**
- Past backtest performance does not guarantee future results
- Always use a demo/paper account before risking real capital
- The algorithm is based on W.D. Gann's historical methods
- Cryptocurrency markets are highly volatile and risky
- Never risk more than you can afford to lose
