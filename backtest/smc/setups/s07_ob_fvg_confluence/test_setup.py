import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))                 # backtest/smc

from core.testkit import has_event, synthetic_context               # noqa: E402
from setups.s07_ob_fvg_confluence.setup import SETUP                # noqa: E402

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


# Same order-block series as setup 5 (see its test): zone 5-10, touched at idx 15.
O = [27, 26, 25, 10, 10, 11, 14, 12, 10, 7, 8, 9, 8, 10, 12, 15]
H = [30, 29, 28, 11, 12, 15, 14, 13, 11, 9, 10, 10, 11, 13, 16, 15.2]
L = [25, 24, 23, 9, 10, 11, 11, 9, 6, 7, 8, 5, 7, 9, 11, 9.5]
C = [27, 26, 25, 10, 11, 14, 12, 10, 7, 8, 9, 8, 10, 12, 15.5, 14]


@check("the leg contains a bullish fair value gap: event")
def _():
    low = list(L)
    low[14] = 11.5                                                    # high of idx 12 (11) < low of idx 14 -> gap around idx 13
    assert has_event(SETUP.detect(synthetic_context(O, H, low, C)), 15, 1)


@check("same order block without a gap in the leg: no event")
def _():
    assert not has_event(SETUP.detect(synthetic_context(O, H, L, C)), 15, 1)


if __name__ == "__main__":
    for name, ok, msg in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"\n      {msg}" if msg else ""))
    sys.exit(0 if all(ok for _, ok, _ in RESULTS) else 1)
