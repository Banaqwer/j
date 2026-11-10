"""Hypothesis family: overnight_drift (ES round, pre-registered).

Question: does the overnight return anomaly of equity indices (Lou, Polk & Skouras 2019; Knuteson) --
index returns accrue while the cash market is closed and the day session is flat-to-negative -- survive
Topstep execution on the E-mini S&P 500 (ES, $50/pt, $16.28 per round turn) when proxied by Oanda SPX500
CFD minute bars?  In-sample only: 2005-01-01 .. 2017-12-31 (ROOT = data_research/IS).

PRE-REGISTERED VARIANTS (all run, all reported, none added, none dropped; times are America/Chicago):
  V1 long_overnight_all            : long at the 17:00 bar (Sun-Thu); exit at the 08:30 bar next day.
  V2 long_overnight_after_down_day : as V1 only when the cash session return of the SAME calendar day as the
                                     entry (open 08:30 -> open 15:08) was negative.
  V3 long_overnight_to_0900        : as V1 but exit at the 09:00 bar.
  V4 short_intraday                : short at the 09:00 bar (Mon-Fri); exit at the 15:08 bar.

Implementation conventions (fixed before any P&L was looked at):
  * Execution grid = 1-minute bars (load_bars_index(.., "1m")).  The pre-registered 15:08 CT exit does not
    exist on a 5-minute grid; the 17:00 / 08:30 / 09:00 opens are identical on both grids.
  * Oanda bars exist only when the quote changed.  "The HH:MM bar" is therefore the first 1-minute bar whose
    open time is >= HH:MM CT on that calendar date.  For an ENTRY that bar must open within 5 minutes of the
    scheduled time (the width of a 5-minute bar), otherwise the day is a no-trade.  For an EXIT the position
    is closed at the open of the first bar >= the scheduled instant whenever it comes; the protocol forced
    flat at 15:10 CT (and before the weekend) remains active as a backstop.  No price is ever invented.
  * Protocol rule "signal computed from bar i is acted on at the open of bar i+1": entries/exits are flagged on
    the bar immediately preceding the fill bar in the bar sequence, and protocol.backtest_signals fills at
    that next bar's open.  Nothing in the signal uses information after the flag bar.
  * V2 conditioning: r_cash(d) = open(15:08 bar of d) / open(08:30 bar of d) - 1, with both bars defined as
    above (entry-style 5-minute tolerance); r_cash < 0 strictly.  Both opens are history at 16:59 CT.
    Sunday has no cash session on the same calendar date, so under the literal pre-registered text V2 never
    enters on Sunday (the alternative reading, Sunday conditioned on Friday's session, is diagnostic D2).
  * V1/V3 entries Sun-Thu 17:00 CT; V4 entries Mon-Fri 09:00 CT.  One contract, no stop, no target.
  * Exchange early closes the protocol cannot see (Good Friday 08:15 CT, holiday 10:30 / 12:15 CT closes): when the
    bar after bar i opens at or after the market's next reopen instant (17:00 CT same day Mon-Thu, Sunday 17:00 CT
    after a Friday) -- i.e. the whole 15:10-17:00 CT break or weekend had no quotes -- the position is closed at the
    open of bar i, the last quoted bar before the halt (early_close_exits).  Exits at the open of the first bar
    inside the break (15:11-15:14 CT when 15:08-15:10 had no quote change) are the protocol's own forced-flat
    semantics and are kept.  A post-check drops any trade whose exit is at/after the reopen instant following its
    entry (none occur in the final run); counts are reported per variant.
  * Costs: protocol.CONTRACT["ES"]: $50/pt, $16.28 per round turn (commission $3.78 + one tick $12.50).
  * Survivor bar: mean_net > 0, t >= 2.5, n >= 150, net P&L > 0 in >= 8 of the 13 calendar years 2005..2017.
  * Deflated Sharpe: protocol.deflated_sharpe(sharpe_per_trade, n, 22) (22 pre-registered ES variants).

Post-hoc diagnostics (<= 2, labelled, never nominated):
  D1 NAS100 twin: V1-V4 on the Nasdaq-100 CFD with the NQ contract spec (protocol.CONTRACT["NQ"]).
  D2 V2 with Sunday entries conditioned on Friday's cash session (the "previous cash session" reading).

Run: cd /home/user/j && python3 -m research.hyp.es_overnight_drift
"""
from __future__ import annotations

import json
import os
import re
import sys

import numpy as np
import pandas as pd

from research.data_index import load_bars_index
from research import protocol as P

