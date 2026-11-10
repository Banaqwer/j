"""Hypothesis family: orb_continuation  (ES, in-sample only, ROOT = data_research/IS, 2005-01 .. 2017-12)

Opening-range breakout of the US cash session on the E-mini S&P 500.  Price proxy: Oanda SPX500 CFD
minute bars (UTC timestamps -> America/Chicago).  P&L per ONE ES contract ($50/pt, $16.28 round-turn cost =
$3.78 commission + one 0.25 tick of slippage).

PRE-REGISTERED VARIANTS (all times CT; all four are run and reported, none dropped)
  Range = high/low of the 5-min bars with open time in [08:30, 09:00) (six bars).  From 09:00 CT, enter at the
  open of the bar after the FIRST 5-min close above the range high (long) or below the range low (short);
  stop = the opposite side of the range (checked on bar high/low, filled at the stop price); exit at 15:08 CT
  unless stated.  One trade per day (no re-entry after a stop).
  V1 us_orb30_all  : as above.
  V2 us_orb30_wide : only on days whose range width (high-low)/open(08:30) >= the median width of the 60 prior
                     valid-range days (strictly before the day; 60 prior observations required).
  V3 us_orb60_all  : range = [08:30, 09:30) (twelve bars), entries from 09:30 CT.
  V4 us_orb30_2h   : as V1 but exit after 2 hours (24 five-minute bars) or at the stop, whichever comes first.

IMPLEMENTATION
  * Signals are computed on the 5-minute grid (research.data_index.load_bars_index(..., "5min"): CT-aligned,
    bars only where quotes changed).  Execution is simulated on the 1-minute grid (same parquet) so that the
    15:08 CT exit is exact: the decision bar of 5-min bar [t, t+5) is the last 1-min bar inside that window and
    the fill is the open of the NEXT 1-min bar (= the open of the next 5-min bar).  Signals from bar i are acted
    on at the open of bar i+1 - no look-ahead.
  * Stop: checked on every 1-min bar from the fill bar through the bar before the exit bar (bar high/low), filled
    at the stop price (conservative, as protocol.backtest_signals).  Same trigger as on 5-min bars.
  * Exit 15:08: fill at the open of the first 1-min bar with CT time >= 15:08 on the same date (exit signal on the
    bar before it).  V4 time exit: fill at the open of the first 1-min bar at/after floor5(entry time) + 120 min
    (= the open of 5-min bar entry+24), or the 15:08 exit if that comes first.
  * Eligible days (known ex ante): weekdays that are not US equity-market holidays (NYSE/CME rules incl. Good
    Friday and the 2007-01-02 / 2012-10-29 / 2012-10-30 closures), with all range bars present and a 1-min bar in
    [15:08, 15:15] CT (missing bars = no trade; holiday/half-day sessions lack the 15:08 bar).  Entry fill must
    satisfy protocol.entry_mask / tradable_mask (fill < 15:08 CT, same date).
  * Engine: `run_trades` replicates protocol.backtest_signals with a per-trade stop PRICE; every traded day of every
    variant is cross-checked against protocol.backtest_signals run on that day's 1-min bars with the equivalent
    stop_pct and exit flags (`validate_against_protocol`); any mismatch aborts the run.
  * Costs: protocol.CONTRACT["ES"].  Deflated Sharpe: 22 pre-registered ES variants in this round.
  * Trade field hold_bars = number of 1-min bars present between fill and exit (not minutes: sparse-quote days have gaps).

Survivor bar (pre-registered): mean_net > 0, t_stat >= 2.5, n >= 150, net P&L > 0 in >= 8 of the 13 years.

Post-hoc diagnostics (clearly labelled, never nominated):
  D1 NAS100 (Nasdaq-100 CFD) twin of V1 with NQ costs ($20/pt, $8.78 RT).
  D2 V1's own trades split by side (long-only / short-only).

Run:  cd /home/user/j && python3 -m research.hyp.es_orb_continuation
"""
from __future__ import annotations

import datetime as dt
import json
import os
import time

import numpy as np
import pandas as pd
from pandas.tseries.holiday import (AbstractHolidayCalendar, GoodFriday, Holiday, USLaborDay, USMartinLutherKingJr,
                                    USMemorialDay, USPresidentsDay, USThanksgivingDay, nearest_workday,
                                    sunday_to_monday)

