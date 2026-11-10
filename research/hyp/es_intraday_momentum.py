"""Hypothesis family: intraday_momentum  (ES, in-sample only, ROOT = data_research/IS, 2005-01 .. 2017-12)

Market intraday momentum (Gao, Han, Li, Zhou 2018, JFE): the first half-hour return of the cash
session predicts the last half-hour return with the same sign; so does the second-to-last half hour,
and the effect is stronger when the signal is large.  Price proxy: Oanda SPX500 CFD minute bars
(timestamps UTC, converted to America/Chicago).  P&L is reported per ONE ES contract ($50/pt,
$16.28 round-turn cost = $3.78 commission + one tick slippage).

PRE-REGISTERED VARIANTS (all times CT, all 5 run and reported, none dropped):
  r1  = open(09:00) / open(08:30) - 1      first half-hour of the cash session
  r60 = open(09:30) / open(08:30) - 1      first hour (V5 only)
  r12 = open(14:30) / open(14:00) - 1      second-to-last half hour
  z(r1) = r1 / std(r1 over the 60 trading days strictly before the decision day)
  V1 first30_last30_sign : at the 14:30 bar enter side = sign(r1); exit at the 15:08 bar
  V2 first30_last30_z1   : as V1, only if |z(r1)| >= 1
  V3 twelfth_last30_sign : at 14:30 enter side = sign(r12); exit 15:08
  V4 both_agree          : at 14:30 enter only if sign(r1) == sign(r12) (both non-zero), that side; exit 15:08
  V5 first60_last30_sign : at 14:30 enter side = sign(r60); exit 15:08

IMPLEMENTATION ON THE 1-MINUTE GRID (the 5-minute grid has no 15:08 bar):
  * "open(HH:MM)" = open of the first 1-minute bar with CT time in [HH:MM, HH:MM+5)  (identical to the
    open of the HH:MM 5-minute bar from load_bars_index(..., "5min")).
  * Signals computed on bar i are acted on at the open of bar i+1 (protocol.backtest_signals).  The
    decision bar is the LAST 1-minute bar before 14:30:00 CT (it must lie in [14:25, 14:30)); the
    entry fills at the open of the next bar, which must be the first bar in [14:30, 14:35) of the
    same CT date ("the 14:30 bar").  For r12 the price "open(14:30)" is therefore the close of the
    decision bar, i.e. the last traded price before 14:30:00 CT - the price a trader sees when the
    14:30 bar opens - so that no bar-(i+1) information enters the bar-i signal.
  * Exit flag is set on the last bar before 15:08:00 CT, so the exit fills at the open of the first
    1-minute bar at/after 15:08 CT ("the 15:08 bar").  If no such bar exists before the 15:10 CT
    break the engine's forced flat closes the trade at the first bar inside the break.  Trades whose
    exit bar is after 15:15 CT (no bar at all in the break -> engine would carry to 17:00) are
    dropped as "missing bar = no trade" and the count is reported.
  * No stops / targets (pure time-window directional bet).  One position at a time per day.
  * Days without any of the needed bars (half days, holidays) produce no trade.

Survivor bar (pre-registered): mean_net > 0, t_stat >= 2.5, n >= 150, net P&L > 0 in >= 8 of the 13
calendar years.  Deflated Sharpe uses 22 pre-registered ES variants in this round.

Post-hoc diagnostics (clearly labelled, never nominated): see DIAGNOSTICS below.

Run:  cd /home/user/j && python3 -m research.hyp.es_intraday_momentum
"""
from __future__ import annotations

import json
import os
import time

import numpy as np
import pandas as pd

from research import protocol as P
from research.data_index import load_bars_index

ROOT = "/home/user/j/data_research/IS"
OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "es_intraday_momentum_results.json")

N_VARIANTS_ROUND = 22   # pre-registered ES variants in this round (deflated Sharpe denominator)
Z_WINDOW = 60           # trailing trading days for the std of r1 (strictly prior days)
Z_THRESH = 1.0
IS_YEARS = list(range(2005, 2018))

SURVIVOR = dict(mean_net=0.0, t_stat=2.5, n=150, pos_years=8)


def mm(h: int, m: int = 0) -> int:
    return h * 60 + m


