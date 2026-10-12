import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))                          # backtest/smc

from core.testkit import has_event, synthetic_context                        # noqa: E402
from setups.s04_accumulate_manipulate_distribute.setup import SETUP          # noqa: E402

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


def _range(n=12):
    return [10.0] * n, [10.5] * n, [9.5] * n, [10.0] * n


@check("12 tight candles, wick above the range that closes back inside: short")
def _():
    o, h, l, c = _range()
    o.append(10); h.append(11.2); l.append(9.8); c.append(10.2)
    ev = SETUP.detect(synthetic_context(o, h, l, c))
    assert has_event(ev, 12, -1) and len(ev) == 1, ev


@check("wick below the range that closes back inside: long")
def _():
    o, h, l, c = _range()
    o.append(10); h.append(10.2); l.append(8.8); c.append(9.8)
    assert has_event(SETUP.detect(synthetic_context(o, h, l, c)), 12, 1)


@check("closing beyond the range is a breakout, not a manipulation")
def _():
    o, h, l, c = _range()
    o.append(10); h.append(11.5); l.append(9.9); c.append(11.2)
    assert SETUP.detect(synthetic_context(o, h, l, c)).empty


@check("a range wider than 3 ATR does not count")
def _():
    o, h, l, c = _range()
    h[5], l[5] = 13.0, 9.5                                            # width 3.5 > 3 ATR
    o.append(10); h.append(13.8); l.append(9.8); c.append(10.2)
    assert SETUP.detect(synthetic_context(o, h, l, c)).empty


if __name__ == "__main__":
    for name, ok, msg in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"\n      {msg}" if msg else ""))
    sys.exit(0 if all(ok for _, ok, _ in RESULTS) else 1)