from research import protocol as P
from research.data_index import load_bars_index

ROOT = "/home/user/j/data_research/IS"
OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "es_orb_continuation_results.json")

N_VARIANTS_ROUND = 22
IS_YEARS = list(range(2005, 2018))
SURVIVOR = dict(mean_net=0.0, t_stat=2.5, n=150, pos_years=8)
WIDTH_LOOKBACK = 60
HOLD_MIN_V4 = 120          # 24 five-minute bars


def mm(h: int, m: int = 0) -> int:
    return h * 60 + m


SESSION_OPEN = mm(8, 30)
EXIT_MN = mm(15, 8)
EXIT_MAX_MN = mm(15, 15)
FIVE = pd.Timedelta(minutes=5)


# ----------------------------------------------------------------------------- holiday calendar (ex ante)
class USEquityHolidays(AbstractHolidayCalendar):
    rules = [
        Holiday("NewYearsDay", month=1, day=1, observance=sunday_to_monday),
        USMartinLutherKingJr, USPresidentsDay, GoodFriday, USMemorialDay,
        Holiday("IndependenceDay", month=7, day=4, observance=nearest_workday),
        USLaborDay, USThanksgivingDay,
        Holiday("Christmas", month=12, day=25, observance=nearest_workday),
    ]


SPECIAL_CLOSURES = {dt.date(2007, 1, 2), dt.date(2012, 10, 29), dt.date(2012, 10, 30)}


def holiday_keys() -> set:
    hol = USEquityHolidays().holidays(pd.Timestamp("2004-12-01"), pd.Timestamp("2018-01-31"))
    keys = {int(h.strftime("%Y%m%d")) for h in hol}
    keys |= {int(d.strftime("%Y%m%d")) for d in SPECIAL_CLOSURES}
    return keys


# ----------------------------------------------------------------------------- helpers
def ct_fields(bars: pd.DataFrame):
    ct = bars["ct"]
    mn = (ct.dt.hour * 60 + ct.dt.minute).values.astype(np.int32)
    key = (ct.dt.year * 10000 + ct.dt.month * 100 + ct.dt.day).values.astype(np.int64)
    dow = ct.dt.dayofweek.values
    return mn, key, dow


def day_table(b5: pd.DataFrame, b1: pd.DataFrame, range_end_mn: int, hol: set) -> pd.DataFrame:
    """One row per CT date: opening range, width, 15:08 exit-bar position (1-min grid), eligibility."""
    mn5, key5, dow5 = ct_fields(b5)
    n_expected = (range_end_mn - SESSION_OPEN) // 5
    in_rng = (mn5 >= SESSION_OPEN) & (mn5 < range_end_mn)
    sub = b5.loc[in_rng, ["high", "low"]].copy()
    sub["key"] = key5[in_rng]
    g = sub.groupby("key")
    tab = pd.DataFrame({"n_rng": g.size(), "rh": g["high"].max(), "rl": g["low"].min()})
    op = b5.loc[mn5 == SESSION_OPEN, ["open"]].copy()
    op["key"] = key5[mn5 == SESSION_OPEN]
    tab["o0830"] = op.groupby("key")["open"].first()
    tab["width"] = (tab["rh"] - tab["rl"]) / tab["o0830"]
    dw = pd.Series(dow5, index=key5).groupby(level=0).first()
    tab["dow"] = dw.reindex(tab.index)
    tab["holiday"] = [k in hol for k in tab.index]
    # 15:08 exit bar on the 1-minute grid
    mn1, key1, _ = ct_fields(b1)
    m = (mn1 >= EXIT_MN) & (mn1 <= EXIT_MAX_MN)
    ex = pd.Series(np.arange(len(b1))[m], index=key1[m]).groupby(level=0).first()
    tab["x_pos"] = ex.reindex(tab.index)
    tab["range_ok"] = (tab["n_rng"] == n_expected) & tab["o0830"].notna() & (tab["dow"] < 5) & ~tab["holiday"]
    tab["eligible"] = tab["range_ok"] & tab["x_pos"].notna()
    # trailing median width over the prior valid-range days (history only)
    w = tab.loc[tab["range_ok"], "width"]
    med = w.shift(1).rolling(WIDTH_LOOKBACK, min_periods=WIDTH_LOOKBACK).median()
    tab["med60"] = med.reindex(tab.index)
    tab["wide"] = tab["width"] >= tab["med60"]
    return tab


