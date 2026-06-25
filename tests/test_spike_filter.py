import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import MetaTrader5 as mt5
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

print("=== BLOC 5 â€” Spike Filter ===\n")

mt5.initialize()
mt5.login(int(os.getenv("MT5_LOGIN")), password=os.getenv("MT5_PASSWORD"), server=os.getenv("MT5_SERVER"))

SYMBOLS = ["Crash 1000 Index.0", "Boom 1000 Index.0"]
SPIKE_THRESHOLD = 0.005  # 0.5%

def check_spike(symbol):
    from datetime import datetime, timezone, timedelta
    now   = datetime.now(timezone.utc)
    start = now - timedelta(seconds=10)
    ticks = mt5.copy_ticks_range(symbol, start, now, mt5.COPY_TICKS_ALL)
    if ticks is None or len(ticks) < 2:
        # Fallback : comparer bid actuel vs dernier close M1
        tick = mt5.symbol_info_tick(symbol)
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 1, 2)
        if tick is None or rates is None or len(rates) < 1:
            print(f"  ERREUR : donnees insuffisantes pour {symbol}")
            return None
        p1 = rates[-1]["close"]
        p2 = tick.ask
    else:
        p1 = ticks[-2]["ask"]
        p2 = ticks[-1]["ask"]

    if p1 == 0:
        print(f"  ERREUR : tick precedent = 0")
        return None

    variation = abs(p2 - p1) / p1
    is_spike  = variation > SPIKE_THRESHOLD

    return {
        "tick_prev": p1,
        "tick_last": p2,
        "variation": variation,
        "is_spike":  is_spike,
    }

for symbol in SYMBOLS:
    print(f"--- {symbol} ---")
    result = check_spike(symbol)
    if result:
        print(f"  Tick precedent : {result['tick_prev']:.3f}")
        print(f"  Tick actuel    : {result['tick_last']:.3f}")
        print(f"  Variation      : {result['variation']*100:.4f}%")
        print(f"  Seuil          : {SPIKE_THRESHOLD*100}%")
        if result["is_spike"]:
            print(f"  => SPIKE DETECTE â€” trade skippe")
        else:
            print(f"  => Pas de spike â€” entree autorisee")
    print()

mt5.shutdown()
print("MT5 deconnecte proprement")
