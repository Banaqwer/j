"""Hypothesis family: orb_long_hold  (round 2; in-sample only, ROOT = data_research/IS)

Opening-range breakouts with SESSION-LONG holds on BTCUSDT perpetual 5-minute bars (proxy for CME MBT).

Economic story: the first 30/60 minutes after the US equity cash open (08:30 CT) and after the CME
re-open (17:00 CT) are auctions that establish a value area.  A 5-min close beyond it means one side has
absorbed the auction's liquidity; the trade then rides the resulting directional day until the Topstep
flat deadline, with the opposite side of the range as the invalidation (stop).  The width filter (V1, V3)
only takes days whose auction range is wide relative to recent history: the MBT round turn is a fixed
$3.82 so only above-median volatility days can plausibly pay for it.

PRE-REGISTERED VARIANTS (fixed before any result was looked at; all four are run and reported):
  V1 us_orb30_wide : range = high/low of 08:30-09:00 CT (six 5-min bars).  From 09:00 CT, enter at the open
                     of the bar after the first 5-min close above the range high (long) or below the range
                     low (short); stop = opposite side of the range (bar high/low); exit at the 15:08 CT
                     deadline.  Only on days whose range width (high-low)/open is >= the trailing 60-day
                     median of range widths.
  V2 us_orb30_all  : V1 without the width filter.
  V3 us_orb60_wide : range = 08:30-09:30 CT, entries from 09:30 CT, width filter as V1.
  V4 evening_orb60 : range = 17:00-18:00 CT (Sun-Thu sessions); breakout entries allowed until 02:00 CT;
                     stop = opposite side of the range; exit at the 15:08 CT deadline next day; no filter.

Mechanics (all variants)
  * Signal computed from the close of 5-min bar i, fill at the OPEN of bar i+1 (protocol.backtest_signals).
  * One trade per session: only the FIRST close outside the range fires (no re-entry after a stop-out).
  * Stop checked on bar high/low from the fill bar onwards (conservative, as the protocol).
  * "Exit at 15:08 CT": the 5-min bar grid has no 15:08 bar; the exit is the protocol's forced flat at the
    open of the 15:10 CT bar (the first printed price after the 15:08 order; live: market order at 15:08 CT).
    Entries require the fill bar to be < 15:08 CT (protocol.entry_mask).
  * Engine: `run_engine` replicates protocol.backtest_signals bar-for-bar but takes a per-signal-bar stop
    PRICE; it is validated against protocol.backtest_signals (unpatched, 2026-11-10 forced_flat_time) at
    the start of every run; any mismatch aborts the run.
  * Costs: protocol.CONTRACT["BTCUSDT"] ($3.82 per round turn, 0.1 BTC per contract).
  * Deflated Sharpe: N = 196 prior trials + 4 variants of this family = 200.

Post-hoc diagnostics (at most 2, breakdowns of the pre-registered variants' own trades, never nominated):
  D1 P&L of V2 (unfiltered) by entry-hour bucket -- are late-day breaks dead weight?
  D2 P&L of V2 by opening-range width quintile (width / trailing-60-day median) -- is the filter direction right?

Run:  cd /home/user/j && python3 -m research.hyp.r2_orb_long_hold
"""
from __future__ import annotations

import json
import os
import time

import numpy as np
import pandas as pd

from research import protocol as P
from research.data import load_bars

ROOT = "/home/user/j/data_research/IS"
SYM = "BTCUSDT"
OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "r2_orb_long_hold_results.json")
N_PRIOR_TRIALS = 196
WIDTH_LOOKBACK = 60          # trailing sessions for the width median (strictly prior sessions)
WIDTH_MIN_PERIODS = 30       # need at least this many prior widths, else the day is not eligible


def hhmm(h: int, m: int = 0) -> int:
    return h * 60 + m


