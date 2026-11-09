# Beating Topstep with probability theory: what is possible, what is not, and the optimal policy

This directory contains a complete mathematical treatment of the Topstep
Trading Combine → Express Funded Account → payout pipeline as a stochastic
control problem, solved exactly on the rules in force in November 2026.

| file | what it is |
|---|---|
| `docs/TOPSTEP_MATH.md` | the theory: impossibility theorem, bold/timid play, trailing-drawdown formulas, the funded-account value bound, the fee/reset economics, and the dynamic programs |
| `docs/TOPSTEP_RULES.md` | every rule parameter used, with the official source and a 2024–2026 change timeline |
| `results/summary.md` | all numbers: pass probabilities (closed form, DP, trade-level simulation), funded-account values, EV until pass, break-even edge, optimal policy maps, figures |
| `topstep/` | the code: closed forms, exact day-P&L model, Combine DP (policy iteration), XFA DP (backward induction), trade-level Monte Carlo, analysis and report scripts, tests |

## The answer in one paragraph

Nothing in futures trading can "always" secure a pass, a profit or a
withdrawal, and that is a theorem, not a disclaimer: for a trader without
an edge the pass probability of any strategy is at most D/(T+D) (40% on a
50K Combine, 33% on 100K/150K), and the expected lifetime payout of a funded
account is at most the drawdown allowance (net $1,800 on a 50K), whatever the
timing of trades and withdrawals.  What probability theory *can* do is (1)
compute the exact optimal daily policy under the real rules (55% consistency
target, end-of-day trailing MLL that locks, 5 winning days of $150+, 50% of
balance up to $2,000 per payout, MLL reset to $0 after each payout, scaling
plan, fees and resets), (2) make passing a *certainty* by resets at a
computable expected cost, and (3) locate the break-even edge below which the
whole Topstep game has negative expectation no matter how it is played.
The rules turn out to be a well-designed filter against the strategy that is
mathematically optimal for a no-edge trader (bold play), and the Responsible
Trading Program targets exactly that behaviour; a trader with a real edge
should instead play timidly in the Combine and treat the XFA as a capped
annuity, withdrawing on the first eligible day.

## Reproduce

```bash
pip install numpy scipy matplotlib pytest
python -m pytest -q topstep/tests            # ~5 min; add -m slow for the brute-force checks
python -m topstep.analysis --size 50K        # one JSON per edge preset in results/raw/
python -m topstep.analysis --size 50K --sweep 0.48,0.50,0.52,0.54,0.56
python -m topstep.compare_paths --size 50K   # Standard vs Consistency payout path
python -m topstep.report                     # results/summary.md + figures
```

Use your own trade statistics:

```python
from topstep.edge import Edge
from topstep.rules import combine_spec
from topstep.dp_combine import CombineDP
from topstep.dp_funded import FundedDP, funded_spec_from_rules

me = Edge(p_win=0.54, reward=150, loss=100, cost_rt=3.78, trades_per_day=8)   # per ES contract
dp = CombineDP(combine_spec("50K"), me); dp.solve()
P, E = dp.evaluate(dp.policy); s0 = dp.fresh_state()
print(P[s0], E[s0], dp.describe_action(int(dp.policy[s0])))
f = FundedDP(funded_spec_from_rules("50K"), me, horizon=250); f.solve()
print(f.V[f.fresh_state()])                     # expected net payouts in 250 trading days
```

All of this is position sizing, stop/target selection and payout timing —
nothing in it touches Topstep's prohibited-conduct list (cross-account
hedging, account stacking, simulator exploitation, copy trading others,
VPNs), which the rules document spells out and which forfeit everything when
detected.
