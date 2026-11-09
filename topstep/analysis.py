"""Full Topstep analysis for one account size: closed forms, Combine DP, funded DP,
fee-aware EV with resets, trade-level validation.  Writes results/raw/<size>_<edge>.json.

usage: python -m topstep.analysis --size 50K --edges zero_free,zero,weak,modest,strong,negative
       python -m topstep.analysis --size 50K --sweep 0.48,0.50,0.51,0.52,0.53,0.54,0.55,0.57,0.60
"""
from __future__ import annotations

import argparse
import json
import os
import time

import numpy as np

from . import closed_form as cf
from .dp_combine import CombineDP
from .dp_funded import FundedDP, funded_spec_from_rules
from .edge import PRESETS, Edge
from .rules import FEES, TRADING_DAYS_PER_MONTH, combine_spec, xfa_params
from .sim import bold_combine_policy, dp_combine_policy, dp_funded_policy, run_combine, run_funded

H_BY_SIZE = {"50K": 100.0, "100K": 100.0, "150K": 150.0}
BMAX_BY_SIZE = {"50K": 10000.0, "100K": 15000.0, "150K": 24000.0}


def analyze(size: str, edge: Edge, edge_name: str, horizon: int = 250, n_sim: int = 20000,
            dll: bool = False, validate: bool = True, log=print) -> dict:
    t0 = time.time()
    h, Bmax = H_BY_SIZE[size], BMAX_BY_SIZE[size]
    cs = combine_spec(size, dll=dll)
    T, D, kmax = cs.target, cs.mll, cs.max_contracts
    g1 = edge.gamma
    res = {"size": size, "edge": edge_name, "edge_desc": edge.describe(), "dll": dll, "horizon": horizon,
           "edge_params": dict(p_win=edge.p_win, reward=edge.reward, loss=edge.loss, cost_rt=edge.cost_rt,
                               trades_per_day=edge.trades_per_day, mu=edge.mu, sigma=edge.sigma, gamma=g1)}
    # ------------------------------------------------------------ closed forms (no consistency rule)
    k_bold = kmax if g1 < 0 else 1
    res["closed_form"] = {
        "fair_bold_bound_D_over_T_plus_D": D / (T + D),
        "one_shot_bold_at_size": {"k": k_bold, "P": cf.p_hit_upper(T, D, g1 / k_bold)},
        "continuous_timid_1_contract": cf.p_pass_topstep_continuous(T, D, g1),
        "continuous_timid_max_contracts": cf.p_pass_topstep_continuous(T, D, g1 / kmax),
        "trailing_only_exp_formula_1_contract": cf.p_target_before_trailing_drawdown(T, D, g1),
    }
    # ------------------------------------------------------------ funded account (XFA standard path)
    fs = funded_spec_from_rules(size, dll=dll)
    log(f"[{size}/{edge_name}] funded DP ...")
    fdp = FundedDP(fs, edge, h=h, Bmax=Bmax, horizon=horizon)
    fdp.solve(keep_policies=True)
    s0 = fdp.fresh_state()
    V_f = float(fdp.V[s0])
    fsim = fdp.simulate_policy(n_paths=n_sim, seed=1)
    res["funded"] = {"V_dp": V_f, "first_action": fdp.describe_action(int(fdp.policy_t[0][s0]), s0),
                     "binary_sim": {k: v for k, v in fsim.items() if k != "paid"},
                     "n_states": int(fdp.S), "n_actions": len(fdp.actions)}
    if validate:
        tv = run_funded(fs, edge, dp_funded_policy(fdp), n_accounts=n_sim, horizon=horizon, seed=2)
        res["funded"]["trade_level_sim"] = {k: v for k, v in tv.items() if k not in ("state", "busted")}
    log(f"[{size}/{edge_name}] funded V={V_f:.0f}  ({time.time()-t0:.0f}s)")
    # ------------------------------------------------------------ combine: pure pass-probability maximiser
    log(f"[{size}/{edge_name}] combine DP ...")
    cdp = CombineDP(cs, edge, h=h)
    cdp.solve()
    c0 = cdp.fresh_state()
    P_opt, E_opt = cdp.evaluate(cdp.policy)
    P_b, E_b = cdp.evaluate(cdp.policy_bold())
    P_t, E_t = cdp.evaluate(cdp.policy_timid())
    res["combine"] = {
        "optimal": {"P_pass": float(P_opt[c0]), "E_days": float(E_opt[c0]), "first_action": cdp.describe_action(int(cdp.policy[c0]))},
        "bold": {"P_pass": float(P_b[c0]), "E_days": float(E_b[c0])},
        "timid": {"P_pass": float(P_t[c0]), "E_days": float(E_t[c0])},
        "n_states": int(cdp.S), "n_actions": len(cdp.actions),
    }
    # policy map along the fresh-MLL row
    pm = []
    for b in np.arange(-D + h, T, h):
        s = cdp.state_index(b=b)
        pm.append({"b": float(b), "action": cdp.describe_action(int(cdp.policy[s])), "P": float(P_opt[s])})
    res["combine"]["policy_fresh_mll"] = pm
    if validate:
        tv = run_combine(cs, edge, dp_combine_policy(cdp), n_accounts=n_sim, max_days=600, seed=3)
        res["combine"]["trade_level_sim_optimal"] = {k: v for k, v in tv.items() if k not in ("state", "passed", "busted")}
        tb = run_combine(cs, edge, bold_combine_policy(k=kmax), n_accounts=n_sim, max_days=600, seed=4)
        res["combine"]["trade_level_sim_bold"] = {k: v for k, v in tb.items() if k not in ("state", "passed", "busted")}
    # ------------------------------------------------------------ fee-aware whole-game economics
    econ = {}
    for path in ("standard", "noaf"):
        fee = FEES[(size, path)]
        R_pass = V_f - fee.activation
        c = fee.monthly / TRADING_DAYS_PER_MONTH
        rho = min(fee.reset, fee.monthly)
        fdp2 = CombineDP(cs, edge, h=h, R_pass=R_pass, daily_fee=c, allow_quit=True)
        fdp2.solve()
        P2, E2 = fdp2.evaluate(fdp2.policy)
        p, ed = float(P2[c0]), float(E2[c0])
        V_attempt = float(fdp2.V[c0])
        quit_at_start = int(fdp2.policy[c0]) == -1
        ev_until_pass = (R_pass - (c * ed + rho * (1 - p)) / p) if p > 0 else float("nan")
        cost_until_pass = ((c * ed + rho * (1 - p)) / p) if p > 0 else float("nan")
        # with the pure P-max policy instead
        p0, ed0 = float(P_opt[c0]), float(E_opt[c0])
        ev0 = R_pass - (c * ed0 + rho * (1 - p0)) / p0 if p0 > 0 else float("nan")
        econ[path] = {"monthly": fee.monthly, "reset": fee.reset, "activation": fee.activation,
                      "R_pass": R_pass, "fee_aware_policy": {"P_pass": p, "E_days": ed, "V_attempt": V_attempt,
                                                             "quit_immediately": quit_at_start,
                                                             "first_action": fdp2.describe_action(int(fdp2.policy[c0]))},
                      "expected_cost_until_pass": cost_until_pass,
                      "EV_until_pass_fee_aware": ev_until_pass,
                      "EV_until_pass_pmax_policy": ev0,
                      "expected_trading_days_until_pass": ed / p if p > 0 else float("inf")}
    res["economics"] = econ
    res["elapsed_s"] = time.time() - t0
    log(f"[{size}/{edge_name}] done in {res['elapsed_s']:.0f}s: P_pass opt={res['combine']['optimal']['P_pass']:.3f} "
        f"V_funded={V_f:.0f} EV(std)={econ['standard']['EV_until_pass_fee_aware']:.0f}")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", default="50K")
    ap.add_argument("--edges", default="zero_free,zero,weak,modest,strong,negative")
    ap.add_argument("--sweep", default="")
    ap.add_argument("--dll", action="store_true")
    ap.add_argument("--horizon", type=int, default=250)
    ap.add_argument("--nsim", type=int, default=20000)
    ap.add_argument("--no-validate", action="store_true")
    ap.add_argument("--out", default="results/raw")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    jobs = []
    if a.sweep:
        for p in a.sweep.split(","):
            pw = float(p)
            jobs.append((f"sweep_p{pw:.3f}", Edge(pw, 100.0, 100.0, 5.0, 10, f"sweep p_win={pw:.3f}")))
    else:
        for name in a.edges.split(","):
            jobs.append((name, PRESETS[name]))
    for name, edge in jobs:
        tag = f"{a.size}_{name}{'_dll' if a.dll else ''}"
        path = os.path.join(a.out, tag + ".json")
        if os.path.exists(path):
            print("skip existing", path)
            continue
        res = analyze(a.size, edge, name, horizon=a.horizon, n_sim=a.nsim, dll=a.dll, validate=not a.no_validate)
        with open(path, "w") as f:
            json.dump(res, f, indent=1, default=float)
        print("wrote", path, flush=True)


if __name__ == "__main__":
    main()