# ----------------------------------------------------------------------------- clock helpers (CT wall clock)
class Clock:
    """Per-bar CT wall-clock minutes-of-day, calendar day key, session key (sessions start 17:00 CT) and the
    weekday of the calendar day / of the session's start day.  Built from naive local wall-clock time so DST
    changes cannot shift a bar into the wrong day."""

    def __init__(self, bars: pd.DataFrame):
        local = bars["ct"].dt.tz_localize(None)            # naive wall clock in America/Chicago
        self.minutes = (local.dt.hour * 60 + local.dt.minute).values
        self.day = local.dt.normalize().values.astype("datetime64[D]").astype(np.int64)
        self.dow = local.dt.dayofweek.values               # Mon=0 .. Sun=6 (calendar day)
        sess_start = (local - pd.Timedelta(hours=17)).dt.normalize()
        self.sess = sess_start.values.astype("datetime64[D]").astype(np.int64)
        self.sess_dow = sess_start.dt.dayofweek.values     # weekday of the session's start date
        self.sess_minutes = (self.minutes - 17 * 60) % 1440  # minutes since the 17:00 CT session open


def group_transform(values: np.ndarray, key: np.ndarray, mask: np.ndarray, how: str) -> np.ndarray:
    s = pd.Series(np.where(mask, values, np.nan))
    return s.groupby(key).transform(how).values


def first_in_group(flag: np.ndarray, key: np.ndarray) -> np.ndarray:
    cum = pd.Series(flag.astype(np.int64)).groupby(key).cumsum().values
    return flag & (cum == 1)


# ----------------------------------------------------------------------------- engine (per-trade stop price)
def run_engine(bars: pd.DataFrame, entries: np.ndarray, side: np.ndarray, stop_px: np.ndarray, sym: str = SYM,
               exits: np.ndarray | None = None) -> pd.DataFrame:
    """protocol.backtest_signals with a per-signal-bar absolute stop price (NaN = no stop).
    A trade whose stop is not on the loss side of the fill is skipped (counted in attrs['skipped'])."""
    c = P.CONTRACT[sym]
    ts = bars["open_time"]
    o, h, l = bars["open"].values, bars["high"].values, bars["low"].values
    can_enter = P.entry_mask(ts)
    can_hold = P.tradable_mask(ts)
    flat_now = P.forced_flat_time(ts)
    n = len(bars)
    if exits is None:
        exits = np.zeros(n, dtype=bool)
    rows = []
    i, pos, skipped = 0, 0, 0
    ei = ep = sp = None
    while i < n - 1:
        if pos == 0:
            if entries[i] and can_enter[i + 1] and can_hold[i + 1]:
                p = int(side[i]) if side[i] != 0 else 1
                ei = i + 1
                ep = o[ei]
                sp = stop_px[i]
                if not np.isfinite(sp):
                    sp = None
                elif p * (ep - sp) <= 0:
                    skipped += 1
                    i += 1
                    continue
                pos = p
                i = ei
                continue
            i += 1
            continue
        reason, xp = None, None
        if sp is not None:
            if (pos == 1 and l[i] <= sp) or (pos == -1 and h[i] >= sp):
                xp, reason = sp, "stop"
        if xp is None and (flat_now[i] or not can_hold[i]):
            xp, reason = o[i], "flat"
        if xp is None and exits[i] and i + 1 < n:
            xp, reason = o[i + 1], "signal"
            i_exit = i + 1
        else:
            i_exit = i
        if xp is not None:
            gross = pos * (xp - ep) * c["mult"]
            rows.append(dict(entry_time=ts.iloc[ei], exit_time=ts.iloc[i_exit], side=pos, entry=ep, exit=xp,
                             gross=gross, net=gross - c["cost_rt"], hold_bars=i_exit - ei, reason=reason))
            pos = 0
            i = i_exit + (0 if reason == "signal" else 1)
            continue
        i += 1
    tr = pd.DataFrame(rows)
    tr.attrs["skipped"] = skipped
    return tr


