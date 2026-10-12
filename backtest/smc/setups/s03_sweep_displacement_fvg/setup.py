import pandas as pd

from core.sweeps import equal_level_sweeps, range_sweeps
from setups.base import Setup, events_frame

WINDOW = 6          # candles after the sweep in which the displacement must appear
BODY_ATR = 1.5      # displacement body, in ATR


class SweepDisplacementFvg(Setup):
    name = "s03_sweep_displacement_fvg"
    title = "Sweep + displacement + fair value gap"

    def detect(self, ctx):
        sweeps = pd.concat([equal_level_sweeps(ctx), range_sweeps(ctx)]).drop_duplicates()
        o, c, atr, n = ctx.o, ctx.c, ctx.atr, ctx.n
        rows = []
        for s, d in sweeps.itertuples(index=False):
            for k in range(s + 1, min(s + WINDOW, n - 2) + 1):
                body = (o[k] - c[k]) if d == -1 else (c[k] - o[k])         # move away from the swept side
                has_fvg = ctx.fvg_bear[k] if d == -1 else ctx.fvg_bull[k]
                if has_fvg and body >= BODY_ATR * atr[k]:
                    rows.append((k + 1, d))                                  # known at the close of the candle after
                    break
        return events_frame([r[0] for r in rows], [r[1] for r in rows])


SETUP = SweepDisplacementFvg()
