"""Hypothesis family: cross_asset_leadlag  (in-sample only, ROOT = data_research/IS)

Question: does one crypto lead the other at intraday horizons that a Topstep micro-futures trader could
act on (1-min to 1-h), and do BTC/ETH RELATIVE moves mean-revert intraday?

Two economic stories, each with a mirror image tested as a control:
  * lead-lag     : BTC is the deepest market; news / large flow is impounded into BTC first and ETH
                   market makers re-quote with a delay.  Test: after a large BTC move, trade ETH in the
                   same direction -- especially when ETH has NOT yet "caught up" (captured < 50% of
                   BTC's move).  Control: the reverse (ETH leading BTC) should be weaker.
  * relative MR  : idiosyncratic flow (liquidation cascades, a large order in one coin) pushes the
                   ETH/BTC ratio away from its short-run mean; relative-value desks and cross-exchange
                   arbitrageurs restore it.  Test: fade the ratio z-score / the 1-h return spread on
                   the ETH leg (and on the BTC leg).  Control: relative momentum (follow) at the
                   same horizon.

All signals use ONLY bars that have closed (bar i); protocol.backtest_signals fills at the open of bar
i+1.  Rolling scale estimates (std) use bars strictly before the decision bar (.shift(1)).  Time exits
via max_hold_bars; Topstep forced-flat / no-entry windows from protocol.

Cost-free diagnostics (logged, not variants): BTC<->ETH return cross-correlations at +-k bars on 5-min
and 1-min bars; conditional forward returns of ETH after a large BTC move with / without the "lag"
filter; and decile sorts of the ratio z-score versus the forward change of the ratio.

Engine note (same as the sibling families): protocol.forced_flat_time() flags every bar with CT time
>= 15:10, which would close evening (17:00-24:00 CT) positions on their own entry bar; the attribute
is patched during each backtest to flag only the 15:10-17:00 CT break, matching the documented rules.

Variants 1-12 were fixed before any costed result was looked at; variants 13-14 (BTC lagging an ETH move)
were added after the diagnostics showed the lag/catch-up subset as the only effect with the predicted sign,
and are counted in the deflated-Sharpe denominator.  Every variant in VARIANTS is logged in cross_asset_leadlag_results.json and counted for the deflated
Sharpe ratio.  Run:  cd /home/user/j && python3 -m research.hyp.cross_asset_leadlag
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
OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cross_asset_leadlag_results.json")

SD_WINDOW_5M = 2016        # 7 days of 5-min bars for the return-scale (std) estimate
SD_MIN_5M = 288            # at least 1 day of history before the scale is defined
SD_WINDOW_1M = 1440        # 1 day of 1-min bars for the 1-min return scale
SD_MIN_1M = 360
RATIO_WINDOW = 288         # 24h of 5-min bars for the ETH/BTC log-ratio mean / std
RATIO_MIN = 144
Z_MOVE = 2.0               # "large move" threshold in rolling-sigma units (5-min / 15-min / 1-h returns)
Z_MOVE_1M = 3.0            # 1-min returns are fatter tailed: use 3 sigma
CAPTURE_MAX = 0.5          # "lagging" = follower captured less than 50% of the leader's move
Z_RATIO_IN, Z_RATIO_OUT = 2.0, 0.5
Z_SPREAD = 2.0


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
def _zret(close: pd.Series, k: int, sd_window: int, sd_min: int):
    """k-bar close-to-close return and the same return divided by the rolling std of that k-bar return
    over the previous sd_window bars (past only)."""
    r = close / close.shift(k) - 1
    sd = r.rolling(sd_window, min_periods=sd_min).std().shift(1)
    return r, r / sd


class Features:
    """Aligned BTC / ETH bars (same open_time grid) and the cross-asset signals."""

    def __init__(self, btc: pd.DataFrame, eth: pd.DataFrame, freq: str):
        assert len(btc) == len(eth) and (btc["open_time"].values == eth["open_time"].values).all()
        self.btc, self.eth, self.freq = btc, eth, freq
        sdw, sdm = (SD_WINDOW_1M, SD_MIN_1M) if freq == "1m" else (SD_WINDOW_5M, SD_MIN_5M)
        self.rb, self.zb, self.re, self.ze = {}, {}, {}, {}
        ks = (1, 3, 5, 12) if freq == "1m" else (1, 3, 12)
        for k in ks:
            self.rb[k], self.zb[k] = _zret(btc["close"], k, sdw, sdm)
            self.re[k], self.ze[k] = _zret(eth["close"], k, sdw, sdm)
        if freq != "1m":
            # ETH/BTC log ratio z-score versus its previous 24h
            lr = np.log(eth["close"] / btc["close"])
            m = lr.rolling(RATIO_WINDOW, min_periods=RATIO_MIN).mean().shift(1)
            s = lr.rolling(RATIO_WINDOW, min_periods=RATIO_MIN).std().shift(1)
            self.ratio_z = (lr - m) / s
            # 1h return spread ETH - BTC, scaled by its rolling std
            sp = self.re[12] - self.rb[12]
            self.spread_z = sp / sp.rolling(SD_WINDOW_5M, min_periods=SD_MIN_5M).std().shift(1)

    def leader_move(self, leader: str, k: int, z: float):
        """side (+1/-1/0) from the leader's k-bar return exceeding z rolling sigmas."""
        zz = (self.zb if leader == "BTC" else self.ze)[k].values
        return np.where(zz >= z, 1, np.where(zz <= -z, -1, 0))

    def capture(self, leader: str, k: int) -> np.ndarray:
        """follower's k-bar return divided by the leader's k-bar return (1 = fully followed, <0 = moved
        against, >1 = overshot).  NaN where the leader did not move."""
        rl = (self.rb if leader == "BTC" else self.re)[k].values
        rf = (self.re if leader == "BTC" else self.rb)[k].values
        with np.errstate(divide="ignore", invalid="ignore"):
            return np.where(rl != 0, rf / rl, np.nan)


