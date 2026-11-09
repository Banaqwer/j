# Topstep rules as verified on 2026-11-09

Every parameter the model uses, with the official source it was read from.
Topstep changes rules often (see the timeline at the end); re-verify before
relying on any number.  "Official" = help.topstep.com / topstep.com page
fetched on 2026-11-09; dates in brackets are the page's own "updated" date
where it shows one.  Community sources are marked as such.

## 1. Trading Combine (the evaluation)

| parameter | 50K | 100K | 150K | source |
|---|---|---|---|---|
| starting balance | $50,000 | $100,000 | $150,000 | [Combine Parameters](https://help.topstep.com/en/articles/8284197-trading-combine-parameters) (2026-09-24) |
| profit target | $3,000 | $6,000 | $9,000 | [Consistency at Topstep](https://help.topstep.com/en/articles/8284208-consistency-at-topstep) (2026-09-17) |
| Maximum Loss Limit (MLL) | $2,000 | $3,000 | $4,500 | [What is the MLL](https://help.topstep.com/en/articles/8284204-what-is-the-maximum-loss-limit) (2026-09-18) |
| max position | 5 minis / 50 micros | 10 / 100 | 15 / 150 | Combine Parameters |
| subscription, Standard path | $49 / 30 days | $99 | $199 | [Pricing](https://help.topstep.com/en/articles/14289835-topstep-pricing-and-payment-questions) (2026-10-15) |
| subscription, No-Activation-Fee path | $95 | $149 | $229 | Pricing |
| reset | same as the subscription price for that path | | | Pricing, [What is a Reset](https://help.topstep.com/en/articles/8284128-what-is-a-reset) (2026-09-25) |
| optional Daily Loss Limit (set at checkout, fixed for life) | $1,000 | $2,000 | $3,000 | [DLL article](https://help.topstep.com/en/articles/10490293-daily-loss-limit-in-the-trading-combine-and-express-funded-account) (2026-06-30) |

Rules and mechanics:

* **The only rule**: "Do not let your account balance hit or go below the
  Maximum Loss Limit."  The MLL **trails the end-of-day balance** at the
  distance above, never falls, and **locks permanently once it reaches the
  starting balance** (i.e. once an EOD balance has been at least +MLL above
  start).  It is **monitored in real time including unrealized P&L**; a touch
  liquidates the account and a realized balance back above the limit does not
  undo it.  Official example: start $50,000 / MLL $48,000; +$500 day → MLL
  $48,500; −$500 next day → MLL stays $48,500. (MLL article; Labs FAQ
  explicitly contrasts "EOD trailing" with "static".)
* **Objective 1**: reach (and hold at the close) the profit target.
* **Objective 2, Consistency Target (55%)**: "Your single best day of profit
  must stay at or below 55% of your Profit Target. If it exceeds that, your
  Profit Target increases" to *best day ÷ 0.55*.  "55% is a hard line. It is
  not rounded, and there is no buffer."  Best day locks at 3:10 PM CT; losses
  never shrink the recorded best day.  Consequence: a one-day pass is
  impossible; two days minimum.  (Consistency article, Combine Parameters.)
  This replaced a 50%-with-buffer objective in September 2026 (community-dated).
* **No time limit, no minimum days**: the subscription rebills every 30 days
  until you pass or cancel; each rebill grants one Reset Credit; resets are
  limited to 2 per account per calendar day; there is no limit on the number
  of Combines, but "excessive purchases of Trading Combines or Resets" and
  "account stacking" are Prohibited Conduct.  ([Subscriptions](https://help.topstep.com/en/articles/8284121-trading-combine-subscriptions) 2026-10-12, [Reset limits](https://help.topstep.com/en/articles/10370307-reset-purchase-limits) 2026-06-18)
* **Breach**: account liquidated and ineligible for funding until Reset; the
  subscription keeps billing.  A Reset restores balance, MLL, consistency
  target and day count and pushes the rebill date 30 days out.
* **Session**: trading day 5:00 PM CT → 3:10 PM CT; all positions flat by
  3:10 PM CT (flattening starts 3:08); CME Group products only.
* **Commissions in SIM** (deducted from Net P&L, so they count against the
  target, MLL and best day): minis $1.00 RT + exchange + $0.02 NFA; all-in
  ES $3.78, MES $1.22, NQ $3.78, MNQ $1.22, CL $4.02, GC $4.32 per round turn
  ([Commissions](https://help.topstep.com/en/articles/8284213-what-are-the-commissions-and-fees), 2026-09-30).
* **Tier-1 news**: no new positions in minis (equity index, metals) during
  the 10-minute window around CPI, FOMC, NFP, PPI; micros capped at 3/6/9.
  "Purposefully trading your full Maximum Position Size directly into a
  scheduled major news event" is a prohibited strategy.
* **Topstep's own 2025 statistics**: 16.8% of Combines passed; 51.8% of
  participants reached the funded level at least once; 33.3% of funded
  participants received a payout; 0.71% of XFA traders were called up to a
  Live Funded Account; "63% of traders lost their Combine on day 1".

## 2. Express Funded Account (XFA) — the simulated funded stage

| parameter | 50K | 100K | 150K | source |
|---|---|---|---|---|
| activation | $149 once (Standard path) / $0 (No-Activation-Fee path); no monthly fee | | | [XFA Activation](https://help.topstep.com/en/articles/8284217-express-funded-account-activation) (2026-09-24) |
| starting balance / buying power | $0 / $50K | $0 / $100K | $0 / $150K | [XFA Parameters](https://help.topstep.com/en/articles/8284215-express-funded-account-parameters) (2026-11-03) |
| MLL | starts −$2,000 | −$3,000 | −$4,500 | MLL article |
| MLL behaviour | trails EOD, locks at $0 once balance reaches +MLL; **set to $0 permanently after the first payout** | | | MLL article, [Payout Policy](https://help.topstep.com/en/articles/8284233-topstep-payout-policy) (2026-11-03) |
| Scaling Plan (max lots by balance) | <$1,500: 2 · $1,500–2,000: 3 · >$2,000: 5 | 3 / 4 / 5 / 10 (>$3,000) | 3 / 4 / 5 / 10 / 15 (>$4,500) | [Scaling Plan](https://help.topstep.com/en/articles/8284223-what-is-the-scaling-plan) (2026-07-16) |
| optional DLL | $1,000 | $2,000 | $3,000 | DLL article |
| max simultaneous XFAs | 5 (sizes may be mixed; balances never combined) | | | XFA Parameters |
| Back2Funded (reactivate an XFA lost before its first payout, ≤2 times, within 30 days) | $599 | $699 | $829 | [Back2Funded](https://help.topstep.com/en/articles/12060405-back2funded-rules-guidelines-and-how-it-works) (2026-09-29) |

Two payout paths, chosen at activation and locked:

| | Standard path | Consistency path |
|---|---|---|
| eligibility per payout | **5 winning days** of **$150+ Net P&L** (non-consecutive; a day locks at 4:00 PM CT; the request day does not count toward the next 5) | **3 trading days** with ≥1 trade each and **largest winning day ≤ 40% of total net profit** in the payout window |
| after the first payout | also **≥ $0.01 net profit since the last payout** | consistency and 3-day count reset each payout |
| max per request | 50% of balance, up to **$2,000 / $3,000 / $5,000** (50K/100K/150K) | 50% of balance, up to **$3,000 / $4,000 / $6,000** |
| with a DLL added at Combine checkout (offer from 2026-06-02, still shown) | caps doubled: $4,000 / $6,000 / $10,000 | $6,000 / $8,000 / $12,000 |
| minimum request | $125 | $125 |
| split | trader keeps **90%** (traders who joined the new dashboard before 2026-01-12: 100% of first $10,000 lifetime, then 90%) | same |
| after each payout | MLL → $0 permanently; 5-day count restarts; scaling tier may drop | MLL → $0; consistency resets; 3-day count restarts |

Other XFA facts: no 30-winning-day milestone exists in the XFA any more (it
lives only in the Live account); XFAs inactive >30 days may be closed; the
trade copier across one's own accounts is allowed up to $750K buying power,
cross-account hedging is not; the Combine balance does not carry over.

## 3. Live Funded Account (real capital, discretionary)

Promotion is a Risk-Team decision ("isn't automatic — it's earned"; 0.71% of
XFA traders in 2025).  One LFA at a time; its size is the average tier of
the trader's payout-eligible XFAs rounded up; 20% of the transferred balance
(min $10,000) is tradable, 80% sits in Reserve released in four 25% steps at
profit milestones ($3,000 on a 50K); mandatory DLL ($2,000 on 50K); payouts
uncapped (50% of balance per request, 5 winning days of $150+), daily
payouts of up to 100% after 30 Live winning days; liquidation if the balance
falls below $1,000; call-down ("shoulder tap") back to a simulated XFA is at
Topstep's discretion.  ([LFA Parameters](https://help.topstep.com/en/articles/10657969-live-funded-account-parameters), [Call-up/call-down](https://help.topstep.com/en/articles/13747178-live-funded-account-call-up-and-call-down-process), [Dynamic Live Risk Expansion](https://help.topstep.com/en/articles/11748475-dynamic-live-risk-expansion))

## 4. Prohibited conduct relevant to "beating the system"

From the [Terms of Use](https://www.topstep.com/terms-of-use) (2026-11-04,
§27–28), [Prohibited Conduct](https://help.topstep.com/en/articles/10296582-prohibited-conduct),
[Understanding Hedging](https://help.topstep.com/en/articles/13747047-understanding-hedging) (2026-07-27),
[Prohibited Trading Strategies](https://help.topstep.com/en/articles/10305426-prohibited-trading-strategies-at-topstep) (2026-06-10),
[Responsible Trading Program](https://help.topstep.com/en/articles/13620045-what-is-the-responsible-trading-program):

* **Cross-account hedging** — opposite positions in the same or correlated
  instrument (ES/MES, NQ/MNQ) across any of one's accounts, or in concert with
  other people ("coordinated trading"): detected in real time, forced
  liquidation, flagged, tracked at trader level, eventually permanent closure
  with forfeiture of balances; "confirmed hedging violations are final and
  cannot be appealed".
* **Account stacking** — repeatedly hitting the MLL in one account and
  switching to another for more high-risk attempts; **excessive purchases of
  Combines or Resets**; "excessive use of XFAs and trading irresponsibly within them".
* **Exploiting the simulator** — SIM fills, queue position, slippage, gaps,
  "high volume of trades within short periods"; price/data-feed errors; slow
  or external data feeds; HFT; "software, AI, ultra-high speed, or mass data
  entry which might manipulate, abuse, or give User an unfair advantage";
  trading "inconsistent with real futures markets".
* **One profile per person**, identity verification, no VPN/VPS/proxy, orders
  must originate from a personal device, no trading on behalf of others.
* **Catch-all**: anything Topstep "in its sole discretion" deems "uncommercial,
  games the market, is not a viable strategy, or is not responsible trading".
* **Responsible Trading Program** (triggers: "multiple accounts hit the MLL in
  one day", "you max position a majority of your trades", no stops, losers
  larger than winners, tilt/FOMO): new accounts get a mandatory DLL and only
  the Consistency XFA (40% best-day rule); Standard XFA unavailable until the
  trader makes $10,000 in a Live account.  The **Focused Trader Program**
  limits repeat offenders to one $50K account.
* Consequences range from warning, deletion of a trading day and reset to
  permanent closure, denial of payouts and forfeiture; no refunds.

Permitted: automated strategies via the TopstepX API ($29/month) in
Combine/XFA (not Live), copying trades across one's own accounts, any
position sizing and stop/target choice within the Scaling Plan.

## 5. Timeline of changes that matter for the model (2024 → 2026)

| date | change | source |
|---|---|---|
| 2024-08-27 | DLL removed from new/reset TopstepX accounts (later re-introduced as an optional add-on) | official X post |
| 2024-12-06 | XFA payouts: 50% of balance, max $5,000 per request | official X post |
| 2025-07-07 | all new Combines on TopstepX only | official X post |
| 2025-07-29 | winning-day threshold $200 → $150 | official X post |
| 2025-07 | XFA winning days no longer count toward the Live 30-day milestone | Payout Policy |
| 2025-11-24 | two funding paths (Standard / No-Activation-Fee) | official |
| 2025-12-30 | repeat payouts need positive net profit since the last payout (community-dated; rule confirmed officially) | Payout Policy |
| 2026-01-12 | 90/10 split from the first dollar for new traders | Payout Policy |
| 2026-02-05 | XFA Standard vs Consistency (40%) payout paths | official X post, blog |
| 2026-02-10 | Live account restructure (20% tradable / 80% reserve, one LFA) | LFA Parameters |
| 2026-03-31 | Responsible Trading Program: mandatory DLL + Consistency XFA | official X post |
| 2026-04 | commissions re-introduced on all simulated accounts | official blog 2026-04-30 |
| 2026-04-28 | XFA per-request caps cut from flat $5K/$6K to $2K/$3K/$5K (Std) and $3K/$4K/$6K (Cons.) by size (community-dated; current official values) | Payout Policy |
| 2026-06-02 | DLL at checkout doubles XFA payout caps (limited-time, still live) | Payout Policy |
| 2026-09 | Combine consistency objective 50% → 55% hard line, target rises to best day ÷ 0.55 | Consistency article (2026-09-17) |
| 2026-11-05 | Topstep Labs "Daily Payouts+" experimental 50K products (one-time fee, daily payouts) | official blog |

## 6. Independent verification

A separate 21-agent research-and-verification pass (six research sweeps, two
adversarial verifier lenses per topic, one synthesis) produced
`TOPSTEP_RULES_VERIFIED.md` (4,700 words, every number with a source key and
confidence) and `topstep_rules_verified.json`.  None of its 30 listed
uncertainties changes a parameter used by the model; the ones that touch the
model are listed below.

## 7. Known inconsistencies / open points

* The XFA Parameters page still says "up to $5,000 / $6,000" per request
  while the Payout Policy (and Pro Account page) give the tiered caps; the
  model uses the tiered caps ($2,000 for a 50K Standard XFA), which the
  Payout Policy states explicitly ("Max Payout per request: 50% of your
  account balance up to the cap below").
* Winning/consistency days "lock in at 4:00 PM CT" (Payout Policy) vs the
  Combine best day locking at 3:10 PM CT (Consistency article); immaterial for
  the model (one bookkeeping point per day).
* Several third-party pages still quote a 50% Combine consistency rule, a
  $200 winning day, "+$100" MLL lock offsets or 30-winning-day XFA payouts;
  all are stale.
* The exact wording of the Trader Pledge could not be fetched (404).
* Whether a best day at *exactly* 55% of profit passes is unresolved across
  official pages ("below" vs "at or below"); the model uses "at or below",
  which matters only on a grid point.
* The XFA MLL-breach timing is "immediate" on the MLL page and "closed at end
  of day" in the XFA FAQ; the model uses immediate (the stricter reading).
* The double-payout-cap offer has no published end date and can be withdrawn.

