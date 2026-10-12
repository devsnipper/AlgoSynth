import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))                 # backtest/smc

from core.testkit import has_event, synthetic_context               # noqa: E402
from setups.s03_sweep_displacement_fvg.setup import SETUP           # noqa: E402

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


def _base():
    o, h, l, c = [5.0] * 25, [5.5] * 25, [4.5] * 25, [5.0] * 25
    o.append(5); h.append(6.5); l.append(4.8); c.append(5.2)           # idx 25: short sweep of the range high
    return o, h, l, c


@check("sweep, then a big bearish candle that leaves a gap: event at the candle after it")
def _():
    o, h, l, c = _base()
    o.append(5.2); h.append(5.3); l.append(3.4); c.append(3.5)         # idx 26: body 1.7 >= 1.5 ATR
    o.append(3.5); h.append(4.6); l.append(3.0); c.append(3.6)         # idx 27: high 4.6 < low of idx 25 (4.8) -> bearish FVG
    ev = SETUP.detect(synthetic_context(o, h, l, c))
    assert has_event(ev, 27, -1), ev


@check("displacement body too small (1.2 ATR): no event")
def _():
    o, h, l, c = _base()
    o.append(5.2); h.append(5.3); l.append(3.9); c.append(4.0)         # body 1.2
    o.append(4.0); h.append(4.6); l.append(3.5); c.append(4.1)
    assert SETUP.detect(synthetic_context(o, h, l, c)).empty


@check("no gap (next candle overlaps): no event")
def _():
    o, h, l, c = _base()
    o.append(5.2); h.append(5.3); l.append(3.4); c.append(3.5)
    o.append(3.5); h.append(5.0); l.append(3.0); c.append(3.6)         # high 5.0 > low of idx 25 (4.8) -> no gap
    assert SETUP.detect(synthetic_context(o, h, l, c)).empty


if __name__ == "__main__":
    for name, ok, msg in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"\n      {msg}" if msg else ""))
    sys.exit(0 if all(ok for _, ok, _ in RESULTS) else 1)
