"""Shared helpers for the tests of techniques/ and smc_live/."""
import json
import os
import sys

import pandas as pd

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

DATA = os.path.join(ROOT, "backtest", "smc", "data")      # price files written by the backtest download tool (read only)
RESULTS = []


def check(name):
    """Decorator: run the test function at once and record PASS/FAIL (the same style as the backtest tests)."""
    def deco(fn):
        import traceback
        try:
            msg = fn()
            RESULTS.append((name, True, msg or ""))
        except Exception as e:  # noqa: BLE001
            RESULTS.append((name, False, f"{type(e).__name__}: {e}\n{traceback.format_exc(limit=3)}"))
        return fn
    return deco


def report_and_exit():
    for name, ok, msg in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"\n      {msg}" if msg else ""))
    sys.exit(0 if all(ok for _, ok, _ in RESULTS) else 1)


def have_data(symbol: str) -> bool:
    return os.path.exists(os.path.join(DATA, f"{symbol.replace(' ', '_')}_H4.csv"))


def real_snapshot(symbol: str, last_n: int = None, first_n: int = None):
    """A Snapshot from the downloaded history. last_n keeps the most recent candles, first_n the oldest.
    Higher-timeframe candles that had not closed by the last M15 close are dropped, like in live use."""
    from techniques.base import Snapshot
    info = json.load(open(os.path.join(DATA, "symbol_info.json")))[symbol]
    rd = lambda tf: pd.read_csv(os.path.join(DATA, f"{symbol.replace(' ', '_')}_{tf}.csv"), parse_dates=["time"])
    m15, h1, h4 = rd("M15"), rd("H1"), rd("H4")
    if first_n:
        m15 = m15.iloc[:first_n]
    if last_n:
        m15 = m15.iloc[-last_n:]
    m15 = m15.reset_index(drop=True)
    last_close = m15["time"].iloc[-1] + pd.Timedelta(minutes=15)
    h1 = h1[h1["time"] + pd.Timedelta(hours=1) <= last_close].reset_index(drop=True)
    h4 = h4[h4["time"] + pd.Timedelta(hours=4) <= last_close].reset_index(drop=True)
    return Snapshot(symbol, info["point"], info["stops_level"], m15, h1, h4)
