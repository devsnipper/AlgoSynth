import json
import os
import sys
from datetime import datetime, timezone, timedelta

import MetaTrader5 as mt5
import pandas as pd
from dotenv import load_dotenv

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, ROOT)
load_dotenv(os.path.join(ROOT, ".env"))

from config import SYMBOLS

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
TIMEFRAMES = {
    "M1":  mt5.TIMEFRAME_M1,
    "M5":  mt5.TIMEFRAME_M5,
    "M15": mt5.TIMEFRAME_M15,
}
DAYS_BACK = 90


def download(symbol: str, tf_name: str, tf: int, start: datetime, end: datetime):
    # Par morceaux de 15 jours : une seule grosse requete M1 est refusee par MT5
    parts, cur = [], start
    while cur < end:
        nxt = min(cur + timedelta(days=15), end)
        rates = mt5.copy_rates_range(symbol, tf, cur, nxt)
        if rates is not None and len(rates) > 0:
            parts.append(pd.DataFrame(rates))
        cur = nxt
    if not parts:
        print(f"  {tf_name:<4} aucune donnee ({mt5.last_error()})")
        return
    df = pd.concat(parts).drop_duplicates("time").sort_values("time").reset_index(drop=True)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    name = symbol.replace(" ", "_")
    df.to_csv(os.path.join(DATA_DIR, f"{name}_{tf_name}.csv"), index=False)
    print(f"  {tf_name:<4} {len(df):>7} bougies | {df['time'].iloc[0]} -> {df['time'].iloc[-1]}")


def main():
    if not mt5.initialize(
        login=int(os.getenv("MT5_LOGIN")),
        password=os.getenv("MT5_PASSWORD"),
        server=os.getenv("MT5_SERVER"),
    ):
        print(f"initialize() echoue : {mt5.last_error()}")
        return

    os.makedirs(DATA_DIR, exist_ok=True)
    end   = datetime.now(timezone.utc)
    start = end - timedelta(days=DAYS_BACK)

    sym_info = {}
    for symbol in SYMBOLS.values():
        print(symbol)
        mt5.symbol_select(symbol, True)
        for tf_name, tf in TIMEFRAMES.items():
            download(symbol, tf_name, tf, start, end)
        i = mt5.symbol_info(symbol)
        sym_info[symbol] = {
            "point": i.point, "digits": i.digits,
            "contract_size": i.trade_contract_size,
            "volume_min": i.volume_min, "volume_step": i.volume_step,
        }

    with open(os.path.join(DATA_DIR, "symbol_info.json"), "w") as f:
        json.dump(sym_info, f, indent=2)

    mt5.shutdown()


if __name__ == "__main__":
    main()
