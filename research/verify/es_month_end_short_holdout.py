"""ONE-SHOT holdout test (2018-01-01 .. 2020-05-14) for the single candidate carried out of the ES round:
SHORT ES at the 14:00 CT bar on the last NYSE trading day of each month, exit at the 15:08 CT bar.
Derived as the mirror of the pre-registered (and significantly losing) V2_month_end_last_hour_long,
in the direction of documented month-end rebalancing flows.  Criterion stated before running:
mean_net > 0 and t >= 1.0 (power-adjusted for ~28 events) and >= 3 of 5 holdout half-years positive.
Uses the pre-registered family script's own event construction (research/hyp/es_calendar_flows.py)
with ROOT pointed at the sealed holdout; the short P&L is the exact mirror of the long trades.
"""
import importlib
import numpy as np
import pandas as pd

mod = importlib.import_module("research.hyp.es_calendar_flows")
mod.ROOT = "/home/user/j/data_research/HO"
mod.IS_START = pd.Timestamp("2018-01-01", tz="UTC")   # the family script asserts its window; point it at the holdout
mod.IS_END = pd.Timestamp("2020-12-31 23:59:59", tz="UTC")
from research.protocol import CONTRACT, trade_stats

bars = mod.load("SPX500")
tab = mod.day_table(bars, mod.holiday_keys())
rec, trades = mod.run_variant(bars, tab, "V2", "ES", "V2_month_end_last_hour_long")
cost = CONTRACT["ES"]["cost_rt"]
gross_long = trades["net"].values + cost
net_short = -gross_long - cost
days = (bars["open_time"].iloc[-1] - bars["open_time"].iloc[0]).total_seconds() / 86400 * 5 / 7
st = trade_stats(net_short, -gross_long, days)
t = trades.copy(); t["net_short"] = net_short
t["half"] = t["entry_time"].dt.year.astype(str) + "H" + ((t["entry_time"].dt.month > 6).astype(int) + 1).astype(str)
print("holdout month-end SHORT: n=%d mean_net=%.2f t=%.2f win_rate=%.3f avg_win=%.1f avg_loss=%.1f CI95=[%.1f, %.1f]" %
      (st.n, st.mean_net, st.t_stat, st.win_rate, st.avg_win, st.avg_loss, st.ci95_low, st.ci95_high))
print("by half-year:", t.groupby("half")["net_short"].agg(["sum", "count"]).round(0).to_dict("index"))
print("long version on holdout (for reference): n=%d mean_net=%.2f t=%.2f" % (rec["n"], rec["mean_net"], rec["t_stat"]))
print("per-event:", [(str(d.date()), round(v, 0)) for d, v in zip(t["entry_time"], t["net_short"])])
crit = st.mean_net > 0 and st.t_stat >= 1.0 and (t.groupby("half")["net_short"].sum() > 0).sum() >= 3
print("CRITERION MET:", bool(crit))
