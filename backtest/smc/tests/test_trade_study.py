"""Tests of the exploratory trade design (core/trade_study.py).

Usage : backtest/.venv/Scripts/python.exe backtest/smc/tests/test_trade_study.py
"""
import os
import sys
import traceback

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))                      # backtest/smc

from core import trade_study as ts                                 # noqa: E402
from core.testkit import T0, synthetic_context                     # noqa: E402

RESULTS = []


def check(name):
    def deco(fn):
        try:
            fn()
            RESULTS.append((name, True, ""))
        except Exception as e:  # noqa: BLE001
            RESULTS.append((name, False, f"{type(e).__name__}: {e}\n{traceback.format_exc(limit=2)}"))
        return fn
    return deco


def _m5(n_m15):
    """M5 candles covering the same period; the open of the M5 candle at time x is 100 + x in hours."""
    n = n_m15 * 3
    times = [T0 + pd.Timedelta(minutes=5 * i) for i in range(n)]
    price = [100 + i * 5 / 60 for i in range(n)]
    return pd.DataFrame({"time": times, "open": price, "high": price, "low": price, "close": price, "spread": 4})


@check("orders: entry at the next M5 open (ask for buys, bid for sells); stop 2 ATR away")
def _():
    ctx = synthetic_context([1.0] * 30, [1.1] * 30, [0.9] * 30, [1.0] * 30, atr=1.5)
    m5 = _m5(30)
    t = np.array([10])
    # the signal at the close of M15 candle 10 happens at T0 + 165 min = M5 candle 33
    buy = ts.make_orders(ctx, m5, t, np.array([1])).iloc[0]
    sell = ts.make_orders(ctx, m5, t, np.array([-1])).iloc[0]
    px = m5["open"].iloc[33]
    assert buy.signal_time == T0 + pd.Timedelta(minutes=165)
    assert abs(buy.entry - (px + 4 * ctx.point)) < 1e-9 and abs(buy.stop - (buy.entry - 3.0)) < 1e-9, buy.to_dict()
    assert abs(sell.entry - px) < 1e-9 and abs(sell.stop - (sell.entry + 3.0)) < 1e-9, sell.to_dict()


@check("orders after the last M5 candle are dropped")
def _():
    ctx = synthetic_context([1.0] * 30, [1.1] * 30, [0.9] * 30, [1.0] * 30)
    m5 = _m5(30).iloc[:50]
    assert ts.make_orders(ctx, m5, np.array([29]), np.array([1])).empty


@check("summary: win rate, profit factor and average R from known trades")
def _():
    tr = pd.DataFrame({"r": [2.0, -1.0, -1.5, 2.0], "r_level": [2.0, -1.0, -1.0, 2.0],
                       "reason": ["TP", "SL", "SL", "TP"]})
    s = ts.summarize(tr)
    assert s["trades"] == 4 and s["win_pct"] == 50 and s["stop_pct"] == 50
    assert abs(s["avg_R"] - 0.375) < 1e-9 and abs(s["profit_factor"] - 4.0 / 2.5) < 1e-9, s
    assert s["worst_R"] == -1.5


if __name__ == "__main__":
    for name, ok, msg in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"\n      {msg}" if msg else ""))
    sys.exit(0 if all(ok for _, ok, _ in RESULTS) else 1)
