"""Hypothesis family: vol_regime_reversal  (in-sample only, ROOT = data_research/IS)

Large N-sigma moves over 15-60 minutes in BTC/ETH perps are frequently liquidation cascades: forced
market orders from the exchange's liquidation engine push price through thin books, and once the
cascade exhausts, price partially reverts (the classic "liquidity wick").  When instead the move is
accompanied by *new* positioning (open interest rising) it is more likely informed/news-driven flow
and should continue rather than revert.

Signal (5-minute bars, BTCUSDT / ETHUSDT perps as the MBT / MET price proxy):
    r5[i]      = ln(close[i] / close[i-1])                              (5-min log return)
    sigma5[i]  = std(r5 over the 288 bars ending at bar i-k)            (24h realised vol, >= 200 obs,
                                                                         window ends BEFORE the move)
    r_k[i]     = close[i] / close[i-k] - 1                              (k = 3 / 6 / 12 bars = 15/30/60 min)
    z[i]       = r_k[i] / (sigma5[i] * sqrt(k))
    event[i]   = |z[i]| >= THR  and  |z[i-1]| < THR                     (fresh crossing only, so one shock
                                                                         = one trade, no re-entry on the
                                                                         same move after a time exit)
Optional conditioning (all computed from bars <= i, i.e. known at the close of bar i):
    vr[i]      = sum(volume over bars i-k+1..i) / (k * mean 5-min volume over the 288 bars ending at i-k)
    dOI[i]     = OI[i] / OI[i-k] - 1, where OI[i] is the latest Binance metrics open_interest snapshot
                 with create_time <= open_time of bar i (so >= 5 min old at the decision = close of bar i;
                 metrics exist from 2022-01-01 only, so OI-conditioned variants cover 2022-2024H1)
Trade:  side = -sign(z) (reversal) or +sign(z) (continuation); enter at the open of bar i+1 (the
        engine does this); exit at the open of bar i+1+H (H bars = 30..240 min), or at the Topstep
        forced flat (15:10 CT), whichever first; one position at a time.  No stop/target except in the
        one explicitly labelled stop variant.

All thresholds (z 3/4, vr 4, dOI -0.5% / +0.3%) were fixed from the unconditional feature
distributions at events (event counts, quartiles) BEFORE any P&L was computed, and every variant that
is run is listed in VARIANTS and logged in the results JSON; the count feeds the deflated-Sharpe
correction.  Diagnostics (no-cost conditional forward returns) are informational, not variants.

Engine note: protocol.forced_flat_time() flags every bar with CT time >= 15:10, including the
17:00-24:00 CT evening session that the documented rules (and entry_mask) allow, so
protocol.backtest_signals would close an evening position on its entry bar.  As in the sibling
families the attribute is patched for the duration of each backtest to flag only the 15:10-17:00 CT
break; daytime behaviour (exit at the open of the 15:10 CT bar) is identical.

Run:  cd /home/user/j && python3 -m research.hyp.vol_regime_reversal
"""
from __future__ import annotations

import json
import os
import time

import numpy as np
import pandas as pd

from research import protocol as P
from research.data import load_bars, load_metrics

ROOT = "/home/user/j/data_research/IS"
OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vol_regime_reversal_results.json")

VOL_WINDOW = 288      # bars (24h of 5-min bars) for the realised-vol and volume baselines
VOL_MIN_OBS = 200
Z_BASE, Z_STRICT = 3.0, 4.0
VR_HI = 4.0           # volume ratio threshold ("high-volume shock")
DOI_DROP = -0.005     # OI change over the move <= -0.5%  -> liquidation-type move
DOI_BUILD = 0.003     # OI change over the move >= +0.3%  -> new positioning


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