def first_breakout(b5: pd.DataFrame, tab: pd.DataFrame, range_end_mn: int) -> pd.DataFrame:
    """Per CT date: the first 5-min bar (open >= range_end_mn) closing above rh (long) / below rl (short)."""
    mn5, key5, _ = ct_fields(b5)
    rh = tab["rh"].reindex(key5).values
    rl = tab["rl"].reindex(key5).values
    close = b5["close"].values
    after = mn5 >= range_end_mn
    lg = after & (close > rh)
    sh = after & (close < rl)
    sig = lg | sh
    s = pd.DataFrame({"key": key5[sig], "pos5": np.arange(len(b5))[sig], "side": np.where(lg[sig], 1, -1),
                      "t5": b5["open_time"].values[sig]})
    return s.groupby("key").first()


def map_entries(sig: pd.DataFrame, tab: pd.DataFrame, b1: pd.DataFrame) -> pd.DataFrame:
    """Decision bar = last 1-min bar inside the signal 5-min window; fill = open of the next 1-min bar."""
    t1 = b1["open_time"].values
    mn1, key1, _ = ct_fields(b1)
    can_enter = P.entry_mask(b1["open_time"])
    can_hold = P.tradable_mask(b1["open_time"])
    d = sig.join(tab[["rh", "rl", "x_pos", "eligible", "wide"]], how="inner")
    t5 = d["t5"].values.astype("datetime64[ns]")
    dec = np.searchsorted(t1.astype("datetime64[ns]"), t5 + np.timedelta64(5, "m"), side="left") - 1
    d["dec_pos"] = dec
    ok = (dec >= 0) & (t1.astype("datetime64[ns]")[dec] >= t5) & (key1[dec] == d.index.values)
    ent = dec + 1
    ok &= ent < len(b1)
    ent_c = np.minimum(ent, len(b1) - 1)
    ok &= can_enter[ent_c] & can_hold[ent_c] & (key1[ent_c] == d.index.values) & (ent_c < d["x_pos"].fillna(-1).values)
    d["entry_pos"] = ent_c
    d["entry_ok"] = ok & d["eligible"].values
    d["stop"] = np.where(d["side"].values == 1, d["rl"].values, d["rh"].values)
    return d


def run_trades(b1: pd.DataFrame, d: pd.DataFrame, sym: str, hold_min: int | None = None) -> pd.DataFrame:
    """Replicates protocol.backtest_signals (stop first on each bar, exit at next-bar open) with a per-trade stop price."""
    c = P.CONTRACT[sym]
    o, h, l = b1["open"].values, b1["high"].values, b1["low"].values
    t = b1["open_time"].values.astype("datetime64[ns]")
    rows = []
    for key, r in d[d["entry_ok"]].iterrows():
        ei, side, stop, xpos = int(r["entry_pos"]), int(r["side"]), float(r["stop"]), int(r["x_pos"])
        reason_end = "flat"
        if hold_min is not None:
            t_ent = pd.Timestamp(t[ei])
            target = (t_ent.floor("5min") + pd.Timedelta(minutes=hold_min)).to_datetime64()
            tpos = int(np.searchsorted(t, target, side="left"))
            if tpos <= xpos:
                xpos, reason_end = tpos, "time"
        ep = o[ei]
        seg = slice(ei, xpos)
        hit = np.nonzero(l[seg] <= stop)[0] if side == 1 else np.nonzero(h[seg] >= stop)[0]
        if hit.size:
            ix, xp, reason = ei + int(hit[0]), stop, "stop"
        else:
            ix, xp, reason = xpos, o[xpos], reason_end
        gross = side * (xp - ep) * c["mult"]
        rows.append(dict(key=int(key), entry_time=pd.Timestamp(t[ei], tz="UTC"), exit_time=pd.Timestamp(t[ix], tz="UTC"),
                         side=side, entry=ep, exit=xp, stop=stop, gross=gross, net=gross - c["cost_rt"],
                         hold_bars=ix - ei, reason=reason, exit_pos=ix, entry_pos=ei))
    return pd.DataFrame(rows)


