"""Read-only: which kinds of markets does the account offer, and what do the main real markets cost?

Usage : backtest/.venv/Scripts/python.exe backtest/smc/tools/list_markets.py
"""
import collections
import os
import sys

import MetaTrader5 as mt5
from dotenv import load_dotenv

HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(HERE, "..", "..", "..", ".env"))          # repo root, read only

if not mt5.initialize(login=int(os.getenv("MT5_LOGIN")), password=os.getenv("MT5_PASSWORD"), server=os.getenv("MT5_SERVER")):
    print("initialize() failed:", mt5.last_error())
    sys.exit(1)

count, examples = collections.Counter(), collections.defaultdict(list)
for s in mt5.symbols_get():
    top = s.path.split("\\")[0] if s.path else "?"
    count[top] += 1
    if len(examples[top]) < 6:
        examples[top].append(s.name)
for k, v in count.most_common():
    print(f"{k:<24} {v:4d}  e.g. {', '.join(examples[k])}")

print()
for name in ("EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD", "ETHUSD", "US_500", "US500", "UK_100", "GER_40"):
    s = mt5.symbol_info(name)
    if s is None:
        continue
    mt5.symbol_select(name, True)
    rates = mt5.copy_rates_from_pos(name, mt5.TIMEFRAME_M15, 0, 50)
    print(f"{name:<8} spread={s.spread} points  point={s.point}  stops_level={s.trade_stops_level}  "
          f"tradable={s.trade_mode == mt5.SYMBOL_TRADE_MODE_FULL}  data_ok={rates is not None and len(rates) > 0}")
mt5.shutdown()
