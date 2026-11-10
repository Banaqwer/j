"""Hypothesis family: oi_trend_long_hold  (round 2; in-sample only, ROOT = data_research/IS)

Open-interest build confirms the trend, on BTCUSDT perpetual 5-minute bars (proxy for CME MBT), with
session-long holds to the Topstep 15:08 CT flat deadline.

Economic story: a 4-hour price move that is accompanied by an unusually large INCREASE in perpetual open
interest is a move driven by new positioning (fresh longs on an up-move, fresh shorts on a down-move) rather
than by closing of old positions; new positioning tends to keep building through the US session, so the
move is ridden in its own direction until the flat deadline.  Metrics exist from 2022-01, so the in-sample
window for this family is 2022-01-01 .. 2024-06-30 (calendar years 2022, 2023, 2024H1).

Feature definitions (identical for every variant)
  * OI_t      : Binance 5-min metric `open_interest` with create_time == bar open_time t (exact match on the
                5-min grid; metric at create_time t is known after t, the signal from bar t is acted on at the
                OPEN of bar t+5min).  Rows with open_interest <= 0 (133 outage rows) are treated as missing.
  * dOI_t     : log(OI_t / OI_{t-4h}), t-4h = 48 bars earlier on the (gap-free) 5-min bar grid.
  * z(dOI)_t  : (dOI_t - mean) / std where mean and std (ddof=1) are computed over the trailing 30 days of
                5-min dOI observations STRICTLY BEFORE bar t (8640 bars; at least 6912 = 80% non-missing
                required, else no signal).
  * ret4h_t   : close_t / close_{t-4h} - 1 (48 bars earlier).
  * trigger   : z(dOI)_t >= Z_MIN and |ret4h_t| >= RET_MIN; side = sign(ret4h_t).

PRE-REGISTERED VARIANTS (fixed before any result was looked at; all three are run and reported):
  V1 oi_z2_ret1          : Z_MIN = 2.0, RET_MIN = 1.0%.  Trigger evaluated at every tradable 5-min bar of a
                           Mon-Fri CT calendar day whose open time is before 11:08 CT (00:00 .. 11:05 CT); if
                           no position is open, enter at the open of the next bar; exit at the 15:08 CT
                           deadline (one trade per day at most).
  V2 oi_z15_ret05        : V1 with Z_MIN = 1.5, RET_MIN = 0.5%.
  V3 oi_z2_ret1_evening  : V1's trigger evaluated at bars whose open time is 17:00 .. 22:55 CT on
                           Sunday-Thursday calendar days; enter at the open of the next bar; exit at the
                           15:08 CT deadline of the NEXT day (one trade per evening session at most).

Mechanics (all variants)
  * Engine: protocol.backtest_signals (unpatched, forced_flat_time fixed 2026-11-10), no stop, no target, no
    signal exits -- the only exit is the protocol's forced flat.
  * "Exit at 15:08 CT": the 5-min grid has no 15:08 bar; the exit is the protocol's forced flat at the open
    of the 15:10 CT bar (first printed price after a 15:08 market order).  No weekend positions.
  * One trade per day/session is automatic (the position is held to the deadline and entries stop before
    it) and is asserted after the run.
  * Costs: protocol.CONTRACT["BTCUSDT"] ($3.82 per round turn, 0.1 BTC per contract).
  * Stats: protocol.summarize over the bars of the metrics period (2022-01-01 .. 2024-06-30), so trades/day
    refers to that period.  Deflated Sharpe: N = 196 prior trials + 3 variants of this family = 199.
  * Survivor bar: mean_net > 0, t >= 2.5, n >= 150, and net P&L > 0 in >= 3 calendar years; this family has
    only 3 calendar years with data (2022, 2023, 2024H1), so all three must be positive.

Post-hoc diagnostics (at most 2, breakdowns of pre-registered variants' own trades, never nominated):
  D1 P&L of V2 (the broadest variant) by CT entry-hour bucket -- is the overnight part dead weight?
  D2 P&L of V2 by z(dOI) bucket at the signal bar -- does a stronger OI build help?

Run:  cd /home/user/j && python3 -m research.hyp.r2_oi_trend_long_hold
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
SYM = "BTCUSDT"
OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "r2_oi_trend_long_hold_results.json")
N_PRIOR_TRIALS = 196
LAG_BARS = 48                 # 4 hours of 5-min bars
Z_WINDOW = 30 * 288           # 30 days of 5-min observations
Z_MIN_PERIODS = int(0.8 * Z_WINDOW)


def hhmm(h: int, m: int = 0) -> int:
    return h * 60 + m


# ----------------------------------------------------------------------------- clock helpers (CT wall clock)
class Clock:
    """Per-bar CT wall-clock minutes-of-day, calendar day key and weekday, built from the naive local wall
    clock so DST changes cannot shift a bar into the wrong day."""

    def __init__(self, bars: pd.DataFrame):
        local = bars["ct"].dt.tz_localize(None)
        self.minutes = (local.dt.hour * 60 + local.dt.minute).values
        self.day = local.dt.normalize().values.astype("datetime64[D]").astype(np.int64)
        self.dow = local.dt.dayofweek.values  # Mon=0 .. Sun=6


# ----------------------------------------------------------------------------- features
def shift_arr(x: np.ndarray, k: int) -> np.ndarray:
    out = np.full_like(x, np.nan, dtype=float)
    out[k:] = x[:-k]
    return out


def build_features(bars: pd.DataFrame, metrics: pd.DataFrame) -> dict:
    """Align 5-min metrics to bar open times by exact timestamp and compute dOI, z(dOI), ret4h."""
    oi = pd.Series(metrics["open_interest"].values.astype(float), index=metrics["create_time"])
    oi = oi.where(oi > 0)                                   # outage rows (OI == 0) -> missing
    oi = oi[~oi.index.duplicated()]
    oi_al = oi.reindex(bars["open_time"]).values            # exact match on the 5-min grid, NaN where absent
    log_oi = np.log(oi_al)
    doi = log_oi - shift_arr(log_oi, LAG_BARS)
    prior = pd.Series(doi).shift(1)                          # strictly prior observations
    mu = prior.rolling(Z_WINDOW, min_periods=Z_MIN_PERIODS).mean().values
    sd = prior.rolling(Z_WINDOW, min_periods=Z_MIN_PERIODS).std(ddof=1).values
    z = (doi - mu) / sd
    close = bars["close"].values.astype(float)
    ret4h = close / shift_arr(close, LAG_BARS) - 1
    return dict(oi=oi_al, doi=doi, z=z, ret4h=ret4h,
                n_oi_matched=int(np.isfinite(oi_al).sum()), n_z_valid=int(np.isfinite(z).sum()),
                first_z=bars["open_time"].values[np.argmax(np.isfinite(z))])


# ----------------------------------------------------------------------------- variants
def make_signals(feat: dict, ck: Clock, tradable: np.ndarray, z_min: float, ret_min: float, window: np.ndarray):
    z, r = feat["z"], feat["ret4h"]
    cond = window & tradable & np.isfinite(z) & np.isfinite(r) & (z >= z_min) & (np.abs(r) >= ret_min)
    side = np.where(cond, np.sign(r), 0).astype(int)
    cond &= side != 0
    return cond, side


def V_day(z_min: float, ret_min: float, label: str):
    def build(feat, ck: Clock, tradable):
        window = (ck.dow < 5) & (ck.minutes < hhmm(11, 8))
        entries, side = make_signals(feat, ck, tradable, z_min, ret_min, window)
        rule = (f"BTCUSDT 5-min bars (proxy for CME MBT), times America/Chicago. Features at bar open time t: OI_t = Binance "
                f"5-min open_interest with create_time == t (OI<=0 treated as missing); dOI_t = ln(OI_t/OI_(t-4h)); z_t = (dOI_t - m)/s with m, s "
                f"the mean and sample std of dOI over the 8640 five-min bars strictly before t (>= 6912 non-missing required); "
                f"ret4h_t = close_t/close_(t-4h) - 1. Trigger: z_t >= {z_min:g} and |ret4h_t| >= {100 * ret_min:g}%. Evaluate the trigger on every "
                f"tradable bar of a Monday-Friday calendar day with open time 00:00 .. 11:05 CT (before 11:08 CT); if flat, enter at the OPEN of the "
                f"next 5-min bar with side = sign(ret4h_t) (long if up, short if down); at most one trade per day. No stop, no target. "
                f"Exit at the 15:08 CT deadline = the open of the 15:10 CT bar of the same day (forced flat). Cost $3.82 per round turn.")
        return dict(entries=entries, side=side, n_eligible=int(pd.Series(ck.day[window & tradable]).nunique())), rule
    return build


def V_evening(z_min: float, ret_min: float):
    def build(feat, ck: Clock, tradable):
        window = np.isin(ck.dow, [6, 0, 1, 2, 3]) & (ck.minutes >= hhmm(17, 0)) & (ck.minutes < hhmm(23, 0))
        entries, side = make_signals(feat, ck, tradable, z_min, ret_min, window)
        rule = (f"BTCUSDT 5-min bars (proxy for CME MBT), times America/Chicago. Features at bar open time t: OI_t = Binance "
                f"5-min open_interest with create_time == t (OI<=0 treated as missing); dOI_t = ln(OI_t/OI_(t-4h)); z_t = (dOI_t - m)/s with m, s "
                f"the mean and sample std of dOI over the 8640 five-min bars strictly before t (>= 6912 non-missing required); "
                f"ret4h_t = close_t/close_(t-4h) - 1. Trigger: z_t >= {z_min:g} and |ret4h_t| >= {100 * ret_min:g}%. Evaluate the trigger on every "
                f"bar with open time 17:00 .. 22:55 CT on Sunday-Thursday calendar days; if flat, enter at the OPEN of the next 5-min bar with "
                f"side = sign(ret4h_t); at most one trade per evening session. No stop, no target. Hold overnight; exit at the 15:08 CT deadline "
                f"of the NEXT calendar day = the open of that day's 15:10 CT bar (forced flat). Cost $3.82 per round turn.")
        return dict(entries=entries, side=side, n_eligible=int(pd.Series(ck.day[window & tradable]).nunique())), rule
    return build


VARIANTS = [
    ("V1_oi_z2_ret1", V_day(2.0, 0.01, "V1")),
    ("V2_oi_z15_ret05", V_day(1.5, 0.005, "V2")),
    ("V3_oi_z2_ret1_evening", V_evening(2.0, 0.01)),
]
N_FAMILY = len(VARIANTS)


# ----------------------------------------------------------------------------- post-hoc diagnostics (never nominated)
def _bucket_stats(tr: pd.DataFrame, labels: pd.Series) -> dict:
    out = {}
    for k, g in tr.groupby(labels):
        x = g["net"].values
        out[str(k)] = {"n": int(x.size), "mean_net": float(x.mean()),
                       "t": float(x.mean() / (x.std(ddof=1) / np.sqrt(x.size))) if x.size > 2 else 0.0}
    return out


def diag_by_entry_hour(tr: pd.DataFrame) -> dict:
    """[post-hoc D1] V2 trades bucketed by CT entry (fill) time."""
    local = tr["entry_time"].dt.tz_convert("America/Chicago")
    mins = local.dt.hour * 60 + local.dt.minute
    lab = pd.Series(np.where(mins < hhmm(6), "00:00-06:00", np.where(mins < hhmm(8, 30), "06:00-08:30", "08:30-11:10")), index=tr.index)
    return _bucket_stats(tr, lab)


def diag_by_z_bucket(tr: pd.DataFrame, bars: pd.DataFrame, z: np.ndarray) -> dict:
    """[post-hoc D2] V2 trades bucketed by z(dOI) at the signal bar (the bar before the fill bar)."""
    ot = bars["open_time"].values.astype("datetime64[ns]").astype(np.int64)
    et = pd.to_datetime(tr["entry_time"]).dt.tz_convert("UTC").values.astype("datetime64[ns]").astype(np.int64)
    idx = np.searchsorted(ot, et) - 1
    zz = z[idx]
    lab = pd.Series(np.where(zz < 2, "z[1.5,2)", np.where(zz < 3, "z[2,3)", "z>=3")), index=tr.index)
    return _bucket_stats(tr, lab)


# ----------------------------------------------------------------------------- main
def main():
    t0 = time.time()
    bars_all = load_bars(SYM, "5min", root=ROOT)
    metrics = load_metrics(SYM, root=ROOT)
    assert bars_all["open_time"].iloc[-1] <= P.IS_END, "holdout data leaked into the in-sample run"
    assert metrics["create_time"].iloc[-1] <= P.IS_END, "holdout metrics leaked into the in-sample run"
    m_start = metrics["create_time"].iloc[0]
    bars = bars_all[bars_all["open_time"] >= m_start].reset_index(drop=True)
    assert (bars["open_time"].diff().dropna() == pd.Timedelta("5min")).all(), "bar grid has gaps"
    ck = Clock(bars)
    tradable = P.tradable_mask(bars["open_time"])
    feat = build_features(bars, metrics)
    print(f"loaded {len(bars)} 5-min bars {bars['open_time'].iloc[0]} -> {bars['open_time'].iloc[-1]}; "
          f"metrics matched on {feat['n_oi_matched']} bars; z valid on {feat['n_z_valid']} bars from {feat['first_z']} "
          f"({time.time() - t0:.1f}s)")
    zf = feat["z"][np.isfinite(feat["z"])]
    print(f"z(dOI) distribution: mean={zf.mean():.3f} sd={zf.std():.3f} P(z>=1.5)={np.mean(zf >= 1.5):.4f} P(z>=2)={np.mean(zf >= 2):.4f}")

    results = {"family": "oi_trend_long_hold", "symbol": SYM, "n_variants": N_FAMILY, "n_prior_trials": N_PRIOR_TRIALS,
               "dsr_N": N_PRIOR_TRIALS + N_FAMILY, "period": [str(bars["open_time"].iloc[0]), str(bars["open_time"].iloc[-1])],
               "variants": {}, "post_hoc_diagnostics": {}}
    print("\n{:<24s} {:>5s} {:>6s} {:>8s} {:>6s} {:>6s} {:>7s} {:>7s} {:>7s} {:>6s}  by_year".format(
        "variant", "n", "t/day", "mean$", "t", "win%", "avgW", "avgL", "SRtr", "DSR"))
    kept = {}
    no_exit = np.zeros(len(bars), dtype=bool)
    for name, builder in VARIANTS:
        kw, rule = builder(feat, ck, tradable)
        tr = P.backtest_signals(bars, kw["entries"], no_exit, kw["side"], sym=SYM)
        kept[name] = (tr, kw)
        st = P.summarize(tr, bars)
        st["rule"] = rule
        st["symbol"] = SYM
        st["n_eligible_sessions"] = kw["n_eligible"]
        st["n_signal_bars"] = int(kw["entries"].sum())
        if st["n"]:
            # one trade per day/session: entry calendar days (CT) must be unique
            eday = tr["entry_time"].dt.tz_convert("America/Chicago").dt.tz_localize(None).dt.normalize()
            assert eday.is_unique, f"{name}: more than one trade on a day"
            assert set(tr["reason"]) == {"flat"}, f"{name}: unexpected exit reasons {set(tr['reason'])}"
            st["reasons"] = {k: int(v) for k, v in tr["reason"].value_counts().items()}
            st["avg_hold_bars"] = float(tr["hold_bars"].mean())
            st["share_long"] = float((tr["side"] > 0).mean())
            st["by_side"] = {("long" if s > 0 else "short"): {"n": int(len(g)), "mean_net": float(g["net"].mean())}
                             for s, g in tr.groupby("side")}
            st["n_pos_years"] = int(sum(v > 0 for v in st["by_year"].values()))
            st["dsr"] = P.deflated_sharpe(st["sharpe_per_trade"], st["n"], N_PRIOR_TRIALS + N_FAMILY)
            by = " ".join(f"{y}:{v:+.0f}" for y, v in st["by_year"].items())
            print(f"{name:<24s} {st['n']:5d} {st['trades_per_day']:6.2f} {st['mean_net']:8.2f} {st['t_stat']:6.2f} "
                  f"{100 * st['win_rate']:6.1f} {st['avg_win']:7.2f} {st['avg_loss']:7.2f} {st['sharpe_per_trade']:7.3f} {st['dsr']:6.3f}  {by}")
            print(f"{'':24s} eligible_sessions={st['n_eligible_sessions']} signal_bars={st['n_signal_bars']} n_by_year={st['n_by_year']} "
                  f"hold={st['avg_hold_bars']:.1f} bars long%={100 * st['share_long']:.0f} "
                  f"by_side={ {k: (v['n'], round(v['mean_net'], 2)) for k, v in st['by_side'].items()} } "
                  f"ci95=[{st['ci95_low']:.2f},{st['ci95_high']:.2f}] maxDD={st['max_drawdown']:.0f}")
        else:
            print(f"{name:<24s}     0   (signal_bars={st['n_signal_bars']})")
        results["variants"][name] = st

    tr2, _ = kept["V2_oi_z15_ret05"]
    if len(tr2):
        results["post_hoc_diagnostics"]["D1_V2_by_entry_time_CT"] = diag_by_entry_hour(tr2)
        results["post_hoc_diagnostics"]["D2_V2_by_z_bucket"] = diag_by_z_bucket(tr2, bars, feat["z"])
        print("\n[post-hoc D1] V2 net P&L by CT entry (fill) time bucket:")
        for k, v in results["post_hoc_diagnostics"]["D1_V2_by_entry_time_CT"].items():
            print(f"   {k:12s} n={v['n']:4d} mean={v['mean_net']:+7.2f} t={v['t']:+.2f}")
        print("[post-hoc D2] V2 net P&L by z(dOI) bucket at the signal bar:")
        for k, v in results["post_hoc_diagnostics"]["D2_V2_by_z_bucket"].items():
            print(f"   {k:12s} n={v['n']:4d} mean={v['mean_net']:+7.2f} t={v['t']:+.2f}")

    surv = [name for name, st in results["variants"].items()
            if st.get("n", 0) >= 150 and st["mean_net"] > 0 and st["t_stat"] >= 2.5 and st.get("n_pos_years", 0) >= 3]
    results["survivors"] = surv
    print("\nvariants passing the survivor bar (n>=150, mean_net>0, t>=2.5, >=3 positive years):", surv or "none")

    with open(OUT_JSON, "w") as f:
        json.dump(results, f, indent=1, default=str)
    print(f"\nwrote {OUT_JSON}  ({time.time() - t0:.1f}s)")


if __name__ == "__main__":
    main()
