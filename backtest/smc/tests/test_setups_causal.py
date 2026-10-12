"""Look-ahead check applied to EVERY registered setup on real data.

For each setup and symbol: detect on the full history, then detect again on only the first N candles
(with only the H1 candles closed by then). Every event with t < N must be identical. If a setup used
future candles, the truncated run would give different events.

Usage : backtest/.venv/Scripts/python.exe backtest/smc/tests/test_setups_causal.py
"""
import os
import sys
import traceback

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))                      # backtest/smc

from core.context import get_context, truncated_context           # noqa: E402
from setups import registry                                        # noqa: E402

N = 30000
SYMBOLS = ("Boom 500 Index", "Crash 500 Index")
RESULTS = []


def schema(events, name):
    assert list(events.columns[:2]) == ["t", "direction"], events.columns
    assert events["direction"].isin([-1, 1]).all(), f"{name}: direction must be +1/-1"
    assert events["t"].is_monotonic_increasing and not events.duplicated(["t", "direction"]).any(), f"{name}: sorted, unique"


for name, setup in registry.load_all().items():
    try:
        msgs = []
        for sym in SYMBOLS:
            ctx = get_context(sym)
            full = setup.detect(ctx)
            schema(full, name)
            part = setup.detect(truncated_context(ctx, N))
            a = full[full["t"] < N][["t", "direction"]].reset_index(drop=True)
            b = part[part["t"] < N][["t", "direction"]].reset_index(drop=True)
            pd.testing.assert_frame_equal(a, b)
            msgs.append(f"{sym[:5]}{sym.split()[1]}: {len(a)} events identical")
        RESULTS.append((f"{name}: no look-ahead, valid output", True, "; ".join(msgs)))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((f"{name}: no look-ahead, valid output", False, f"{type(e).__name__}: {e}\n{traceback.format_exc(limit=2)}"))

if __name__ == "__main__":
    for name, ok, msg in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"\n      {msg}" if msg else ""))
    sys.exit(0 if all(ok for _, ok, _ in RESULTS) else 1)
