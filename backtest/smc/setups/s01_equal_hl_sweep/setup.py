from core.sweeps import equal_level_sweeps
from setups.base import Setup, events_frame


class EqualHighLowSweep(Setup):
    name = "s01_equal_hl_sweep"
    title = "Equal highs/lows sweep"

    def detect(self, ctx):
        ev = equal_level_sweeps(ctx)
        return events_frame(ev["t"], ev["direction"])


SETUP = EqualHighLowSweep()
