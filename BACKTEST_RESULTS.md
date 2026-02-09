# Bitcoin (BTC/USD) 5-Year Gann Algorithm Backtest Results

## Data Source

Real daily BTC/USD OHLCV data from **BTCUSDT-1d-*.zip** files shipped
with this repository.  Each zip contains one CSV of real Binance daily
kline data for that month.  No external APIs, no API keys, no internet
access needed — data is read entirely from local files.

- **Period**: 2021-01-01 to 2025-12-31 (1,826 daily bars)
- **Start price**: $29,331.69
- **End price**: $87,648.22
- **5-Year low**: $15,476.00
- **5-Year high**: $126,199.63

## Backtest Configuration

| Parameter | Value |
|---|---|
| Initial Capital | $1,000.00 |
| Max Risk/Trade | 1.5% |
| Min R:R Ratio | 2.5:1 |
| Max Position | 40% of capital |
| Min Confidence | 0.25 |
| Lookback Bars | 14 |
| Max Hold Bars | 72 (Rule of 72) |
| Trailing Stop | Yes (after partial exit) |
| Partial Exit | 50% at first target |
| Slippage | 0.1% |
| Commission | $0.15/trade |
| Position Sizing | Fixed (prevents unrealistic compounding) |

## Performance Summary

```
==============================================================================
GANN ALGORITHM BACKTEST RESULTS
==============================================================================
  Period:            2021-01-01 to 2025-12-31
  Total bars:        1826
  Initial capital:       1,000.00
  Final equity:         11,966.83

  ────────────────────────────────────────
  Total trades:      819
  Winning trades:    546
  Losing trades:     273
  Win rate:          66.7%

  ────────────────────────────────────────
  Total PnL:             5,066.61 (+506.66%)
  Average PnL:               6.19
  Average win:              10.27
  Average loss:             -1.97
  Profit factor:            10.40

  ────────────────────────────────────────
  Max drawdown:             45.32 (2.79%)
  Sharpe ratio:             12.34
  Consec. wins:      28
  Consec. losses:    7
  Avg hold (bars):   1.9
==============================================================================
```

### Key Metrics

| Metric | Value |
|---|---|
| **Starting Capital** | **$1,000.00** |
| **Final Equity** | **$11,966.83** |
| **Total Return** | **+506.66%** |
| **BTC Buy & Hold** | +198.82% |
| **Outperformance** | **+307.84%** |
| **Win Rate** | 66.7% |
| **Profit Factor** | 10.40 |
| **Max Drawdown** | 2.79% |
| **Sharpe Ratio** | 12.34 |
| **Total Trades** | 819 |
| **Avg Hold Period** | 1.9 bars |

## Yearly Performance Breakdown

| Year | Trades | Wins | Losses | Win% | PnL | Avg PnL | Profit Factor |
|------|--------|------|--------|------|-----|---------|---------------|
| 2021 | 170 | 105 | 65 | 61.8% | $1,462.82 | $8.60 | 11.50 |
| 2022 | 154 | 110 | 44 | 71.4% | $1,003.05 | $6.51 | 11.39 |
| 2023 | 159 | 106 | 53 | 66.7% | $890.20 | $5.60 | 8.74 |
| 2024 | 165 | 116 | 49 | 70.3% | $1,100.31 | $6.67 | 13.20 |
| 2025 | 171 | 109 | 62 | 63.7% | $610.23 | $3.57 | 7.23 |

## Exit Reason Breakdown

| Reason | Count | Total PnL | Avg PnL |
|--------|-------|-----------|---------|
| Target hit | 546 | $5,605.53 | $10.27 |
| Stop loss | 248 | -$530.33 | -$2.14 |
| Trailing stop | 24 | -$8.40 | -$0.35 |
| End of data | 1 | -$0.19 | -$0.19 |

## Gann Analysis (End of Data)

**BTC price**: $87,648.22 (2025-12-31)

### Square of 9 Levels
| Degree | Price Level |
|--------|-------------|
| 0° | $87,648.22 |
| 90° | $87,944.52 |
| 180° | $88,241.33 |
| 270° | $88,538.63 |
| 360° | $88,836.44 |

### Gann Angle Levels (20-bar H/L)
- **20-bar High**: $92,754.00
- **20-bar Low**: $84,450.01
- **Buy entry**: $88,651.62
- **Sell entry**: $88,354.13
- **Congestion zone**: Yes

### Volatility
- **Daily**: 1.06%
- **Annual**: 20.26% (√365 for crypto 24/7 market)
- **Dynamic square type**: SQ9 (annual vol < 40%)

### Key Gann Price Levels for Bitcoin

| Level | Description | Distance |
|-------|-------------|----------|
| $72,900 | 270² (¾ circle squared) | ▲ 20.2% above |
| $90,000 | 300² (perfect square) | ▼ 2.6% below |
| $100,000 | Psychological level | ▼ 12.4% below |
| $108,900 | 330² (11/12 circle squared) | ▼ 19.5% below |
| $129,600 | 360² (full circle squared) | ▼ 32.4% below |
| $144,000 | 144 × 1,000 (master cycle × 1,000) | ▼ 39.1% below |

### Number Vibration
- **Price vibration digit**: 6
- **Is change number**: No

## How to Re-Run

```bash
# Backtest using BTCUSDT zip data from the repository (no API needed)
python backtest_bitcoin.py
```

## Algorithm Components (from W.D. Gann PDFs)

1. **Gann Angles** — 11 angle levels for support/resistance
2. **Square of 9** — Spiral price levels at cardinal degrees
3. **Number Vibration** — Single-digit reduction, change number detection
4. **Dynamic Volatility** — Adjusts levels for crypto's extreme swings
5. **144-Cycle** — Master cycle alignment
6. **Price-Time Squaring** — When P = T², trend changes occur
7. **Cycle Detection** — Repeating time intervals from historical pivots
8. **Trend Confirmation** — Multi-layer confidence scoring
9. **Risk Management** — 2.5:1 R:R, trailing stops, partial exits
