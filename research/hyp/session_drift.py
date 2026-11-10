"""Hypothesis family: session_drift.

Question: do BTC / ETH returns concentrate in a particular trading session (Asia / Europe / US /
CME close / CME open), around the 00:00-UTC funding settlement, or across the Sunday-17:00-CT CME
re-open after the weekend, in a way a Topstep MBT/MET trader could capture?

Variants are pre-specified (listed in VARIANTS below) before any data was examined.  Every variant
that is run is logged, so the count feeds the deflated-Sharpe correction.  All sessions are
time-of-day rules in America/Chicago (CT) unless marked UTC.  Entries/exits are flagged on the bar
BEFORE the desired fill bar so that protocol.backtest_signals fills at the open of the desired bar
(no look-ahead).  No stops / targets: the hypothesis is pure time-of-day exposure.

Run: cd /home/user/j && python3 -m research.hyp.session_drift
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

from research.data import load_bars, load_funding
from research import protocol as P

ROOT = "/home/user/j/data_research/IS"
OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "session_drift_results.json")

SUN, MON, TUE, WED, THU, FRI, SAT = 6, 0, 1, 2, 3, 4, 5
WEEKDAYS = (MON, TUE, WED, THU, FRI)
NIGHTS = (SUN, MON, TUE, WED, THU)          # evenings whose overnight session is tradable


# ----------------------------------------------------------------------------- helpers
def hhmm(h: int, m: int = 0) -> int:
    return h * 60 + m


def shift_back(mask: np.ndarray) -> np.ndarray:
    """entries[i] must be True on the bar BEFORE the fill bar: out[i] = mask[i+1]."""
    out = np.zeros_like(mask, dtype=bool)
    out[:-1] = mask[1:]
    return out


def tod(bars: pd.DataFrame, tz: str = "ct"):
    if tz == "ct":
        t = bars["ct"]
    else:
        t = bars["open_time"]
    return (t.dt.hour * 60 + t.dt.minute).values, t.dt.dayofweek.values


def session_signals(bars, entry_min, exit_min, entry_days, tz="ct"):
    """Enter at the open of the bar whose time-of-day == entry_min (on entry_days), exit at the open of
    the bar whose time-of-day == exit_min (any day).  exit_min=None -> rely on the 15:10 CT forced flat."""
    minutes, dow = tod(bars, tz)
    m_entry = (minutes == entry_min) & np.isin(dow, entry_days)
    entries = shift_back(m_entry)
    if exit_min is None:
        exits = np.zeros(len(bars), dtype=bool)
    else:
        exits = shift_back(minutes == exit_min)
    return entries, exits


def forced_flat_break_only(ts_utc: pd.Series) -> np.ndarray:
    """Corrected forced-flat trigger: True only during the 15:10-17:00 CT daily break.

    protocol.forced_flat_time returns True for EVERY bar with CT time >= 15:10, including the whole
    17:00-23:59 CT evening, so protocol.backtest_signals closes any evening position on its own entry
    bar (gross = 0, net = -cost).  That contradicts its docstring and the Topstep rules (positions
    allowed Sun 17:00 CT -> Fri 15:10 CT, flat only through the 15:10-17:00 break).  We patch the
    module attribute for the duration of each backtest call; behaviour for daytime positions is
    unchanged (exit at the 15:10 CT bar open, reason 'flat')."""
    t = P.ct(ts_utc)
    minutes = (t.dt.hour * 60 + t.dt.minute).values
    return (minutes >= 15 * 60 + 10) & (minutes < 17 * 60)


def run(bars, sym, entries, exits, side, **kw):
    orig = P.forced_flat_time
    P.forced_flat_time = forced_flat_break_only
    try:
        tr = P.backtest_signals(bars, entries, exits, side, sym=sym, **kw)
    finally:
        P.forced_flat_time = orig
    st = P.summarize(tr, bars)
    return tr, st


def weekend_gap(bars: pd.DataFrame) -> np.ndarray:
    """Per-bar array: on the Sunday 16:55 CT bar, the Binance return from the Friday 15:10 CT open
    (the price at which a Topstep trader was forced flat) to the Sunday 16:55 CT close (the last price
    known before the 17:00 CT re-open).  NaN elsewhere."""
    minutes, dow = tod(bars)
    ct = bars["ct"]
    out = np.full(len(bars), np.nan)
    fri_close_mask = (dow == FRI) & (minutes == hhmm(15, 10))
    sun_mask = (dow == SUN) & (minutes == hhmm(16, 55))
    fri = pd.Series(bars["open"].values[fri_close_mask], index=ct.dt.normalize().values[fri_close_mask])
    sun_idx = np.where(sun_mask)[0]
    sun_dates = ct.dt.normalize().values[sun_mask]
    for i, d in zip(sun_idx, sun_dates):
        fd = d - np.timedelta64(2, "D")
        if fd in fri.index:
            out[i] = bars["close"].values[i] / fri.loc[fd] - 1.0
    return out


def prev_funding_sign(bars: pd.DataFrame, funding: pd.DataFrame) -> np.ndarray:
    """Sign of the most recent *settled* funding rate known at each bar's open (strictly backward
    looking: rate at calc_time T is used only for bars with open_time >= T)."""
    f = funding.sort_values("calc_time")
    idx = np.searchsorted(f["calc_time"].values, bars["open_time"].values, side="right") - 1
    rate = np.where(idx >= 0, f["rate"].values[np.clip(idx, 0, None)], np.nan)
    return np.sign(rate)


# ----------------------------------------------------------------------------- variant definitions
# Each: (name, symbol, builder) where builder(bars, aux) -> (entries, exits, side, kwargs, rule_text)
def V_session(entry_h, entry_m, exit_h, exit_m, days, side_val, label):
    def build(bars, aux):
        e, x = session_signals(bars, hhmm(entry_h, entry_m), None if exit_h is None else hhmm(exit_h, exit_m), days)
        side = np.full(len(bars), side_val, dtype=int)
        rule = (f"{'Long' if side_val > 0 else 'Short'} 1 contract at the open of the {entry_h:02d}:{entry_m:02d} CT 5-min bar "
                f"on {label}; exit at the open of the "
                + (f"{exit_h:02d}:{exit_m:02d} CT bar" if exit_h is not None else "15:10 CT bar (Topstep forced flat)")
                + ". No stop/target.")
        return e, x, side, {}, rule
    return build


def V_funding(hours_utc, side_mult, label):
    """Enter at (funding_hour - 1):00 UTC, exit at funding_hour:00 UTC; side = side_mult * sign(last settled rate)."""
    def build(bars, aux):
        minutes, dow = tod(bars, "utc")
        m_entry = np.isin(minutes, [hhmm((h - 1) % 24) for h in hours_utc])
        m_exit = np.isin(minutes, [hhmm(h) for h in hours_utc])
        sgn = prev_funding_sign(bars, aux["funding"])
        side = (side_mult * np.nan_to_num(sgn)).astype(int)
        entries = shift_back(m_entry) & (side != 0)
        exits = shift_back(m_exit)
        rule = (f"At the open of the {label} UTC 5-min bar, enter with side = {'-' if side_mult < 0 else '+'}sign(most recently "
                f"settled Binance funding rate); exit at the open of the funding-settlement bar one hour later. "
                f"Skipped automatically when the window falls outside Topstep hours. No stop/target.")
        return entries, exits, side, {}, rule
    return build


def V_gap(side_mult, min_abs, exit_min, label):
    def build(bars, aux):
        gap = weekend_gap(bars)
        ok = ~np.isnan(gap) & (np.abs(gap) >= min_abs)
        side = (side_mult * np.sign(np.nan_to_num(gap))).astype(int)
        entries = ok & (side != 0)            # flagged on the Sunday 16:55 bar -> fill at 17:00 open
        minutes, _ = tod(bars)
        exits = np.zeros(len(bars), dtype=bool) if exit_min is None else shift_back(minutes == exit_min)
        rule = (f"Weekend gap g = Sunday 16:55 CT close / Friday 15:10 CT open - 1 (Binance perp). "
                f"If |g| >= {min_abs:.2%}, at the Sunday 17:00 CT open enter {'against' if side_mult < 0 else 'with'} the gap "
                f"(side = {'-' if side_mult < 0 else '+'}sign(g)); exit at "
                + (f"the open of the {exit_min // 60:02d}:{exit_min % 60:02d} CT bar" if exit_min else "the Monday 15:10 CT forced flat")
                + ". No stop/target.")
        return entries, exits, side, {}, rule
    return build


VARIANTS = [
    # --- BTC session exposure (long and short of each session) ---
    ("BTC_US_long", "BTCUSDT", V_session(8, 30, None, None, WEEKDAYS, +1, "Mon-Fri")),
    ("BTC_US_short", "BTCUSDT", V_session(8, 30, None, None, WEEKDAYS, -1, "Mon-Fri")),
    ("BTC_Asia_long", "BTCUSDT", V_session(17, 0, 2, 0, NIGHTS, +1, "Sun-Thu evenings")),
    ("BTC_Asia_short", "BTCUSDT", V_session(17, 0, 2, 0, NIGHTS, -1, "Sun-Thu evenings")),
    ("BTC_Europe_long", "BTCUSDT", V_session(2, 0, 8, 30, WEEKDAYS, +1, "Mon-Fri")),
    ("BTC_Europe_short", "BTCUSDT", V_session(2, 0, 8, 30, WEEKDAYS, -1, "Mon-Fri")),
    ("BTC_CMEclose_long", "BTCUSDT", V_session(14, 0, None, None, WEEKDAYS, +1, "Mon-Fri")),
    ("BTC_CMEclose_short", "BTCUSDT", V_session(14, 0, None, None, WEEKDAYS, -1, "Mon-Fri")),
    ("BTC_CMEopen1h_long", "BTCUSDT", V_session(17, 0, 18, 0, NIGHTS, +1, "Sun-Thu evenings")),
    ("BTC_SunMon_long", "BTCUSDT", V_session(17, 0, None, None, (SUN,), +1, "Sunday (hold to Monday 15:10 CT)")),
    # --- funding ---
    ("BTC_fund00_contra", "BTCUSDT", V_funding([0], -1, "23:00")),
    ("BTC_fundAll_contra", "BTCUSDT", V_funding([0, 8, 16], -1, "07:00 / 15:00 / 23:00")),
    # --- weekend gap at the Sunday re-open ---
    ("BTC_gap_fade", "BTCUSDT", V_gap(-1, 0.0, None, "")),
    ("BTC_gap_fade_1pct", "BTCUSDT", V_gap(-1, 0.01, None, "")),
    ("BTC_gap_follow", "BTCUSDT", V_gap(+1, 0.0, None, "")),
    # --- ETH ---
    ("ETH_US_long", "ETHUSDT", V_session(8, 30, None, None, WEEKDAYS, +1, "Mon-Fri")),
    ("ETH_US_short", "ETHUSDT", V_session(8, 30, None, None, WEEKDAYS, -1, "Mon-Fri")),
    ("ETH_Asia_long", "ETHUSDT", V_session(17, 0, 2, 0, NIGHTS, +1, "Sun-Thu evenings")),
    ("ETH_Asia_short", "ETHUSDT", V_session(17, 0, 2, 0, NIGHTS, -1, "Sun-Thu evenings")),
    ("ETH_fund00_contra", "ETHUSDT", V_funding([0], -1, "23:00")),
    ("ETH_gap_fade", "ETHUSDT", V_gap(-1, 0.0, None, "")),
]


# ----------------------------------------------------------------------------- diagnostics (logged, not variants)
def hour_of_day_table(bars: pd.DataFrame) -> pd.DataFrame:
    """Mean 5-min log return by CT hour, in bp, with t-stat; informational only (computed AFTER variants were fixed)."""
    r = np.log(bars["close"] / bars["open"]).values * 1e4
    h = bars["ct"].dt.hour.values
    df = pd.DataFrame({"h": h, "r": r})
    g = df.groupby("h")["r"]
    out = pd.DataFrame({"mean_bp": g.mean(), "t": g.mean() / (g.std() / np.sqrt(g.count())), "n": g.count()})
    return out


def main():
    results = []
    cache = {}
    for name, sym, build in VARIANTS:
        if sym not in cache:
            cache[sym] = {"bars": load_bars(sym, "5min", root=ROOT), "funding": load_funding(sym, root=ROOT)}
        bars, aux = cache[sym]["bars"], cache[sym]
        entries, exits, side, kw, rule = build(bars, aux)
        tr, st = run(bars, sym, entries, exits, side, **kw)
        rec = {"name": name, "symbol": sym, "rule": rule, "n": int(st.get("n", 0))}
        if st.get("n", 0) > 0:
            rec.update({k: st[k] for k in ("trades_per_day", "mean_net", "t_stat", "ci95_low", "ci95_high", "win_rate",
                                           "avg_win", "avg_loss", "sharpe_per_trade", "total_net", "gross_mean",
                                           "max_drawdown")})
            rec["by_year"] = {k: round(v, 1) for k, v in st["by_year"].items()}
            rec["n_by_year"] = st["n_by_year"]
            rec["reasons"] = tr["reason"].value_counts().to_dict()
            rec["dsr"] = P.deflated_sharpe(st["sharpe_per_trade"], st["n"], len(VARIANTS))
        results.append(rec)
        print(f"{name:22s} {sym:8s} n={rec['n']:5d} mean_net={rec.get('mean_net', 0):8.2f} t={rec.get('t_stat', 0):6.2f} "
              f"wr={rec.get('win_rate', 0):.3f} tpd={rec.get('trades_per_day', 0):.2f} by_year={rec.get('by_year')}")
        sys.stdout.flush()

    # ---- diagnostics
    diag = {}
    for sym in cache:
        bars = cache[sym]["bars"]
        tab = hour_of_day_table(bars)
        diag[f"{sym}_hour_of_day_CT"] = tab.round(3).to_dict(orient="index")
        print(f"\n{sym} mean 5-min return by CT hour (bp) / t-stat:")
        print(tab.round(3).to_string())
    # weekday breakdown of BTC US long and ETH US long (diagnostic)
    for name, sym, build in VARIANTS:
        if name in ("BTC_US_long", "ETH_US_long", "BTC_Asia_long"):
            bars, aux = cache[sym]["bars"], cache[sym]
            entries, exits, side, kw, rule = build(bars, aux)
            tr, _ = run(bars, sym, entries, exits, side, **kw)
            wd = tr.groupby(tr["entry_time"].dt.tz_convert("America/Chicago").dt.dayofweek)["net"].agg(["count", "mean", "sum"])
            wd["t"] = tr.groupby(tr["entry_time"].dt.tz_convert("America/Chicago").dt.dayofweek)["net"].apply(
                lambda x: x.mean() / (x.std() / np.sqrt(len(x))) if x.std() > 0 else 0.0)
            diag[f"{name}_by_weekday"] = wd.round(2).to_dict(orient="index")
            print(f"\n{name} by CT weekday (0=Mon):\n{wd.round(2).to_string()}")
            # ETF-era slice
            etf = tr[tr["entry_time"] >= pd.Timestamp("2024-01-11", tz="UTC")]
            if len(etf):
                diag[f"{name}_etf_era"] = {"n": int(len(etf)), "mean_net": float(etf["net"].mean()),
                                           "t": float(etf["net"].mean() / (etf["net"].std() / np.sqrt(len(etf)))) if etf["net"].std() > 0 else 0.0}
                print(f"{name} ETF era (>= 2024-01-11): n={len(etf)} mean_net={etf['net'].mean():.2f} t={diag[f'{name}_etf_era']['t']:.2f}")

    with open(OUT_JSON, "w") as fh:
        json.dump({"n_variants": len(VARIANTS), "variants": results, "diagnostics": diag}, fh, indent=1, default=str)
    print(f"\nwrote {OUT_JSON}; n_variants={len(VARIANTS)}")


if __name__ == "__main__":
    main()
