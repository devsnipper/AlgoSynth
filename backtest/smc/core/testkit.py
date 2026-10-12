"""Helpers to build small hand-made contexts for setup tests."""
import numpy as np
import pandas as pd

from core.context import Context, make_context

T0 = pd.Timestamp("2026-01-01 00:00")


def synthetic_context(o, h, l, c, L: int = 2, Lh: int = 2, atr: float = 1.0, h1_dir: int = 0) -> Context:
    """Context from explicit M15 candles. ATR is forced to a constant, spreads are 0, point is 1,
    spike flags are off and the H1 bias is a constant (override ctx.* afterwards if needed)."""
    n = len(c)
    m15 = pd.DataFrame({"time": [T0 + pd.Timedelta(minutes=15 * i) for i in range(n)],
                        "open": o, "high": h, "low": l, "close": c, "spread": 0})
    nh = n // 4 + 3
    h1 = pd.DataFrame({"time": [T0 + pd.Timedelta(hours=i) for i in range(nh)],
                       "open": 1.0, "high": 1.1, "low": 0.9, "close": 1.0, "spread": 0})
    ctx = make_context("TEST", m15, h1, 1.0, L, Lh)
    ctx.atr = np.full(n, float(atr))
    ctx.spike = np.zeros(n, bool)
    ctx.h1_dir = np.full(n, h1_dir, np.int8)
    return ctx


def has_event(events: pd.DataFrame, t: int, direction: int) -> bool:
    return bool(((events["t"] == t) & (events["direction"] == direction)).any())
