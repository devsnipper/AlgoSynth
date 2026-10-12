import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))        # backtest/smc

from core.testkit import has_event, synthetic_context      # noqa: E402
from setups.s01_equal_hl_sweep.setup import SETUP          # noqa: E402

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


def _series(second_peak):
    # swing high 10.0 at idx 3, a second swing high at idx 8, then a sweep candle at idx 12 (high 10.4, close 9.5)
    H = [6, 7, 8, 10.0, 8, 7, 8, 9, second_peak, 8, 7, 7.5, 10.4]
    Lw = [h - 1.0 for h in H]
    C = [h - 0.5 for h in H]
    O = list(C)
    O[12], Lw[12], C[12] = 9.0, 8.8, 9.5
    return O, H, Lw, C


@check("two equal highs form a pool; the wick above it that closes back inside is a short sweep")
def _():
    ev = SETUP.detect(synthetic_context(*_series(9.95), L=2))      # 9.95 is within 0.15 ATR of 10.0
    assert has_event(ev, 12, -1), ev
    assert not has_event(ev, 12, 1)


@check("highs that are NOT equal (0.5 apart) form no pool: no event")
def _():
    ev = SETUP.detect(synthetic_context(*_series(9.5), L=2))
    assert not has_event(ev, 12, -1), ev


if __name__ == "__main__":
    for name, ok, msg in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"\n      {msg}" if msg else ""))
    sys.exit(0 if all(ok for _, ok, _ in RESULTS) else 1)
