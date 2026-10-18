"""The live structure code must give exactly the same results as the backtest code it was ported from.

Usage : backtest/.venv/Scripts/python.exe smc_tests/test_structure_parity.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from helpers import ROOT, check, have_data, real_snapshot, report_and_exit      # noqa: E402

sys.path.insert(0, os.path.join(ROOT, "backtest", "smc"))                          # backtest code, read only
from core import orderblocks as bt_ob                                               # noqa: E402
from core import primitives as bt                                                   # noqa: E402
from techniques import structure as st                                              # noqa: E402

SYMBOLS = [s for s in ("Boom 500 Index", "Crash 500 Index") if have_data(s)]


def arrays(snap, tf="m15"):
    df = getattr(snap, tf).iloc[:20000]
    return [df[x].to_numpy(float) for x in ("open", "high", "low", "close")]


@check("raw swings, FVG flags and ATR are identical")
def _():
    for sym in SYMBOLS:
        o, h, l, c = arrays(real_snapshot(sym))
        for L in (3, 5):
            a, b = st.raw_swings(h, l, L), bt.raw_swings(h, l, L)
            assert all(np.array_equal(x, y) for x, y in zip(a, b)), (sym, L)
        a, b = st.fvg_flags(o, h, l, c), bt.fvg_flags(o, h, l, c)
        assert all(np.array_equal(x, y) for x, y in zip(a, b))
        assert np.allclose(st.atr(h, l, c), bt.atr(h, l, c), equal_nan=True)
        assert np.array_equal(st.spike_flags(h, l), bt.spike_flags(h, l))


@check("structure state machine is identical (direction, range, previous swings)")
def _():
    for sym in SYMBOLS:
        _, h, l, c = arrays(real_snapshot(sym))
        for L in (3, 5):
            a, b = st.structure(h, l, c, L), bt.structure(h, l, c, L)
            for key in a:
                assert np.allclose(a[key], b[key], equal_nan=True), (sym, L, key)


@check("order-block zones are identical")
def _():
    total = 0
    for sym in SYMBOLS:
        snap = real_snapshot(sym)
        for tf, L in (("m15", 5), ("h1", 3)):
            o, h, l, c = arrays(snap, tf)
            fb, fr = bt.fvg_flags(o, h, l, c)
            spike = bt.spike_flags(h, l)
            a = st.ob_zones(o, h, l, c, L, fb, fr, spike)
            b = bt_ob.ob_zones(o, h, l, c, L, fb, fr, spike)
            assert a == b, (sym, tf)
            total += len(a)
    return f"{total} zones compared"


if __name__ == "__main__":
    report_and_exit()
