import numpy as np
import pandas as pd

from core import primitives as sc
from core.orderblocks import ob_zones
from setups.base import Setup, events_frame

H1_WINDOW = 48      # H1 candles after the break in which the first touch (measured on M15) must happen


class H1OrderBlock(Setup):
    name = "s08_h1_order_block"
    title = "H1 order block, touch measured on M15"

    def detect(self, ctx):
        h1 = ctx.h1
        o, h, l, c = (h1[x].to_numpy(dtype=float) for x in ("open", "high", "low", "close"))
        fb, fr = sc.fvg_flags(o, h, l, c)
        zones = ob_zones(o, h, l, c, ctx.Lh, fb, fr, sc.spike_flags(h, l))

        times = ctx.times                                                  # M15 open times
        rows = []
        for z in zones:
            close_time = (h1["time"].iloc[z["born"]] + pd.Timedelta(hours=1)).to_datetime64()
            k0 = int(np.searchsorted(times, close_time, side="left"))      # first M15 candle after the H1 break closes
            k1 = int(np.searchsorted(times, close_time + np.timedelta64(H1_WINDOW, "h"), side="left"))
            for k in range(k0, min(k1, ctx.n)):
                if (z["dir"] == 1 and ctx.l[k] <= z["hi"]) or (z["dir"] == -1 and ctx.h[k] >= z["lo"]):
                    rows.append((k, z["dir"], z["lo"], z["hi"]))
                    break
        return events_frame([r[0] for r in rows], [r[1] for r in rows],
                            zone_lo=[r[2] for r in rows], zone_hi=[r[3] for r in rows])


SETUP = H1OrderBlock()
