import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))                 # backtest/smc

from core.testkit import has_event, synthetic_context               # noqa: E402
from setups.s06_fvg_continuation.setup import SETUP                 # noqa: E402

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


def _series(touch_at):
    o, h, l, c = [10.0] * 10, [10.4] * 10, [9.6] * 10, [10.0] * 10
    o.append(10); h.append(12.1); l.append(9.9); c.append(12.0)         # idx 10: bullish displacement, body 2.0
    o.append(12); h.append(12.8); l.append(11.5); c.append(12.5)        # idx 11: low 11.5 > high of idx 9 (10.4): gap, top edge 11.5
    for m in range(12, 17):
        low = 11.4 if m == touch_at else 12.2
        o.append(12.5); h.append(13.0); l.append(low); c.append(12.8)
    return o, h, l, c


@check("price comes back into the gap after 2+ candles, with the H1 bias up: long")
def _():
    ev = SETUP.detect(synthetic_context(*_series(14), h1_dir=1))
    assert has_event(ev, 14, 1), ev


@check("same touch with the H1 bias down: no event (the bias is part of the definition)")
def _():
    assert SETUP.detect(synthetic_context(*_series(14), h1_dir=-1)).empty


@check("touch too early (first candle after the gap): the gap is cancelled")
def _():
    ev = SETUP.detect(synthetic_context(*_series(12), h1_dir=1))
    assert not has_event(ev, 12, 1) and not has_event(ev, 14, 1), ev


if __name__ == "__main__":
    for name, ok, msg in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"\n      {msg}" if msg else ""))
    sys.exit(0 if all(ok for _, ok, _ in RESULTS) else 1)
