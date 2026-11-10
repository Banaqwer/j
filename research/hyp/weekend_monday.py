"""Hypothesis family: weekend_monday.

Question: the CME (and Topstep) week closes Friday afternoon CT and re-opens Sunday 17:00 CT while the
crypto spot/perp market trades through the weekend, so the Sunday re-open shows a "gap" relative to the
Friday close.  Does that gap partially reverse (CME gap-fill folklore) or continue, in a way an MBT/MET
trader can capture?  Also: does the Monday US session react to the weekend move, and is there a
systematic Friday-afternoon pre-weekend positioning effect?

The earlier `session_drift` family already ran the plain versions (fade / follow the gap, hold Sunday
17:00 -> Monday 15:10 CT, no stop/target): fade was negative (t=-1.8), follow weakly positive (t=+1.1).
This family tests the DISTINCT mechanics that the folklore actually describes:

  * gap-fill target: exit when price returns to the Friday close level F; stop one gap-width beyond entry
  * vol-normalised gap filters (gap z-score against the previous week's realised vol)
  * a Sunday-evening-only window (exit 02:00 CT, before Europe/US)
  * Monday US-session (08:30 -> 15:10 CT) reaction to the weekend move / to the Sunday-night move
  * Friday afternoon (12:00 -> 15:10 CT) directional positioning, unconditional and conditioned on the
    week-to-date move

All variants are pre-specified in VARIANTS below and every one that is run is logged (the count feeds
the deflated-Sharpe correction).  Levels:
  F = close of the Friday 15:55 CT 5-min bar (last price before the 16:00 CT CME close)
  S = close of the Sunday 16:55 CT 5-min bar (last price before the 17:00 CT CME re-open)
  g = S / F - 1  (weekend gap, known at the Sunday 16:55 close, acted on at the 17:00 open)
  z = g / (sigma5 * sqrt(588)) where sigma5 = std of the 2016 5-min log returns ending at the Friday
      15:55 CT bar (one week) and 588 = number of 5-min bars between Fri 16:00 and Sun 17:00 CT.
Signals are flagged on the bar BEFORE the desired fill bar so fills happen at the open of the desired bar
(no look-ahead).  Bar-level backtest replicates protocol.backtest_signals exactly, extended with
per-trade stop/target price levels (needed for the gap-fill target) and with the forced-flat trigger
restricted to the 15:10-17:00 CT daily break (protocol.forced_flat_time fires on every bar after 15:10
CT, which would close a 17:00 CT entry on its own bar; see session_drift.py for the same patch).

Run: cd /home/user/j && python3 -m research.hyp.weekend_monday
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
OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "weekend_monday_results.json")

SUN, MON, TUE, WED, THU, FRI, SAT = 6, 0, 1, 2, 3, 4, 5
WEEKEND_BARS = 588          # 5-min bars from Fri 16:00 CT to Sun 17:00 CT (49 h)
WEEK_BARS = 2016            # 5-min bars in 7 days


# ----------------------------------------------------------------------------- helpers
def hhmm(h: int, m: int = 0) -> int:
    return h * 60 + m


def shift_back(mask: np.ndarray) -> np.ndarray:
    """entries[i] must be True on the bar BEFORE the fill bar: out[i] = mask[i+1]."""
    out = np.zeros_like(mask, dtype=bool)
    out[:-1] = mask[1:]
    return out


def tod(bars: pd.DataFrame):
    t = bars["ct"]
    return (t.dt.hour * 60 + t.dt.minute).values, t.dt.dayofweek.values


def forced_flat_break_only(ts_utc: pd.Series) -> np.ndarray:
    """True only during the 15:10-17:00 CT daily break (positions must be flat then)."""
    t = P.ct(ts_utc)
    minutes = (t.dt.hour * 60 + t.dt.minute).values
    return (minutes >= 15 * 60 + 10) & (minutes < 17 * 60)


def backtest_levels(bars: pd.DataFrame, entries: np.ndarray, exits: np.ndarray, side: np.ndarray, sym: str,
                    stop_px: np.ndarray | None = None, target_px: np.ndarray | None = None,
                    max_hold_bars: int | None = None) -> pd.DataFrame:
    """Exact replica of protocol.backtest_signals, except (a) stop/target are per-bar PRICE arrays read on
    the signal bar (NaN = none) instead of global percentages and (b) the forced-flat trigger is the
    15:10-17:00 CT break only.  One position at a time, one contract, fills at bar opens, stop checked
    before target on each bar (conservative), cost CONTRACT[sym]['cost_rt'] per round turn."""
    c = P.CONTRACT[sym]
    ts = bars["open_time"]
    o, h, l = bars["open"].values, bars["high"].values, bars["low"].values
    can_enter = P.entry_mask(ts)
    can_hold = P.tradable_mask(ts)
    flat_now = forced_flat_break_only(ts)
    n = len(bars)
    rows = []
    i = 0
    pos = 0
    while i < n - 1:
        if pos == 0:
            if entries[i] and can_enter[i + 1] and can_hold[i + 1]:
                pos = int(side[i]) if side[i] != 0 else 1
                ei = i + 1
                ep = o[ei]
                sp = stop_px[i] if stop_px is not None and not np.isnan(stop_px[i]) else None
                tp = target_px[i] if target_px is not None and not np.isnan(target_px[i]) else None
                i = ei
                continue
            i += 1
            continue
        reason = None
        xp = None
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
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------- weekend features
def weekend_features(bars: pd.DataFrame) -> dict:
    """Per-bar arrays (NaN except on the Sunday 16:55 CT bar):
       F  = Friday 15:55 CT close (2 days earlier), S = Sunday 16:55 CT close, g = S/F-1, z = vol-normalised g.
       Also 'sun_idx' = indices of Sunday 16:55 bars, 'sun_date' = CT date of those Sundays."""
    minutes, dow = tod(bars)
    close = bars["close"].values
    n = len(bars)
    dates = bars["ct"].dt.normalize().values
    logret = np.diff(np.log(close), prepend=np.nan)
    sigma5 = pd.Series(logret).rolling(WEEK_BARS, min_periods=WEEK_BARS // 2).std().values
    fri_mask = (dow == FRI) & (minutes == hhmm(15, 55))
    sun_mask = (dow == SUN) & (minutes == hhmm(16, 55))
    fri = pd.DataFrame({"F": close[fri_mask], "sig": sigma5[fri_mask]}, index=dates[fri_mask])
    F = np.full(n, np.nan)
    g = np.full(n, np.nan)
    z = np.full(n, np.nan)
    sun_idx = np.where(sun_mask)[0]
    for i in sun_idx:
        fd = dates[i] - np.timedelta64(2, "D")
        if fd in fri.index:
            F[i] = fri.at[fd, "F"]
            g[i] = close[i] / F[i] - 1.0
            s = fri.at[fd, "sig"]
            z[i] = g[i] / (s * np.sqrt(WEEKEND_BARS)) if s and not np.isnan(s) else np.nan
    return {"F": F, "g": g, "z": z, "sun_idx": sun_idx}


def carry_forward_on_bars(values: np.ndarray, src_idx: np.ndarray, dst_mask: np.ndarray) -> np.ndarray:
    """For each bar where dst_mask is True, take the value from the most recent src bar (strictly earlier).
    Returns a per-bar array (NaN where dst_mask False or no earlier source)."""
    out = np.full(len(values), np.nan)
    dst = np.where(dst_mask)[0]
    pos = np.searchsorted(src_idx, dst, side="left") - 1
    ok = pos >= 0
    out[dst[ok]] = values[src_idx[pos[ok]]]
    return out


# ----------------------------------------------------------------------------- variant builders
# builder(bars, feats) -> (entries, exits, side, stop_px, target_px, rule_text)
def V_gapfill_fade(min_abs: float, min_z: float | None, exit_min: int | None, stop_mult: float = 1.0):
    def build(bars, ft):
        n = len(bars)
        g, z, F = ft["g"], ft["z"], ft["F"]
        ok = ~np.isnan(g) & (np.abs(g) >= min_abs)
        if min_z is not None:
            ok &= ~np.isnan(z) & (np.abs(z) >= min_z)
        side = np.where(ok, -np.sign(g), 0).astype(int)
        entries = ok & (side != 0)                       # flagged on Sunday 16:55 -> fill at 17:00 open
        S = bars["close"].values
        # target = gap fill level F; stop = one gap-width beyond the Sunday close (in the gap direction)
        target = np.where(entries, F, np.nan)
        stop = np.where(entries, S * (1 + stop_mult * g), np.nan)
        minutes, _ = tod(bars)
        exits = np.zeros(n, dtype=bool) if exit_min is None else shift_back(minutes == exit_min)
        rule = (f"Weekend gap g = S/F - 1 with F = Binance {'{sym}'} close of the Friday 15:55 CT 5-min bar and "
                f"S = close of the Sunday 16:55 CT bar. Filter: |g| >= {min_abs:.2%}"
                + (f" and |z| >= {min_z:.1f} where z = g / (sigma5 * sqrt(588)), sigma5 = std of the 2016 5-min log "
                   f"returns ending at the Friday 15:55 CT bar" if min_z is not None else "")
                + f". At the Sunday 17:00 CT bar open enter AGAINST the gap (short if g>0, long if g<0), 1 contract. "
                f"Target: limit at F (gap fill). Stop: S*(1 + {stop_mult:.1f}*g) (one gap-width beyond S, stop checked "
                f"before target on bar high/low). Time exit: "
                + (f"open of the {exit_min // 60:02d}:{exit_min % 60:02d} CT bar Monday" if exit_min else
                   "Monday 15:10 CT forced flat") + ".")
        return entries, exits, side, stop, target, rule
    return build


def V_gapfollow(min_abs: float, min_z: float | None, target_mult: float | None):
    def build(bars, ft):
        n = len(bars)
        g, z, F = ft["g"], ft["z"], ft["F"]
        ok = ~np.isnan(g) & (np.abs(g) >= min_abs)
        if min_z is not None:
            ok &= ~np.isnan(z) & (np.abs(z) >= min_z)
        side = np.where(ok, np.sign(g), 0).astype(int)
        entries = ok & (side != 0)
        S = bars["close"].values
        stop = np.where(entries, F, np.nan)              # a full gap fill falsifies the continuation idea
        target = np.where(entries, S * (1 + target_mult * g), np.nan) if target_mult else np.full(n, np.nan)
        exits = np.zeros(n, dtype=bool)
        rule = (f"Weekend gap g = S/F - 1 with F = Binance {'{sym}'} close of the Friday 15:55 CT 5-min bar and "
                f"S = close of the Sunday 16:55 CT bar. Filter: |g| >= {min_abs:.2%}"
                + (f" and |z| >= {min_z:.1f} where z = g / (sigma5 * sqrt(588)), sigma5 = std of the 2016 5-min log "
                   f"returns ending at the Friday 15:55 CT bar" if min_z is not None else "")
                + f". At the Sunday 17:00 CT bar open enter WITH the gap (long if g>0, short if g<0), 1 contract. "
                f"Stop: F (full gap fill). "
                + (f"Target: S*(1 + {target_mult:.1f}*g). " if target_mult else "No target. ")
                + "Time exit: Monday 15:10 CT forced flat.")
        return entries, exits, side, stop, target, rule
    return build


def V_monday_us(mode: str, min_abs: float = 0.0):
    """Monday 08:30 -> 15:10 CT.  mode 'gapfade': side = -sign(weekend gap g);
       mode 'overnight_follow': side = sign(Sunday 17:00 open -> Monday 08:25 close return)."""
    def build(bars, ft):
        n = len(bars)
        minutes, dow = tod(bars)
        sig_bar = (dow == MON) & (minutes == hhmm(8, 25))        # flag here -> fill at 08:30 open
        if mode == "gapfade":
            gg = carry_forward_on_bars(ft["g"], ft["sun_idx"], sig_bar)
            # only use a gap from the immediately preceding Sunday (<= 16 h earlier)
            age_ok = np.zeros(n, dtype=bool)
            dst = np.where(sig_bar)[0]
            pos = np.searchsorted(ft["sun_idx"], dst, side="left") - 1
            good = (pos >= 0) & ((dst - ft["sun_idx"][np.clip(pos, 0, None)]) <= 16 * 12)
            age_ok[dst[good]] = True
            ok = sig_bar & age_ok & ~np.isnan(gg) & (np.abs(gg) >= min_abs)
            side = np.where(ok, -np.sign(gg), 0).astype(int)
            rule = (f"Weekend gap g = S/F - 1 (F = Binance {'{sym}'} close of the Friday 15:55 CT 5-min bar, S = close of "
                    f"the Sunday 16:55 CT bar). Filter |g| >= {min_abs:.2%}. At the Monday 08:30 CT bar open enter AGAINST "
                    f"the weekend gap (short if g>0, long if g<0), 1 contract; exit at the Monday 15:10 CT forced flat. "
                    f"No stop/target.")
        else:
            sun_open_mask = (dow == SUN) & (minutes == hhmm(17, 0))
            sun_open_idx = np.where(sun_open_mask)[0]
            o = bars["open"].values
            close = bars["close"].values
            r = np.full(n, np.nan)
            dst = np.where(sig_bar)[0]
            pos = np.searchsorted(sun_open_idx, dst, side="left") - 1
            good = (pos >= 0) & ((dst - sun_open_idx[np.clip(pos, 0, None)]) <= 16 * 12)
            r[dst[good]] = close[dst[good]] / o[sun_open_idx[pos[good]]] - 1.0
            ok = sig_bar & ~np.isnan(r) & (np.abs(r) >= min_abs)
            side = np.where(ok, np.sign(r), 0).astype(int)
            rule = (f"Sunday-night return r = Monday 08:25 CT bar close / Sunday 17:00 CT bar open - 1 (Binance {'{sym}'}). "
                    f"Filter |r| >= {min_abs:.2%}. At the Monday 08:30 CT bar open enter WITH r (long if r>0, short if r<0), "
                    f"1 contract; exit at the Monday 15:10 CT forced flat. No stop/target.")
        entries = ok & (side != 0)
        exits = np.zeros(n, dtype=bool)
        return entries, exits, side, np.full(n, np.nan), np.full(n, np.nan), rule
    return build


def V_friday_pm(mode: str, entry_h: int = 12, entry_m: int = 0, min_abs: float = 0.0):
    """Friday entry_h:entry_m -> 15:10 CT.  mode 'long' / 'short' unconditional; 'weekmom' side = sign(week-to-date
       return from the Sunday 17:00 CT open to the Friday entry-1 bar close); 'weekcontra' the opposite."""
    def build(bars, ft):
        n = len(bars)
        minutes, dow = tod(bars)
        em = hhmm(entry_h, entry_m) - 5
        sig_bar = (dow == FRI) & (minutes == em)
        if mode in ("long", "short"):
            ok = sig_bar
            side = np.where(ok, 1 if mode == "long" else -1, 0).astype(int)
            rule = (f"{'Long' if mode == 'long' else 'Short'} 1 contract at the open of the Friday {entry_h:02d}:{entry_m:02d} CT "
                    f"5-min bar; exit at the Friday 15:10 CT forced flat. No stop/target. Unconditional.")
        else:
            sun_open_mask = (dow == SUN) & (minutes == hhmm(17, 0))
            sun_open_idx = np.where(sun_open_mask)[0]
            o = bars["open"].values
            close = bars["close"].values
            r = np.full(n, np.nan)
            dst = np.where(sig_bar)[0]
            pos = np.searchsorted(sun_open_idx, dst, side="left") - 1
            good = (pos >= 0) & ((dst - sun_open_idx[np.clip(pos, 0, None)]) <= 6 * 288)
            r[dst[good]] = close[dst[good]] / o[sun_open_idx[pos[good]]] - 1.0
            ok = sig_bar & ~np.isnan(r) & (np.abs(r) >= min_abs)
            sgn = 1 if mode == "weekmom" else -1
            side = np.where(ok, sgn * np.sign(r), 0).astype(int)
            rule = (f"Week-to-date return w = Friday {(em // 60):02d}:{(em % 60):02d} CT bar close / Sunday 17:00 CT bar open - 1 "
                    f"(Binance {'{sym}'}). Filter |w| >= {min_abs:.2%}. At the Friday {entry_h:02d}:{entry_m:02d} CT bar open enter "
                    f"{'WITH' if sgn > 0 else 'AGAINST'} w ({'long' if sgn > 0 else 'short'} if w>0, {'short' if sgn > 0 else 'long'} if w<0), "
                    f"1 contract; exit at the Friday 15:10 CT forced flat. No stop/target.")
        entries = ok & (side != 0)
        exits = np.zeros(n, dtype=bool)
        return entries, exits, side, np.full(n, np.nan), np.full(n, np.nan), rule
    return build


VARIANTS = [
    # --- A. Sunday 17:00 CT re-open: gap FILL (fade with target at the Friday close, stop one gap-width) ---
    ("BTC_gapfill_fade_50bp", "BTCUSDT", V_gapfill_fade(0.005, None, None)),
    ("BTC_gapfill_fade_1pct", "BTCUSDT", V_gapfill_fade(0.010, None, None)),
    ("BTC_gapfill_fade_z1", "BTCUSDT", V_gapfill_fade(0.005, 1.0, None)),
    ("BTC_gapfill_fade_evening", "BTCUSDT", V_gapfill_fade(0.005, None, hhmm(2, 0))),
    # --- A'. Sunday re-open: gap CONTINUATION (stop at the gap-fill level) ---
    ("BTC_gapfollow_1pct", "BTCUSDT", V_gapfollow(0.010, None, None)),
    ("BTC_gapfollow_z1", "BTCUSDT", V_gapfollow(0.005, 1.0, None)),
    # --- B. Monday US session reaction ---
    ("BTC_MonUS_gapfade", "BTCUSDT", V_monday_us("gapfade", 0.0)),
    ("BTC_MonUS_overnight_follow", "BTCUSDT", V_monday_us("overnight_follow", 0.0)),
    # --- C. Friday afternoon positioning ---
    ("BTC_FriPM_short", "BTCUSDT", V_friday_pm("short")),
    ("BTC_FriPM_long", "BTCUSDT", V_friday_pm("long")),
    ("BTC_FriPM_weekmom", "BTCUSDT", V_friday_pm("weekmom")),
    ("BTC_FriPM_weekcontra", "BTCUSDT", V_friday_pm("weekcontra")),
    # --- D. ETH replications of the two most economically motivated rules ---
    ("ETH_gapfill_fade_50bp", "ETHUSDT", V_gapfill_fade(0.005, None, None)),
    ("ETH_MonUS_gapfade", "ETHUSDT", V_monday_us("gapfade", 0.0)),
    ("ETH_FriPM_weekmom", "ETHUSDT", V_friday_pm("weekmom")),
]


# ----------------------------------------------------------------------------- diagnostics (informational, computed after the variants were fixed)
def gap_diagnostics(bars: pd.DataFrame, ft: dict) -> dict:
    """Gap distribution and unconditional fill statistics (does F get touched between Sun 17:00 and Mon 15:10 CT?)."""
    minutes, dow = tod(bars)
    h, l, close = bars["high"].values, bars["low"].values, bars["close"].values
    years = bars["ct"].dt.year.values
    out = {}
    rows = []
    mon_flat = (dow == MON) & (minutes == hhmm(15, 10))
    mon_flat_idx = np.where(mon_flat)[0]
    for i in ft["sun_idx"]:
        g = ft["g"][i]
        if np.isnan(g):
            continue
        j = np.searchsorted(mon_flat_idx, i, side="left")
        if j >= len(mon_flat_idx):
            continue
        k = mon_flat_idx[j]
        if k - i > 24 * 12:
            continue
        F = ft["F"][i]
        seg_h, seg_l = h[i + 1:k + 1], l[i + 1:k + 1]
        filled = bool((seg_l <= F).any()) if g > 0 else bool((seg_h >= F).any())
        # when was it filled (bars after the 17:00 open)
        if filled:
            hit = np.where(seg_l <= F)[0] if g > 0 else np.where(seg_h >= F)[0]
            t_fill = int(hit[0])
        else:
            t_fill = None
        r_mon = close[k] / close[i] - 1.0          # Sunday 16:55 close -> Monday 15:10 (approx.)
        rows.append(dict(year=int(years[i]), g=g, z=ft["z"][i], filled=filled, t_fill=t_fill, r_mon=r_mon))
    d = pd.DataFrame(rows)
    out["n_weekends"] = int(len(d))
    out["abs_gap_quantiles_pct"] = {q: round(float(np.quantile(np.abs(d["g"]), q)) * 100, 3) for q in (0.25, 0.5, 0.75, 0.9)}
    out["share_abs_gap_ge_50bp"] = float((np.abs(d["g"]) >= 0.005).mean())
    out["share_abs_gap_ge_1pct"] = float((np.abs(d["g"]) >= 0.01).mean())
    out["fill_rate_all"] = float(d["filled"].mean())
    out["fill_rate_ge_1pct"] = float(d.loc[np.abs(d["g"]) >= 0.01, "filled"].mean())
    out["fill_rate_by_year"] = d.groupby("year")["filled"].mean().round(3).to_dict()
    out["median_bars_to_fill"] = float(d.loc[d["filled"], "t_fill"].median())
    # does the subsequent Sunday->Monday return correlate with the gap?  (sign agreement, regression slope)
    out["corr_gap_vs_next"] = float(np.corrcoef(d["g"], d["r_mon"])[0, 1])
    out["sign_agreement"] = float((np.sign(d["g"]) == np.sign(d["r_mon"])).mean())
    return out


def main():
    results = []
    cache = {}
    for name, sym, build in VARIANTS:
        if sym not in cache:
            bars = load_bars(sym, "5min", root=ROOT)
            cache[sym] = {"bars": bars, "ft": weekend_features(bars)}
        bars, ft = cache[sym]["bars"], cache[sym]["ft"]
        entries, exits, side, stop_px, target_px, rule = build(bars, ft)
        rule = rule.replace("{sym}", sym)
        tr = backtest_levels(bars, entries, exits, side, sym, stop_px, target_px)
        st = P.summarize(tr, bars)
        rec = {"name": name, "symbol": sym, "rule": rule, "n": int(st.get("n", 0)), "n_signals": int(entries.sum())}
        if st.get("n", 0) > 0:
            rec.update({k: st[k] for k in ("trades_per_day", "mean_net", "t_stat", "ci95_low", "ci95_high", "win_rate",
                                           "avg_win", "avg_loss", "sharpe_per_trade", "total_net", "gross_mean",
                                           "max_drawdown")})
            rec["by_year"] = {k: round(v, 1) for k, v in st["by_year"].items()}
            rec["n_by_year"] = st["n_by_year"]
            rec["reasons"] = tr["reason"].value_counts().to_dict()
            rec["dsr"] = P.deflated_sharpe(st["sharpe_per_trade"], st["n"], len(VARIANTS))
            rec["years_positive"] = int(sum(v > 0 for v in st["by_year"].values()))
        results.append(rec)
        print(f"{name:28s} {sym:8s} n={rec['n']:4d} mean_net={rec.get('mean_net', 0):8.2f} t={rec.get('t_stat', 0):6.2f} "
              f"wr={rec.get('win_rate', 0):.3f} tpd={rec.get('trades_per_day', 0):.3f} by_year={rec.get('by_year')} "
              f"reasons={rec.get('reasons')}")
        sys.stdout.flush()

    diag = {}
    for sym in cache:
        diag[f"{sym}_gap"] = gap_diagnostics(cache[sym]["bars"], cache[sym]["ft"])
        print(f"\n{sym} weekend-gap diagnostics: {json.dumps(diag[f'{sym}_gap'], default=str)}")

    with open(OUT_JSON, "w") as fh:
        json.dump({"n_variants": len(VARIANTS), "variants": results, "diagnostics": diag}, fh, indent=1, default=str)
    print(f"\nwrote {OUT_JSON}; n_variants={len(VARIANTS)}")


if __name__ == "__main__":
    main()
