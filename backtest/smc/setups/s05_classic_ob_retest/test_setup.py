import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))                 # backtest/smc

from core.testkit import has_event, synthetic_context               # noqa: E402
from setups.s05_classic_ob_retest.setup import SETUP                # noqa: E402

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


# Series used for all order-block tests (swing length 2). Three padding candles come first because a swing needs
# 2L-1 candles of history. Swing high 15 at idx 5; pullback low 5 at idx 11; the close of idx 14 (15.5) breaks it.
# Order block = last bearish candle of the leg = idx 11 (zone 5-10). Idx 15 trades back into it.
O = [27, 26, 25, 10, 10, 11, 14, 12, 10, 7, 8, 9, 8, 10, 12, 15]
H = [30, 29, 28, 11, 12, 15, 14, 13, 11, 9, 10, 10, 11, 13, 16, 15.2]
L = [25, 24, 23, 9, 10, 11, 11, 9, 6, 7, 8, 5, 7, 9, 11, 9.5]
C = [27, 26, 25, 10, 11, 14, 12, 10, 7, 8, 9, 8, 10, 12, 15.5, 14]


@check("break of structure, then the first touch of the order block: long event at the touch candle")
def _():
    ev = SETUP.detect(synthetic_context(O, H, L, C))
    assert has_event(ev, 15, 1), ev
    row = ev[(ev.t == 15) & (ev.direction == 1)].iloc[0]
    assert row.zone_lo == 5 and row.zone_hi == 10, row.to_dict()      # the zone is candle 11


@check("no touch of the zone: no long event")
def _():
    l = list(L)
    l[15] = 12.0                                                      # stays above the zone
    assert not has_event(SETUP.detect(synthetic_context(O, H, l, C)), 15, 1)


if __name__ == "__main__":
    for name, ok, msg in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"\n      {msg}" if msg else ""))
    sys.exit(0 if all(ok for _, ok, _ in RESULTS) else 1)
