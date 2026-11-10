"""Price a researched edge through the Topstep dynamic programs.

usage: python -m research.evaluate_survivor --win_rate 0.55 --avg_win 40 --avg_loss 35 --trades_per_day 2 [--size 50K] [--n 600]
Stats are per ONE micro contract, NET of costs (as produced by research.protocol.summarize).
Prints: Combine pass probability (optimal policy), expected days, funded value over 250 days,
expected cost until pass and EV, plus a bootstrap-style uncertainty band from n trades.
"""
from __future__ import annotations

import argparse
import math

from topstep.dp_combine import CombineDP
from topstep.dp_funded import FundedDP, funded_spec_from_rules
from topstep.edge import Edge
from topstep.rules import FEES, TRADING_DAYS_PER_MONTH, combine_spec


def evaluate(win_rate: float, avg_win: float, avg_loss: float, trades_per_day: float, size: str = "50K",
             max_contracts: int = 5, horizon: int = 250, h: float = 100.0, label: str = "") -> dict:
    tpd = max(1, int(round(trades_per_day)))
    # scale per-trade magnitudes onto the $100 grid: the DP works in $ per contract, so use raw $ values but
    # a coarser grid when trades are small relative to h would discard them; choose h from avg loss.
    h_eff = 50.0 if max(avg_win, avg_loss) < 120 else 100.0
    edge = Edge(p_win=win_rate, reward=avg_win, loss=avg_loss, cost_rt=0.0, trades_per_day=tpd, name=label or "research edge")
    cs = combine_spec(size)
    cs.max_contracts = max_contracts
    cdp = CombineDP(cs, edge, h=h_eff, coarse=True)
    cdp.solve()
    P, E = cdp.evaluate(cdp.policy)
    c0 = cdp.fresh_state()
    fs = funded_spec_from_rules(size)
    fs.scaling = tuple((ub, min(l, max_contracts)) for ub, l in fs.scaling)
    fdp = FundedDP(fs, edge, h=h_eff, Bmax=6000.0, horizon=horizon, coarse=True)
    fdp.solve(keep_policies=False)
    V = float(fdp.V[fdp.fresh_state()])
    fee = FEES[(size, "standard")]
    c = fee.monthly / TRADING_DAYS_PER_MONTH
    R_pass = V - fee.activation
    cdp2 = CombineDP(cs, edge, h=h_eff, R_pass=R_pass, daily_fee=c, allow_quit=True, coarse=True)
    cdp2.solve()
    P2, E2 = cdp2.evaluate(cdp2.policy)
    p, ed = float(P2[c0]), float(E2[c0])
    cost = (c * ed + min(fee.reset, fee.monthly) * (1 - p)) / p if p > 0 else float("inf")
    return {"edge": edge.describe(), "gamma": edge.gamma, "sharpe_per_trade": edge.sharpe_per_trade,
            "sharpe_annual": edge.annual_sharpe(), "P_pass_optimal": float(P[c0]), "E_days": float(E[c0]),
            "first_action": cdp.describe_action(int(cdp.policy[c0])), "V_funded_250d": V,
            "fee_aware_P_pass": p, "expected_cost_until_pass": cost, "EV_until_pass": R_pass - cost if p > 0 else float("-inf")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--win_rate", type=float, required=True)
    ap.add_argument("--avg_win", type=float, required=True)
    ap.add_argument("--avg_loss", type=float, required=True)
    ap.add_argument("--trades_per_day", type=float, required=True)
    ap.add_argument("--size", default="50K")
    ap.add_argument("--n", type=int, default=0, help="number of holdout trades, for an uncertainty band on the win rate")
    ap.add_argument("--label", default="")
    a = ap.parse_args()
    base = evaluate(a.win_rate, a.avg_win, a.avg_loss, a.trades_per_day, a.size, label=a.label)
    for k, v in base.items():
        print(f"{k:>28}: {v:,.3f}" if isinstance(v, float) else f"{k:>28}: {v}")
    if a.n > 0:
        se = math.sqrt(a.win_rate * (1 - a.win_rate) / a.n)
        for lab, wr in (("win rate -2se", a.win_rate - 2 * se), ("win rate +2se", a.win_rate + 2 * se)):
            r = evaluate(wr, a.avg_win, a.avg_loss, a.trades_per_day, a.size, label=lab)
            print(f"{lab}: wr={wr:.3f} P_pass={r['P_pass_optimal']:.3f} V_funded={r['V_funded_250d']:,.0f} EV={r['EV_until_pass']:,.0f}")


if __name__ == "__main__":
    main()