# ----------------------------------------------------------------------------- variant builders
def _no_exit(n):
    return np.zeros(n, dtype=bool)


def leadlag(leader: str, k: int, hold: int, lag_only: bool, z: float | None = None):
    """Trade the FOLLOWER in the direction of a large k-bar move of the LEADER."""
    follower = "ETH" if leader == "BTC" else "BTC"
    sym = "ETHUSDT" if follower == "ETH" else "BTCUSDT"

    def build(f: Features):
        zz = Z_MOVE_1M if f.freq == "1m" else Z_MOVE
        zz = z if z is not None else zz
        side = f.leader_move(leader, k, zz)
        if lag_only:
            cap = f.capture(leader, k)
            side = np.where(np.isfinite(cap) & (cap < CAPTURE_MAX), side, 0)
        n = len(side)
        bar = "1-min" if f.freq == "1m" else "5-min"
        mins = k if f.freq == "1m" else 5 * k
        sdw = SD_WINDOW_1M if f.freq == "1m" else SD_WINDOW_5M
        rule = (f"{bar} bars on both BTCUSDT and ETHUSDT (same clock). Leader = {leader}, traded instrument = "
                f"{'MET' if follower == 'ETH' else 'MBT'} ({sym} proxy). Signal on decision bar i: r_L = {leader} close[i]/close[i-{k}] - 1 "
                f"({mins}-min return); sd = std of r_L over the previous {sdw} bars (bars i-{sdw}..i-1); z = r_L/sd. "
                f"z >= {zz} -> LONG the follower, z <= -{zz} -> SHORT the follower. "
                + (f"Filter: follower lag only: capture = ({follower} close[i]/close[i-{k}] - 1) / r_L must be < {CAPTURE_MAX} "
                   f"(the follower has moved less than half of the leader's move, or against it). " if lag_only else "")
                + f"Entry at the open of bar i+1, one position at a time; exit at the open of the {hold}th bar after entry "
                f"({hold * (1 if f.freq == '1m' else 5)} min); Topstep forced flat at 15:10 CT / Friday 15:10 CT; no entries 15:08-17:00 CT.")
        return sym, side != 0, _no_exit(n), side, rule, dict(max_hold_bars=hold)
    return build