# ----------------------------------------------------------------------------- daily signal table
def daily_table(bars: pd.DataFrame) -> pd.DataFrame:
    """One row per CT date with the session opens, the decision-bar position and the signals."""
    ct = bars["ct"]
    mn = (ct.dt.hour * 60 + ct.dt.minute).values
    date = ct.dt.date.values
    pos = np.arange(len(bars))
    df = pd.DataFrame({"date": date, "mn": mn, "pos": pos, "open": bars["open"].values, "close": bars["close"].values})

    def first_open(lo, hi):
        s = df[(df["mn"] >= lo) & (df["mn"] < hi)].groupby("date")["open"].first()
        return s

    d = pd.DataFrame(index=pd.Index(sorted(set(date)), name="date"))
    d["o0830"] = first_open(mm(8, 30), mm(8, 35))
    d["o0900"] = first_open(mm(9, 0), mm(9, 5))
    d["o0930"] = first_open(mm(9, 30), mm(9, 35))
    d["o1400"] = first_open(mm(14, 0), mm(14, 5))
    # decision bar: last bar in [14:25, 14:30)
    dec = df[(df["mn"] >= mm(14, 25)) & (df["mn"] < mm(14, 30))].groupby("date").last()
    d["dec_pos"] = dec["pos"]
    d["p1430m"] = dec["close"]           # last traded price before 14:30:00 CT
    # fill bar = bar right after the decision bar; must be in [14:30, 14:35) on the same date
    dp = d["dec_pos"].dropna().astype(int)
    nxt = dp + 1
    ok = nxt < len(df)
    nxt = nxt[ok]
    nxt_mn = df["mn"].values[nxt.values]
    nxt_date = df["date"].values[nxt.values]
    valid = (nxt_mn >= mm(14, 30)) & (nxt_mn < mm(14, 35)) & (nxt_date == nxt.index.values)
    d["fill_ok"] = False
    d.loc[nxt.index[valid], "fill_ok"] = True
    d["o1430"] = np.nan
    d.loc[nxt.index[valid], "o1430"] = df["open"].values[nxt.values[valid]]   # literal 14:30 open (diagnostic only)

    d["r1"] = d["o0900"] / d["o0830"] - 1.0
    d["r60"] = d["o0930"] / d["o0830"] - 1.0
    d["r12"] = d["p1430m"] / d["o1400"] - 1.0
    d["r12_lit"] = d["o1430"] / d["o1400"] - 1.0   # literal open(14:30) version (diagnostic only)
    # trailing std of r1 over the 60 prior days on which r1 is defined (history only)
    r1 = d["r1"].dropna()
    sd = r1.rolling(Z_WINDOW, min_periods=Z_WINDOW).std().shift(1)
    d["sd_r1"] = sd
    d["z1"] = d["r1"] / d["sd_r1"]
    return d


def exit_flags(bars: pd.DataFrame, exit_mn: int = mm(15, 8)) -> np.ndarray:
    """True on the last bar before exit_mn CT of each date -> engine exits at the open of the next bar."""
    ct = bars["ct"]
    mn = (ct.dt.hour * 60 + ct.dt.minute).values
    date = ct.dt.date.values
    n = len(bars)
    ex = np.zeros(n, dtype=bool)
    same = date[1:] == date[:-1]
    ex[:-1] = (mn[:-1] < exit_mn) & (mn[1:] >= exit_mn) & same
    return ex


def build_entries(d: pd.DataFrame, side_daily: pd.Series, n_bars: int, pos_col: str = "dec_pos"):
    entries = np.zeros(n_bars, dtype=bool)
    side = np.zeros(n_bars, dtype=int)
    sel = d[d["fill_ok"] & (side_daily != 0) & side_daily.notna()]
    p = sel[pos_col].astype(int).values
    entries[p] = True
    side[p] = side_daily.loc[sel.index].astype(int).values
    return entries, side


def sgn(x: pd.Series) -> pd.Series:
    return np.sign(x).fillna(0).astype(int)


# ----------------------------------------------------------------------------- variants (pre-registered)
def side_v1(d):
    return sgn(d["r1"])


def side_v2(d):
    s = sgn(d["r1"])
    return s.where(d["z1"].abs() >= Z_THRESH, 0)


def side_v3(d):
    return sgn(d["r12"])


def side_v4(d):
    s1, s12 = sgn(d["r1"]), sgn(d["r12"])
    return s1.where((s1 == s12) & (s1 != 0), 0)


def side_v5(d):
    return sgn(d["r60"])