class Features:
    """Per-bar shock features for one symbol (all values at index i use bars <= i only)."""

    def __init__(self, bars: pd.DataFrame, metrics: pd.DataFrame | None):
        self.bars = bars
        close = bars["close"]
        self.r5 = np.log(close).diff()
        self.vol5_mean = bars["volume"].rolling(VOL_WINDOW, min_periods=VOL_MIN_OBS).mean()
        self.sig5 = self.r5.rolling(VOL_WINDOW, min_periods=VOL_MIN_OBS).std()
        self.oi = None
        if metrics is not None and len(metrics):
            m = metrics[["create_time", "open_interest"]].copy()
            m["create_time"] = m["create_time"].astype("datetime64[us, UTC]")
            bb = bars[["open_time"]].copy()
            bb["open_time"] = bb["open_time"].astype("datetime64[us, UTC]")
            mm = pd.merge_asof(bb, m, left_on="open_time", right_on="create_time", direction="backward")
            self.oi = mm["open_interest"].values
        self._cache = {}

    def at(self, k: int) -> dict:
        if k in self._cache:
            return self._cache[k]
        close = self.bars["close"]
        rk = close.pct_change(k)
        sig_k = self.sig5.shift(k) * np.sqrt(k)
        z = (rk / sig_k).values
        vr = (self.bars["volume"].rolling(k).sum() / (k * self.vol5_mean.shift(k))).values
        doi = pd.Series(self.oi).pct_change(k).values if self.oi is not None else np.full(len(z), np.nan)
        d = {"rk": rk.values, "z": z, "vr": vr, "doi": doi}
        self._cache[k] = d
        return d


def fresh_events(z: np.ndarray, thr: float) -> np.ndarray:
    az = np.abs(np.nan_to_num(z, nan=0.0))
    prev = np.concatenate([[0.0], az[:-1]])
    return (az >= thr) & (prev < thr)


# ----------------------------------------------------------------------------- variant builder
def V(k: int, thr: float, mode: str, hold: int, sign_filter: int | None = None, vr_min: float | None = None,
      doi_max: float | None = None, doi_min: float | None = None, stop_pct: float | None = None):
    """mode: 'rev' (fade the move) or 'cont' (follow it).  hold: bars (5 min each)."""

    def build(bars: pd.DataFrame, F: Features):
        f = F.at(k)
        ev = fresh_events(f["z"], thr)
        if sign_filter is not None:
            ev &= np.sign(np.nan_to_num(f["z"])) == sign_filter
        if vr_min is not None:
            ev &= np.nan_to_num(f["vr"], nan=0.0) >= vr_min
        if doi_max is not None:
            ev &= np.nan_to_num(f["doi"], nan=np.inf) <= doi_max
        if doi_min is not None:
            ev &= np.nan_to_num(f["doi"], nan=-np.inf) >= doi_min
        s = np.sign(np.nan_to_num(f["z"])).astype(int)
        side = -s if mode == "rev" else s
        exits = np.zeros(len(bars), dtype=bool)
        mins = k * 5
        rule = (f"5-min bars. r5 = ln(close/prev close); sigma5 = std of r5 over the 288 bars ending {mins} min before the "
                f"decision bar (>=200 obs); r = close[i]/close[i-{k}] - 1 ({mins}-min return); z = r/(sigma5*sqrt({k})). "
                f"Event when |z| >= {thr:.0f} at bar i and |z| < {thr:.0f} at bar i-1 (fresh crossing). "
                + (f"Only {'down' if sign_filter < 0 else 'up'} moves (z {'<=' if sign_filter < 0 else '>='} {sign_filter * thr:+.0f}). " if sign_filter else "")
                + (f"Only if volume over the {mins}-min move >= {vr_min:.0f} x ({k} x mean 5-min volume over the 288 bars ending {mins} min before). " if vr_min else "")
                + (f"Only if open interest (latest Binance 5-min OI snapshot with timestamp <= bar open) changed by <= {100 * doi_max:+.1f}% over the {mins}-min move. " if doi_max is not None else "")
                + (f"Only if open interest (latest Binance 5-min OI snapshot with timestamp <= bar open) changed by >= {100 * doi_min:+.1f}% over the {mins}-min move. " if doi_min is not None else "")
                + f"Enter at the open of bar i+1, side = {'-' if mode == 'rev' else '+'}sign(z) ({'fade' if mode == 'rev' else 'follow'} the move). "
                f"Exit at the open of the bar {hold} bars ({hold * 5} min) after entry, or at the 15:10 CT Topstep flat if earlier"
                + (f"; stop {100 * stop_pct:.1f}% from entry checked on bar high/low" if stop_pct else "") + ". "
                "One position at a time; entries only when the next bar is inside Topstep hours (not 15:08-17:00 CT, no weekend).")
        kw = {"max_hold_bars": hold}
        if stop_pct:
            kw["stop_pct"] = stop_pct
        return ev, exits, side, rule, kw

    return build


