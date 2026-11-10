"""Hypothesis family: calendar_flows  (ES round, pre-registered; in-sample only, ROOT = data_research/IS,
2005-01-01 .. 2017-12-31).

Calendar flow effects on the E-mini S&P 500 (ES, $50/pt, $16.28 per round turn = $3.78 commission + one
0.25 tick of slippage), proxied by Oanda SPX500 CFD minute bars (UTC timestamps -> America/Chicago).
Turn-of-month / month-end flows (Lakonishok & Smidt 1988; Ariel 1987; McConnell & Xu 2008; Etula et al. 2020
"Dash for cash") and option-expiration-day reversal (Stoll & Whaley 1987 and the "pinning" literature).

PRE-REGISTERED VARIANTS (all times America/Chicago; all three run and reported, none dropped, none added)
  "Trading day" = a weekday with cash-session bars.  Read as: a Mon-Fri CT calendar date that is NOT a US
  equity-market holiday (NYSE calendar: New Year's, MLK, Presidents', Good Friday, Memorial, Independence,
  Labor, Thanksgiving, Christmas, plus the 2007-01-02 and 2012-10-29/30 closures - all known ex ante) and that
  has at least one 1-minute bar with open time in [08:30, 15:10) CT.  The holiday exclusion is needed because
  the CFD quotes during the abbreviated Globex holiday sessions (bars until 10:30 / 12:00 CT on MLK, Presidents',
  Memorial, July 4, Labor Day, Thanksgiving): those are Globex bars, not cash-session bars.  In this data every
  non-holiday weekday 2005-01-03 .. 2017-12-29 has cash-session bars, so the two readings differ only on holidays.
  V1 turn_of_month_long     : for every month M, legs on the four trading days  L(M) = last trading day of M and
                              F1, F2, F3 = first three trading days of M+1.  Each leg: long at the 17:00 CT bar on
                              the calendar day BEFORE the leg day (Sunday 17:00 for a Monday leg), exit at the
                              15:08 CT bar of the leg day.  Each 17:00 -> 15:08 hold is one trade (4 per month).
  V2 month_end_last_hour_long: long at the 14:00 CT bar on L(M); exit at the 15:08 bar the same day.
  V3 opex_friday_fade       : on the calendar third Friday of each month, at the 14:00 CT bar enter
                              side = -sign(open(14:00) / open(08:30) - 1); exit at the 15:08 bar.

IMPLEMENTATION CONVENTIONS (fixed before any P&L was looked at)
  * Execution grid = 1-minute bars (load_bars_index(.., "1m")); the 15:08 exit does not exist on a 5-minute
    grid; the 17:00 / 14:00 / 08:30 opens are identical on both grids.  Oanda bars exist only when the quote
    changed, so "the HH:MM bar" = the first 1-minute bar with open time >= HH:MM CT on that CT calendar date.
    An ENTRY requires that bar to open within 5 minutes of HH:MM (else no trade for that leg/day: missing bar =
    no trade).  Protocol rule "signal from bar i acts at the open of bar i+1": entries/exits are flagged on the
    bar that immediately precedes the fill bar and protocol.backtest_signals fills at the next bar's open.
  * EXIT ("the 15:08 bar") on leg day D: the first bar on D with open time in [15:08, 15:15] CT (a fill at
    15:10-15:15 is the protocol's own forced-flat semantics).  If no such bar exists: (a) if the last bar on D
    before 15:08 opens before 15:00 CT the session halted early (CME early close at 12:15 CT: day after
    Thanksgiving, Christmas Eve, July 3, New Year's Eve 2012-2015) and the position is closed at the open of
    that last quoted bar before the halt ("early_close"; a trader is flat at the halt by exchange rule; the
    protocol's forced flat would otherwise fill at the 15:30 CT post-close bar, three hours after the halt);
    (b) otherwise the position is closed at the open of the first bar on D with open time in (15:15, 17:00) CT
    ("late_flat": the protocol's forced flat at the first bar inside the break; the quote did not change
    between the last pre-15:08 bar and that bar); (c) if neither exists, at the last bar before 15:08
    ("early_close").  Kinds and counts are reported per variant.
  * V1 entry on Sunday 17:00 CT for a Monday leg; the first leg of the sample (2005-01-03, entry 2005-01-02
    17:00 CT = the first bar of the data, no preceding bar to flag) cannot be traded; legs whose 17:00 bar
    is missing (no quote within 5 minutes) are no-trades.  L(2004-12) is before the data; F1-F3 of 2018-01
    are after it.
  * V3 signal price "open(14:00)": the close of the decision bar = the last 1-minute bar before the 14:00
    fill bar on the same date (the last traded price before 14:00:00 CT, exactly as in the intraday-momentum
    family of this round), so no fill-bar information enters the signal.  open(08:30) = open of the 08:30 bar
    (within 5 minutes).  side = -sign(ratio - 1); ratio == 1 exactly -> no trade.  The number of days on which
    the literal fill-bar open would give a different sign is reported (not a variant).
  * One contract, no stop, no target, one position at a time.  Costs: protocol.CONTRACT["ES"].
  * Validity post-checks: every trade's exit must be the intended exit bar of its leg day (same CT date,
    not after 17:00 CT); mismatches are dropped and counted (none expected).
  * Survivor bar: mean_net > 0, t_stat >= 2.5, n >= 150, net P&L > 0 in >= 8 of the 13 calendar years.
    Deflated Sharpe: protocol.deflated_sharpe(sharpe_per_trade, n, 22) (22 pre-registered ES variants).

POST-HOC DIAGNOSTICS (<= 2, clearly labelled, never nominated)
  D1 NAS100 twin: V1-V3 on the Nasdaq-100 CFD with the NQ contract spec (protocol.CONTRACT["NQ"]).
  D2 V1 decomposition: the same leg days traded as (a) overnight-only holds 17:00 -> 08:30 bar and
     (b) day-only holds 08:30 -> 15:08 bar (each its own round turn).

Run:  cd /home/user/j && python3 -m research.hyp.es_calendar_flows
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
IS_START = pd.Timestamp("2005-01-01", tz="UTC")
IS_END = pd.Timestamp("2017-12-31 23:59:59", tz="UTC")
TZ = "America/Chicago"
FAMILY = "calendar_flows"
N_VARIANTS_DSR = 22
IS_YEARS = [str(y) for y in range(2005, 2018)]
OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "es_calendar_flows_results.json")
SURVIVOR = dict(mean_net=0.0, t_stat=2.5, n=150, pos_years=8)

TOL_MIN = 5.0


def mm(h: int, m: int = 0) -> int:
    return h * 60 + m


CASH_OPEN_MN, CASH_END_MN = mm(8, 30), mm(15, 10)
EXIT_MN, EXIT_MAX_MN, EARLY_MN, REOPEN_MN = mm(15, 8), mm(15, 15), mm(15, 0), mm(17, 0)
DOW_NAME = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}
LEGS = ("T-1", "T+1", "T+2", "T+3")


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


def key_to_ts(keys) -> pd.DatetimeIndex:
    return pd.DatetimeIndex(pd.to_datetime(pd.Series(np.asarray(keys, dtype=np.int64)).astype(str), format="%Y%m%d"))


def ts_to_key(ts: pd.DatetimeIndex) -> np.ndarray:
    return (ts.year * 10000 + ts.month * 100 + ts.day).values.astype(np.int64)


def prev_calendar_key(keys) -> np.ndarray:
    return ts_to_key(key_to_ts(keys) - pd.Timedelta(days=1))


def instant_rows(bars: pd.DataFrame, keys, hh: int, mi: int) -> pd.DataFrame:
    """For each CT calendar date key: row j of the first bar with open_time >= HH:MM CT on that date, its lag in
    minutes after the instant, and ok (0 <= lag < 5 min and a preceding bar exists to carry the flag)."""
    keys = np.asarray(keys, dtype=np.int64)
    loc = (key_to_ts(keys) + pd.Timedelta(hours=hh, minutes=mi)).tz_localize(TZ, ambiguous="raise", nonexistent="raise")
    s_ns = loc.tz_convert("UTC").values.astype("datetime64[ns]").astype(np.int64)
    ot = bars["open_time"].values.astype("datetime64[ns]").astype(np.int64)
    n = len(ot)
    j = np.searchsorted(ot, s_ns, side="left")
    jj = np.minimum(j, n - 1)
    lag = (ot[jj] - s_ns) / 60e9
    ok = (j < n) & (j >= 1) & (lag >= 0) & (lag < TOL_MIN)
    return pd.DataFrame({"j": j, "lag_min": np.where(j < n, lag, np.nan), "ok": ok}, index=pd.Index(keys, name="key"))


def day_table(bars: pd.DataFrame, hol: set) -> pd.DataFrame:
    """One row per CT calendar date present in the data: weekday, cash-bar count, holiday flag, trading-day flag,
    and the intended exit row / kind for the 15:08 exit."""
    mn, key, dow = ct_fields(bars)
    df = pd.DataFrame({"key": key, "mn": mn, "row": np.arange(len(bars))})
    tab = pd.DataFrame(index=pd.Index(np.unique(key), name="key"))
    tab["dow"] = pd.Series(dow, index=key).groupby(level=0).first()
    cash = df[(df["mn"] >= CASH_OPEN_MN) & (df["mn"] < CASH_END_MN)]
    tab["n_cash"] = cash.groupby("key").size().reindex(tab.index).fillna(0).astype(int)
    tab["holiday"] = tab.index.isin(list(hol))
    tab["trading_day"] = (tab["dow"] < 5) & ~tab["holiday"] & (tab["n_cash"] > 0)
    reg = df[(df["mn"] >= EXIT_MN) & (df["mn"] <= EXIT_MAX_MN)].groupby("key")["row"].first()
    pre = df[df["mn"] < EXIT_MN].groupby("key")["row"].last()
    late = df[(df["mn"] > EXIT_MAX_MN) & (df["mn"] < REOPEN_MN)].groupby("key")["row"].first()
    tab["x_reg"] = reg.reindex(tab.index)
    tab["x_pre"] = pre.reindex(tab.index)
    tab["x_late"] = late.reindex(tab.index)
    tab["pre_mn"] = pd.Series(mn[tab["x_pre"].fillna(0).astype(int).values], index=tab.index).where(tab["x_pre"].notna())
    kind = np.where(tab["x_reg"].notna(), "regular",
                    np.where(tab["x_pre"].isna(), "none",
                             np.where(tab["pre_mn"] < EARLY_MN, "early_close",
                                      np.where(tab["x_late"].notna(), "late_flat", "early_close"))))
    tab["x_kind"] = kind
    xr = tab["x_reg"].copy()
    xr = xr.where(kind != "late_flat", tab["x_late"])
    xr = xr.where(kind != "early_close", tab["x_pre"])
    tab["x_row"] = xr
    return tab


def exit_flags(n: int, tab: pd.DataFrame) -> np.ndarray:
    exits = np.zeros(n, dtype=bool)
    rows = tab.loc[tab["trading_day"] & tab["x_row"].notna(), "x_row"].astype(int).values
    rows = rows[rows >= 1]
    exits[rows - 1] = True            # engine fills at the open of row x_row
    return exits


def flag_entries(n: int, rows_fill: np.ndarray, sides: np.ndarray):
    entries = np.zeros(n, dtype=bool)
    side = np.zeros(n, dtype=int)
    entries[rows_fill - 1] = True      # flag on the bar before the fill bar
    side[rows_fill - 1] = sides
    return entries, side


# ----------------------------------------------------------------------------- calendar schedules
def tom_legs(tab: pd.DataFrame) -> pd.DataFrame:
    """Leg days of the turn-of-month window: L(M) and F1..F3 of M+1 for every month M present in the data."""
    td = np.sort(tab.index[tab["trading_day"]].values)
    month = td // 100
    rows = []
    months = np.unique(month)
    for i, m in enumerate(months):
        days_m = td[month == m]
        turn = f"{m // 100:04d}-{m % 100:02d}->"
        rows.append(dict(key=int(days_m[-1]), leg="T-1", turn=turn))
        if i + 1 < len(months):
            m2 = months[i + 1]
            days_m2 = td[month == m2]
            for k, lab in enumerate(("T+1", "T+2", "T+3")):
                if k < len(days_m2):
                    rows.append(dict(key=int(days_m2[k]), leg=lab, turn=turn))
    legs = pd.DataFrame(rows).sort_values("key").reset_index(drop=True)
    assert legs["key"].is_unique, "overlapping legs"
    return legs


def month_end_days(tab: pd.DataFrame) -> np.ndarray:
    td = np.sort(tab.index[tab["trading_day"]].values)
    return np.array([int(td[td // 100 == m][-1]) for m in np.unique(td // 100)], dtype=np.int64)


def third_fridays(tab: pd.DataFrame) -> np.ndarray:
    ts = key_to_ts(tab.index.values)
    cal = pd.date_range(ts.min().normalize(), ts.max().normalize(), freq="D")
    sel = cal[(cal.dayofweek == 4) & (cal.day >= 15) & (cal.day <= 21)]
    return ts_to_key(sel)


# ----------------------------------------------------------------------------- variants
def build_v1(bars: pd.DataFrame, tab: pd.DataFrame, mode: str = "full"):
    """mode: 'full' = 17:00 (day before) -> 15:08; 'overnight' = 17:00 -> 08:30 bar; 'day' = 08:30 -> 15:08 (D2)."""
    n = len(bars)
    legs = tom_legs(tab)
    if mode == "day":
        ent = instant_rows(bars, legs["key"].values, 8, 30)
    else:
        legs["entry_key"] = prev_calendar_key(legs["key"].values)
        ent = instant_rows(bars, legs["entry_key"].values, 17, 0)
    legs["e_row"], legs["e_lag"], legs["e_ok"] = ent["j"].values, ent["lag_min"].values, ent["ok"].values
    if mode == "overnight":
        xo = instant_rows(bars, legs["key"].values, 8, 30)
        legs["x_row"] = np.where(xo["ok"].values, xo["j"].values, np.nan)
        legs["x_kind"] = np.where(xo["ok"].values, "regular", "none")
        exits = np.zeros(n, dtype=bool)
        xr = legs.loc[legs["x_row"].notna(), "x_row"].astype(int).values
        exits[xr[xr >= 1] - 1] = True
    else:
        legs["x_row"] = tab["x_row"].reindex(legs["key"].values).values
        legs["x_kind"] = tab["x_kind"].reindex(legs["key"].values).values
        exits = exit_flags(n, tab)
    legs["use"] = legs["e_ok"] & legs["x_row"].notna() & (legs["x_row"] > legs["e_row"])
    legs["side"] = 1
    rows_fill = legs.loc[legs["use"], "e_row"].astype(int).values
    entries, side = flag_entries(n, rows_fill, np.ones(len(rows_fill), dtype=int))
    return entries, exits, side, legs


def build_v2(bars: pd.DataFrame, tab: pd.DataFrame):
    n = len(bars)
    keys = month_end_days(tab)
    legs = pd.DataFrame({"key": keys, "leg": "T-1"})
    ent = instant_rows(bars, keys, 14, 0)
    legs["e_row"], legs["e_lag"], legs["e_ok"] = ent["j"].values, ent["lag_min"].values, ent["ok"].values
    legs["x_row"] = tab["x_row"].reindex(keys).values
    legs["x_kind"] = tab["x_kind"].reindex(keys).values
    legs["use"] = legs["e_ok"] & legs["x_row"].notna() & (legs["x_row"] > legs["e_row"])
    legs["side"] = 1
    rows_fill = legs.loc[legs["use"], "e_row"].astype(int).values
    entries, side = flag_entries(n, rows_fill, np.ones(len(rows_fill), dtype=int))
    return entries, exits_for(n, tab), side, legs


def exits_for(n: int, tab: pd.DataFrame) -> np.ndarray:
    return exit_flags(n, tab)


def build_v3(bars: pd.DataFrame, tab: pd.DataFrame):
    n = len(bars)
    mn, key, _ = ct_fields(bars)
    o, c = bars["open"].values, bars["close"].values
    keys = third_fridays(tab)
    legs = pd.DataFrame({"key": keys, "leg": "opex"})
    legs["in_data"] = np.isin(keys, tab.index.values)
    legs["trading_day"] = tab["trading_day"].reindex(keys).fillna(False).values.astype(bool)
    ent = instant_rows(bars, keys, 14, 0)
    op = instant_rows(bars, keys, 8, 30)
    legs["e_row"], legs["e_lag"], legs["e_ok"] = ent["j"].values, ent["lag_min"].values, ent["ok"].values
    legs["o0830_ok"] = op["ok"].values
    jj = np.minimum(ent["j"].values, n - 1)
    dec = np.maximum(jj - 1, 0)
    legs["dec_same_date"] = key[dec] == keys
    legs["dec_mn"] = mn[dec]
    o0830 = np.where(op["ok"].values, o[np.minimum(op["j"].values, n - 1)], np.nan)
    p_dec = c[dec].astype(float)
    legs["ratio"] = p_dec / o0830
    legs["ratio_literal"] = o[jj] / o0830
    legs["side"] = -np.sign(legs["ratio"] - 1.0)
    legs["side_literal"] = -np.sign(legs["ratio_literal"] - 1.0)
    legs["x_row"] = tab["x_row"].reindex(keys).values
    legs["x_kind"] = tab["x_kind"].reindex(keys).values
    legs["use"] = (legs["e_ok"] & legs["o0830_ok"] & legs["dec_same_date"] & legs["trading_day"]
                   & legs["x_row"].notna() & (legs["x_row"] > legs["e_row"]) & np.isfinite(legs["ratio"]) & (legs["side"] != 0))
    rows_fill = legs.loc[legs["use"], "e_row"].astype(int).values
    sides = legs.loc[legs["use"], "side"].astype(int).values
    entries, side = flag_entries(n, rows_fill, sides)
    return entries, exits_for(n, tab), side, legs


def rule_text(key: str, sym: str, mode: str = "full") -> str:
    c = P.CONTRACT[sym]
    common = (f"1 {sym} contract (${c['mult']:.0f}/pt), no stop/target, ${c['cost_rt']:.2f} per round turn, one position at a "
              f"time. Price proxy: Oanda index CFD 1-minute bars; 'the HH:MM bar' = the first 1-minute bar with open time >= "
              f"HH:MM America/Chicago on that CT calendar date; an entry requires that bar to open within 5 minutes of HH:MM "
              f"(else no trade). Exit = open of the first bar in [15:08, 15:15] CT of the day; if none, on an early-close day "
              f"(last pre-15:08 bar before 15:00 CT) the open of the last quoted bar before the halt, otherwise the open of "
              f"the first bar inside the 15:10-17:00 CT break. Flags are set on the bar before the fill bar "
              f"(protocol.backtest_signals fills at the next bar's open). Trading day = Mon-Fri CT date that is not a US "
              f"equity-market holiday (NYSE calendar incl. 2007-01-02, 2012-10-29/30) and has cash-session bars. ")
    if key == "V1":
        hold = {"full": "enter long at the open of the 17:00 CT bar on the calendar day before the leg day (Sunday 17:00 for a "
                        "Monday leg) and exit at the 15:08 bar of the leg day",
                "overnight": "DIAGNOSTIC D2a: enter long at the 17:00 CT bar on the calendar day before the leg day, exit at "
                             "the open of the 08:30 CT bar of the leg day (within 5 minutes, else the leg is skipped)",
                "day": "DIAGNOSTIC D2b: enter long at the 08:30 CT bar of the leg day (within 5 minutes), exit at the 15:08 bar"}[mode]
        return common + (f"For every month M: leg days = last trading day of M and the first three trading days of M+1. "
                         f"On each leg day {hold}; each hold is one trade (4 per month).")
    if key == "V2":
        return common + "On the last trading day of each month: enter long at the open of the 14:00 CT bar; exit at the 15:08 bar."
    return common + ("On the calendar third Friday of each month (15th-21st): at 14:00 CT compute ratio = (last traded price "
                     "before 14:00:00 CT, i.e. the close of the 1-minute bar preceding the 14:00 bar) / open(08:30 bar) and "
                     "enter side = -sign(ratio - 1) at the open of the 14:00 bar (ratio == 1 -> no trade); exit at the 15:08 bar.")


# ----------------------------------------------------------------------------- run / stats
def tstat(x) -> float:
    x = np.asarray(x, float)
    return float(x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))) if len(x) > 1 and x.std(ddof=1) > 0 else 0.0


def qualifies(st: dict) -> tuple[bool, dict]:
    by = st.get("by_year", {})
    pos_years = sum(1 for y in IS_YEARS if by.get(y, 0.0) > 0)
    checks = {"mean_net_pos": bool(st.get("mean_net", 0) > SURVIVOR["mean_net"]), "t_ge_2.5": bool(st.get("t_stat", 0) >= SURVIVOR["t_stat"]),
              "n_ge_150": bool(st.get("n", 0) >= SURVIVOR["n"]), "pos_years_ge_8_of_13": bool(pos_years >= SURVIVOR["pos_years"]),
              "pos_years": int(pos_years)}
    return all(v for k, v in checks.items() if k != "pos_years"), checks


def run_variant(bars: pd.DataFrame, tab: pd.DataFrame, key: str, sym: str, name: str, mode: str = "full") -> tuple[dict, pd.DataFrame]:
    t0 = time.time()
    if key == "V1":
        entries, exits, side, legs = build_v1(bars, tab, mode)
    elif key == "V2":
        entries, exits, side, legs = build_v2(bars, tab)
    else:
        entries, exits, side, legs = build_v3(bars, tab)
    tr = P.backtest_signals(bars, entries, exits, side, sym=sym)
    ot = bars["open_time"].values.astype("datetime64[ns]").astype(np.int64)
    used = legs[legs["use"]].set_index("e_row")
    rec = {"name": name, "variant": key, "symbol": sym, "data": "NAS100" if sym == "NQ" else "SPX500",
           "rule": rule_text(key, sym, mode), "n_scheduled": int(len(legs)), "n_entry_ok": int(legs["use"].sum()),
           "n_engine_trades": int(len(tr)), "n_dropped_exit_mismatch": 0}
    if key == "V3":
        rec["n_third_fridays_in_data"] = int(legs["in_data"].sum())
        rec["n_not_trading_day"] = int((legs["in_data"] & ~legs["trading_day"]).sum())
        rec["n_missing_1400_or_0830_bar"] = int((legs["trading_day"] & ~(legs["e_ok"] & legs["o0830_ok"])).sum())
        rec["n_zero_signal"] = int((legs["trading_day"] & legs["e_ok"] & legs["o0830_ok"] & (legs["side"] == 0)).sum())
        u = legs[legs["use"]]
        rec["n_sign_differs_from_literal_1400_open"] = int((u["side"] != u["side_literal"]).sum())
        rec["decision_bar_minute_ct"] = {f"{int(k) // 60:02d}:{int(k) % 60:02d}": int(v) for k, v in u["dec_mn"].value_counts().sort_index().items()}
    if len(tr):
        e_rows = np.searchsorted(ot, tr["entry_time"].values.astype("datetime64[ns]").astype(np.int64))
        x_rows = np.searchsorted(ot, tr["exit_time"].values.astype("datetime64[ns]").astype(np.int64))
        assert np.isin(e_rows, used.index.values).all(), "engine entered on an unscheduled bar"
        intended = used["x_row"].reindex(e_rows).values.astype(float)
        ok = x_rows == intended
        rec["n_dropped_exit_mismatch"] = int((~ok).sum())
        tr = tr.loc[ok].reset_index(drop=True)
        e_rows = e_rows[ok]
        tr["leg"] = used["leg"].reindex(e_rows).values
        tr["x_kind"] = used["x_kind"].reindex(e_rows).values
        tr["leg_key"] = used["key"].reindex(e_rows).values if "key" in used.columns else used.index.values
    st = P.summarize(tr, bars)
    rec["n"] = int(st.get("n", 0))
    if rec["n"] > 0:
        rec.update({k: float(st[k]) for k in ("trades_per_day", "mean_net", "median_net", "std_net", "t_stat", "ci95_low", "ci95_high",
                                              "win_rate", "avg_win", "avg_loss", "sharpe_per_trade", "sharpe_annual", "total_net",
                                              "gross_mean", "max_drawdown")})
        rec["by_year"] = {k: round(v, 1) for k, v in st["by_year"].items()}
        rec["n_by_year"] = st["n_by_year"]
        rec["reasons"] = {str(k): int(v) for k, v in tr["reason"].value_counts().items()}
        rec["exit_kinds"] = {str(k): int(v) for k, v in tr["x_kind"].value_counts().items()}
        ect = tr["entry_time"].dt.tz_convert(TZ)
        xct = tr["exit_time"].dt.tz_convert(TZ)
        rec["entry_tod_ct"] = ect.dt.strftime("%H:%M").value_counts().head(5).to_dict()
        rec["exit_tod_ct"] = xct.dt.strftime("%H:%M").value_counts().head(6).to_dict()
        rec["entry_lag_min_mean"] = float(legs.loc[legs["use"], "e_lag"].mean())
        rec["hold_minutes_median"] = float(((tr["exit_time"] - tr["entry_time"]).dt.total_seconds() / 60).median())
        rec["n_long"], rec["n_short"] = int((tr["side"] == 1).sum()), int((tr["side"] == -1).sum())
        rec["by_leg"] = {str(l): {"n": int(len(g)), "mean_net": round(float(g["net"].mean()), 2), "t_stat": round(tstat(g["net"].values), 2),
                                  "win_rate": round(float((g["net"] > 0).mean()), 3)} for l, g in tr.groupby("leg")}
        rec["by_dow"] = {DOW_NAME[int(d)]: {"n": int(len(g)), "mean_net": round(float(g["net"].mean()), 2), "t_stat": round(tstat(g["net"].values), 2)}
                         for d, g in tr.groupby(xct.dt.dayofweek)}
        if key == "V3":
            rec["by_side"] = {("long" if s == 1 else "short"): {"n": int(len(g)), "mean_net": round(float(g["net"].mean()), 2),
                                                                  "t_stat": round(tstat(g["net"].values), 2)} for s, g in tr.groupby("side")}
        rec["dsr"] = float(P.deflated_sharpe(st["sharpe_per_trade"], st["n"], N_VARIANTS_DSR))
        rec["survivor"], rec["survivor_checks"] = qualifies(st)
    else:
        rec.update({"survivor": False, "survivor_checks": {}, "dsr": 0.0})
    rec["seconds"] = round(time.time() - t0, 1)
    return rec, tr


def by_year_str(rec: dict) -> str:
    return " ".join(f"{y}:{rec.get('by_year', {}).get(y, 0.0):+.0f}" for y in IS_YEARS)


def fmt_row(r: dict) -> str:
    if r["n"] == 0:
        return f"{r['name']:<34} n=0 (scheduled={r['n_scheduled']}, entry_ok={r['n_entry_ok']})"
    return (f"{r['name']:<34} n={r['n']:4d} tpd={r['trades_per_day']:.3f} mean=${r['mean_net']:8.2f} t={r['t_stat']:6.2f} "
            f"ci=[{r['ci95_low']:.1f},{r['ci95_high']:.1f}] wr={r['win_rate']:.3f} aw={r['avg_win']:.1f} al={r['avg_loss']:.1f} "
            f"spt={r['sharpe_per_trade']:.3f} dsr={r['dsr']:.3f} posyrs={r['survivor_checks']['pos_years']}/13 surv={r['survivor']}\n"
            f"{'':34} {by_year_str(r)}\n"
            f"{'':34} sched={r['n_scheduled']} ok={r['n_entry_ok']} dropped={r['n_dropped_exit_mismatch']} reasons={r['reasons']} "
            f"exit_kinds={r['exit_kinds']} legs={ {k: (v['n'], v['mean_net'], v['t_stat']) for k, v in r['by_leg'].items()} }")


# ----------------------------------------------------------------------------- main
def load(sym: str) -> pd.DataFrame:
    b = load_bars_index(sym, "1m", root=ROOT).sort_values("open_time").reset_index(drop=True)
    assert b["open_time"].min() >= IS_START and b["open_time"].max() <= IS_END, "in-sample data only"
    assert (b[["open", "high", "low", "close"]] > 0).all().all()
    assert b["open_time"].is_unique
    return b


VARIANTS = [("V1", "V1_turn_of_month_long"), ("V2", "V2_month_end_last_hour_long"), ("V3", "V3_opex_friday_fade")]


def main():
    hol = holiday_keys()
    bars = load("SPX500")
    tab = day_table(bars, hol)
    print(f"SPX500 1m bars={len(bars)} {bars['open_time'].iloc[0]} -> {bars['open_time'].iloc[-1]}")
    wk = tab[tab["dow"] < 5]
    print(f"CT dates={len(tab)} weekdays={len(wk)} holidays-with-bars={int(wk['holiday'].sum())} trading_days={int(tab['trading_day'].sum())} "
          f"non-holiday weekdays without cash bars={int(((~wk['holiday']) & (wk['n_cash'] == 0)).sum())}")
    print("exit kinds on trading days:", tab.loc[tab["trading_day"], "x_kind"].value_counts().to_dict())
    ec = tab[tab["trading_day"] & (tab["x_kind"] != "regular")]
    print("non-regular exit days:", {int(k): (v, f"{int(m) // 60:02d}:{int(m) % 60:02d}") for k, v, m in zip(ec.index, ec["x_kind"], ec["pre_mn"].fillna(0))})
    for k in sorted(SPECIAL_CLOSURES):
        kk = int(k.strftime("%Y%m%d"))
        print(f"special closure {k}: in data={kk in tab.index}, n_cash={int(tab['n_cash'].get(kk, 0))}")
    legs = tom_legs(tab)
    print("turn-of-month legs:", len(legs), legs["leg"].value_counts().to_dict(), "first", legs['key'].iloc[0], "last", legs['key'].iloc[-1])

    results, trades = [], {}
    for key, name in VARIANTS:
        rec, tr = run_variant(bars, tab, key, "ES", name)
        results.append(rec)
        trades[name] = tr
        print(fmt_row(rec))

    diagnostics = []
    nq = load("NAS100")
    tab_nq = day_table(nq, hol)
    print(f"\nDIAGNOSTIC D1: NAS100 twin (NQ spec, $20/pt, $8.78 rt) bars={len(nq)} trading_days={int(tab_nq['trading_day'].sum())}")
    for key, name in VARIANTS:
        rec, _ = run_variant(nq, tab_nq, key, "NQ", "D1_NAS100_" + name)
        rec["diagnostic"] = True
        rec["note"] = "post-hoc diagnostic: NAS100 CFD twin of the pre-registered variant with NQ contract spec; not nominable"
        diagnostics.append(rec)
        print(fmt_row(rec))
    print("\nDIAGNOSTIC D2: V1 leg decomposition (overnight-only 17:00->08:30 / day-only 08:30->15:08), ES")
    for mode, name in (("overnight", "D2a_V1_overnight_only"), ("day", "D2b_V1_day_only")):
        rec, _ = run_variant(bars, tab, "V1", "ES", name, mode=mode)
        rec["diagnostic"] = True
        rec["note"] = "post-hoc diagnostic: decomposition of V1's holds into overnight / day legs (each its own round turn); not nominable"
        diagnostics.append(rec)
        print(fmt_row(rec))

    survivors = [r for r in results if r["survivor"]]
    out = {"family": FAMILY, "symbol": "ES", "data": "SPX500 Oanda CFD 1-minute bars, IS 2005-01..2017-12", "bar_size": "1min",
           "n_variants": len(VARIANTS), "dsr_N": N_VARIANTS_DSR, "survivor_bar": SURVIVOR, "variants": results,
           "diagnostics": diagnostics, "survivors": [r["name"] for r in survivors]}
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=1, default=str)
    print(f"\nsurvivors: {[r['name'] for r in survivors] or 'none'}; wrote {OUT_JSON}")
    return out


if __name__ == "__main__":
    main()
