# Topstep as a stochastic control problem

*A rigorous treatment of the Topstep Trading Combine, Express Funded Account and
payout policy as a barrier-hitting / optimal-stopping problem, with exact
numerical solutions.  Rules are the official ones in force in November 2026
(see `TOPSTEP_RULES.md`).  All code is in `topstep/`; every number in the
results section is reproducible with `python -m topstep.analysis`.*

---

## 0. The short answer

**No strategy can "always" secure a pass, a profit or a withdrawal.** That is
not an opinion: it is Theorem 1 below, and it holds for every strategy a human
or an algorithm can execute, including strategies that vary size, stop early,
or pick instruments.  What probability theory *does* give is sharper and more
useful than a promise:

1. An exact **upper bound on the pass probability** of any no-edge trader
   (40.0% on a 50K, 33.3% on a 100K or 150K), and the strategy that attains it.
2. An exact **upper bound on what the funded account can ever pay** a no-edge
   trader (gross expectation at most the drawdown allowance: $2,000 / $3,000 /
   $4,500; net of the 90/10 split: $1,800 / $2,700 / $4,050), however the
   payouts are timed.
3. The **optimal policy** (daily target, daily stop, size, when to request a
   payout) for any given edge, computed by dynamic programming on the real rule
   set (end-of-day trailing MLL that locks at the starting balance, 55%
   consistency target, 5 winning days of $150+, 50%-of-balance payout cap of
   $2,000, MLL reset to $0 after each payout, scaling plan, fees and resets).
4. The **expected cost of passing with certainty** (resets make a pass a
   certainty, at a computable price), and therefore the **break-even edge**:
   the smallest per-trade edge at which the whole Topstep game (fees, resets,
   activation, capped payouts) has non-negative expected value.

The structural result is that Topstep's rule set is a well-designed
*anti-bold-play* filter: the mathematically optimal no-edge strategy is bold
play (maximum size, few bets), and the consistency target, winning-day
requirement, payout cap, MLL reset and the Responsible Trading Program are each
aimed at exactly that strategy.  A trader with no edge who plays optimally is
left with a small, bounded expected value; a trader with a genuine edge should
play *timidly* in the Combine and treat the funded account as a capped annuity.

---

## 1. The game, stated precisely

Let $X_t$ be the trader's cumulative **net** P&L (after commissions) in one
account, $t$ counting trading days.  Topstep's parameters for a 50K account
(100K, 150K in brackets):

| object | symbol | value |
|---|---|---|
| profit target | $T$ | 3,000 (6,000, 9,000) |
| maximum loss limit distance | $D$ | 2,000 (3,000, 4,500) |
| MLL rule | | trails the **end-of-day** balance at distance $D$, never falls, **locks at the starting balance** once the EOD balance reaches $+D$; breach is evaluated in real time including open P&L |
| consistency target | $s$ | best single day $\le 0.55 \times$ (adjusted) target, i.e. you pass only when profit $\ge \max(T,\ \text{best day}/0.55)$ |
| size cap | $k_{\max}$ | 5 (10, 15) minis |
| subscription | $f$ | $49 ($99, $199) per 30 days, Standard path; reset $49 ($99, $199); XFA activation $149 |
| XFA (Standard path) | | balance starts at $0, MLL starts at $-D$, trails EOD, locks at 0; payout needs 5 winning days of $\ge$ $150, $\le 50\%$ of balance, $\le$ $2,000 ($3,000, $5,000), $\ge$ $125, trader keeps 90%; after each payout the MLL is set to $0 permanently and the day count restarts; scaling plan 2/3/5 lots below $1,500 / to $2,000 / above |

A **strategy** is any non-anticipating rule for position size (including zero)
as a function of everything observed so far.  "Passing" is the event that the
balance reaches the adjusted target while the MLL has never been touched.

### 1.1 The P&L model and the only parameter that matters