def validate_against_protocol(b1: pd.DataFrame, d: pd.DataFrame, tr: pd.DataFrame, sym: str,
                              hold_min: int | None = None) -> int:
    """Re-run every signalled day through protocol.backtest_signals on that day's 1-min bars and compare."""
    mn1, key1, _ = ct_fields(b1)
    t = b1["open_time"].values.astype("datetime64[ns]")
    o = b1["open"].values
    starts = pd.Series(np.arange(len(b1))).groupby(key1).first()
    ends = pd.Series(np.arange(len(b1))).groupby(key1).last()
    mine = tr.set_index("key") if len(tr) else pd.DataFrame()
    n_checked = 0
    n_float_edge = 0
    n_float_edge_touch = 0
    for key, r in d.iterrows():
        if not r["eligible"] or pd.isna(r["x_pos"]):
            continue
        lo, hi = int(starts[key]), int(ends[key]) + 1
        day = b1.iloc[lo:hi].reset_index(drop=True)
        n = len(day)
        entries = np.zeros(n, dtype=bool)
        side = np.zeros(n, dtype=int)
        exits = np.zeros(n, dtype=bool)
        dec, ei, xpos = int(r["dec_pos"]), int(r["entry_pos"]), int(r["x_pos"])
        entries[dec - lo] = True
        side[dec - lo] = int(r["side"])
        exits[xpos - 1 - lo] = True
        if hold_min is not None:
            target = (pd.Timestamp(t[ei]).floor("5min") + pd.Timedelta(minutes=hold_min)).to_datetime64()
            tpos = int(np.searchsorted(t, target, side="left"))
            if tpos <= xpos:
                exits[tpos - 1 - lo] = True
        ep, stop, sd = o[ei], float(r["stop"]), int(r["side"])
        # stop_pct such that the engine's reconstructed level ep*(1-stop_pct*side) equals the range level EXACTLY
        # (otherwise a bar touching the level to the tick may trigger one engine and not the other)
        stop_pct = (ep - stop) / (ep * sd)
        exact = False
        for k in range(0, 6):
            ups = stop_pct
            dns = stop_pct
            for _ in range(k):
                ups, dns = np.nextafter(ups, np.inf), np.nextafter(dns, -np.inf)
            for cand in (ups, dns):
                if ep * (1 - cand * sd) == stop:
                    stop_pct, exact = cand, True
                    break
            if exact:
                break
        ref = P.backtest_signals(day, entries, exits, side, sym, stop_pct=stop_pct)
        if not r["entry_ok"]:
            assert len(ref) == 0, f"{key}: protocol engine traded where this script did not"
            continue
        assert len(ref) >= 1, f"{key}: protocol engine produced no trade"
        a, b = ref.iloc[0], mine.loc[key]
        assert a["entry_time"] == b["entry_time"], (key, a["entry_time"], b["entry_time"])
        assert int(a["side"]) == int(b["side"])
        assert np.isclose(a["entry"], b["entry"]), (key, a["entry"], b["entry"])
        if not exact:
            # the engine's level differs from the range level by an ulp: outcomes must agree unless a bar touched
            # the range level EXACTLY (this script fills the stop on the touch; the engine's level was 1 ulp beyond)
            n_float_edge += 1
            if a["exit_time"] == b["exit_time"] and np.isclose(a["net"], b["net"], atol=1e-6):
                continue
            lvl = ep * (1 - stop_pct * sd)
            assert abs(lvl - stop) < 1e-9 * stop, (key, lvl, stop)
            assert b["reason"] == "stop", (key, a["reason"], b["reason"])
            bar = b1.iloc[int(b["exit_pos"])]
            touched = (bar["low"] == stop) if sd == 1 else (bar["high"] == stop)
            assert touched and ((lvl < stop) if sd == 1 else (lvl > stop)), (key, lvl, stop, bar["low"], bar["high"])
            n_float_edge_touch += 1
            continue
        assert a["exit_time"] == b["exit_time"], (key, a["exit_time"], b["exit_time"], a["reason"], b["reason"])
        assert np.isclose(a["exit"], b["exit"], atol=1e-9), (key, a["exit"], b["exit"])
        assert np.isclose(a["net"], b["net"], atol=1e-6), (key, a["net"], b["net"])
        assert (a["reason"] == "stop") == (b["reason"] == "stop"), (key, a["reason"], b["reason"])
        n_checked += 1
    assert n_checked + n_float_edge == len(tr), (n_checked, n_float_edge, len(tr))
    return n_checked, n_float_edge, n_float_edge_touch


