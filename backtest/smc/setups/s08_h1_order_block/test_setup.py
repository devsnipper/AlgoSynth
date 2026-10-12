import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))                 # backtest/smc

from core.testkit import T0, has_event, synthetic_context           # noqa: E402
from setups.s08_h1_order_block.setup import SETUP                   # noqa: E402

RESULTS = []


def check(name):
    def deco(fn):
        try:
            fn()
            RESULTS.append((name, True, ""))
        except Exception as e:  # noqa: BLE001
            import traceback
            RESULTS.append((name, False, f"{type(e).__name__}: {e}\n{traceback.format_exc(limit=2)}"))
        return fn
    return deco


# The H1 candles are the order-block series of setup 5: the break candle is H1 idx 14, which closes at hour 15.
O = [27, 26, 25, 10, 10, 11, 14, 12, 10, 7, 8, 9, 8, 10, 12, 15]
H = [30, 29, 28, 11, 12, 15, 14, 13, 11, 9, 10, 10, 11, 13, 16, 15.2]
L = [25, 24, 23, 9, 10, 11, 11, 9, 6, 7, 8, 5, 7, 9, 11, 9.5]
C = [27, 26, 25, 10, 11, 14, 12, 10, 7, 8, 9, 8, 10, 12, 15.5, 14]


def _ctx(dip):
    """M15 candles sit above the H1 zone (5-10), except one candle that dips into it."""
    n15 = 70
    o = [15.5] * n15; h = [15.6] * n15; l = [15.4] * n15; c = [15.5] * n15
    if dip is not None:
        l[dip] = 9.5
    ctx = synthetic_context(o, h, l, c, L=2, Lh=2)
    ctx.h1 = pd.DataFrame({"time": [T0 + pd.Timedelta(hours=i) for i in range(len(C))],
                           "open": O, "high": H, "low": L, "close": C, "spread": 0})
    return ctx


@check("H1 break closes at hour 15; the first M15 candle that dips into the H1 zone is the event")
def _():
    ev = SETUP.detect(_ctx(dip=64))
    assert has_event(ev, 64, 1), ev


@check("a dip BEFORE the H1 break has closed does not count")
def _():
    ev = SETUP.detect(_ctx(dip=50))
    assert not has_event(ev, 50, 1), ev


@check("no dip into the zone: no long event")
def _():
    ev = SETUP.detect(_ctx(dip=None))
    assert not (ev["direction"] == 1).any(), ev


if __name__ == "__main__":
    for name, ok, msg in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"\n      {msg}" if msg else ""))
    sys.exit(0 if all(ok for _, ok, _ in RESULTS) else 1)
