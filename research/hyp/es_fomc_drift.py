"""Hypothesis family: fomc_drift (ES round, pre-registered).

Question: does the pre-FOMC announcement drift (Lucca & Moench 2015: the S&P 500 earns most of its excess
return in the 24 hours before scheduled FOMC statements) -- and a post-statement continuation -- survive
Topstep execution on the E-mini S&P 500 (ES, $50/pt, $16.28 per round turn) when proxied by Oanda SPX500 CFD
minute bars?  In-sample only: 2005-01-01 .. 2017-12-31 (ROOT = data_research/IS).

ANNOUNCEMENT DATES: parsed from the saved Federal Reserve pages data_research/fomc/fomchistorical<year>.htm
(2005-2019).  A meeting is SCHEDULED when its panel heading reads "<dates> Meeting - <year>"; headings that read
"Conference Call" or "(unscheduled)" are excluded.  The statement is released on the LAST day of the meeting, which
is the last day in the heading ("January 29-30" -> Jan 30, "July 31-August 1" -> Aug 1, "April/May 30-1" -> May 1,
"Jan/Feb 31-1" -> Feb 1).  Cross-check: the date embedded in the panel's "Statement" link.  The saved
fomccalendars.htm (fetched 2026) carries only 2021-2027, so 2020 could not be parsed from it; 2020 is outside the
in-sample window and is irrelevant to this run (a clearly labelled fallback list is kept for completeness).

PRE-REGISTERED VARIANTS (all run, all reported, none added, none dropped; times are America/Chicago):
  V1 pre_fomc_long_1d        : enter long at the 17:00 bar on the calendar day before the announcement day;
                               exit at the 12:55 bar on the announcement day.
  V2 pre_fomc_long_2d        : enter long at the 17:00 bar two trading days (weekdays) before the announcement day;
                               hold through, re-entering at the 17:00 bar after each forced flat (daily break and
                               weekend), until the 12:55 bar on the announcement day.  Every leg is a separate
                               round turn (that is what a Topstep trader pays); per-event sums are also reported.
  V3 post_fomc_continuation  : at the 13:35 bar on the announcement day, side = sign(open(13:35) / open(12:55) - 1);
                               exit at the 15:08 bar.

Implementation conventions (fixed before any P&L was looked at):
  * Execution grid = 1-minute bars (load_bars_index(.., "1m")): the pre-registered 15:08 CT exit does not exist on a
    5-minute grid; 17:00 / 12:55 / 13:35 opens are identical on both grids.
  * Oanda bars exist only when the quote changed.  "The HH:MM bar" = the first 1-minute bar whose open time is
    >= HH:MM CT on that calendar date.  For an ENTRY (and for the two V3 signal bars) that bar must open within
    5 minutes of the scheduled instant, otherwise no trade for that leg.  For an EXIT the position is closed at the
    open of the first bar >= the scheduled instant whenever it comes; the protocol forced flat at 15:10 CT / before
    the weekend remains active as a backstop.  No price is ever invented.
  * Protocol rule "a signal computed from bar i is acted on at the open of bar i+1":
      - time-scheduled entries (V1, V2) and all exits are flagged on the bar immediately preceding the fill bar, so
        the fill is at the open of the HH:MM bar itself (the signal is the calendar, known in advance);
      - V3's signal needs open(13:35), i.e. the price prevailing at the start of the 13:35 bar: the signal is
        attached to the 13:35 bar (bar i) and the fill is at the open of the NEXT quoted bar (bar i+1, normally the
        13:36 bar).  This is the strict no-look-ahead reading; it costs one minute of delay.
  * V2 "two trading days before" = two weekdays before (holidays are not special-cased: a missing 17:00 bar simply
    means no leg).  For a Tuesday announcement the two weekdays before are Friday and Monday; the Friday 17:00 bar
    is inside the weekend close, so the first leg opens at the Sunday 17:00 re-open and the second at Monday 17:00.
    Entry instants are therefore every 17:00 CT (Sun-Thu) from the second weekday before the announcement through
    the day before it.
  * Exchange early closes the protocol cannot see: as in es_overnight_drift (early_close_exits) -- a backstop only;
    no FOMC day is an early-close day.  Post-check: any trade whose exit is at/after the market re-open following
    its entry is dropped as unpriceable (count reported).
  * Costs: protocol.CONTRACT["ES"]: $50/pt, $16.28 per round turn (commission $3.78 + one tick $12.50).
  * Survivor bar: mean_net > 0, t >= 2.5, n >= 150, net P&L > 0 in >= 8 of the 13 calendar years 2005..2017.
    NOTE: 2005-2017 has 104 scheduled statements, so V1 and V3 (one trade per statement) cannot reach n >= 150
    in-sample whatever their edge; only V2 (two legs per statement) can.
  * Deflated Sharpe: protocol.deflated_sharpe(sharpe_per_trade, n, 22) (22 pre-registered ES variants).

Statement release times (the task text says 13:15 CT before 2011, 13:00 CT from 2011, 13:30 CT for some 2011-2012
press-conference meetings).  DATA CHECK printed with the date list: the minute of the largest 1-minute range in
10:30-14:30 CT on each announcement day.  It shows 13:15 CT (2:15 pm ET) through January 2013, 13:00 CT (2:00 pm
ET) from March 2013, and 11:30 CT (12:30 pm ET) for the eight 2011-2012 press-conference meetings (Apr/Jun/Nov 2011,
Jan/Apr/Jun/Sep/Dec 2012).  So the pre-registered 12:55 CT exit is pre-announcement on 96 of 104 days and 85
minutes POST-announcement on those eight.  The pre-registered rules are implemented exactly as written; the
timing-corrected version is diagnostic D2.

Post-hoc diagnostics (<= 2, labelled, never nominated):
  D1 NAS100 twin: V1-V3 on the Nasdaq-100 CFD with the NQ contract spec (protocol.CONTRACT["NQ"]).
  D2 release-time corrected: for the eight 2011-2012 press-conference meetings only, all instants move 90 minutes
     earlier (pre-announcement exit 11:25, V3 signal 12:05 vs 11:25); every other day unchanged.

Run: cd /home/user/j && python3 -m research.hyp.es_fomc_drift
"""
from __future__ import annotations

