"""Read-only download of the last ~70 days of M1 candles (99,999 bars) for the spike-free instruments.
Same window as the first backtest (backtesting_1), whose M1 data also stopped at the terminal's 100,000-bar limit.

Usage : backtest/.venv/Scripts/python.exe backtest/backtesting_2/download_m1.py
"""
import json
import os
import sys

import MetaTrader5 as mt5
import pandas as pd
from dotenv import load_dotenv

HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(HERE, "..", "..", ".env"))               # repo root, read only

DATA_DIR = os.path.join(HERE, "data")
SMC_INFO = os.path.join(HERE, "..", "smc", "data", "symbol_info.json")


def main():
    info = json.load(open(SMC_INFO))
    symbols = [s for s, v in info.items() if v.get("group") == "spikefree"]
    if not mt5.initialize(login=int(os.getenv("MT5_LOGIN")), password=os.getenv("MT5_PASSWORD"),
                          server=os.getenv("MT5_SERVER")):
        print("initialize() failed:", mt5.last_error())
        sys.exit(1)
    os.makedirs(DATA_DIR, exist_ok=True)
    rows = []
    for s in symbols:
        mt5.symbol_select(s, True)
        rates = mt5.copy_rates_from_pos(s, mt5.TIMEFRAME_M1, 0, 99999)
        if rates is None or len(rates) == 0:
            print(s, "no data")
            continue
        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        df = df.drop_duplicates("time").sort_values("time").reset_index(drop=True)
        df.to_csv(os.path.join(DATA_DIR, f"{s.replace(' ', '_')}_M1.csv"), index=False)
        rows.append({"symbol": s, "bars": len(df), "from": df.time.iloc[0], "to": df.time.iloc[-1]})
        print(s, "done", flush=True)
    mt5.shutdown()
    pd.set_option("display.width", 200)
    print("\n" + pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
