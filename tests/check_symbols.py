import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import MetaTrader5 as mt5
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

mt5.initialize()
mt5.login(int(os.getenv("MT5_LOGIN")), password=os.getenv("MT5_PASSWORD"), server=os.getenv("MT5_SERVER"))

# Chercher tous les symboles contenant "crash" ou "boom"
all_symbols = mt5.symbols_get()
matches = [s.name for s in all_symbols if "crash" in s.name.lower() or "boom" in s.name.lower()]

print("Symboles Crash/Boom disponibles :")
for s in matches:
    print(f"  '{s}'")

mt5.shutdown()