Trades are i.i.d. with per-contract mean $\mu_1$ and standard deviation
$\sigma_1$ (net of costs).  With $k$ contracts the P&L per trade has mean
$k\mu_1$ and variance $k^2\sigma_1^2$.  In the diffusion approximation $X$ is a
Brownian motion with drift $\mu$ and volatility $\sigma$, whose *scale
function* is $s(x) = e^{-\gamma x}$ with

$$\gamma \;=\; \frac{2\mu}{\sigma^2} \;=\; \frac{2\mu_1}{k\,\sigma_1^2}\qquad[\$^{-1}].$$

Every barrier-hitting probability depends on $(\mu,\sigma)$ only through
$\gamma$.  Doubling the size halves $\gamma$: **larger size makes any game look
fairer** (closer to $\gamma=0$), which is the whole reason bold play helps a
losing trader and hurts a winning one.

For a binary trade model (win $R$ with probability $p$, lose $L$ otherwise,
cost $c$ per round turn): $\mu_1 = pR-(1-p)L-c$ and
$\sigma_1^2 = pR^2+(1-p)L^2-(pR-(1-p)L)^2$.  Reference edges used throughout
(ES, $R=L=\$100$ per contract, $c=\$5$):

| name | $p$ | $\mu_1$ | $\sigma_1$ | $\gamma$ per contract | annualised Sharpe (10 trades/day) |
|---|---|---|---|---|---|
| zero edge, no costs | 0.50 | 0 | 100 | 0 | 0 |
| zero edge (coin flip after costs) | 0.50 | $-5$ | 100 | $-0.0010$ | $-2.5$ |
| weak | 0.53 | $+1$ | 99.8 | $+0.0002$ | $+0.5$ |
| modest | 0.55 | $+5$ | 99.5 | $+0.0010$ | $+2.5$ |
| strong | 0.60 | $+15$ | 98.0 | $+0.0031$ | $+7.7$ |
| negative | 0.47 | $-11$ | 99.8 | $-0.0022$ | $-5.5$ |

(An annualised Sharpe of 2.5 from 10 scalps a day is already a very good
discretionary trader; "strong" is well beyond what most funded traders show.)

---

## 2. Theorem 1 — nothing is certain, and the no-edge ceiling is $D/(T+D)$

**Theorem 1.** Suppose the trader has no edge, i.e. $X$ is a supermartingale
(fair or costly trading), and the trader uses *any* strategy.  Then

$$\mathbb P(\text{pass}) \;\le\; \frac{D}{T+D},$$

with equality only for a fair game and a strategy that stops exactly at $+T$
or $-D$ with nothing in between (one-shot **bold play**).  In particular no
strategy passes with probability 1, and with the 55% consistency target the
bound is not attainable at all.

*Proof.* Let $\tau$ be the first time the account passes or busts (possibly
$\infty$).  While alive the balance is above the MLL, and the MLL is never
below $-D$, so $Y_n := X_{\tau\wedge n} + D \ge 0$ is a non-negative
supermartingale with $\mathbb E Y_n \le D$.  On $\{\text{pass}\}$,
$\lim Y_n \ge T + D$.  By Fatou,
$(T+D)\,\mathbb P(\text{pass}) \le \mathbb E[\liminf Y_n] \le \liminf \mathbb E Y_n \le D$.
Equality needs $X$ to be a true martingale (no costs), $Y_\tau \in \{0, T+D\}$
a.s. (no overshoot, bust exactly at $-D$) and $\tau<\infty$ a.s.: the
one-shot bet.  The consistency target forbids a one-day pass, so the
inequality is strict.  $\square$

Numerically: 50K $\to 0.400$, 100K $\to 0.333$, 150K $\to 0.333$.  Topstep's
published 2025 statistic that 16.8% of Combines pass is consistent with a
population that is mostly no-edge and far from optimal.

**Corollary 1.1 (costs).** With commissions the game is strictly subfair; for
one-shot bold play with $k$ contracts the pass probability is the gambler's
ruin value

