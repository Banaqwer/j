"""Standard vs Consistency XFA payout path, and the effect of the optional DLL,
evaluated in the trade-level simulator with simple fixed daily policies
(the DP covers the Standard path exactly; this script answers the path choice).

usage: python -m topstep.compare_paths --size 50K --edges zero,modest,strong
"""
from __future__ import annotations

import argparse
import itertools
import json
import os

import numpy as np

from .dp_funded import FundedSpec
from .edge import PRESETS
from .rules import xfa_params
from .sim import run_funded


def spec_from(size: str, path: str, dll: bool) -> FundedSpec:
    p = xfa_params(size, path, dll)
    return FundedSpec(size=size, mll=p["mll"], lock_at=p["lock_at"], win_threshold=p["win_threshold"],
                      w_required=p["w_required"], cap_share=p["cap_share"], cap_abs=p["cap_abs"],
                      min_payout=p["min_payout"], split=p["split"], scaling=p["scaling"],
                      daily_loss_limit=p["daily_loss_limit"], consistency_share=p["consistency_share"],
                      path=path, name=f"XFA {size} {path}{' +DLL' if dll else ''}")


def fixed_with_payout(delta: float, lam: float, k: int):
    """Trade (+delta/-lam, k lots) every day; request a payout on any day the account is eligible."""
    def pol(st, spec):
        n = st.b.size
        d = np.full(n, float(delta)); l = np.full(n, float(lam)); kk = np.full(n, int(k))
        A = np.minimum(spec.cap_share * st.b, spec.cap_abs)
        elig = (st.w >= spec.w_required) & (st.b > 0) & (A >= spec.min_payout)
        if spec.require_profit_since_last_payout:
            elig &= (~st.had_payout) | (st.b > st.ref)
        if spec.consistency_share:
            wp = st.b - st.ref
            elig &= (wp > 0) & (st.best <= spec.consistency_share * wp)
        d[elig] = 0.0
        return d, l, kk
    return pol


def best_fixed(spec, edge, n=6000, horizon=250, seed=0):
    grid_d = [200, 300, 500, 800, 1000, 1500, 2000]
    grid_l = [100, 200, 300, 500, 800, 1000, 1500, 2000]
    grid_k = sorted({l for _, l in spec.scaling})
    best = None
    for d, l, k in itertools.product(grid_d, grid_l, grid_k):
        if spec.daily_loss_limit is not None and l > spec.daily_loss_limit:
            continue
        r = run_funded(spec, edge, fixed_with_payout(d, l, k), n_accounts=n, horizon=horizon, seed=seed)
        if best is None or r["mean_payout"] > best["mean_payout"]:
            best = {"delta": d, "lam": l, "k": k, "mean_payout": r["mean_payout"], "p_any_payout": r["p_any_payout"],
                    "p_bust": r["p_bust"], "mean_n_payouts": r["mean_n_payouts"]}
    # re-evaluate the winner with more paths
    r = run_funded(spec, edge, fixed_with_payout(best["delta"], best["lam"], best["k"]), n_accounts=4 * n, horizon=horizon, seed=seed + 1)
    best.update({"mean_payout": r["mean_payout"], "p_any_payout": r["p_any_payout"], "p_bust": r["p_bust"],
                 "mean_n_payouts": r["mean_n_payouts"], "median_payout": r["median_payout"]})
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", default="50K")
    ap.add_argument("--edges", default="zero,modest,strong")
    ap.add_argument("--out", default="results/raw_paths")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for name in a.edges.split(","):
        edge = PRESETS[name]
        out = {"size": a.size, "edge": name, "edge_desc": edge.describe(), "variants": {}}
        for path, dll in (("standard", False), ("consistency", False), ("standard", True), ("consistency", True)):
            spec = spec_from(a.size, path, dll)
            res = best_fixed(spec, edge)
            out["variants"][f"{path}{'_dll' if dll else ''}"] = res
            print(a.size, name, path, "dll" if dll else "", res, flush=True)
        with open(os.path.join(a.out, f"{a.size}_{name}.json"), "w") as f:
            json.dump(out, f, indent=1)


if __name__ == "__main__":
    main()