def validate_engine(bars: pd.DataFrame, sym: str = SYM) -> None:
    """run_engine with stop_px = next open x (1 -/+ 0.6%) must reproduce protocol.backtest_signals(stop_pct=0.006)
    exactly (unpatched protocol: forced_flat_time fixed 2026-11-10 covers only the daily break + weekend)."""
    rng = np.random.default_rng(7)
    n = len(bars)
    entries = rng.random(n) < 0.004
    side = rng.choice([-1, 1], n)
    exits = rng.random(n) < 0.01
    ref = P.backtest_signals(bars, entries, exits, side, sym=sym, stop_pct=0.006)
    o = bars["open"].values
    nxt = np.r_[o[1:], np.nan]
    stop_px = nxt * (1 - 0.006 * side)
    mine = run_engine(bars, entries, side, stop_px, sym, exits=exits)
    ok = len(ref) == len(mine) and len(ref) > 100
    if ok:
        for col in ("entry_time", "exit_time", "side", "entry", "exit", "net", "hold_bars", "reason"):
            ok &= bool((ref[col].values == mine[col].values).all())
    if not ok:
        raise RuntimeError(f"engine validation FAILED: ref n={len(ref)} mine n={len(mine)}")
    print(f"engine validation OK ({len(ref)} random trades identical to protocol.backtest_signals, "
          f"reasons={dict(ref['reason'].value_counts())})")


# ----------------------------------------------------------------------------- range + filter builders
def session_range(bars: pd.DataFrame, key: np.ndarray, minutes: np.ndarray, r_start: int, r_end: int):
    """[hi, lo, open] of the bars whose `minutes` lie in [r_start, r_end), broadcast over `key`; NaN unless the
    range is complete ((r_end - r_start)/5 bars present)."""
    in_r = (minutes >= r_start) & (minutes < r_end)
    cnt = group_transform(np.ones(len(bars)), key, in_r, "sum")
    full = cnt >= (r_end - r_start) // 5
    hi = np.where(full, group_transform(bars["high"].values, key, in_r, "max"), np.nan)
    lo = np.where(full, group_transform(bars["low"].values, key, in_r, "min"), np.nan)
    # open of the range = open of its first bar
    first_bar = in_r & first_in_group(in_r, key)
    op = np.where(full, group_transform(bars["open"].values, key, first_bar, "max"), np.nan)
    return hi, lo, op


def wide_filter(hi, lo, op, key: np.ndarray, eligible_day: np.ndarray):
    """True on sessions whose width (hi-lo)/open is >= the median width of the previous WIDTH_LOOKBACK
    eligible sessions with a complete range (strictly prior; >= WIDTH_MIN_PERIODS required).
    Also returns the per-bar ratio width / trailing median (diagnostic)."""
    df = pd.DataFrame({"k": key, "hi": hi, "lo": lo, "op": op, "el": eligible_day}).dropna()
    df = df[df["el"]].drop_duplicates("k").sort_values("k")
    w = (df["hi"] - df["lo"]) / df["op"]
    med = w.shift(1).rolling(WIDTH_LOOKBACK, min_periods=WIDTH_MIN_PERIODS).median()
    ok = pd.Series((w >= med).values & med.notna().values, index=df["k"].values)
    ratio = pd.Series((w / med).values, index=df["k"].values)
    k = pd.Series(key)
    return k.map(ok).fillna(False).values.astype(bool), k.map(ratio).values.astype(float)


def breakout_signals(bars, key: np.ndarray, hi, lo, window: np.ndarray):
    """First 5-min close outside [lo, hi] within `window`, per key -> entries, side."""
    cl = bars["close"].values
    up = window & np.isfinite(hi) & (cl > hi)
    dn = window & np.isfinite(lo) & (cl < lo)
    first = first_in_group(up | dn, key)
    side = np.where(up, 1, np.where(dn, -1, 0)) * first
    return first, side


