"""Hypothesis family: calendar_events.

Question: do scheduled calendar events produce a tradable intraday edge in BTC / ETH that a Topstep
MBT / MET trader could capture?  Events tested (all pre-specified below, before looking at results):

  A. Options expiry (Deribit, 08:00 UTC every Friday; the last Friday of the month is the large
     monthly/quarterly expiry).  Two mechanisms: (i) the final hour into the settlement window is
     dominated by hedging / settlement-price games and should REVERT after 08:00 UTC; (ii) the
     "pin" that dealer gamma hedging imposes over the last 24 h is released at expiry, so the 24 h
     pre-expiry move should CONTINUE once the pin is gone.
  B. CME Bitcoin futures expiry (last Friday of the month, cash settled to the CME CF BRR which is
     computed over the 15:00-16:00 London window; trading terminates 16:00 London).  Hedging of the
     expiring contract is executed as a TWAP inside the BRR window; the move during that window
     should REVERT once the window closes (fade) -- or, if it is informed, continue (follow).
  C. US macro: CPI and NFP (07:30 CT, 8:30 ET) and FOMC statements (13:00 CT, 2 pm ET).  Known
     2020-2024 release calendars are embedded below.  We test (i) first-5-minute reaction
     continuation (post-announcement drift) vs fade (over-reaction), and (ii) the pre-FOMC
     announcement drift (Lucca-Moench) applied to BTC.
  D. Turn of the month / month end: (i) long the Topstep session that contains the 00:00 UTC roll
     into the 1st of the month (month-start inflows, "turn-of-month" effect); (ii) short the US day
     session of the last weekday of the month (window-dressing / de-risking into month end).
  E. Day of week: short the Friday session (Thu 17:00 CT -> Fri 15:10 CT): CME / Topstep traders
     must be flat over the weekend, so pre-weekend de-risking should produce a negative drift.

Every variant run is listed in VARIANTS and logged to calendar_events_results.json; the count feeds
the deflated-Sharpe correction.  Follow / fade pairs are both counted even though one is close to
the mirror image of the other.

Signals are computed on bar i and acted on at the open of bar i+1 (protocol.backtest_signals).
Entries are flagged on the bar BEFORE the desired fill bar.  Costs: protocol.CONTRACT.

Note on protocol.forced_flat_time: it returns True for every bar with CT time >= 15:10, including
the 17:00-23:59 CT evening, which makes backtest_signals close any evening-entered position on its
own entry bar.  As in research/hyp/session_drift.py we patch it (for the duration of each backtest
call only) to be True solely during the 15:10-17:00 CT daily break.  Daytime behaviour (forced flat
at the 15:10 CT bar open) is unchanged.

Run: cd /home/user/j && python3 -m research.hyp.calendar_events
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
OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calendar_events_results.json")

SUN, MON, TUE, WED, THU, FRI, SAT = 6, 0, 1, 2, 3, 4, 5

# ----------------------------------------------------------------------------- known event calendars
# FOMC scheduled statement dates (2:00 pm ET = 13:00 CT).  The March 2020 scheduled meeting did not take
# place (replaced by the 15 March 2020 Sunday emergency action); emergency moves are excluded.
FOMC_DATES = [
    "2020-01-29", "2020-04-29", "2020-06-10", "2020-07-29", "2020-09-16", "2020-11-05", "2020-12-16",
    "2021-01-27", "2021-03-17", "2021-04-28", "2021-06-16", "2021-07-28", "2021-09-22", "2021-11-03", "2021-12-15",
    "2022-01-26", "2022-03-16", "2022-05-04", "2022-06-15", "2022-07-27", "2022-09-21", "2022-11-02", "2022-12-14",
    "2023-02-01", "2023-03-22", "2023-05-03", "2023-06-14", "2023-07-26", "2023-09-20", "2023-11-01", "2023-12-13",
    "2024-01-31", "2024-03-20", "2024-05-01", "2024-06-12",
]
# BLS CPI release dates (8:30 am ET = 07:30 CT)
CPI_DATES = [
    "2020-01-14", "2020-02-13", "2020-03-11", "2020-04-10", "2020-05-12", "2020-06-10", "2020-07-14", "2020-08-12",
    "2020-09-11", "2020-10-13", "2020-11-12", "2020-12-10",
    "2021-01-13", "2021-02-10", "2021-03-10", "2021-04-13", "2021-05-12", "2021-06-10", "2021-07-13", "2021-08-11",
    "2021-09-14", "2021-10-13", "2021-11-10", "2021-12-10",
    "2022-01-12", "2022-02-10", "2022-03-10", "2022-04-12", "2022-05-11", "2022-06-10", "2022-07-13", "2022-08-10",
    "2022-09-13", "2022-10-13", "2022-11-10", "2022-12-13",
    "2023-01-12", "2023-02-14", "2023-03-14", "2023-04-12", "2023-05-10", "2023-06-13", "2023-07-12", "2023-08-10",
    "2023-09-13", "2023-10-12", "2023-11-14", "2023-12-12",
    "2024-01-11", "2024-02-13", "2024-03-12", "2024-04-10", "2024-05-15", "2024-06-12",
]
# BLS Employment Situation (NFP) release dates (8:30 am ET = 07:30 CT)
NFP_DATES = [
    "2020-01-10", "2020-02-07", "2020-03-06", "2020-04-03", "2020-05-08", "2020-06-05", "2020-07-02", "2020-08-07",
    "2020-09-04", "2020-10-02", "2020-11-06", "2020-12-04",
    "2021-01-08", "2021-02-05", "2021-03-05", "2021-04-02", "2021-05-07", "2021-06-04", "2021-07-02", "2021-08-06",
    "2021-09-03", "2021-10-08", "2021-11-05", "2021-12-03",
    "2022-01-07", "2022-02-04", "2022-03-04", "2022-04-01", "2022-05-06", "2022-06-03", "2022-07-08", "2022-08-05",
    "2022-09-02", "2022-10-07", "2022-11-04", "2022-12-02",
    "2023-01-06", "2023-02-03", "2023-03-10", "2023-04-07", "2023-05-05", "2023-06-02", "2023-07-07", "2023-08-04",
    "2023-09-01", "2023-10-06", "2023-11-03", "2023-12-08",
    "2024-01-05", "2024-02-02", "2024-03-08", "2024-04-05", "2024-05-03", "2024-06-07",
]


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
    elif tz == "utc":
        t = bars["open_time"]
    else:
        t = bars["open_time"].dt.tz_convert(tz)
    # local calendar date as a NAIVE datetime64 (tz-aware .values would silently convert back to UTC)
    dates = t.dt.normalize().dt.tz_localize(None).values.astype("datetime64[ns]")
    return (t.dt.hour * 60 + t.dt.minute).values, t.dt.dayofweek.values, dates


def forced_flat_break_only(ts_utc: pd.Series) -> np.ndarray:
    """True only during the 15:10-17:00 CT daily break (see module docstring)."""
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


def last_friday_mask(dates: np.ndarray, dow: np.ndarray) -> np.ndarray:
    """True on bars whose (local) date is the last Friday of its month."""
    d = pd.DatetimeIndex(dates)
    is_fri = dow == FRI
    days_in_month = d.days_in_month.values
    return is_fri & (d.day.values + 7 > days_in_month)


def window_return(bars: pd.DataFrame, tz: str, start_min: int, end_min: int, day_filter: np.ndarray | None = None):
    """Per-bar array: on the bar whose local time == end_min - 5, the return from the open of the bar at
    start_min (same local date) to the close of that bar.  NaN elsewhere.  Only uses data up to and
    including the flagged bar (no look-ahead)."""
    minutes, dow, dates = tod(bars, tz)
    out = np.full(len(bars), np.nan)
    start_mask = minutes == start_min
    end_mask = minutes == end_min - 5
    if day_filter is not None:
        end_mask &= day_filter
    start_open = pd.Series(bars["open"].values[start_mask], index=dates[start_mask])
    start_open = start_open[~start_open.index.duplicated()]
    idx = np.where(end_mask)[0]
    for i in idx:
        d = dates[i]
        if d in start_open.index:
            out[i] = bars["close"].values[i] / start_open.loc[d] - 1.0
    return out


def window_return_prev_day(bars: pd.DataFrame, tz: str, start_min: int, end_min: int, day_filter: np.ndarray | None = None):
    """Like window_return but the start bar is on the PREVIOUS local date (24 h windows)."""
    minutes, dow, dates = tod(bars, tz)
    out = np.full(len(bars), np.nan)
    start_mask = minutes == start_min
    end_mask = minutes == end_min - 5
    if day_filter is not None:
        end_mask &= day_filter
    start_open = pd.Series(bars["open"].values[start_mask], index=dates[start_mask])
    start_open = start_open[~start_open.index.duplicated()]
    for i in np.where(end_mask)[0]:
        d = dates[i] - np.timedelta64(1, "D")
        if d in start_open.index:
            out[i] = bars["close"].values[i] / start_open.loc[d] - 1.0
    return out


def date_mask(bars: pd.DataFrame, date_list, tz: str = "ct") -> np.ndarray:
    _, _, dates = tod(bars, tz)
    wanted = pd.to_datetime(date_list).values.astype("datetime64[ns]")
    return np.isin(dates, wanted)


# ----------------------------------------------------------------------------- variant builders
# builder(bars) -> (entries, exits, side, kwargs, rule_text)
def V_expiry(kind: str, mode: str, hold: str):
    """Deribit options expiry at 08:00 UTC Friday.
    kind: 'weekly' (every Friday) or 'monthly' (last Friday of the month)
    mode: 'fade_lasthour' (side = -sign(07:00->08:00 UTC return)) or 'follow_24h' (side = +sign(Thu 08:00 -> Fri 08:00 UTC return))
    hold: '4h' (48 bars) or 'flat' (hold to the Friday 15:10 CT forced flat)."""
    def build(bars):
        minutes, dow, dates = tod(bars, "utc")
        day = (dow == FRI) if kind == "weekly" else last_friday_mask(dates, dow)
        if mode == "fade_lasthour":
            r = window_return(bars, "utc", hhmm(7), hhmm(8), day)
            side = (-np.sign(np.nan_to_num(r))).astype(int)
            sig = "r = close(07:55 UTC bar) / open(07:00 UTC bar) - 1 on the expiry Friday; side = -sign(r)"
        else:
            r = window_return_prev_day(bars, "utc", hhmm(8), hhmm(8), day)
            side = (np.sign(np.nan_to_num(r))).astype(int)
            sig = "r = close(Fri 07:55 UTC bar) / open(Thu 08:00 UTC bar) - 1; side = +sign(r)"
        entries = ~np.isnan(r) & (side != 0)
        exits = np.zeros(len(bars), dtype=bool)
        kw = {"max_hold_bars": 48} if hold == "4h" else {}
        rule = (f"BTC/ETH 5-min bars. On {'every Friday' if kind == 'weekly' else 'the last Friday of each month'} "
                f"(Deribit {kind} options expiry 08:00 UTC): {sig}. Enter 1 contract at the open of the 08:00 UTC bar; "
                f"exit {'at the open of the bar 48 bars (4 h) later' if hold == '4h' else 'at the 15:10 CT forced flat'}"
                f" (earlier if the Topstep 15:10 CT flat comes first). No stop/target.")
        return entries, exits, side, kw, rule
    return build


def V_cme_brr(mode: str):
    """CME BTC futures expiry: last Friday of the month, BRR window 15:00-16:00 London.
    side = -sign (fade) or +sign (follow) of the BRR-window return; enter at the 16:00 London open; exit at the
    15:10 CT forced flat."""
    def build(bars):
        minutes, dow, dates = tod(bars, "Europe/London")
        day = last_friday_mask(dates, dow)
        r = window_return(bars, "Europe/London", hhmm(15), hhmm(16), day)
        s = -1 if mode == "fade" else +1
        side = (s * np.sign(np.nan_to_num(r))).astype(int)
        entries = ~np.isnan(r) & (side != 0)
        exits = np.zeros(len(bars), dtype=bool)
        rule = (f"BTC 5-min bars. On the last Friday of each month (CME BTC futures expiry): r = close(15:55 London bar) / "
                f"open(15:00 London bar) - 1 (the CME CF BRR calculation window). side = {'-' if s < 0 else '+'}sign(r). "
                f"Enter 1 contract at the open of the 16:00 London bar; exit at the 15:10 CT forced flat. No stop/target.")
        return entries, exits, side, {}, rule
    return build


def V_macro_react(event: str, mode: str):
    """First-5-minute reaction to a scheduled release.
    event: 'cpi_nfp' (07:30 CT; signal bar 07:30-07:35, fill 07:35) or 'fomc' (13:00 CT; signal bar 13:00-13:05, fill 13:05).
    mode: 'follow' (+sign) or 'fade' (-sign).  Exit at the 15:10 CT forced flat."""
    def build(bars):
        minutes, dow, dates = tod(bars, "ct")
        if event == "cpi_nfp":
            days = date_mask(bars, CPI_DATES + NFP_DATES)
            sig_min = hhmm(7, 30)
            label = "CPI or NFP release days (07:30 CT)"
        else:
            days = date_mask(bars, FOMC_DATES)
            sig_min = hhmm(13, 0)
            label = "scheduled FOMC statement days (13:00 CT)"
        sig_bar = days & (minutes == sig_min)
        r = np.where(sig_bar, bars["close"].values / bars["open"].values - 1.0, np.nan)
        s = -1 if mode == "fade" else +1
        side = (s * np.sign(np.nan_to_num(r))).astype(int)
        entries = sig_bar & (side != 0)
        exits = np.zeros(len(bars), dtype=bool)
        hh, mm = divmod(sig_min, 60)
        rule = (f"BTC 5-min bars. On {label}: r = close/open - 1 of the {hh:02d}:{mm:02d} CT bar (the release bar). "
                f"side = {'-' if s < 0 else '+'}sign(r). Enter 1 contract at the open of the {hh:02d}:{mm + 5:02d} CT bar; "
                f"exit at the 15:10 CT forced flat. No stop/target.")
        return entries, exits, side, {}, rule
    return build


def V_pre_fomc_drift():
    """Long from the 17:00 CT re-open on the evening before an FOMC statement to the 13:00 CT open on the day."""
    def build(bars):
        minutes, dow, dates = tod(bars, "ct")
        fomc = pd.to_datetime(FOMC_DATES).values.astype("datetime64[ns]")
        eve = (fomc - np.timedelta64(1, "D"))
        m_entry = np.isin(dates, eve) & (minutes == hhmm(17, 0))
        m_exit = np.isin(dates, fomc) & (minutes == hhmm(13, 0))
        entries = shift_back(m_entry)
        exits = shift_back(m_exit)
        side = np.ones(len(bars), dtype=int)
        rule = ("BTC 5-min bars. On the evening before a scheduled FOMC statement day, go long 1 contract at the open of "
                "the 17:00 CT bar (CME re-open); exit at the open of the 13:00 CT bar on the FOMC day (statement time). "
                "No stop/target.")
        return entries, exits, side, {}, rule
    return build


def V_turn_of_month_long():
    """Long the Topstep session that contains 00:00 UTC of the 1st of the month."""
    def build(bars):
        minutes, dow, dates = tod(bars, "ct")
        d = pd.DatetimeIndex(dates)
        last_day = d.day.values == d.days_in_month.values
        m_entry = last_day & (minutes == hhmm(17, 0)) & np.isin(dow, [SUN, MON, TUE, WED, THU])
        entries = shift_back(m_entry)
        exits = np.zeros(len(bars), dtype=bool)
        side = np.ones(len(bars), dtype=int)
        rule = ("BTC 5-min bars. On the last calendar day of the month (Chicago date), if that evening is a tradable "
                "Topstep session (Sun-Thu), go long 1 contract at the open of the 17:00 CT bar; hold through the 00:00 UTC "
                "month roll and exit at the next 15:10 CT forced flat. Skip if the last day is a Friday or Saturday. "
                "No stop/target.")
        return entries, exits, side, {}, rule
    return build


def V_monthend_day_short():
    """Short the US day session (08:30 -> 15:10 CT) of the last weekday of the month."""
    def build(bars):
        minutes, dow, dates = tod(bars, "ct")
        d = pd.DatetimeIndex(dates)
        dim = d.days_in_month.values
        day = d.day.values
        # last weekday: last day if Mon-Fri; else the preceding Friday
        wd = dow <= FRI
        last_wd = wd & (((day == dim)) | ((dow == FRI) & (day + 2 >= dim)))
        m_entry = last_wd & (minutes == hhmm(8, 30))
        entries = shift_back(m_entry)
        exits = np.zeros(len(bars), dtype=bool)
        side = -np.ones(len(bars), dtype=int)
        rule = ("BTC 5-min bars. On the last weekday of each month (Chicago date; if the month ends on a weekend, the "
                "preceding Friday), short 1 contract at the open of the 08:30 CT bar; exit at the 15:10 CT forced flat. "
                "No stop/target.")
        return entries, exits, side, {}, rule
    return build


def V_friday_session(side_val: int):
    def build(bars):
        minutes, dow, dates = tod(bars, "ct")
        m_entry = (dow == THU) & (minutes == hhmm(17, 0))
        entries = shift_back(m_entry)
        exits = np.zeros(len(bars), dtype=bool)
        side = np.full(len(bars), side_val, dtype=int)
        rule = (f"BTC 5-min bars. {'Short' if side_val < 0 else 'Long'} 1 contract at the open of the Thursday 17:00 CT bar "
                f"(start of the Friday CME session); exit at the Friday 15:10 CT forced flat. No stop/target.")
        return entries, exits, side, {}, rule
    return build


VARIANTS = [
    # A. options expiry
    ("BTC_wexp_lasthour_fade_4h", "BTCUSDT", V_expiry("weekly", "fade_lasthour", "4h")),
    ("BTC_wexp_24h_follow_flat", "BTCUSDT", V_expiry("weekly", "follow_24h", "flat")),
    ("BTC_mexp_lasthour_fade_4h", "BTCUSDT", V_expiry("monthly", "fade_lasthour", "4h")),
    ("BTC_mexp_24h_follow_flat", "BTCUSDT", V_expiry("monthly", "follow_24h", "flat")),
    ("ETH_wexp_lasthour_fade_4h", "ETHUSDT", V_expiry("weekly", "fade_lasthour", "4h")),
    # B. CME futures expiry / BRR window
    ("BTC_cme_brr_fade", "BTCUSDT", V_cme_brr("fade")),
    ("BTC_cme_brr_follow", "BTCUSDT", V_cme_brr("follow")),
    # C. US macro
    ("BTC_cpi_nfp_react_follow", "BTCUSDT", V_macro_react("cpi_nfp", "follow")),
    ("BTC_cpi_nfp_react_fade", "BTCUSDT", V_macro_react("cpi_nfp", "fade")),
    ("BTC_fomc_react_follow", "BTCUSDT", V_macro_react("fomc", "follow")),
    ("BTC_fomc_react_fade", "BTCUSDT", V_macro_react("fomc", "fade")),
    ("BTC_pre_fomc_drift_long", "BTCUSDT", V_pre_fomc_drift()),
    # D. month turn
    ("BTC_turn_of_month_long", "BTCUSDT", V_turn_of_month_long()),
    ("BTC_monthend_day_short", "BTCUSDT", V_monthend_day_short()),
    # E. day of week
    ("BTC_friday_session_short", "BTCUSDT", V_friday_session(-1)),
]


# ----------------------------------------------------------------------------- diagnostics (not variants)
def event_day_range(bars: pd.DataFrame, dates_list, start_min: int, end_min: int, label: str) -> dict:
    """Realised high-low range (in % of open) over a CT window on event days vs all other weekdays."""
    minutes, dow, dates = tod(bars, "ct")
    ev = date_mask(bars, dates_list)
    inwin = (minutes >= start_min) & (minutes < end_min) & (dow <= FRI)
    df = pd.DataFrame({"d": dates, "ev": ev, "hi": bars["high"].values, "lo": bars["low"].values, "o": bars["open"].values})[inwin]
    g = df.groupby("d").agg(ev=("ev", "max"), hi=("hi", "max"), lo=("lo", "min"), o=("o", "first"))
    g["rng"] = (g["hi"] - g["lo"]) / g["o"] * 100
    return {"label": label, "event_days": int(g["ev"].sum()), "range_pct_event": float(g.loc[g["ev"], "rng"].mean()),
            "range_pct_other": float(g.loc[~g["ev"], "rng"].mean())}


def main():
    results = []
    cache = {}
    for name, sym, build in VARIANTS:
        if sym not in cache:
            cache[sym] = load_bars(sym, "5min", root=ROOT)
        bars = cache[sym]
        entries, exits, side, kw, rule = build(bars)
        tr, st = run(bars, sym, entries, exits, side, **kw)
        rec = {"name": name, "symbol": sym, "rule": rule, "n": int(st.get("n", 0))}
        if st.get("n", 0) > 0:
            rec.update({k: st[k] for k in ("trades_per_day", "mean_net", "t_stat", "ci95_low", "ci95_high", "win_rate",
                                           "avg_win", "avg_loss", "sharpe_per_trade", "total_net", "gross_mean",
                                           "max_drawdown")})
            rec["by_year"] = {k: round(v, 1) for k, v in st["by_year"].items()}
            rec["n_by_year"] = st["n_by_year"]
            rec["reasons"] = tr["reason"].value_counts().to_dict()
            rec["mean_hold_bars"] = float(tr["hold_bars"].mean())
            rec["dsr"] = P.deflated_sharpe(st["sharpe_per_trade"], st["n"], len(VARIANTS))
        results.append(rec)
        print(f"{name:28s} {sym:8s} n={rec['n']:4d} mean_net={rec.get('mean_net', 0):8.2f} t={rec.get('t_stat', 0):6.2f} "
              f"wr={rec.get('win_rate', 0):.3f} tpd={rec.get('trades_per_day', 0):.3f} by_year={rec.get('by_year')}")
        sys.stdout.flush()

    # ---- diagnostics: do the events matter at all (realised range on event days vs other days)?
    bars = cache["BTCUSDT"]
    diag = {}
    for lab, dl, a, b in (("CPI 07:30-09:30 CT", CPI_DATES, hhmm(7, 30), hhmm(9, 30)),
                          ("NFP 07:30-09:30 CT", NFP_DATES, hhmm(7, 30), hhmm(9, 30)),
                          ("FOMC 13:00-15:10 CT", FOMC_DATES, hhmm(13, 0), hhmm(15, 10))):
        d = event_day_range(bars, dl, a, b, lab)
        diag[lab] = d
        print(f"\n{lab}: event days={d['event_days']} mean range {d['range_pct_event']:.2f}% vs other days {d['range_pct_other']:.2f}%")
    # expiry-Friday vs other-Friday 08:00-12:00 UTC range
    minutes, dow, dates = tod(bars, "utc")
    lf = last_friday_mask(dates, dow)
    inwin = (minutes >= hhmm(8)) & (minutes < hhmm(12)) & (dow == FRI)
    df = pd.DataFrame({"d": dates, "lf": lf, "hi": bars["high"].values, "lo": bars["low"].values, "o": bars["open"].values})[inwin]
    g = df.groupby("d").agg(lf=("lf", "max"), hi=("hi", "max"), lo=("lo", "min"), o=("o", "first"))
    g["rng"] = (g["hi"] - g["lo"]) / g["o"] * 100
    diag["expiry_friday_0800_1200_UTC_range"] = {"monthly_expiry_fridays": int(g["lf"].sum()),
                                                 "range_pct_monthly": float(g.loc[g["lf"], "rng"].mean()),
                                                 "range_pct_other_fridays": float(g.loc[~g["lf"], "rng"].mean())}
    print(f"\nFriday 08:00-12:00 UTC range: monthly-expiry Fridays {diag['expiry_friday_0800_1200_UTC_range']['range_pct_monthly']:.2f}% "
          f"vs other Fridays {diag['expiry_friday_0800_1200_UTC_range']['range_pct_other_fridays']:.2f}%")
    # mean 5-min return by hour relative to the 08:00 UTC Friday expiry (bp), Fridays only, informational
    r = np.log(bars["close"] / bars["open"]).values * 1e4
    fri = dow == FRI
    tab = pd.DataFrame({"h": bars["open_time"].dt.hour.values[fri], "r": r[fri]}).groupby("h")["r"].agg(["mean", "count"])
    tab["t"] = tab["mean"] / (pd.DataFrame({"h": bars["open_time"].dt.hour.values[fri], "r": r[fri]}).groupby("h")["r"].std() / np.sqrt(tab["count"]))
    diag["friday_mean_5min_ret_by_utc_hour_bp"] = tab.round(3).to_dict(orient="index")
    print("\nFriday mean 5-min log return by UTC hour (bp):")
    print(tab.round(3).to_string())

    with open(OUT_JSON, "w") as fh:
        json.dump({"n_variants": len(VARIANTS), "variants": results, "diagnostics": diag}, fh, indent=1, default=str)
    print(f"\nwrote {OUT_JSON}; n_variants={len(VARIANTS)}")


if __name__ == "__main__":
    main()