import calendar
import json
import os
import re

import numpy as np
import pandas as pd

from research.data_index import load_bars_index
from research import protocol as P

ROOT = "/home/user/j/data_research/IS"
FOMC_DIR = "/home/user/j/data_research/fomc"
IS_START = pd.Timestamp("2005-01-01", tz="UTC")
IS_END = pd.Timestamp("2017-12-31 23:59:59", tz="UTC")
TZ = "America/Chicago"
FAMILY = "fomc_drift"
N_VARIANTS_DSR = 22
IS_YEARS = [str(y) for y in range(2005, 2018)]
TOL_MIN = 5.0
OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "es_fomc_drift_results.json")

SUN, MON, TUE, WED, THU, FRI, SAT = 6, 0, 1, 2, 3, 4, 5
EVENINGS = (SUN, MON, TUE, WED, THU)
DOW_NAME = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}
VARIANTS = ["V1_pre_fomc_long_1d", "V2_pre_fomc_long_2d", "V3_post_fomc_continuation"]

MONTHS = {m: i for i, m in enumerate(calendar.month_name) if m}
MONTHS.update({m: i for i, m in enumerate(calendar.month_abbr) if m})
MONTHS.update({"Sept": 9})

# 2020 fallback (NOT parsed: the saved fomccalendars.htm holds 2021-2027 only).  Scheduled-meeting last days from
# the FOMC calendar; the March 17-18 2020 meeting was pre-empted by the unscheduled March 15 action (excluded, as
# is the unscheduled March 3 cut).  Outside the in-sample window; listed for completeness only.
FALLBACK_2020 = ["2020-01-29", "2020-04-29", "2020-06-10", "2020-07-29", "2020-09-16", "2020-11-05", "2020-12-16"]