VARIANTS = [
    ("V1_first30_last30_sign", "side=sign(r1), r1=open(09:00)/open(08:30)-1; enter 14:30 bar open; exit 15:08 bar open", side_v1),
    ("V2_first30_last30_z1", "as V1 but only if |r1| >= 1 x trailing-60-day std of r1 (prior days)", side_v2),
    ("V3_twelfth_last30_sign", "side=sign(r12), r12=open(14:30)/open(14:00)-1 (14:30 price = last trade before 14:30:00); enter 14:30; exit 15:08", side_v3),
    ("V4_both_agree", "enter only if sign(r1)==sign(r12) (both non-zero), that side; enter 14:30; exit 15:08", side_v4),
    ("V5_first60_last30_sign", "side=sign(r60), r60=open(09:30)/open(08:30)-1; enter 14:30; exit 15:08", side_v5),
]


# ----------------------------------------------------------------------------- run
def run_variant(bars: pd.DataFrame, d: pd.DataFrame, side_daily: pd.Series, sym: str, exits: np.ndarray,
                pos_col: str = "dec_pos") -> tuple[pd.DataFrame, dict]:
    entries, side = build_entries(d, side_daily, len(bars), pos_col)
    tr = P.backtest_signals(bars, entries, exits, side, sym)
    info = {"n_raw": int(len(tr)), "n_dropped_missing_exit_bar": 0}
    if len(tr):
        ect = tr["entry_time"].dt.tz_convert("America/Chicago")
        xct = tr["exit_time"].dt.tz_convert("America/Chicago")
        emn = ect.dt.hour * 60 + ect.dt.minute
        xmn = xct.dt.hour * 60 + xct.dt.minute
        bad = (xmn > mm(15, 15)) | (xct.dt.date != ect.dt.date)
        info["n_dropped_missing_exit_bar"] = int(bad.sum())
        tr = tr[~bad].reset_index(drop=True)
        ect = tr["entry_time"].dt.tz_convert("America/Chicago")
        xct = tr["exit_time"].dt.tz_convert("America/Chicago")
        emn = ect.dt.hour * 60 + ect.dt.minute
        xmn = xct.dt.hour * 60 + xct.dt.minute
        assert ((emn >= mm(14, 30)) & (emn < mm(14, 35))).all(), "entry outside the 14:30 bar"
        assert ((xmn >= mm(15, 8)) & (xmn <= mm(15, 15))).all(), "exit outside 15:08-15:15"
        info["exit_min_dist"] = {f"{k // 60:02d}:{k % 60:02d}": int(v) for k, v in xmn.value_counts().sort_index().items()}
        info["exit_reason"] = {str(k): int(v) for k, v in tr["reason"].value_counts().items()}
        info["n_long"] = int((tr["side"] == 1).sum())
        info["n_short"] = int((tr["side"] == -1).sum())
    return tr, info


def evaluate(tr: pd.DataFrame, bars: pd.DataFrame, n_variants: int) -> dict:
    st = P.summarize(tr, bars)
    if st.get("n", 0) == 0:
        st.update(dict(mean_net=0.0, t_stat=0.0, win_rate=0.0, avg_win=0.0, avg_loss=0.0, sharpe_per_trade=0.0,
                       trades_per_day=0.0, by_year={}, n_by_year={}, dsr=0.0, pos_years=0, survivor=False))
        return st
    st["dsr"] = P.deflated_sharpe(st["sharpe_per_trade"], st["n"], n_variants)
    by = st["by_year"]
    st["pos_years"] = int(sum(1 for y in IS_YEARS if by.get(str(y), 0.0) > 0))
    st["survivor"] = bool(st["mean_net"] > SURVIVOR["mean_net"] and st["t_stat"] >= SURVIVOR["t_stat"]
                          and st["n"] >= SURVIVOR["n"] and st["pos_years"] >= SURVIVOR["pos_years"])
    return st


def fmt_by_year(by: dict) -> str:
    return ",".join(f"{y}:{by.get(str(y), 0.0):+.0f}" for y in IS_YEARS)


