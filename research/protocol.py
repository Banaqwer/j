"""Research protocol shared by every hypothesis test and every verifier.

Instruments: Binance USDT-M perpetual (BTCUSDT, ETHUSDT) as the data proxy for
CME micro futures traded on Topstep: MBT = 0.1 BTC, MET = 0.1 ETH.

Topstep / CME constraints applied to every strategy:
  * trading week: Sunday 17:00 CT -> Friday 15:10 CT; daily break 15:10 -> 17:00 CT
    (no entries after 15:08 CT; everything flat by 15:10 CT; no weekend holds)
  * costs per contract per round turn: MBT $2.82 commission + $1.00 slippage (2 ticks of $0.50);
    MET $0.72 + $0.20
  * max 5 MBT/MET contracts on a 50K (micro crypto capped at mini-equivalent lot sizes)

Statistics: per-trade $ P&L per contract (net), win rate at the realised R, bootstrap CI of the
mean, t-stat, per-trade Sharpe, trades/day, and the deflated Sharpe ratio given how many
variants were tried.  In-sample = 2020-01-01 .. 2024-06-30; holdout = 2024-07-01 .. 2026-10-31
(sealed: hypothesis agents never see it, verifiers use only it).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, asdict

import numpy as np
import pandas as pd

IS_START, IS_END = pd.Timestamp("2020-01-01", tz="UTC"), pd.Timestamp("2024-06-30 23:59:59", tz="UTC")
HO_START, HO_END = pd.Timestamp("2024-07-01", tz="UTC"), pd.Timestamp("2026-10-31 23:59:59", tz="UTC")

CONTRACT = {"BTCUSDT": {"mult": 0.1, "cost_rt": 2.82 + 1.00, "name": "MBT"},
            "ETHUSDT": {"mult": 0.1, "cost_rt": 0.72 + 0.20, "name": "MET"},
            # CME equity index futures (price proxy: Oanda/histdata index CFD minute bars)
            "ES": {"mult": 50.0, "cost_rt": 3.78 + 12.50, "name": "ES"},      # $50/pt, 1 tick = 0.25 = $12.50 slippage
            "MES": {"mult": 5.0, "cost_rt": 1.22 + 1.25, "name": "MES"},
            "NQ": {"mult": 20.0, "cost_rt": 3.78 + 5.00, "name": "NQ"},       # $20/pt, 1 tick = 0.25 = $5
            "MNQ": {"mult": 2.0, "cost_rt": 1.22 + 0.50, "name": "MNQ"},
            "RTY": {"mult": 50.0, "cost_rt": 3.78 + 5.00, "name": "RTY"},     # $50/pt, tick 0.10 = $5
            "M2K": {"mult": 5.0, "cost_rt": 1.22 + 0.50, "name": "M2K"}}


# ------------------------------------------------------------------ session masks (CT)
def ct(ts: pd.Series) -> pd.Series:
    return ts.dt.tz_convert("America/Chicago")


def tradable_mask(ts_utc: pd.Series) -> np.ndarray:
    """True when a position may be held (Topstep/CME crypto hours), for bar open times."""
    t = ct(ts_utc)
    dow = t.dt.dayofweek.values  # Mon=0 .. Sun=6
    minutes = (t.dt.hour * 60 + t.dt.minute).values
    daily_break = (minutes >= 15 * 60 + 10) & (minutes < 17 * 60)
    sat = dow == 5
    fri_after = (dow == 4) & (minutes >= 15 * 60 + 10)
    sun_before = (dow == 6) & (minutes < 17 * 60)
    return ~(daily_break | sat | fri_after | sun_before)


def entry_mask(ts_utc: pd.Series) -> np.ndarray:
    """True when a NEW position may be opened (no entries from 15:08 CT to 17:00 CT)."""
    t = ct(ts_utc)
    minutes = (t.dt.hour * 60 + t.dt.minute).values
    return tradable_mask(ts_utc) & ~((minutes >= 15 * 60 + 8) & (minutes < 17 * 60))


def forced_flat_time(ts_utc: pd.Series) -> np.ndarray:
    """True on bars inside the daily break (15:10-17:00 CT) and from Friday 15:10 CT to Sunday 17:00 CT:
    any open position must be closed at the open of such a bar.  (Earlier version had no upper bound and
    closed evening-session positions one bar after entry; fixed 2026-11-10.)"""
    return ~tradable_mask(ts_utc)


# ------------------------------------------------------------------ trade statistics
@dataclass
class TradeStats:
    n: int
    trades_per_day: float
    mean_net: float          # $ per contract per trade, net of costs
    median_net: float
    std_net: float
    win_rate: float          # fraction with net > 0
    avg_win: float
    avg_loss: float          # positive number
    t_stat: float
    ci95_low: float
    ci95_high: float
    sharpe_per_trade: float
    sharpe_annual: float
    max_drawdown: float
    total_net: float
    gross_mean: float
    p_win_at_1R: float       # win rate if wins/losses were symmetric (= mean/ (|avg_win|+|avg_loss|) adjusted)

    def to_dict(self):
        return asdict(self)


def trade_stats(pnl_net: np.ndarray, pnl_gross: np.ndarray, n_days: float, seed: int = 0) -> TradeStats:
    x = np.asarray(pnl_net, dtype=float)
    n = x.size
    if n == 0:
        return TradeStats(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    rng = np.random.default_rng(seed)
    boots = np.array([rng.choice(x, n, replace=True).mean() for _ in range(2000)])
    mean, std = x.mean(), x.std(ddof=1) if n > 1 else 0.0
    t = mean / (std / math.sqrt(n)) if std > 0 else 0.0
    wins, losses = x[x > 0], x[x <= 0]
    avg_w = wins.mean() if wins.size else 0.0
    avg_l = -losses.mean() if losses.size else 0.0
    eq = np.cumsum(x)
    dd = float((np.maximum.accumulate(eq) - eq).max()) if n else 0.0
    tpd = n / max(n_days, 1.0)
    spt = mean / std if std > 0 else 0.0
    # symmetric-1R equivalent win rate: p such that p*R - (1-p)*R = mean with R = (avg_w+avg_l)/2
    R = 0.5 * (avg_w + avg_l) if (avg_w + avg_l) > 0 else 1.0
    p1r = min(max(0.5 + mean / (2 * R), 0.0), 1.0)
    return TradeStats(n, tpd, float(mean), float(np.median(x)), float(std), float((x > 0).mean()), float(avg_w),
                      float(avg_l), float(t), float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975)),
                      float(spt), float(spt * math.sqrt(tpd * 252)), dd, float(x.sum()), float(np.mean(pnl_gross)), p1r)


def deflated_sharpe(sr_per_trade: float, n: int, n_variants: int, skew: float = 0.0, kurt: float = 3.0) -> float:
    """Bailey & Lopez de Prado deflated Sharpe ratio: probability that the observed per-trade
    Sharpe exceeds the expected maximum Sharpe of `n_variants` unskilled variants."""
    from scipy.stats import norm
    if n < 3 or n_variants < 1:
        return 0.0
    var_sr = 1.0 / n  # sampling variance of an unskilled per-trade Sharpe estimate from n trades
    sr0 = math.sqrt(var_sr) * ((1 - 0.5772) * norm.ppf(1 - 1.0 / n_variants) + 0.5772 * norm.ppf(1 - 1.0 / (n_variants * math.e))) if n_variants > 1 else 0.0
    denom = math.sqrt(max(1 - skew * sr_per_trade + (kurt - 1) / 4 * sr_per_trade ** 2, 1e-12))
    z = (sr_per_trade - sr0) * math.sqrt(n - 1) / denom
    return float(norm.cdf(z))


# ------------------------------------------------------------------ generic backtester
def backtest_signals(bars: pd.DataFrame, entries: np.ndarray, exits: np.ndarray, side: np.ndarray,
                     sym: str = "BTCUSDT", stop_pct: float | None = None, target_pct: float | None = None,
                     max_hold_bars: int | None = None) -> pd.DataFrame:
    """Bar-level event backtest, one position at a time, per ONE micro contract.

    bars    : DataFrame with open_time (UTC), open, high, low, close (1 bar = 1 decision step)
    entries : bool array, enter at the NEXT bar's open when True (and entry allowed)
    exits   : bool array, exit at the NEXT bar's open when True
    side    : +1 long / -1 short per bar (used at entry)
    stop/target : fractional moves from entry price, checked on bar high/low (stop first, conservative)
    Forced flat at 15:10 CT and before the weekend.  Costs: CONTRACT[sym]['cost_rt'] per trade.
    Returns one row per trade: entry_time, exit_time, side, entry, exit, gross, net, hold_bars, reason.
    """
    c = CONTRACT[sym]
    ts = bars["open_time"]
    o, h, l = bars["open"].values, bars["high"].values, bars["low"].values
    can_enter = entry_mask(ts)
    can_hold = tradable_mask(ts)
    flat_now = forced_flat_time(ts)
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
        # in position at bar i: check stop/target on this bar, then exits
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


def summarize(trades: pd.DataFrame, bars: pd.DataFrame) -> dict:
    if trades is None or len(trades) == 0:
        return {"n": 0}
    days = (bars["open_time"].iloc[-1] - bars["open_time"].iloc[0]).total_seconds() / 86400 * (5 / 7)
    st = trade_stats(trades["net"].values, trades["gross"].values, days)
    d = st.to_dict()
    d["by_year"] = {str(y): float(g["net"].sum()) for y, g in trades.groupby(trades["entry_time"].dt.year)}
    d["n_by_year"] = {str(y): int(len(g)) for y, g in trades.groupby(trades["entry_time"].dt.year)}
    return d


def to_edge(stats: dict, trades_per_day_cap: int = 10):
    """Map a trade-stat dict to the Topstep DP's Edge model (per contract)."""
    from topstep.edge import Edge
    tpd = max(1, min(trades_per_day_cap, int(round(stats["trades_per_day"]))))
    aw, al = max(stats["avg_win"], 1e-6), max(stats["avg_loss"], 1e-6)
    return Edge(p_win=stats["win_rate"], reward=aw, loss=al, cost_rt=0.0, trades_per_day=tpd, name="research edge")
