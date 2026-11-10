"""Hypothesis family: funding_fade_long_hold (round 2, pre-registered; in-sample only, ROOT = data_research/IS).

Fade extreme perpetual funding with holds to the next settlement (or to the Topstep 15:08 CT deadline).
Instrument: CME micro Bitcoin (MBT = 0.1 BTC) on Topstep, proxied by the Binance BTCUSDT perpetual.
Funding settles at 00:00 / 08:00 / 16:00 UTC; the rate of a settlement is known at its calc_time (not before).
Percentiles use the trailing 180 days of settled rates, history only (the settlement being scored is excluded).

PRE-REGISTERED VARIANTS (all run, all reported; none added, none dropped):
  V1 fade_p95_next    : first tradable bar after a settlement whose rate >= 95th pct -> short; <= 5th pct -> long;
                        exit at the bar before the next settlement (8h later) or at 15:08 CT, whichever first.
  V2 fade_p90_next    : thresholds 90 / 10.
  V3 fade_p95_session : as V1 but hold to 15:08 CT; entries whose fill would be after 15:08 CT are skipped.

Implementation conventions (fixed before any result was looked at):
  * Execution grid = 1-minute bars (the registered times "15:08 CT" and "the bar before the next settlement"
    exist exactly on this grid).  bars = load_bars("BTCUSDT", "1m", root=IS).
  * Settlement times: funding.calc_time rounded to the minute (the raw stamps carry millisecond jitter).
  * Percentile window for the settlement at T: all settled rates with calc_time in [T - 180 days, T), i.e.
    strictly before T; np.quantile (linear interpolation) at 0.95/0.05 (V1, V3) or 0.90/0.10 (V2);
    at least 486 of the nominal 540 settlements must be present (90%), else no signal.
    The comparison is LITERAL (>= / <=): when more than 5% (10%) of the window sits at Binance's default
    0.0001 rate, the upper percentile equals 0.0001 and every settlement AT the default fires a short.
    That is what the registered rule says, so it is what is run; tie counts are reported, and the
    strict-inequality version is post-hoc diagnostic D1 (never nominated).
  * Signal -> fill: the rate is known at T, so the signal is attached to the 1-min bar whose open_time == T and,
    per the protocol ("signal from bar i acted on at the open of bar i+1"), the fill is at the open of the first
    bar with open_time > T that protocol.entry_mask / tradable_mask allow ("first tradable bar after the
    settlement").  If no such bar exists before the exit bar (V1/V2: Saturday and Sunday 00:00/08:00 UTC
    settlements) the signal is void.  A Sunday 16:00 UTC signal fills at the Sunday 17:00 CT re-open.
  * V1/V2 exit: fill at the open of the last 1-min bar before the next settlement (next_T - 1 min), flagged on
    the bar before it (protocol 'signal' exit), or at the open of the 15:08 CT bar (flagged on 15:07 CT),
    whichever comes first.  The protocol's forced flat (15:10 CT, weekend) stays active as a backstop.
  * V3 exit: open of the 15:08 CT bar only (same day session); entries whose fill bar is at or after 15:08 CT
    (i.e. the 00:00 UTC settlement, 18:01/19:01 CT, and the Sunday 17:00 CT carry) are skipped as registered.
  * One contract, one position at a time (protocol.backtest_signals): a signal that arrives while a position is
    open (V3: the 16:00 UTC settlement while the 08:00 UTC trade is held) is skipped.  No stop / target.
  * Costs: protocol.CONTRACT["BTCUSDT"] = $3.82 per round turn, 0.1 BTC per contract.
  * Deflated Sharpe: N = 196 prior trials + 3 variants of this family = 199.
  * Survivor bar: mean_net > 0, t >= 2.5, n >= 150, net P&L > 0 in >= 3 of the calendar years 2020..2024.

Post-hoc diagnostics (at most 2, clearly labelled, never nominated):
  D1 strict_V1 : V1 with strict inequalities (rate > p95 / rate < p5) so settlements tied AT the percentile
                 (the clipped default rate) do not fire.  One extra trial, reported for interpretation only.
  D2 breakdown : each variant's own trades split by entry hour (UTC) x side -- no new trial.

Run:  cd /home/user/j && python3 -m research.hyp.r2_funding_fade_long_hold
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
import pandas as pd

from research import protocol as P
from research.data import load_bars, load_funding

ROOT = "/home/user/j/data_research/IS"
SYM = "BTCUSDT"
OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "r2_funding_fade_long_hold_results.json")
N_PRIOR_TRIALS = 196
PCT_WINDOW_DAYS = 180
PCT_MIN_OBS = 486            # 90% of the nominal 540 settlements in 180 days
IS_YEARS = ("2020", "2021", "2022", "2023", "2024")
EXIT_CT_MIN = 15 * 60 + 8    # 15:08 CT

VARIANTS = [
    # name, upper pct, lower pct, exit mode
    ("V1_fade_p95_next", 0.95, 0.05, "next"),
    ("V2_fade_p90_next", 0.90, 0.10, "next"),
    ("V3_fade_p95_session", 0.95, 0.05, "session"),
]
N_VARIANTS_TOTAL = N_PRIOR_TRIALS + len(VARIANTS)


# ----------------------------------------------------------------------------- funding percentiles
def settlement_table(funding: pd.DataFrame) -> pd.DataFrame:
    f = funding.copy()
    f["t"] = f["calc_time"].dt.round("min")
    f = f.drop_duplicates("t").sort_values("t").reset_index(drop=True)
    assert f["t"].max() <= P.IS_END, "in-sample funding only"
    t = f["t"].values.astype("datetime64[ns]")
    r = f["rate"].values.astype(float)
    n = len(f)
    q = {k: np.full(n, np.nan) for k in ("q05", "q10", "q90", "q95")}
    cnt = np.zeros(n, dtype=int)
    win = np.timedelta64(PCT_WINDOW_DAYS, "D")
    for k in range(n):
        lo = np.searchsorted(t, t[k] - win, side="left")
        w = r[lo:k]                                   # strictly before t[k]: history only
        cnt[k] = len(w)
        if len(w) >= PCT_MIN_OBS:
            q["q05"][k], q["q10"][k], q["q90"][k], q["q95"][k] = np.quantile(w, [0.05, 0.10, 0.90, 0.95])
    for k, v in q.items():
        f[k] = v
    f["n_window"] = cnt
    f["next_t"] = f["t"].shift(-1)
    return f


def signal_sides(st: pd.DataFrame, hi_q: float, lo_q: float, strict: bool = False) -> tuple[np.ndarray, dict]:
    """-1 short when rate >= upper percentile, +1 long when rate <= lower percentile, 0 otherwise."""
    qh = st[{0.95: "q95", 0.90: "q90"}[hi_q]].values
    ql = st[{0.05: "q05", 0.10: "q10"}[lo_q]].values
    r = st["rate"].values
    valid = ~np.isnan(qh)
    if strict:
        sh, lg = valid & (r > qh), valid & (r < ql)
    else:
        sh, lg = valid & (r >= qh), valid & (r <= ql)
    both = sh & lg                                     # degenerate window (upper == lower == rate): no signal
    side = np.where(sh & ~both, -1, np.where(lg & ~both, 1, 0)).astype(int)
    info = {"n_settlements_scored": int(valid.sum()), "n_short_signals": int((side == -1).sum()),
            "n_long_signals": int((side == 1).sum()), "n_conflict_dropped": int(both.sum()),
            "n_short_tied_at_pct": int((sh & np.isclose(r, qh)).sum()), "n_long_tied_at_pct": int((lg & np.isclose(r, ql)).sum())}
    return side, info


# ----------------------------------------------------------------------------- bar-level signal arrays
def build_signals(bars: pd.DataFrame, st: pd.DataFrame, side_k: np.ndarray, mode: str):
    n = len(bars)
    ot = bars["open_time"].values.astype("datetime64[ns]")
    ctmin = (bars["ct"].dt.hour * 60 + bars["ct"].dt.minute).values
    can = P.entry_mask(bars["open_time"]) & P.tradable_mask(bars["open_time"])
    # next allowed entry bar at or after each index
    nxt = np.full(n + 1, n, dtype=np.int64)
    for i in range(n - 1, -1, -1):
        nxt[i] = i if can[i] else nxt[i + 1]
    entries = np.zeros(n, dtype=bool)
    side = np.zeros(n, dtype=int)
    t = st["t"].values.astype("datetime64[ns]")
    next_t = st["next_t"].values.astype("datetime64[ns]")
    one_min = np.timedelta64(1, "m")
    skipped = {"no_bar_before_exit": 0, "after_1508_ct": 0, "no_data": 0}
    fills = []
    for k in np.flatnonzero(side_k != 0):
        j = int(np.searchsorted(ot, t[k], side="right"))      # first bar with open_time > T
        j = int(nxt[j]) if j < n else n
        if j >= n or j == 0:
            skipped["no_data"] += 1
            continue
        if mode == "next":
            if np.isnat(next_t[k]) or not (ot[j] < next_t[k] - one_min):
                skipped["no_bar_before_exit"] += 1
                continue
        else:  # session
            if ctmin[j] >= EXIT_CT_MIN:
                skipped["after_1508_ct"] += 1
                continue
        entries[j - 1] = True
        side[j - 1] = int(side_k[k])
        fills.append((k, j))
    exits = ctmin == EXIT_CT_MIN - 1                          # 15:07 CT -> fill at 15:08 CT open
    if mode == "next":
        flag_t = t - 2 * one_min                              # flagged 2 min before each settlement -> fill at T - 1 min
        exits = exits | pd.DatetimeIndex(ot).isin(pd.DatetimeIndex(flag_t))
    return entries, exits, side, skipped, fills


# ----------------------------------------------------------------------------- helpers
def rule_text(name: str, hi_q: float, lo_q: float, mode: str) -> str:
    hp, lp = int(round(hi_q * 100)), int(round(lo_q * 100))
    common = (f"1 MBT (0.1 BTC), no stop/target, Binance BTCUSDT perp 1-min bars as CME proxy, $3.82 round turn, one "
              f"position at a time. Funding settlements T at 00:00/08:00/16:00 UTC (calc_time rounded to the minute). "
              f"For each T compute the {hp}th and {lp}th percentiles (np.quantile, linear) of the settled rates with "
              f"calc_time in [T-180d, T) (history only; need >= 486 of 540). Signal: rate(T) >= p{hp} -> short, "
              f"rate(T) <= p{lp} -> long (literal inequalities; a window with p{hp} == p{lp} == rate gives no signal). "
              f"Fill at the open of the first 1-min bar with open_time > T that is allowed by protocol.entry_mask and "
              f"tradable_mask (first tradable bar after the settlement; a Sunday 16:00 UTC signal fills at Sunday 17:00 CT). ")
    if mode == "next":
        return (common + "Exit at the open of the 1-min bar opening at next_T - 1 min (the bar before the next settlement) "
                "or at the open of the 15:08 CT bar, whichever comes first; if no allowed entry bar exists before "
                "next_T - 1 min the signal is void. Protocol forced flat (15:10 CT, weekend) as backstop.")
    return (common + "Skip the signal if the fill bar's Chicago time-of-day is >= 15:08 (evening session / Sunday re-open). "
            "Exit at the open of the 15:08 CT bar of that same Topstep day session; a signal arriving while a position is "
            "open is skipped. Protocol forced flat (15:10 CT, weekend) as backstop.")


def qualifies(st: dict) -> tuple[bool, dict]:
    by = st.get("by_year", {})
    pos_years = sum(1 for y in IS_YEARS if by.get(y, 0.0) > 0)
    checks = {"mean_net_pos": st.get("mean_net", 0) > 0, "t_ge_2.5": st.get("t_stat", 0) >= 2.5,
              "n_ge_150": st.get("n", 0) >= 150, "pos_years_ge_3": pos_years >= 3, "pos_years": pos_years}
    return all(v for k, v in checks.items() if k != "pos_years"), checks


def tstat(x) -> float:
    x = np.asarray(x, float)
    return float(x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))) if len(x) > 1 and x.std(ddof=1) > 0 else 0.0


def record(name: str, tr: pd.DataFrame, bars: pd.DataFrame, extra: dict) -> dict:
    st = P.summarize(tr, bars)
    rec = {"name": name, "symbol": SYM, "n": int(st.get("n", 0))}
    rec.update(extra)
    if rec["n"] > 0:
        rec.update({k: float(st[k]) for k in ("trades_per_day", "mean_net", "median_net", "t_stat", "ci95_low", "ci95_high",
                                              "win_rate", "avg_win", "avg_loss", "sharpe_per_trade", "sharpe_annual",
                                              "total_net", "gross_mean", "max_drawdown")})
        rec["by_year"] = {k: round(v, 1) for k, v in st["by_year"].items()}
        rec["n_by_year"] = st["n_by_year"]
        rec["reasons"] = {k: int(v) for k, v in tr["reason"].value_counts().items()}
        rec["n_long"], rec["n_short"] = int((tr["side"] > 0).sum()), int((tr["side"] < 0).sum())
        rec["mean_net_long"] = float(tr.loc[tr["side"] > 0, "net"].mean()) if rec["n_long"] else 0.0
        rec["mean_net_short"] = float(tr.loc[tr["side"] < 0, "net"].mean()) if rec["n_short"] else 0.0
        rec["t_long"] = tstat(tr.loc[tr["side"] > 0, "net"].values) if rec["n_long"] > 1 else 0.0
        rec["t_short"] = tstat(tr.loc[tr["side"] < 0, "net"].values) if rec["n_short"] > 1 else 0.0
        rec["mean_hold_min"] = float(tr["hold_bars"].mean())
        rec["dsr"] = float(P.deflated_sharpe(st["sharpe_per_trade"], st["n"], N_VARIANTS_TOTAL))
        rec["survivor"], rec["survivor_checks"] = qualifies(st)
    else:
        rec.update({"survivor": False, "survivor_checks": {}})
    return rec


def run_variant(bars, st, hi_q, lo_q, mode, strict=False):
    side_k, info = signal_sides(st, hi_q, lo_q, strict=strict)
    entries, exits, side, skipped, fills = build_signals(bars, st, side_k, mode)
    tr = P.backtest_signals(bars, entries, exits, side, sym=SYM)
    info["n_entry_flags"] = int(entries.sum())
    info["skipped"] = skipped
    return tr, info


# ----------------------------------------------------------------------------- main
def main():
    t0 = time.time()
    bars = load_bars(SYM, "1m", root=ROOT).sort_values("open_time").reset_index(drop=True)
    assert bars["open_time"].max() <= P.IS_END and bars["open_time"].min() >= P.IS_START, "in-sample bars only"
    funding = load_funding(SYM, root=ROOT)
    st = settlement_table(funding)
    first_valid = st.loc[st["q95"].notna(), "t"].iloc[0]
    print(f"bars={len(bars)} {bars['open_time'].iloc[0]} -> {bars['open_time'].iloc[-1]}  settlements={len(st)} "
          f"scored={int(st['q95'].notna().sum())} first scored={first_valid}  ({time.time() - t0:.1f}s)")

    results, trades_all = [], {}
    for name, hi_q, lo_q, mode in VARIANTS:
        tr, info = run_variant(bars, st, hi_q, lo_q, mode)
        trades_all[name] = tr
        rec = record(name, tr, bars, {"upper_pct": hi_q, "lower_pct": lo_q, "exit_mode": mode,
                                      "rule": rule_text(name, hi_q, lo_q, mode), "signals": info})
        results.append(rec)
        print(f"{name:22s} n={rec['n']:5d} mean_net={rec.get('mean_net', 0):8.2f} t={rec.get('t_stat', 0):6.2f} "
              f"wr={rec.get('win_rate', 0):.3f} tpd={rec.get('trades_per_day', 0):.3f} dsr={rec.get('dsr', 0):.3f} "
              f"long n={rec.get('n_long', 0)} mean={rec.get('mean_net_long', 0):.2f} short n={rec.get('n_short', 0)} "
              f"mean={rec.get('mean_net_short', 0):.2f} hold={rec.get('mean_hold_min', 0):.0f}min\n"
              f"{'':22s} by_year={rec.get('by_year')} reasons={rec.get('reasons')} signals={info} survivor={rec['survivor']}")
        sys.stdout.flush()

    # ------------------------------------------------------------------ POST-HOC DIAGNOSTICS (labelled; never nominated)
    diag = {}
    # D1: V1 with strict inequalities (ties at the percentile, i.e. the clipped default 0.0001 rate, do not fire)
    tr_d1, info_d1 = run_variant(bars, st, 0.95, 0.05, "next", strict=True)
    d1 = record("D1_strict_V1_posthoc", tr_d1, bars, {"signals": info_d1})
    d1.pop("survivor", None); d1.pop("survivor_checks", None); d1["nominable"] = False
    diag["D1_strict_inequality_V1"] = d1
    print(f"\nD1 strict V1 (post-hoc): n={d1['n']} mean_net={d1.get('mean_net', 0):.2f} t={d1.get('t_stat', 0):.2f} "
          f"long n={d1.get('n_long', 0)} mean={d1.get('mean_net_long', 0):.2f} short n={d1.get('n_short', 0)} "
          f"mean={d1.get('mean_net_short', 0):.2f} by_year={d1.get('by_year')} signals={info_d1}")
    # D2: breakdown of each variant's own trades by entry hour (UTC) x side
    d2 = {}
    for name, tr in trades_all.items():
        if len(tr) == 0:
            d2[name] = {}
            continue
        hr = tr["entry_time"].dt.tz_convert("UTC").dt.hour
        tab = {}
        for (h, s), g in tr.groupby([hr, tr["side"]]):
            tab[f"h{int(h):02d}_{'long' if s > 0 else 'short'}"] = {"n": int(len(g)), "mean_net": float(g["net"].mean()),
                                                                     "t": tstat(g["net"].values), "total": float(g["net"].sum())}
        d2[name] = tab
    diag["D2_by_entry_hour_utc_x_side"] = d2
    print("D2 by entry hour (UTC) x side:")
    for k, tab in d2.items():
        print(" ", k, json.dumps({b: {kk: round(vv, 2) if isinstance(vv, float) else vv for kk, vv in v.items()} for b, v in tab.items()}))

    survivors = [r for r in results if r.get("survivor")]
    out = {"family": "funding_fade_long_hold", "symbol": SYM, "n_variants": len(VARIANTS), "n_prior_trials": N_PRIOR_TRIALS,
           "dsr_N": N_VARIANTS_TOTAL, "bar_size": "1min", "pct_window_days": PCT_WINDOW_DAYS, "pct_min_obs": PCT_MIN_OBS,
           "first_scored_settlement": str(first_valid), "variants": results,
           "survivors": [r["name"] for r in survivors], "diagnostics": diag}
    with open(OUT_JSON, "w") as fh:
        json.dump(out, fh, indent=1, default=str)
    print(f"\nsurvivors: {[r['name'] for r in survivors] or 'none'}; wrote {OUT_JSON}  ({time.time() - t0:.1f}s)")


if __name__ == "__main__":
    main()
