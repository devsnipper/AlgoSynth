import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import MetaTrader5 as mt5
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

print("=== BLOC 4 â€” Detection signal M15 + croisement M1 ===\n")

mt5.initialize()
mt5.login(int(os.getenv("MT5_LOGIN")), password=os.getenv("MT5_PASSWORD"), server=os.getenv("MT5_SERVER"))

SYMBOLS = {
    "Crash 1000 Index.0": "buy",
    "Boom 1000 Index.0":  "sell",
}

def get_candles(symbol, timeframe, nb=100):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 1, nb)
    if rates is None or len(rates) == 0:
        return None
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    df["ema5"]  = df["close"].ewm(span=5,  adjust=False).mean()
    df["ema13"] = df["close"].ewm(span=13, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    return df

def check_trend_m15(symbol):
    df = get_candles(symbol, mt5.TIMEFRAME_M15)
    if df is None:
        return None
    last = df.iloc[-1]
    if last["ema5"] > last["ema13"] > last["ema50"]:
        return "buy"
    if last["ema5"] < last["ema13"] < last["ema50"]:
        return "sell"
    return None

def check_signal_m1(symbol, direction):
    df = get_candles(symbol, mt5.TIMEFRAME_M1)
    if df is None or len(df) < 2:
        return False
    prev = df.iloc[-2]
    last = df.iloc[-1]
    price = last["close"]

    if direction == "buy":
        crossed_up  = prev["ema5"] <= prev["ema13"] and last["ema5"] > last["ema13"]
        above_slow  = price > last["ema50"]
        return crossed_up and above_slow

    if direction == "sell":
        crossed_down = prev["ema5"] >= prev["ema13"] and last["ema5"] < last["ema13"]
        below_slow   = price < last["ema50"]
        return crossed_down and below_slow

    return False

for symbol, expected_dir in SYMBOLS.items():
    print(f"--- {symbol} (direction attendue : {expected_dir.upper()}) ---")

    # Tendance M15
    trend = check_trend_m15(symbol)
    trend_ok = trend == expected_dir
    print(f"  Tendance M15   : {trend if trend else 'NEUTRE'} â€” {'OK' if trend_ok else 'PAS OK'}")

    # Signal M1 (teste dans les 2 sens pour debug)
    signal = check_signal_m1(symbol, expected_dir)
    print(f"  Croisement M1  : {'OUI' if signal else 'NON'}")

    # Conclusion
    if trend_ok and signal:
        print(f"  => SIGNAL VALIDE â€” entree {expected_dir.upper()} possible")
    elif trend_ok and not signal:
        print(f"  => Tendance OK mais pas de croisement M1 pour l instant")
    else:
        print(f"  => Pas de signal (tendance M15 non alignee)")
    print()

mt5.shutdown()
print("MT5 deconnecte proprement")