# ----------------------------------------------------------------------------- FOMC dates
def _clean(h: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", h)).strip()


def _last_day(title: str, year: int):
    """'January 29-30 Meeting - 2008' -> Timestamp(2008-01-30); None when not a scheduled meeting."""
    t = title.replace(f" - {year}", "").strip()
    if "Meeting" not in t or "unscheduled" in t.lower() or "Conference Call" in t:
        return None
    t = t.replace("Meeting", "").strip()
    m = re.match(r"^([A-Za-z]+)(?:/([A-Za-z]+))?\s+(\d+)(?:-(?:([A-Za-z]+)\s+)?(\d+))?$", t)
    if not m:
        raise ValueError(f"cannot parse FOMC heading {title!r}")
    m1, m2, d1, m3, d2 = m.groups()
    if d2 is None:
        return pd.Timestamp(year, MONTHS[m1], int(d1))
    mon = MONTHS[m2] if m2 else (MONTHS[m3] if m3 else MONTHS[m1])
    return pd.Timestamp(year, mon, int(d2))


def parse_historical(year: int) -> list[dict]:
    path = os.path.join(FOMC_DIR, f"fomchistorical{year}.htm")
    with open(path, encoding="utf-8", errors="replace") as f:
        s = f.read()
    out = []
    for panel in re.split(r'<div class="panel panel-default', s)[1:]:
        h = re.search(r"<h5[^>]*>(.*?)</h5>", panel, flags=re.S)
        if not h:
            continue
        title = _clean(h.group(1))
        d = _last_day(title, year)
        link = re.search(r'href="[^"]*?(?:/monetary/?(\d{8})[a-z]?\.htm|/monetary/\d{4}/(\d{8})/(?:default\.htm)?)"[^>]*>\s*Statement\s*<',
                         panel)
        link_date = next((g for g in link.groups() if g), None) if link else None
        out.append({"date": d, "title": title, "year": year, "scheduled": d is not None,
                    "press_conf": bool(re.search(r"Press Conference", panel)),
                    "statement_link_date": link_date, "source": os.path.basename(path)})
    return out


def parse_calendars(path: str) -> dict[int, list[dict]]:
    """Year panels of the current-format calendar page -> {year: [rows]}; rows carry the statement-link date."""
    with open(path, encoding="utf-8", errors="replace") as f:
        s = f.read()
    out: dict[int, list[dict]] = {}
    for panel in re.split(r'<div class="panel panel-default">', s)[1:]:
        hy = re.search(r"<h4[^>]*>(.*?)</h4>", panel, flags=re.S)
        if not hy:
            continue
        ym = re.search(r"(\d{4}) FOMC Meetings", _clean(hy.group(1)))
        if not ym:
            continue
        year = int(ym.group(1))
        rows = []
        for r in re.split(r'<div class="(?:fomc-meeting--shaded )?row fomc-meeting"', panel)[1:]:
            mo = re.search(r"fomc-meeting__month[^>]*>(.*?)</div>", r, flags=re.S)
            da = re.search(r"fomc-meeting__date[^>]*>(.*?)</div>", r, flags=re.S)
            st = re.findall(r"pressreleases/monetary(\d{8})a\.htm", r)
            mo_t, da_t = (_clean(mo.group(1)) if mo else ""), (_clean(da.group(1)) if da else "")
            unsched = "unscheduled" in (mo_t + da_t).lower() or "notation vote" in r.lower() or "cancel" in (mo_t + da_t).lower()
            d = pd.Timestamp(sorted(set(st))[0]) if st else None
            rows.append({"date": d if not unsched else None, "title": f"{mo_t} {da_t} - {year}", "year": year,
                         "scheduled": (d is not None) and not unsched, "press_conf": "Press Conference" in r,
                         "statement_link_date": sorted(set(st))[0] if st else None, "source": os.path.basename(path)})
        out[year] = rows
    return out


def fomc_dates() -> pd.DataFrame:
    rows = []
    for y in range(2005, 2020):
        rows += parse_historical(y)
    cal = parse_calendars(os.path.join(FOMC_DIR, "fomccalendars.htm"))
    if 2020 in cal:
        rows += cal[2020]
        note_2020 = "2020 parsed from fomccalendars.htm"
    else:
        rows += [{"date": pd.Timestamp(d), "title": f"FALLBACK (not parsed) - 2020", "year": 2020, "scheduled": True,
                  "press_conf": True, "statement_link_date": None, "source": "FALLBACK_2020 (fomccalendars.htm holds "
                  + ",".join(str(k) for k in sorted(cal)) + " only)"} for d in FALLBACK_2020]
        note_2020 = f"fomccalendars.htm holds years {sorted(cal)} only; 2020 from the labelled fallback list (unused in-sample)"
    df = pd.DataFrame(rows)
    df["link_mismatch"] = [bool(pd.notna(d) and isinstance(l, str) and pd.Timestamp(d).strftime("%Y%m%d") != l)
                           for d, l in zip(df["date"], df["statement_link_date"])]
    df.attrs["note_2020"] = note_2020
    return df


# ----------------------------------------------------------------------------- bar lookups
def ct_instants_ns(dates: pd.DatetimeIndex, hh: int, mm: int) -> np.ndarray:
    loc = (pd.DatetimeIndex(dates) + pd.Timedelta(hours=hh, minutes=mm)).tz_localize(TZ, ambiguous="raise", nonexistent="raise")
    return loc.tz_convert("UTC").values.astype("datetime64[ns]").astype(np.int64)


def bar_at(ot: np.ndarray, inst: np.ndarray, tol_min: float | None = TOL_MIN):
    """Row of the first bar with open_time >= instant, its lag in minutes, and ok (row valid and lag < tol)."""
    n = len(ot)
    j = np.searchsorted(ot, inst, side="left")
    jj = np.minimum(j, n - 1)
    lag = (ot[jj] - inst) / 60e9
    ok = (j < n) & (j >= 1)
    if tol_min is not None:
        ok &= lag < tol_min
    return j, np.where(j < n, lag, np.nan), ok


def forced_flat_and_reopen_ns(bars: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Per bar: UTC ns of the next 15:10 CT forced flat strictly after the bar's open and of the re-open after it."""
    ct = bars["ct"]
    tod = ct.dt.hour * 60 + ct.dt.minute
    date = ct.dt.tz_localize(None).dt.normalize()
    date = pd.DatetimeIndex(date.where(tod < 15 * 60 + 10, date + pd.Timedelta(days=1)))
    ff = (date + pd.Timedelta(hours=15, minutes=10)).tz_localize(TZ, ambiguous="raise", nonexistent="raise")
    dow = date.dayofweek.values
    add = np.where(dow == 4, 2, np.where(dow == 5, 1, 0))
    reopen = (date + pd.to_timedelta(add, unit="D") + pd.Timedelta(hours=17)).tz_localize(TZ, ambiguous="raise", nonexistent="raise")
    to_ns = lambda idx: idx.tz_convert("UTC").values.astype("datetime64[ns]").astype(np.int64)
    return to_ns(ff), to_ns(reopen)


def early_close_exits(bars: pd.DataFrame) -> np.ndarray:
    """Backstop for quote-less breaks (exchange early close): when holdable bar i is followed by a bar opening at/after
    the next re-open instant, close at the open of bar i (flag exits[i-1])."""
    ot = bars["open_time"].values.astype("datetime64[ns]").astype(np.int64)
    _, reopen = forced_flat_and_reopen_ns(bars)
    hold = P.tradable_mask(bars["open_time"])
    n = len(ot)
    gap = np.zeros(n, dtype=bool)
    gap[:-1] = hold[:-1] & (ot[1:] >= reopen[:-1])
    exits = np.zeros(n, dtype=bool)
    exits[:-1] = gap[1:]
    return exits


# ----------------------------------------------------------------------------- events
def build_events(dates: pd.DataFrame, bars: pd.DataFrame) -> pd.DataFrame:
    """Scheduled announcement days inside the data span, with the release-time class and the data-detected minute."""
    ct = bars["ct"]
    d0 = ct.iloc[0].tz_localize(None).normalize()
    d1 = ct.iloc[-1].tz_localize(None).normalize()
    ev = dates[dates["scheduled"] & (dates["date"] >= d0) & (dates["date"] <= d1)].copy()
    ev = ev.sort_values("date").reset_index(drop=True)
    ev["pc_2011_2012"] = ev["press_conf"] & ev["year"].isin([2011, 2012])
    # data check: minute of the largest 1-minute range in 10:30-14:30 CT
    bd = ct.dt.tz_localize(None).dt.normalize()
    tod = ct.dt.hour * 60 + ct.dt.minute
    rng = (bars["high"] - bars["low"]).values
    det = []
    for d in ev["date"]:
        m = (bd.values == np.datetime64(d)) & (tod.values >= 10 * 60 + 30) & (tod.values <= 14 * 60 + 30)
        if not m.any():
            det.append(None)
            continue
        k = np.flatnonzero(m)[np.argmax(rng[m])]
        det.append(ct.iloc[k].strftime("%H:%M"))
    ev["detected_max_range_minute_ct"] = det
    ev["release_ct_assumed"] = np.where(ev["pc_2011_2012"], "11:30", np.where(ev["date"] < pd.Timestamp("2013-03-01"), "13:15", "13:00"))
    return ev


def entry_dates_v2(D: pd.Timestamp) -> list[pd.Timestamp]:
    d2 = D - 2 * pd.offsets.BDay()
    return [c for c in pd.date_range(d2, D - pd.Timedelta(days=1), freq="D") if c.dayofweek in EVENINGS]


def build_variant(bars: pd.DataFrame, ev: pd.DataFrame, key: str, corrected: bool = False):
    """Returns entries, exits, side arrays plus a legs table (event_date, entry instant, fill row, ok)."""
    n = len(bars)
    ot = bars["open_time"].values.astype("datetime64[ns]").astype(np.int64)
    o = bars["open"].values
    entries = np.zeros(n, dtype=bool)
    exits = np.zeros(n, dtype=bool)
    side = np.zeros(n, dtype=int)
    shift = np.where(corrected & ev["pc_2011_2012"].values, 90, 0)          # minutes earlier on the 8 corrected days
    D = pd.DatetimeIndex(ev["date"])
    exit_inst = ct_instants_ns(D, 12, 55) - shift * 60_000_000_000
    if key in ("V1", "V2"):
        legs = []
        for k, d in enumerate(D):
            cdates = [d - pd.Timedelta(days=1)] if key == "V1" else entry_dates_v2(d)
            for c in cdates:
                legs.append({"event_date": d, "entry_date": c, "inst": ct_instants_ns(pd.DatetimeIndex([c]), 17, 0)[0]})
        legs = pd.DataFrame(legs)
        j, lag, ok = bar_at(ot, legs["inst"].values, TOL_MIN)
        legs["j"], legs["lag_min"], legs["ok"] = j, lag, ok
        rows = j[ok] - 1
        entries[rows] = True
        side[rows] = +1
        jx, _, okx = bar_at(ot, exit_inst, None)
        exits[jx[okx] - 1] = True
    else:
        ref_inst = exit_inst                                                  # 12:55 (11:25 corrected)
        sig_inst = ct_instants_ns(D, 13, 35) - shift * 60_000_000_000        # 13:35 (12:05 corrected)
        jr, lr, okr = bar_at(ot, ref_inst, TOL_MIN)
        js, ls, oks = bar_at(ot, sig_inst, TOL_MIN)
        ok = okr & oks & (js < n - 1) & (js > jr)
        s = np.zeros(len(D), dtype=int)
        s[ok] = np.sign(o[js[ok]] / o[jr[ok]] - 1.0).astype(int)
        use = ok & (s != 0)
        entries[js[use]] = True                                               # signal on the 13:35 bar, fill next bar
        side[js[use]] = s[use]
        legs = pd.DataFrame({"event_date": D, "entry_date": D, "inst": sig_inst, "j": js + 1, "lag_min": ls, "ok": use,
                             "ref_ok": okr, "sig_ok": oks, "signal": s})
        jx, _, okx = bar_at(ot, ct_instants_ns(D, 15, 8), None)
        exits[jx[okx] - 1] = True
    exits |= early_close_exits(bars)
    return entries, exits, side, legs


# ----------------------------------------------------------------------------- stats / records
def tstat(x) -> float:
    x = np.asarray(x, float)
    return float(x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))) if len(x) > 1 and x.std(ddof=1) > 0 else 0.0


