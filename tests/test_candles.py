import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import MetaTrader5 as mt5
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

print("=== BLOC 2 â€” Candles M15 et M1 ===\n")

mt5.initialize()
mt5.login(int(os.getenv("MT5_LOGIN")), password=os.getenv("MT5_PASSWORD"), server=os.getenv("MT5_SERVER"))

SYMBOLS = {
    "Crash 1000 Index": mt5.TIMEFRAME_M15,
    "Boom 1000 Index":  mt5.TIMEFRAME_M15,
}

def get_candles(symbol, timeframe, nb=10):
    # index 1+ = candles fermees uniquement
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 1, nb)
    if rates is None or len(rates) == 0:
        print(f"ERREUR : impossible de recuperer les candles pour {symbol}")
        print(f"  last_error = {mt5.last_error()}")
        return None
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    return df

for symbol in ["Crash 1000 Index.0", "Boom 1000 Index.0"]:
    print(f"--- {symbol} ---")

    for tf_name, tf in [("M15", mt5.TIMEFRAME_M15), ("M1", mt5.TIMEFRAME_M1)]:
        df = get_candles(symbol, tf, nb=5)
        if df is not None:
            print(f"  {tf_name} ({len(df)} candles fermees) :")
            print(df[["time", "open", "high", "low", "close"]].to_string(index=False))
        print()

mt5.shutdown()
print("MT5 deconnecte proprement")
