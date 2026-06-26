"""
Test : le bot detecte une position fermee par MT5 (SL/fermeture manuelle)
et la logge correctement dans trades.csv.

Etapes :
1. Ouvre un BUY sur Boom 1000 (contre-tendance volontaire pour toucher SL vite)
2. Attend 5 secondes puis ferme manuellement la position depuis MT5
   OU attend que le SL soit touche naturellement
3. Verifie que la ligne apparait dans trades.csv
"""

import sys
import os
import csv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import MetaTrader5 as mt5
from dotenv import load_dotenv
from trader import monitor_trade, LOG_FILE
from config import LOT, MAGIC

load_dotenv()

SYMBOL    = "Boom 1000 Index.0"
DIRECTION = "buy"   # contre-tendance → SL probable rapidement
TP_PTS    = 500     # TP loin pour ne pas le toucher pendant le test
SL_PTS    = 30      # SL serré pour que MT5 le ferme vite


def connect():
    if not mt5.initialize():
        print(f"[TEST] initialize() echoue : {mt5.last_error()}")
        return False
    login    = int(os.getenv("MT5_LOGIN"))
    password = os.getenv("MT5_PASSWORD")
    server   = os.getenv("MT5_SERVER")
    if not mt5.login(login, password=password, server=server):
        print(f"[TEST] login() echoue : {mt5.last_error()}")
        mt5.shutdown()
        return False
    return True


def open_test_trade():
    tick = mt5.symbol_info_tick(SYMBOL)
    if tick is None:
        print("[TEST] Impossible de lire le tick")
        return None

    price = tick.ask
    point = mt5.symbol_info(SYMBOL).point

    request = {
        "action":       mt5.TRADE_ACTION_DEAL,
        "symbol":       SYMBOL,
        "volume":       LOT,
        "type":         mt5.ORDER_TYPE_BUY,
        "price":        price,
        "deviation":    10,
        "magic":        MAGIC,
        "comment":      "test-sl-detection",
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    result = mt5.order_send(request)
    if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
        code = result.retcode if result else "None"
        print(f"[TEST] Ordre refuse ({code})")
        return None

    print(f"[TEST] Trade ouvert | BUY {SYMBOL} @ {price} | ticket={result.order}")
    print(f"[TEST] SL={round(price - SL_PTS * point, 3)}  TP={round(price + TP_PTS * point, 3)}")
    return result.order, price


def count_csv_lines():
    if not os.path.exists(LOG_FILE):
        return 0
    with open(LOG_FILE, "r") as f:
        return sum(1 for _ in csv.reader(f)) - 1  # sans header


def run():
    print("=" * 50)
    print("TEST : detection SL ferme par MT5")
    print("=" * 50)

    if not connect():
        return

    lines_before = count_csv_lines()
    print(f"[TEST] Trades dans CSV avant : {lines_before}")

    result = open_test_trade()
    if result is None:
        mt5.shutdown()
        return

    ticket, entry_price = result

    print(f"\n[TEST] Surveillance du trade...")
    print(f"[TEST] Ferme manuellement la position dans MT5 pour simuler un SL,")
    print(f"       ou attends que le SL serré soit touché automatiquement.\n")

    profit = monitor_trade(SYMBOL, ticket, entry_price, DIRECTION)

    lines_after = count_csv_lines()
    print(f"\n[TEST] Trades dans CSV apres : {lines_after}")

    if lines_after > lines_before:
        print(f"[TEST] SUCCES — trade logge | profit={profit:.2f}")
    else:
        print(f"[TEST] ECHEC — aucune ligne ajoutee dans le CSV")

    mt5.shutdown()


if __name__ == "__main__":
    run()
