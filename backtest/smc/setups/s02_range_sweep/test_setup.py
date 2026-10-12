import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))        # backtest/smc

from core.testkit import has_event, synthetic_context      # noqa: E402
from setups.s02_range_sweep.setup import SETUP             # noqa: E402

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


def _flat(n):
    return [5.0] * n, [5.5] * n, [4.5] * n, [5.0] * n


@check("wick above the 20-candle high that closes back inside = short; wick below the low = long")
def _():
    o, h, l, c = _flat(25)
    for cand in [(5, 6.5, 4.8, 5.2),      # idx 25: high 6.5 > 5.5, close 5.2 < 5.5   -> short
                 (5, 7.0, 5.0, 7.2),      # idx 26: breaks above and CLOSES above    -> nothing
                 (5, 5.2, 4.0, 5.0)]:     # idx 27: low 4.0 < 4.5, close 5.0 > 4.5   -> long
        o.append(cand[0]); h.append(cand[1]); l.append(cand[2]); c.append(cand[3])
    ev = SETUP.detect(synthetic_context(o, h, l, c))
    assert has_event(ev, 25, -1) and has_event(ev, 27, 1) and len(ev) == 2, ev


@check("the first 20 candles produce nothing (no range yet)")
def _():
    o, h, l, c = _flat(19)
    o.append(5); h.append(9); l.append(4); c.append(5)
    assert SETUP.detect(synthetic_context(o, h, l, c)).empty


if __name__ == "__main__":
    for name, ok, msg in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"\n      {msg}" if msg else ""))
    sys.exit(0 if all(ok for _, ok, _ in RESULTS) else 1)
