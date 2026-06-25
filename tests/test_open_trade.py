import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import MetaTrader5 as mt5
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

print("=== BLOC 6 â€” Ouverture trade demo ===\n")

mt5.initialize()
mt5.login(int(os.getenv("MT5_LOGIN")), password=os.getenv("MT5_PASSWORD"), server=os.getenv("MT5_SERVER"))

SYMBOL    = "Crash 1000 Index.0"
LOT       = 0.20
MAGIC     = 123456
DIRECTION = "buy"  # on teste un BUY sur Crash

# Verifier qu il n y a pas deja une position ouverte
positions = mt5.positions_get(symbol=SYMBOL)
if positions and len(positions) > 0:
    print(f"Position deja ouverte sur {SYMBOL} (ticket={positions[0].ticket})")
    print("Ferme la position manuellement avant de relancer ce bloc.")
    mt5.shutdown()
    exit(0)

# Prix d entree
tick = mt5.symbol_info_tick(SYMBOL)
if tick is None:
    print(f"ERREUR : impossible de recuperer le tick pour {SYMBOL}")
    mt5.shutdown()
    exit(1)

price = tick.ask
print(f"Symbole    : {SYMBOL}")
print(f"Direction  : {DIRECTION.upper()}")
print(f"Prix ask   : {price:.3f}")
print(f"Lot        : {LOT}")
print()

# Construction de la requete (sans SL/TP â€” gere par Python)
request = {
    "action":       mt5.TRADE_ACTION_DEAL,
    "symbol":       SYMBOL,
    "volume":       LOT,
    "type":         mt5.ORDER_TYPE_BUY,
    "price":        price,
    "deviation":    10,
    "magic":        MAGIC,
    "comment":      "deriv-scalper-test",
    "type_filling": mt5.ORDER_FILLING_FOK,
}

print("Envoi de l ordre...")
result = mt5.order_send(request)

if result is None:
    print(f"ERREUR : order_send a retourne None")
    print(f"last_error = {mt5.last_error()}")
elif result.retcode != mt5.TRADE_RETCODE_DONE:
    print(f"ERREUR : ordre refuse")
    print(f"  retcode = {result.retcode}")
    print(f"  comment = {result.comment}")
else:
    print(f"Trade ouvert avec succes !")
    print(f"  Ticket  : {result.order}")
    print(f"  Prix    : {result.price}")
    print(f"  Volume  : {result.volume}")

    # Verifier la position dans MT5
    pos = mt5.positions_get(symbol=SYMBOL)
    if pos:
        p = pos[0]
        print(f"\nPosition confirmee dans MT5 :")
        print(f"  Ticket    : {p.ticket}")
        print(f"  Symbole   : {p.symbol}")
        print(f"  Type      : {'BUY' if p.type == 0 else 'SELL'}")
        print(f"  Volume    : {p.volume}")
        print(f"  Prix open : {p.price_open:.3f}")
        print(f"  Profit    : {p.profit:.2f} USD")

print("\nLa position reste ouverte pour le Bloc 7 (surveillance + fermeture).")

mt5.shutdown()