def qualifies(st: dict) -> tuple[bool, dict]:
    by = st.get("by_year", {})
    pos_years = sum(1 for y in IS_YEARS if by.get(y, 0.0) > 0)
    checks = {"mean_net_pos": bool(st.get("mean_net", 0) > 0), "t_ge_2.5": bool(st.get("t_stat", 0) >= 2.5),
              "n_ge_150": bool(st.get("n", 0) >= 150), "pos_years_ge_8_of_13": bool(pos_years >= 8), "pos_years": int(pos_years)}
    return all(v for k, v in checks.items() if k != "pos_years"), checks


def rule_text(key: str, sym_contract: str, corrected: bool = False) -> str:
    c = P.CONTRACT[sym_contract]
    common = (f"1 {sym_contract} contract (${c['mult']:.0f}/pt), no stop/target, ${c['cost_rt']:.2f} per round turn. "
              f"Oanda index CFD 1-minute bars as the price proxy; 'the HH:MM bar' = the first 1-minute bar with open time "
              f">= HH:MM America/Chicago on that calendar date; an entry (and each V3 signal bar) requires that bar to open "
              f"within 5 minutes of HH:MM, else no trade; an exit fills at the open of the first bar >= the scheduled "
              f"instant; protocol forced flat at 15:10 CT / before the weekend is the backstop. Announcement days = last "
              f"day of each scheduled FOMC meeting ('... Meeting - <year>' headings of federalreserve.gov/monetarypolicy/"
              f"fomchistorical<year>.htm; 'Conference Call' and '(unscheduled)' entries excluded), 104 days in 2005-2017. ")
    corr = (" DIAGNOSTIC D2: on the eight 2011-2012 press-conference days (statement 12:30 pm ET = 11:30 CT) every "
            "instant is 90 minutes earlier (exit 11:25; V3 signal 12:05 vs 11:25)." if corrected else "")
    if key == "V1":
        return common + ("Enter long at the open of the 17:00 CT bar on the calendar day before the announcement day; exit "
                         "at the open of the 12:55 CT bar on the announcement day." + corr)
    if key == "V2":
        return common + ("Enter long at the open of the 17:00 CT bar on every evening (Sun-Thu) from the second weekday "
                         "before the announcement day through the day before it (Wednesday announcement: Mon 17:00 and "
                         "Tue 17:00; Tuesday announcement: Sun 17:00 and Mon 17:00); each leg is closed by the protocol "
                         "forced flat at 15:10 CT and the last leg exits at the open of the 12:55 CT bar on the "
                         "announcement day; one round-turn cost per leg." + corr)
    return common + ("On the announcement day compute s = sign(open(13:35 CT bar) / open(12:55 CT bar) - 1) when the "
                     "13:35 bar opens; if s != 0 enter with side s at the open of the next quoted bar (normally the 13:36 "
                     "bar); exit at the open of the 15:08 CT bar the same day (forced flat 15:10 CT backstop)." + corr)