ROOT = "/home/user/j/data_research/IS"
IS_START = pd.Timestamp("2005-01-01", tz="UTC")
IS_END = pd.Timestamp("2017-12-31 23:59:59", tz="UTC")
TZ = "America/Chicago"
FAMILY = "overnight_drift"
N_VARIANTS_DSR = 22
IS_YEARS = [str(y) for y in range(2005, 2018)]
TOL = pd.Timedelta(minutes=5)
OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "es_overnight_drift_results.json")

SUN, MON, TUE, WED, THU, FRI = 6, 0, 1, 2, 3, 4
EVENINGS = (SUN, MON, TUE, WED, THU)
WEEKDAYS = (MON, TUE, WED, THU, FRI)
DOW_NAME = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}

VARIANTS = ["V1_long_overnight_all", "V2_long_overnight_after_down_day", "V3_long_overnight_to_0900", "V4_short_intraday"]


# ----------------------------------------------------------------------------- schedule -> bar rows
def scheduled_bars(bars: pd.DataFrame, hh: int, mm: int, dows) -> pd.DataFrame:
    """For every CT calendar date in the span whose weekday is in `dows`: the row `j` of the first bar with
    open_time >= HH:MM CT on that date, its lag in minutes after the scheduled instant, and `ok` (lag < 5 min).
    `j == len(bars)` means no bar at or after the instant."""
    ct = bars["ct"]
    d0 = ct.iloc[0].tz_localize(None).normalize() - pd.Timedelta(days=1)
    d1 = ct.iloc[-1].tz_localize(None).normalize() + pd.Timedelta(days=1)
    dates = pd.date_range(d0, d1, freq="D")
    dates = dates[np.isin(dates.dayofweek, list(dows))]
    loc = (dates + pd.Timedelta(hours=hh, minutes=mm)).tz_localize(TZ, ambiguous="raise", nonexistent="raise")
    s_ns = loc.tz_convert("UTC").values.astype("datetime64[ns]").astype(np.int64)
    ot = bars["open_time"].values.astype("datetime64[ns]").astype(np.int64)
    n = len(ot)
    j = np.searchsorted(ot, s_ns, side="left")
    jj = np.minimum(j, n - 1)
    lag = (ot[jj] - s_ns) / 60e9
    ok = (j < n) & (j >= 1) & (lag < TOL.total_seconds() / 60.0)
    out = pd.DataFrame({"j": j, "lag_min": np.where(j < n, lag, np.nan), "ok": ok}, index=dates)
    out.index.name = "date"
    return out


def flag_entries(n: int, sched: pd.DataFrame, side_val: int, mask=None):
    entries = np.zeros(n, dtype=bool)
    side = np.zeros(n, dtype=int)
    use = sched["ok"].values if mask is None else (sched["ok"].values & np.asarray(mask, dtype=bool))
    rows = sched.loc[use, "j"].values.astype(int) - 1      # flag the bar BEFORE the fill bar
    entries[rows] = True
    side[rows] = side_val
    return entries, side


def flag_exits(n: int, sched: pd.DataFrame):
    exits = np.zeros(n, dtype=bool)
    use = (sched["j"].values < n) & (sched["j"].values >= 1)      # first bar at/after the instant, no tolerance
    rows = sched["j"].values[use].astype(int) - 1
    exits[rows] = True
    return exits


