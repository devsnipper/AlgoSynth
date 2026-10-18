"""Read-only: account facts that matter for running two systems side by side (margin mode, open positions, limits).

Usage : backtest/.venv/Scripts/python.exe backtest/smc/tools/check_account.py
"""
import os
import sys

import MetaTrader5 as mt5
from dotenv import load_dotenv

HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(HERE, "..", "..", "..", ".env"))          # repo root, read only

if not mt5.initialize(login=int(os.getenv("MT5_LOGIN")), password=os.getenv("MT5_PASSWORD"), server=os.getenv("MT5_SERVER")):
    print("initialize() failed:", mt5.last_error())
    sys.exit(1)

a = mt5.account_info()
modes = {mt5.ACCOUNT_MARGIN_MODE_RETAIL_NETTING: "NETTING (one position per symbol; opposite orders offset)",
         mt5.ACCOUNT_MARGIN_MODE_EXCHANGE: "EXCHANGE",
         mt5.ACCOUNT_MARGIN_MODE_RETAIL_HEDGING: "HEDGING (several positions per symbol allowed)"}
print("login", a.login, "| server", a.server, "| currency", a.currency, "| balance", a.balance, "| leverage 1:%d" % a.leverage)
print("margin mode :", modes.get(a.margin_mode, a.margin_mode))
print("trade allowed:", a.trade_allowed, "| expert trading allowed:", a.trade_expert, "| limit orders:", a.limit_orders)
pos = mt5.positions_get()
print("open positions now:", 0 if pos is None else len(pos))
for p in (pos or []):
    print("  ", p.symbol, "ticket", p.ticket, "magic", p.magic, "volume", p.volume, "sl", p.sl, "tp", p.tp, "comment", p.comment)
orders = mt5.orders_get()
print("pending orders now:", 0 if orders is None else len(orders))
t = mt5.terminal_info()
print("terminal: algo trading enabled:", t.trade_allowed, "| connected:", t.connected, "| community:", t.community_account)
print()
for name in ("Boom 500 Index", "Crash 500 Index", "Boom 150 Index"):
    s = mt5.symbol_info(name)
    print(f"{name:<16} filling_mode={s.filling_mode} order_mode={s.order_mode} stops_level={s.trade_stops_level} "
          f"freeze_level={s.trade_freeze_level} volume_min={s.volume_min} volume_step={s.volume_step} volume_max={s.volume_max}")
mt5.shutdown()
