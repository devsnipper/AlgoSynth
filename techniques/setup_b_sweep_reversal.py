"""Technique B: a liquidity sweep followed by a structure shift.

Liquidity levels: the previous calendar day's high / low, the extreme of the last 20 closed H1 candles, and pools of
equal highs / lows on H1 (two swings within 0.15 x ATR). An M15 candle that trades through a level and CLOSES back
inside is a sweep. If within 12 M15 candles a candle then closes beyond the last confirmed M15 swing on the other
side (a structure shift), that candle is the trigger. Direction: opposite to the wick.
"""
import numpy as np
import pandas as pd

from techniques import structure as st
from techniques.base import Signal, Snapshot, Technique
from techniques.prepared import prepare

SHIFT_WINDOW = 12         # M15 candles after the sweep
SL_BUFFER_ATR = 0.25      # beyond the sweep extreme, in M15 ATR
RR = 3.0
EQ_TOL = 0.15             # equal levels: within this many H1 ATR
RANGE_H1 = 20
POOL_MAX_AGE_H = 200
MIN_DAY_CANDLES = 90      # a day counts as complete with at least this many M15 candles (96 in a full day)


def equal_pools_h1(snap: Snapshot, p):
    """Pools of equal highs / lows on H1: list of (side, level, known_from, expires). side +1 = highs, -1 = lows."""
    h, l, c = p.h1_h, p.h1_l, p.h1_c
    t = p.h1_open
    if len(c) < 2 * 3 + 2:
        return []
    atr = st.atr(h, l, c)
    sh, sl = st.raw_swings(h, l, 3)
    active_hi, active_lo, pools = [], [], []
    for j in range(len(c)):
        active_hi = [s for s in active_hi if h[j] <= s[0] and j - s[1] <= POOL_MAX_AGE_H]
        active_lo = [s for s in active_lo if l[j] >= s[0] and j - s[1] <= POOL_MAX_AGE_H]
        i = j - 3
        if i >= 0 and not np.isnan(atr[j]):
            tol = EQ_TOL * atr[j]
            known = t[j] + np.timedelta64(60, "m")                         # the H1 candle j has just closed
            if sh[i]:
                lvl = h[i]
                grp = [s for s in active_hi if abs(s[0] - lvl) <= tol]
                if grp:
                    pools.append((1, max([lvl] + [s[0] for s in grp]), known, known + np.timedelta64(POOL_MAX_AGE_H, "h")))
                    active_hi = [s for s in active_hi if s not in grp]
                else:
                    active_hi.append([lvl, i])
            if sl[i]:
                lvl = l[i]
                grp = [s for s in active_lo if abs(s[0] - lvl) <= tol]
                if grp:
                    pools.append((-1, min([lvl] + [s[0] for s in grp]), known, known + np.timedelta64(POOL_MAX_AGE_H, "h")))
                    active_lo = [s for s in active_lo if s not in grp]
                else:
                    active_lo.append([lvl, i])
    return sorted(pools, key=lambda x: x[2])


def previous_day_levels(t_open: np.ndarray, h: np.ndarray, l: np.ndarray):
    """High and low of the previous complete calendar day, for each M15 candle (NaN if not complete)."""
    day = t_open.astype("datetime64[D]")
    uniq, inv, counts = np.unique(day, return_inverse=True, return_counts=True)
    hi = np.full(len(uniq), -np.inf)
    lo = np.full(len(uniq), np.inf)
    np.maximum.at(hi, inv, h)
    np.minimum.at(lo, inv, l)
    usable = np.zeros(len(uniq), bool)               # day i can be used as "previous day" if it is complete
    usable[1:] = (counts[:-1] >= MIN_DAY_CANDLES) & ((uniq[1:] - uniq[:-1]) == np.timedelta64(1, "D"))
    hi_prev = np.full(len(uniq), np.nan)
    lo_prev = np.full(len(uniq), np.nan)
    hi_prev[1:], lo_prev[1:] = hi[:-1], lo[:-1]
    hi_prev[~usable], lo_prev[~usable] = np.nan, np.nan
    return hi_prev[inv], lo_prev[inv]


