"""Everything a setup may look at, computed once per symbol.

A Context holds M15 candles, the H1 bias and a few derived arrays. All derived values are causal:
the value at index t only uses candles up to and including t.
"""
from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np
import pandas as pd

from core import primitives as sc
from core.constants import M15_TD
from core.data import load, symbol_info


@dataclass
class Context:
    symbol: str
    point: float
    m15: pd.DataFrame
    h1: pd.DataFrame
    o: np.ndarray
    h: np.ndarray
    l: np.ndarray
    c: np.ndarray
    sp: np.ndarray            # spread in price units, per candle
    atr: np.ndarray           # ATR(14) on M15
    times: np.ndarray         # candle OPEN times (datetime64)
    t_close: np.ndarray       # candle CLOSE times = signal times
    h1_dir: np.ndarray        # +1 / -1 / 0: H1 structure direction at each M15 close (closed H1 candles only)
    h1ctx: dict               # full H1 context (dir, range_low, range_high) for the reference setup
    spike: np.ndarray         # spike candle flags
    fvg_bull: np.ndarray
    fvg_bear: np.ndarray
    L: int = 5                # swing length on M15
    Lh: int = 3               # swing length on H1
    cache: dict = field(default_factory=dict)

    @property
    def n(self) -> int:
        return len(self.c)


def make_context(symbol: str, m15: pd.DataFrame, h1: pd.DataFrame, point: float, L: int = 5, Lh: int = 3) -> Context:
    o, h, l, c = (m15[x].to_numpy(dtype=float) for x in ("open", "high", "low", "close"))
    h1ctx = sc.htf_context(m15["time"], h1, 60, Lh, False)
    bull, bear = sc.fvg_flags(o, h, l, c)
    times = m15["time"].to_numpy()
    return Context(symbol=symbol, point=point, m15=m15, h1=h1, o=o, h=h, l=l, c=c,
                   sp=m15["spread"].to_numpy(dtype=float) * point, atr=sc.atr(h, l, c),
                   times=times, t_close=(m15["time"] + M15_TD).to_numpy(),
                   h1_dir=h1ctx["dir"].astype(np.int8), h1ctx=h1ctx, spike=sc.spike_flags(h, l),
                   fvg_bull=bull, fvg_bear=bear, L=L, Lh=Lh)


@lru_cache(maxsize=None)
def get_context(symbol: str) -> Context:
    return make_context(symbol, load(symbol, "M15"), load(symbol, "H1"), symbol_info()[symbol]["point"])


def truncated_context(ctx: Context, n: int) -> Context:
    """The same context built from only the first n M15 candles (used by the look-ahead tests)."""
    m15 = ctx.m15.iloc[:n].reset_index(drop=True)
    last_close = m15["time"].iloc[-1] + M15_TD
    h1 = ctx.h1[ctx.h1["time"] + pd.Timedelta(minutes=60) <= last_close].reset_index(drop=True)
    return make_context(ctx.symbol, m15, h1, ctx.point, ctx.L, ctx.Lh)
