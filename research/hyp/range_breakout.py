"""Hypothesis family: range_breakout  (in-sample only, ROOT = data_research/IS)

Opening-range breakouts (ORB) of the US session and of the UTC day, previous-UTC-day high/low breaks,
and fades of failed breakouts, on BTCUSDT / ETHUSDT perpetual 5-minute bars (proxy for CME MBT / MET).

Economic stories
  * ORB: the first 30/60 minutes after a session open (08:30 CT = US equity cash open, the time crypto's
    correlation with US risk assets is expressed; 00:00 UTC = daily-candle open / funding settlement /
    daily P&L mark) is an auction that establishes a value area.  A 5-minute close beyond it means one
    side has absorbed the auction's liquidity; stop orders and intraday trend followers then push the
    move further (the classic ORB argument).  The range itself is the volatility scale for the stop.
  * Previous-day high/low break: the prior day's extremes are the most widely watched intraday levels;
    a close beyond them triggers resting stops and breakout systems (continuation), with a stop sized
    as a fraction of the previous day's range (volatility-scaled).
  * Failed-breakout fade: a break that closes back inside the range within 30 minutes is a stop-run /
    liquidity grab; trapped breakout traders unwind and price returns into the range.  Stop above the
    excursion extreme (the level that would invalidate the "trap"), time exit.

Mechanics (all variants)
  * Signal computed from the close of 5-min bar i, fill at the OPEN of bar i+1 (as protocol.backtest_signals).
  * One position at a time; ORB / PDHL-break variants take only the FIRST break of the session/day;
    fade variants are eligible on every failed-break event (still one position at a time).
  * Stops are checked on bar high/low (stop before target, conservative), targets as a multiple of the
    stop distance (R), time exits at the open of the bar `max_hold_bars` after entry, and the Topstep
    forced flat at the open of the 15:10 CT bar / before the weekend.  Costs: protocol.CONTRACT.
  * Engine: `run_engine` replicates protocol.backtest_signals bar-for-bar but takes PER-TRADE stop
    distances (needed for range/vol-scaled stops).  It is validated against protocol.backtest_signals
    (patched exactly as the sibling families patch it: forced_flat_time flags only the 15:10-17:00 CT
    break, because the protocol's version also flags the allowed 17:00-24:00 CT evening session) on a
    constant-fraction stop/target case at the start of every run; any mismatch aborts the run.

Every variant that is run is listed in VARIANTS (fixed before any result was looked at) and logged in the
results JSON; the count feeds the deflated-Sharpe correction.

Run:  cd /home/user/j && python3 -m research.hyp.range_breakout
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
OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "range_breakout_results.json")

FADE_K = 6             # a break must close back inside within FADE_K bars (30 min) to count as "failed"
FADE_BUFFER = 0.10     # fade stop = excursion extreme + FADE_BUFFER x reference range
PD_STOP_FRAC = 0.25    # prev-day-break stop = PD_STOP_FRAC x previous-day range from entry
NARROW_LOOKBACK = 20   # sessions for the narrow-range median (strictly prior sessions)


# ----------------------------------------------------------------------------- helpers
def hhmm(h: int, m: int = 0) -> int:
    return h * 60 + m


def forced_flat_break_only(ts_utc: pd.Series) -> np.ndarray:
    t = P.ct(ts_utc)
    minutes = (t.dt.hour * 60 + t.dt.minute).values
    return (minutes >= 15 * 60 + 10) & (minutes < 17 * 60)


class Clock:
    """Per-bar minutes-of-day, integer day key and weekday in one time zone (utc or ct)."""

    def __init__(self, bars: pd.DataFrame, tz: str):
        t = bars["open_time"] if tz == "utc" else bars["ct"]
        self.minutes = (t.dt.hour * 60 + t.dt.minute).values
        self.day = t.dt.normalize().dt.tz_localize(None).values.astype("datetime64[D]").astype(np.int64)
        self.dow = t.dt.dayofweek.values


def day_transform(values: np.ndarray, day: np.ndarray, mask: np.ndarray, how: str) -> np.ndarray:
    """Per-day aggregate of values[mask], broadcast to every bar of that day (NaN if the day has no masked bar)."""
    s = pd.Series(np.where(mask, values, np.nan))
    return s.groupby(day).transform(how).values


def first_in_day(flag: np.ndarray, day: np.ndarray) -> np.ndarray:
    cum = pd.Series(flag.astype(np.int64)).groupby(day).cumsum().values
    return flag & (cum == 1)


def shift(a: np.ndarray, k: int, fill):
    out = np.full_like(a, fill)
    if k > 0:
        out[k:] = a[:-k]
    elif k < 0:
        out[:k] = a[-k:]
    else:
        out[:] = a
    return out


# ----------------------------------------------------------------------------- engine (per-trade stops)
def run_engine(bars: pd.DataFrame, entries: np.ndarray, side: np.ndarray, sym: str,
               stop_frac: np.ndarray | None = None, stop_dist: np.ndarray | None = None,
               stop_px: np.ndarray | None = None, target_frac: np.ndarray | None = None,
               target_rr: float | None = None, max_hold_bars: int | None = None,
               exits: np.ndarray | None = None) -> pd.DataFrame:
    """protocol.backtest_signals with per-signal-bar stop definitions.

    stop_frac[i] : fractional distance (as the protocol's stop_pct), stop_dist[i]: absolute $ distance from
    the fill price, stop_px[i]: absolute stop price.  target_frac[i] fractional, or target_rr x stop distance.
    A trade whose stop would not be on the loss side of the fill is skipped (counted in attrs['skipped']).
    """
    c = P.CONTRACT[sym]
    ts = bars["open_time"]
    o, h, l = bars["open"].values, bars["high"].values, bars["low"].values
    can_enter = P.entry_mask(ts)
    can_hold = P.tradable_mask(ts)
    flat_now = forced_flat_break_only(ts)
    n = len(bars)
    if exits is None:
        exits = np.zeros(n, dtype=bool)
    rows = []
    i, pos, skipped = 0, 0, 0
    ei = ep = sp = tp = None
    while i < n - 1:
        if pos == 0:
            if entries[i] and can_enter[i + 1] and can_hold[i + 1]:
                p = int(side[i]) if side[i] != 0 else 1
                ei = i + 1
                ep = o[ei]
                sp = None
                if stop_frac is not None:
                    sp = ep * (1 - stop_frac[i] * p)
                elif stop_dist is not None:
                    sp = ep - p * stop_dist[i]
                elif stop_px is not None:
                    sp = stop_px[i]
                if sp is not None and (not np.isfinite(sp) or p * (ep - sp) <= 0):
                    skipped += 1
                    i += 1
                    continue
                tp = None
                if target_frac is not None:
                    tp = ep * (1 + target_frac[i] * p)
                elif target_rr is not None and sp is not None:
                    tp = ep + p * target_rr * abs(ep - sp)
                pos = p
                i = ei
                continue
            i += 1
            continue
        reason, xp = None, None
        if sp is not None:
            if (pos == 1 and l[i] <= sp) or (pos == -1 and h[i] >= sp):
                xp, reason = sp, "stop"
        if xp is None and tp is not None:
            if (pos == 1 and h[i] >= tp) or (pos == -1 and l[i] <= tp):
                xp, reason = tp, "target"
        if xp is None and (flat_now[i] or not can_hold[i]):
            xp, reason = o[i], "flat"
        if xp is None and max_hold_bars is not None and i - ei >= max_hold_bars:
            xp, reason = o[i], "time"
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


def validate_engine(bars: pd.DataFrame, sym: str) -> None:
    """run_engine with constant fractional stop/target must reproduce protocol.backtest_signals exactly
    (with the protocol's forced_flat_time patched to the 15:10-17:00 CT break, as the sibling families do)."""
    rng = np.random.default_rng(1)
    n = len(bars)
    entries = rng.random(n) < 0.004
    side = rng.choice([-1, 1], n)
    exits = rng.random(n) < 0.01
    orig = P.forced_flat_time
    P.forced_flat_time = forced_flat_break_only
    try:
        ref = P.backtest_signals(bars, entries, exits, side, sym=sym, stop_pct=0.006, target_pct=0.012, max_hold_bars=40)
    finally:
        P.forced_flat_time = orig
    mine = run_engine(bars, entries, side, sym, stop_frac=np.full(n, 0.006), target_frac=np.full(n, 0.012),
                      max_hold_bars=40, exits=exits)
    ok = len(ref) == len(mine) and len(ref) > 100
    if ok:
        for col in ("entry_time", "exit_time", "side", "entry", "exit", "net", "hold_bars", "reason"):
            ok &= bool((ref[col].values == mine[col].values).all())
    if not ok:
        raise RuntimeError(f"engine validation FAILED for {sym}: ref n={len(ref)} mine n={len(mine)}")
    print(f"engine validation OK ({sym}, {len(ref)} random trades identical to protocol.backtest_signals)")


# ----------------------------------------------------------------------------- level builders
def opening_range(bars, ck: Clock, or_start: int, or_end: int):
    in_or = (ck.minutes >= or_start) & (ck.minutes < or_end)
    cnt = day_transform(np.ones(len(bars)), ck.day, in_or, "sum")
    full = cnt >= (or_end - or_start) // 5          # complete opening range only
    or_hi = np.where(full, day_transform(bars["high"].values, ck.day, in_or, "max"), np.nan)
    or_lo = np.where(full, day_transform(bars["low"].values, ck.day, in_or, "min"), np.nan)
    return or_hi, or_lo


def prev_day_levels(bars, ck: Clock):
    """Previous UTC day's high/low broadcast to every bar of the current day (NaN if the previous calendar
    day is missing from the data)."""
    daily = pd.DataFrame({"hi": bars["high"].values, "lo": bars["low"].values, "d": ck.day}).groupby("d").agg(hi=("hi", "max"), lo=("lo", "min"))
    consecutive = np.r_[False, np.diff(daily.index.values) == 1]
    pdh = daily["hi"].shift(1).where(consecutive)
    pdl = daily["lo"].shift(1).where(consecutive)
    key = pd.Series(ck.day)
    return key.map(pdh).values, key.map(pdl).values


def narrow_filter(or_hi, or_lo, ck: Clock, wide: bool = False) -> np.ndarray:
    """True on days whose opening-range width (as % of price) is below (wide=True: above) the median of the
    previous NARROW_LOOKBACK sessions that had a complete opening range."""
    df = pd.DataFrame({"d": ck.day, "hi": or_hi, "lo": or_lo}).dropna().drop_duplicates("d")
    rp = (df["hi"] - df["lo"]) / df["lo"]
    med = rp.shift(1).rolling(NARROW_LOOKBACK, min_periods=15).median()
    narrow = pd.Series(((rp > med) if wide else (rp < med)).values, index=df["d"].values)
    return pd.Series(ck.day).map(narrow).fillna(False).values.astype(bool)


# ----------------------------------------------------------------------------- signal builders
def breakout_signals(bars, ck: Clock, level_hi, level_lo, window: np.ndarray):
    """First 5-min close outside [level_lo, level_hi] within `window` per day -> entries/side."""
    cl = bars["close"].values
    up = window & np.isfinite(level_hi) & (cl > level_hi)
    dn = window & np.isfinite(level_lo) & (cl < level_lo)
    first = first_in_day(up | dn, ck.day)
    side = np.where(up, 1, np.where(dn, -1, 0)) * first
    return first, side, up & first, dn & first


def failed_break_signals(bars, ck: Clock, level_hi, level_lo, window: np.ndarray, ref_range: np.ndarray):
    """Break events: a close outside the level whose previous close was inside (within `window`).  If one of
    the next FADE_K closes is back inside (same day), fire a fade signal on that bar with the stop at the
    excursion extreme +/- FADE_BUFFER x ref_range."""
    n = len(bars)
    cl, hi, lo = bars["close"].values, bars["high"].values, bars["low"].values
    prev_cl = shift(cl, 1, np.nan)
    entries = np.zeros(n, dtype=bool)
    side = np.zeros(n, dtype=np.int64)
    stop_px = np.full(n, np.nan)
    n_events = {"up": 0, "dn": 0}
    for name, cross, inside, ext_fn, sgn in (
            ("up", window & np.isfinite(level_hi) & (cl > level_hi) & (prev_cl <= level_hi), lambda j: cl[j] < level_hi[j], np.maximum, -1),
            ("dn", window & np.isfinite(level_lo) & (cl < level_lo) & (prev_cl >= level_lo), lambda j: cl[j] > level_lo[j], np.minimum, 1)):
        ev = np.flatnonzero(cross)
        ev = ev[ev + FADE_K < n]
        n_events[name] = int(len(ev))
        done = np.zeros(len(ev), dtype=bool)
        ext = hi[ev].copy() if sgn < 0 else lo[ev].copy()
        for k in range(1, FADE_K + 1):
            j = ev + k
            ext = ext_fn(ext, hi[j] if sgn < 0 else lo[j])
            same_day = ck.day[j] == ck.day[ev]
            fail = ~done & same_day & inside(j)
            idx = j[fail]
            entries[idx] = True
            side[idx] = sgn
            stop_px[idx] = ext[fail] - sgn * FADE_BUFFER * ref_range[idx]
            done |= fail | ~same_day
    return entries, side, stop_px, n_events


# ----------------------------------------------------------------------------- variants
def V_orb(tz, or_start, or_end, cutoff, target_rr=None, max_hold=None, narrow=False, wide=False, label=""):
    def build(bars, ck):
        c = ck[tz]
        or_hi, or_lo = opening_range(bars, c, or_start, or_end)
        window = (c.minutes >= or_end) & (c.minutes < cutoff)
        if tz == "ct":
            window &= c.dow < 5
        if narrow:
            window &= narrow_filter(or_hi, or_lo, c)
        if wide:
            window &= narrow_filter(or_hi, or_lo, c, wide=True)
        entries, side, up, dn = breakout_signals(bars, c, or_hi, or_lo, window)
        stop_px = np.where(side > 0, or_lo, np.where(side < 0, or_hi, np.nan))
        zone = "UTC" if tz == "utc" else "CT (America/Chicago), Mon-Fri"
        rule = (label + f"5-min bars, {zone}. Opening range OR = [min low, max high] of the bars from {or_start // 60:02d}:{or_start % 60:02d} "
                f"to {or_end // 60:02d}:{or_end % 60:02d} (bar open times, exclusive end). "
                + (f"Trade only if (OR high - OR low)/OR low is below the median of that quantity over the previous {NARROW_LOOKBACK} sessions. " if narrow else "")
                + (f"Trade only if (OR high - OR low)/OR low is ABOVE the median of that quantity over the previous {NARROW_LOOKBACK} sessions. " if wide else "")
                + f"From the {or_end // 60:02d}:{or_end % 60:02d} bar until the {cutoff // 60:02d}:{cutoff % 60:02d} bar, the FIRST 5-min close above OR high -> long, "
                f"first close below OR low -> short (one trade per session, whichever happens first). Fill at the open of the next bar. "
                f"Stop = the opposite side of the OR (OR low for longs, OR high for shorts), checked on bar highs/lows. "
                + (f"Target = {target_rr:.0f} x the stop distance from the fill. " if target_rr else "No target. ")
                + (f"Time exit at the open of the bar {max_hold} bars ({max_hold * 5 // 60}h) after entry. " if max_hold else "")
                + "Forced flat at the open of the 15:10 CT bar; no entries 15:08-17:00 CT; no weekend positions.")
        return dict(entries=entries, side=side, stop_px=stop_px, target_rr=target_rr, max_hold_bars=max_hold), rule
    return build


def V_pd_break(max_hold):
    def build(bars, ck):
        c = ck["utc"]
        pdh, pdl = prev_day_levels(bars, c)
        window = np.isfinite(pdh)
        entries, side, up, dn = breakout_signals(bars, c, pdh, pdl, window)
        stop_dist = PD_STOP_FRAC * (pdh - pdl)
        rule = (f"5-min bars, UTC days. PDH/PDL = previous UTC calendar day's high/low. The FIRST 5-min close of the day above PDH -> long, "
                f"first close below PDL -> short (one trade per UTC day). Fill at the open of the next bar. "
                f"Stop = fill price -/+ {PD_STOP_FRAC:.2f} x (PDH - PDL), checked on bar highs/lows. No target. "
                f"Time exit at the open of the bar {max_hold} bars ({max_hold * 5 // 60}h) after entry. "
                "Forced flat at the open of the 15:10 CT bar; no entries 15:08-17:00 CT; no weekend positions.")
        return dict(entries=entries, side=side, stop_dist=stop_dist, max_hold_bars=max_hold), rule
    return build


def V_pd_fade(max_hold):
    def build(bars, ck):
        c = ck["utc"]
        pdh, pdl = prev_day_levels(bars, c)
        window = np.isfinite(pdh)
        entries, side, stop_px, n_ev = failed_break_signals(bars, c, pdh, pdl, window, pdh - pdl)
        rule = (f"5-min bars, UTC days. PDH/PDL = previous UTC calendar day's high/low. Break event: a 5-min close above PDH whose previous "
                f"close was <= PDH (resp. close below PDL, previous close >= PDL). If any of the next {FADE_K} closes (same UTC day) is back "
                f"inside (< PDH resp. > PDL), on that bar fade: short after a failed upside break, long after a failed downside break; "
                f"fill at the open of the next bar. Stop = highest high (resp. lowest low) from the break bar to the signal bar, plus "
                f"(minus) {FADE_BUFFER:.2f} x (PDH - PDL), checked on bar highs/lows. No target. Time exit at the open of the bar {max_hold} bars "
                f"({max_hold * 5 // 60}h) after entry. Forced flat at the open of the 15:10 CT bar; no entries 15:08-17:00 CT; no weekend positions. "
                "Every failed-break event is eligible, one position at a time.")
        return dict(entries=entries, side=side, stop_px=stop_px, max_hold_bars=max_hold, n_events=n_ev), rule
    return build


def V_orb_fade(or_start, or_end, cutoff):
    def build(bars, ck):
        c = ck["ct"]
        or_hi, or_lo = opening_range(bars, c, or_start, or_end)
        window = (c.minutes >= or_end) & (c.minutes < cutoff) & (c.dow < 5)
        entries, side, stop_px, n_ev = failed_break_signals(bars, c, or_hi, or_lo, window, or_hi - or_lo)
        rule = (f"5-min bars, CT (America/Chicago), Mon-Fri. OR = [min low, max high] of the bars from {or_start // 60:02d}:{or_start % 60:02d} to "
                f"{or_end // 60:02d}:{or_end % 60:02d}. Break event (from the {or_end // 60:02d}:{or_end % 60:02d} bar until the {cutoff // 60:02d}:{cutoff % 60:02d} bar): "
                f"a close above OR high whose previous close was <= OR high (resp. below OR low). If any of the next {FADE_K} closes (same day) is "
                f"back inside the OR, on that bar fade: short after a failed upside break, long after a failed downside break; fill at the open of "
                f"the next bar. Stop = highest high (lowest low) from the break bar to the signal bar plus (minus) {FADE_BUFFER:.2f} x (OR high - OR low). "
                "No target. Forced flat at the open of the 15:10 CT bar; no entries 15:08-17:00 CT. Every failed-break event is eligible, one position at a time.")
        return dict(entries=entries, side=side, stop_px=stop_px, n_events=n_ev), rule
    return build


VARIANTS = [
    # --- US-session opening-range breakout (08:30 CT = US equity open) ---
    ("BTC_us_orb30_rangestop_flat", "BTCUSDT", V_orb("ct", hhmm(8, 30), hhmm(9, 0), hhmm(13, 0))),
    ("BTC_us_orb60_rangestop_flat", "BTCUSDT", V_orb("ct", hhmm(8, 30), hhmm(9, 30), hhmm(13, 0))),
    ("BTC_us_orb60_rangestop_tgt2R", "BTCUSDT", V_orb("ct", hhmm(8, 30), hhmm(9, 30), hhmm(13, 0), target_rr=2.0)),
    ("BTC_us_orb60_narrow_rangestop_flat", "BTCUSDT", V_orb("ct", hhmm(8, 30), hhmm(9, 30), hhmm(13, 0), narrow=True)),
    ("ETH_us_orb60_rangestop_flat", "ETHUSDT", V_orb("ct", hhmm(8, 30), hhmm(9, 30), hhmm(13, 0))),
    # --- UTC-day opening-range breakout (00:00 UTC = daily candle open) ---
    ("BTC_utc_orb60_rangestop_flat", "BTCUSDT", V_orb("utc", hhmm(0), hhmm(1), hhmm(12))),
    ("BTC_utc_orb60_rangestop_4h", "BTCUSDT", V_orb("utc", hhmm(0), hhmm(1), hhmm(12), max_hold=48)),
    ("ETH_utc_orb60_rangestop_flat", "ETHUSDT", V_orb("utc", hhmm(0), hhmm(1), hhmm(12))),
    # --- previous-UTC-day high/low break, vol-scaled stop, time exit ---
    ("BTC_pdhl_break_qstop_6h", "BTCUSDT", V_pd_break(72)),
    ("ETH_pdhl_break_qstop_6h", "ETHUSDT", V_pd_break(72)),
    # --- failed-breakout fades ---
    ("BTC_pdhl_failed_fade_4h", "BTCUSDT", V_pd_fade(48)),
    ("ETH_pdhl_failed_fade_4h", "ETHUSDT", V_pd_fade(48)),
    ("BTC_us_orb60_failed_fade_flat", "BTCUSDT", V_orb_fade(hhmm(8, 30), hhmm(9, 30), hhmm(14, 30))),
]

# POST-HOC follow-ups (added after the 13 pre-specified variants and the diagnostics were seen; logged and
# counted in the deflation like every other variant).  The diagnostics showed raw continuation after the
# first US-session ORB break in BTC (+17bp at 4h, t ~ 3.3 on ~1000 events) that the traded versions did not
# convert into a net edge (ORB30: +$2.46/trade, t 1.3), and the narrow-range filter lost.
#   14. wide-range filter (mirror of the narrow one): the continuation is a few bp, the MBT cost is a fixed
#       $3.82, so only sessions with a larger-than-usual opening range can pay for the round turn.
#   15. early-break cutoff (10:30 CT instead of 13:00): a break within the hour after the opening range is
#       driven by the opening order flow; later breaks happen in thinner midday trade.
VARIANTS += [
    ("BTC_us_orb30_wide_rangestop_flat", "BTCUSDT", V_orb("ct", hhmm(8, 30), hhmm(9, 0), hhmm(13, 0), wide=True, label="[post-hoc] ")),
    ("BTC_us_orb30_early_rangestop_flat", "BTCUSDT", V_orb("ct", hhmm(8, 30), hhmm(9, 0), hhmm(10, 30), label="[post-hoc] ")),
]


# ----------------------------------------------------------------------------- diagnostics (not variants)
def breakout_forward_returns(bars, ck: dict) -> dict:
    """Signed forward returns (bp, no costs, no hours filter) after the first break of the day for the three
    level types, at 1h / 4h / 12h: tells whether raw continuation exists at all."""
    cl, o = bars["close"].values, bars["open"].values
    n = len(bars)
    out = {}
    specs = {}
    c = ck["ct"]
    hi, lo = opening_range(bars, c, hhmm(8, 30), hhmm(9, 30))
    specs["us_orb60"] = (c, hi, lo, (c.minutes >= hhmm(9, 30)) & (c.minutes < hhmm(13)) & (c.dow < 5))
    c = ck["utc"]
    hi, lo = opening_range(bars, c, hhmm(0), hhmm(1))
    specs["utc_orb60"] = (c, hi, lo, (c.minutes >= hhmm(1)) & (c.minutes < hhmm(12)))
    pdh, pdl = prev_day_levels(bars, c)
    specs["pdhl"] = (c, pdh, pdl, np.isfinite(pdh))
    for name, (c, hi, lo, window) in specs.items():
        entries, side, up, dn = breakout_signals(bars, c, hi, lo, window)
        idx = np.flatnonzero(entries)
        idx = idx[idx + 145 < n]
        fill = o[idx + 1]
        s = side[idx]
        d = {"n_breaks": int(len(idx)), "share_long": float((s > 0).mean()) if len(idx) else 0.0,
             "range_pct_median": float(np.nanmedian((hi[idx] - lo[idx]) / lo[idx]) * 100) if len(idx) else 0.0}
        for lab, k in (("1h", 12), ("4h", 48), ("12h", 144)):
            r = s * (cl[idx + k] / fill - 1) * 1e4
            d[f"fwd_{lab}_bp"] = float(r.mean())
            d[f"fwd_{lab}_t"] = float(r.mean() / (r.std(ddof=1) / np.sqrt(len(r)))) if len(r) > 2 else 0.0
        out[name] = d
    return out


# ----------------------------------------------------------------------------- main
def main():
    t0 = time.time()
    bars = {s: load_bars(s, "5min", root=ROOT) for s in ("BTCUSDT", "ETHUSDT")}
    clocks = {s: {"utc": Clock(b, "utc"), "ct": Clock(b, "ct")} for s, b in bars.items()}
    print(f"loaded {len(bars['BTCUSDT'])} 5-min bars per symbol in {time.time() - t0:.1f}s")
    for s in bars:
        validate_engine(bars[s], s)

    results = {"family": "range_breakout", "n_variants": len(VARIANTS), "variants": {}, "diagnostics": {}}
    for sym in bars:
        results["diagnostics"][sym] = breakout_forward_returns(bars[sym], clocks[sym])
        print(f"\n[diag] {sym} signed forward returns after the first break of the day (no costs, no hours filter):")
        for k, v in results["diagnostics"][sym].items():
            print(f"   {k:10s} n={v['n_breaks']:5d} long%={100 * v['share_long']:4.1f} range%={v['range_pct_median']:.2f} "
                  f"1h={v['fwd_1h_bp']:+.1f}bp(t{v['fwd_1h_t']:+.1f}) 4h={v['fwd_4h_bp']:+.1f}bp(t{v['fwd_4h_t']:+.1f}) "
                  f"12h={v['fwd_12h_bp']:+.1f}bp(t{v['fwd_12h_t']:+.1f})")

    print("\n{:<36s} {:>5s} {:>6s} {:>8s} {:>6s} {:>6s} {:>7s} {:>7s} {:>7s}  by_year".format(
        "variant", "n", "t/day", "mean$", "t", "win%", "avgW", "avgL", "SRtr"))
    for name, sym, builder in VARIANTS:
        b = bars[sym]
        kw, rule = builder(b, clocks[sym])
        n_events = kw.pop("n_events", None)
        tr = run_engine(b, kw.pop("entries"), kw.pop("side"), sym, **kw)
        st = P.summarize(tr, b)
        st["rule"] = rule
        st["symbol"] = sym
        st["skipped_entries"] = int(tr.attrs.get("skipped", 0))
        if n_events:
            st["n_break_events"] = n_events
        if st["n"]:
            st["reasons"] = {k: int(v) for k, v in tr["reason"].value_counts().items()}
            st["avg_hold_bars"] = float(tr["hold_bars"].mean())
            st["share_long"] = float((tr["side"] > 0).mean())
            st["by_side"] = {("long" if s > 0 else "short"): {"n": int(len(g)), "mean_net": float(g["net"].mean())}
                             for s, g in tr.groupby("side")}
            st["n_pos_years"] = int(sum(v > 0 for v in st["by_year"].values()))
            st["dsr"] = P.deflated_sharpe(st["sharpe_per_trade"], st["n"], len(VARIANTS))
            by = " ".join(f"{y}:{v:+.0f}" for y, v in st["by_year"].items())
            print(f"{name:<36s} {st['n']:5d} {st['trades_per_day']:6.2f} {st['mean_net']:8.2f} {st['t_stat']:6.2f} "
                  f"{100 * st['win_rate']:6.1f} {st['avg_win']:7.2f} {st['avg_loss']:7.2f} {st['sharpe_per_trade']:7.3f}  {by}")
            print(f"{'':36s} reasons={st['reasons']} hold={st['avg_hold_bars']:.1f} bars long%={100 * st['share_long']:.0f} "
                  f"by_side={ {k: round(v['mean_net'], 2) for k, v in st['by_side'].items()} }")
        else:
            print(f"{name:<36s}     0")
        results["variants"][name] = st

    surv = [name for name, st in results["variants"].items()
            if st["n"] >= 150 and st["mean_net"] > 0 and st["t_stat"] >= 2.5 and st.get("n_pos_years", 0) >= 3]
    results["screen_passers"] = surv
    print("\nvariants passing the numeric screen (n>=150, mean_net>0, t>=2.5, >=3 positive years):", surv or "none")

    with open(OUT_JSON, "w") as f:
        json.dump(results, f, indent=1, default=str)
    print(f"\nwrote {OUT_JSON}  ({time.time() - t0:.1f}s)")


if __name__ == "__main__":
    main()