def find_sweeps(p, pools, prev_hi, prev_lo, rng_hi, rng_lo):
    """Sweeps on M15: list of (index, direction, extreme, kinds). direction -1 = highs swept (short)."""
    sweeps = []
    live = []                                           # active pools: [side, level, expires]
    ptr = 0
    for t in range(p.n):
        now = p.t_open[t]
        while ptr < len(pools) and pools[ptr][2] <= now:               # known before this candle opened
            live.append([pools[ptr][0], pools[ptr][1], pools[ptr][3]])
            ptr += 1
        live = [q for q in live if q[2] > now]

        hi_levels = [(prev_hi[t], "previous-day high"), (rng_hi[t], "20-candle H1 high")] + \
                    [(q[1], "equal highs") for q in live if q[0] == 1]
        lo_levels = [(prev_lo[t], "previous-day low"), (rng_lo[t], "20-candle H1 low")] + \
                    [(q[1], "equal lows") for q in live if q[0] == -1]
        up = [(lv, k) for lv, k in hi_levels if np.isfinite(lv) and p.h[t] > lv and p.c[t] < lv]
        dn = [(lv, k) for lv, k in lo_levels if np.isfinite(lv) and p.l[t] < lv and p.c[t] > lv]
        # a pool is used up once any candle trades through it
        live = [q for q in live if not ((q[0] == 1 and p.h[t] > q[1]) or (q[0] == -1 and p.l[t] < q[1]))]
        if up and not dn:
            sweeps.append((t, -1, float(p.h[t]), ", ".join(sorted({k for _, k in up}))))
        elif dn and not up:
            sweeps.append((t, 1, float(p.l[t]), ", ".join(sorted({k for _, k in dn}))))
    return sweeps


def shift_triggers(p, sweeps):
    """For each sweep, the first candle within SHIFT_WINDOW that closes beyond the last confirmed M15 swing on the
    other side (known before the sweep). The idea is cancelled if price closes beyond the sweep extreme first."""
    out = []
    for s, d, ext, kinds in sweeps:
        ref = p.m15_struct["prev_sl"][s] if d == -1 else p.m15_struct["prev_sh"][s]
        if not np.isfinite(ref) or (d == -1 and ref >= p.c[s]) or (d == 1 and ref <= p.c[s]):
            continue
        for t in range(s + 1, min(s + SHIFT_WINDOW, p.n - 1) + 1):
            if (d == -1 and p.c[t] > ext) or (d == 1 and p.c[t] < ext):
                break
            if (d == -1 and p.c[t] < ref) or (d == 1 and p.c[t] > ref):
                out.append((t, d, ext, kinds, s))
                break
    return out


class SweepReversal(Technique):
    name = "SMC_B_SWEEP_REV"
    title = "B: liquidity sweep and structure shift"

    def signals(self, snap: Snapshot) -> list:
        p = prepare(snap)
        pools = equal_pools_h1(snap, p)
        prev_hi, prev_lo = previous_day_levels(p.t_open, p.h, p.l)
        # H1 range extremes known BEFORE each M15 candle opens
        t_before = p.t_open - np.timedelta64(15, "m")
        rng_hi = st.map_htf(p.h1_open, 60, t_before, pd.Series(p.h1_h).rolling(RANGE_H1).max().to_numpy())
        rng_lo = st.map_htf(p.h1_open, 60, t_before, pd.Series(p.h1_l).rolling(RANGE_H1).min().to_numpy())
        sweeps = find_sweeps(p, pools, prev_hi, prev_lo, rng_hi, rng_lo)

        out, seen = [], set()
        for t, d, ext, kinds, s in sorted(shift_triggers(p, sweeps), key=lambda x: (x[0], x[4])):
            if (t, d) in seen or not np.isfinite(p.atr15[t]):
                continue
            seen.add((t, d))
            entry = float(p.c[t])
            sl = ext + d * -1 * SL_BUFFER_ATR * p.atr15[t]            # beyond the sweep extreme
            risk = abs(entry - sl)
            if risk <= 0 or (sl - entry) * d >= 0:
                continue
            out.append(Signal(technique=self.name, symbol=snap.symbol, direction=d, trigger_idx=t,
                              trigger_time=pd.Timestamp(p.t_close[t]), entry_ref=entry, sl=float(sl),
                              tp=float(entry + d * RR * risk), rr=RR, zone_lo=float(min(ext, entry)),
                              zone_hi=float(max(ext, entry)), bias_dir=int(p.bias[t]),
                              notes=f"swept {kinds}; shift {t - s} candles later; TP {RR:g}R"))
        return out


TECHNIQUE = SweepReversal()
