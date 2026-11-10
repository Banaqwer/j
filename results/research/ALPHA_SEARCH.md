# Alpha search: intraday BTC/ETH edges tradable on Topstep (MBT / MET)

*Run on 2026-11-10 on Binance USDT-M perpetual data (1-minute bars, funding,
5-minute open-interest and positioning metrics, 2020-01 to 2026-10), under
`research/protocol.py`: Topstep hours (Sunday 17:00 CT to Friday 15:10 CT,
daily break 15:10 to 17:00 CT), CME micro contract costs (MBT $2.82 + $1.00
slippage per round turn, MET $0.72 + $0.20), signals acted on at the next bar
open, in-sample 2020-01-01 to 2024-06-30, holdout 2024-07-01 to 2026-10-31
sealed.  Twelve hypothesis families, each pre-specified by an independent
agent, 196 logged variants, survivor bar: net mean > 0, t ≥ 2.5, n ≥ 150,
net P&L positive in at least 3 calendar years.  Raw results:
`alpha_search_raw.json`, per-family JSON in `research/hyp/` and this directory.*

## Result

**Zero of 196 variants met the bar, so nothing reached the holdout.**  The
best net t-statistic with n ≥ 150 was +2.07.  For roughly 130 effectively
independent trials the expected maximum of pure-noise t-statistics is about
3.1, so the best result sits *below* the noise ceiling: this is what a search
over zero-edge signals with a fixed cost drag looks like.  A protocol defect
found by the synthesis (the forced-flat check had no upper bound and closed
evening-session positions one bar after entry unless an agent patched it)
was fixed and all twelve family scripts were re-run; every family's own
screen still reports no qualifying variant.

| family | variants | best variant (n ≥ 150 unless noted) | n | net $/contract | t | note |
|---|---|---|---|---|---|---|
| range_breakout | 15 | US-session 30-min opening-range breakout, wide-range filter, range stop, flat at close | 659 | +5.58 | 2.07 | post-hoc mirror of a losing filter; 2020 = −$740; deflated-Sharpe p 0.62 |
| funding_signal | 20 | fade 180-day 95th-percentile funding, 8-hour hold | 307 | +7.49 | 1.56 | 2021-driven; DSR p 0.37 |
| funding_signal | 20 | short when funding ≥ 0.1%/8h, 4-hour hold | 63 | +26.8 | 2.57 | all P&L in 2021, no signals 2022–24 |
| positioning_metrics | 19 | follow 4-hour open-interest build (z ≥ 2) with ≥1% move, hold 4h | 201 | +6.57 | 1.65 | 3 years of OI data; relaxed and ETH versions do not confirm |
| calendar_events | 15 | fade the last hour before monthly options expiry, 4-hour hold | 54 | +18.9 | 1.37 | 54 events |
| weekend_monday | 15 | follow a ≥1% weekend gap from the Sunday open to Monday close | 126 | +16.1 | 1.20 | plain gap-follow t 1.08 in session_drift |
| session_drift | 21 | long BTC Europe session (02:00 to 08:30 CT) | 1173 | +1.31 | 0.62 | gross +$5.13 (t 2.4) killed by cost; negative 2020 and 2022 |
| intraday_momentum | 15 | day-so-far sign → last UTC hour, |z| ≥ 1 | 315 | +2.13 | 1.02 | regression t 7.5 but +9 bp conditional |
| vwap_reversion | 18 | best pre-specified: 2.5σ band from UTC-day VWAP | 283 | +0.36 | 0.09 | |
| vol_regime_reversal | 15 | every variant net negative | | | | 3σ down-move reversal exists but sits in the daily break and weekends |
| taker_imbalance | 13 | every variant net negative | | | | reversal relation t −13 cost-free, +0.4 $/contract gross |
| cross_asset_leadlag | 14 | every variant net negative | | | | ETH/BTC lead-lag +2 to +4 bp gross |
| volume_time_seasonality | 16 | hour × weekday cells selected on 2020–22, scored on 2022–24 | 234 | −0.95 | −0.17 | no cell survives its own out-of-sample test |

## Why the result is "no", and the dot that connects it

Every real relation the search found is 1 to 10 basis points per event.
That is not nothing: several are statistically unmistakable in regression
form (day-so-far → last hour continuation t ≈ 7.5 in both BTC and ETH;
opening-range continuation +25 bp at 12 hours, t 3.0; rising open interest
confirms the trend; fading extreme funding is weakly positive and following
it reliably negative; the strongest positive hour of the day is 16:00 to
17:00 CT, which sits inside the CME daily break where no position may be
held).  They are untradable **at this contract's cost-to-notional ratio**:
one MBT is 0.1 BTC, so $3.82 per round turn is 6 to 38 bp of notional
depending on the year, and one MET is worse (25 to 100+ bp); every ETH
variant in every family was net negative.  The same 5 to 10 bp effect on an
ES contract ($3.78 on roughly $325,000 of notional, about 0.1 bp) would be
$160 to $325 gross per contract against $3.78 of cost.  The intraday
continuation effects found here are the same family documented in equity
index futures (Gao, Han, Li and Zhou 2018), where the cost ratio is fifty
times better; they could not be tested in this sandbox because free
intraday index futures data was not reachable.

## What would be a legitimate next step

1. A second, pre-registered family on the regression-level relations with
   holds long enough to amortise the fixed cost (multi-hour to full-session,
   BTC only, large conditional moves), deflated for the 196 prior trials.
2. The same protocol on ES/MES intraday data (paid or a sample), where the
   cost structure gives the same effects room to be positive.
3. Only then open the holdout, once, on whatever qualifies.

What should **not** be done is to promote any near-miss above to the
holdout: with 196 trials behind them, a holdout t ≥ 1.5 for one of them is
likely by chance, and it would contaminate the sealed window for a real
second round.

## Pricing any future survivor

`python -m research.evaluate_survivor --win_rate W --avg_win A --avg_loss L --trades_per_day T --n N`
feeds holdout trade statistics into the Topstep dynamic programs (50K,
5-contract micro cap) and prints pass probability, funded value, expected
cost until pass and EV, with a ±2 standard-error band on the win rate.  The
smoke test shows the band matters: a hypothetical 54% edge at 2 trades/day
prices at EV ≈ +$3,000, but at 49% (two standard errors on 400 trades) it is
not worth buying.
