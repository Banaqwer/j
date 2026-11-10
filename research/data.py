"""Consolidate the downloaded Binance Vision files into fast parquet tables.

Outputs (in data_research/):
  bars_<SYM>_1m.parquet   : open_time(UTC), open, high, low, close, volume, quote_volume, count,
                            taker_buy_volume, taker_buy_quote_volume, plus ct (America/Chicago) timestamp
  funding_<SYM>.parquet   : calc_time(UTC), rate
  metrics_<SYM>.parquet   : create_time(UTC), open_interest, oi_value, top_count_ls, top_sum_ls, count_ls, taker_ls_vol
Usage: python -m research.data
"""
from __future__ import annotations

import glob
import os
import zipfile
from io import BytesIO

import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data_research")
BIN = os.path.join(ROOT, "binance")
KCOLS = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume", "count",
         "taker_buy_volume", "taker_buy_quote_volume", "ignore"]


def _read_zip_csv(path: str, names=None) -> pd.DataFrame:
    with zipfile.ZipFile(path) as z:
        raw = z.read(z.namelist()[0])
    head = raw[:200].decode(errors="ignore")
    has_header = not head[:1].isdigit()
    return pd.read_csv(BytesIO(raw), header=0 if has_header else None, names=None if has_header else names)


def build_bars(sym: str) -> pd.DataFrame:
    files = sorted(glob.glob(os.path.join(BIN, "klines", f"{sym}-1m-*.zip")))
    parts = []
    for f in files:
        df = _read_zip_csv(f, KCOLS)
        df.columns = KCOLS[:len(df.columns)]
        parts.append(df)
    df = pd.concat(parts, ignore_index=True)
    df = df[["open_time", "open", "high", "low", "close", "volume", "quote_volume", "count",
             "taker_buy_volume", "taker_buy_quote_volume"]].copy()
    for c in df.columns[1:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    # open_time: ms (or us in newer files)
    ot = df["open_time"].astype("int64")
    unit = "us" if ot.iloc[-1] > 10**14 else "ms"
    df["open_time"] = pd.to_datetime(ot, unit=unit, utc=True)
    df = df.drop_duplicates("open_time").sort_values("open_time").reset_index(drop=True)
    df["ct"] = df["open_time"].dt.tz_convert("America/Chicago")
    df.to_parquet(os.path.join(ROOT, f"bars_{sym}_1m.parquet"))
    return df


def build_funding(sym: str) -> pd.DataFrame:
    files = sorted(glob.glob(os.path.join(BIN, "funding", f"{sym}-fundingRate-*.zip")))
    parts = [_read_zip_csv(f, ["calc_time", "funding_interval_hours", "last_funding_rate"]) for f in files]
    df = pd.concat(parts, ignore_index=True)
    df.columns = [c.strip() for c in df.columns]
    ct = df["calc_time"].astype("int64")
    unit = "us" if ct.iloc[-1] > 10**14 else "ms"
    df["calc_time"] = pd.to_datetime(ct, unit=unit, utc=True)
    df = df.rename(columns={"last_funding_rate": "rate"})[["calc_time", "rate"]]
    df["rate"] = pd.to_numeric(df["rate"], errors="coerce")
    df = df.drop_duplicates("calc_time").sort_values("calc_time").reset_index(drop=True)
    df.to_parquet(os.path.join(ROOT, f"funding_{sym}.parquet"))
    return df


def build_metrics(sym: str) -> pd.DataFrame:
    files = sorted(glob.glob(os.path.join(BIN, "metrics", f"{sym}-metrics-*.zip")))
    parts = []
    for f in files:
        try:
            parts.append(_read_zip_csv(f))
        except Exception:
            continue
    if not parts:
        return pd.DataFrame()
    df = pd.concat(parts, ignore_index=True)
    df = df.rename(columns={"sum_open_interest": "open_interest", "sum_open_interest_value": "oi_value",
                            "count_toptrader_long_short_ratio": "top_count_ls", "sum_toptrader_long_short_ratio": "top_sum_ls",
                            "count_long_short_ratio": "count_ls", "sum_taker_long_short_vol_ratio": "taker_ls_vol"})
    df["create_time"] = pd.to_datetime(df["create_time"], utc=True)
    df = df[["create_time", "open_interest", "oi_value", "top_count_ls", "top_sum_ls", "count_ls", "taker_ls_vol"]]
    for c in df.columns[1:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.drop_duplicates("create_time").sort_values("create_time").reset_index(drop=True)
    df.to_parquet(os.path.join(ROOT, f"metrics_{sym}.parquet"))
    return df


def load_bars(sym: str = "BTCUSDT", freq: str = "1m", root: str = ROOT) -> pd.DataFrame:
    """root: data_research (full), data_research/IS (in-sample only), data_research/HO (holdout only)."""
    df = pd.read_parquet(os.path.join(root, f"bars_{sym}_1m.parquet"))
    if freq == "1m":
        return df
    g = df.set_index("open_time").resample(freq, label="left", closed="left")
    out = pd.DataFrame({"open": g["open"].first(), "high": g["high"].max(), "low": g["low"].min(),
                        "close": g["close"].last(), "volume": g["volume"].sum(), "quote_volume": g["quote_volume"].sum(),
                        "count": g["count"].sum(), "taker_buy_volume": g["taker_buy_volume"].sum(),
                        "taker_buy_quote_volume": g["taker_buy_quote_volume"].sum()}).dropna(subset=["open"]).reset_index()
    out["ct"] = out["open_time"].dt.tz_convert("America/Chicago")
    return out


def load_funding(sym: str = "BTCUSDT", root: str = ROOT) -> pd.DataFrame:
    return pd.read_parquet(os.path.join(root, f"funding_{sym}.parquet"))


def load_metrics(sym: str = "BTCUSDT", root: str = ROOT) -> pd.DataFrame:
    return pd.read_parquet(os.path.join(root, f"metrics_{sym}.parquet"))


IS_ROOT = os.path.join(ROOT, "IS")
HO_ROOT = os.path.join(ROOT, "HO")


def build_splits():
    """Write in-sample (<= 2024-06-30) and holdout (>= 2024-07-01) copies of every table."""
    from .protocol import IS_END, HO_START
    os.makedirs(IS_ROOT, exist_ok=True)
    os.makedirs(HO_ROOT, exist_ok=True)
    for sym in ("BTCUSDT", "ETHUSDT"):
        for kind, col in (("bars_%s_1m", "open_time"), ("funding_%s", "calc_time"), ("metrics_%s", "create_time")):
            path = os.path.join(ROOT, (kind % sym) + ".parquet")
            if not os.path.exists(path):
                continue
            df = pd.read_parquet(path)
            df[df[col] <= IS_END].to_parquet(os.path.join(IS_ROOT, (kind % sym) + ".parquet"))
            df[df[col] >= HO_START].to_parquet(os.path.join(HO_ROOT, (kind % sym) + ".parquet"))
            print("split", kind % sym, "IS", int((df[col] <= IS_END).sum()), "HO", int((df[col] >= HO_START).sum()))


if __name__ == "__main__":
    import sys
    if "--split" in sys.argv:
        build_splits()
        sys.exit(0)
    for sym in ("BTCUSDT", "ETHUSDT"):
        b = build_bars(sym)
        print(sym, "bars", len(b), b["open_time"].min(), "->", b["open_time"].max())
        f = build_funding(sym)
        print(sym, "funding", len(f), f["calc_time"].min(), "->", f["calc_time"].max())
        m = build_metrics(sym)
        print(sym, "metrics", len(m), (m["create_time"].min(), m["create_time"].max()) if len(m) else "none")
