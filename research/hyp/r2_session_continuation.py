"""Hypothesis family: session_continuation (round 2, pre-registered).

Question: does the return already accrued inside the current Topstep day (overnight 17:00 -> 08:30 CT,
day-so-far 17:00 -> 12:00 CT) or over the previous Topstep day (17:00 CT -> 15:08 CT) predict the
rest-of-day return of BTC, conditional on that accrued return being large relative to its trailing
60-Topstep-day standard deviation?  Instrument: CME micro Bitcoin (MBT = 0.1 BTC) on Topstep, proxied
by the Binance BTCUSDT perpetual.  In-sample only (2020-01-01 .. 2024-06-30).

PRE-REGISTERED VARIANTS (all of them run and reported; none added, none dropped):
  V1 overnight_reversal_z1     : 08:30 CT, |z| >= 1.0, side = -sign(r_overnight),  exit 15:08 CT same day
  V2 overnight_reversal_z05    : 08:30 CT, |z| >= 0.5, side = -sign(r_overnight),  exit 15:08 CT same day
  V3 daysofar_continuation_z1  : 12:00 CT, |z| >= 1.0, side = +sign(r_daysofar),   exit 15:08 CT same day
  V4 daysofar_continuation_z05 : 12:00 CT, |z| >= 0.5, side = +sign(r_daysofar),   exit 15:08 CT same day
  V5 prevday_continuation_z1   : 17:00 CT Sun-Thu, |z| >= 1.0, side = +sign(r_prevday), exit 15:08 CT next day

Implementation conventions (fixed before any result was looked at):
  * Execution grid = 1-minute bars.  The pre-registered exit is "the 15:08 CT bar open", which does not
    exist on a 5-minute grid; signal prices (bar opens at 17:00 / 08:30 / 12:00 / 15:08 CT) are the same
    on either grid, so nothing else changes.
  * Topstep day d = the session that opens at 17:00 CT on calendar date d (d = Sun..Thu) and ends at
    15:10 CT on d+1.  "previous 17:00 CT bar" = the 17:00 CT bar of day d.
  * Protocol rule "signal computed from bar i is acted on at the open of bar i+1": the entry is flagged on
    the bar immediately BEFORE the named entry bar and the decision price is that bar's close
    (08:29 CT close for the 08:30 entry, 11:59 CT close for the 12:00 entry).  That close is the last
    price known before the named open and is the decision-time proxy for "open of the 08:30 (12:00) bar".
    The same proxy is used in the history that feeds the standard deviation (consistent definition).
    For V5 both ends of the window (17:00 open, 15:08 open) are history at decision time and are used as is.
  * z(r) = r / sd, where sd = sample standard deviation (ddof=1) of the same window return over the 60
    Topstep days immediately preceding the day whose return is being scored (min 50 valid days), i.e.
    history only, the scored return never enters its own sd.  No mean is subtracted (the spec says
    "standard deviation" and takes side = sign(r), so z and r share a sign).
  * Exit: flagged on the 15:07 CT bar -> fill at the 15:08 CT bar open (protocol reason 'signal').
    The protocol's forced flat at 15:10 CT and the weekend rule remain active as a backstop.
  * One contract, no stop / target, costs $3.82 per round turn (protocol.CONTRACT).
  * Deflated Sharpe uses N = 196 prior trials + 5 variants of this family = 201.

Post-hoc diagnostics (at most 2, clearly labelled, never nominated): see DIAGNOSTICS in main().

Run: cd /home/user/j && python3 -m research.hyp.r2_session_continuation
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

from research.data import load_bars
from research import protocol as P

ROOT = "/home/user/j/data_research/IS"
SYM = "BTCUSDT"
OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "r2_session_continuation_results.json")
TZ = "America/Chicago"
N_PRIOR_TRIALS = 196
Z_WINDOW, Z_MINP = 60, 50
TOPSTEP_KEY_DOW = (6, 0, 1, 2, 3)          # Sun..Thu = calendar date of the 17:00 CT open
IS_YEARS = ("2020", "2021", "2022", "2023", "2024")

VARIANTS = [
    # name, window, threshold, side multiplier (+1 continuation / -1 reversal)
    ("V1_overnight_reversal_z1", "overnight", 1.0, -1),
    ("V2_overnight_reversal_z05", "overnight", 0.5, -1),
    ("V3_daysofar_continuation_z1", "daysofar", 1.0, +1),
    ("V4_daysofar_continuation_z05", "daysofar", 0.5, +1),
    ("V5_prevday_continuation_z1", "prevday", 1.0, +1),
]
N_VARIANTS_TOTAL = N_PRIOR_TRIALS + len(VARIANTS)


# ----------------------------------------------------------------------------- daily table
def hhmm(h, m=0):
    return h * 60 + m


def build_daily(bars: pd.DataFrame) -> pd.DataFrame:
    """One row per Topstep day key d (Sun..Thu CT date): the prices and 1-min bar row positions needed."""
    ct = bars["ct"]
    pos = pd.Series(np.arange(len(bars)), index=pd.DatetimeIndex(ct))
    opn = pd.Series(bars["open"].values, index=pos.index)
    cls = pd.Series(bars["close"].values, index=pos.index)
    first = ct.iloc[0].normalize().tz_localize(None) - pd.Timedelta(days=1)
    last = ct.iloc[-1].normalize().tz_localize(None)
    keys = pd.date_range(first, last, freq="D")
    keys = keys[np.isin(keys.dayofweek, TOPSTEP_KEY_DOW)]
    days = pd.DataFrame(index=keys)

    def at(day_offset, h, m):
        naive = keys + pd.Timedelta(days=day_offset, hours=h, minutes=m)
        return pd.DatetimeIndex(naive).tz_localize(TZ, ambiguous="NaT", nonexistent="NaT")

    spots = {"1659": (0, 16, 59), "1700": (0, 17, 0), "0829": (1, 8, 29), "0830": (1, 8, 30),
             "1159": (1, 11, 59), "1200": (1, 12, 0), "1507": (1, 15, 7), "1508": (1, 15, 8)}
    for k, (do, h, m) in spots.items():
        idx = at(do, h, m)
        days[f"i{k}"] = pos.reindex(idx).values
        days[f"o{k}"] = opn.reindex(idx).values
        days[f"c{k}"] = cls.reindex(idx).values

    # window returns (decision-time definitions, see module docstring)
    days["r_overnight"] = days["c0829"] / days["o1700"] - 1.0      # 17:00 open -> last price before 08:30
    days["r_daysofar"] = days["c1159"] / days["o1700"] - 1.0       # 17:00 open -> last price before 12:00
    days["r_fullday"] = days["o1508"] / days["o1700"] - 1.0        # 17:00 open -> 15:08 open (all history at 17:00 next day)
    for w in ("overnight", "daysofar", "fullday"):
        sd = days[f"r_{w}"].rolling(Z_WINDOW, min_periods=Z_MINP).std(ddof=1).shift(1)
        days[f"sd_{w}"] = sd
        days[f"z_{w}"] = days[f"r_{w}"] / sd
    # V5 uses the PREVIOUS Topstep day's full-day return and its z (Sunday <- Thursday)
    days["r_prevday"] = days["r_fullday"].shift(1)
    days["z_prevday"] = days["z_fullday"].shift(1)
    return days


# ----------------------------------------------------------------------------- signal arrays
WINDOW_ENTRY = {"overnight": ("i0829", "i0830"), "daysofar": ("i1159", "i1200"), "prevday": ("i1659", "i1700")}


def build_signals(bars: pd.DataFrame, days: pd.DataFrame, window: str, thr: float, side_mult: int):
    n = len(bars)
    entries = np.zeros(n, dtype=bool)
    side = np.zeros(n, dtype=int)
    flag_col, fill_col = WINDOW_ENTRY[window]
    r, z = days[f"r_{window}"], days[f"z_{window}"]
    ok = (days[flag_col].notna() & days[fill_col].notna() & (days[fill_col] == days[flag_col] + 1)
          & z.abs().ge(thr) & r.ne(0) & r.notna())
    rows = days.loc[ok, flag_col].astype(int).values
    entries[rows] = True
    side[rows] = (side_mult * np.sign(r[ok].values)).astype(int)
    minutes = (bars["ct"].dt.hour * 60 + bars["ct"].dt.minute).values
    exits = minutes == hhmm(15, 7)             # -> fill at the open of the next (15:08 CT) bar
    return entries, exits, side


def rule_text(window: str, thr: float, side_mult: int) -> str:
    sd = (f"z = r / sd, sd = sample std (ddof=1) of the same window return over the 60 Topstep days preceding "
          f"the scored day (min 50 valid), no mean subtracted")
    common = ("1 MBT (0.1 BTC), no stop/target, Binance BTCUSDT perp 1-min bars as CME proxy, $3.82 round turn. "
              "Topstep day d = session opening 17:00 CT on date d (Sun-Thu) and ending 15:10 CT on d+1. ")
    if window == "overnight":
        return (common + f"At the 08:29 CT bar close on d+1 compute r = close(08:29 CT) / open(17:00 CT bar of day d) - 1 "
                f"(the 08:29 close is the last price before the 08:30 open); {sd}. If |z| >= {thr}: enter at the open of the "
                f"08:30 CT bar with side = -sign(r) (fade the overnight move); exit at the open of the 15:08 CT bar the same day. "
                f"Forced flat 15:10 CT as backstop.")
    if window == "daysofar":
        return (common + f"At the 11:59 CT bar close on d+1 compute r = close(11:59 CT) / open(17:00 CT bar of day d) - 1 "
                f"(the 11:59 close is the last price before the 12:00 open); {sd}. If |z| >= {thr}: enter at the open of the "
                f"12:00 CT bar with side = +sign(r) (continue the day-so-far move); exit at the open of the 15:08 CT bar the "
                f"same day. Forced flat 15:10 CT as backstop.")
    return (common + f"At 16:59 CT on date d (Sun-Thu) compute r = open(15:08 CT bar of the previous Topstep day's day session) "
            f"/ open(17:00 CT bar that opened the previous Topstep day) - 1 (for Sunday the previous Topstep day is "
            f"Thu 17:00 -> Fri 15:08); {sd} (the 60 Topstep days preceding that previous day). If |z| >= {thr}: enter at "
            f"the open of the 17:00 CT bar of date d with side = +sign(r); hold overnight and exit at the open of the 15:08 CT "
            f"bar on d+1. Forced flat 15:10 CT / weekend as backstop.")


def qualifies(st: dict) -> tuple[bool, dict]:
    by = st.get("by_year", {})
    pos_years = sum(1 for y in IS_YEARS if by.get(y, 0.0) > 0)
    checks = {"mean_net_pos": st.get("mean_net", 0) > 0, "t_ge_2.5": st.get("t_stat", 0) >= 2.5,
              "n_ge_150": st.get("n", 0) >= 150, "pos_years_ge_3": pos_years >= 3, "pos_years": pos_years}
    return all(v for k, v in checks.items() if k != "pos_years"), checks


def tstat(x: np.ndarray) -> float:
    x = np.asarray(x, float)
    return float(x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))) if len(x) > 1 and x.std(ddof=1) > 0 else 0.0


# ----------------------------------------------------------------------------- main
def main():
    bars = load_bars(SYM, "1m", root=ROOT).sort_values("open_time").reset_index(drop=True)
    assert bars["open_time"].max() <= P.IS_END, "in-sample data only"
    days = build_daily(bars)
    c = P.CONTRACT[SYM]
    print(f"bars={len(bars)} {bars['open_time'].iloc[0]} -> {bars['open_time'].iloc[-1]}; topstep days={len(days)}; "
          f"days with all prices={int(days[['o1700', 'o0830', 'o1200', 'o1508']].notna().all(axis=1).sum())}")

    results, trades_all = [], {}
    for name, window, thr, side_mult in VARIANTS:
        entries, exits, side = build_signals(bars, days, window, thr, side_mult)
        tr = P.backtest_signals(bars, entries, exits, side, sym=SYM)
        st = P.summarize(tr, bars)
        trades_all[name] = tr
        rec = {"name": name, "symbol": SYM, "window": window, "z_threshold": thr, "side_mult": side_mult,
               "rule": rule_text(window, thr, side_mult), "n": int(st.get("n", 0))}
        if rec["n"] > 0:
            rec.update({k: float(st[k]) for k in ("trades_per_day", "mean_net", "median_net", "t_stat", "ci95_low", "ci95_high",
                                                  "win_rate", "avg_win", "avg_loss", "sharpe_per_trade", "sharpe_annual",
                                                  "total_net", "gross_mean", "max_drawdown")})
            rec["by_year"] = {k: round(v, 1) for k, v in st["by_year"].items()}
            rec["n_by_year"] = st["n_by_year"]
            rec["reasons"] = {k: int(v) for k, v in tr["reason"].value_counts().items()}
            rec["n_long"], rec["n_short"] = int((tr["side"] > 0).sum()), int((tr["side"] < 0).sum())
            rec["mean_net_long"] = float(tr.loc[tr["side"] > 0, "net"].mean()) if rec["n_long"] else 0.0
            rec["mean_net_short"] = float(tr.loc[tr["side"] < 0, "net"].mean()) if rec["n_short"] else 0.0
            rec["dsr"] = float(P.deflated_sharpe(st["sharpe_per_trade"], st["n"], N_VARIANTS_TOTAL))
            rec["survivor"], rec["survivor_checks"] = qualifies(st)
        else:
            rec.update({"survivor": False, "survivor_checks": {}})
        results.append(rec)
        print(f"{name:30s} n={rec['n']:5d} mean_net={rec.get('mean_net', 0):8.2f} t={rec.get('t_stat', 0):6.2f} "
              f"wr={rec.get('win_rate', 0):.3f} tpd={rec.get('trades_per_day', 0):.3f} dsr={rec.get('dsr', 0):.3f} "
              f"by_year={rec.get('by_year')} reasons={rec.get('reasons')} survivor={rec['survivor']}")
        sys.stdout.flush()

    # ------------------------------------------------------------------ POST-HOC DIAGNOSTICS (labelled; never nominated)
    diag = {}
    # D1: response by |z| bucket for each window, same side convention and the same fills as the variants
    #     (computed from the daily table: entry open -> 15:08 open, net of cost).  Shows the whole conditional
    #     response including the unconditional (|z| < 0.5) region that no variant trades.
    buckets = [(0.0, 0.5), (0.5, 1.0), (1.0, 2.0), (2.0, np.inf)]
    d1 = {}
    for name, window, thr, side_mult, entry_col in (("overnight_reversal", "overnight", None, -1, "o0830"),
                                                     ("daysofar_continuation", "daysofar", None, +1, "o1200"),
                                                     ("prevday_continuation", "prevday", None, +1, "o1700")):
        r, z = days[f"r_{window}"], days[f"z_{window}"]
        pnl = side_mult * np.sign(r) * (days["o1508"] - days[entry_col]) * c["mult"] - c["cost_rt"]
        valid = z.notna() & r.ne(0) & pnl.notna()
        tab = {}
        for lo, hi in buckets:
            m = valid & z.abs().ge(lo) & z.abs().lt(hi)
            x = pnl[m].values
            tab[f"|z| in [{lo},{hi})"] = {"n": int(m.sum()), "mean_net": float(x.mean()) if len(x) else 0.0, "t": tstat(x)}
        x = pnl[valid].values
        tab["all"] = {"n": int(valid.sum()), "mean_net": float(x.mean()), "t": tstat(x)}
        d1[name] = tab
    diag["D1_response_by_abs_z_bucket"] = d1
    # D2: sensitivity to the decision-price proxy: V1 and V3 recomputed with the LITERAL pre-registered formula
    #     (open of the 08:30 / 12:00 CT bar, i.e. the fill price itself) instead of the preceding 1-min close.
    d2 = {}
    for name, window, thr, side_mult, lit_col, entry_col in (("V1_literal_open0830", "overnight", 1.0, -1, "o0830", "o0830"),
                                                              ("V2_literal_open0830", "overnight", 0.5, -1, "o0830", "o0830"),
                                                              ("V3_literal_open1200", "daysofar", 1.0, +1, "o1200", "o1200"),
                                                              ("V4_literal_open1200", "daysofar", 0.5, +1, "o1200", "o1200")):
        r_lit = days[lit_col] / days["o1700"] - 1.0
        sd_lit = r_lit.rolling(Z_WINDOW, min_periods=Z_MINP).std(ddof=1).shift(1)
        z_lit = r_lit / sd_lit
        pnl = side_mult * np.sign(r_lit) * (days["o1508"] - days[entry_col]) * c["mult"] - c["cost_rt"]
        m = z_lit.notna() & z_lit.abs().ge(thr) & r_lit.ne(0) & pnl.notna()
        x = pnl[m].values
        d2[name] = {"n": int(m.sum()), "mean_net": float(x.mean()) if len(x) else 0.0, "t": tstat(x),
                    "n_same_days_as_variant": int((m & days[f"z_{window}"].abs().ge(thr)).sum())}
    diag["D2_literal_open_formula_sensitivity"] = d2
    print("\nD1 response by |z| bucket (net $/contract, entry open -> 15:08 open):")
    for k, tab in d1.items():
        print(" ", k, json.dumps({b: {kk: round(vv, 2) if isinstance(vv, float) else vv for kk, vv in v.items()} for b, v in tab.items()}))
    print("D2 literal-open sensitivity:", json.dumps({k: {kk: round(vv, 2) if isinstance(vv, float) else vv for kk, vv in v.items()} for k, v in d2.items()}))

    survivors = [r for r in results if r.get("survivor")]
    out = {"family": "session_continuation", "symbol": SYM, "n_variants": len(VARIANTS), "n_prior_trials": N_PRIOR_TRIALS,
           "dsr_N": N_VARIANTS_TOTAL, "bar_size": "1min", "variants": results,
           "survivors": [r["name"] for r in survivors], "diagnostics": diag}
    with open(OUT_JSON, "w") as fh:
        json.dump(out, fh, indent=1, default=str)
    print(f"\nsurvivors: {[r['name'] for r in survivors] or 'none'}; wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
