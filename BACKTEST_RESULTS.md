# Bitcoin (BTC/USD) 5-Year Gann Algorithm Backtest Results

## Data Source

Real daily BTC/USD OHLCV data sourced via the **Binance public API** (primary)
or **CoinGecko free API** (fallback). No API keys required — uses only standard
library `urllib` and `json`. Falls back to cached `btc_real_daily.csv` when
offline.

- **Period**: 2021-02-01 to 2026-02-09 (1,835 daily bars)
- **Start price**: $35,181.40
- **End price**: $139,732.85
- **5-Year low**: $14,815.63
- **5-Year high**: $143,499.46

## Backtest Configuration

| Parameter | Value |
|---|---|
| Initial Capital | $100,000.00 |
| Max Risk/Trade | 1.5% |
| Min R:R Ratio | 2.5:1 |
| Max Position | 40% of capital |
| Min Confidence | 0.25 |
| Lookback Bars | 14 |
| Max Hold Bars | 72 (Rule of 72) |
| Trailing Stop | Yes (after partial exit) |
| Partial Exit | 50% at first target |
| Slippage | 0.1% |
| Commission | $15/trade |
| Position Sizing | Fixed (prevents unrealistic compounding) |

## Performance Summary

```
==============================================================================
GANN ALGORITHM BACKTEST RESULTS
==============================================================================
  Period:            2021-02-01 to 2026-02-09
  Total bars:        1835
  Initial capital:     100,000.00
  Final equity:      1,480,439.23

  ────────────────────────────────────────
  Total trades:      867
  Winning trades:    524
  Losing trades:     343
  Win rate:          60.4%

  ────────────────────────────────────────
  Total PnL:           630,099.96 (+630.10%)
  Average PnL:             726.76
  Average win:           1,330.67
  Average loss:           -195.84
  Profit factor:            10.38

  ────────────────────────────────────────
  Max drawdown:          3,955.87 (2.56%)
  Sharpe ratio:             12.04
  Consec. wins:      22
  Consec. losses:    18
  Avg hold (bars):   1.9
==============================================================================
```

### Key Metrics

| Metric | Value |
|---|---|
| **Total Return** | **+630.10%** |
| **BTC Buy & Hold** | +297.18% |
| **Outperformance** | **+332.92%** |
| **Win Rate** | 60.4% |
| **Profit Factor** | 10.38 |
| **Max Drawdown** | 2.56% |
| **Sharpe Ratio** | 12.04 |
| **Total Trades** | 867 |
| **Avg Hold Period** | 1.9 bars |

## Yearly Performance Breakdown

| Year | Trades | Wins | Losses | Win% | PnL | Avg PnL | Profit Factor |
|------|--------|------|--------|------|-----|---------|---------------|
| 2021 | 143 | 102 | 41 | 71.3% | $177,268.10 | $1,239.64 | 25.97 |
| 2022 | 161 | 107 | 54 | 66.5% | $130,109.76 | $808.14 | 11.27 |
| 2023 | 163 | 106 | 57 | 65.0% | $118,259.43 | $725.52 | 9.60 |
| 2024 | 182 | 117 | 65 | 64.3% | $141,173.84 | $775.68 | 12.21 |
| 2025 | 196 | 82 | 114 | 41.8% | $55,961.92 | $285.52 | 3.94 |
| 2026 | 22 | 10 | 12 | 45.5% | $7,326.91 | $333.04 | 4.68 |

## Exit Reason Breakdown

| Reason | Count | Total PnL | Avg PnL |
|--------|-------|-----------|---------|
| Target hit | 523 | $695,023.67 | $1,328.92 |
| Stop loss | 317 | -$66,263.74 | -$209.03 |
| Trailing stop | 26 | -$910.00 | -$35.00 |
| End of data | 1 | $2,250.03 | $2,250.03 |

## Gann Analysis (Current Price)

**Current BTC price**: $139,732.85 (2026-02-09)

### Square of 9 Levels
| Degree | Price Level |
|--------|-------------|
| 0° | $139,732.85 |
| 90° | $140,106.91 |
| 180° | $140,481.47 |
| 270° | $140,856.53 |
| 360° | $141,232.08 |

### Gann Angle Levels (20-bar H/L)
- **20-bar High**: $143,499.46
- **20-bar Low**: $120,605.48
- **Buy entry**: $132,113.04
- **Sell entry**: $131,749.82
- **Congestion zone**: Yes

### Volatility
- **Daily**: 2.02%
- **Annual**: 38.65% (√365 for crypto 24/7 market)
- **Dynamic square type**: SQ9 (annual vol < 40%)

### Key Gann Price Levels for Bitcoin

| Level | Description | Distance |
|-------|-------------|----------|
| $100,000 | Psychological level | ▲ 39.7% above |
| $108,900 | 330² (11/12 circle squared) | ▲ 28.3% above |
| $129,600 | 360² (full circle squared) | ▲ 7.8% above |
| $144,000 | 144 × 1,000 (master cycle × 1,000) | ▼ 3.0% below |

### Number Vibration
- **Price vibration digit**: 7
- **Is change number**: No

## Trade Log (First 50 Trades)

