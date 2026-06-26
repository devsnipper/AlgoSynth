"""
Test complet : ouverture + surveillance + fermeture
Verifie que l'ordre est accepte par MT5 et que orders.csv est mis a jour
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import MetaTrader5 as mt5
from dotenv import load_dotenv
from trader import open_trade, monitor_trade, ORDER_LOG, LOG_FILE
import csv

load_dotenv()

SYMBOL    = "Boom 1000 Index.0"
DIRECTION = "sell"


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


def count_lines(filepath):
    if not os.path.exists(filepath):
        return 0
    with open(filepath, "r") as f:
        return sum(1 for _ in csv.reader(f)) - 1


def run():
    print("=" * 55)
    print("TEST : ouverture + fermeture + logs")
    print("=" * 55)

    if not connect():
        return

    trades_avant  = count_lines(LOG_FILE)
    orders_avant  = count_lines(ORDER_LOG) if os.path.exists(ORDER_LOG) else 0
    print(f"[TEST] trades.csv avant  : {trades_avant} lignes")
    print(f"[TEST] orders.csv avant  : {orders_avant} lignes")

    # Ouverture
    tick        = mt5.symbol_info_tick(SYMBOL)
    entry_price = tick.bid if DIRECTION == "sell" else tick.ask
    print(f"\n[TEST] Ouverture {DIRECTION.upper()} {SYMBOL} @ {entry_price:.3f}")
    ticket = open_trade(SYMBOL, DIRECTION)

    if ticket is None:
        print("[TEST] ECHEC — ouverture refusee par MT5")
        mt5.shutdown()
        return

    print(f"[TEST] Ouverture OK | ticket={ticket}")
    print(f"[TEST] Surveillance en cours — attends TP ou SL...")
    print(f"[TEST] (tu peux aussi fermer manuellement dans MT5)\n")

    profit = monitor_trade(SYMBOL, ticket, entry_price, DIRECTION)

    trades_apres = count_lines(LOG_FILE)
    orders_apres = count_lines(ORDER_LOG) if os.path.exists(ORDER_LOG) else 0

    print(f"\n[TEST] trades.csv apres  : {trades_apres} lignes")
    print(f"[TEST] orders.csv apres  : {orders_apres} lignes")
    print()

    ok_trades = trades_apres > trades_avant
    ok_orders = orders_apres > orders_avant

    print(f"[TEST] trades.csv mis a jour : {'OK' if ok_trades else 'ECHEC'}")
    print(f"[TEST] orders.csv mis a jour : {'OK' if ok_orders else 'ECHEC'}")

    if profit is not None:
        print(f"[TEST] Profit trade      : {profit:.2f} USD")

    if ok_trades and ok_orders:
        print("\n[TEST] SUCCES — tout fonctionne correctement")
    else:
        print("\n[TEST] PROBLEME — verifie les logs")

    mt5.shutdown()


if __name__ == "__main__":
    run()
