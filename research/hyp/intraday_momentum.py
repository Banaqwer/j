"""Hypothesis family: intraday_momentum  (in-sample only, ROOT = data_research/IS)

Market intraday momentum (Gao, Han, Li, Zhou 2018, JFE): in SPY the first half-hour return of the
day predicts the last half-hour return (same sign), the second-to-last half hour does too, and the
effect is stronger when the signal is large.  Economic story: late-informed / slow-reacting traders
and end-of-day rebalancing by institutions that benchmark to the daily close.

Crypto analogues tested here (BTCUSDT / ETHUSDT perps as the MBT / MET price proxy):
  * UTC day  : 00:00-01:00 UTC "first hour"  ->  23:00-24:00 UTC "last hour".  The UTC close is the
               daily-candle close followed by every trend-following/alt-data system, and 00:00 UTC
               is the funding settlement + daily P&L mark on most venues -> end-of-day flows.
  * US session: 08:30-09:30 CT first hour  ->  14:10-15:10 CT last hour (Topstep forced flat at
               15:10 CT replaces the 15:00 CT CME equity close).
  * Overnight : the Asia/Europe return (17:00 CT previous evening -> 08:30 CT) predicts the US
               session (08:30 -> 15:10 CT) return.
Each is tested in a sign-only version (side = sign(signal)) and, where sensible, a size-conditioned
version (trade only if |signal| >= 1 trailing-30-day standard deviation of the signal, std computed
from days strictly before the decision day), plus the GHLZ half-hour window, the penultimate-hour
signal, the combined (both-signals-agree) rule, and a day-so-far version.

No look-ahead: every signal is a return that is fully known at the close of the decision bar; the
entry is flagged on the bar before the desired fill bar so protocol.backtest_signals fills at the
open of the following bar.  Exits are flagged the same way (fill at the open of the bar after the
flagged one) or come from the 15:10 CT forced flat.  No stops/targets: the hypothesis is a pure
time-window directional bet; adding stops is a separate (unlogged) degree of freedom.

Every variant that is run is listed in VARIANTS (fixed before any result was looked at) and every
one is logged in the results JSON; the count feeds the deflated-Sharpe correction.

Engine note: protocol.forced_flat_time() returns True for every bar with CT time >= 15:10, i.e. also
for the 17:00-24:00 CT evening session that the documented Topstep rules (and entry_mask) allow, so
protocol.backtest_signals would close any evening position on its own entry bar.  As in the sibling
families (session_drift, funding_signal) the module attribute is patched for the duration of each
backtest to flag only the 15:10-17:00 CT break; daytime behaviour (exit at the 15:10 CT bar open)
is identical to the unpatched engine.

Run:  cd /home/user/j && python3 -m research.hyp.intraday_momentum
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
OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "intraday_momentum_results.json")

Z_WINDOW = 30      # trailing days for the signal std (size-conditioned variants)
Z_MIN_OBS = 20     # minimum observations before a z-score is defined
Z_THRESH = 1.0     # |signal| >= Z_THRESH * trailing std


# ----------------------------------------------------------------------------- helpers
def hhmm(h: int, m: int = 0) -> int:
    return h * 60 + m


def shift_back(a: np.ndarray) -> np.ndarray:
    """out[i] = a[i+1]: a flag/side that refers to the fill bar is moved onto the decision bar."""
    out = np.zeros_like(a)
    out[:-1] = a[1:]
    return out


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


class Clock:
    """Per-bar time-of-day (minutes) and calendar date in one time zone (UTC or CT)."""

    def __init__(self, bars: pd.DataFrame, tz: str):
        t = bars["open_time"] if tz == "utc" else bars["ct"]
        self.minutes = (t.dt.hour * 60 + t.dt.minute).values
        self.date = t.dt.normalize().dt.tz_localize(None).values.astype("datetime64[D]")
        self.dow = t.dt.dayofweek.values
        self.bars = bars

    def price_at(self, tmin: int, col: str) -> pd.Series:
        """Series indexed by date: bars[col] of the bar whose time-of-day == tmin (one bar per date)."""
        m = self.minutes == tmin
        s = pd.Series(self.bars[col].values[m], index=self.date[m])
        return s[~s.index.duplicated(keep="first")]

    def window_return(self, t_open: int, t_last: int, open_day_shift: int = 0) -> pd.Series:
        """Return from the open of the `t_open` bar to the close of the `t_last` bar, keyed by the date
        of the close bar.  open_day_shift=-1 takes the open from the previous calendar day."""
        op = self.price_at(t_open, "open")
        cl = self.price_at(t_last, "close")
        if open_day_shift:
            op.index = op.index - np.timedelta64(open_day_shift, "D")   # shift -1 day -> key = next day
        r = cl / op.reindex(cl.index) - 1.0
        return r.dropna()

    def to_bars(self, s: pd.Series) -> np.ndarray:
        return s.reindex(self.date).values


def zscore(sig: pd.Series) -> pd.Series:
    """signal / trailing std of the signal over the previous Z_WINDOW days (strictly past days)."""
    sd = sig.rolling(Z_WINDOW, min_periods=Z_MIN_OBS).std().shift(1)
    return sig / sd


def build_signals(bars, clock: Clock, sig: pd.Series, entry_min: int, exit_min: int | None,
                  z_thresh: float | None = None, days: tuple | None = None):
    """entries/exits/side arrays for: at the open of the `entry_min` bar take side = sign(sig[date]);
    exit at the open of the `exit_min` bar (or rely on the 15:10 CT forced flat when None)."""
    s = clock.to_bars(sig)
    ok = np.isfinite(s) & (s != 0)
    if z_thresh is not None:
        z = clock.to_bars(zscore(sig))
        ok &= np.isfinite(z) & (np.abs(z) >= z_thresh)
    fill = (clock.minutes == entry_min) & ok
    if days is not None:
        fill &= np.isin(clock.dow, days)
    entries = shift_back(fill)
    side = shift_back(np.sign(np.nan_to_num(s)).astype(int))
    exits = np.zeros(len(bars), dtype=bool) if exit_min is None else shift_back(clock.minutes == exit_min)
    return entries, exits, side


# ----------------------------------------------------------------------------- variant builders
# each builder(bars, clocks) -> (entries, exits, side, rule_text)
def V_utc(first_open, first_last, entry, exit_, z=None, label=""):
    def build(bars, ck):
        c = ck["utc"]
        sig = c.window_return(first_open, first_last)
        e, x, s = build_signals(bars, c, sig, entry, exit_, z)
        rule = (f"UTC day. Signal r = close of the {first_last // 60:02d}:{first_last % 60:02d} UTC 5-min bar / open of the "
                f"{first_open // 60:02d}:{first_open % 60:02d} UTC bar - 1 (same UTC date). "
                + (f"Trade only if |r| >= {z:.1f} x std(r over the previous {Z_WINDOW} UTC days, excluding today). " if z else "")
                + f"Enter at the open of the {entry // 60:02d}:{entry % 60:02d} UTC bar with side = sign(r); "
                f"exit at the open of the {exit_ // 60:02d}:{exit_ % 60:02d} UTC bar (next day). {label}No stop/target. "
                f"Skipped when the window is outside Topstep hours (Friday evening).")
        return e, x, s, rule
    return build


def V_utc_combo():
    """GHLZ combined: first hour and penultimate hour agree in sign -> trade last hour with that sign."""
    def build(bars, ck):
        c = ck["utc"]
        r1 = c.window_return(hhmm(0), hhmm(0, 55))
        r2 = c.window_return(hhmm(22), hhmm(22, 55))
        both = pd.concat([r1, r2], axis=1, keys=["r1", "r2"], sort=True).dropna()
        sig = pd.Series(np.where(np.sign(both.r1) == np.sign(both.r2), np.sign(both.r1), 0.0), index=both.index)
        e, x, s = build_signals(bars, c, sig, hhmm(23), hhmm(0))
        rule = ("UTC day. r1 = 00:00-01:00 UTC return (close 00:55 bar / open 00:00 bar - 1), r2 = 22:00-23:00 UTC return. "
                "If sign(r1) == sign(r2) enter at the open of the 23:00 UTC bar with that sign, else no trade; "
                "exit at the open of the 00:00 UTC bar. No stop/target.")
        return e, x, s, rule
    return build


def V_us(first_open, first_last, entry, z=None):
    def build(bars, ck):
        c = ck["ct"]
        sig = c.window_return(first_open, first_last)
        e, x, s = build_signals(bars, c, sig, entry, None, z, days=(0, 1, 2, 3, 4))
        rule = (f"US session (America/Chicago). Signal r = close of the {first_last // 60:02d}:{first_last % 60:02d} CT 5-min bar / "
                f"open of the {first_open // 60:02d}:{first_open % 60:02d} CT bar - 1 (same CT date, Mon-Fri). "
                + (f"Trade only if |r| >= {z:.1f} x std(r over the previous {Z_WINDOW} sessions, excluding today). " if z else "")
                + f"Enter at the open of the {entry // 60:02d}:{entry % 60:02d} CT bar with side = sign(r); "
                f"exit at the open of the 15:10 CT bar (Topstep forced flat). No stop/target.")
        return e, x, s, rule
    return build


def V_overnight(z=None, exit_min=None, side_mult=1):
    def build(bars, ck):
        c = ck["ct"]
        sig = side_mult * c.window_return(hhmm(17), hhmm(8, 25), open_day_shift=-1)
        e, x, s = build_signals(bars, c, sig, hhmm(8, 30), exit_min, z, days=(0, 1, 2, 3, 4))
        rule = ("America/Chicago. Signal r = close of the 08:25 CT 5-min bar / open of the previous calendar day's 17:00 CT bar - 1 "
                "(the overnight Asia+Europe session; for Monday the Sunday 17:00 CT open). Mon-Fri. "
                + (f"Trade only if |r| >= {z:.1f} x std(r over the previous {Z_WINDOW} sessions, excluding today). " if z else "")
                + f"Enter at the open of the 08:30 CT bar with side = {'-' if side_mult < 0 else ''}sign(r); exit at the open of the "
                + (f"{exit_min // 60:02d}:{exit_min % 60:02d} CT bar" if exit_min else "15:10 CT bar (Topstep forced flat)")
                + ". No stop/target.")
        return e, x, s, rule
    return build


VARIANTS = [
    # --- BTC, UTC day ---
    ("BTC_utc_h1_last1h_sign", "BTCUSDT", V_utc(hhmm(0), hhmm(0, 55), hhmm(23), hhmm(0))),
    ("BTC_utc_h1_last1h_z1", "BTCUSDT", V_utc(hhmm(0), hhmm(0, 55), hhmm(23), hhmm(0), z=Z_THRESH)),
    ("BTC_utc_30m_last30m_sign", "BTCUSDT", V_utc(hhmm(0), hhmm(0, 25), hhmm(23, 30), hhmm(0))),
    ("BTC_utc_penult1h_last1h_sign", "BTCUSDT", V_utc(hhmm(22), hhmm(22, 55), hhmm(23), hhmm(0))),
    ("BTC_utc_h1_and_penult_agree", "BTCUSDT", V_utc_combo()),
    ("BTC_utc_daysofar_last1h_sign", "BTCUSDT", V_utc(hhmm(0), hhmm(22, 55), hhmm(23), hhmm(0))),
    # --- BTC, US session ---
    ("BTC_us_h1_last1h_sign", "BTCUSDT", V_us(hhmm(8, 30), hhmm(9, 25), hhmm(14, 10))),
    ("BTC_us_h1_last1h_z1", "BTCUSDT", V_us(hhmm(8, 30), hhmm(9, 25), hhmm(14, 10), z=Z_THRESH)),
    # --- BTC, overnight -> US session ---
    ("BTC_overnight_us_sign", "BTCUSDT", V_overnight()),
    ("BTC_overnight_us_z1", "BTCUSDT", V_overnight(z=Z_THRESH)),
    # --- ETH ---
    ("ETH_utc_h1_last1h_sign", "ETHUSDT", V_utc(hhmm(0), hhmm(0, 55), hhmm(23), hhmm(0))),
    ("ETH_us_h1_last1h_sign", "ETHUSDT", V_us(hhmm(8, 30), hhmm(9, 25), hhmm(14, 10))),
    ("ETH_overnight_us_sign", "ETHUSDT", V_overnight()),
]

# POST-HOC follow-ups (added after the 13 pre-specified variants and the diagnostic regressions were seen;
# they are logged and counted in the deflation like every other variant):
#   14. the day-so-far -> last-hour regression was the only strong predictive relation (t ~ 7.5 in both
#       symbols); the size-conditioned version of that rule follows the family's "sign vs size" design.
#   15. the overnight -> US regression had a significant NEGATIVE slope (reversal, not momentum); the
#       size-conditioned reversal is logged so the finding is not left as an unlogged implication.
VARIANTS += [
    ("BTC_utc_daysofar_last1h_z1", "BTCUSDT", V_utc(hhmm(0), hhmm(22, 55), hhmm(23), hhmm(0), z=Z_THRESH, label="[post-hoc] ")),
    ("BTC_overnight_us_z1_reversal", "BTCUSDT", V_overnight(z=Z_THRESH, side_mult=-1)),
]


# ----------------------------------------------------------------------------- diagnostics (not variants)
def predictive_regressions(ck: dict) -> dict:
    """OLS slope / t-stat of the target-window return on the signal-window return (all days, no costs,
    no trading-hours filter).  Informational: tells whether the raw predictive relation exists at all."""
    out = {}
    specs = {
        "utc_h1->last1h": ("utc", (hhmm(0), hhmm(0, 55), 0), (hhmm(23), hhmm(23, 55), 0)),
        "utc_penult1h->last1h": ("utc", (hhmm(22), hhmm(22, 55), 0), (hhmm(23), hhmm(23, 55), 0)),
        "utc_daysofar->last1h": ("utc", (hhmm(0), hhmm(22, 55), 0), (hhmm(23), hhmm(23, 55), 0)),
        "us_h1->last1h": ("ct", (hhmm(8, 30), hhmm(9, 25), 0), (hhmm(14, 10), hhmm(15, 5), 0)),
        "overnight->us": ("ct", (hhmm(17), hhmm(8, 25), -1), (hhmm(8, 30), hhmm(15, 5), 0)),
    }
    for name, (tz, a, b) in specs.items():
        c = ck[tz]
        x = c.window_return(a[0], a[1], a[2])
        y = c.window_return(b[0], b[1], b[2])
        d = pd.concat([x, y], axis=1, keys=["x", "y"], sort=True).dropna()
        if tz == "ct":
            d = d[pd.DatetimeIndex(d.index).dayofweek < 5]
        xx, yy = d.x.values, d.y.values
        X = np.column_stack([np.ones_like(xx), xx])
        beta, res, *_ = np.linalg.lstsq(X, yy, rcond=None)
        resid = yy - X @ beta
        s2 = resid @ resid / (len(yy) - 2)
        se = np.sqrt(s2 * np.linalg.inv(X.T @ X)[1, 1])
        sign_hit = float((np.sign(xx) == np.sign(yy)).mean())
        out[name] = {"n_days": int(len(d)), "beta": float(beta[1]), "t_beta": float(beta[1] / se),
                     "corr": float(np.corrcoef(xx, yy)[0, 1]), "sign_agreement": sign_hit,
                     "mean_y_given_sign_x_bp": float(np.mean(np.sign(xx) * yy) * 1e4)}
    return out


# ----------------------------------------------------------------------------- main
def main():
    t0 = time.time()
    bars = {s: load_bars(s, "5min", root=ROOT) for s in ("BTCUSDT", "ETHUSDT")}
    clocks = {s: {"utc": Clock(b, "utc"), "ct": Clock(b, "ct")} for s, b in bars.items()}
    print(f"loaded {len(bars['BTCUSDT'])} 5-min bars per symbol in {time.time() - t0:.1f}s")

    results = {"family": "intraday_momentum", "n_variants": len(VARIANTS), "variants": {}, "diagnostics": {}}
    for sym in bars:
        results["diagnostics"][sym] = predictive_regressions(clocks[sym])
        print(f"\n[diag] {sym} predictive regressions (no costs, no hours filter):")
        for k, v in results["diagnostics"][sym].items():
            print(f"   {k:24s} n={v['n_days']:4d} beta={v['beta']:+.4f} t={v['t_beta']:+.2f} corr={v['corr']:+.3f} "
                  f"sign-hit={v['sign_agreement']:.3f} E[y|sign x]={v['mean_y_given_sign_x_bp']:+.1f}bp")

    print("\n{:<32s} {:>5s} {:>6s} {:>8s} {:>6s} {:>6s} {:>7s} {:>7s} {:>7s}  by_year".format(
        "variant", "n", "t/day", "mean$", "t", "win%", "avgW", "avgL", "SRtr"))
    for name, sym, builder in VARIANTS:
        b = bars[sym]
        entries, exits, side, rule = builder(b, clocks[sym])
        tr = run_backtest(b, sym, entries, exits, side)
        st = P.summarize(tr, b)
        st["rule"] = rule
        st["symbol"] = sym
        if st["n"]:
            st["reasons"] = {k: int(v) for k, v in tr["reason"].value_counts().items()}
            st["avg_hold_bars"] = float(tr["hold_bars"].mean())
            st["n_pos_years"] = int(sum(v > 0 for v in st["by_year"].values()))
            st["dsr"] = P.deflated_sharpe(st["sharpe_per_trade"], st["n"], len(VARIANTS))
            by = " ".join(f"{y}:{v:+.0f}" for y, v in st["by_year"].items())
            print(f"{name:<32s} {st['n']:5d} {st['trades_per_day']:6.2f} {st['mean_net']:8.2f} {st['t_stat']:6.2f} "
                  f"{100 * st['win_rate']:6.1f} {st['avg_win']:7.2f} {st['avg_loss']:7.2f} {st['sharpe_per_trade']:7.3f}  {by}")
        else:
            print(f"{name:<32s}     0")
        results["variants"][name] = st

    # survivor screen (in-sample criteria from the protocol)
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