```
      Date   Dir      Entry       Exit         SL        PnL    PnL% Bars  Exit Reason  Conf
2021-02-15   BUY   46324.39   55818.99   46134.80    4084.30  20.42%    2       target  0.30
2021-02-17   BUY   46956.65   56673.51   46765.46    4123.41  20.62%    2       target  0.30
2021-02-19   BUY   50412.26   61691.87   50212.40    4460.18  22.30%    2       target  0.30
2021-02-21   BUY   50801.93   50550.50   50601.10    -113.99  -0.57%    3         stop  0.30
2021-02-24  SELL   54042.17   51836.13   54406.83     801.46   4.01%    2       target  0.30
2021-02-26  SELL   53607.54   46245.78   53970.52    2731.67  13.66%    2       target  0.55
2021-02-28  SELL   52624.53   42650.87   52983.67    3775.49  18.88%    2       target  0.45
2021-03-02  SELL   52624.53   53036.66   52983.67    -171.63  -0.86%    3         stop  0.45
2021-03-06   BUY   52959.88   52700.99   52753.74    -210.54  -0.53%    1         stop  0.45
2021-03-07   BUY   52750.12   56114.65   52544.49    1260.66   6.30%    2       target  0.55
2021-03-09   BUY   51470.40   59274.69   51267.93    3017.35  15.09%    2       target  0.45
2021-03-11   BUY   51831.99   59838.38   51628.62    3074.26  15.37%    2       target  0.45
2021-03-13   BUY   54068.49   65640.16   53859.65    4265.36  21.33%    2       target  0.30
2021-03-15   BUY   56141.45   55871.67   55927.60    -111.11  -0.56%   11         stop  0.45
2021-03-26  SELL   62328.80   57906.12   62724.68    1404.24   7.02%    2       target  0.45
2021-03-28  SELL   61743.27   61805.01   62136.99     -35.00  -0.17%    2     trailing  0.45
2021-03-30   BUY   59899.22   59616.74   59676.41    -203.64  -0.51%    1         stop  0.30
2021-03-31   BUY   59899.22   63282.89   59676.41    1114.81   5.57%    2       target  0.30
2021-04-02   BUY   59225.94   63234.60   59004.72    1338.72   6.69%    2       target  0.45
2021-04-04   BUY   59989.39   65130.00   59766.37    1698.88   8.49%    2       target  0.45
2021-04-06   BUY   62030.99   66986.58   61803.18    1582.68   7.91%    5       target  0.40
2021-04-11   BUY   62848.38   65545.67   62618.66     843.41   4.22%    2       target  0.30
2021-04-13   BUY   63536.65   63242.02   63305.33    -200.50  -0.50%    1         stop  0.45
2021-04-14  SELL   64324.55   62902.40   64727.72     427.15   2.14%    2       target  0.40
2021-04-16  SELL   62547.05   56934.16   62943.73    1779.72   8.90%    2       target  0.30
2021-04-18  SELL   62528.04   57234.29   62924.65    1678.21   8.39%    2       target  0.45
2021-04-20  SELL   60623.50   54833.19   61013.08    1895.22   9.48%    2       target  0.45
2021-04-22  SELL   57925.78   50824.54   58305.27    2436.70  12.18%    2       target  0.30
2021-04-24  SELL   57925.78   50206.89   58305.27    2649.95  13.25%    2       target  0.45
2021-04-26  SELL   57685.02   58121.66   58063.60    -166.39  -0.83%    3         stop  0.45
2021-04-29   BUY   54957.93   58131.32   54746.93    1139.80   5.70%    2       target  0.40
2021-05-01   BUY   54018.28   57432.60   53809.56    1249.15   6.25%    2       target  0.45
2021-05-03   BUY   54545.25   58706.66   54335.25    1510.78   7.55%    2       target  0.55
2021-05-05   BUY   54545.25   59953.03   54335.25    1967.76   9.84%    2       target  0.45
2021-05-07   BUY   54545.25   59733.50   54335.25    1887.27   9.44%    2       target  0.45
2021-05-09   BUY   54545.25   54280.91   54335.25    -111.92  -0.56%    2         stop  0.45
2021-05-11  SELL   54735.95   53851.00   55103.28     308.36   1.54%    2       target  0.30
2021-05-13  SELL   54216.19   48524.29   54581.52    2084.74  10.42%    2       target  0.30
2021-05-15  SELL   53217.03   46360.12   53578.49    2561.83  12.81%    2       target  0.45
2021-05-17  SELL   51346.02   42467.32   51700.14    3443.25  17.22%    2       target  0.30
2021-05-19  SELL   48483.20   37684.81   48825.91    4439.34  22.20%    2       target  0.30
2021-05-21  SELL   46634.86   33814.95   46970.06    5482.82  27.41%    2       target  0.30
2021-05-23  SELL   45045.83   30807.36   45374.49    6306.88  31.53%    2       target  0.30
2021-05-25  SELL   43654.84   32168.93   43977.71    5247.27  26.24%    2       target  0.45
2021-05-27  SELL   39708.41   34232.01   40014.43    2743.19  13.72%    2       target  0.45
2021-05-29  SELL   37950.82   35366.76   38249.13    1346.80   6.73%    2       target  0.45
2021-05-31  SELL   37950.82   36788.41   38249.13     597.59   2.99%    2       target  0.45
2021-06-02   BUY   34403.40   36541.39   34245.55    1227.92   6.14%    2       target  0.45
2021-06-04   BUY   33501.62   35264.68   33346.30    1037.55   5.19%    2       target  0.45
2021-06-06   BUY   33501.62   35632.38   33346.30    1257.06   6.29%    2       target  0.45
```

## How to Re-Run

```bash
# Auto-downloads from Binance → CoinGecko → cached CSV
python backtest_bitcoin.py

# Or pre-download data first
python download_btc_data.py
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
