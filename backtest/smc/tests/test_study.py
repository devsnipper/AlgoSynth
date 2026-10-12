"""Tests of the Stage 1 statistics (core/study.py) and the block-B guard.

Usage : backtest/.venv/Scripts/python.exe backtest/smc/tests/test_study.py
"""
import os
import sys
import traceback

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))                      # backtest/smc

from core import study                                             # noqa: E402
from core.context import get_context                               # noqa: E402
from core.testkit import synthetic_context                         # noqa: E402

RESULTS = []


def check(name):
    def deco(fn):
        try:
            msg = fn()
            RESULTS.append((name, True, msg or ""))
        except Exception as e:  # noqa: BLE001
            RESULTS.append((name, False, f"{type(e).__name__}: {e}\n{traceback.format_exc(limit=2)}"))
        return fn
    return deco


@check("clustering keeps the first event of every group closer than 12 candles")
def _():
    keep = study.cluster(np.array([0, 5, 12, 13, 30]))
    assert keep.tolist() == [True, False, True, False, True], keep


@check("forward moves: a market entry on a steadily rising market gains exactly the horizon, in ATR")
def _():
    n = 40
    o = [10.0 + i for i in range(n)]
    c = [11.0 + i for i in range(n)]
    ctx = synthetic_context(o, c, o, c)                            # highs = closes, lows = opens
    fw = study.forward(ctx, 4)
    assert fw[1]["net"][10] == 4.0 and fw[-1]["net"][10] == -4.0, (fw[1]["net"][10], fw[-1]["net"][10])
    assert fw[1]["mfe"][10] == 4.0 and fw[1]["mae"][10] == 0.0
    assert np.isnan(fw[1]["net"][n - 2])                           # not enough candles left


@check("spread is charged on entry and exit")
def _():
    n = 20
    o = [10.0] * n
    ctx = synthetic_context(o, [10.0] * n, o, o)
    ctx.sp = np.full(n, 0.2)
    fw = study.forward(ctx, 4)
    assert abs(fw[1]["net"][5] + 0.2) < 1e-9 and abs(fw[-1]["net"][5] + 0.2) < 1e-9, (fw[1]["net"][5], fw[-1]["net"][5])


@check("block B cannot be opened at Stage 1")
def _():
    try:
        study.assert_block_allowed("B")
    except ValueError:
        return
    raise AssertionError("block B was allowed")


@check("random events give z-scores near zero (the test does not invent edges)")
def _():
    ctx = get_context("Boom 500 Index")
    rng = np.random.default_rng(11)
    valid = np.where(study.block_mask(ctx, "A"))[0]
    zs = []
    for _ in range(12):
        t = np.sort(rng.choice(valid, size=1500, replace=False))
        d = rng.choice([-1, 1], size=len(t))
        ev = pd.DataFrame({"t": t, "direction": d})
        part = study.symbol_excess(ctx, ev, "A", "none")
        zs.append(study.cell_stats([part])["z_3h"])
    zs = np.array(zs)
    assert np.all(np.abs(zs) < 3.5), zs
    assert abs(zs.mean()) < 1.5, zs.mean()
    return f"12 random draws: z in [{zs.min():.2f}, {zs.max():.2f}], mean {zs.mean():.2f}"


@check("bias h1 keeps only events that agree with the H1 direction")
def _():
    ctx = get_context("Crash 500 Index")
    valid = np.where(study.block_mask(ctx, "A"))[0][::7]
    ev = pd.DataFrame({"t": valid, "direction": np.where(valid % 2 == 0, 1, -1)})
    part = study.symbol_excess(ctx, ev, "A", "h1")
    assert (ctx.h1_dir[part["t"]] == part["direction"]).all()
    assert part["n"] < len(study.cluster(valid))


if __name__ == "__main__":
    for name, ok, msg in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"\n      {msg}" if msg else ""))
    sys.exit(0 if all(ok for _, ok, _ in RESULTS) else 1)
