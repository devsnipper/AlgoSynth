import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import MetaTrader5 as mt5
import os
import time
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

print("=== BLOC 7 â€” Surveillance prix + fermeture TP/SL ===\n")

mt5.initialize()
mt5.login(int(os.getenv("MT5_LOGIN")), password=os.getenv("MT5_PASSWORD"), server=os.getenv("MT5_SERVER"))

SYMBOL     = "Crash 1000 Index.0"
MAGIC      = 123456
LOT        = 0.20
TP_POINTS  = 150
SL_POINTS  = 100

# Recuperer la position ouverte
positions = mt5.positions_get(symbol=SYMBOL)
if not positions or len(positions) == 0:
    print("Aucune position ouverte sur Crash 1000 Index.0")
    print("Lance d abord test_bloc6.py pour ouvrir un trade.")
    mt5.shutdown()
    exit(0)

pos        = positions[0]
ticket     = pos.ticket
direction  = "buy" if pos.type == 0 else "sell"
entry      = pos.price_open
point      = mt5.symbol_info(SYMBOL).point

tp_level = entry + TP_POINTS * point if direction == "buy" else entry - TP_POINTS * point
sl_level = entry - SL_POINTS * point if direction == "buy" else entry + SL_POINTS * point

print(f"Position active :")
print(f"  Ticket    : {ticket}")
print(f"  Direction : {direction.upper()}")
print(f"  Entree    : {entry:.3f}")
print(f"  TP niveau : {tp_level:.3f}  (+{TP_POINTS} pts)")
print(f"  SL niveau : {sl_level:.3f}  (-{SL_POINTS} pts)")
print(f"\nSurveillance en cours... (Ctrl+C pour arreter)\n")

def close_position(ticket, direction):
    tick = mt5.symbol_info_tick(SYMBOL)
    if tick is None:
        return None

    close_type  = mt5.ORDER_TYPE_SELL if direction == "buy" else mt5.ORDER_TYPE_BUY
    close_price = tick.bid            if direction == "buy" else tick.ask

    request = {
        "action":       mt5.TRADE_ACTION_DEAL,
        "symbol":       SYMBOL,
        "volume":       LOT,
        "type":         close_type,
        "position":     ticket,
        "price":        close_price,
        "deviation":    10,
        "magic":        MAGIC,
        "comment":      "deriv-scalper-close",
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    result = mt5.order_send(request)
    if result and result.retcode == mt5.TRADE_RETCODE_DONE:
        return result.price
    print(f"  ERREUR fermeture : retcode={result.retcode if result else 'None'}")
    return None

try:
    while True:
        positions = mt5.positions_get(symbol=SYMBOL)
        if not positions or not any(p.ticket == ticket for p in positions):
            print("Position introuvable â€” peut-etre fermee manuellement.")
            break

        tick  = mt5.symbol_info_tick(SYMBOL)
        price = tick.bid if direction == "buy" else tick.ask
        pos   = next(p for p in positions if p.ticket == ticket)
        profit = pos.profit

        print(f"  Prix={price:.3f}  TP={tp_level:.3f}  SL={sl_level:.3f}  Profit={profit:.2f}$", end="\r")

        hit_tp = price >= tp_level if direction == "buy" else price <= tp_level
        hit_sl = price <= sl_level if direction == "buy" else price >= sl_level

        if hit_tp:
            print(f"\n  TP ATTEINT @ {price:.3f} !")
            close_price = close_position(ticket, direction)
            if close_price:
                print(f"  Position fermee @ {close_price:.3f}")
                print(f"  Profit final    : {profit:.2f} USD")
            break

        if hit_sl:
            print(f"\n  SL ATTEINT @ {price:.3f} !")
            close_price = close_position(ticket, direction)
            if close_price:
                print(f"  Position fermee @ {close_price:.3f}")
                print(f"  Profit final    : {profit:.2f} USD")
            break

        time.sleep(0.5)

except KeyboardInterrupt:
    print(f"\n\nArret manuel â€” fermeture de la position...")
    close_price = close_position(ticket, direction)
    if close_price:
        print(f"Position fermee @ {close_price:.3f}")

mt5.shutdown()
print("\nMT5 deconnecte proprement")