# ----------------------------------------------------------------------------- variants
def V_us_orb(r_end_min: int, wide: bool):
    r_start = hhmm(8, 30)

    def build(bars, ck: Clock):
        hi, lo, op = session_range(bars, ck.day, ck.minutes, r_start, r_end_min)
        weekday = ck.dow < 5
        window = (ck.minutes >= r_end_min) & (ck.minutes < hhmm(15, 8)) & weekday
        ratio = np.full(len(bars), np.nan)
        if wide:
            ok, ratio = wide_filter(hi, lo, op, ck.day, weekday)
            window &= ok
        entries, side = breakout_signals(bars, ck.day, hi, lo, window)
        stop_px = np.where(side > 0, lo, np.where(side < 0, hi, np.nan))
        n_eligible = int(pd.Series(ck.day[window]).nunique())
        re = f"{r_end_min // 60:02d}:{r_end_min % 60:02d}"
        rule = (f"BTCUSDT 5-min bars (proxy for CME MBT), times America/Chicago, Mon-Fri. Opening range OR = [min low, max high] of the "
                f"{(r_end_min - r_start) // 5} bars with open times 08:30 to {re} CT exclusive (complete range required); OR open = open of the 08:30 bar. "
                + (f"Width filter: trade only if (OR high - OR low)/OR open >= the median of that quantity over the previous {WIDTH_LOOKBACK} "
                   f"weekdays with a complete OR (strictly prior days; at least {WIDTH_MIN_PERIODS} required, else no trade). " if wide else "No width filter. ")
                + f"From the {re} bar onwards, the FIRST 5-min close above OR high -> long, first close below OR low -> short (one trade per day, "
                f"whichever happens first, no re-entry). Fill at the open of the next bar; the fill bar must open before 15:08 CT. "
                f"Stop = the opposite side of the OR (OR low for longs, OR high for shorts), checked on bar highs/lows from the fill bar on, filled at the stop price. "
                f"No target. Exit at the 15:08 CT deadline = the open of the 15:10 CT bar (forced flat); no weekend positions. Cost $3.82 per round turn.")
        return dict(entries=entries, side=side, stop_px=stop_px, n_eligible=n_eligible, ratio=ratio, hi=hi, lo=lo), rule
    return build


def V_evening_orb():
    def build(bars, ck: Clock):
        hi, lo, op = session_range(bars, ck.sess, ck.sess_minutes, 0, 60)          # 17:00-18:00 CT of the session
        sun_thu = np.isin(ck.sess_dow, [6, 0, 1, 2, 3])
        window = (ck.sess_minutes >= 60) & (ck.sess_minutes < 9 * 60) & sun_thu     # 18:00 CT .. 02:00 CT
        entries, side = breakout_signals(bars, ck.sess, hi, lo, window)
        stop_px = np.where(side > 0, lo, np.where(side < 0, hi, np.nan))
        n_eligible = int(pd.Series(ck.sess[window]).nunique())
        rule = ("BTCUSDT 5-min bars (proxy for CME MBT), times America/Chicago. Sessions start 17:00 CT; only sessions starting Sunday-Thursday. "
                "Opening range OR = [min low, max high] of the 12 bars with open times 17:00 to 18:00 CT exclusive (complete range required). "
                "From the 18:00 CT bar until the 01:55 CT bar (signal bar open < 02:00 CT), the FIRST 5-min close above OR high -> long, "
                "first close below OR low -> short (one trade per session, whichever happens first, no re-entry). Fill at the open of the next bar. "
                "Stop = the opposite side of the OR (OR low for longs, OR high for shorts), checked on bar highs/lows from the fill bar on, filled at the stop price. "
                "No target. Exit at the 15:08 CT deadline the next day = the open of the 15:10 CT bar (forced flat). Cost $3.82 per round turn.")
        return dict(entries=entries, side=side, stop_px=stop_px, n_eligible=n_eligible, ratio=np.full(len(bars), np.nan), hi=hi, lo=lo), rule
    return build


