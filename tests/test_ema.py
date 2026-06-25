import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import MetaTrader5 as mt5
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

print("=== BLOC 3 â€” Calcul EMA 5 / 13 / 50 ===\n")

mt5.initialize()
mt5.login(int(os.getenv("MT5_LOGIN")), password=os.getenv("MT5_PASSWORD"), server=os.getenv("MT5_SERVER"))

SYMBOLS = ["Crash 1000 Index.0", "Boom 1000 Index.0"]

def get_candles(symbol, timeframe, nb=100):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 1, nb)
    if rates is None or len(rates) == 0:
        print(f"ERREUR candles {symbol}")
        return None
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    return df

def add_emas(df):
    df["ema5"]  = df["close"].ewm(span=5,  adjust=False).mean()
    df["ema13"] = df["close"].ewm(span=13, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    return df

for symbol in SYMBOLS:
    print(f"--- {symbol} ---")
    for tf_name, tf in [("M15", mt5.TIMEFRAME_M15), ("M1", mt5.TIMEFRAME_M1)]:
        df = get_candles(symbol, tf)
        if df is None:
            continue
        df = add_emas(df)
        last = df.iloc[-1]

        print(f"  {tf_name} â€” derniere candle fermee : {last['time']}")
        print(f"    Close : {last['close']:.3f}")
        print(f"    EMA5  : {last['ema5']:.3f}")
        print(f"    EMA13 : {last['ema13']:.3f}")
        print(f"    EMA50 : {last['ema50']:.3f}")

        # Lecture tendance
        if last["ema5"] > last["ema13"] > last["ema50"]:
            tendance = "HAUSSIERE (BUY possible)"
        elif last["ema5"] < last["ema13"] < last["ema50"]:
            tendance = "BAISSIERE (SELL possible)"
        else:
            tendance = "NEUTRE (pas de signal)"

        print(f"    Tendance {tf_name} : {tendance}")
        print()

mt5.shutdown()
print("MT5 deconnecte proprement")