def forced_flat_and_reopen_ns(bars: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """For every bar: (a) the UTC instant (ns) of the next 15:10 CT forced-flat time strictly after the bar's open
    (15:10 CT of the bar's CT date if the bar opens before 15:10, else 15:10 CT of the next date) and (b) the
    instant the market is holdable again after it (17:00 CT the same date for Mon-Thu, Sunday 17:00 CT after a
    Friday / weekend)."""
    ct = bars["ct"]
    tod = ct.dt.hour * 60 + ct.dt.minute
    date = ct.dt.tz_localize(None).dt.normalize()
    date = pd.DatetimeIndex(date.where(tod < 15 * 60 + 10, date + pd.Timedelta(days=1)))
    ff = (date + pd.Timedelta(hours=15, minutes=10)).tz_localize(TZ, ambiguous="raise", nonexistent="raise")
    dow = date.dayofweek.values
    add = np.where(dow == 4, 2, np.where(dow == 5, 1, 0))              # Fri -> Sun 17:00, Sat -> Sun 17:00
    reopen = (date + pd.to_timedelta(add, unit="D") + pd.Timedelta(hours=17)).tz_localize(TZ, ambiguous="raise", nonexistent="raise")
    to_ns = lambda idx: idx.tz_convert("UTC").values.astype("datetime64[ns]").astype(np.int64)
    return to_ns(ff), to_ns(reopen)


def early_close_exits(bars: pd.DataFrame) -> np.ndarray:
    """Exit flags for session ends the protocol cannot see: when bar i is holdable and bar i+1 opens at or after the
    market's next reopen instant (i.e. the whole 15:10-17:00 CT break, or the weekend, had no quotes: exchange early
    close such as Good Friday 08:15 CT or Thanksgiving/Black Friday 12:15 CT), the position is closed at the open of
    bar i -- the last quoted bar before the halt -- by flagging exits[i-1].  A trader is flat before an early close
    by exchange calendar; this only supplies the last available price.  A bar i+1 that falls inside the break is
    left to the protocol's own forced flat (exit at that bar's open)."""
    ot = bars["open_time"].values.astype("datetime64[ns]").astype(np.int64)
    _, reopen = forced_flat_and_reopen_ns(bars)
    hold = P.tradable_mask(bars["open_time"])
    n = len(ot)
    gap = np.zeros(n, dtype=bool)
    gap[:-1] = hold[:-1] & (ot[1:] >= reopen[:-1])
    exits = np.zeros(n, dtype=bool)
    exits[:-1] = gap[1:]                      # exits[i-1] <- gap at bar i  => fill at open of bar i
    return exits


# ----------------------------------------------------------------------------- variants
def build_variant(bars: pd.DataFrame, key: str, sunday_uses_friday: bool = False):
    """key in {"V1","V2","V3","V4"} selects the pre-registered rule; labels are handled by the caller."""
    n = len(bars)
    if key == "V4":
        ent = scheduled_bars(bars, 9, 0, WEEKDAYS)
        entries, side = flag_entries(n, ent, -1)
        exits = flag_exits(n, scheduled_bars(bars, 15, 8, WEEKDAYS)) | early_close_exits(bars)
        return entries, exits, side, ent
    ent = scheduled_bars(bars, 17, 0, EVENINGS)
    if key == "V2":
        o = bars["open"].values
        c0830 = scheduled_bars(bars, 8, 30, WEEKDAYS)
        c1508 = scheduled_bars(bars, 15, 8, WEEKDAYS)
        ok = c0830["ok"].values & c1508["ok"].values
        r = np.full(len(c0830), np.nan)
        r[ok] = o[c1508["j"].values[ok]] / o[c0830["j"].values[ok]] - 1.0
        r_cash = pd.Series(r, index=c0830.index)
        kdate = ent.index.to_series().copy()
        if sunday_uses_friday:
            kdate = kdate.where(kdate.dt.dayofweek != SUN, kdate - pd.Timedelta(days=2))
        rc = r_cash.reindex(kdate.values).values
        mask = np.isfinite(rc) & (rc < 0)
        ent = ent.assign(r_cash=rc)
        entries, side = flag_entries(n, ent, +1, mask)
    else:
        entries, side = flag_entries(n, ent, +1)
    exit_hh, exit_mm = (9, 0) if key == "V3" else (8, 30)
    exits = flag_exits(n, scheduled_bars(bars, exit_hh, exit_mm, WEEKDAYS)) | early_close_exits(bars)
    return entries, exits, side, ent


def rule_text(key: str, sym_contract: str, sunday_uses_friday: bool = False) -> str:
    c = P.CONTRACT[sym_contract]
    common = (f"1 {sym_contract} contract (${c['mult']:.0f}/pt), no stop/target, ${c['cost_rt']:.2f} per round turn. "
              f"Oanda index CFD 1-minute bars as the price proxy; 'the HH:MM bar' = the first 1-minute bar with open "
              f"time >= HH:MM America/Chicago on that calendar date; an entry requires that bar to open within 5 minutes "
              f"of HH:MM (else no trade that day); an exit fills at the open of the first bar >= the scheduled instant; "
              f"protocol forced flat at 15:10 CT / before the weekend is the backstop. ")
    if key == "V1":
        return common + ("Enter long at the open of the 17:00 CT bar on Sun, Mon, Tue, Wed, Thu; exit at the open of the "
                         "08:30 CT bar of the next calendar day.")
    if key == "V2":
        sun = ("Sunday entries are conditioned on Friday's cash session (DIAGNOSTIC reading)." if sunday_uses_friday else
               "Sunday has no same-day cash session, so no Sunday entries (literal pre-registered reading).")
        return common + ("At 16:59 CT on date d compute r_cash = open(15:08 CT bar of d) / open(08:30 CT bar of d) - 1 "
                         "(both bars as defined above, both must exist within 5 minutes). If r_cash < 0: enter long at the "
                         "open of the 17:00 CT bar of d (Mon-Thu); exit at the open of the 08:30 CT bar of d+1. " + sun)
    if key == "V3":
        return common + ("Enter long at the open of the 17:00 CT bar on Sun, Mon, Tue, Wed, Thu; exit at the open of the "
                         "09:00 CT bar of the next calendar day.")
    return common + ("Enter short at the open of the 09:00 CT bar on Mon-Fri; exit at the open of the 15:08 CT bar the "
                     "same day (forced flat 15:10 CT backstop).")


def qualifies(st: dict) -> tuple[bool, dict]:
    by = st.get("by_year", {})
    pos_years = sum(1 for y in IS_YEARS if by.get(y, 0.0) > 0)
    checks = {"mean_net_pos": bool(st.get("mean_net", 0) > 0), "t_ge_2.5": bool(st.get("t_stat", 0) >= 2.5),
              "n_ge_150": bool(st.get("n", 0) >= 150), "pos_years_ge_8_of_13": bool(pos_years >= 8), "pos_years": int(pos_years)}
    return all(v for k, v in checks.items() if k != "pos_years"), checks


def run_one(bars: pd.DataFrame, name: str, sym_contract: str, sunday_uses_friday: bool = False) -> tuple[dict, pd.DataFrame]:
    key = name.split("_")[0] if name.startswith("V") else re.search(r"(V[1-4])_", name).group(1)
    entries, exits, side, ent = build_variant(bars, key, sunday_uses_friday)
    tr = P.backtest_signals(bars, entries, exits, side, sym=sym_contract)
    # validity post-check: a Topstep position can never survive to the market reopen that follows the forced flat
    # after its entry (exits at the open of the first bar inside the 15:10-17:00 CT break are the protocol's own
    # forced-flat semantics and are kept)
    ff, reopen = forced_flat_and_reopen_ns(bars)
    ot = bars["open_time"].values.astype("datetime64[ns]").astype(np.int64)
    e_rows = np.searchsorted(ot, tr["entry_time"].values.astype("datetime64[ns]").astype(np.int64))
    x_ns = tr["exit_time"].values.astype("datetime64[ns]").astype(np.int64)
    invalid = x_ns >= reopen[e_rows]
    n_invalid = int(invalid.sum())
    n_in_break = int(((x_ns >= ff[e_rows]) & ~invalid).sum())
    tr = tr.loc[~invalid].reset_index(drop=True)
    # early-close exits: exit bar is the last quoted bar before a quote-less break (see early_close_exits)
    ec = early_close_exits(bars)
    x_rows = np.searchsorted(ot, x_ns[~invalid])
    n_early_close = int(ec[np.maximum(x_rows - 1, 0)].sum())
    st = P.summarize(tr, bars)
    rec = {"name": name, "variant": key, "symbol": sym_contract, "data": "NAS100" if sym_contract == "NQ" else "SPX500",
           "rule": rule_text(key, sym_contract, sunday_uses_friday), "n": int(st.get("n", 0)),
           "n_scheduled_days": int(len(ent)), "n_entry_bar_ok": int(ent["ok"].sum()),
           "n_dropped_unpriceable": n_invalid, "n_early_close_exits": n_early_close, "n_exits_inside_break": n_in_break,
           "entry_lag_min_mean": float(ent.loc[ent["ok"], "lag_min"].mean()) if ent["ok"].any() else None}
    if "r_cash" in ent:
        rc = ent["r_cash"]
        rec["n_days_with_r_cash"] = int(np.isfinite(rc).sum())
        rec["n_down_days"] = int((rc < 0).sum())
    if rec["n"] > 0:
        rec.update({k: float(st[k]) for k in ("trades_per_day", "mean_net", "median_net", "std_net", "t_stat", "ci95_low",
                                              "ci95_high", "win_rate", "avg_win", "avg_loss", "sharpe_per_trade",
                                              "sharpe_annual", "total_net", "gross_mean", "max_drawdown")})
        rec["by_year"] = {k: round(v, 1) for k, v in st["by_year"].items()}
        rec["n_by_year"] = st["n_by_year"]
        rec["reasons"] = {k: int(v) for k, v in tr["reason"].value_counts().items()}
        ect = tr["entry_time"].dt.tz_convert(TZ)
        xct = tr["exit_time"].dt.tz_convert(TZ)
        rec["by_dow"] = {DOW_NAME[int(d)]: {"n": int(len(g)), "mean_net": round(float(g["net"].mean()), 2),
                                            "t_stat": round(tstat(g["net"].values), 2)}
                         for d, g in tr.groupby(ect.dt.dayofweek)}
        rec["entry_tod_ct"] = ect.dt.strftime("%H:%M").value_counts().head(5).to_dict()
        rec["exit_tod_ct"] = xct.dt.strftime("%H:%M").value_counts().head(5).to_dict()
        rec["hold_minutes_median"] = float(((tr["exit_time"] - tr["entry_time"]).dt.total_seconds() / 60).median())
        rec["dsr"] = float(P.deflated_sharpe(st["sharpe_per_trade"], st["n"], N_VARIANTS_DSR))
        rec["survivor"], rec["survivor_checks"] = qualifies(st)
    else:
        rec.update({"survivor": False, "survivor_checks": {}})
    return rec, tr


def tstat(x: np.ndarray) -> float:
    x = np.asarray(x, float)
    return float(x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))) if len(x) > 1 and x.std(ddof=1) > 0 else 0.0