def run_one(bars: pd.DataFrame, ev: pd.DataFrame, name: str, sym_contract: str, corrected: bool = False):
    key = re.search(r"(V[1-3])_", name).group(1)
    entries, exits, side, legs = build_variant(bars, ev, key, corrected)
    tr = P.backtest_signals(bars, entries, exits, side, sym=sym_contract)
    ot = bars["open_time"].values.astype("datetime64[ns]").astype(np.int64)
    ff, reopen = forced_flat_and_reopen_ns(bars)
    rec = {"name": name, "variant": key, "symbol": sym_contract, "data": "NAS100" if sym_contract == "NQ" else "SPX500",
           "rule": rule_text(key, sym_contract, corrected), "n": 0, "n_events": int(len(ev)),
           "n_legs_scheduled": int(len(legs)), "n_legs_entry_bar_ok": int(legs["ok"].sum()),
           "entry_lag_min_mean": float(legs.loc[legs["ok"], "lag_min"].mean()) if legs["ok"].any() else None}
    if key == "V3":
        rec["n_signal_zero"] = int((legs["ref_ok"] & legs["sig_ok"] & (legs["signal"] == 0)).sum())
        rec["n_signal_long"] = int((legs["ok"] & (legs["signal"] > 0)).sum())
        rec["n_signal_short"] = int((legs["ok"] & (legs["signal"] < 0)).sum())
    if len(tr) == 0:
        rec.update({"survivor": False, "survivor_checks": {}})
        return rec, tr
    e_rows = np.searchsorted(ot, tr["entry_time"].values.astype("datetime64[ns]").astype(np.int64))
    x_ns = tr["exit_time"].values.astype("datetime64[ns]").astype(np.int64)
    invalid = x_ns >= reopen[e_rows]
    rec["n_dropped_unpriceable"] = int(invalid.sum())
    tr = tr.loc[~invalid].reset_index(drop=True)
    # map trades to events via the leg fill row
    fill_ns = ot[np.minimum(legs["j"].values, len(ot) - 1)]
    m = pd.Series(legs["event_date"].values, index=fill_ns)
    m = m[~m.index.duplicated()]
    tr["event_date"] = m.reindex(tr["entry_time"].values.astype("datetime64[ns]").astype(np.int64)).values
    rec["n_trades_unmapped"] = int(tr["event_date"].isna().sum())
    st = P.summarize(tr, bars)
    rec["n"] = int(st["n"])
    rec.update({k: float(st[k]) for k in ("trades_per_day", "mean_net", "median_net", "std_net", "t_stat", "ci95_low",
                                          "ci95_high", "win_rate", "avg_win", "avg_loss", "sharpe_per_trade",
                                          "sharpe_annual", "total_net", "gross_mean", "max_drawdown")})
    rec["by_year"] = {k: round(v, 1) for k, v in st["by_year"].items()}
    rec["n_by_year"] = st["n_by_year"]
    rec["reasons"] = {k: int(v) for k, v in tr["reason"].value_counts().items()}
    ect = tr["entry_time"].dt.tz_convert(TZ)
    xct = tr["exit_time"].dt.tz_convert(TZ)
    rec["entry_tod_ct"] = ect.dt.strftime("%H:%M").value_counts().head(5).to_dict()
    rec["exit_tod_ct"] = xct.dt.strftime("%H:%M").value_counts().head(5).to_dict()
    rec["entry_dow"] = {DOW_NAME[int(d)]: int(c) for d, c in ect.dt.dayofweek.value_counts().items()}
    rec["hold_minutes_median"] = float(((tr["exit_time"] - tr["entry_time"]).dt.total_seconds() / 60).median())
    # per-event sums (one number per announcement) and release-time classes
    pe = tr.groupby("event_date")["net"].sum()
    rec["per_event"] = {"n_events_traded": int(len(pe)), "mean_net": float(pe.mean()), "t_stat": tstat(pe.values),
                        "win_rate": float((pe > 0).mean())}
    cls = ev.set_index("date")["release_ct_assumed"]
    tr["release_ct"] = cls.reindex(tr["event_date"]).values
    rec["by_release_time"] = {str(k): {"n": int(len(g)), "mean_net": round(float(g["net"].mean()), 2), "t_stat": round(tstat(g["net"].values), 2)}
                              for k, g in tr.groupby("release_ct")}
    if key == "V3":
        rec["by_side"] = {("long" if s > 0 else "short"): {"n": int(len(g)), "mean_net": round(float(g["net"].mean()), 2),
                                                            "t_stat": round(tstat(g["net"].values), 2)} for s, g in tr.groupby("side")}
    rec["dsr"] = float(P.deflated_sharpe(st["sharpe_per_trade"], st["n"], N_VARIANTS_DSR))
    rec["survivor"], rec["survivor_checks"] = qualifies(st)
    return rec, tr


