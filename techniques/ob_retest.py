"""Order-block retest engine shared by techniques A and C.

An H1 order block (created by a break of structure) is waited for. The first time M15 trades back into it, an M15
candle that CLOSES back out of the zone, in the zone's direction and within a few candles, is the trigger.
"""
import numpy as np
import pandas as pd

from techniques.base import Signal, Snapshot
from techniques.prepared import Prepared, nearest_swing_ahead, prepare

ZONE_WINDOW_H1 = 48       # H1 candles after the break in which the first touch must happen
TRIGGER_WINDOW = 4        # M15 candles, counted from the touch candle, in which the closing trigger must appear
SL_BUFFER_ATR = 0.25      # beyond the zone's far edge, in H1 ATR


def first_trigger(c, h, l, d: int, zone_lo: float, zone_hi: float, k0: int, k1: int, trigger_window: int):
    """Index of the trigger candle for one zone, or None.
    The zone dies if a candle closes beyond its far edge before a trigger, or if no trigger appears in time."""
    n = len(c)
    for k in range(k0, min(k1, n)):
        touched = (l[k] <= zone_hi) if d == 1 else (h[k] >= zone_lo)
        if not touched:
            continue
        for t in range(k, min(k + trigger_window + 1, n)):
            if d == 1:
                if c[t] < zone_lo:
                    return None
                if c[t] > zone_hi:
                    return t
            else:
                if c[t] > zone_hi:
                    return None
                if c[t] < zone_lo:
                    return t
        return None
    return None


def ob_retest_signals(snap: Snapshot, technique: str, *, require_fvg: bool, premium_discount: bool,
                      min_room_rr: float = 1.5, rr: float = 2.0, max_rr_c: float = 3.0) -> list:
    p: Prepared = prepare(snap)
    out = []
    for z in p.h1_zones:
        if require_fvg and not z["has_fvg"]:
            continue
        d = z["dir"]
        born_close = p.h1_open[z["born"]] + np.timedelta64(60, "m")
        k0 = int(np.searchsorted(p.t_open, born_close, side="left"))
        k1 = int(np.searchsorted(p.t_open, born_close + np.timedelta64(ZONE_WINDOW_H1, "h"), side="left"))
        t = first_trigger(p.c, p.h, p.l, d, z["lo"], z["hi"], k0, k1, TRIGGER_WINDOW)
        if t is None or p.bias[t] != d or np.isnan(p.atr1[t]):
            continue
        entry = float(p.c[t])
        buf = SL_BUFFER_ATR * p.atr1[t]
        sl = z["lo"] - buf if d == 1 else z["hi"] + buf
        risk = abs(entry - sl)
        if risk <= 0:
            continue

        if premium_discount:                                   # technique C
            rl, rh = p.rl4[t], p.rh4[t]
            if not (np.isfinite(rl) and np.isfinite(rh) and rh > rl):
                continue
            mid = (rl + rh) / 2
            if (d == 1 and entry >= mid) or (d == -1 and entry <= mid):
                continue                                       # buys only in discount, sells only in premium
            dist = (rh - entry) if d == 1 else (entry - rl)
            if dist < rr * risk:
                continue                                       # not enough room to the other side of the range
            reward = min(dist, max_rr_c * risk)
            note_tp = f"TP at {'H4 range high' if d == 1 else 'H4 range low'} capped at {max_rr_c:g}R"
        else:                                                  # technique A
            nxt = nearest_swing_ahead(p, t, entry, d)
            if nxt is not None and abs(nxt - entry) < min_room_rr * risk:
                continue                                       # the next H4 swing is too close
            reward = rr * risk
            note_tp = f"TP {rr:g}R"
        tp = entry + d * reward
        out.append(Signal(technique=technique, symbol=snap.symbol, direction=d, trigger_idx=t,
                          trigger_time=pd.Timestamp(p.t_close[t]), entry_ref=entry, sl=float(sl), tp=float(tp),
                          rr=float(reward / risk), zone_lo=float(z["lo"]), zone_hi=float(z["hi"]), bias_dir=int(p.bias[t]),
                          notes=f"H1 OB {z['lo']:.5g}-{z['hi']:.5g}{' with FVG' if z['has_fvg'] else ''}; "
                                f"H4 bias {'up' if p.bias[t] == 1 else 'down'}; {note_tp}"))
    out.sort(key=lambda s: s.trigger_idx)
    return out