VARIANTS = [
    ("V1_us_orb30_wide", V_us_orb(hhmm(9, 0), wide=True)),
    ("V2_us_orb30_all", V_us_orb(hhmm(9, 0), wide=False)),
    ("V3_us_orb60_wide", V_us_orb(hhmm(9, 30), wide=True)),
    ("V4_evening_orb60", V_evening_orb()),
]
N_FAMILY = len(VARIANTS)


# ----------------------------------------------------------------------------- post-hoc diagnostics (never nominated)
def diag_by_entry_hour(tr: pd.DataFrame) -> dict:
    """[post-hoc D1] V2 trades bucketed by CT entry hour."""
    hr = tr["entry_time"].dt.tz_convert("America/Chicago").dt.hour
    out = {}
    for lab, m in (("09", hr == 9), ("10", hr == 10), ("11", hr == 11), ("12-13", (hr >= 12) & (hr <= 13)), ("14-15", hr >= 14)):
        x = tr.loc[m, "net"].values
        if x.size:
            out[lab] = {"n": int(x.size), "mean_net": float(x.mean()),
                        "t": float(x.mean() / (x.std(ddof=1) / np.sqrt(x.size))) if x.size > 2 else 0.0}
    return out


def diag_by_width_quintile(tr: pd.DataFrame, bars: pd.DataFrame, ratio: np.ndarray) -> dict:
    """[post-hoc D2] V2 trades bucketed by (OR width)/(trailing-60-day median width) quintile."""
    ot = bars["open_time"].values.astype("datetime64[ns]").astype(np.int64)
    et = pd.to_datetime(tr["entry_time"]).dt.tz_convert("UTC").values.astype("datetime64[ns]").astype(np.int64)
    idx = np.searchsorted(ot, et) - 1   # signal bar = bar before the fill bar
    r = ratio[idx]
    ok = np.isfinite(r)
    tr = tr[ok].assign(ratio=r[ok])
    q = pd.qcut(tr["ratio"], 5, labels=False)
    out = {}
    for k, g in tr.groupby(q):
        x = g["net"].values
        out[f"Q{int(k) + 1}"] = {"n": int(x.size), "ratio_range": [float(g["ratio"].min()), float(g["ratio"].max())],
                                 "mean_net": float(x.mean()),
                                 "t": float(x.mean() / (x.std(ddof=1) / np.sqrt(x.size))) if x.size > 2 else 0.0}
    return out