def by_year_str(rec: dict) -> str:
    return " ".join(f"{y}:{rec.get('by_year', {}).get(y, 0.0):+.0f}" for y in IS_YEARS)


def fmt_row(r: dict) -> str:
    if r["n"] == 0:
        return f"{r['name']:<34} n=0 (legs scheduled={r['n_legs_scheduled']} ok={r['n_legs_entry_bar_ok']})"
    pe = r["per_event"]
    return (f"{r['name']:<34} n={r['n']:4d} tpd={r['trades_per_day']:.4f} mean=${r['mean_net']:8.2f} t={r['t_stat']:6.2f} "
            f"ci=[{r['ci95_low']:.1f},{r['ci95_high']:.1f}] wr={r['win_rate']:.3f} aw={r['avg_win']:.1f} al={r['avg_loss']:.1f} "
            f"spt={r['sharpe_per_trade']:.3f} dsr={r['dsr']:.3f} posyrs={r['survivor_checks']['pos_years']}/13 surv={r['survivor']}\n"
            f"{'':34} {by_year_str(r)}\n"
            f"{'':34} reasons={r['reasons']} per_event: n={pe['n_events_traded']} mean=${pe['mean_net']:.2f} t={pe['t_stat']:.2f} "
            f"wr={pe['win_rate']:.3f} by_release={r['by_release_time']} dropped={r.get('n_dropped_unpriceable', 0)}"
            + (f" by_side={r['by_side']} zero_signals={r['n_signal_zero']}" if "by_side" in r else ""))