def by_year_str(rec: dict) -> str:
    return " ".join(f"{y}:{rec.get('by_year', {}).get(y, 0.0):+.0f}" for y in IS_YEARS)


def fmt_row(r: dict) -> str:
    if r["n"] == 0:
        return f"{r['name']:<36} n=0"
    return (f"{r['name']:<36} n={r['n']:5d} tpd={r['trades_per_day']:.3f} mean=${r['mean_net']:8.2f} t={r['t_stat']:6.2f} "
            f"ci=[{r['ci95_low']:.1f},{r['ci95_high']:.1f}] wr={r['win_rate']:.3f} aw={r['avg_win']:.1f} al={r['avg_loss']:.1f} "
            f"spt={r['sharpe_per_trade']:.3f} dsr={r['dsr']:.3f} posyrs={r['survivor_checks']['pos_years']}/13 "
            f"surv={r['survivor']}\n{'':36} {by_year_str(r)}\n{'':36} reasons={r['reasons']} dow={ {k: v['mean_net'] for k, v in r['by_dow'].items()} }")


# ----------------------------------------------------------------------------- main
def main():
    bars = load_bars_index("SPX500", "1m", root=ROOT).sort_values("open_time").reset_index(drop=True)
    assert bars["open_time"].min() >= IS_START and bars["open_time"].max() <= IS_END, "in-sample data only"
    assert (bars[["open", "high", "low", "close"]] > 0).all().all()
    print(f"SPX500 1m bars={len(bars)} {bars['open_time'].iloc[0]} -> {bars['open_time'].iloc[-1]}")

    results, trades = [], {}
    for name in VARIANTS:
        rec, tr = run_one(bars, name, "ES")
        results.append(rec)
        trades[name] = tr
        print(fmt_row(rec))

    # ---- post-hoc diagnostics (never nominated)
    diagnostics = []
    nq = load_bars_index("NAS100", "1m", root=ROOT).sort_values("open_time").reset_index(drop=True)
    assert nq["open_time"].min() >= IS_START and nq["open_time"].max() <= IS_END
    print(f"\nDIAGNOSTIC D1: NAS100 twin (NQ contract spec, $20/pt, $8.78 rt) bars={len(nq)}")
    for name in VARIANTS:
        rec, _ = run_one(nq, "D1_NAS100_" + name, "NQ")
        rec["diagnostic"] = True
        rec["note"] = "post-hoc diagnostic: NAS100 CFD twin of the pre-registered variant with NQ contract spec; not nominable"
        diagnostics.append(rec)
        print(fmt_row(rec))
    print("\nDIAGNOSTIC D2: V2 with Sunday entries conditioned on Friday's cash session")
    rec, _ = run_one(bars, "D2_V2_sunday_uses_friday", "ES", sunday_uses_friday=True)
    rec["diagnostic"] = True
    rec["note"] = "post-hoc diagnostic: alternative reading of V2 (previous cash session = Friday for Sunday entries); not nominable"
    diagnostics.append(rec)
    print(fmt_row(rec))

    survivors = [r for r in results if r["survivor"]]
    out = {"family": FAMILY, "symbol": "ES", "data": "SPX500 Oanda CFD 1-minute bars, IS 2005-01..2017-12", "bar_size": "1min",
           "n_variants": len(VARIANTS), "dsr_N": N_VARIANTS_DSR, "variants": results, "diagnostics": diagnostics,
           "survivors": [r["name"] for r in survivors]}
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=1, default=str)
    print(f"\nsurvivors: {[r['name'] for r in survivors] or 'none'}; wrote {OUT_JSON}")
    return out


if __name__ == "__main__":
    main()
