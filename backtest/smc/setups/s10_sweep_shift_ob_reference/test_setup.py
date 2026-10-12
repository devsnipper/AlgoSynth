import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))                 # backtest/smc

from core.testkit import has_event, synthetic_context               # noqa: E402
from setups.s10_sweep_shift_ob_reference.setup import SETUP         # noqa: E402

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


# Same series as the primitives test: padding, swing high 15, swing low 6, sweep at idx 11, shift at idx 14.
O = [27, 26, 25] + [10, 10, 11, 14, 12, 10, 7, 8, 9, 8, 10, 12]
H = [30, 29, 28] + [11, 12, 15, 14, 13, 11, 9, 10, 10, 11, 13, 16]
L = [25, 24, 23] + [9, 10, 11, 11, 9, 6, 7, 8, 5, 7, 9, 11]
C = [27, 26, 25] + [10, 11, 14, 12, 10, 7, 8, 9, 8, 10, 12, 15.5]


@check("sweep of the swing low, then a close above the swing high: long event at the shift candle")
def _():
    ev = SETUP.detect(synthetic_context(O, H, L, C))
    assert has_event(ev, 14, 1), ev
    row = ev[ev.t == 14].iloc[0]
    assert row.entry == 7.5 and row.stop == 5.0, row.to_dict()


if __name__ == "__main__":
    for name, ok, msg in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"\n      {msg}" if msg else ""))
    sys.exit(0 if all(ok for _, ok, _ in RESULTS) else 1)
