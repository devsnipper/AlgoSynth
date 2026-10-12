import pandas as pd

from setups.base import Setup, events_frame

RANGE_CANDLES = 12      # length of the accumulation range
MAX_WIDTH_ATR = 3.0     # range width limit, in ATR
MANIP_WINDOW = 6        # candles after the range in which the manipulation wick must appear


class AccumulateManipulateDistribute(Setup):
    name = "s04_accumulate_manipulate_distribute"
    title = "Accumulate, manipulate, distribute"

    def detect(self, ctx):
        h, l, c, atr, n = ctx.h, ctx.l, ctx.c, ctx.atr, ctx.n
        rh = pd.Series(h).rolling(RANGE_CANDLES).max().to_numpy()      # range ending at candle r
        rl = pd.Series(l).rolling(RANGE_CANDLES).min().to_numpy()
        tight = (rh - rl) <= MAX_WIDTH_ATR * atr
        rows = []
        for t in range(RANGE_CANDLES, n):
            for r in range(t - 1, t - MANIP_WINDOW - 1, -1):           # most recent range first
                if r < RANGE_CANDLES - 1 or not tight[r]:
                    continue
                if r + 1 <= t - 1 and (h[r + 1:t].max() > rh[r] or l[r + 1:t].min() < rl[r]):
                    continue                                              # range already pierced earlier
                up = h[t] > rh[r] and c[t] <= rh[r]                       # wick above the range, close back inside
                dn = l[t] < rl[r] and c[t] >= rl[r]
                if up and not dn:
                    rows.append((t, -1))                                  # distribution towards the lower edge
                    break
                if dn and not up:
                    rows.append((t, 1))
                    break
                if up and dn:
                    break
        return events_frame([r[0] for r in rows], [r[1] for r in rows])


SETUP = AccumulateManipulateDistribute()
