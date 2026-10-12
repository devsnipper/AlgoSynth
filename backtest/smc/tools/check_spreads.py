"""Read-only check of the trading costs of the spike-free instruments (and Boom/Crash for comparison).

For each symbol: the spread and the stops level, in price units and as a share of a typical M15 move (ATR).
A trade pays the spread once at entry; the stop must also respect the stops level. A symbol is only worth
testing if the spread is small next to the ATR.

Usage : backtest/.venv/Scripts/python.exe backtest/smc/tools/check_spreads.py
"""
import os
import sys

import MetaTrader5 as mt5
import numpy as np
import pandas as pd
from dotenv import load_dotenv

HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(HERE, "..", "..", "..", ".env"))          # repo root, read only
sys.path.insert(0, os.path.join(HERE, ".."))
from core import primitives as sc                                    # noqa: E402

FAMILIES = ("Step", "Range Break", "Volatility", "Jump", "DEX", "Drift", "Skew", "Multi Step", "Spot Up",
            "Ladder", "Boom", "Crash")
BARS = 3000                                                          # about one month of M15


def main():
    if not mt5.initialize(login=int(os.getenv("MT5_LOGIN")), password=os.getenv("MT5_PASSWORD"),
                          server=os.getenv("MT5_SERVER")):
        print("initialize() failed:", mt5.last_error())
        sys.exit(1)
    rows = []
    for s in mt5.symbols_get():
        if not any(s.name.startswith(f) or f in s.name for f in FAMILIES):
            continue
        mt5.symbol_select(s.name, True)
        rates = mt5.copy_rates_from_pos(s.name, mt5.TIMEFRAME_M15, 0, BARS)
        if rates is None or len(rates) < 200:
            rows.append({"symbol": s.name, "note": "no data"})
            continue
        df = pd.DataFrame(rates)
        atr = np.nanmedian(sc.atr(df["high"].to_numpy(float), df["low"].to_numpy(float), df["close"].to_numpy(float)))
        sp_px = df["spread"].to_numpy(float) * s.point
        price = float(df["close"].median())
        rows.append({
            "symbol": s.name, "price": price, "point": s.point,
            "spread_med_pts": float(np.median(df["spread"])), "spread_p90_pts": float(np.percentile(df["spread"], 90)),
            "spread_px": float(np.median(sp_px)), "atr_px": atr,
            "spread_pct_atr": 100 * float(np.median(sp_px)) / atr if atr > 0 else np.nan,
            "stops_px": s.trade_stops_level * s.point,
            "stops_pct_atr": 100 * s.trade_stops_level * s.point / atr if atr > 0 else np.nan,
            "min_lot": s.volume_min, "tradable": s.trade_mode == mt5.SYMBOL_TRADE_MODE_FULL,
            "candles": len(df), "note": ""})
    mt5.shutdown()
    out = pd.DataFrame(rows).sort_values("spread_pct_atr")
    folder = os.path.join(HERE, "..", "reports")
    os.makedirs(folder, exist_ok=True)
    out.to_csv(os.path.join(folder, "spreads.csv"), index=False)
    pd.set_option("display.width", 250)
    pd.set_option("display.max_rows", 200)
    cols = ["symbol", "price", "spread_med_pts", "spread_px", "atr_px", "spread_pct_atr", "stops_pct_atr", "min_lot", "tradable"]
    print(out[cols].round(4).to_string(index=False))


if __name__ == "__main__":
    main()
