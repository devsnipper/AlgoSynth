import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import MetaTrader5 as mt5
import pandas as pd
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

mt5.initialize()
mt5.login(int(os.getenv("MT5_LOGIN")), password=os.getenv("MT5_PASSWORD"), server=os.getenv("MT5_SERVER"))

SYMBOLS = {
    "Crash 1000 Index.0": "buy",
    "Boom 1000 Index.0":  "sell",
}

print("=== STATUS BOT EN TEMPS REEL ===\n")

for symbol, direction in SYMBOLS.items():
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 1, 100)
    df = pd.DataFrame(rates)
    df["ema5"]  = df["close"].ewm(span=5,  adjust=False).mean()
    df["ema13"] = df["close"].ewm(span=13, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    last = df.iloc[-1]

    if last["ema5"] > last["ema13"] > last["ema50"]:
        trend = "HAUSSIERE"
    elif last["ema5"] < last["ema13"] < last["ema50"]:
        trend = "BAISSIERE"
    else:
        trend = "NEUTRE"

    match = "OK - SURVEILLE" if (direction == "buy" and trend == "HAUSSIERE") or (direction == "sell" and trend == "BAISSIERE") else "EN ATTENTE"

    print(f"{symbol}")
    print(f"  Direction attendue : {direction.upper()}")
    print(f"  Tendance M15       : {trend} — {match}")
    print(f"  EMA5  : {last['ema5']:.3f}")
    print(f"  EMA13 : {last['ema13']:.3f}")
    print(f"  EMA50 : {last['ema50']:.3f}")

    pos = mt5.positions_get(symbol=symbol)
    if pos and len(pos) > 0:
        p = pos[0]
        print(f"  Position ouverte : {'BUY' if p.type == 0 else 'SELL'} @ {p.price_open:.3f} | Profit={p.profit:.2f}$")
    else:
        print(f"  Position ouverte : Aucune")
    print()

mt5.shutdown()
