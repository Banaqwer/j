"""Equity-index minute data (Oanda CFD bars 2005-2020 from the FutureSharks/financial-data mirror,
plus histdata SPXUSD 2010-2018 as a cross-check) -> parquet tables usable with research.protocol.

Tables (data_research/): bars_<SYM>_1m.parquet with SYM in SPX500, NAS100, US2000
  columns: open_time (UTC), open, high, low, close, volume, ct (America/Chicago)
Oanda CSV timestamps are UTC (verified below by the US cash-open activity spike at 13:30/14:30 UTC).
Bars are only present when quotes changed; load_bars_index(..., freq) resamples and keeps gaps.
Split: IS <= 2017-12-31, HO >= 2018-01-01 (data ends 2020).
Usage: python -m research.data_index [--split]
"""
from __future__ import annotations

import glob
import os

import pandas as pd

from .data import ROOT, IS_ROOT, HO_ROOT

SRC = os.path.join(ROOT, "spx", "github", "pyfinancialdata", "data", "currencies", "oanda")
IS_END_IDX = pd.Timestamp("2017-12-31 23:59:59", tz="UTC")
HO_START_IDX = pd.Timestamp("2018-01-01", tz="UTC")


def build(sym: str = "SPX500") -> pd.DataFrame:
    files = sorted(glob.glob(os.path.join(SRC, f"{sym}_USD", "*", f"oanda-{sym}_USD-*.csv")))
    if not files:
        print("no files for", sym)
        return pd.DataFrame()
    parts = [pd.read_csv(f) for f in files]
    df = pd.concat(parts, ignore_index=True)
    df["open_time"] = pd.to_datetime(df["time"], utc=True)
    df = df[["open_time", "open", "high", "low", "close", "volume"]].dropna()
    df = df.drop_duplicates("open_time").sort_values("open_time").reset_index(drop=True)
    df["ct"] = df["open_time"].dt.tz_convert("America/Chicago")
    df.to_parquet(os.path.join(ROOT, f"bars_{sym}_1m.parquet"))
    return df


def load_bars_index(sym: str = "SPX500", freq: str = "5min", root: str = ROOT) -> pd.DataFrame:
    df = pd.read_parquet(os.path.join(root, f"bars_{sym}_1m.parquet"))
    if freq == "1m":
        return df
    g = df.set_index("open_time").resample(freq, label="left", closed="left")
    out = pd.DataFrame({"open": g["open"].first(), "high": g["high"].max(), "low": g["low"].min(),
                        "close": g["close"].last(), "volume": g["volume"].sum()}).dropna(subset=["open"]).reset_index()
    out["ct"] = out["open_time"].dt.tz_convert("America/Chicago")
    return out


def build_splits():
    os.makedirs(IS_ROOT, exist_ok=True)
    os.makedirs(HO_ROOT, exist_ok=True)
    for sym in ("SPX500", "NAS100", "US2000"):
        path = os.path.join(ROOT, f"bars_{sym}_1m.parquet")
        if not os.path.exists(path):
            continue
        df = pd.read_parquet(path)
        df[df["open_time"] <= IS_END_IDX].to_parquet(os.path.join(IS_ROOT, f"bars_{sym}_1m.parquet"))
        df[df["open_time"] >= HO_START_IDX].to_parquet(os.path.join(HO_ROOT, f"bars_{sym}_1m.parquet"))
        print("split", sym, "IS", int((df["open_time"] <= IS_END_IDX).sum()), "HO", int((df["open_time"] >= HO_START_IDX).sum()))


if __name__ == "__main__":
    import sys
    if "--split" in sys.argv:
        build_splits()
        sys.exit(0)
    for sym in ("SPX500", "NAS100", "US2000"):
        d = build(sym)
        if len(d):
            print(sym, len(d), d["open_time"].min(), "->", d["open_time"].max())