VARIANTS = [
    # --- BTC, horizon ladder (reversal, z >= 3, hold ~ 2x the move window) ---
    ("BTC_15m_z3_rev_h30", "BTCUSDT", V(3, Z_BASE, "rev", 6)),
    ("BTC_30m_z3_rev_h60", "BTCUSDT", V(6, Z_BASE, "rev", 12)),
    ("BTC_60m_z3_rev_h120", "BTCUSDT", V(12, Z_BASE, "rev", 24)),
    ("BTC_30m_z3_rev_h240", "BTCUSDT", V(6, Z_BASE, "rev", 48)),
    # --- BTC, stricter shock ---
    ("BTC_30m_z4_rev_h60", "BTCUSDT", V(6, Z_STRICT, "rev", 12)),
    # --- BTC, down-moves only (long liquidation cascades: buy the flush) ---
    ("BTC_30m_z3_rev_h60_down_only", "BTCUSDT", V(6, Z_BASE, "rev", 12, sign_filter=-1)),
    # --- BTC, conditioning on volume / open interest ---
    ("BTC_30m_z3_rev_h60_hivol", "BTCUSDT", V(6, Z_BASE, "rev", 12, vr_min=VR_HI)),
    ("BTC_30m_z3_rev_h60_oi_drop", "BTCUSDT", V(6, Z_BASE, "rev", 12, doi_max=DOI_DROP)),
    ("BTC_30m_z3_cont_h60_oi_build", "BTCUSDT", V(6, Z_BASE, "cont", 12, doi_min=DOI_BUILD)),
    # --- BTC, risk-controlled version ---
    ("BTC_30m_z3_rev_h60_stop1pct", "BTCUSDT", V(6, Z_BASE, "rev", 12, stop_pct=0.01)),
    # --- ETH ---
    ("ETH_30m_z3_rev_h60", "ETHUSDT", V(6, Z_BASE, "rev", 12)),
    ("ETH_60m_z3_rev_h120", "ETHUSDT", V(12, Z_BASE, "rev", 24)),
    ("ETH_30m_z3_rev_h60_oi_drop", "ETHUSDT", V(6, Z_BASE, "rev", 12, doi_max=DOI_DROP)),
]

# POST-HOC follow-ups (added after the 13 pre-specified variants and the diagnostics were seen; logged and
# counted in the deflation like every other variant):
#   14/15. the no-cost diagnostics showed the only consistent raw effect is directional: DOWN moves partially
#          revert (BTC k=12 H12 +11bp t+2.6, ETH k=12 H12 +17bp t+3.2) while UP moves continue.  The
#          60-min down-only fade with a 60-min hold is the direct trading version of that diagnostic.
VARIANTS += [
    ("BTC_60m_z3_rev_h60_down_only", "BTCUSDT", V(12, Z_BASE, "rev", 12, sign_filter=-1)),
    ("ETH_60m_z3_rev_h60_down_only", "ETHUSDT", V(12, Z_BASE, "rev", 12, sign_filter=-1)),
]