def main():
    t0 = time.time()
    bars = load_bars_index("SPX500", "1m", root=ROOT)
    assert bars["open_time"].max() <= pd.Timestamp("2017-12-31 23:59:59", tz="UTC")
    d = daily_table(bars)
    exits = exit_flags(bars)
    print(f"SPX500 1m bars {len(bars)}  {bars['open_time'].min()} -> {bars['open_time'].max()}  "
          f"days {len(d)}  days with valid 14:30 fill {int(d['fill_ok'].sum())}  "
          f"r1 defined {int(d['r1'].notna().sum())}  r12 defined {int(d['r12'].notna().sum())}  z1 defined {int(d['z1'].notna().sum())}")

    results = {"family": "intraday_momentum", "symbol": "ES", "root": ROOT, "n_variants_family": len(VARIANTS),
               "n_variants_round": N_VARIANTS_ROUND, "survivor_bar": SURVIVOR, "variants": [], "diagnostics": []}
    trades_store = {}
    for name, rule, fn in VARIANTS:
        tr, info = run_variant(bars, d, fn(d), "ES", exits)
        st = evaluate(tr, bars, N_VARIANTS_ROUND)
        st.update(info)
        st["name"], st["rule"] = name, rule
        results["variants"].append(st)
        trades_store[name] = tr
        print(f"{name:26s} n={st['n']:5d} mean_net={st['mean_net']:8.2f} t={st['t_stat']:6.2f} "
              f"wr={st['win_rate']:.3f} aw={st['avg_win']:7.1f} al={st['avg_loss']:7.1f} spt={st['sharpe_per_trade']:.3f} "
              f"dsr={st['dsr']:.3f} tpd={st['trades_per_day']:.3f} pos_years={st['pos_years']}/13 "
              f"dropped={info['n_dropped_missing_exit_bar']} survivor={st['survivor']}")
        print("    by_year:", fmt_by_year(st["by_year"]))

    # ------------------------------------------------------------------ post-hoc diagnostics (labelled, not nominable)
    # D1: NAS100 (Nasdaq-100 CFD) twin of V1 with NQ costs ($20/pt, $8.78 RT) - same rule, same timing.
    nbars = load_bars_index("NAS100", "1m", root=ROOT)
    nd = daily_table(nbars)
    nexits = exit_flags(nbars)
    tr, info = run_variant(nbars, nd, side_v1(nd), "NQ", nexits)
    st = evaluate(tr, nbars, N_VARIANTS_ROUND)
    st.update(info)
    st["name"] = "D1_NAS100_twin_of_V1 (post-hoc diagnostic, NQ $/contract)"
    st["rule"] = "V1 rule on NAS100 CFD, NQ costs; diagnostic only"
    results["diagnostics"].append(st)
    print(f"[diag] {st['name']}: n={st['n']} mean_net={st['mean_net']:.2f} t={st['t_stat']:.2f} wr={st['win_rate']:.3f} pos_years={st['pos_years']}/13")
    print("    by_year:", fmt_by_year(st["by_year"]))

    # D2: timing-convention check for V3 - literal open(14:30) as the signal's end price, decision bar = the
    # 14:30 bar itself, fill at the open of the NEXT 1-minute bar (14:31).  Tests whether the r12 result depends
    # on using "last trade before 14:30:00" vs the 14:30 open as the signal price.
    d2 = d.copy()
    d2["dec_pos2"] = d2["dec_pos"] + 1   # the 14:30 bar (fill_ok guarantees it is the first bar in [14:30,14:35))
    s_lit = sgn(d2["r12_lit"])
    entries = np.zeros(len(bars), dtype=bool)
    side = np.zeros(len(bars), dtype=int)
    sel = d2[d2["fill_ok"] & (s_lit != 0)]
    p = sel["dec_pos2"].astype(int).values
    entries[p] = True
    side[p] = s_lit.loc[sel.index].astype(int).values
    tr = P.backtest_signals(bars, entries, exits, side, "ES")
    ect = tr["entry_time"].dt.tz_convert("America/Chicago")
    xct = tr["exit_time"].dt.tz_convert("America/Chicago")
    bad = ((xct.dt.hour * 60 + xct.dt.minute) > mm(15, 15)) | (xct.dt.date != ect.dt.date)
    tr = tr[~bad].reset_index(drop=True)
    st = evaluate(tr, bars, N_VARIANTS_ROUND)
    st["name"] = "D2_V3_literal_open1430_fill_next_bar (post-hoc diagnostic)"
    st["rule"] = "side=sign(open(14:30)/open(14:00)-1) with the literal 14:30 open; fill at open of the next 1m bar; exit 15:08"
    st["n_dropped_missing_exit_bar"] = int(bad.sum())
    results["diagnostics"].append(st)
    print(f"[diag] {st['name']}: n={st['n']} mean_net={st['mean_net']:.2f} t={st['t_stat']:.2f} wr={st['win_rate']:.3f} pos_years={st['pos_years']}/13")
    print("    by_year:", fmt_by_year(st["by_year"]))

    surv = [v for v in results["variants"] if v["survivor"]]
    results["survivors"] = [v["name"] for v in surv]
    results["elapsed_s"] = time.time() - t0
    with open(OUT_JSON, "w") as f:
        json.dump(results, f, indent=1, default=str)
    print("survivors:", results["survivors"])
    print("wrote", OUT_JSON, f"({results['elapsed_s']:.1f}s)")
    return results


if __name__ == "__main__":
    main()
