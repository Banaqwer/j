"""Hypothesis family: taker_imbalance  (in-sample only, ROOT = data_research/IS)

Signal: taker-buy share of volume on Binance USDT-M perps (BTCUSDT / ETHUSDT as the MBT / MET price
proxy).  imb = 2 * taker_buy_volume / volume - 1  in [-1, +1]  (+1 = every trade was a market buy).
Aggressive (taker) flow at 5-15 minute horizons is the classic "order-flow imbalance" measure; two
competing stories:
  * continuation : informed traders cross the spread, flow predicts the next move (Kyle / OFI);
  * reversal     : a one-bar burst of market orders is liquidity demand that is absorbed by
                   limit-order traders and bounces back (inventory / overshoot / "exhaustion").
Cost-free diagnostics run first (decile sorts, logged in the results JSON) and then a fixed list of
~13 costed variants: fade vs follow, 5-min vs 15-min vs 1-h aggregation, rolling-quantile vs fixed
threshold, volume confirmation, US-hours filter, a bracket (stop/target) version, a price-divergence
("flow that did not move price") continuation version, and ETH analogues.

Decision rules: the signal is computed from the bar that just closed (bar i); the entry is flagged on
bar i and protocol.backtest_signals fills at the open of bar i+1.  Rolling thresholds use only bars
strictly before the decision bar (.shift(1)).  Time exits via max_hold_bars (exit at the open of the
k-th bar after entry); Topstep forced-flat / no-entry windows from protocol.

Engine note (same as the sibling families): protocol.forced_flat_time() flags every bar with CT time
>= 15:10, which would close evening (17:00-24:00 CT) positions on their own entry bar; the attribute
is patched during each backtest to flag only the 15:10-17:00 CT break, matching the documented rules.

Every variant in VARIANTS is logged in taker_imbalance_results.json and counted for the deflated
Sharpe ratio.  Run:  cd /home/user/j && python3 -m research.hyp.taker_imbalance
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
OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "taker_imbalance_results.json")

Q_WINDOW = 288 * 30     # 30 days of 5-min bars for the rolling quantile thresholds
Q_MIN = 288 * 7         # at least 7 days of history before a threshold is defined
Q_TAIL = 0.02           # 2% / 98% tails
VOL_WINDOW = 288        # trailing 24h median volume for the volume filter
VOL_MULT = 2.0


# ----------------------------------------------------------------------------- engine helpers
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


# ----------------------------------------------------------------------------- features
class Features:
    def __init__(self, bars: pd.DataFrame):
        self.bars = bars
        v = bars["volume"].replace(0, np.nan)
        self.imb = {1: (2 * bars["taker_buy_volume"] / v - 1)}
        for w in (3, 12):
            tb = bars["taker_buy_volume"].rolling(w).sum()
            vv = bars["volume"].rolling(w).sum().replace(0, np.nan)
            self.imb[w] = 2 * tb / vv - 1
        self.ret = {1: bars["close"] / bars["open"] - 1,
                    3: bars["close"] / bars["open"].shift(2) - 1,
                    12: bars["close"] / bars["open"].shift(11) - 1}
        self.volz = bars["volume"] / bars["volume"].rolling(VOL_WINDOW, min_periods=100).median().shift(1)
        mins = (bars["ct"].dt.hour * 60 + bars["ct"].dt.minute).values
        self.us_hours = (mins >= 8 * 60 + 30) & (mins < 15 * 60)
        self._q = {}

    def tails(self, w: int):
        """(lo, hi) rolling Q_TAIL / 1-Q_TAIL quantiles of imb[w] over the previous Q_WINDOW bars (past only)."""
        if w not in self._q:
            s = self.imb[w]
            r = s.rolling(Q_WINDOW, min_periods=Q_MIN)
            self._q[w] = (r.quantile(Q_TAIL).shift(1), r.quantile(1 - Q_TAIL).shift(1))
        return self._q[w]


def signal_arrays(f: Features, w: int, mode: str, thr: float | None = None, vol: bool = False,
                  us: bool = False, diverge: bool = False):
    """side array (+1/-1/0) per decision bar.
    mode 'fade'  : imb <= lo -> +1 (long), imb >= hi -> -1 (short)
    mode 'follow': imb <= lo -> -1,       imb >= hi -> +1
    thr          : fixed |imb| threshold instead of rolling quantiles
    vol          : require bar volume >= VOL_MULT x trailing 24h median
    us           : require decision bar in 08:30-15:00 CT
    diverge      : require sign(bar return over the signal window) opposite to (or zero vs) sign(imb)"""
    s = f.imb[w]
    if thr is None:
        lo, hi = f.tails(w)
        is_lo, is_hi = (s <= lo).values, (s >= hi).values
    else:
        is_lo, is_hi = (s <= -thr).values, (s >= thr).values
    side = np.where(is_lo, 1, np.where(is_hi, -1, 0))
    if mode == "follow":
        side = -side
    ok = np.ones(len(s), dtype=bool)
    if vol:
        ok &= (f.volz >= VOL_MULT).values
    if us:
        ok &= f.us_hours
    if diverge:
        r = f.ret[w].values
        ok &= (is_lo & (r >= 0)) | (is_hi & (r <= 0))
    side = np.where(ok, side, 0)
    entries = side != 0
    exits = np.zeros(len(s), dtype=bool)
    return entries, exits, side


# ----------------------------------------------------------------------------- variants
def V(w: int, mode: str, hold: int, thr=None, vol=False, us=False, diverge=False, stop=None, target=None):
    def build(f: Features):
        e, x, s = signal_arrays(f, w, mode, thr, vol, us, diverge)
        sig = ("imb = 2*taker_buy_volume/volume - 1 of the last 5-min bar" if w == 1 else
               f"imb = 2*sum(taker_buy_volume)/sum(volume) - 1 over the last {w} 5-min bars ({5 * w} min)")
        th = (f"|imb| >= {thr}" if thr is not None else
              f"imb <= rolling {int(Q_TAIL * 100)}th pct (long leg) or >= rolling {int(100 - Q_TAIL * 100)}th pct (short leg) of imb over the "
              f"previous {Q_WINDOW} bars (30 days), thresholds computed from bars strictly before the decision bar")
        dirn = ("FADE: extreme selling (low tail) -> LONG, extreme buying (high tail) -> SHORT" if mode == "fade"
                else "FOLLOW: extreme selling -> SHORT, extreme buying -> LONG")
        filt = []
        if vol:
            filt.append(f"bar volume >= {VOL_MULT}x median volume of the previous {VOL_WINDOW} bars")
        if us:
            filt.append("decision bar between 08:30 and 15:00 CT")
        if diverge:
            filt.append(f"the {5 * w}-min return over the signal window has the OPPOSITE sign to imb (or is zero): flow that did not move price")
        ex = (f"exit at the open of the {hold}th bar after entry ({5 * hold} min)" +
              (f", or earlier on a {100 * stop:.2f}% stop / {100 * target:.2f}% target checked on bar high/low (stop first)" if stop else "") +
              "; Topstep forced flat at 15:10 CT / Friday; no entries 15:08-17:00 CT")
        rule = (f"5-min bars. Signal: {sig}. Threshold: {th}. {dirn}. "
                + ("Filters: " + "; ".join(filt) + ". " if filt else "")
                + f"Entry at the open of the bar after the signal bar, one position at a time; {ex}.")
        return e, x, s, rule, dict(max_hold_bars=hold, stop_pct=stop, target_pct=target)
    return build


VARIANTS = [
    # name, symbol, builder  -- fixed before any costed result was looked at
    ("BTC_fade5_q2_h3",        "BTCUSDT", V(1, "fade", 3)),
    ("BTC_fade5_q2_h12",       "BTCUSDT", V(1, "fade", 12)),
    ("BTC_fade15_q2_h3",       "BTCUSDT", V(3, "fade", 3)),
    ("BTC_fade15_q2_h12",      "BTCUSDT", V(3, "fade", 12)),
    ("BTC_follow15_q2_h12",    "BTCUSDT", V(3, "follow", 12)),
    ("BTC_follow60_q2_h12",    "BTCUSDT", V(12, "follow", 12)),
    ("BTC_fade5_q2_vol2_h3",   "BTCUSDT", V(1, "fade", 3, vol=True)),
    ("BTC_fade5_q2_US_h6",     "BTCUSDT", V(1, "fade", 6, us=True)),
    ("BTC_fade5_q2_h12_brk",   "BTCUSDT", V(1, "fade", 12, stop=0.003, target=0.003)),
    ("BTC_diverge5_q2_follow_h6", "BTCUSDT", V(1, "follow", 6, diverge=True)),
    ("BTC_fade5_fix05_h3",     "BTCUSDT", V(1, "fade", 3, thr=0.5)),
    ("ETH_fade5_q2_h3",        "ETHUSDT", V(1, "fade", 3)),
    ("ETH_fade15_q2_h12",      "ETHUSDT", V(3, "fade", 12)),
]


# ----------------------------------------------------------------------------- diagnostics (not variants)
def decile_diagnostics(f: Features) -> dict:
    """Cost-free, no-hours-filter decile sort of forward returns (open of next bar -> close of bar i+k)
    on the imbalance signal.  Informational: is there a raw relation, and which sign?"""
    out = {}
    o, c = f.bars["open"].values, f.bars["close"].values
    n = len(o)
    for w in (1, 3, 12):
        s = f.imb[w]
        for k in (1, 3, 12):
            fwd = np.full(n, np.nan)
            fwd[:n - k] = c[k:] / o[1:n - k + 1] - 1
            d = pd.DataFrame({"s": s.values, "f": fwd}).dropna()
            corr = float(np.corrcoef(d.s, d.f)[0, 1])
            t = corr * np.sqrt(len(d) - 2) / np.sqrt(1 - corr ** 2)
            q = pd.qcut(d.s, 10, labels=False, duplicates="drop")
            dm = d.groupby(q).f.mean() * 1e4
            out[f"imb{5 * w}m->fwd{5 * k}m"] = {"n": int(len(d)), "corr": corr, "t": float(t),
                                               "bottom_decile_bp": float(dm.iloc[0]), "top_decile_bp": float(dm.iloc[-1])}
    return out


# ----------------------------------------------------------------------------- main
def main():
    t0 = time.time()
    bars = {s: load_bars(s, "5min", root=ROOT) for s in ("BTCUSDT", "ETHUSDT")}
    feats = {s: Features(b) for s, b in bars.items()}
    print(f"loaded {len(bars['BTCUSDT'])} 5-min bars per symbol in {time.time() - t0:.1f}s")

    results = {"family": "taker_imbalance", "n_variants": len(VARIANTS), "variants": {}, "diagnostics": {}}
    for sym in bars:
        results["diagnostics"][sym] = decile_diagnostics(feats[sym])
        print(f"\n[diag] {sym} decile sorts (no costs, no hours filter), fwd return in bp:")
        for k, v in results["diagnostics"][sym].items():
            print(f"   {k:18s} n={v['n']:6d} corr={v['corr']:+.4f} t={v['t']:+.1f} "
                  f"bottom-decile={v['bottom_decile_bp']:+.2f}bp top-decile={v['top_decile_bp']:+.2f}bp")

    print("\n{:<28s} {:>5s} {:>6s} {:>8s} {:>7s} {:>6s} {:>6s} {:>7s} {:>7s} {:>7s}  by_year".format(
        "variant", "n", "t/day", "mean$", "gross$", "t", "win%", "avgW", "avgL", "SRtr"))
    for name, sym, builder in VARIANTS:
        b = bars[sym]
        entries, exits, side, rule, kw = builder(feats[sym])
        tr = run_backtest(b, sym, entries, exits, side, **kw)
        st = P.summarize(tr, b)
        st["rule"] = rule
        st["symbol"] = sym
        st["n_signals"] = int(entries.sum())
        if st["n"]:
            st["reasons"] = {k: int(v) for k, v in tr["reason"].value_counts().items()}
            st["avg_hold_bars"] = float(tr["hold_bars"].mean())
            st["n_pos_years"] = int(sum(v > 0 for v in st["by_year"].values()))
            st["dsr"] = P.deflated_sharpe(st["sharpe_per_trade"], st["n"], len(VARIANTS))
            st["gross_mean_bp"] = float(np.mean(tr["side"] * (tr["exit"] / tr["entry"] - 1)) * 1e4)
            st["n_long"] = int((tr["side"] > 0).sum())
            st["n_short"] = int((tr["side"] < 0).sum())
            st["mean_net_long"] = float(tr.loc[tr["side"] > 0, "net"].mean()) if st["n_long"] else 0.0
            st["mean_net_short"] = float(tr.loc[tr["side"] < 0, "net"].mean()) if st["n_short"] else 0.0
            by = " ".join(f"{y}:{v:+.0f}" for y, v in st["by_year"].items())
            print(f"{name:<28s} {st['n']:5d} {st['trades_per_day']:6.2f} {st['mean_net']:8.2f} {st['gross_mean']:7.2f} "
                  f"{st['t_stat']:6.2f} {100 * st['win_rate']:6.1f} {st['avg_win']:7.2f} {st['avg_loss']:7.2f} "
                  f"{st['sharpe_per_trade']:7.3f}  {by}")
        else:
            print(f"{name:<28s}     0")
        results["variants"][name] = st

    surv = [name for name, st in results["variants"].items()
            if st["n"] >= 150 and st["mean_net"] > 0 and st["t_stat"] >= 2.5 and st.get("n_pos_years", 0) >= 3]
    results["screen_passers"] = surv
    print("\nvariants passing the numeric screen (n>=150, mean_net>0, t>=2.5, >=3 positive years):", surv or "none")

    with open(OUT_JSON, "w") as fh:
        json.dump(results, fh, indent=1, default=str)
    print(f"\nwrote {OUT_JSON}  ({time.time() - t0:.1f}s)")


if __name__ == "__main__":
    main()