# ----------------------------------------------------------------------------- diagnostics (not variants)
def conditional_forward(F: Features, sym: str) -> dict:
    """No-cost, no-hours-filter conditional forward returns after fresh |z|>=3 events, signed so that a
    positive number means the move REVERTED (return measured from the open of bar i+1 to the open of
    bar i+1+H).  Informational only."""
    out = {}
    bars = F.bars
    o = bars["open"].values
    tradable = P.entry_mask(bars["open_time"])  # could a Topstep trader have entered at the next bar?
    for k in (3, 6, 12):
        f = F.at(k)
        ev = fresh_events(f["z"], Z_BASE)
        s = np.sign(np.nan_to_num(f["z"]))
        idx = np.where(ev)[0]
        idx = idx[idx + 1 + 48 < len(o)]
        row = {"n_events": int(len(idx))}
        tr_ok = tradable[np.minimum(idx + 1, len(o) - 1)]
        for H in (6, 12, 24, 48):
            fwd = o[idx + 1 + H] / o[idx + 1] - 1.0
            rev = -s[idx] * fwd * 1e4  # bp, positive = reversal
            row[f"rev_bp_H{H}"] = float(rev.mean())
            row[f"t_H{H}"] = float(rev.mean() / (rev.std(ddof=1) / np.sqrt(len(rev))))
            if H == 12:
                for lab, m in (("down", s[idx] < 0), ("up", s[idx] > 0),
                               ("down_topstep_hrs", (s[idx] < 0) & tr_ok), ("down_off_hrs", (s[idx] < 0) & ~tr_ok),
                               ("vr>=4", np.nan_to_num(f["vr"][idx]) >= VR_HI), ("vr<4", np.nan_to_num(f["vr"][idx], nan=99) < VR_HI),
                               ("oi_drop", np.nan_to_num(f["doi"][idx], nan=9) <= DOI_DROP),
                               ("oi_mid", (np.nan_to_num(f["doi"][idx], nan=9) > DOI_DROP) & (np.nan_to_num(f["doi"][idx], nan=9) < DOI_BUILD)),
                               ("oi_build", np.nan_to_num(f["doi"][idx], nan=-9) >= DOI_BUILD)):
                    if m.sum() > 10:
                        r = rev[m]
                        row[f"H12_{lab}"] = {"n": int(m.sum()), "rev_bp": float(r.mean()),
                                             "t": float(r.mean() / (r.std(ddof=1) / np.sqrt(len(r))))}
        out[f"k{k}"] = row
    return out


# ----------------------------------------------------------------------------- main
def main():
    t0 = time.time()
    syms = ("BTCUSDT", "ETHUSDT")
    bars = {s: load_bars(s, "5min", root=ROOT) for s in syms}
    metrics = {s: load_metrics(s, root=ROOT) for s in syms}
    feats = {s: Features(bars[s], metrics[s]) for s in syms}
    print(f"loaded {len(bars['BTCUSDT'])} 5-min bars per symbol in {time.time() - t0:.1f}s")

    results = {"family": "vol_regime_reversal", "n_variants": len(VARIANTS), "variants": {}, "diagnostics": {}}
    for s in syms:
        d = conditional_forward(feats[s], s)
        results["diagnostics"][s] = d
        print(f"\n[diag] {s}: mean forward return after fresh |z|>=3 events, signed + = reversal, bp, no costs/hours filter")
        for k, row in d.items():
            print(f"   {k:4s} n={row['n_events']:5d}  " + "  ".join(f"H{H}:{row[f'rev_bp_H{H}']:+.1f}bp(t{row[f't_H{H}']:+.1f})" for H in (6, 12, 24, 48)))
            print("        H12 splits: " + "  ".join(f"{lab}: n={v['n']} {v['rev_bp']:+.1f}bp t{v['t']:+.1f}"
                                                   for lab, v in row.items() if lab.startswith("H12_")))

    print("\n{:<32s} {:>5s} {:>6s} {:>8s} {:>6s} {:>6s} {:>7s} {:>7s} {:>7s}  by_year".format(
        "variant", "n", "t/day", "mean$", "t", "win%", "avgW", "avgL", "SRtr"))
    for name, sym, builder in VARIANTS:
        b = bars[sym]
        entries, exits, side, rule, kw = builder(b, feats[sym])
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
            st["dsr"] = P.deflated_sharpe(st["sharpe_per_trade"], st["n"], len(VARIANTS))
            by = " ".join(f"{y}:{v:+.0f}" for y, v in st["by_year"].items())
            print(f"{name:<32s} {st['n']:5d} {st['trades_per_day']:6.2f} {st['mean_net']:8.2f} {st['t_stat']:6.2f} "
                  f"{100 * st['win_rate']:6.1f} {st['avg_win']:7.2f} {st['avg_loss']:7.2f} {st['sharpe_per_trade']:7.3f}  {by}")
        else:
            print(f"{name:<32s}     0")
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
