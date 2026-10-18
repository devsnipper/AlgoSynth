"""Causal market-structure building blocks (no MT5, no files).

Ported from backtest/smc/core/primitives.py and core/orderblocks.py, which were tested for look-ahead. The parity test
smc_tests/test_structure_parity.py checks that both versions give identical results on real data.

Rule of this module: the value at candle t only uses candles up to and including t. A swing at index i is only known
once candle i + L has closed.
"""
import numpy as np
import pandas as pd


def raw_swings(high: np.ndarray, low: np.ndarray, L: int):
    """Swing high at i if high[i] == max(high[i-L+1 .. i+L]); same for lows. Known at the close of candle i + L."""
    roll_hi = pd.Series(high).shift(-L).rolling(2 * L).max().to_numpy()
    roll_lo = pd.Series(low).shift(-L).rolling(2 * L).min().to_numpy()
    return high == roll_hi, low == roll_lo


def fvg_flags(o, h, l, c):
    """Fair value gap on the middle candle j of three candles (j-1, j, j+1). Known at the close of j + 1."""
    n = len(o)
    bull = np.zeros(n, bool)
    bear = np.zeros(n, bool)
    if n >= 3:
        bull[1:-1] = (h[:-2] < l[2:]) & (c[1:-1] > o[1:-1])
        bear[1:-1] = (l[:-2] > h[2:]) & (c[1:-1] < o[1:-1])
    return bull, bear


def atr(high: np.ndarray, low: np.ndarray, close: np.ndarray, n: int = 14) -> np.ndarray:
    """Wilder ATR. NaN for the first n - 1 candles."""
    prev_close = np.concatenate([[np.nan], close[:-1]])
    tr = np.nanmax(np.vstack([high - low, np.abs(high - prev_close), np.abs(low - prev_close)]), axis=0)
    return pd.Series(tr).ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean().to_numpy()


def spike_flags(high: np.ndarray, low: np.ndarray, mult: float = 8.0, window: int = 200) -> np.ndarray:
    """True for candles whose range is above mult x the median range of the previous `window` candles."""
    rng = pd.Series(high - low)
    med = rng.shift(1).rolling(window, min_periods=20).median()
    return (rng > mult * med).fillna(False).to_numpy()


def structure(high, low, close, L: int) -> dict:
    """Causal state machine: last confirmed swing high / low, breaks of structure and direction.
    dir, range_low, range_high describe the state AFTER candle t; prev_sh / prev_sl the state BEFORE it."""
    n = len(close)
    sh, sl = raw_swings(high, low, L)
    direction = np.zeros(n, np.int8)
    rl = np.full(n, np.nan)
    rh = np.full(n, np.nan)
    prev_sh = np.full(n, np.nan)
    prev_sl = np.full(n, np.nan)
    last_sh = last_sl = np.nan
    sh_open = sl_open = False
    d = 0
    for t in range(n):
        prev_sh[t], prev_sl[t] = last_sh, last_sl
        i = t - L
        if i >= 0:
            if sh[i]:
                last_sh, sh_open = high[i], True
            if sl[i]:
                last_sl, sl_open = low[i], True
        if sh_open and close[t] > last_sh:
            d, sh_open = 1, False
        elif sl_open and close[t] < last_sl:
            d, sl_open = -1, False
        direction[t], rl[t], rh[t] = d, last_sl, last_sh
    return {"dir": direction, "range_low": rl, "range_high": rh, "prev_sh": prev_sh, "prev_sl": prev_sl}


def ob_zones(o, h, l, c, L: int, fvg_bull, fvg_bear, spike) -> list:
    """One order block per break of structure, known from the close of its break candle `born`.
    The block is the last opposite-colour candle of the leg that made the break (the leg starts at the pullback
    extreme between the broken swing and the break). has_fvg: the leg holds a fair value gap in the break direction."""
    n = len(c)
    sh, sl = raw_swings(h, l, L)
    last_sh = last_sl = np.nan
    i_sh = i_sl = -1
    sh_open = sl_open = False
    zones = []
    for t in range(n):
        i = t - L
        if i >= 0:
            if sh[i]:
                last_sh, i_sh, sh_open = h[i], i, True
            if sl[i]:
                last_sl, i_sl, sl_open = l[i], i, True
        if sh_open and c[t] > last_sh:                      # bullish break
            sh_open = False
            a = i_sh + int(np.argmin(l[i_sh:t]))
            ob = next((k for k in range(t - 1, a - 1, -1) if c[k] < o[k]), None)
            if ob is not None:
                zones.append({"born": t, "dir": 1, "lo": l[ob], "hi": h[ob], "ob_idx": ob, "leg_start": a,
                              "has_fvg": bool(fvg_bull[a + 1:t].any()), "has_spike": bool(spike[a:t + 1].any())})
        elif sl_open and c[t] < last_sl:                    # bearish break
            sl_open = False
            a = i_sl + int(np.argmax(h[i_sl:t]))
            ob = next((k for k in range(t - 1, a - 1, -1) if c[k] > o[k]), None)
            if ob is not None:
                zones.append({"born": t, "dir": -1, "lo": l[ob], "hi": h[ob], "ob_idx": ob, "leg_start": a,
                              "has_fvg": bool(fvg_bear[a + 1:t].any()), "has_spike": bool(spike[a:t + 1].any())})
    return zones


def map_htf(htf_open_times, htf_minutes: int, m15_open_times, values, fill=np.nan) -> np.ndarray:
    """For each M15 candle: the value of the last higher-timeframe candle that had CLOSED by the M15 candle's close.
    (A higher-timeframe candle is never used before it has closed.)"""
    htf_close = np.asarray(htf_open_times, dtype="datetime64[ns]") + np.timedelta64(htf_minutes, "m")
    m15_close = np.asarray(m15_open_times, dtype="datetime64[ns]") + np.timedelta64(15, "m")
    k = np.searchsorted(htf_close, m15_close, side="right") - 1
    ok = k >= 0
    out = np.full(len(m15_close), fill, dtype=float)
    out[ok] = np.asarray(values, dtype=float)[k[ok]]
    return out


def confirmed_swings(high, low, L: int, times_open, minutes: int):
    """Confirmed swing points with the time at which each became known.
    Returns (high_levels, high_known_at, low_levels, low_known_at); *_known_at are datetime64 candle-close times."""
    sh, sl = raw_swings(high, low, L)
    n = len(high)
    t = np.asarray(times_open, dtype="datetime64[ns]")
    idx_h = np.where(sh)[0]
    idx_l = np.where(sl)[0]
    idx_h, idx_l = idx_h[idx_h + L < n], idx_l[idx_l + L < n]
    known = lambda idx: t[idx + L] + np.timedelta64(minutes, "m")
    return high[idx_h], known(idx_h), low[idx_l], known(idx_l)