# ----------------------------------------------------------------------------- main
def main():
    bars = load_bars_index("SPX500", "1m", root=ROOT).sort_values("open_time").reset_index(drop=True)
    assert bars["open_time"].min() >= IS_START and bars["open_time"].max() <= IS_END, "in-sample data only"
    assert (bars[["open", "high", "low", "close"]] > 0).all().all()
    print(f"SPX500 1m bars={len(bars)} {bars['open_time'].iloc[0]} -> {bars['open_time'].iloc[-1]}")

    dates = fomc_dates()
    sched = dates[dates["scheduled"]]
    print(f"\nFOMC pages parsed: {len(dates)} panels 2005-2020, {len(sched)} scheduled statements, "
          f"{int((~dates['scheduled']).sum())} excluded (conference calls / unscheduled). {dates.attrs['note_2020']}")
    mism = dates[dates["link_mismatch"]]
    if len(mism):
        print("statement-link date differs from heading (heading kept):",
              [(r.title, r.statement_link_date) for r in mism.itertuples()])
    ev = build_events(dates, bars)
    print(f"\nANNOUNCEMENT DATES USED (in-sample, {len(ev)}): date dow title | press_conf | assumed release CT | "
          f"data-detected max-range minute CT")
    for r in ev.itertuples():
        print(f"  {r.date.date()} {DOW_NAME[r.date.dayofweek]} {r.title:<36} pc={int(r.press_conf)} rel={r.release_ct_assumed} "
              f"detected={r.detected_max_range_minute_ct}")
    print("\nall scheduled statement dates 2005-2020 (incl. out-of-sample, for the record):")
    print(" ".join(d.strftime("%Y-%m-%d") for d in sched["date"]))
    agree = ev["detected_max_range_minute_ct"].notna()
    det_min = pd.to_timedelta(ev.loc[agree, "detected_max_range_minute_ct"] + ":00")
    rel_min = pd.to_timedelta(ev.loc[agree, "release_ct_assumed"] + ":00")
    within = ((det_min - rel_min).dt.total_seconds() / 60).between(-5, 30)
    print(f"data check: detected max-range minute within [-5,+30] min of the assumed release time on {int(within.sum())}/{int(agree.sum())} days; "
          f"days where 12:55 CT is POST-release: {int(ev['pc_2011_2012'].sum())} ({', '.join(d.strftime('%Y-%m-%d') for d in ev.loc[ev['pc_2011_2012'], 'date'])})\n")

    results, trades = [], {}
    for name in VARIANTS:
        rec, tr = run_one(bars, ev, name, "ES")
        results.append(rec)
        trades[name] = tr
        print(fmt_row(rec))

    diagnostics = []
    nq = load_bars_index("NAS100", "1m", root=ROOT).sort_values("open_time").reset_index(drop=True)
    assert nq["open_time"].min() >= IS_START and nq["open_time"].max() <= IS_END
    ev_nq = build_events(dates, nq)
    print(f"\nDIAGNOSTIC D1: NAS100 twin (NQ contract spec, $20/pt, $8.78 rt) bars={len(nq)} events={len(ev_nq)}")
    for name in VARIANTS:
        rec, _ = run_one(nq, ev_nq, "D1_NAS100_" + name, "NQ")
        rec["diagnostic"] = True
        rec["note"] = "post-hoc diagnostic: NAS100 CFD twin of the pre-registered variant with NQ contract spec; not nominable"
        diagnostics.append(rec)
        print(fmt_row(rec))
    print("\nDIAGNOSTIC D2: release-time corrected on the eight 2011-2012 press-conference days (all instants 90 min earlier)")
    for name in VARIANTS:
        rec, _ = run_one(bars, ev, "D2_release_corrected_" + name, "ES", corrected=True)
        rec["diagnostic"] = True
        rec["note"] = ("post-hoc diagnostic: the 2011-2012 press-conference statements came out at 11:30 CT (data-confirmed), "
                       "so on those 8 days the exit is 11:25 and the V3 signal 12:05 vs 11:25; not nominable")
        diagnostics.append(rec)
        print(fmt_row(rec))

    survivors = [r for r in results if r["survivor"]]
    out = {"family": FAMILY, "symbol": "ES", "data": "SPX500 Oanda CFD 1-minute bars, IS 2005-01..2017-12", "bar_size": "1min",
           "n_variants": len(VARIANTS), "dsr_N": N_VARIANTS_DSR,
           "announcement_dates_used": [d.strftime("%Y-%m-%d") for d in ev["date"]],
           "announcement_dates_all_scheduled_2005_2020": [d.strftime("%Y-%m-%d") for d in sched["date"]],
           "note_2020": dates.attrs["note_2020"],
           "release_time_check": ev[["date", "title", "press_conf", "release_ct_assumed", "detected_max_range_minute_ct"]]
           .assign(date=lambda d: d["date"].dt.strftime("%Y-%m-%d")).to_dict("records"),
           "variants": results, "diagnostics": diagnostics, "survivors": [r["name"] for r in survivors]}
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=1, default=str)
    print(f"\nsurvivors: {[r['name'] for r in survivors] or 'none'}; wrote {OUT_JSON}")
    return out


if __name__ == "__main__":
    main()
