"""Liquidity sweep detectors shared by setups 1, 2 and 3. All causal.

A sweep is a candle that trades beyond a level and closes back inside. The trade direction is the opposite
of the wick: a wick above a high is a short (-1), a wick below a low is a long (+1).
"""
import numpy as np
import pandas as pd

from core import primitives as sc


def range_sweeps(ctx, lookback: int = 20) -> pd.DataFrame:
    """Setup 2: the candle takes out the highest high / lowest low of the previous `lookback` candles and
    closes back inside. An outside candle that does both is ignored."""
    prev_hi = pd.Series(ctx.h).shift(1).rolling(lookback).max().to_numpy()
    prev_lo = pd.Series(ctx.l).shift(1).rolling(lookback).min().to_numpy()
    with np.errstate(invalid="ignore"):
        short = (ctx.h > prev_hi) & (ctx.c < prev_hi)
        long_ = (ctx.l < prev_lo) & (ctx.c > prev_lo)
    both = short & long_
    short, long_ = short & ~both, long_ & ~both
    t = np.concatenate([np.where(short)[0], np.where(long_)[0]])
    d = np.concatenate([-np.ones(short.sum(), int), np.ones(long_.sum(), int)])
    out = pd.DataFrame({"t": t, "direction": d}).sort_values("t").reset_index(drop=True)
    return out


def equal_level_sweeps(ctx, tol_mult: float = 0.15, max_age: int = 200) -> pd.DataFrame:
    """Setup 1: two or more confirmed swing points within tol_mult x ATR of each other form a liquidity pool
    (at the level of the most extreme one). The first candle that wicks beyond the pool and closes back
    inside it is the sweep. A candle that closes beyond the pool just consumes it."""
    h, l, c, atr, L = ctx.h, ctx.l, ctx.c, ctx.atr, ctx.L
    sh, sl = sc.raw_swings(h, l, L)
    n = len(c)
    active_hi, active_lo = [], []        # single confirmed swings not yet taken out: [level, index]
    pools_hi, pools_lo = [], []          # pools: [level, formed_at]
    rows = []

    for t in range(n):
        # 1. pools and swings from BEFORE this candle
        for p in pools_hi[:]:
            if t - p[1] > max_age:
                pools_hi.remove(p)
            elif h[t] > p[0]:
                if c[t] < p[0]:
                    rows.append((t, -1))
                pools_hi.remove(p)
        for p in pools_lo[:]:
            if t - p[1] > max_age:
                pools_lo.remove(p)
            elif l[t] < p[0]:
                if c[t] > p[0]:
                    rows.append((t, 1))
                pools_lo.remove(p)
        active_hi = [s for s in active_hi if h[t] <= s[0] and t - s[1] <= max_age]
        active_lo = [s for s in active_lo if l[t] >= s[0] and t - s[1] <= max_age]

        # 2. the swing confirmed at the close of t (it formed at t - L)
        i = t - L
        if i >= 0 and not np.isnan(atr[t]):
            tol = tol_mult * atr[t]
            if sh[i]:
                lvl = h[i]
                grp = [s for s in active_hi if abs(s[0] - lvl) <= tol]
                if grp:
                    pools_hi.append([max([lvl] + [s[0] for s in grp]), t])
                    active_hi = [s for s in active_hi if s not in grp]
                else:
                    active_hi.append([lvl, i])
            if sl[i]:
                lvl = l[i]
                grp = [s for s in active_lo if abs(s[0] - lvl) <= tol]
                if grp:
                    pools_lo.append([min([lvl] + [s[0] for s in grp]), t])
                    active_lo = [s for s in active_lo if s not in grp]
                else:
                    active_lo.append([lvl, i])

    return pd.DataFrame(rows, columns=["t", "direction"]).sort_values("t").reset_index(drop=True)