# ----------------------------------------------------------------------------- stats
def evaluate(tr: pd.DataFrame, bars: pd.DataFrame, n_variants: int) -> dict:
    st = P.summarize(tr, bars)
    if st.get("n", 0) == 0:
        st.update(dict(mean_net=0.0, t_stat=0.0, win_rate=0.0, avg_win=0.0, avg_loss=0.0, sharpe_per_trade=0.0,
                       trades_per_day=0.0, by_year={}, n_by_year={}, dsr=0.0, pos_years=0, survivor=False))
        return st
    st["dsr"] = P.deflated_sharpe(st["sharpe_per_trade"], st["n"], n_variants)
    by = st["by_year"]
    st["pos_years"] = int(sum(1 for y in IS_YEARS if by.get(str(y), 0.0) > 0))
    st["survivor"] = bool(st["mean_net"] > SURVIVOR["mean_net"] and st["t_stat"] >= SURVIVOR["t_stat"]
                          and st["n"] >= SURVIVOR["n"] and st["pos_years"] >= SURVIVOR["pos_years"])
    return st


def fmt_by_year(by: dict) -> str:
    return ",".join(f"{y}:{by.get(str(y), 0.0):+.0f}" for y in IS_YEARS)


def trade_info(tr: pd.DataFrame) -> dict:
    if len(tr) == 0:
        return {}
    ect = tr["entry_time"].dt.tz_convert("America/Chicago")
    emn = ect.dt.hour * 60 + ect.dt.minute
    return {"exit_reason": {str(k): int(v) for k, v in tr["reason"].value_counts().items()},
            "n_long": int((tr["side"] == 1).sum()), "n_short": int((tr["side"] == -1).sum()),
            "median_entry_ct": f"{int(emn.median()) // 60:02d}:{int(emn.median()) % 60:02d}",
            "mean_hold_min": float(tr["hold_bars"].mean()),
            "gross_mean": float(tr["gross"].mean())}


# ----------------------------------------------------------------------------- variants (pre-registered)
VARIANTS = [
    ("V1_us_orb30_all", dict(range_end=mm(9, 0), wide=False, hold=None),
     "range=[08:30,09:00) CT 5-min high/low; from 09:00 enter at open of bar after first 5-min close > range high (long) / < range low (short); stop=opposite side of range (bar high/low); exit 15:08 CT; one trade/day"),
    ("V2_us_orb30_wide", dict(range_end=mm(9, 0), wide=True, hold=None),
     "V1 only on days with (range high-low)/open(08:30) >= median of the 60 prior valid-range days' widths"),
    ("V3_us_orb60_all", dict(range_end=mm(9, 30), wide=False, hold=None),
     "as V1 with range=[08:30,09:30) and entries from 09:30 CT"),
    ("V4_us_orb30_2h", dict(range_end=mm(9, 0), wide=False, hold=HOLD_MIN_V4),
     "as V1 but exit at the open of 5-min bar entry+24 (120 min) or the stop, whichever first (15:08 flat if earlier)"),
]


def run_variant(b5: pd.DataFrame, b1: pd.DataFrame, cfg: dict, sym: str, hol: set, validate: bool = True):
    tab = day_table(b5, b1, cfg["range_end"], hol)
    if cfg["wide"]:
        tab["eligible"] = tab["eligible"] & tab["wide"].fillna(False)
    sig = first_breakout(b5, tab, cfg["range_end"])
    d = map_entries(sig, tab, b1)
    tr = run_trades(b1, d, sym, cfg["hold"])
    info = {"n_days_total": int(len(tab)), "n_days_range_ok": int(tab["range_ok"].sum()),
            "n_days_eligible": int(tab["eligible"].sum()), "n_days_with_breakout": int(d["eligible"].sum()),
            "n_days_entered": int(d["entry_ok"].sum()),
            "n_breakout_rejected_entry_rule": int((d["eligible"] & ~d["entry_ok"]).sum())}
    if validate:
        (info["n_validated_vs_protocol_engine"], info["n_validation_float_edge"],
         info["n_validation_float_edge_touch_only"]) = validate_against_protocol(b1, d, tr, sym, cfg["hold"])
    info.update(trade_info(tr))
    return tr, info, d


