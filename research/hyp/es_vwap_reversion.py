"""Hypothesis family: vwap_reversion  (ES, in-sample only, ROOT = data_research/IS, 2005-01 .. 2017-12)

Cash-session VWAP mean reversion on the E-mini S&P 500.  Price proxy: Oanda SPX500 CFD minute bars (UTC
timestamps -> America/Chicago).  P&L per ONE ES contract ($50/pt, $16.28 round-turn cost = $3.78 commission +
one 0.25 tick of slippage).

PRE-REGISTERED VARIANTS (all times CT; all three are run and reported, none dropped)
  VWAP = cumulative sum(typical price x volume) / cumulative sum(volume) over the 5-min bars of the US cash
  session, anchored at the 08:30 CT bar (bars with open time in [08:30, 15:10) of the same CT date); typical
  price = (high+low+close)/3; volume = the bar's tick count (if a session has a zero-volume bar, that session
  uses equal weights; the IS data has none).  dev = close/VWAP - 1.
  V1 band_030          : from the 09:30 CT bar, dev >= +0.30% -> short, dev <= -0.30% -> long, at the next bar
                         open; target = VWAP (exit when the bar's range touches the VWAP level known at that
                         time), stop = 0.30% beyond entry (bar high/low, stop checked first); exit at 15:08 CT
                         at the latest; one trade at a time (re-entry allowed after an exit).
  V2 band_020          : thresholds 0.20% / stop 0.20%.
  V3 band_030_rangeday : as V1 only on days whose first-hour range (max high - min low of the twelve 5-min bars
                         with open in [08:30, 09:30), in index points) is below the median of the first-hour
                         ranges of the 20 previous valid-range days (strictly before the day; 20 observations
                         required).

IMPLEMENTATION
  * Signals are computed on the 5-minute grid (research.data_index.load_bars_index(..., "5min"): CT-aligned,
    bars only where quotes changed).  Signal bars: 5-min bars with CT open time >= 09:30 inside the session
    (the 09:30 bar is the first that can signal, so the first possible entry is 09:35 CT).  Execution is
    simulated on the 1-minute grid (same parquet) so the 15:08 CT exit is exact: the decision bar of 5-min bar
    [t, t+5) is the last 1-min bar inside that window and the fill is the open of the NEXT 1-min bar (= the open
    of the next 5-min bar).  Signals from bar i are acted on at the open of bar i+1 - no look-ahead.
  * Target level: while the position is inside 5-min window j, the target is the VWAP at the close of the last
    5-min session bar that opened BEFORE window j (i.e. the VWAP known when window j started; for the entry
    window this is the signal bar's VWAP).  Long: exit at the target when a 1-min bar's high >= target; short:
    when low <= target; filled AT the target level (resting limit order).  No target before 08:30 (NaN).
  * Stop: price = entry x (1 - band x side), checked on every 1-min bar from the fill bar through the bar before
    the exit bar (bar high/low), checked before the target on the same bar and filled at the stop price
    (conservative, exactly as protocol.backtest_signals).
  * Exit 15:08: fill at the open of the first 1-min bar with CT time in [15:08, 15:10] on the same date (so the
    15:10 CT hard flat is never breached; a day without such a bar is ineligible).
  * One trade at a time: after an exit at 1-min bar ix, the next entry needs a decision bar >= ix+1 (the
    protocol engine's bar sequencing on the 1-min grid).
  * Eligible days (known ex ante): weekdays that are not US equity-market holidays (NYSE/CME rules incl. Good
    Friday and the 2007-01-02 / 2012-10-29 / 2012-10-30 closures), with the 08:30 CT 5-min bar present (VWAP
    anchor) and a 1-min bar in [15:08, 15:10] CT (missing bars = no trade; holiday/half-day sessions lack the
    15:08 bar).  Entry fill must satisfy protocol.entry_mask (fill < 15:08 CT, same date, before the exit bar).
  * Engine: `run_day` replicates protocol.backtest_signals (stop first on each bar, fill at next-bar open) with a
    moving target level.  Cross-check (`validate_against_protocol`): every eligible day with signals is re-run
    through protocol.backtest_signals on that day's 1-min bars (same decision bars, stop_pct = band, exit flag
    at the bar before the 15:08 bar, NO target); the trade sequences must agree exactly up to and including the
    first trade that this script closed at the target (entry time/price/side always; exit time/price/net for
    stop and flat exits).  Any mismatch aborts the run.  Target exits are checked internally (the exit bar
    touches the level; no earlier bar touched the stop or the level).
  * Costs: protocol.CONTRACT["ES"].  Stats: protocol.summarize / protocol.deflated_sharpe with the 22
    pre-registered ES variants of this round.

Survivor bar (pre-registered): mean_net > 0, t_stat >= 2.5, n >= 150, net P&L > 0 in >= 8 of the 13 years.

Post-hoc diagnostics (clearly labelled, never nominated):
  D1 NAS100 (Nasdaq-100 CFD) twin of V1 with NQ costs ($20/pt, $8.78 RT).
  D2 V1's own trades split by side (long-only / short-only).

Run:  cd /home/user/j && python3 -m research.hyp.es_vwap_reversion
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
OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "es_vwap_reversion_results.json")

N_VARIANTS_ROUND = 22
IS_YEARS = list(range(2005, 2018))
SURVIVOR = dict(mean_net=0.0, t_stat=2.5, n=150, pos_years=8)
RANGE_LOOKBACK = 20


def mm(h: int, m: int = 0) -> int:
    return h * 60 + m


SESSION_OPEN = mm(8, 30)
FIRST_HOUR_END = mm(9, 30)
SIGNAL_FROM = mm(9, 30)
SESSION_END = mm(15, 10)
EXIT_MN = mm(15, 8)
EXIT_MAX_MN = mm(15, 10)
FIVE = np.timedelta64(5, "m")
N_FIRST_HOUR_BARS = (FIRST_HOUR_END - SESSION_OPEN) // 5


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


def utc_ns(bars: pd.DataFrame) -> np.ndarray:
    return bars["open_time"].values.astype("datetime64[ns]")


def session_vwap(b5: pd.DataFrame) -> dict:
    """Per 5-min bar: session VWAP anchored at 08:30 CT (cumulative over bars with CT open in [08:30, 15:10) of
    the same CT date), dev = close/VWAP - 1.  NaN outside the session."""
    mn, key, _ = ct_fields(b5)
    in_sess = (mn >= SESSION_OPEN) & (mn < SESSION_END)
    h, l, c = b5["high"].values, b5["low"].values, b5["close"].values
    tp = (h + l + c) / 3.0
    vol = b5["volume"].values.astype(float)
    w = vol.copy()
    # equal weights for any session that contains a zero-volume bar (none in the IS data; recorded)
    df = pd.DataFrame({"key": key[in_sess], "zero": (vol[in_sess] <= 0)})
    zero_days = set(df.loc[df["zero"], "key"].unique().tolist())
    n_zero_vol_bars = int(df["zero"].sum())
    if zero_days:
        eq = in_sess & np.isin(key, list(zero_days))
        w[eq] = 1.0
    s = pd.DataFrame({"key": key[in_sess], "w": w[in_sess], "wtp": (w * tp)[in_sess]})
    cw = s.groupby("key")["w"].cumsum().values
    cwtp = s.groupby("key")["wtp"].cumsum().values
    vwap = np.full(len(b5), np.nan)
    vwap[in_sess] = cwtp / cw
    dev = c / vwap - 1.0
    first_mn = pd.Series(mn[in_sess]).groupby(key[in_sess]).first()
    return dict(vwap=vwap, dev=dev, in_sess=in_sess, mn=mn, key=key, has_0830=(first_mn == SESSION_OPEN),
                n_zero_vol_bars=n_zero_vol_bars, n_zero_vol_days=len(zero_days))


def day_table(b5: pd.DataFrame, b1: pd.DataFrame, feats: dict, hol: set) -> pd.DataFrame:
    """One row per CT date: eligibility, first-hour range + trailing-20-day median (history only), 15:08 exit bar."""
    mn5, key5, dow5 = feats["mn"], feats["key"], ct_fields(b5)[2]
    keys = np.unique(key5[feats["in_sess"]])
    tab = pd.DataFrame(index=pd.Index(keys, name="key"))
    tab["has_0830"] = feats["has_0830"].reindex(keys).fillna(False).astype(bool)
    dw = pd.Series(dow5, index=key5).groupby(level=0).first()
    tab["dow"] = dw.reindex(keys)
    tab["holiday"] = [k in hol for k in keys]
    fh = (mn5 >= SESSION_OPEN) & (mn5 < FIRST_HOUR_END)
    sub = b5.loc[fh, ["high", "low"]].copy()
    sub["key"] = key5[fh]
    g = sub.groupby("key")
    tab["n_fh"] = g.size().reindex(keys).fillna(0).astype(int)
    tab["fh_range"] = (g["high"].max() - g["low"].min()).reindex(keys)
    tab["range_ok"] = (tab["n_fh"] == N_FIRST_HOUR_BARS) & tab["fh_range"].notna()
    # 15:08 exit bar on the 1-minute grid
    mn1, key1, _ = ct_fields(b1)
    m = (mn1 >= EXIT_MN) & (mn1 <= EXIT_MAX_MN)
    ex = pd.Series(np.arange(len(b1))[m], index=key1[m]).groupby(level=0).first()
    tab["x_pos"] = ex.reindex(keys)
    tab["eligible"] = tab["has_0830"] & (tab["dow"] < 5) & ~tab["holiday"] & tab["x_pos"].notna()
    # trailing median of the first-hour range over the 20 previous valid-range days (strictly before the day)
    r = tab.loc[tab["range_ok"], "fh_range"]
    med = r.shift(1).rolling(RANGE_LOOKBACK, min_periods=RANGE_LOOKBACK).median()
    tab["med20"] = med.reindex(keys)
    tab["rangeday"] = tab["range_ok"] & (tab["fh_range"] < tab["med20"])
    return tab


def signal_bars(b5: pd.DataFrame, feats: dict, band: float) -> pd.DataFrame:
    """5-min signal bars: in-session, CT open >= 09:30, |dev| >= band; side = -sign(dev)."""
    mn, key, dev = feats["mn"], feats["key"], feats["dev"]
    sig = feats["in_sess"] & (mn >= SIGNAL_FROM) & np.isfinite(dev) & (np.abs(dev) >= band)
    return pd.DataFrame({"key": key[sig], "pos5": np.arange(len(b5))[sig], "side": np.where(dev[sig] > 0, -1, 1),
                         "t5": utc_ns(b5)[sig], "dev": dev[sig]})


def map_decisions(sig: pd.DataFrame, b1: pd.DataFrame) -> pd.DataFrame:
    """Decision bar = last 1-min bar inside the signal 5-min window (must lie in the window and on the same date)."""
    t1 = utc_ns(b1)
    _, key1, _ = ct_fields(b1)
    dec = np.searchsorted(t1, sig["t5"].values + FIVE, side="left") - 1
    ok = (dec >= 0) & (t1[np.maximum(dec, 0)] >= sig["t5"].values) & (key1[np.maximum(dec, 0)] == sig["key"].values)
    out = sig.copy()
    out["dec_pos"] = dec
    out["dec_ok"] = ok
    return out


def target_levels(b1: pd.DataFrame, b5: pd.DataFrame, feats: dict) -> np.ndarray:
    """Per 1-min bar: the session VWAP at the close of the last 5-min session bar that opened before this bar's
    5-min window (same CT date); NaN when there is none."""
    t1 = utc_ns(b1)
    _, key1, _ = ct_fields(b1)
    sess = feats["in_sess"]
    t5s = utc_ns(b5)[sess]
    v5s = feats["vwap"][sess]
    k5s = feats["key"][sess]
    floor5 = t1 - (t1 - np.datetime64("1970-01-01T00:00:00", "ns")) % FIVE
    idx = np.searchsorted(t5s, floor5, side="left") - 1
    valid = idx >= 0
    idx_c = np.maximum(idx, 0)
    valid &= k5s[idx_c] == key1
    return np.where(valid, v5s[idx_c], np.nan)


# ----------------------------------------------------------------------------- engine
def run_day(o, h, l, tgt, can_enter, decs, sides, xpos, stop_pct, mult, cost):
    """protocol.backtest_signals semantics on one day's 1-min bars with a moving target level.
    decs: decision-bar positions (ascending), sides: +1/-1; xpos: 15:08 exit bar.  Returns trade dicts."""
    rows = []
    i_free = 0
    for dec, sd in zip(decs, sides):
        if dec < i_free:
            continue
        ei = dec + 1
        if ei >= xpos or not can_enter[ei]:
            continue
        ep = o[ei]
        sp = ep * (1 - stop_pct * sd)
        seg = slice(ei, xpos)
        if sd == 1:
            s_hit = np.flatnonzero(l[seg] <= sp)
            t_hit = np.flatnonzero(h[seg] >= tgt[seg])
        else:
            s_hit = np.flatnonzero(h[seg] >= sp)
            t_hit = np.flatnonzero(l[seg] <= tgt[seg])
        s0 = int(s_hit[0]) if s_hit.size else None
        t0 = int(t_hit[0]) if t_hit.size else None
        if s0 is not None and (t0 is None or s0 <= t0):
            ix, xp, reason = ei + s0, sp, "stop"
        elif t0 is not None:
            ix, xp, reason = ei + t0, float(tgt[ei + t0]), "target"
        else:
            ix, xp, reason = xpos, o[xpos], "flat"
        gross = sd * (xp - ep) * mult
        rows.append(dict(dec_pos=dec, entry_pos=ei, exit_pos=ix, side=sd, entry=ep, exit=xp, stop=sp,
                         target_at_exit=float(tgt[ix]) if ix < len(tgt) else np.nan,
                         gross=gross, net=gross - cost, reason=reason))
        i_free = ix + 1 if reason != "flat" else xpos
    return rows


def run_trades(b1: pd.DataFrame, tab: pd.DataFrame, d: pd.DataFrame, tgt: np.ndarray, sym: str,
               stop_pct: float) -> pd.DataFrame:
    c = P.CONTRACT[sym]
    o, h, l = b1["open"].values, b1["high"].values, b1["low"].values
    t = utc_ns(b1)
    can_enter = P.entry_mask(b1["open_time"])
    rows = []
    dd = d[d["dec_ok"]].sort_values(["key", "dec_pos"])
    for key, g in dd.groupby("key", sort=True):
        if key not in tab.index or not tab.at[key, "eligible"]:
            continue
        xpos = int(tab.at[key, "x_pos"])
        decs = g["dec_pos"].values.astype(int)
        sides = g["side"].values.astype(int)
        for r in run_day(o, h, l, tgt, can_enter, decs, sides, xpos, stop_pct, c["mult"], c["cost_rt"]):
            r["key"] = int(key)
            r["entry_time"] = pd.Timestamp(t[r["entry_pos"]], tz="UTC")
            r["exit_time"] = pd.Timestamp(t[r["exit_pos"]], tz="UTC")
            r["hold_bars"] = r["exit_pos"] - r["entry_pos"]
            r["hold_min"] = float((t[r["exit_pos"]] - t[r["entry_pos"]]) / np.timedelta64(1, "m"))
            rows.append(r)
    cols = ["key", "entry_time", "exit_time", "side", "entry", "exit", "stop", "target_at_exit", "gross", "net",
            "hold_bars", "hold_min", "reason", "dec_pos", "entry_pos", "exit_pos"]
    return pd.DataFrame(rows, columns=cols)


def validate_against_protocol(b1: pd.DataFrame, tab: pd.DataFrame, d: pd.DataFrame, tgt: np.ndarray,
                              tr: pd.DataFrame, sym: str, stop_pct: float) -> dict:
    """Re-run every eligible day with decision bars through protocol.backtest_signals on that day's 1-min bars
    (stop_pct = band, exit flag at x_pos-1, no target) and compare trade by trade up to and including the first
    target exit of this script.  Also check every target exit internally."""
    _, key1, _ = ct_fields(b1)
    o, h, l = b1["open"].values, b1["high"].values, b1["low"].values
    starts = pd.Series(np.arange(len(b1))).groupby(key1).first()
    ends = pd.Series(np.arange(len(b1))).groupby(key1).last()
    dd = d[d["dec_ok"]].sort_values(["key", "dec_pos"])
    n_days = n_trades_full = n_trades_entry_only = n_days_all_match = n_trades_after_target = 0
    for key, g in dd.groupby("key", sort=True):
        if key not in tab.index or not tab.at[key, "eligible"]:
            continue
        lo, hi = int(starts[key]), int(ends[key]) + 1
        day = b1.iloc[lo:hi].reset_index(drop=True)
        n = len(day)
        entries = np.zeros(n, dtype=bool)
        side = np.zeros(n, dtype=int)
        exits = np.zeros(n, dtype=bool)
        xpos = int(tab.at[key, "x_pos"])
        for dec, sd in zip(g["dec_pos"].values, g["side"].values):
            entries[int(dec) - lo] = True
            side[int(dec) - lo] = int(sd)
        exits[xpos - 1 - lo] = True
        ref = P.backtest_signals(day, entries, exits, side, sym, stop_pct=stop_pct)
        mine = tr[tr["key"] == key].sort_values("entry_pos").reset_index(drop=True)
        n_days += 1
        all_match = True
        for k in range(len(mine)):
            b = mine.iloc[k]
            assert k < len(ref), (key, "protocol engine has fewer trades", k, len(ref))
            a = ref.iloc[k]
            assert a["entry_time"] == b["entry_time"], (key, k, a["entry_time"], b["entry_time"])
            assert int(a["side"]) == int(b["side"]), (key, k)
            assert a["entry"] == b["entry"], (key, k, a["entry"], b["entry"])
            if b["reason"] == "target":
                # internal check of the target exit
                ei, ix, sd = int(b["entry_pos"]), int(b["exit_pos"]), int(b["side"])
                lvl = tgt[ix]
                assert np.isfinite(lvl) and b["exit"] == lvl
                assert (h[ix] >= lvl) if sd == 1 else (l[ix] <= lvl), (key, k)
                if ix > ei:
                    pre = slice(ei, ix)
                    if sd == 1:
                        assert not np.any(l[pre] <= b["stop"]) and not np.any(h[pre] >= tgt[pre]), (key, k)
                    else:
                        assert not np.any(h[pre] >= b["stop"]) and not np.any(l[pre] <= tgt[pre]), (key, k)
                assert not ((l[ix] <= b["stop"]) if sd == 1 else (h[ix] >= b["stop"])), (key, k, "stop same bar")
                # the protocol trade (no target) cannot have ended before this script's target exit
                assert a["exit_time"] >= b["exit_time"], (key, k, a["exit_time"], b["exit_time"])
                n_trades_entry_only += 1
                n_trades_after_target += len(mine) - (k + 1)   # same-day trades after a target exit: timeline differs
                all_match = False
                break
            assert a["exit_time"] == b["exit_time"], (key, k, a["reason"], b["reason"], a["exit_time"], b["exit_time"])
            assert a["exit"] == b["exit"], (key, k, a["exit"], b["exit"])
            assert np.isclose(a["net"], b["net"], atol=1e-6), (key, k, a["net"], b["net"])
            assert (a["reason"] == "stop") == (b["reason"] == "stop"), (key, k, a["reason"], b["reason"])
            n_trades_full += 1
        if all_match:
            assert len(ref) == len(mine), (key, len(ref), len(mine))
            n_days_all_match += 1
    assert n_trades_full + n_trades_entry_only + n_trades_after_target == len(tr), \
        (n_trades_full, n_trades_entry_only, n_trades_after_target, len(tr))
    return dict(n_validation_days=n_days, n_validated_full_vs_protocol_engine=n_trades_full,
                n_validated_entry_only_target_exit=n_trades_entry_only,
                n_not_comparable_after_target_exit=n_trades_after_target,
                n_validation_days_identical_sequence=n_days_all_match)


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
    by_reason = {str(k): float(v) for k, v in tr.groupby("reason")["net"].mean().items()}
    return {"exit_reason": {str(k): int(v) for k, v in tr["reason"].value_counts().items()},
            "mean_net_by_reason": by_reason,
            "n_long": int((tr["side"] == 1).sum()), "n_short": int((tr["side"] == -1).sum()),
            "n_days_traded": int(tr["key"].nunique()),
            "median_entry_ct": f"{int(emn.median()) // 60:02d}:{int(emn.median()) % 60:02d}",
            "mean_hold_min": float(tr["hold_min"].mean()), "median_hold_min": float(tr["hold_min"].median()),
            "gross_mean": float(tr["gross"].mean())}


# ----------------------------------------------------------------------------- variants (pre-registered)
VARIANTS = [
    ("V1_band_030", dict(band=0.003, rangeday=False),
     "5-min cash-session VWAP (anchor 08:30 CT, tp=(H+L+C)/3, w=tick volume); from the 09:30 CT bar, dev=close/VWAP-1 >= +0.30% -> short, <= -0.30% -> long at next bar open; target = VWAP level known at the time (touch, fill at level), stop = entry x (1 -/+ 0.30%) checked first; exit 15:08 CT; one trade at a time"),
    ("V2_band_020", dict(band=0.002, rangeday=False),
     "as V1 with entry threshold 0.20% and stop 0.20%"),
    ("V3_band_030_rangeday", dict(band=0.003, rangeday=True),
     "as V1 only on days whose first-hour range (max high - min low of the 08:30-09:25 5-min bars, index points) < median first-hour range of the 20 previous valid-range days"),
]


def run_variant(b5: pd.DataFrame, b1: pd.DataFrame, feats: dict, tab: pd.DataFrame, tgt: np.ndarray, cfg: dict,
                sym: str, validate: bool = True):
    tab_v = tab.copy()
    if cfg["rangeday"]:
        tab_v["eligible"] = tab_v["eligible"] & tab_v["rangeday"].fillna(False).astype(bool)
    sig = signal_bars(b5, feats, cfg["band"])
    d = map_decisions(sig, b1)
    tr = run_trades(b1, tab_v, d, tgt, sym, cfg["band"])
    elig_keys = set(tab_v.index[tab_v["eligible"]])
    info = {"n_days_total": int(len(tab_v)), "n_days_eligible": int(tab_v["eligible"].sum()),
            "n_signal_bars_eligible_days": int(d["key"].isin(elig_keys).sum()),
            "n_days_with_signal": int(d.loc[d["key"].isin(elig_keys), "key"].nunique())}
    if validate:
        info.update(validate_against_protocol(b1, tab_v, d, tgt, tr, sym, cfg["band"]))
    info.update(trade_info(tr))
    return tr, info, d


def prepare(sym5: str):
    b5 = load_bars_index(sym5, "5min", root=ROOT)
    b1 = load_bars_index(sym5, "1m", root=ROOT)
    assert b1["open_time"].max() <= pd.Timestamp("2017-12-31 23:59:59", tz="UTC")
    feats = session_vwap(b5)
    tab = day_table(b5, b1, feats, holiday_keys())
    tgt = target_levels(b1, b5, feats)
    return b5, b1, feats, tab, tgt


def main():
    t0 = time.time()
    b5, b1, feats, tab, tgt = prepare("SPX500")
    print(f"SPX500 5m bars {len(b5)}  1m bars {len(b1)}  {b1['open_time'].min()} -> {b1['open_time'].max()}  "
          f"zero-volume session bars={feats['n_zero_vol_bars']}  days={len(tab)} eligible={int(tab['eligible'].sum())} "
          f"rangeday={int(tab['rangeday'].sum())}")

    results = {"family": "vwap_reversion", "symbol": "ES", "root": ROOT, "n_variants_family": len(VARIANTS),
               "n_variants_round": N_VARIANTS_ROUND, "survivor_bar": SURVIVOR,
               "data_notes": {"n_zero_vol_session_bars": feats["n_zero_vol_bars"],
                              "n_days_eligible": int(tab["eligible"].sum()),
                              "n_days_rangeday": int((tab["eligible"] & tab["rangeday"]).sum())},
               "variants": [], "diagnostics": []}
    store = {}
    for name, cfg, rule in VARIANTS:
        tr, info, _ = run_variant(b5, b1, feats, tab, tgt, cfg, "ES")
        st = evaluate(tr, b1, N_VARIANTS_ROUND)
        st.update(info)
        st["name"], st["rule"] = name, rule
        results["variants"].append(st)
        store[name] = tr
        print(f"{name:22s} n={st['n']:5d} mean_net={st['mean_net']:8.2f} t={st['t_stat']:6.2f} wr={st['win_rate']:.3f} "
              f"aw={st['avg_win']:7.1f} al={st['avg_loss']:7.1f} spt={st['sharpe_per_trade']:.3f} dsr={st['dsr']:.3f} "
              f"tpd={st['trades_per_day']:.3f} pos_years={st['pos_years']}/13 survivor={st['survivor']}")
        print(f"    days eligible={info['n_days_eligible']} with_signal={info['n_days_with_signal']} traded={info.get('n_days_traded')} "
              f"signal_bars={info['n_signal_bars_eligible_days']} validated_full={info.get('n_validated_full_vs_protocol_engine')} "
              f"entry_only(target)={info.get('n_validated_entry_only_target_exit')} identical_days={info.get('n_validation_days_identical_sequence')}/{info.get('n_validation_days')} "
              f"reasons={info.get('exit_reason')} net_by_reason={ {k: round(v, 1) for k, v in info.get('mean_net_by_reason', {}).items()} } "
              f"long/short={info.get('n_long')}/{info.get('n_short')} hold_min={info.get('mean_hold_min', 0):.0f} entry_ct={info.get('median_entry_ct')}")
        print("    by_year:", fmt_by_year(st["by_year"]))

    # ------------------------------------------------------------------ post-hoc diagnostics (labelled, never nominated)
    n5, n1, nfeats, ntab, ntgt = prepare("NAS100")
    tr, info, _ = run_variant(n5, n1, nfeats, ntab, ntgt, VARIANTS[0][1], "NQ", validate=False)
    st = evaluate(tr, n1, N_VARIANTS_ROUND)
    st.update(info)
    st["name"] = "D1_NAS100_twin_of_V1 (post-hoc diagnostic, NQ $/contract)"
    st["rule"] = "V1 rule on NAS100 CFD with NQ costs ($20/pt, $8.78 RT); diagnostic only"
    results["diagnostics"].append(st)
    print(f"[diag] {st['name']}: n={st['n']} mean_net={st['mean_net']:.2f} t={st['t_stat']:.2f} wr={st['win_rate']:.3f} pos_years={st['pos_years']}/13 reasons={info.get('exit_reason')}")
    print("    by_year:", fmt_by_year(st["by_year"]))

    v1 = store["V1_band_030"]
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