$$P_{\text{bold}}(k)=\frac{1-e^{-\gamma_k D}}{1-e^{-\gamma_k (T+D)}},\qquad \gamma_k=\gamma_1/k,$$

which increases toward $D/(T+D)$ as $k\to\infty$ when $\gamma_1<0$: a losing
trader should bet as large as the rules allow.  The Topstep size cap is thus a
binding constraint on the no-edge optimum.

---

## 3. Theorem 2 — bold when you are losing, timid when you are winning

**Theorem 2** (Dubins–Savage 1965 for red-and-black; Pestien–Sudderth 1985 for
diffusions). To maximise the probability of reaching a goal before ruin, a
player whose game is *subfair* ($\mu\le0$) should play **boldly** (maximal
stake each time), and a player whose game is *superfair* ($\mu>0$) should play
**timidly**: in the diffusion model the optimal control maximises
$\mu/\sigma^2$ over the admissible sizes, and for linear sizing that is the
*smallest* size when $\mu_1>0$ and the *largest* when $\mu_1<0$.  Under timid
play with $\mu>0$ the pass probability tends to 1 as the size tends to 0, at
the cost of an expected time that tends to infinity.

Consequences for Topstep:

* **No edge:** bold play (5 minis, one or two decisive days).  This is exactly
  the behaviour listed as a trigger of Topstep's Responsible Trading Program
  ("maxing position on most trades", "multiple accounts hitting MLL in one
  day") and is capped by the 55% consistency target.
* **Positive edge:** small size, many days.  The Combine then becomes a race
  between a pass probability that rises toward 1 and the monthly fee; Section 6
  solves that trade-off exactly.

---

## 4. Theorem 3 — the trailing drawdown and the Topstep lock

For a *continuously* trailing drawdown of size $D$ (the MLL follows the
running maximum), the probability that the running maximum reaches $+T$ before
the drawdown from the maximum exceeds $D$ is (Taylor 1975, Lehoczky 1977)

$$P_{\text{trail}}(T,D,\gamma)=\exp\!\Big(-\frac{\gamma T}{e^{\gamma D}-1}\Big),\qquad P_{\text{trail}}(T,D,0)=e^{-T/D}.$$

*Derivation.* When the maximum sits at level $m$ the process must reach
$m+dm$ before $m-D$, which has probability
$1-\tfrac{\gamma e^{-\gamma D}}{1-e^{-\gamma D}}dm + o(dm)$; the product of
$T/dm$ such factors gives the exponential.

Topstep's MLL trails only the **end-of-day** balance and **locks** once it
reaches the starting balance, i.e. once the running EOD maximum reaches $+D$.
Hence, in the continuous limit,

$$P_{\text{Topstep,timid}} = \underbrace{\exp\!\Big(-\frac{\gamma D}{e^{\gamma D}-1}\Big)}_{\text{max reaches } D \text{ before a } D\text{-drawdown}} \times \underbrace{\frac{1-e^{-\gamma D}}{1-e^{-\gamma (T-D)}\,e^{-\gamma D}}}_{\text{then } +T \text{ before } 0}\!\!,
\qquad \gamma=0:\ e^{-1}\,\frac{D}{T}.$$

For a fair game that is **24.5%** on a 50K and **18.4%** on a 100K/150K —
compared with **40.0% / 33.3%** for one-shot bold play.  Timid play *costs* a
no-edge trader 15 points of pass probability because the trailing MLL
ratchets away the cushion.  (EOD trailing is gentler than continuous
trailing; the exact discrete values are produced by the DP and verified by
simulation.)  Topstep's "Static" Labs accounts remove the ratchet entirely,
which is why their targets are higher.

---

## 5. The exact solution: a dynamic program on the real rules

Closed forms stop at the consistency target, the EOD granularity, the size
cap and the fee clock.  The package solves the real problem exactly.

**State** (end of day): balance $b$, MLL $M$, required profit
$r=\max(T,\ \text{best day}/0.55)$, (day count).  **Action**: a daily profit
target $\Delta$ and daily stop $\Lambda$ on a $100 grid; the contract size is
chosen by the Theorem-2 rule inside the size cap (smallest size whose bet
resolves within the session with probability $\ge 0.9$ when $\gamma_1\ge0$,
largest size when $\gamma_1<0$).  The day's P&L then has the **exact
distribution of the stopped trade walk** — up to 10 trades of $+k(R-c)$ /
$-k(L+c)$, stopped at $\ge+\Delta$ or $\le-\Lambda$ — computed on the trade
lattice, including overshoot and sessions that end unresolved, and mapped to
the grid by mean-preserving rounding (so no commission is ever "rounded
away").  The MLL then updates as $M'=\min(0,\max(M,b'-D))$; a day whose P&L
reaches the MLL is a bust; a day that brings $b'\ge r$ (and satisfies the day
count) is a pass.  This day model reproduces a trade-by-trade Monte Carlo of
the same policies to within sampling error (`topstep/tests`, `results/`).

**Objective**: $\max\ \mathbb E[R_{\text{pass}}\mathbf 1_{\text{pass}} - c\cdot\text{days}]$,
where $c$ is the subscription per trading day and $R_{\text{pass}}$ the value
of a pass (the funded-account value minus the activation fee); with
$R_{\text{pass}}=1, c=0$ it is the pure pass-probability maximiser.  Solved by
Howard policy iteration with exact sparse policy evaluation (≈30,000 states,
≈200 actions, a few seconds).

**Funded account**: state $(b, M, \text{ref}, w)$ with ref the balance after
the last payout (for the "positive profit since last payout" rule) and $w$
the winning-day count; actions add *request payout*; the scaling plan makes
the size cap state-dependent; MLL is set to 0 after each payout; objective
$\max \mathbb E[\sum \text{payouts}]$ over a 250-trading-day horizon by backward
induction (≈74,000 states, ≈200 actions, each with its exact day-P&L distribution).  Both programs are validated against a trade-level
Monte Carlo that simulates every trade (overshoot, unresolved days, intraday
MLL touches) — see `topstep/tests/`.

**Theorem 4 (the funded account is worth at most $D$ to a no-edge trader).**
If $X$ is a supermartingale, then for any trading and payout policy
$\mathbb E[\text{total gross payouts}] \le D$.
*Proof.* Balance $= X_t - W_t$ where $W_t$ is cumulative payouts; while the
account is alive the balance is above the MLL $\ge -D$, so $X_{t\wedge\tau}+D\ge W_{t\wedge\tau}\ge0$,
and $X_{t\wedge\tau}+D$ is a non-negative supermartingale with mean $\le D$;
Fatou gives $\mathbb E W_\infty \le D$. $\square$
So the Standard-path 50K XFA is worth at most $0.9\times 2{,}000 = \$1{,}800$
net to a no-edge trader, *before* the 5-winning-day, 50%, $2,000-cap and
MLL-reset frictions; the DP computes what those frictions leave.

---

## 6. The whole game: fees, resets and the price of certainty

Let a Combine attempt have pass probability $P$ and expected length
$E_d$ trading days under the chosen policy; subscription $c=f/21$ per trading
day; reset price $\rho$ (a bust is cured by a reset, or by the free monthly
reset credit); value of a pass $R_{\text{pass}} = V_{\text{XFA}} - a$ with
activation fee $a$.  Because a busted Combine is reset to day one and attempts
are independent, the number of attempts until the first pass is geometric
with mean $1/P$, so

$$\mathbb E[\text{cost until pass}] = \frac{c\,E_d + \rho\,(1-P)}{P},\qquad
\text{EV}_{\text{until pass}} = R_{\text{pass}} - \frac{c\,E_d + \rho\,(1-P)}{P}.$$

Two things follow.  **Passing can be made certain** — any trader with $P>0$
who keeps resetting passes with probability 1 — but at an expected price, and
that price is what "securing the evaluation" means mathematically.  And the
**break-even edge** is the $\gamma_1$ at which
$\text{EV}_{\text{until pass}}=0$; below it the Combine is a negative-expectation
product however it is played, above it the fee-aware policy of Section 5 is
the right way to play it.

---

## 7. What the optimal policies look like

(Numbers for the 50K Standard path, ES with $R=L=\$100$, $5 round turn,
10 trades per day; full tables in Section 9 and `results/`.)

* **No edge, pure pass maximiser.** Day 1: target $+1{,}500$ with a $200 stop
  at 5 minis — a small-loss, high-payoff bet repeated until it hits, keeping
  the best day under the 55% line; day 2: the remaining $1{,}500$.  Pass
  probability 23.5%, i.e. the consistency target removes 16.5 points from the
  40% bound.  The expected number of trading days is large because the policy
  ignores the fee clock.
* **No edge, fee-aware.** The daily fee makes the DP prefer faster resolution
  and makes it *quit* from states whose continuation value is below the fee
  burn; the EV of the whole game is small but — because resets are cheap —
  can be slightly positive on paper.  That paper value is exactly the
  behaviour Topstep's Responsible Trading Program is built to catch
  (mandatory DLL, Consistency-path XFA with a 40% best-day rule, review of
  "maxing position"), so it is not a reliable income.
* **Positive edge.** The DP keeps size at 1 contract and uses moderate daily
  targets; pass probability rises steeply with $\gamma_1$ and the fee-aware
  policy never quits.  In the XFA the optimal payout policy is "request the
  first payout the day you become eligible, then rebuild"; waiting for a
  bigger balance is wrong because the cap is 50% of balance and the MLL
  resets to 0 after the first payout anyway.

---

## 8. What is *not* a strategy

* **Cross-account hedging** (opposite positions in several Combines/XFAs so
  that "one must pass") is Prohibited Conduct, enforced in real time with
  forced liquidation and permanent closure with forfeiture of profits, and is
  tracked at trader level.  Mathematically it does not even beat Theorem 1 per
  dollar of fees: $n$ hedged accounts cost $n$ subscriptions and the combined
  P&L is still a supermartingale.
* **Account stacking / excessive resets**, exploiting SIM fills, latency,
  data-feed errors, copy trading other people's accounts, VPN use: all
  prohibited; detection removes all accumulated value.
* **Martingale / doubling** inside one account is just bold play with extra
  steps; it cannot beat the $D/(T+D)$ ceiling.

Everything in this document is within the rules: it is position sizing,
stop/target selection and payout timing.

---

## 9. Results

See `results/summary.md` (generated by `python -m topstep.report`) for the
full tables: pass probabilities (closed form, DP, trade-level simulation),
funded-account values, EV until pass under both fee paths, the break-even
sweep and the optimal policy maps.

---

## References

* Dubins, L. & Savage, L. (1965). *How to Gamble If You Must: Inequalities for Stochastic Processes.*
* Pestien, V. & Sudderth, W. (1985). Continuous-time red and black: how to control a diffusion to a goal. *Math. Oper. Res.* 10, 599–611.
* Taylor, H. (1975). A stopped Brownian motion formula. *Ann. Probab.* 3, 234–246.
* Lehoczky, J. (1977). Formulas for stopped diffusion processes with stopping times based on the maximum. *Ann. Probab.* 5, 601–607.
* Grossman, S. & Zhou, Z. (1993). Optimal investment strategies for controlling drawdowns. *Math. Finance* 3, 241–276.
* Kelly, J. (1956). A new interpretation of information rate. *Bell Syst. Tech. J.* 35, 917–926.
* Williams, D. (1991). *Probability with Martingales* (optional stopping, Fatou).
