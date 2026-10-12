"""Classic order blocks shared by setups 5, 7, 8 and 9. All causal.

A break of structure is a close beyond the last confirmed swing point. The order block is the last
opposite-colour candle of the leg that made the break. Its zone is that candle's high-low range.
The leg starts at the extreme of the pullback between the broken swing and the break.
"""
import numpy as np

from core import primitives as sc


def ob_zones(o, h, l, c, L: int, fvg_bull, fvg_bear, spike) -> list:
    """One zone per break of structure. Each zone is known from the close of its break candle `born`.
    has_fvg: the leg contains a fair value gap in the break direction. has_spike: it contains a spike candle."""
    n = len(c)
    sh, sl = sc.raw_swings(h, l, L)
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
            a = i_sh + int(np.argmin(l[i_sh:t]))             # pullback low since the broken high
            ob = next((k for k in range(t - 1, a - 1, -1) if c[k] < o[k]), None)
            if ob is not None:
                zones.append({"born": t, "dir": 1, "lo": l[ob], "hi": h[ob], "ob_idx": ob, "leg_start": a,
                              "has_fvg": bool(fvg_bull[a + 1:t].any()), "has_spike": bool(spike[a:t + 1].any())})
        elif sl_open and c[t] < last_sl:                    # bearish break
            sl_open = False
            a = i_sl + int(np.argmax(h[i_sl:t]))             # pullback high since the broken low
            ob = next((k for k in range(t - 1, a - 1, -1) if c[k] > o[k]), None)
            if ob is not None:
                zones.append({"born": t, "dir": -1, "lo": l[ob], "hi": h[ob], "ob_idx": ob, "leg_start": a,
                              "has_fvg": bool(fvg_bear[a + 1:t].any()), "has_spike": bool(spike[a:t + 1].any())})
    return zones


def first_touches(zones: list, h, l, window: int) -> list:
    """The first candle after the break where price trades back into the zone, within `window` candles.
    Returns (touch_index, zone) pairs. The touch is known at the close of that candle."""
    n = len(h)
    out = []
    for z in zones:
        for k in range(z["born"] + 1, min(n, z["born"] + window + 1)):
            if (z["dir"] == 1 and l[k] <= z["hi"]) or (z["dir"] == -1 and h[k] >= z["lo"]):
                out.append((k, z))
                break
    return out
