"""Hypothesis family: vwap_reversion  (in-sample only, ROOT = data_research/IS)

Economic story.  The session VWAP is the reference price of the day's institutional / algorithmic
execution: VWAP-benchmarked algos, market makers managing inventory against it, and discretionary
traders all treat a large deviation from VWAP as "rich" or "cheap".  On quiet (range-bound) days that
flow is enough to pull price back toward VWAP; on trend days (news, liquidation cascades) it is not.
We therefore test: fade a fresh k-sigma excursion from the session VWAP, target a return to VWAP,
and condition on a low realised-vol regime or on a choppy (low efficiency-ratio) session.

Signal (5-minute bars, BTCUSDT / ETHUSDT perps as the MBT / MET price proxy):
    session     = calendar day anchored at 00:00 UTC ("UTC0", the crypto-native daily VWAP) or at
                  17:00 CT ("CT17", the Topstep/CME trading day)
    tp[i]       = (high+low+close)/3
    vwap[i]     = sum_{session, <= i}(volume*tp) / sum_{session, <= i}(volume)
    sd[i]       = sqrt( sum(volume*tp^2)/sum(volume) - vwap^2 )      (volume-weighted st.dev. of tp
                                                                       around VWAP = the classic
                                                                       "VWAP standard-deviation band")
    z[i]        = (close[i] - vwap[i]) / sd[i]
    robustness band ("rvband"): sd_rv[i] = vwap[i] * rv24[i] * sqrt(nbar[i]/3), rv24 = std of 5-min
                  log returns over the 288 bars ending at i (>= 200 obs), nbar = bars since session
                  start (the expected deviation of a random-walk endpoint from its running mean)
    event[i]    = |z[i]| >= K and |z[i-1]| < K (fresh crossing, one trade per excursion)
                  and nbar[i] >= 12 (VWAP has >= 1h of data)
                  and |close[i] - vwap[i]| >= 3 x cost_rt / 0.1   (the distance to VWAP must be worth
                  at least 3 round-trip costs in contract terms: $114.6 for MBT, $27.6 for MET)
Optional filters (all known at the close of bar i):
    low-vol regime : rv24[i] / median(rv24 over the previous 30 days, ending at bar i-1) <= RV_MAX
    choppy session : ER[i] = |close[i] - session open| / sum_{session}|close - prev close| <= ER_MAX
    day session    : bar i between 08:30 and 15:00 CT (US cash hours)
Trade:  side = -sign(z) (fade), enter at the open of bar i+1 (the engine does this).
        Exit at the open of bar j+1 when, at the close of bar j, (a) price is back at VWAP
        (|z[j]| <= 0.2 or z changed sign), (b) the excursion extended to |z[j]| >= K + 1.5 (soft stop),
        or (c) bar j is the last bar of the session (the VWAP resets); else at the open of the bar
        48 bars (4h) after entry; else at the Topstep forced flat (15:10 CT).  One position at a time.
        No fixed-fraction stop/target (the reversion target is the moving VWAP level).

All thresholds (K = 2/2.5/3, exit |z| <= 0.2, soft stop at K+1.5, 12-bar warm-up, 3x-cost distance,
RV_MAX = 1.0 / 0.7, ER_MAX = 0.3, hold 48 bars) were fixed BEFORE any P&L was computed.  Every variant
that is run is listed in VARIANTS (pre-specified) or POSTHOC (added after seeing results) and logged in
the results JSON; the total count feeds the deflated-Sharpe correction.  Diagnostics (no-cost
conditional forward returns) are informational, not variants.

Soft-stop note: a VWAP-sd band inflates with the excursion itself, so |z| almost never exceeds K+1.5
(99.9th pct of |z| = 3.0); the "nostop" variant is therefore numerically identical to the base and is
counted but uninformative.

Engine note: protocol.forced_flat_time() flags every bar with CT time >= 15:10, including the
17:00-24:00 CT evening session that the documented rules (and entry_mask) allow, so
protocol.backtest_signals would close an evening position on its entry bar.  As in the sibling
families the attribute is patched for the duration of each backtest to flag only the 15:10-17:00 CT
break; daytime behaviour (exit at the open of the 15:10 CT bar) is identical.

Run:  cd /home/user/j && python3 -m research.hyp.vwap_reversion
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
OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vwap_reversion_results.json")

MIN_BARS_IN_SESSION = 12     # VWAP must have >= 1h of data before a signal is taken
Z_EXIT = 0.2                 # "back at VWAP"
Z_FAIL_EXTRA = 1.5           # soft stop when |z| >= K + 1.5
MAX_HOLD = 48                # bars (4h)
RV_WINDOW, RV_MIN_OBS = 288, 200
RV_REF_BARS, RV_REF_MIN = 288 * 30, 288 * 10
MIN_DIST_COST_MULT = 3.0     # distance to VWAP >= 3 round-trip costs (in price units: cost_rt / mult)


# ----------------------------------------------------------------------------- helpers
def forced_flat_break_only(ts_utc: pd.Series) -> np.ndarray:
    t = P.ct(ts_utc)
    minutes = (t.dt.hour * 60 + t.dt.minute).values
    return (minutes >= 15 * 60 + 10) & (minutes < 17 * 60)


def run_backtest(bars, sym, entries, exits, side, **kw):
    orig = P.forced_flat_time
    P.forced_flat_time = forced_flat_break_only
    try:
        tr = P.backtest_signals(bars, entries, exits, side, sym=sym, **kw)
    finally:
        P.forced_flat_time = orig
    return tr


def session_ids(bars: pd.DataFrame, anchor: str) -> np.ndarray:
    if anchor == "UTC0":
        return bars["open_time"].dt.floor("D").values.astype("datetime64[D]").astype(np.int64)
    if anchor == "CT17":
        naive = bars["ct"].dt.tz_localize(None) + pd.Timedelta(hours=7)   # 17:00 CT -> midnight
        return naive.dt.floor("D").values.astype("datetime64[D]").astype(np.int64)
    raise ValueError(anchor)


class Features:
    """Per-bar VWAP features for one symbol (all values at index i use bars <= i only)."""

    def __init__(self, bars: pd.DataFrame):
        self.bars = bars
        close = bars["close"]
        r5 = np.log(close).diff()
        self.rv24 = r5.rolling(RV_WINDOW, min_periods=RV_MIN_OBS).std()
        rv_ref = self.rv24.rolling(RV_REF_BARS, min_periods=RV_REF_MIN).median().shift(1)
        self.rv_ratio = (self.rv24 / rv_ref).values
        t = bars["ct"]
        self.ct_minutes = (t.dt.hour * 60 + t.dt.minute).values
        self._cache = {}

    def at(self, anchor: str) -> dict:
        if anchor in self._cache:
            return self._cache[anchor]
        b = self.bars
        sid = session_ids(b, anchor)
        g = pd.Series(np.arange(len(b))).groupby(sid)
        close = b["close"].values
        tp = (b["high"].values + b["low"].values + close) / 3.0
        vol = b["volume"].values
        key = pd.Series(sid)
        cum_v = pd.Series(vol).groupby(key).cumsum().values
        cum_pv = pd.Series(vol * tp).groupby(key).cumsum().values
        cum_pv2 = pd.Series(vol * tp * tp).groupby(key).cumsum().values
        with np.errstate(divide="ignore", invalid="ignore"):
            vwap = cum_pv / cum_v
            var = cum_pv2 / cum_v - vwap ** 2
            sd = np.sqrt(np.clip(var, 0.0, None))
            nbar = (key.groupby(key).cumcount() + 1).values
            dev = close - vwap
            z = np.where(sd > 0, dev / sd, np.nan)
            sd_rv = vwap * self.rv24.values * np.sqrt(nbar / 3.0)
            z_rv = np.where(sd_rv > 0, dev / sd_rv, np.nan)
            # session efficiency ratio (trendiness so far)
            sess_open = pd.Series(b["open"].values).groupby(key).transform("first").values
            absd = np.abs(np.diff(close, prepend=close[0]))
            first = np.r_[True, sid[1:] != sid[:-1]]
            absd[first] = np.abs(close[first] - sess_open[first])
            path = pd.Series(absd).groupby(key).cumsum().values
            er = np.where(path > 0, np.abs(close - sess_open) / path, 1.0)
        last_of_session = np.r_[sid[1:] != sid[:-1], True]
        d = {"sid": sid, "vwap": vwap, "sd": sd, "nbar": nbar, "dev": dev, "z": z, "z_rv": z_rv, "er": er,
             "last": last_of_session}
        self._cache[anchor] = d
        return d


def fresh_events(z: np.ndarray, thr: float) -> np.ndarray:
    az = np.abs(np.nan_to_num(z, nan=0.0))
    prev = np.concatenate([[0.0], az[:-1]])
    return (az >= thr) & (prev < thr)


# ----------------------------------------------------------------------------- variant builder
def V(anchor: str, K: float, rv_max: float | None = None, er_max: float | None = None, band: str = "vwapsd",
      day_only: bool = False, soft_stop: bool = True, hold: int = MAX_HOLD, min_dist_mult: float = MIN_DIST_COST_MULT,
      rv_min: float | None = None, sign_filter: int | None = None):
    def build(bars: pd.DataFrame, F: Features, sym: str):
        f = F.at(anchor)
        c = P.CONTRACT[sym]
        min_dist = min_dist_mult * c["cost_rt"] / c["mult"]
        z = f["z"] if band == "vwapsd" else f["z_rv"]
        az = np.abs(np.nan_to_num(z, nan=0.0))
        ev = fresh_events(z, K) & (f["nbar"] >= MIN_BARS_IN_SESSION) & (np.abs(f["dev"]) >= min_dist)
        if rv_max is not None:
            ev &= np.nan_to_num(F.rv_ratio, nan=np.inf) <= rv_max
        if rv_min is not None:
            ev &= np.nan_to_num(F.rv_ratio, nan=-np.inf) >= rv_min
        if er_max is not None:
            ev &= f["er"] <= er_max
        if sign_filter is not None:
            ev &= np.sign(np.nan_to_num(z, nan=0.0)) == sign_filter
        if day_only:
            ev &= (F.ct_minutes >= 8 * 60 + 30) & (F.ct_minutes < 15 * 60)
        s = np.sign(np.nan_to_num(z, nan=0.0))
        side = (-s).astype(int)
        prev_s = np.concatenate([[0.0], s[:-1]])
        reverted = (az <= Z_EXIT) | (s != prev_s)
        exits = reverted | f["last"]
        if soft_stop:
            exits |= az >= K + Z_FAIL_EXTRA
        anchor_txt = ("00:00 UTC" if anchor == "UTC0" else "17:00 CT")
        band_txt = ("sd = volume-weighted st.dev. of tp around VWAP within the session (sqrt(sum(v*tp^2)/sum(v) - vwap^2))"
                    if band == "vwapsd" else
                    "sd = vwap * rv24 * sqrt(nbar/3), rv24 = st.dev. of 5-min log close returns over the 288 bars ending at bar i (>=200 obs), nbar = bars since session start")
        rule = (f"{c['name']} ({sym} perp as proxy), 5-min bars. Session = day anchored at {anchor_txt}. tp = (high+low+close)/3; "
                f"vwap = cumulative sum(volume*tp)/sum(volume) within the session; {band_txt}; z = (close - vwap)/sd. "
                f"Signal at the close of bar i when |z[i]| >= {K} and |z[i-1]| < {K} (fresh crossing), at least {MIN_BARS_IN_SESSION} bars into the session, "
                f"and |close - vwap| >= {min_dist_mult:.0f} x round-trip cost / 0.1 = ${min_dist:.1f}"
                + (f", and rv24[i] / median(rv24 over the previous 30 days ending at bar i-1) <= {rv_max} (rv24 = st.dev. of 5-min log returns over the 288 bars ending at i)" if rv_max is not None else "")
                + (f", and rv24[i] / median(rv24 over the previous 30 days ending at bar i-1) >= {rv_min} (high-vol regime; rv24 = st.dev. of 5-min log returns over the 288 bars ending at i)" if rv_min is not None else "")
                + (f", and only {'down' if sign_filter < 0 else 'up'} excursions (z {'<=' if sign_filter < 0 else '>='} {sign_filter * K:+.1f}, i.e. {'long' if sign_filter < 0 else 'short'} trades only)" if sign_filter is not None else "")
                + (f", and session efficiency ratio |close - session open| / sum of |5-min close changes| since the session start <= {er_max}" if er_max is not None else "")
                + (", and bar i opens between 08:30 and 15:00 CT" if day_only else "")
                + f". Enter at the open of bar i+1, side = -sign(z) (long below VWAP, short above). "
                f"Exit at the open of bar j+1 when at the close of bar j: |z[j]| <= {Z_EXIT} or z changed sign (back at VWAP)"
                + (f", or |z[j]| >= {K + Z_FAIL_EXTRA} (soft stop)" if soft_stop else "")
                + f", or bar j is the last bar of the session; otherwise exit at the open of the bar {hold} bars ({hold * 5} min) after entry, or at the 15:10 CT Topstep flat if earlier. "
                "No fixed stop/target. One position at a time; entries only when the next bar is inside Topstep hours (not 15:08-17:00 CT, no weekend).")
        return ev, exits, side, rule, {"max_hold_bars": hold}

    return build


VARIANTS = [
    # --- BTC, threshold ladder (UTC-day VWAP, VWAP-sd band) ---
    ("BTC_utc0_k2.0", "BTCUSDT", V("UTC0", 2.0)),
    ("BTC_utc0_k2.5", "BTCUSDT", V("UTC0", 2.5)),
    ("BTC_utc0_k3.0", "BTCUSDT", V("UTC0", 3.0)),
    # --- BTC, session anchor robustness ---
    ("BTC_ct17_k2.5", "BTCUSDT", V("CT17", 2.5)),
    # --- BTC, low-vol regime filters (the family's core claim) ---
    ("BTC_utc0_k2.5_lowvol", "BTCUSDT", V("UTC0", 2.5, rv_max=1.0)),
    ("BTC_utc0_k2.5_lowvol_strict", "BTCUSDT", V("UTC0", 2.5, rv_max=0.7)),
    # --- BTC, choppy-session filter ---
    ("BTC_utc0_k2.5_chop", "BTCUSDT", V("UTC0", 2.5, er_max=0.3)),
    # --- BTC, band definition robustness ---
    ("BTC_utc0_k2.5_rvband", "BTCUSDT", V("UTC0", 2.5, band="rvband")),
    # --- BTC, US day session only ---
    ("BTC_utc0_k2.5_day", "BTCUSDT", V("UTC0", 2.5, day_only=True)),
    # --- BTC, no soft stop (hold to VWAP / 4h) ---
    ("BTC_utc0_k2.5_nostop", "BTCUSDT", V("UTC0", 2.5, soft_stop=False)),
    # --- ETH ---
    ("ETH_utc0_k2.0", "ETHUSDT", V("UTC0", 2.0)),
    ("ETH_utc0_k2.5", "ETHUSDT", V("UTC0", 2.5)),
    ("ETH_utc0_k2.5_lowvol", "ETHUSDT", V("UTC0", 2.5, rv_max=1.0)),
]

# POST-HOC follow-ups (added after the 13 pre-specified variants and the diagnostics were seen; logged and
# counted in the deflation like every other variant).  The diagnostics showed the family's conditioning
# is BACKWARDS in-sample: after a fresh 2.5-sd excursion, price moves toward VWAP only when the trailing
# 24h realised vol is ABOVE its 30-day median (BTC +24bp/24 bars, t+4.3) and only after DOWN excursions
# (+19bp, t+3.7); in low-vol regimes the excursion continues (-10bp, t-3.3).  The k=3 CT17-anchored
# excursions showed the largest raw recovery (19-27% of the distance).  These five variants trade those
# diagnostics directly and are data-snooped by construction.
POSTHOC: list = [
    ("PH_BTC_utc0_k2.5_hivol", "BTCUSDT", V("UTC0", 2.5, rv_min=1.0)),
    ("PH_BTC_utc0_k2.5_hivol_long", "BTCUSDT", V("UTC0", 2.5, rv_min=1.0, sign_filter=-1)),
    ("PH_BTC_ct17_k3.0", "BTCUSDT", V("CT17", 3.0)),
    ("PH_BTC_ct17_k3.0_long", "BTCUSDT", V("CT17", 3.0, sign_filter=-1)),
    ("PH_ETH_utc0_k2.5_hivol_long", "ETHUSDT", V("UTC0", 2.5, rv_min=1.0, sign_filter=-1)),
]


# ----------------------------------------------------------------------------- diagnostics (not variants)
def conditional_forward(F: Features, sym: str) -> dict:
    """No-cost, no-hours-filter forward returns after fresh |z| >= K VWAP excursions, signed so that a
    positive number means price moved TOWARD VWAP (measured from the open of bar i+1 to the open of
    bar i+1+H), plus the fraction of the entry distance recovered.  Informational only."""
    out = {}
    b = F.bars
    o = b["open"].values
    for anchor in ("UTC0", "CT17"):
        f = F.at(anchor)
        for K in (2.0, 2.5, 3.0):
            ev = fresh_events(f["z"], K) & (f["nbar"] >= MIN_BARS_IN_SESSION)
            idx = np.where(ev)[0]
            idx = idx[idx + 1 + 48 < len(o)]
            s = np.sign(np.nan_to_num(f["z"][idx]))
            dist = np.abs(f["dev"][idx])
            row = {"n_events": int(len(idx)), "median_dist_bp": float(np.median(dist / o[idx + 1]) * 1e4)}
            for H in (6, 12, 24, 48):
                fwd = o[idx + 1 + H] - o[idx + 1]
                tow = -s * fwd
                bp = tow / o[idx + 1] * 1e4
                row[f"toward_bp_H{H}"] = float(bp.mean())
                row[f"t_H{H}"] = float(bp.mean() / (bp.std(ddof=1) / np.sqrt(len(bp)))) if len(bp) > 2 else 0.0
                row[f"frac_recovered_H{H}"] = float(np.mean(tow / dist))
            if K == 2.5:
                rv = np.nan_to_num(F.rv_ratio[idx], nan=np.inf)
                er = f["er"][idx]
                H = 24
                fwd = o[idx + 1 + H] - o[idx + 1]
                bp = -s * fwd / o[idx + 1] * 1e4
                for lab, m in (("rv<=1", rv <= 1.0), ("rv>1", rv > 1.0), ("rv<=0.7", rv <= 0.7),
                               ("er<=0.3", er <= 0.3), ("er>0.3", er > 0.3), ("down_exc", s < 0), ("up_exc", s > 0)):
                    if m.sum() > 10:
                        r = bp[m]
                        row[f"H24_{lab}"] = {"n": int(m.sum()), "toward_bp": float(r.mean()),
                                             "t": float(r.mean() / (r.std(ddof=1) / np.sqrt(len(r))))}
            out[f"{anchor}_k{K}"] = row
    return out


# ----------------------------------------------------------------------------- main
def main():
    t0 = time.time()
    syms = ("BTCUSDT", "ETHUSDT")
    bars = {s: load_bars(s, "5min", root=ROOT) for s in syms}
    feats = {s: Features(bars[s]) for s in syms}
    print(f"loaded {len(bars['BTCUSDT'])} 5-min bars per symbol in {time.time() - t0:.1f}s")

    all_variants = VARIANTS + POSTHOC
    results = {"family": "vwap_reversion", "n_variants": len(all_variants), "variants": {}, "diagnostics": {}}
    for s in syms:
        d = conditional_forward(feats[s], s)
        results["diagnostics"][s] = d
        print(f"\n[diag] {s}: forward move toward VWAP after fresh |z|>=K excursions, bp, no costs/hours filter")
        for k, row in d.items():
            print(f"   {k:10s} n={row['n_events']:5d} dist={row['median_dist_bp']:5.0f}bp  "
                  + "  ".join(f"H{H}:{row[f'toward_bp_H{H}']:+.1f}bp(t{row[f't_H{H}']:+.1f},{100 * row[f'frac_recovered_H{H}']:+.0f}%)"
                              for H in (6, 12, 24, 48)))
            splits = [(lab, v) for lab, v in row.items() if lab.startswith("H24_")]
            if splits:
                print("        H24 splits: " + "  ".join(f"{lab[4:]}: n={v['n']} {v['toward_bp']:+.1f}bp t{v['t']:+.1f}" for lab, v in splits))

    print("\n{:<30s} {:>5s} {:>6s} {:>8s} {:>6s} {:>6s} {:>7s} {:>7s} {:>7s}  by_year".format(
        "variant", "n", "t/day", "mean$", "t", "win%", "avgW", "avgL", "SRtr"))
    for name, sym, builder in all_variants:
        b = bars[sym]
        entries, exits, side, rule, kw = builder(b, feats[sym], sym)
        tr = run_backtest(b, sym, entries, exits, side, **kw)
        st = P.summarize(tr, b)
        st["rule"] = rule
        st["symbol"] = sym
        st["n_signals"] = int(entries.sum())
        if st["n"]:
            st["reasons"] = {k: int(v) for k, v in tr["reason"].value_counts().items()}
            st["avg_hold_bars"] = float(tr["hold_bars"].mean())
            st["n_pos_years"] = int(sum(v > 0 for v in st["by_year"].values()))
            st["n_years"] = len(st["by_year"])
            st["dsr"] = P.deflated_sharpe(st["sharpe_per_trade"], st["n"], len(all_variants))
            st["mean_net_by_side"] = {str(k): float(v) for k, v in tr.groupby("side")["net"].mean().items()}
            st["n_by_side"] = {str(k): int(v) for k, v in tr.groupby("side")["net"].size().items()}
            by = " ".join(f"{y}:{v:+.0f}" for y, v in st["by_year"].items())
            print(f"{name:<30s} {st['n']:5d} {st['trades_per_day']:6.2f} {st['mean_net']:8.2f} {st['t_stat']:6.2f} "
                  f"{100 * st['win_rate']:6.1f} {st['avg_win']:7.2f} {st['avg_loss']:7.2f} {st['sharpe_per_trade']:7.3f}  {by}"
                  f"   exits={st['reasons']}")
        else:
            print(f"{name:<30s}     0")
        results["variants"][name] = st

    surv = []
    for name, st in results["variants"].items():
        if st["n"] >= 150 and st["mean_net"] > 0 and st["t_stat"] >= 2.5 and st.get("n_pos_years", 0) >= 3:
            surv.append(name)
    results["screen_passers"] = surv
    print("\nvariants passing the numeric screen (n>=150, mean_net>0, t>=2.5, >=3 positive years):", surv or "none")

    with open(OUT_JSON, "w") as f:
        json.dump(results, f, indent=1, default=str)
    print(f"\nwrote {OUT_JSON}  ({time.time() - t0:.1f}s)")


if __name__ == "__main__":
    main()
