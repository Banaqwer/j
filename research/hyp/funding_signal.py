"""Hypothesis family: funding_signal  (in-sample only, ROOT = data_research/IS)

Perpetual funding (settled every 8h at 00:00 / 08:00 / 16:00 UTC) prices leverage crowding.
Question: do extreme funding levels (absolute, z-score, percentile), 24h cumulative funding or a
funding *jump* predict the perp's return over the next 1-8 hours, and should one fade or follow?

Alignment / no look-ahead
  * the rate settled at calc_time T is attached to the 5-min bar whose open_time == T (bar i).
    backtest_signals acts on a bar-i signal at the open of bar i+1, i.e. T+5min -> conservative
    (in practice the rate is visible as Binance's "predicted" rate well before T).
  * rolling statistics (z, percentile) use only settlements strictly before T.
  * "pre-settlement" variants use the PREVIOUS settled rate (T-8h) as the proxy for the
    predicted rate, so nothing settled at T is used before T.

Horizon convention: holding "to the next funding" = max_hold_bars 94 (7h50m) so the position is
closed at the open of the bar 5 min before the next settlement and the next signal can be taken.
The protocol's forced flat (15:10 CT, weekend) and no-entry windows are enforced by backtest_signals.

Run:  cd /home/user/j && python3 -m research.hyp.funding_signal
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
import pandas as pd

from research import protocol as P
from research.data import load_bars, load_funding

ROOT = "/home/user/j/data_research/IS"

# ---------------------------------------------------------------------------------------------
# NOTE on protocol.backtest_signals: protocol.forced_flat_time() returns True for EVERY bar with
# CT minutes >= 15:10, i.e. for the whole 15:10 -> 24:00 CT span, not just the 15:10-17:00 break.
# Any position opened in the evening session (17:00-24:00 CT, which the documented rules allow and
# entry_mask permits) is therefore closed on its own entry bar for a pure cost loss.  The 00:00 UTC
# settlement (18:00/19:00 CT) falls in that window, so one third of this family's trades would be
# zero-duration losers.  backtest_signals_fixed below is a verbatim copy of protocol.backtest_signals
# with the flat condition reduced to `not tradable_mask` (which already covers the 15:10 CT break and
# the weekend: exit at the open of the 15:10 CT bar / Friday 15:10 bar).  Results are reported with
# the fixed engine; the as-is protocol numbers are kept in the JSON under "protocol_asis".
# ---------------------------------------------------------------------------------------------
def backtest_signals_fixed(bars, entries, exits, side, sym="BTCUSDT", stop_pct=None, target_pct=None,
                           max_hold_bars=None):
    c = P.CONTRACT[sym]
    ts = bars["open_time"]
    o, h, l = bars["open"].values, bars["high"].values, bars["low"].values
    can_enter = P.entry_mask(ts)
    can_hold = P.tradable_mask(ts)
    flat_now = ~can_hold                      # <- the only change vs protocol.backtest_signals
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
                sp = ep * (1 - stop_pct * pos) if stop_pct else None
                tp = ep * (1 + target_pct * pos) if target_pct else None
                i = ei
                continue
            i += 1
            continue
        reason = None
        xp = None
        if stop_pct is not None:
            if (pos == 1 and l[i] <= sp) or (pos == -1 and h[i] >= sp):
                xp, reason = sp, "stop"
        if xp is None and target_pct is not None:
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

OUT_JSON = "/home/user/j/results/research/funding_signal.json"

FREQ = "5min"
BARS_PER_HOUR = 12
TO_NEXT_FUNDING = 94          # 7h50m: exit the bar before the next settlement bar

# feature windows (in settlements; 3 per day)
Z_WIN = 270                   # 90 days
Z_STD_FLOOR = 1e-4            # the baseline rate itself; stops z exploding when funding is pinned at 0.01%
PCT_WIN = 540                 # 180 days


# ------------------------------------------------------------------ features
def funding_features(fund: pd.DataFrame) -> pd.DataFrame:
    f = fund.copy()
    f["calc_time"] = f["calc_time"].dt.round("1min")
    f = f.drop_duplicates("calc_time").sort_values("calc_time").reset_index(drop=True)
    r = f["rate"].astype(float)
    prev = r.shift(1)
    mu = prev.rolling(Z_WIN, min_periods=Z_WIN // 2).mean()
    sd = prev.rolling(Z_WIN, min_periods=Z_WIN // 2).std().clip(lower=Z_STD_FLOOR)
    f["z"] = (r - mu) / sd
    # percentile of current rate within the previous PCT_WIN settlements (strictly before T)
    vals = r.values
    pct = np.full(len(vals), np.nan)
    for i in range(PCT_WIN // 2, len(vals)):
        w = vals[max(0, i - PCT_WIN):i]
        pct[i] = (w < vals[i]).mean() + 0.5 * (w == vals[i]).mean()
    f["pct"] = pct
    f["cum3"] = r + r.shift(1) + r.shift(2)
    f["dF"] = r - r.shift(1)
    f["prev"] = prev
    return f


def attach(bars: pd.DataFrame, feats: pd.DataFrame) -> pd.DataFrame:
    """One row per bar; funding columns = latest settlement with calc_time <= open_time.
    is_settle marks the bar whose open_time == calc_time (the first bar that can see the rate)."""
    b = bars[["open_time", "open", "high", "low", "close"]].copy()
    m = pd.merge_asof(b, feats.rename(columns={"calc_time": "ftime"}), left_on="open_time", right_on="ftime",
                      direction="backward")
    m["is_settle"] = m["ftime"] == m["open_time"]
    # bars 60 min before a settlement (for pre-settlement variants): next settlement time
    nxt = pd.merge_asof(b[["open_time"]], feats[["calc_time"]].rename(columns={"calc_time": "next_ftime"}),
                        left_on="open_time", right_on="next_ftime", direction="forward", allow_exact_matches=False)
    m["mins_to_next"] = (nxt["next_ftime"] - m["open_time"]).dt.total_seconds() / 60.0
    return m


# ------------------------------------------------------------------ variant runner
def run_variant(name, sym, m, side_fn, hold, stop=None, target=None, rule="", bars=None, log=None, pre_mins=None):
    """side_fn(m) -> int array (+1/-1/0) evaluated on settlement bars (or on the bar `pre_mins` before)."""
    side = side_fn(m).astype(int)
    if pre_mins is None:
        mask = m["is_settle"].values
    else:
        mask = (m["mins_to_next"].values == pre_mins)
    side = np.where(mask, side, 0)
    entries = side != 0
    exits = np.zeros(len(m), dtype=bool)
    t0 = time.time()
    tr = backtest_signals_fixed(bars, entries, exits, side, sym=sym, stop_pct=stop, target_pct=target, max_hold_bars=hold)
    st = P.summarize(tr, bars)
    st["name"], st["symbol"], st["rule"] = name, sym, rule
    tr_asis = P.backtest_signals(bars, entries, exits, side, sym=sym, stop_pct=stop, target_pct=target, max_hold_bars=hold)
    sa = P.summarize(tr_asis, bars)
    st["protocol_asis"] = {k: sa.get(k) for k in ("n", "mean_net", "t_stat", "by_year")}
    st["protocol_asis"]["n_zero_hold"] = int((tr_asis.hold_bars == 0).sum()) if len(tr_asis) else 0
    st["n_signals"] = int(entries.sum())
    if len(tr):
        st["n_long"], st["n_short"] = int((tr.side == 1).sum()), int((tr.side == -1).sum())
        st["net_long"], st["net_short"] = float(tr.net[tr.side == 1].sum()), float(tr.net[tr.side == -1].sum())
        st["reasons"] = tr.reason.value_counts().to_dict()
    st["runtime_s"] = round(time.time() - t0, 1)
    log.append(st)
    yrs = st.get("by_year", {})
    print(f"{name:34s} {sym:8s} n={st.get('n',0):5d} tpd={st.get('trades_per_day',0):.2f} mean={st.get('mean_net',0):8.2f} "
          f"t={st.get('t_stat',0):6.2f} wr={st.get('win_rate',0):.3f} aw={st.get('avg_win',0):7.1f} al={st.get('avg_loss',0):7.1f} "
          f"spt={st.get('sharpe_per_trade',0):.3f} L/S net={st.get('net_long',0):.0f}/{st.get('net_short',0):.0f} "
          f"by_year={ {k: round(v) for k, v in yrs.items()} }")
    return tr, st


def diagnostics(m, sym):
    """Conditional mean forward returns (not trades) to see the raw shape of the effect."""
    s = m[m["is_settle"]].copy()
    idx = s.index.values
    close = m["close"].values
    openp = m["open"].values
    for h, lab in ((12, "1h"), (48, "4h"), (94, "~8h")):
        j = np.minimum(idx + 1 + h, len(m) - 1)
        s[f"fwd_{lab}"] = (openp[j] - openp[np.minimum(idx + 1, len(m) - 1)]) / openp[np.minimum(idx + 1, len(m) - 1)] * 1e4
    bins = [-1, -1e-4, 0, 0.5e-4, 1.5e-4, 3e-4, 5e-4, 1e-3, 1]
    s["bucket"] = pd.cut(s["rate"], bins)
    g = s.groupby("bucket", observed=True)[[c for c in s.columns if c.startswith("fwd_")]].agg(["mean", "count"])
    print(f"\n[diag] {sym}: mean forward return (bp) after settlement, by funding-rate bucket")
    print(g.round(1).to_string())
    g2 = s.groupby(pd.cut(s["z"], [-99, -2, -1, 1, 2, 99]), observed=True)[["fwd_1h", "fwd_4h", "fwd_~8h"]].agg(["mean", "count"])
    print(f"[diag] {sym}: by z-score bucket")
    print(g2.round(1).to_string())


# ------------------------------------------------------------------ side functions
def fade_abs(hi=5e-4, lo=-1e-4):
    return lambda m: np.where(m["rate"].values >= hi, -1, np.where(m["rate"].values <= lo, 1, 0))


def follow_abs(hi=5e-4, lo=-1e-4):
    return lambda m: -fade_abs(hi, lo)(m)


def fade_z(k=2.0):
    return lambda m: np.where(m["z"].values >= k, -1, np.where(m["z"].values <= -k, 1, 0))


def follow_z(k=2.0):
    return lambda m: -fade_z(k)(m)


def fade_pct(hi=0.95, lo=0.05, min_hi=2e-4, max_lo=0.0):
    def f(m):
        r, p = m["rate"].values, m["pct"].values
        return np.where((p >= hi) & (r >= min_hi), -1, np.where((p <= lo) & (r <= max_lo), 1, 0))
    return f


def fade_cum3(hi=1.5e-3, lo=-3e-4):
    return lambda m: np.where(m["cum3"].values >= hi, -1, np.where(m["cum3"].values <= lo, 1, 0))


def fade_jump(k=3e-4):
    return lambda m: np.where(m["dF"].values >= k, -1, np.where(m["dF"].values <= -k, 1, 0))


def short_only(hi=5e-4):
    return lambda m: np.where(m["rate"].values >= hi, -1, 0)


def long_only(lo=-1e-4):
    return lambda m: np.where(m["rate"].values <= lo, 1, 0)


def post_settle_long(hi=3e-4):
    return lambda m: np.where(m["rate"].values >= hi, 1, 0)


def pre_settle_short(hi=3e-4):
    # uses the PREVIOUS settled rate (the one in `rate` at a bar 60 min before the next settlement
    # is the rate settled ~7h earlier -> already known)
    return lambda m: np.where(m["rate"].values >= hi, -1, 0)


def fade_abs_mom(hi=5e-4, lo=-1e-4, lookback=96):
    """A1 sides, but only when price moved against the crowd during the funding window:
    short if F>=hi and close_T < close_{T-8h} (longs paying AND losing -> liquidation-prone);
    long if F<=lo and close_T > close_{T-8h} (shorts paying AND losing -> squeeze-prone)."""
    def f(m):
        r = m["rate"].values
        c = m["close"].values
        c_prev = np.roll(c, lookback)
        c_prev[:lookback] = np.nan
        down, up = c < c_prev, c > c_prev
        return np.where((r >= hi) & down, -1, np.where((r <= lo) & up, 1, 0))
    return f


def tail_short(hi=1e-3):
    return lambda m: np.where(m["rate"].values >= hi, -1, 0)


# ------------------------------------------------------------------ main
def main():
    log = []
    data = {}
    for sym in ("BTCUSDT", "ETHUSDT"):
        bars = load_bars(sym, FREQ, root=ROOT)
        feats = funding_features(load_funding(sym, root=ROOT))
        m = attach(bars, feats)
        data[sym] = (bars, m)
        print(sym, "bars", len(bars), bars.open_time.min(), "->", bars.open_time.max(),
              "| settlement bars", int(m.is_settle.sum()))
        diagnostics(m, sym)
    print()

    B, MB = data["BTCUSDT"]
    E, ME = data["ETHUSDT"]
    V = []  # (name, sym, side_fn, hold, stop, target, rule, pre_mins)
    H8 = TO_NEXT_FUNDING
    # --- level, absolute thresholds (economic units: 0.05%/8h ~ 55%/yr paid by longs)
    V.append(("A1_fade_abs_8h", "BTCUSDT", fade_abs(), H8, None, None,
              "short if F>=0.0005, long if F<=-0.0001; enter T+5m; exit 7h50m later (before next settlement)", None))
    V.append(("A2_follow_abs_8h", "BTCUSDT", follow_abs(), H8, None, None, "A1 with sides reversed", None))
    # --- level, relative thresholds
    V.append(("A3_fade_z2_8h", "BTCUSDT", fade_z(2.0), H8, None, None,
              "z=(F-mean_prev270)/max(std_prev270,1e-4); short z>=2, long z<=-2; hold 7h50m", None))
    V.append(("A4_follow_z2_8h", "BTCUSDT", follow_z(2.0), H8, None, None, "A3 with sides reversed", None))
    V.append(("A5_fade_pct95_8h", "BTCUSDT", fade_pct(), H8, None, None,
              "pct over prev 540 settlements; short pct>=.95 & F>=0.0002, long pct<=.05 & F<=0; hold 7h50m", None))
    # --- horizon
    V.append(("A6_fade_abs_4h", "BTCUSDT", fade_abs(), 4 * BARS_PER_HOUR, None, None, "A1 sides, hold 4h", None))
    V.append(("A7_fade_abs_2h", "BTCUSDT", fade_abs(), 2 * BARS_PER_HOUR, None, None, "A1 sides, hold 2h", None))
    # --- risk control
    V.append(("A8_fade_abs_8h_stop1", "BTCUSDT", fade_abs(), H8, 0.01, None, "A1 plus 1% stop (no target)", None))
    # --- other funding transforms
    V.append(("A9_fade_cum24h_8h", "BTCUSDT", fade_cum3(), H8, None, None,
              "sum of last 3 settlements: short >=0.0015, long <=-0.0003; hold 7h50m", None))
    V.append(("A10_fade_jump_8h", "BTCUSDT", fade_jump(), H8, None, None,
              "dF=F_t-F_{t-1}: short dF>=0.0003, long dF<=-0.0003; hold 7h50m", None))
    # --- side decomposition of A1
    V.append(("A11_short_only_abs_8h", "BTCUSDT", short_only(), H8, None, None, "short if F>=0.0005 only; hold 7h50m", None))
    V.append(("A12_long_only_abs_8h", "BTCUSDT", long_only(), H8, None, None, "long if F<=-0.0001 only; hold 7h50m", None))
    # --- ETH
    V.append(("E1_fade_abs_8h", "ETHUSDT", fade_abs(), H8, None, None, "A1 on ETH", None))
    V.append(("E2_follow_abs_8h", "ETHUSDT", follow_abs(), H8, None, None, "A2 on ETH", None))
    V.append(("E3_fade_z2_8h", "ETHUSDT", fade_z(2.0), H8, None, None, "A3 on ETH", None))
    # --- settlement micro-structure
    V.append(("M1_post_settle_long_1h", "BTCUSDT", post_settle_long(), 1 * BARS_PER_HOUR, None, None,
              "long at T+5m if F_T>=0.0003, exit 1h later (pre-settlement selling by payers reverses)", None))
    V.append(("M2_pre_settle_short_1h", "BTCUSDT", pre_settle_short(), 1 * BARS_PER_HOUR, None, None,
              "short at T-55m if previous settled rate (T-8h) >=0.0003, exit at ~T+5m (payers sell before paying)", 60))

    # --- interaction with price action during the funding window, and the far tail
    V.append(("A13_fade_abs_mom_8h", "BTCUSDT", fade_abs_mom(), H8, None, None,
              "short if F>=0.0005 and close_T<close_{T-8h}; long if F<=-0.0001 and close_T>close_{T-8h}; hold 7h50m", None))
    V.append(("A14_tail_short_abs1e-3_4h", "BTCUSDT", tail_short(1e-3), 4 * BARS_PER_HOUR, None, None,
              "short if F>=0.001 (>=0.1%/8h); hold 4h", None))
    V.append(("E4_fade_pct95_8h", "ETHUSDT", fade_pct(), H8, None, None, "A5 on ETH", None))

    for name, sym, fn, hold, stop, target, rule, pre in V:
        bars, m = data[sym]
        run_variant(name, sym, m, fn, hold, stop, target, rule, bars, log, pre_mins=pre)

    n_var = len(log)
    print(f"\nvariants tried: {n_var}")
    for st in log:
        if st.get("n", 0) >= 3:
            st["deflated_sharpe_p"] = P.deflated_sharpe(st["sharpe_per_trade"], st["n"], n_var)
    # survivor screen
    print("\nscreen (mean_net>0, t>=2.5, n>=150, >=3 positive years of 5):")
    for st in log:
        if st.get("n", 0) == 0:
            continue
        pos_years = sum(1 for v in st["by_year"].values() if v > 0)
        ok = st["mean_net"] > 0 and st["t_stat"] >= 2.5 and st["n"] >= 150 and pos_years >= 3
        st["pos_years"], st["passes_screen"] = pos_years, bool(ok)
        pa = st["protocol_asis"]
        print(f"  {st['name']:34s} {st['symbol']:8s} t={st['t_stat']:5.2f} n={st['n']:4d} posyrs={pos_years} DSR_p={st.get('deflated_sharpe_p',0):.3f} -> {'PASS' if ok else 'fail'}"
              f"   [protocol as-is: n={pa['n']} mean={pa['mean_net']:.2f} t={pa['t_stat']:.2f} zero-hold={pa['n_zero_hold']}]")
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w") as fh:
        json.dump(log, fh, indent=1, default=str)
    print("wrote", OUT_JSON)


if __name__ == "__main__":
    main()