def ratio_fade(leg: str, hold: int):
    """Fade the 24h z-score of log(ETH/BTC) on one leg: z <= -ZIN (ETH cheap) -> long ETH / short BTC;
    z >= +ZIN (ETH rich) -> short ETH / long BTC.  Exit when |z| <= ZOUT (next open) or after `hold` bars."""
    sym = "ETHUSDT" if leg == "ETH" else "BTCUSDT"

    def build(f: Features):
        z = f.ratio_z.values
        side = np.where(z <= -Z_RATIO_IN, 1, np.where(z >= Z_RATIO_IN, -1, 0))
        if leg == "BTC":
            side = -side
        exits = np.abs(z) <= Z_RATIO_OUT
        rule = (f"5-min bars. x[i] = ln(ETHUSDT close[i] / BTCUSDT close[i]); m, s = mean and std of x over the previous {RATIO_WINDOW} bars "
                f"(i-{RATIO_WINDOW}..i-1, at least {RATIO_MIN}); z = (x[i]-m)/s. Traded instrument = {'MET' if leg == 'ETH' else 'MBT'}. "
                + (f"z <= -{Z_RATIO_IN} (ETH cheap vs BTC) -> LONG MET; z >= +{Z_RATIO_IN} -> SHORT MET. " if leg == "ETH" else
                   f"z <= -{Z_RATIO_IN} (BTC rich vs ETH) -> SHORT MBT; z >= +{Z_RATIO_IN} -> LONG MBT. ")
                + f"Entry at the open of bar i+1, one position at a time. Exit at the open of the bar after |z| <= {Z_RATIO_OUT}, "
                f"or at the open of the {hold}th bar after entry ({5 * hold} min); Topstep forced flat at 15:10 CT / Friday; no entries 15:08-17:00 CT.")
        return sym, side != 0, exits, side, rule, dict(max_hold_bars=hold)
    return build


def spread_trade(mode: str, hold: int):
    """1h return spread (ETH 1h ret - BTC 1h ret) in rolling-sigma units, traded on the ETH leg.
    fade: spread_z <= -Z -> long ETH, >= +Z -> short ETH.  follow: the opposite."""
    def build(f: Features):
        z = f.spread_z.values
        side = np.where(z <= -Z_SPREAD, 1, np.where(z >= Z_SPREAD, -1, 0))
        if mode == "follow":
            side = -side
        rule = (f"5-min bars. s[i] = (ETHUSDT close[i]/close[i-12] - 1) - (BTCUSDT close[i]/close[i-12] - 1) (1-h return spread); "
                f"sd = std of s over the previous {SD_WINDOW_5M} bars (i-{SD_WINDOW_5M}..i-1); z = s/sd. Traded instrument = MET. "
                + (f"z <= -{Z_SPREAD} (ETH lagged BTC over the hour) -> LONG MET; z >= +{Z_SPREAD} -> SHORT MET (fade). " if mode == "fade" else
                   f"z <= -{Z_SPREAD} -> SHORT MET; z >= +{Z_SPREAD} -> LONG MET (relative momentum). ")
                + f"Entry at the open of bar i+1, one position at a time; exit at the open of the {hold}th bar after entry ({5 * hold} min); "
                f"Topstep forced flat at 15:10 CT / Friday; no entries 15:08-17:00 CT.")
        return "ETHUSDT", side != 0, _no_exit(len(side)), side, rule, dict(max_hold_bars=hold)
    return build


# name, bar frequency, builder  -- fixed before any costed result was looked at
VARIANTS = [
    ("ETH_followBTC_5m_h3",     "5min", leadlag("BTC", 1, 3, lag_only=False)),
    ("ETH_followBTC_15m_h6",    "5min", leadlag("BTC", 3, 6, lag_only=False)),
    ("ETH_lagBTC_5m_h3",        "5min", leadlag("BTC", 1, 3, lag_only=True)),
    ("ETH_lagBTC_15m_h6",       "5min", leadlag("BTC", 3, 6, lag_only=True)),
    ("ETH_lagBTC_1h_h12",       "5min", leadlag("BTC", 12, 12, lag_only=True)),
    ("BTC_followETH_5m_h3",     "5min", leadlag("ETH", 1, 3, lag_only=False)),
    ("ETH_ratioZ24h_fade_h24",  "5min", ratio_fade("ETH", 24)),
    ("BTC_ratioZ24h_fade_h24",  "5min", ratio_fade("BTC", 24)),
    ("ETH_spread1h_fade_h6",    "5min", spread_trade("fade", 6)),
    ("ETH_spread1h_follow_h6",  "5min", spread_trade("follow", 6)),
    ("ETH_followBTC_1min_h5",   "1m",   leadlag("BTC", 1, 5, lag_only=False)),
    ("ETH_lagBTC_1min_h5",      "1m",   leadlag("BTC", 1, 5, lag_only=True)),
    # -- added AFTER the diagnostics (post-hoc, counted in n_variants): the only conditional effect with the
    #    "lead-lag" sign was the lag/catch-up subset, and MBT is the cheaper leg in bp, so test it on BTC too.
    ("BTC_lagETH_15m_h12",      "5min", leadlag("ETH", 3, 12, lag_only=True)),
    ("BTC_lagETH_1h_h12",       "5min", leadlag("ETH", 12, 12, lag_only=True)),
]