def main():
    t0 = time.time()
    hol = holiday_keys()
    b5 = load_bars_index("SPX500", "5min", root=ROOT)
    b1 = load_bars_index("SPX500", "1m", root=ROOT)
    assert b1["open_time"].max() <= pd.Timestamp("2017-12-31 23:59:59", tz="UTC")
    print(f"SPX500 5m bars {len(b5)}  1m bars {len(b1)}  {b1['open_time'].min()} -> {b1['open_time'].max()}")

    results = {"family": "orb_continuation", "symbol": "ES", "root": ROOT, "n_variants_family": len(VARIANTS),
               "n_variants_round": N_VARIANTS_ROUND, "survivor_bar": SURVIVOR, "variants": [], "diagnostics": []}
    store = {}
    for name, cfg, rule in VARIANTS:
        tr, info, d = run_variant(b5, b1, cfg, "ES", hol)
        st = evaluate(tr, b1, N_VARIANTS_ROUND)
        st.update(info)
        st["name"], st["rule"] = name, rule
        results["variants"].append(st)
        store[name] = tr
        print(f"{name:18s} n={st['n']:5d} mean_net={st['mean_net']:8.2f} t={st['t_stat']:6.2f} wr={st['win_rate']:.3f} "
              f"aw={st['avg_win']:7.1f} al={st['avg_loss']:7.1f} spt={st['sharpe_per_trade']:.3f} dsr={st['dsr']:.3f} "
              f"tpd={st['trades_per_day']:.3f} pos_years={st['pos_years']}/13 survivor={st['survivor']}")
        print(f"    days eligible={info['n_days_eligible']} breakout={info['n_days_with_breakout']} entered={info['n_days_entered']} "
              f"validated={info.get('n_validated_vs_protocol_engine')} float_edge={info.get('n_validation_float_edge')} (touch-only diffs {info.get('n_validation_float_edge_touch_only')}) reasons={info.get('exit_reason')} long/short={info.get('n_long')}/{info.get('n_short')} "
              f"hold_min={info.get('mean_hold_min', 0):.0f}")
        print("    by_year:", fmt_by_year(st["by_year"]))

    # ------------------------------------------------------------------ post-hoc diagnostics (labelled, never nominated)
    n5 = load_bars_index("NAS100", "5min", root=ROOT)
    n1 = load_bars_index("NAS100", "1m", root=ROOT)
    tr, info, _ = run_variant(n5, n1, VARIANTS[0][1], "NQ", hol, validate=False)
    st = evaluate(tr, n1, N_VARIANTS_ROUND)
    st.update(info)
    st["name"] = "D1_NAS100_twin_of_V1 (post-hoc diagnostic, NQ $/contract)"
    st["rule"] = "V1 rule on NAS100 CFD with NQ costs ($20/pt, $8.78 RT); diagnostic only"
    results["diagnostics"].append(st)
    print(f"[diag] {st['name']}: n={st['n']} mean_net={st['mean_net']:.2f} t={st['t_stat']:.2f} wr={st['win_rate']:.3f} pos_years={st['pos_years']}/13")
    print("    by_year:", fmt_by_year(st["by_year"]))

    v1 = store["V1_us_orb30_all"]
    for lab, s in (("long", 1), ("short", -1)):
        sub = v1[v1["side"] == s].reset_index(drop=True)
        st = evaluate(sub, b1, N_VARIANTS_ROUND)
        st.update(trade_info(sub))
        st["name"] = f"D2_V1_{lab}_only (post-hoc diagnostic)"
        st["rule"] = f"V1 trades with side={s}; diagnostic only"
        results["diagnostics"].append(st)
        print(f"[diag] {st['name']}: n={st['n']} mean_net={st['mean_net']:.2f} t={st['t_stat']:.2f} wr={st['win_rate']:.3f} pos_years={st['pos_years']}/13")
        print("    by_year:", fmt_by_year(st["by_year"]))

    results["survivors"] = [v["name"] for v in results["variants"] if v["survivor"]]
    results["elapsed_s"] = time.time() - t0
    with open(OUT_JSON, "w") as f:
        json.dump(results, f, indent=1, default=str)
    print("survivors:", results["survivors"])
    print("wrote", OUT_JSON, f"({results['elapsed_s']:.1f}s)")
    return results


if __name__ == "__main__":
    main()
