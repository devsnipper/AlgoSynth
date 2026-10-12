import numpy as np

from setups.base import Setup, events_frame

BODY_ATR = 1.5      # displacement body, in ATR
MIN_WAIT = 2        # candles after the gap completes before a touch counts
WINDOW = 24         # candles after the gap completes in which the first touch must happen


class FvgContinuation(Setup):
    name = "s06_fvg_continuation"
    title = "FVG continuation (H1 bias)"
    uses_bias = False        # the H1 bias is part of the definition

    def detect(self, ctx):
        o, h, l, c, atr, n = ctx.o, ctx.h, ctx.l, ctx.c, ctx.atr, ctx.n
        big = np.abs(c - o) >= BODY_ATR * atr
        rows = []
        for k in range(1, n - 1):
            if not big[k]:
                continue
            if c[k] > o[k] and ctx.fvg_bull[k]:
                d, born, edge = 1, k + 1, l[k + 1]                          # gap top: price must come back down to it
            elif c[k] < o[k] and ctx.fvg_bear[k]:
                d, born, edge = -1, k + 1, h[k + 1]                         # gap bottom
            else:
                continue
            for m in range(born + 1, min(n, born + WINDOW + 1)):
                if (d == 1 and l[m] <= edge) or (d == -1 and h[m] >= edge):
                    # the FIRST touch decides: too early cancels the gap; later needs the H1 bias
                    if m >= born + MIN_WAIT and ctx.h1_dir[m] == d:
                        rows.append((m, d))
                    break
        return events_frame([r[0] for r in rows], [r[1] for r in rows])


SETUP = FvgContinuation()