# ----------------------------------------------------------------------------- diagnostics (not variants)
def _corr_t(a, b):
    d = pd.DataFrame({"a": a, "b": b}).dropna()
    c = float(np.corrcoef(d.a, d.b)[0, 1])
    t = c * np.sqrt(len(d) - 2) / np.sqrt(max(1 - c * c, 1e-12))
    return c, float(t), int(len(d))


def diagnostics(f: Features) -> dict:
    """Cost-free, no-hours-filter.  (1) cross-correlation corr(rBTC[t], rETH[t+lag]) for lag in -L..L
    (positive lag & positive corr = BTC leads ETH).  (2) forward ETH return (open[i+1] -> close[i+k], bp,
    signed by the BTC move direction) after |zBTC|>=Z, with and without the lag filter.  (3) 5-min only:
    decile sort of the ratio z-score vs the forward 2h change of ln(ETH/BTC)."""
    out = {}
    rb, re = f.rb[1], f.re[1]
    L = 5 if f.freq == "1m" else 3
    xc = {}
    for lag in range(-L, L + 1):
        c, t, n = _corr_t(rb.values, re.shift(-lag).values)   # re at t+lag
        xc[str(lag)] = {"corr": c, "t": t}
    out["xcorr_rBTC_t_vs_rETH_t+lag"] = xc
    o_e, c_e = f.eth["open"].values, f.eth["close"].values
    n = len(o_e)
    zz = Z_MOVE_1M if f.freq == "1m" else Z_MOVE
    cond = {}
    for k in ((1, 3, 12) if f.freq != "1m" else (1, 3, 5)):
        side = f.leader_move("BTC", k, zz)
        cap = f.capture("BTC", k)
        for h in ((3, 12) if f.freq != "1m" else (5, 15)):
            fwd = np.full(n, np.nan)
            fwd[:n - h] = c_e[h:] / o_e[1:n - h + 1] - 1
            s = side * fwd * 1e4
            m_all = s[side != 0]
            m_lag = s[(side != 0) & np.isfinite(cap) & (cap < CAPTURE_MAX)]
            m_over = s[(side != 0) & np.isfinite(cap) & (cap >= 1.0)]
            cond[f"BTC{k}bar_move->ETH_fwd{h}bar"] = {
                "all": {"n": int(np.isfinite(m_all).sum()), "mean_bp": float(np.nanmean(m_all)),
                        "t": float(np.nanmean(m_all) / (np.nanstd(m_all) / np.sqrt(np.isfinite(m_all).sum())))},
                "lag(<50% captured)": {"n": int(np.isfinite(m_lag).sum()), "mean_bp": float(np.nanmean(m_lag)),
                                       "t": float(np.nanmean(m_lag) / (np.nanstd(m_lag) / np.sqrt(max(np.isfinite(m_lag).sum(), 2))))},
                "overshoot(>=100%)": {"n": int(np.isfinite(m_over).sum()), "mean_bp": float(np.nanmean(m_over)),
                                      "t": float(np.nanmean(m_over) / (np.nanstd(m_over) / np.sqrt(max(np.isfinite(m_over).sum(), 2))))}}
    out["conditional_fwd_ETH_after_BTC_move_bp_signed"] = cond
    if f.freq != "1m":
        lr = np.log(f.eth["close"] / f.btc["close"])
        fwd = (lr.shift(-24) - lr) * 1e4
        d = pd.DataFrame({"z": f.ratio_z, "f": fwd}).dropna()
        q = pd.qcut(d.z, 10, labels=False, duplicates="drop")
        dm = d.groupby(q).f.mean()
        c, t, nn = _corr_t(d.z.values, d.f.values)
        out["ratio_z_vs_fwd2h_ratio_change"] = {"n": nn, "corr": c, "t": t,
                                                "decile_means_bp": [float(v) for v in dm.values]}
        d2 = pd.DataFrame({"z": f.spread_z, "f": (f.re[12] - f.rb[12]).shift(-12) * 1e4}).dropna()
        c, t, nn = _corr_t(d2.z.values, d2.f.values)
        out["spread1h_z_vs_fwd1h_spread"] = {"n": nn, "corr": c, "t": t}
    return out


