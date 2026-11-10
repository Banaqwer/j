# Alpha search, rounds 2 and 3: pre-registered crypto session-hold rules and documented equity-index effects on ES

*Continuation of `ALPHA_SEARCH.md` (round 1: 12 families, 196 variants on BTC/ETH, zero survivors).
Run on 2026-11-10.  Raw results: `alpha_round2_raw.json`, `alpha_es_raw.json`; scripts in
`research/hyp/r2_*.py` and `research/hyp/es_*.py`; the one holdout test in
`research/verify/es_month_end_short_holdout.py`.*

## Round 2: BTC, session-long holds to amortise the micro-contract cost

Four families, 15 variants fixed before any result was seen, in-sample 2020-01 to 2024-06,
MBT costs ($3.82 per round turn), deflated for the 196 prior trials on the same data
(ledger after this round: 211).  Survivor bar: net mean > 0, t ≥ 2.5, n ≥ 150, positive
in ≥ 3 of 5 calendar periods.

| family | variants | best variant | n | net $/MBT | t | positive periods |
|---|---|---|---|---|---|---|
| session_continuation | 5 | fade the overnight move at 08:30 CT when |z| ≥ 1, hold to 15:08 | 260 | +3.37 | 0.57 | 2/5 |
| orb_long_hold | 4 | US 30-min opening-range breakout, range stop, hold to close | 1144 | +2.14 | 1.18 | 3/5 |
| oi_trend_long_hold | 3 | follow a 4-hour open-interest build with a ≥1% move, hold to close | 122 | +11.42 | 1.26 | 3/3 (2022–24 only) |
| funding_fade_long_hold | 3 | fade 95th-percentile funding to the next settlement | 893 | +0.77 | 0.33 | 2/5 |

Nothing nominated; the highest t-statistic was 1.26 and the highest deflated-Sharpe
probability 0.067.  Two of the premises ran the wrong way in-sample: day-so-far
*continuation* at |z| ≥ 0.5 is a significant *reversal* (t = −2.01), and an evening
opening-range breakout held overnight is significantly negative (t = −2.03, 73% of trades
stopped out).  The open-interest result does not survive its own neighbourhood (the adjacent
parameter setting doubles the sample and flips the mean to −$5.29).  The holdout was not opened.

## Round 3: ES, six documented effects, 13 in-sample years

Data: Oanda S&P 500 CFD one-minute bars 2005-01 to 2020-05 (timestamps verified UTC against
an independent series to the point), ES economics ($50 per point, $16.28 per round turn
including one tick of slippage), Topstep hours with the overnight session holdable.
In-sample 2005 to 2017; sealed holdout 2018-01 to 2020-05 (Feb 2018, Dec 2018 and the 2020
crash).  22 variants pre-registered.  Survivor bar: net mean > 0, t ≥ 2.5, n ≥ 150,
positive in ≥ 8 of 13 years.

| family (literature) | variants | best variant | n | net $/ES | t | positive years |
|---|---|---|---|---|---|---|
| intraday momentum (Gao, Han, Li, Zhou 2018) | 5 | first-60-min sign → last 30 min | 3158 | −8.74 | −2.15 | 4/13 |
| overnight drift (Lou, Polk, Skouras 2019) | 4 | long 17:00→08:30 CT after a down cash day | 1136 | +9.29 | 0.74 | 9/13 |
| opening-range breakout | 4 | 30-min range, wide-range filter, range stop | 1525 | −14.01 | −1.02 | 5/13 |
| pre-FOMC drift (Lucca, Moench 2015) | 3 | long 17:00 CT day before → 12:55 CT statement day | 102 | +125.19 | 2.88 | 8/13 |
| calendar flows | 3 | turn-of-month long, four session legs | 603 | +7.79 | 0.26 | 7/13 |
| VWAP reversion | 3 | 0.30% band, low-range days | 3135 | −25.57 | −7.00 | 1/13 |

Findings worth recording:

* **Intraday momentum does not exist in this data.** Gross means are within a few dollars of
  zero for all five variants; the realised last-half-hour return correlates −0.05 with the first
  half-hour (opposite sign to the published result).  The Nasdaq-100 twin gives the same null.
* **The overnight premium exists but is tiny on the proxy**: +$18 gross per night per ES
  contract (0.36 points), which the round turn consumes; and the cash session itself was
  positive on average 2005 to 2017, so the "short the day" leg loses reliably (t = −3.0).
* **The pre-FOMC drift is real and dead.** +$219 per event, t = 3.56 for the 55 statements in
  the 13:15 CT era (2005 to January 2013); −$35, t = −0.54 for the 39 statements from March
  2013 to 2017.  It could never meet the 150-trade rule (104 statements exist), and its
  disappearance before the holdout starts is why the holdout was not opened for it.
* **Opening-range breakouts do not continue** on average (gross ≈ 0; 2008 is the only strong
  year), and **VWAP excursions continue rather than revert** (stops hit 1.8 times as often as
  the target, losing before costs in every year 2005 to 2016).
* **Month-end last hour.** Going long the last hour of the last trading day of the month lost
  −$88.73 per contract with t = −3.94, negative in 12 of 13 years including 2013 to 2017,
  consistent with documented month-end rebalancing flows.  Its short mirror was not
  pre-registered and so could not be nominated; it was the strongest, most stable signal in all
  three rounds.

## The one holdout opening

Criterion stated before running: short ES at 14:00 CT on the last NYSE trading day of each
month, exit 15:08 CT; confirmed if net mean > 0, t ≥ 1.0 (power-adjusted for ~28 events) and
at least 3 of 5 half-years positive.  Result on 2018-01 to 2020-05, 28 events:

| statistic | value |
|---|---|
| mean net per ES contract | −$132 |
| t | −0.76 |
| win rate | 39% |
| half-years positive | 1 of 5 (2018H1 only) |
| long version, same window | +$100, t = 0.57 |

Not confirmed.  (The last event, 2020-05-13, is an artefact of the data ending mid-month;
excluding it leaves the mean at about −$97 and the verdict unchanged.)  The holdout has now
been opened for exactly one candidate and should be treated as spent for that rule.

## Ledger and conclusion

| round | instrument | variants | best t (n ≥ 150) | survivors | holdout opened |
|---|---|---|---|---|---|
| 1 | BTC/ETH | 196 | 2.07 | 0 | no |
| 2 | BTC | 15 | 1.26 | 0 | no |
| 3 | ES | 22 | 2.17 (0.74 with a positive mean) | 0 | once, failed |

233 pre-registered trading rules across two asset classes and 20 years of minute data, each
run with the exact Topstep hours and contract costs, produced no rule that a trader could
take into a Combine with evidence of a positive expectation.  The two effects with genuine
historical support, the pre-FOMC drift and the month-end rebalancing move, are documented
in the academic literature, were visible in this data, and are gone: the first after 2013,
the second in the 2018 to 2020 holdout.  That is the expected life cycle of a published
anomaly, and it is the strongest argument in this whole project for the conclusion of
`docs/TOPSTEP_MATH.md`: the sizing and payout policy can be solved exactly, but the edge has
to come from somewhere the public record does not reach.
