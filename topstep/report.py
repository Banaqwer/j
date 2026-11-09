"""Assemble results/raw/*.json into results/summary.md and figures.

usage: python -m topstep.report
"""
from __future__ import annotations

import glob
import json
import math
import os

import numpy as np

from . import closed_form as cf
from .edge import Edge
from .rules import COMBINE_PARAMS

RAW = "results/raw"
OUT = "results"
EDGE_ORDER = ["negative", "zero_free", "zero", "weak", "modest", "strong"]


def load():
    rows = []
    for p in sorted(glob.glob(os.path.join(RAW, "*.json"))):
        with open(p) as f:
            rows.append(json.load(f))
    return rows


def f0(x):
    return "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:,.0f}"


def f1(x):
    return "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:,.1f}"


def pct(x):
    return "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{100*x:.1f}%"


def key(r):
    e = r["edge"]
    if e.startswith("sweep"):
        return (99, r["edge_params"]["p_win"])
    return (EDGE_ORDER.index(e) if e in EDGE_ORDER else 50, 0)


def combine_table(rows, size, dll=False):
    rs = [r for r in rows if r["size"] == size and r["dll"] == dll and not r["edge"].startswith("sweep")]
    rs.sort(key=key)
    if not rs:
        return ""
    L = [f"### Trading Combine {size}{' with optional DLL' if dll else ''}: pass probability and duration\n",
         "| edge | p_win | γ per contract | bound D/(T+D) | one-shot bold (closed form) | continuous timid (closed form) | **DP optimal** P_pass | E[days] | DP bold | DP timid | trade-level sim (optimal) | trade-level sim (bold) | first action (fresh account) |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rs:
        c, cfm, ep = r["combine"], r["closed_form"], r["edge_params"]
        ts = c.get("trade_level_sim_optimal", {})
        tb = c.get("trade_level_sim_bold", {})
        L.append(f"| {r['edge']} | {ep['p_win']:.2f} | {ep['gamma']:+.4f} | {pct(cfm['fair_bold_bound_D_over_T_plus_D'])} | "
                 f"{pct(cfm['one_shot_bold_at_size']['P'])} (k={cfm['one_shot_bold_at_size']['k']}) | {pct(cfm['continuous_timid_1_contract'])} | "
                 f"**{pct(c['optimal']['P_pass'])}** | {f1(c['optimal']['E_days'])} | {pct(c['bold']['P_pass'])} | {pct(c['timid']['P_pass'])} | "
                 f"{pct(ts.get('P_pass'))} ({f1(ts.get('E_days'))} d) | {pct(tb.get('P_pass'))} | {c['optimal']['first_action']} |")
    return "\n".join(L) + "\n"


def funded_table(rows, size, dll=False):
    rs = [r for r in rows if r["size"] == size and r["dll"] == dll and not r["edge"].startswith("sweep")]
    rs.sort(key=key)
    if not rs:
        return ""
    L = [f"### Express Funded Account {size} (Standard path{', DLL-doubled cap' if dll else ''}): value over 250 trading days\n",
         "| edge | **V (DP, net of 90/10)** | binary-day sim mean | trade-level sim mean | P(any payout) DP-sim / trade-level | P(bust) | mean # payouts | median net payout | 90th pct | first action |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rs:
        fd = r["funded"]
        bs, tl = fd["binary_sim"], fd.get("trade_level_sim", {})
        L.append(f"| {r['edge']} | **${f0(fd['V_dp'])}** | ${f0(bs['mean_payout'])} | ${f0(tl.get('mean_payout'))} | "
                 f"{pct(bs['p_any_payout'])} / {pct(tl.get('p_any_payout'))} | {pct(bs['p_bust'])} | {f1(bs['mean_n_payouts'])} | "
                 f"${f0(bs['median_payout'])} | ${f0(bs['payout_quantiles']['0.9'])} | {fd['first_action']} |")
    return "\n".join(L) + "\n"


def econ_table(rows, size, dll=False):
    rs = [r for r in rows if r["size"] == size and r["dll"] == dll and not r["edge"].startswith("sweep")]
    rs.sort(key=key)
    if not rs:
        return ""
    L = [f"### Whole-game economics {size}{' with DLL' if dll else ''}: pay until you pass, then trade the XFA for 250 days\n",
         "| edge | path | monthly / reset / activation | R_pass = V_XFA − activation | fee-aware P_pass | E[days] per attempt | quits at start? | E[trading days until pass] | **E[cost until pass]** | **EV until pass (fee-aware)** | EV with pure P-max policy |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rs:
        for path in ("standard", "noaf"):
            e = r["economics"][path]
            fa = e["fee_aware_policy"]
            L.append(f"| {r['edge']} | {path} | ${e['monthly']:.0f} / ${e['reset']:.0f} / ${e['activation']:.0f} | ${f0(e['R_pass'])} | "
                     f"{pct(fa['P_pass'])} | {f1(fa['E_days'])} | {'yes' if fa['quit_immediately'] else 'no'} | {f1(e['expected_trading_days_until_pass'])} | "
                     f"**${f0(e['expected_cost_until_pass'])}** | **${f0(e['EV_until_pass_fee_aware'])}** | ${f0(e['EV_until_pass_pmax_policy'])} |")
    return "\n".join(L) + "\n"


def sweep_table(rows, size="50K"):
    rs = [r for r in rows if r["size"] == size and r["edge"].startswith("sweep")]
    rs.sort(key=lambda r: r["edge_params"]["p_win"])
    if not rs:
        return "", None
    L = [f"### Break-even sweep ({size}, ES R=L=$100, $5 RT, 10 trades/day): win rate → EV\n",
         "| p_win | γ/contract | ann. Sharpe | DP P_pass | V_XFA (250 d) | E[cost until pass] std | **EV until pass, standard** | EV until pass, no-activation-fee | E[days until pass] |",
         "|---|---|---|---|---|---|---|---|---|"]
    xs, ys_std, ys_noaf = [], [], []
    for r in rs:
        ep = r["edge_params"]
        e = Edge(ep["p_win"], ep["reward"], ep["loss"], ep["cost_rt"], ep["trades_per_day"])
        es, en = r["economics"]["standard"], r["economics"]["noaf"]
        L.append(f"| {ep['p_win']:.2f} | {ep['gamma']:+.4f} | {e.annual_sharpe():+.1f} | {pct(r['combine']['optimal']['P_pass'])} | ${f0(r['funded']['V_dp'])} | "
                 f"${f0(es['expected_cost_until_pass'])} | **${f0(es['EV_until_pass_fee_aware'])}** | ${f0(en['EV_until_pass_fee_aware'])} | {f1(es['expected_trading_days_until_pass'])} |")
        xs.append(ep["p_win"]); ys_std.append(es["EV_until_pass_fee_aware"]); ys_noaf.append(en["EV_until_pass_fee_aware"])
    # break-even by linear interpolation
    be = None
    for i in range(1, len(xs)):
        if ys_std[i - 1] < 0 <= ys_std[i]:
            be = xs[i - 1] + (0 - ys_std[i - 1]) * (xs[i] - xs[i - 1]) / (ys_std[i] - ys_std[i - 1])
    if be is not None:
        L.append(f"\nBreak-even win rate at 1R (standard path): **p_win ≈ {be:.3f}**.")
    return "\n".join(L) + "\n", (xs, ys_std, ys_noaf, be)


def policy_section(rows, size="50K"):
    rs = [r for r in rows if r["size"] == size and not r["dll"] and r["edge"] in ("zero", "modest", "strong")]
    rs.sort(key=key)
    if not rs:
        return ""
    L = [f"### Optimal Combine policy along a fresh account ({size}, MLL still at −D)\n"]
    for r in rs:
        L.append(f"**{r['edge']}** — {r['edge_desc']}\n")
        L.append("| balance vs start | optimal daily action | P(pass from here) |")
        L.append("|---|---|---|")
        for p in r["combine"]["policy_fresh_mll"][::3]:
            L.append(f"| {p['b']:+,.0f} | {p['action']} | {pct(p['P'])} |")
        L.append("")
    return "\n".join(L) + "\n"


def figures(rows, sweep):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    os.makedirs(OUT, exist_ok=True)
    # Fig 1: pass probability vs gamma, 50K
    T, D = COMBINE_PARAMS["50K"]["target"], COMBINE_PARAMS["50K"]["mll"]
    g = np.linspace(-0.004, 0.004, 400)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(g, [cf.p_hit_upper(T, D, x / 5) for x in g], label="one-shot bold, 5 contracts (closed form, no consistency rule)")
    ax.plot(g, [cf.p_hit_upper(T, D, x) for x in g], label="one-shot bold, 1 contract")
    ax.plot(g, [cf.p_pass_topstep_continuous(T, D, x) for x in g], label="timid, 1 contract (trailing MLL + lock, closed form)")
    pts = [r for r in rows if r["size"] == "50K" and not r["dll"]]
    ax.scatter([r["edge_params"]["gamma"] for r in pts], [r["combine"]["optimal"]["P_pass"] for r in pts], c="k", zorder=5,
               label="DP optimal with 55% consistency target")
    ax.axhline(D / (T + D), ls="--", c="gray", lw=1); ax.text(-0.0039, D / (T + D) + 0.01, "no-edge ceiling D/(T+D)=0.40")
    ax.set_xlabel("γ = 2μ/σ² per contract  (1/$)"); ax.set_ylabel("P(pass 50K Combine)"); ax.set_ylim(0, 1)
    ax.legend(fontsize=8); ax.set_title("Pass probability vs edge, 50K Trading Combine")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig_pass_vs_gamma_50K.png"), dpi=130); plt.close(fig)
    # Fig 2: EV sweep
    if sweep:
        xs, ys, yn, be = sweep
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(xs, ys, "o-", label="standard path ($49/mo + $149 activation)")
        ax.plot(xs, yn, "s-", label="no-activation-fee path ($95/mo)")
        ax.axhline(0, c="gray", lw=1)
        if be:
            ax.axvline(be, ls="--", c="r", lw=1); ax.text(be + 0.002, min(ys) * 0.8, f"break-even p≈{be:.3f}", color="r")
        ax.set_xlabel("per-trade win rate at 1R (ES, $5 round turn)"); ax.set_ylabel("EV until pass + 250 XFA days  ($)")
        ax.set_title("Whole-game expected value vs edge, 50K"); ax.legend()
        fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig_ev_sweep_50K.png"), dpi=130); plt.close(fig)
    # Fig 3: funded value vs edge across sizes
    fig, ax = plt.subplots(figsize=(8, 5))
    for size, mk in (("50K", "o"), ("100K", "s"), ("150K", "^")):
        pts = sorted([r for r in rows if r["size"] == size and not r["dll"]], key=lambda r: r["edge_params"]["gamma"])
        if pts:
            ax.plot([r["edge_params"]["gamma"] for r in pts], [r["funded"]["V_dp"] for r in pts], mk + "-", label=f"{size} XFA (DP, 250 days)")
    ax.set_xlabel("γ per contract (1/$)"); ax.set_ylabel("expected net payouts in 250 trading days ($)")
    ax.set_title("Funded-account value vs edge"); ax.legend()
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig_funded_value.png"), dpi=130); plt.close(fig)


def main():
    rows = load()
    parts = ["# Results: Topstep Trading Combine and Express Funded Account, solved\n",
             "Generated from `results/raw/*.json` by `python -m topstep.report`. Rules as of 2026-11-09; "
             "edges are per-contract binary trade models (see `docs/TOPSTEP_MATH.md` §1.1). "
             "DP = exact dynamic program on end-of-day states; trade-level sim = Monte Carlo of every trade with 20,000 accounts.\n"]
    for size in ("50K", "100K", "150K"):
        for dll in (False, True):
            t = combine_table(rows, size, dll)
            if t:
                parts += [t, funded_table(rows, size, dll), econ_table(rows, size, dll)]
    st, sweep = sweep_table(rows)
    parts.append(st)
    parts.append(policy_section(rows))
    try:
        figures(rows, sweep)
        parts.append("### Figures\n\n![pass vs gamma](fig_pass_vs_gamma_50K.png)\n\n![EV sweep](fig_ev_sweep_50K.png)\n\n![funded value](fig_funded_value.png)\n")
    except Exception as ex:  # pragma: no cover
        parts.append(f"(figures not generated: {ex})\n")
    with open(os.path.join(OUT, "summary.md"), "w") as f:
        f.write("\n".join(parts))
    print("wrote results/summary.md with", len(rows), "runs")


if __name__ == "__main__":
    main()
