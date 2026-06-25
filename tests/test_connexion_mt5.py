import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import MetaTrader5 as mt5
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

LOGIN    = os.getenv("MT5_LOGIN")
PASSWORD = os.getenv("MT5_PASSWORD")
SERVER   = os.getenv("MT5_SERVER")

print("=== BLOC 1 â€” Connexion MT5 ===\n")

# Verification .env
if not LOGIN or not PASSWORD or not SERVER:
    print("ERREUR : variables MT5 manquantes dans .env")
    print(f"  MT5_LOGIN    = {LOGIN}")
    print(f"  MT5_PASSWORD = {'OK' if PASSWORD else 'MANQUANT'}")
    print(f"  MT5_SERVER   = {SERVER}")
    exit(1)

# Initialisation
if not mt5.initialize():
    print(f"ERREUR initialize() : {mt5.last_error()}")
    exit(1)
print("MT5 initialise avec succes")

# Connexion
authorized = mt5.login(int(LOGIN), password=PASSWORD, server=SERVER)
if not authorized:
    print(f"ERREUR login() : {mt5.last_error()}")
    mt5.shutdown()
    exit(1)

print("Connexion reussie\n")
info = mt5.account_info()
print(f"Compte    : {info.login}")
print(f"Serveur   : {info.server}")
print(f"Balance   : {info.balance} {info.currency}")
print(f"Equity    : {info.equity} {info.currency}")
print(f"Profit    : {info.profit} {info.currency}")
print(f"Levier    : 1:{info.leverage}")
print(f"Mode      : {'DEMO' if info.trade_mode == 0 else 'REEL'}")

mt5.shutdown()
print("\nMT5 deconnecte proprement")
