"""Hypothesis family: volume_time_seasonality.

Question: is there an hour-of-day x weekday seasonality in BTC / ETH returns (2020-2024) strong and
stable enough that a Topstep MBT/MET trader could run it as a fixed long/short time schedule?

Design (fixed before looking at the data):
  * Grid cells are (weekday, hour) on the UTC clock (funding / daily-close anchored), 168 cells, or the
    coarser 24-hour-only, 7x6 four-hour-block, or weekday-only grids.  One CT-clock variant.
  * Returns are open-to-next-open log returns of 5-min bars, aggregated to one observation per
    calendar hour, restricted to bars where a Topstep position may be held.
  * Cell selection is done ONLY on the first half of the in-sample window (H1 = 2020-01-01 ..
    2022-03-31): a cell is selected when |t| >= T_SEL on H1 AND the sign of its mean return agrees in
    both halves of H1 (consistency).  Long in positive cells, short in negative cells, adjacent same-sign
    cells merge into one trade.  The schedule is then evaluated on the second half (H2 = 2022-04-01 ..
    2024-06-30) with protocol.backtest_signals: that H2 result is the honest, out-of-sample test and is
    the headline statistic for every variant.  H1 ("fit") and full-IS numbers are reported as well but
    are contaminated by the selection.  One variant reverses the roles (select on H2, test on H1).
  * Volume: the seasonal volume profile is a diagnostic; one variant gates each scheduled block on the
    last completed hour's quote volume exceeding the trailing 24-hour hourly average.
  * No stops / targets: the hypothesis is pure time-of-day exposure.  Costs as in protocol.CONTRACT.

Forced-flat note: protocol.forced_flat_time returns True for every bar with CT time >= 15:10,
including the whole 17:00-23:59 CT evening, so protocol.backtest_signals would close any evening
position on its own entry bar.  Like research.hyp.session_drift we patch it for the duration of each
backtest to the daily break only (15:10-17:00 CT); day-session behaviour is unchanged.

Run: cd /home/user/j && python3 -m research.hyp.volume_time_seasonality
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

from research.data import load_bars
from research import protocol as P

ROOT = "/home/user/j/data_research/IS"
OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "volume_time_seasonality_results.json")

H1 = (pd.Timestamp("2020-01-01", tz="UTC"), pd.Timestamp("2022-03-31 23:59:59", tz="UTC"))
H2 = (pd.Timestamp("2022-04-01", tz="UTC"), pd.Timestamp("2024-06-30 23:59:59", tz="UTC"))
H1_MID = pd.Timestamp("2021-02-15", tz="UTC")   # splits H1 into two ~13.5-month consistency halves
H2_MID = pd.Timestamp("2023-05-15", tz="UTC")
DOW_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


# ----------------------------------------------------------------------------- helpers
def forced_flat_break_only(ts_utc: pd.Series) -> np.ndarray:
    t = P.ct(ts_utc)
    minutes = (t.dt.hour * 60 + t.dt.minute).values
    return (minutes >= 15 * 60 + 10) & (minutes < 17 * 60)


def run_backtest(bars, sym, entries, exits, side):
    orig = P.forced_flat_time
    P.forced_flat_time = forced_flat_break_only
    try:
        return P.backtest_signals(bars, entries, exits, side, sym=sym)
    finally:
        P.forced_flat_time = orig


def prepare(sym: str) -> dict:
    bars = load_bars(sym, "5min", root=ROOT)
    o = bars["open"].values
    n = len(bars)
    r = np.zeros(n)
    r[:-1] = np.log(o[1:] / o[:-1])            # return of holding bar i open -> bar i+1 open
    hold_ok = P.tradable_mask(bars["open_time"])
    hold_ok[-1] = False
    ts = bars["open_time"]
    aux = {"bars": bars, "r": r, "hold_ok": hold_ok, "ts": ts}
    for clock in ("utc", "ct"):
        t = ts if clock == "utc" else bars["ct"]
        aux[clock] = {"dow": t.dt.dayofweek.values, "hour": t.dt.hour.values,
                      "day": t.dt.normalize().values}
    # relative volume gate: last completed hour's quote volume vs trailing 24h hourly average (both
    # known at bar i's open: sums over bars i-12..i-1 and i-288..i-1)
    qv = bars["quote_volume"].values.astype(float)
    cs = np.concatenate([[0.0], np.cumsum(qv)])
    last_h = np.full(n, np.nan)
    last_d = np.full(n, np.nan)
    last_h[12:] = cs[12:n] - cs[0:n - 12]              # sum of quote volume over bars i-12..i-1 at index i
    last_d[288:] = (cs[288:n] - cs[0:n - 288]) / 24.0
    aux["relvol"] = last_h / last_d
    return aux


def hourly_obs(aux: dict, clock: str, mask: np.ndarray, block_hours: int = 1) -> pd.DataFrame:
    """One observation per (calendar day, hour-block) summing the tradable 5-min returns inside it."""
    c = aux[clock]
    m = mask & aux["hold_ok"]
    df = pd.DataFrame({"day": c["day"][m], "dow": c["dow"][m], "hour": c["hour"][m] // block_hours, "r": aux["r"][m]})
    g = df.groupby(["day", "dow", "hour"], sort=False)["r"].sum().reset_index()
    return g


def cell_table(obs: pd.DataFrame, keys) -> pd.DataFrame:
    g = obs.groupby(keys)["r"]
    out = pd.DataFrame({"mean_bp": g.mean() * 1e4, "std_bp": g.std() * 1e4, "n": g.count()})
    out["t"] = out["mean_bp"] / (out["std_bp"] / np.sqrt(out["n"]))
    return out


def select_cells(aux, clock, window, keys, block_hours=1, t_sel=2.0, top_k=None, min_abs_bp=0.0, mid=None):
    """Cells chosen on `window` with |t| >= t_sel (or the top_k by |t|), |mean| >= min_abs_bp, and the
    same sign of the mean in both halves of the window.  Returns {cell_key: sign} and the table."""
    ts = aux["ts"].values
    w = (ts >= window[0].to_datetime64()) & (ts <= window[1].to_datetime64())
    obs = hourly_obs(aux, clock, w, block_hours)
    tab = cell_table(obs, keys)
    mid = mid.to_datetime64()
    a = cell_table(obs[obs["day"] < mid], keys)["mean_bp"].reindex(tab.index)
    b = cell_table(obs[obs["day"] >= mid], keys)["mean_bp"].reindex(tab.index)
    tab["consistent"] = (np.sign(a) == np.sign(b)) & (np.sign(tab["mean_bp"]) == np.sign(a))
    tab["abs_t"] = tab["t"].abs()
    cand = tab[tab["consistent"] & (tab["mean_bp"].abs() >= min_abs_bp) & (tab["n"] >= 30)]
    if top_k is not None:
        cand = cand.sort_values("abs_t", ascending=False).head(top_k)
    else:
        cand = cand[cand["abs_t"] >= t_sel]
    sel = {k: int(np.sign(v)) for k, v in cand["mean_bp"].items()}
    return sel, tab


def select_best_windows(aux, clock, window, per_dow, mid, t_sel=2.0, min_len=2, max_len=8):
    """For each weekday (or for all days pooled) pick the contiguous window of min_len..max_len hours
    (same calendar day, no wrap) whose summed hourly return has the largest |t| on `window`, provided
    |t| >= t_sel and the sign agrees in both halves of `window`.  Returns {(dow, hour): sign} cells."""
    ts = aux["ts"].values
    w = (ts >= window[0].to_datetime64()) & (ts <= window[1].to_datetime64())
    obs = hourly_obs(aux, clock, w, 1)
    mid = mid.to_datetime64()
    groups = sorted(obs["dow"].unique()) if per_dow else [None]
    sel, info = {}, []
    for d in groups:
        o = obs if d is None else obs[obs["dow"] == d]
        piv = o.pivot_table(index="day", columns="hour", values="r", aggfunc="sum")
        piv = piv.reindex(columns=range(24))
        best = None
        for L in range(min_len, max_len + 1):
            for h0 in range(0, 24 - L + 1):
                x = piv.iloc[:, h0:h0 + L]
                if x.notna().sum(axis=1).eq(L).sum() < 30:
                    continue
                v = x.sum(axis=1, min_count=L).dropna()
                a, b = v[v.index < mid], v[v.index >= mid]
                if len(a) < 10 or len(b) < 10 or np.sign(a.mean()) != np.sign(b.mean()):
                    continue
                t = v.mean() / (v.std() / np.sqrt(len(v)))
                if abs(t) >= t_sel and (best is None or abs(t) > abs(best[0])):
                    best = (t, h0, L, v.mean() * 1e4, len(v))
        if best is not None:
            t, h0, L, mbp, nn = best
            info.append({"dow": None if d is None else int(d), "h0": h0, "len": L, "t": round(float(t), 2),
                         "mean_bp": round(float(mbp), 1), "n": int(nn)})
            for h in range(h0, h0 + L):
                for dd in ([d] if d is not None else range(7)):
                    sel[(int(dd), h)] = int(np.sign(t))
    return sel, info


def schedule_from_cells(aux, clock, sel, keys, block_hours=1) -> np.ndarray:
    c = aux[clock]
    desired = np.zeros(len(aux["r"]), dtype=int)
    if not sel:
        return desired
    hour = c["hour"] // block_hours
    for k, s in sel.items():
        if keys == ["dow", "hour"]:
            m = (c["dow"] == k[0]) & (hour == k[1])
        elif keys == ["hour"]:
            m = hour == k
        else:  # ["dow"]
            m = c["dow"] == k
        desired[m] = s
    desired[~aux["hold_ok"]] = 0
    return desired


def gate_blocks(desired: np.ndarray, cond: np.ndarray) -> np.ndarray:
    """Keep a contiguous nonzero block of `desired` only if cond is True on the bar before it starts."""
    nz = desired != 0
    start = nz & ~np.concatenate([[False], nz[:-1]])
    block_id = np.cumsum(start) * nz
    start_idx = np.where(start)[0]
    ok = np.zeros(len(start_idx) + 1, dtype=bool)
    prev = np.clip(start_idx - 1, 0, None)
    ok[1:] = np.nan_to_num(cond[prev], nan=0.0).astype(bool)
    return desired * ok[block_id]


def signals_from_desired(desired: np.ndarray):
    n = len(desired)
    nxt = np.zeros(n, dtype=int)
    nxt[:-1] = desired[1:]
    entries = nxt != 0
    exits = nxt != desired
    side = nxt.copy()
    return entries, exits, side


def window_stats(trades: pd.DataFrame, bars: pd.DataFrame, window) -> dict:
    if trades is None or len(trades) == 0:
        return {"n": 0}
    tr = trades[(trades["entry_time"] >= window[0]) & (trades["entry_time"] <= window[1])]
    b = bars[(bars["open_time"] >= window[0]) & (bars["open_time"] <= window[1])]
    st = P.summarize(tr, b)
    if st.get("n", 0):
        st["reasons"] = tr["reason"].value_counts().to_dict()
        st["by_year"] = {k: round(v, 1) for k, v in st["by_year"].items()}
    return st


def cells_text(sel, keys, clock, block_hours=1):
    if not sel:
        return "none"
    parts = []
    for k, s in sorted(sel.items(), key=lambda kv: (kv[0] if isinstance(kv[0], tuple) else (kv[0],))):
        sgn = "L" if s > 0 else "S"
        if keys == ["dow", "hour"]:
            h0 = k[1] * block_hours
            parts.append(f"{DOW_NAMES[k[0]]} {h0:02d}-{h0 + block_hours:02d}{clock.upper()}:{sgn}")
        elif keys == ["hour"]:
            parts.append(f"{k:02d}-{k + 1:02d}{clock.upper()}:{sgn}")
        else:
            parts.append(f"{DOW_NAMES[k]}:{sgn}")
    return ", ".join(parts)


# ----------------------------------------------------------------------------- variants
# name, symbol, dict(clock, keys, block_hours, t_sel|top_k, min_abs_bp, select_window, test_window, gate)
VARIANTS = [
    ("BTC_hw_t2",        "BTCUSDT", dict(clock="utc", keys=["dow", "hour"], t_sel=2.0)),
    ("BTC_hw_top10",     "BTCUSDT", dict(clock="utc", keys=["dow", "hour"], top_k=10)),
    ("BTC_blk4h_t2",     "BTCUSDT", dict(clock="utc", keys=["dow", "hour"], block_hours=4, t_sel=2.0)),
    ("BTC_hour_t2",      "BTCUSDT", dict(clock="utc", keys=["hour"], t_sel=2.0)),
    ("BTC_dow_t15",      "BTCUSDT", dict(clock="utc", keys=["dow"], t_sel=1.5)),
    ("BTC_hw_t2_CT",     "BTCUSDT", dict(clock="ct", keys=["dow", "hour"], t_sel=2.0)),
    ("BTC_hw_t2_volgate", "BTCUSDT", dict(clock="utc", keys=["dow", "hour"], t_sel=2.0, gate="relvol")),
    ("BTC_hw_t2_hurdle10", "BTCUSDT", dict(clock="utc", keys=["dow", "hour"], t_sel=2.0, min_abs_bp=10.0)),
    ("BTC_hw_t2_reverse", "BTCUSDT", dict(clock="utc", keys=["dow", "hour"], t_sel=2.0, reverse=True)),
    ("ETH_hw_t2",        "ETHUSDT", dict(clock="utc", keys=["dow", "hour"], t_sel=2.0)),
    ("ETH_hw_top10",     "ETHUSDT", dict(clock="utc", keys=["dow", "hour"], top_k=10)),
    ("ETH_blk4h_t2",     "ETHUSDT", dict(clock="utc", keys=["dow", "hour"], block_hours=4, t_sel=2.0)),
    ("ETH_hour_t2",      "ETHUSDT", dict(clock="utc", keys=["hour"], t_sel=2.0)),
    # cost-aware: best contiguous 2-8 hour window per weekday (or pooled over days), chosen on H1
    ("BTC_bestwin_dow",  "BTCUSDT", dict(clock="utc", keys=["dow", "hour"], bestwin="dow", t_sel=2.0)),
    ("BTC_bestwin_all",  "BTCUSDT", dict(clock="utc", keys=["dow", "hour"], bestwin="all", t_sel=2.0)),
    ("ETH_bestwin_dow",  "ETHUSDT", dict(clock="utc", keys=["dow", "hour"], bestwin="dow", t_sel=2.0)),
]


def describe(cfg, sel) -> str:
    keys, clock, bh = cfg["keys"], cfg["clock"], cfg.get("block_hours", 1)
    grid = {("dow", "hour"): f"weekday x {bh}-hour block", ("hour",): "hour-of-day (all days)", ("dow",): "weekday"}[tuple(keys)]
    if cfg.get("bestwin"):
        grid = ("best contiguous 2-8 hour window " + ("per weekday" if cfg["bestwin"] == "dow" else "pooled over all days")
                + " (window sum of hourly returns)")
    crit = f"top {cfg['top_k']} cells by |t|" if cfg.get("top_k") else f"|t| >= {cfg['t_sel']}"
    if cfg.get("min_abs_bp"):
        crit += f" and |mean| >= {cfg['min_abs_bp']:.0f} bp/hour"
    sw, tw = ("H2", "H1") if cfg.get("reverse") else ("H1", "H2")
    gate = (" Each scheduled block is traded only if the quote volume of the last completed hour before the "
            "block start exceeds the trailing-24h average hourly quote volume." if cfg.get("gate") else "")
    return (f"5-min bars, {clock.upper()} clock, {grid} grid. Cells selected on {sw} by {crit} on hourly "
            f"open-to-open returns (tradable bars only) with the same sign in both halves of {sw}. Schedule: hold "
            f"+1 (long) in positive cells and -1 (short) in negative cells, entering at the open of the first "
            f"5-min bar of the cell and exiting at the open of the first bar after the last adjacent same-sign "
            f"cell; forced flat at 15:10 CT and before the weekend; no stop/target.{gate} Selected cells: "
            f"{cells_text(sel, keys, clock, bh)}. Tested on {tw}.")


def main():
    cache = {}
    results = []
    diag = {}
    for name, sym, cfg in VARIANTS:
        if sym not in cache:
            cache[sym] = prepare(sym)
        aux = cache[sym]
        bars = aux["bars"]
        keys, clock, bh = cfg["keys"], cfg["clock"], cfg.get("block_hours", 1)
        sel_w, test_w, mid = (H2, H1, H2_MID) if cfg.get("reverse") else (H1, H2, H1_MID)
        if cfg.get("bestwin"):
            sel, win_info = select_best_windows(aux, clock, sel_w, cfg["bestwin"] == "dow", mid, t_sel=cfg.get("t_sel", 2.0))
        else:
            sel, tab = select_cells(aux, clock, sel_w, keys, bh, t_sel=cfg.get("t_sel", 2.0), top_k=cfg.get("top_k"),
                                    min_abs_bp=cfg.get("min_abs_bp", 0.0), mid=mid)
            win_info = None
        desired = schedule_from_cells(aux, clock, sel, keys, bh)
        if cfg.get("gate") == "relvol":
            desired = gate_blocks(desired, aux["relvol"] > 1.0)
        entries, exits, side = signals_from_desired(desired)
        tr = run_backtest(bars, sym, entries, exits, side)
        st_fit = window_stats(tr, bars, sel_w)
        st_oos = window_stats(tr, bars, test_w)
        st_all = P.summarize(tr, bars) if len(tr) else {"n": 0}
        rec = {"name": name, "symbol": sym, "rule": describe(cfg, sel), "n_cells": len(sel),
               "cells": cells_text(sel, keys, clock, bh), "select_window": "H2" if cfg.get("reverse") else "H1",
               "fit": st_fit, "oos": st_oos, "full_is": st_all, "windows": win_info}
        if st_oos.get("n", 0) > 2:
            rec["dsr_oos"] = P.deflated_sharpe(st_oos["sharpe_per_trade"], st_oos["n"], len(VARIANTS))
        results.append(rec)
        print(f"{name:20s} {sym} cells={len(sel):2d} | FIT n={st_fit.get('n',0):5d} mean={st_fit.get('mean_net',0):7.2f} "
              f"t={st_fit.get('t_stat',0):6.2f} | OOS n={st_oos.get('n',0):5d} mean={st_oos.get('mean_net',0):7.2f} "
              f"t={st_oos.get('t_stat',0):6.2f} wr={st_oos.get('win_rate',0):.3f} tpd={st_oos.get('trades_per_day',0):.2f} "
              f"gross={st_oos.get('gross_mean',0):6.2f} by_year={st_oos.get('by_year')} | FULL n={st_all.get('n',0)} mean={st_all.get('mean_net',0):.2f} t={st_all.get('t_stat',0):.2f}")
        if win_info:
            print("    windows:", win_info)
        print("    cells:", rec["cells"])
        sys.stdout.flush()

    # ---- diagnostics: full-IS return / vol / volume profiles, and H1-vs-H2 cell-mean correlation
    for sym, aux in cache.items():
        ts = aux["ts"].values
        full = np.ones(len(ts), dtype=bool)
        obs = hourly_obs(aux, "utc", full)
        tab = cell_table(obs, ["dow", "hour"])
        obs1 = hourly_obs(aux, "utc", ts <= H1[1].to_datetime64())
        obs2 = hourly_obs(aux, "utc", ts >= H2[0].to_datetime64())
        t1, t2 = cell_table(obs1, ["dow", "hour"]), cell_table(obs2, ["dow", "hour"])
        j = t1[["mean_bp", "t"]].join(t2[["mean_bp", "t"]], lsuffix="_h1", rsuffix="_h2").dropna()
        corr = float(np.corrcoef(j["mean_bp_h1"], j["mean_bp_h2"])[0, 1])
        sign_agree = float((np.sign(j["mean_bp_h1"]) == np.sign(j["mean_bp_h2"])).mean())
        n_t2_h1 = int((j["t_h1"].abs() >= 2).sum())
        n_t2_h2 = int((j["t_h2"].abs() >= 2).sum())
        hour_tab = cell_table(obs, ["hour"])
        bars = aux["bars"]
        qv = pd.DataFrame({"hour": aux["utc"]["hour"], "dow": aux["utc"]["dow"], "qv": bars["quote_volume"].values})
        vol_prof = qv.groupby("hour")["qv"].mean()
        vol_prof = (vol_prof / vol_prof.mean()).round(3)
        diag[sym] = {"cell_mean_corr_H1_H2": corr, "cell_sign_agreement_H1_H2": sign_agree,
                     "n_cells_abs_t_ge2_H1": n_t2_h1, "n_cells_abs_t_ge2_H2": n_t2_h2, "n_cells": int(len(j)),
                     "hour_of_day_UTC_full_IS": hour_tab.round(3).to_dict(orient="index"),
                     "relative_volume_by_UTC_hour": vol_prof.to_dict(),
                     "hourly_ret_std_bp_by_UTC_hour": cell_table(obs, ["hour"])["std_bp"].round(1).to_dict()}
        print(f"\n{sym}: 168-cell mean-return correlation H1 vs H2 = {corr:.3f}, sign agreement = {sign_agree:.3f} "
              f"(chance 0.5); cells with |t|>=2: H1 {n_t2_h1}, H2 {n_t2_h2} (chance ~{0.0455 * len(j):.1f})")
        print(f"{sym} hour-of-day UTC (full IS, bp/hour):\n{hour_tab.round(2).to_string()}")
        print(f"{sym} relative volume by UTC hour: {vol_prof.to_dict()}")

    with open(OUT_JSON, "w") as fh:
        json.dump({"n_variants": len(VARIANTS), "variants": results, "diagnostics": diag}, fh, indent=1, default=str)
    print(f"\nwrote {OUT_JSON}; n_variants={len(VARIANTS)}")


if __name__ == "__main__":
    main()
