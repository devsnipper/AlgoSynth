from core.sweeps import range_sweeps
from setups.base import Setup, events_frame


class RangeSweep(Setup):
    name = "s02_range_sweep"
    title = "Range-extreme sweep (20 candles)"

    def detect(self, ctx):
        ev = range_sweeps(ctx, lookback=20)
        return events_frame(ev["t"], ev["direction"])


SETUP = RangeSweep()