# ----------------------------------------------------------------------------- main
def main():
    t0 = time.time()
    bars = load_bars(SYM, "5min", root=ROOT)
    assert bars["open_time"].iloc[-1] <= P.IS_END, "holdout data leaked into the in-sample run"
    ck = Clock(bars)
    print(f"loaded {len(bars)} 5-min bars {bars['open_time'].iloc[0]} -> {bars['open_time'].iloc[-1]} in {time.time() - t0:.1f}s")
    validate_engine(bars)

    results = {"family": "orb_long_hold", "symbol": SYM, "n_variants": N_FAMILY, "n_prior_trials": N_PRIOR_TRIALS,
               "dsr_N": N_PRIOR_TRIALS + N_FAMILY, "variants": {}, "post_hoc_diagnostics": {}}
    print("\n{:<20s} {:>5s} {:>6s} {:>8s} {:>6s} {:>6s} {:>7s} {:>7s} {:>7s} {:>6s}  by_year".format(
        "variant", "n", "t/day", "mean$", "t", "win%", "avgW", "avgL", "SRtr", "DSR"))
    kept = {}
    for name, builder in VARIANTS:
        kw, rule = builder(bars, ck)
        tr = run_engine(bars, kw["entries"], kw["side"], kw["stop_px"])
        kept[name] = (tr, kw)
        st = P.summarize(tr, bars)
        st["rule"] = rule
        st["symbol"] = SYM
        st["n_eligible_sessions"] = kw["n_eligible"]
        st["n_signal_bars"] = int(kw["entries"].sum())
        st["skipped_entries"] = int(tr.attrs.get("skipped", 0))
        if st["n"]:
            st["reasons"] = {k: int(v) for k, v in tr["reason"].value_counts().items()}
            st["avg_hold_bars"] = float(tr["hold_bars"].mean())
            st["share_long"] = float((tr["side"] > 0).mean())
            st["by_side"] = {("long" if s > 0 else "short"): {"n": int(len(g)), "mean_net": float(g["net"].mean())}
                             for s, g in tr.groupby("side")}
            st["n_pos_years"] = int(sum(v > 0 for v in st["by_year"].values()))
            st["dsr"] = P.deflated_sharpe(st["sharpe_per_trade"], st["n"], N_PRIOR_TRIALS + N_FAMILY)
            by = " ".join(f"{y}:{v:+.0f}" for y, v in st["by_year"].items())
            print(f"{name:<20s} {st['n']:5d} {st['trades_per_day']:6.2f} {st['mean_net']:8.2f} {st['t_stat']:6.2f} "
                  f"{100 * st['win_rate']:6.1f} {st['avg_win']:7.2f} {st['avg_loss']:7.2f} {st['sharpe_per_trade']:7.3f} {st['dsr']:6.3f}  {by}")
            print(f"{'':20s} eligible_sessions={st['n_eligible_sessions']} signals={st['n_signal_bars']} skipped={st['skipped_entries']} "
                  f"reasons={st['reasons']} hold={st['avg_hold_bars']:.1f} bars long%={100 * st['share_long']:.0f} "
                  f"by_side={ {k: round(v['mean_net'], 2) for k, v in st['by_side'].items()} }")
        else:
            print(f"{name:<20s}     0")
        results["variants"][name] = st

    # post-hoc diagnostics on V2's trades (the unfiltered US ORB)
    tr2, kw2 = kept["V2_us_orb30_all"]
    if len(tr2):
        _, ratio2 = wide_filter(kw2["hi"], kw2["lo"], session_range(bars, ck.day, ck.minutes, hhmm(8, 30), hhmm(9, 0))[2],
                                ck.day, ck.dow < 5)
        results["post_hoc_diagnostics"]["D1_V2_by_entry_hour_CT"] = diag_by_entry_hour(tr2)
        results["post_hoc_diagnostics"]["D2_V2_by_width_ratio_quintile"] = diag_by_width_quintile(tr2, bars, ratio2)
        print("\n[post-hoc D1] V2 net P&L by CT entry hour:")
        for k, v in results["post_hoc_diagnostics"]["D1_V2_by_entry_hour_CT"].items():
            print(f"   {k:6s} n={v['n']:4d} mean={v['mean_net']:+7.2f} t={v['t']:+.2f}")
        print("[post-hoc D2] V2 net P&L by (OR width / trailing-60-day median) quintile:")
        for k, v in results["post_hoc_diagnostics"]["D2_V2_by_width_ratio_quintile"].items():
            print(f"   {k} ratio[{v['ratio_range'][0]:.2f},{v['ratio_range'][1]:.2f}] n={v['n']:4d} mean={v['mean_net']:+7.2f} t={v['t']:+.2f}")

    surv = [name for name, st in results["variants"].items()
            if st.get("n", 0) >= 150 and st["mean_net"] > 0 and st["t_stat"] >= 2.5 and st.get("n_pos_years", 0) >= 3]
    results["survivors"] = surv
    print("\nvariants passing the survivor bar (n>=150, mean_net>0, t>=2.5, >=3 positive years):", surv or "none")

    with open(OUT_JSON, "w") as f:
        json.dump(results, f, indent=1, default=str)
    print(f"\nwrote {OUT_JSON}  ({time.time() - t0:.1f}s)")


if __name__ == "__main__":
    main()