# ----------------------------------------------------------------------------- main
def main():
    t0 = time.time()
    feats = {}
    for freq in ("5min", "1m"):
        b = load_bars("BTCUSDT", freq, root=ROOT)
        e = load_bars("ETHUSDT", freq, root=ROOT)
        if len(b) != len(e) or not (b["open_time"].values == e["open_time"].values).all():
            common = np.intersect1d(b["open_time"].values, e["open_time"].values)
            b = b[b["open_time"].isin(common)].reset_index(drop=True)
            e = e[e["open_time"].isin(common)].reset_index(drop=True)
        feats[freq] = Features(b, e, freq)
        print(f"{freq}: {len(b)} aligned bars per symbol ({time.time() - t0:.1f}s)")

    results = {"family": "cross_asset_leadlag", "n_variants": len(VARIANTS), "variants": {}, "diagnostics": {}}
    for freq, f in feats.items():
        d = diagnostics(f)
        results["diagnostics"][freq] = d
        print(f"\n[diag {freq}] corr(rBTC[t], rETH[t+lag]):  " +
              "  ".join(f"lag{int(k):+d}:{v['corr']:+.3f}(t={v['t']:+.0f})" for k, v in d["xcorr_rBTC_t_vs_rETH_t+lag"].items()))
        for k, v in d["conditional_fwd_ETH_after_BTC_move_bp_signed"].items():
            print(f"   {k:28s} all: n={v['all']['n']:6d} {v['all']['mean_bp']:+6.2f}bp t={v['all']['t']:+5.1f} | "
                  f"lag: n={v['lag(<50% captured)']['n']:6d} {v['lag(<50% captured)']['mean_bp']:+6.2f}bp t={v['lag(<50% captured)']['t']:+5.1f} | "
                  f"overshoot: n={v['overshoot(>=100%)']['n']:6d} {v['overshoot(>=100%)']['mean_bp']:+6.2f}bp t={v['overshoot(>=100%)']['t']:+5.1f}")
        if "ratio_z_vs_fwd2h_ratio_change" in d:
            r = d["ratio_z_vs_fwd2h_ratio_change"]
            print(f"   ratio z -> fwd 2h ratio change: n={r['n']} corr={r['corr']:+.4f} t={r['t']:+.1f} deciles(bp)=" +
                  " ".join(f"{v:+.1f}" for v in r["decile_means_bp"]))
            r = d["spread1h_z_vs_fwd1h_spread"]
            print(f"   spread1h z -> fwd 1h spread: n={r['n']} corr={r['corr']:+.4f} t={r['t']:+.1f}")

    print("\n{:<26s} {:>5s} {:>6s} {:>8s} {:>7s} {:>6s} {:>6s} {:>7s} {:>7s} {:>7s}  by_year".format(
        "variant", "n", "t/day", "mean$", "gross$", "t", "win%", "avgW", "avgL", "SRtr"))
    for name, freq, builder in VARIANTS:
        f = feats[freq]
        sym, entries, exits, side, rule, kw = builder(f)
        b = f.eth if sym == "ETHUSDT" else f.btc
        t1 = time.time()
        tr = run_backtest(b, sym, entries, exits, side, **kw)
        st = P.summarize(tr, b)
        st["rule"] = rule
        st["symbol"] = sym
        st["bar"] = freq
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
            print(f"{name:<26s} {st['n']:5d} {st['trades_per_day']:6.2f} {st['mean_net']:8.2f} {st['gross_mean']:7.2f} "
                  f"{st['t_stat']:6.2f} {100 * st['win_rate']:6.1f} {st['avg_win']:7.2f} {st['avg_loss']:7.2f} "
                  f"{st['sharpe_per_trade']:7.3f}  {by}   [{time.time() - t1:.0f}s]")
        else:
            print(f"{name:<26s}     0")
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
