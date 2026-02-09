# 🚀 How to Use the Gann Strategy in TradingView

## Step-by-Step (Takes 5 Minutes)

---

### STEP 1: Open TradingView

1. Go to **https://www.tradingview.com**
2. Create a free account (or log in if you have one)
3. Click **"Chart"** at the top menu

---

### STEP 2: Pick Your Asset

1. In the **search bar** at the top-left of the chart, type:
   - `BTCUSD` for Bitcoin
   - `ETHUSD` for Ethereum
   - `SOLUSD` for Solana
   - `XAUUSD` for Gold
2. Click the result (pick any exchange — Coinbase, Binance, etc.)
3. Change the timeframe to **1D** (Daily):
   - Look at the top toolbar — click where it says "1H" or "4H"
   - Select **"1D"**

---

### STEP 3: Open Pine Editor

1. Look at the **bottom** of the screen
2. You'll see tabs: "Strategy Tester", "Pine Editor", etc.
3. Click **"Pine Editor"**
4. A code editor opens at the bottom

---

### STEP 4: Paste the Strategy Code

1. In the Pine Editor, **select all** existing code (Ctrl+A) and **delete** it
2. Open the file `gann_tradingview_strategy.pine` from this repository
3. **Copy everything** in that file (Ctrl+A, then Ctrl+C)
4. **Paste** it into the Pine Editor (Ctrl+V)
5. Click the **"Add to Chart"** button (or press Ctrl+Enter)
   - It's the blue/purple button above the code editor

✅ **You should now see colored lines and triangles on your chart!**

---

### STEP 5: See the Backtest Results

1. Click the **"Strategy Tester"** tab at the bottom
2. You'll see three sub-tabs:
   - **Overview** → Shows net profit, win rate, profit factor
   - **Performance Summary** → Detailed stats (max drawdown, avg trade, etc.)
   - **List of Trades** → Every single trade with entry/exit prices and P/L
3. This is TradingView backtesting your strategy on **real historical data**

---

### STEP 6: Enable Paper Trading (Demo Account)

This lets the strategy trade **automatically** on a demo account (no real money):

1. In the **Strategy Tester** tab, look for the **three dots menu** (⋯) at the top-right
2. Click it → Select **"Paper Trading"** or **"Forward Testing"**
3. TradingView will now automatically:
   - Open BUY/SELL positions when the Gann algorithm signals
   - Track your P/L in real-time
   - Send you notifications

⚠️ **Paper Trading = Fake money. No risk. Perfect for testing.**

---

### STEP 7: Set Up Alerts (Optional)

Get notified on your phone/email when the strategy signals:

1. **Right-click** anywhere on the chart
2. Select **"Add Alert..."**
3. In the alert dialog:
   - Condition: Select **"Gann Unified Strategy"**
   - Choose: **"Gann BUY Signal"** or **"Gann SELL Signal"**
4. Set notification: App notification, Email, or Webhook
5. Click **"Create"**

Now you'll get alerts even when you're not watching the chart!

---

## 📖 What You'll See on the Chart

After adding the strategy, your chart will show:

| What You See | What It Means |
|-------------|---------------|
| 🟢 Green triangle pointing UP | **BUY signal** — algorithm says go long |
| 🔴 Red triangle pointing DOWN | **SELL signal** — algorithm says go short |
| Green line above price | Gann 1x1 (45°) resistance |
| Red line below price | Gann 1x1 (45°) support |
| Blue + marks | Square of 9 price levels (above) |
| Purple + marks | Square of 9 price levels (below) |
| Teal shaded zone | Expected daily volatility range |
| Green background | Bullish trend confirmed |
| Red background | Bearish trend confirmed |

---

## 📊 Info Panel (Top Right Corner)

The strategy shows a live dashboard in the top-right:

```
Trend: ▼ BEARISH        ← Current direction
Buy Conf: 0.15          ← Buy confidence (0 to 1)
Sell Conf: 0.72         ← Sell confidence (0 to 1)
Vibration: 5            ← Price vibration number
SQ9 Near: YES           ← Near a key Gann level?
Daily Vol: 3.2%         ← Today's volatility
Annual Vol: 61%         ← Yearly volatility
Buy R:R: 1.8            ← Reward-to-risk for buys
Sell R:R: 3.1           ← Reward-to-risk for sells
```

---

## ⚙️ Settings You Can Change

Click the **gear icon** (⚙️) next to the strategy name on the chart to change:

| Setting | Default | What It Does |
|---------|---------|-------------|
| Risk Per Trade | 1.5% | How much to risk per trade |
| Reward:Risk Ratio | 2.5 | Minimum profit-to-loss ratio |
| Min Confidence | 0.45 | Higher = fewer but better trades |
| Swing Lookback | 50 | More bars = wider Gann angles |
| Partial Exit | 50% | Close half position at first target |
| Trailing Stop | 2.0% | Trail the remaining position |
| Max Bars in Trade | 60 | Auto-close after 60 days |

**Tip**: Start with defaults. Only change after you understand the results.

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Add to Chart" doesn't work | Make sure you copied ALL the code from the `.pine` file |
| No signals appearing | Change timeframe to **1D** (Daily). Won't work on 1m/5m/1H. |
| "Study error" message | Make sure you deleted the old code first before pasting |
| Strategy Tester is empty | Click "Strategy Tester" tab at bottom, not "Pine Editor" |
| Signals look wrong | Click ⚙️ → reset all settings to defaults |
| "Too many instruments" error | Free TradingView accounts have limits — use one chart at a time |

---

## 💡 Quick Summary

```
1. Go to tradingview.com
2. Open BTCUSD chart, set to 1D timeframe
3. Open Pine Editor (bottom of screen)
4. Paste the code from gann_tradingview_strategy.pine
5. Click "Add to Chart"
6. Check Strategy Tester for backtest results
7. Enable Paper Trading for live demo execution
8. Set up alerts to get notified on your phone
```

**That's it! You're now running the Gann algorithm live on TradingView.** 🎉

---

## ⚠️ Important Disclaimer

This strategy is for **educational and research purposes only**.
- Past performance does not guarantee future results
- Always start with **Paper Trading** (demo) — never real money first
- Cryptocurrency and financial markets carry significant risk
- Never invest more than you can afford to lose
- This is based on W.D. Gann's historical methods, not guaranteed predictions
