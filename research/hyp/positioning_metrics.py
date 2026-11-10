"""Hypothesis family: positioning_metrics  (in-sample only, ROOT = data_research/IS)

Binance 5-min futures metrics (open interest, top-trader long/short ratios, global account L/S
ratio, taker buy/sell volume ratio; available from 2022-01, top-trader ratios effectively from
2023-01) plus the klines' taker-buy volume (available from 2020-01) measure crowding and forced
flow.  Questions tested (one position at a time, one micro contract, 5-min decision bars):

  O  open-interest x price  : a strong OI build (z >= 2 of the 1h / 4h log-OI change) together with a
                              large price move (|dP| >= 1%) = fresh directional positioning.  Follow
                              (textbook "rising OI confirms the trend") or fade (crowding)?  And an OI
                              *drop* with a sharp move = liquidations / squeeze exhaustion -> reversal?
  T  taker imbalance        : 1h taker-buy share (from klines, full 2020-2024 span), z-scored over
                              30 days.  Fade (liquidity provision) or follow (informed flow)?
  P  positioning ratios     : follow top traders (4h change in top_sum_ls), fade retail (count_ls
                              30-day percentile), or the top-vs-retail divergence.

Alignment / no look-ahead
  * a metric row with create_time T summarises data up to T (checked: taker_ls_vol@T matches the
    kline bar [T-5m, T) with corr 0.83).  It is attached to the bar whose open_time == T (merge_asof
    backward, tolerance 15 min, so stale values are never carried across data gaps) and a signal on
    bar i is acted on at the open of bar i+1 (= T+5m): always >= 5 min after the data existed.
  * price features use the close of bar i; rolling z-score denominators use values strictly before i.
  * bars are sliced per variant to the span where the features exist so trades/day is meaningful.

Engine: backtest_signals_fixed = protocol.backtest_signals with the flat condition reduced to
`not tradable_mask` (protocol.forced_flat_time is True for the whole 15:10-24:00 CT span, which
closes every evening-session entry on its own bar; see research/hyp/funding_signal.py).  The
as-is protocol numbers are kept in the JSON under "protocol_asis".

Run:  cd /home/user/j && python3 -m research.hyp.positioning_metrics
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
OUT_JSON = "/home/user/j/results/research/positioning_metrics.json"

FREQ = "5min"
H1, H2, H4 = 12, 24, 48          # bars
ZWIN, ZMIN = 8640, 2016          # 30 days / 7 days of 5-min bars


def backtest_signals_fixed(bars, entries, exits, side, sym="BTCUSDT", stop_pct=None, target_pct=None,
                           max_hold_bars=None):
    """Verbatim protocol.backtest_signals except flat_now = ~tradable_mask (15:10 CT break + weekend)."""
    c = P.CONTRACT[sym]
    ts = bars["open_time"]
    o, h, l = bars["open"].values, bars["high"].values, bars["low"].values
    can_enter = P.entry_mask(ts)
    can_hold = P.tradable_mask(ts)
    flat_now = ~can_hold
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


# ------------------------------------------------------------------ features
def features(bars: pd.DataFrame, metrics: pd.DataFrame) -> pd.DataFrame:
    b = bars[["open_time", "open", "high", "low", "close", "volume", "taker_buy_volume"]].copy()
    m = metrics.rename(columns={"create_time": "mtime"}).sort_values("mtime")
    b["open_time"] = b["open_time"].astype("datetime64[us, UTC]")
    m["mtime"] = m["mtime"].astype("datetime64[us, UTC]")
    f = pd.merge_asof(b, m, left_on="open_time", right_on="mtime", direction="backward",
                      tolerance=pd.Timedelta("15min"))
    loi = np.log(f["open_interest"])
    for w in (3, H1, H4):
        d = loi - loi.shift(w)
        f[f"zoi{w}"] = d / d.shift(1).rolling(ZWIN, min_periods=ZMIN).std()
        f[f"dp{w}"] = f["close"] / f["close"].shift(w) - 1.0
    # taker-buy share of volume over the last 1h (klines, from 2020), z-scored over 30 days
    ti = f["taker_buy_volume"].rolling(H1).sum() / f["volume"].rolling(H1).sum() - 0.5
    f["zti12"] = (ti - ti.shift(1).rolling(ZWIN, min_periods=ZMIN).mean()) / ti.shift(1).rolling(ZWIN, min_periods=ZMIN).std()
    # top-trader (position-weighted) L/S ratio: 4h change, z-scored
    dts = f["top_sum_ls"] - f["top_sum_ls"].shift(H4)
    f["ztop4h"] = dts / dts.shift(1).rolling(ZWIN, min_periods=ZMIN).std()
    # global account L/S ratio: 4h change z and 30-day percentile of the level
    dcl = f["count_ls"] - f["count_ls"].shift(H4)
    f["zcnt4h"] = dcl / dcl.shift(1).rolling(ZWIN, min_periods=ZMIN).std()
    f["pct_cnt"] = f["count_ls"].rolling(ZWIN, min_periods=ZMIN).rank(pct=True)
    return f


# ------------------------------------------------------------------ side functions (+1 long / -1 short / 0)
def oi_follow(w, zk=2.0, pk=0.01):
    def s(F):
        z, dp = F[f"zoi{w}"].values, F[f"dp{w}"].values
        return np.where((z >= zk) & (dp >= pk), 1, np.where((z >= zk) & (dp <= -pk), -1, 0))
    return s


def oi_fade(w, zk=2.0, pk=0.01):
    return lambda F: -oi_follow(w, zk, pk)(F)


def oi_drop_reversal(w, zk=-2.0, pk=0.01):
    def s(F):
        z, dp = F[f"zoi{w}"].values, F[f"dp{w}"].values
        return np.where((z <= zk) & (dp >= pk), -1, np.where((z <= zk) & (dp <= -pk), 1, 0))
    return s


def oi_drop_short_only(w, zk=-2.0, pk=0.01):
    return lambda F: np.where((F[f"zoi{w}"].values <= zk) & (F[f"dp{w}"].values >= pk), -1, 0)


def oi_follow_taker(w, zk=2.0, pk=0.01, tk=1.0):
    def s(F):
        base, zt = oi_follow(w, zk, pk)(F), F["zti12"].values
        return np.where((base == 1) & (zt >= tk), 1, np.where((base == -1) & (zt <= -tk), -1, 0))
    return s


def taker_fade(k=2.0):
    return lambda F: np.where(F["zti12"].values >= k, -1, np.where(F["zti12"].values <= -k, 1, 0))


def taker_follow(k=2.0):
    return lambda F: -taker_fade(k)(F)


def top_follow(k=2.0):
    return lambda F: np.where(F["ztop4h"].values >= k, 1, np.where(F["ztop4h"].values <= -k, -1, 0))


def retail_fade(hi=0.95, lo=0.05):
    return lambda F: np.where(F["pct_cnt"].values >= hi, -1, np.where(F["pct_cnt"].values <= lo, 1, 0))


def divergence(k=1.5):
    def s(F):
        zt, zc = F["ztop4h"].values, F["zcnt4h"].values
        return np.where((zt >= k) & (zc <= -k), 1, np.where((zt <= -k) & (zc >= k), -1, 0))
    return s


# ------------------------------------------------------------------ runner
def run_variant(name, sym, F, bars, side_fn, hold, rule, start, stop=None, target=None, log=None):
    sl = (bars["open_time"] >= pd.Timestamp(start, tz="UTC")).values
    b, Fs = bars[sl].reset_index(drop=True), F[sl].reset_index(drop=True)
    side = np.nan_to_num(side_fn(Fs)).astype(int)
    entries = side != 0
    exits = np.zeros(len(b), dtype=bool)
    t0 = time.time()
    tr = backtest_signals_fixed(b, entries, exits, side, sym=sym, stop_pct=stop, target_pct=target, max_hold_bars=hold)
    st = P.summarize(tr, b)
    st["name"], st["symbol"], st["rule"], st["start"] = name, sym, rule, start
    st["hold_bars"], st["stop_pct"], st["target_pct"] = hold, stop, target
    st["n_signal_bars"] = int(entries.sum())
    tra = P.backtest_signals(b, entries, exits, side, sym=sym, stop_pct=stop, target_pct=target, max_hold_bars=hold)
    sa = P.summarize(tra, b)
    st["protocol_asis"] = {k: sa.get(k) for k in ("n", "mean_net", "t_stat", "by_year")}
    st["protocol_asis"]["n_zero_hold"] = int((tra.hold_bars == 0).sum()) if len(tra) else 0
    if len(tr):
        st["n_long"], st["n_short"] = int((tr.side == 1).sum()), int((tr.side == -1).sum())
        st["net_long"], st["net_short"] = float(tr.net[tr.side == 1].sum()), float(tr.net[tr.side == -1].sum())
        st["t_long"] = float(tr.net[tr.side == 1].mean() / tr.net[tr.side == 1].std() * np.sqrt((tr.side == 1).sum())) if (tr.side == 1).sum() > 2 else 0.0
        st["t_short"] = float(tr.net[tr.side == -1].mean() / tr.net[tr.side == -1].std() * np.sqrt((tr.side == -1).sum())) if (tr.side == -1).sum() > 2 else 0.0
        st["reasons"] = tr.reason.value_counts().to_dict()
        st["mean_gross_bp"] = float((tr.side * (tr.exit / tr.entry - 1)).mean() * 1e4)
    st["runtime_s"] = round(time.time() - t0, 1)
    log.append(st)
    yrs = st.get("by_year", {})
    print(f"{name:30s} {sym:8s} n={st.get('n',0):5d} tpd={st.get('trades_per_day',0):.2f} mean={st.get('mean_net',0):7.2f} "
          f"t={st.get('t_stat',0):5.2f} wr={st.get('win_rate',0):.3f} aw={st.get('avg_win',0):6.1f} al={st.get('avg_loss',0):6.1f} "
          f"spt={st.get('sharpe_per_trade',0):.3f} L/S n={st.get('n_long',0)}/{st.get('n_short',0)} "
          f"t={st.get('t_long',0):.1f}/{st.get('t_short',0):.1f} by_year={ {k: round(v) for k, v in yrs.items()} } "
          f"[asis n={st['protocol_asis']['n']} t={st['protocol_asis']['t_stat'] or 0:.2f}]")
    return tr, st


def diagnostics(F, sym):
    """Conditional mean forward returns (bp, open i+1 -> open i+1+h) by feature bucket, not trades."""
    o = F["open"].values
    for h in (H1, H4):
        F[f"fwd{h}"] = np.r_[(o[1 + h:] - o[1:len(o) - h]) / o[1:len(o) - h], np.full(h + 1, np.nan)] * 1e4
    print(f"\n[diag] {sym}: OI z (1h) x price change (1h) -> forward 1h / 4h return (bp), count")
    g = F.groupby([pd.cut(F["zoi12"], [-99, -2, 2, 99]), pd.cut(F["dp12"], [-1, -0.01, 0.01, 1])], observed=True)[["fwd12", "fwd48"]].agg(["mean", "count"])
    print(g.round(1).to_string())
    print(f"[diag] {sym}: taker z (1h) -> fwd 1h / 4h")
    print(F.groupby(pd.cut(F["zti12"], [-99, -2, -1, 1, 2, 99]), observed=True)[["fwd12", "fwd48"]].agg(["mean", "count"]).round(1).to_string())
    print(f"[diag] {sym}: top-trader 4h change z -> fwd 1h / 4h")
    print(F.groupby(pd.cut(F["ztop4h"], [-99, -2, -1, 1, 2, 99]), observed=True)[["fwd12", "fwd48"]].agg(["mean", "count"]).round(1).to_string())
    print(f"[diag] {sym}: retail count_ls 30d percentile -> fwd 1h / 4h")
    print(F.groupby(pd.cut(F["pct_cnt"], [-0.01, 0.05, 0.5, 0.95, 1.01]), observed=True)[["fwd12", "fwd48"]].agg(["mean", "count"]).round(1).to_string())


# ------------------------------------------------------------------ main
def main():
    log, data = [], {}
    for sym in ("BTCUSDT", "ETHUSDT"):
        bars = load_bars(sym, FREQ, root=ROOT)
        F = features(bars, load_metrics(sym, root=ROOT))
        data[sym] = (bars, F)
        print(sym, "bars", len(bars), bars.open_time.min(), "->", bars.open_time.max(),
              "| OI rows", int(F.open_interest.notna().sum()), "| top_sum rows", int(F.top_sum_ls.notna().sum()))
        diagnostics(F, sym)
    print()

    OI0, TK0, TOP0, CNT0 = "2022-01-01", "2020-01-01", "2023-01-01", "2022-02-01"
    R_O1 = ("BTC 5-min bars. zoi = (ln OI_t - ln OI_{t-12}) / std of that 1h log-change over the prior 30 days; "
            "dp = close_t/close_{t-12} - 1. Signal at bar close: LONG if zoi>=2 and dp>=+1%, SHORT if zoi>=2 and dp<=-1%. "
            "Enter at next 5-min open, exit at the open 48 bars (4h) after entry, no stop/target; forced flat at 15:10 CT / Friday 15:10; "
            "no entries 15:08-17:00 CT; one position at a time")
    V = [
        ("O1_oi_build_follow_1h_h4", "BTCUSDT", oi_follow(H1), H4, R_O1, OI0, None),
        ("O2_oi_build_follow_1h_h2", "BTCUSDT", oi_follow(H1), H2, "O1 but exit 24 bars (2h) after entry", OI0, None),
        ("O3_oi_build_follow_1h_h4_stop1", "BTCUSDT", oi_follow(H1), H4, "O1 plus a 1% stop from entry price (bar high/low)", OI0, 0.01),
        ("O4_oi_build_follow_4h_h4", "BTCUSDT", oi_follow(H4), H4, "O1 with the 4h (48-bar) OI change and 4h price change; |dp|>=1%; hold 4h", OI0, None),
        ("O5_oi_build_fade_1h_h4", "BTCUSDT", oi_fade(H1), H4, "O1 with sides reversed (fade fresh crowding)", OI0, None),
        ("O6_oi_drop_reversal_1h_h4", "BTCUSDT", oi_drop_reversal(H1), H4,
         "zoi<=-2 (OI collapse over 1h): SHORT if dp>=+1% (short-squeeze exhaustion), LONG if dp<=-1% (long-liquidation reversal); hold 4h", OI0, None),
        ("O7_oi_drop_short_only_1h_h4", "BTCUSDT", oi_drop_short_only(H1), H4, "O6 short side only", OI0, None),
        ("O8_oi_build_follow_taker_1h_h4", "BTCUSDT", oi_follow_taker(H1), H4,
         "O1 and the 1h taker-buy-share z (30d) agrees: long needs zti>=+1, short needs zti<=-1", OI0, None),
        ("E1_oi_build_follow_1h_h4", "ETHUSDT", oi_follow(H1), H4, "O1 on ETH (MET)", OI0, None),
        ("T1_taker_fade_1h_h1", "BTCUSDT", taker_fade(2.0), H1,
         "zti = z-score (30d) of 1h taker-buy share of volume (klines): SHORT if zti>=2, LONG if zti<=-2; hold 1h", TK0, None),
        ("T2_taker_follow_1h_h4", "BTCUSDT", taker_follow(2.0), H4, "T1 sides reversed, hold 4h", TK0, None),
        ("P1_top_follow_4h", "BTCUSDT", top_follow(2.0), H4,
         "ztop = 4h change in top_sum_ls / std (30d): LONG if ztop>=2, SHORT if ztop<=-2; hold 4h", TOP0, None),
        ("P2_retail_fade_level_h4", "BTCUSDT", retail_fade(), H4,
         "pct = 30d rolling percentile of count_ls level: SHORT if pct>=0.95, LONG if pct<=0.05; hold 4h", CNT0, None),
        ("P3_top_vs_retail_divergence_h4", "BTCUSDT", divergence(1.5), H4,
         "LONG if ztop>=1.5 and zcnt<=-1.5 (top traders add longs, retail adds shorts), SHORT if reverse; hold 4h", TOP0, None),
        # --- second pass (added after seeing the first 14; all logged)
        ("O9_oi_build_follow_4h_relaxed_h4", "BTCUSDT", oi_follow(H4, 1.5, 0.005), H4,
         "O4 with relaxed thresholds: zoi(4h)>=1.5 and |dp(4h)|>=0.5%; hold 4h", OI0, None),
        ("O10_oi_cascade_reversal_15m_h1", "BTCUSDT", oi_drop_reversal(3, -3.0, 0.01), H1,
         "15-min window (3 bars): zoi(15m)<=-3 (OI collapse) and dp(15m)<=-1% -> LONG, dp>=+1% -> SHORT (liquidation cascade reversal); hold 1h", OI0, None),
        ("E2_retail_fade_level_h4", "ETHUSDT", retail_fade(), H4, "P2 on ETH (MET)", CNT0, None),
        ("E3_top_follow_4h", "ETHUSDT", top_follow(2.0), H4, "P1 on ETH (MET)", TOP0, None),
        ("E4_oi_build_follow_4h_h4", "ETHUSDT", oi_follow(H4), H4, "O4 on ETH (MET)", OI0, None),
    ]
    for name, sym, fn, hold, rule, start, stop in V:
        bars, F = data[sym]
        run_variant(name, sym, F, bars, fn, hold, rule, start, stop=stop, log=log)

    n_var = len(log)
    print(f"\nvariants tried: {n_var}")
    print("screen (mean_net>0, t>=2.5, n>=150, net>0 in >=3 calendar years):")
    for st in log:
        if st.get("n", 0) >= 3:
            st["deflated_sharpe_p"] = P.deflated_sharpe(st["sharpe_per_trade"], st["n"], n_var)
        if st.get("n", 0) == 0:
            st["passes_screen"] = False
            continue
        pos_years = sum(1 for v in st["by_year"].values() if v > 0)
        ok = st["mean_net"] > 0 and st["t_stat"] >= 2.5 and st["n"] >= 150 and pos_years >= 3
        st["pos_years"], st["passes_screen"] = pos_years, bool(ok)
        print(f"  {st['name']:30s} {st['symbol']:8s} t={st['t_stat']:5.2f} n={st['n']:4d} posyrs={pos_years}/{len(st['by_year'])} "
              f"DSR_p={st.get('deflated_sharpe_p',0):.3f} -> {'PASS' if ok else 'fail'}")
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w") as fh:
        json.dump(log, fh, indent=1, default=str)
    print("wrote", OUT_JSON)


if __name__ == "__main__":
    main()
