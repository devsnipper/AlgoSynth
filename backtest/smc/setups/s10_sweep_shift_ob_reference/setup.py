from core import primitives as sc
from setups.base import Setup, events_frame


class SweepShiftObReference(Setup):
    name = "s10_sweep_shift_ob_reference"
    title = "Sweep + structure shift + OB (reference)"

    def detect(self, ctx):
        st = sc.find_setups(ctx.m15, ctx.point, ctx.h1ctx, ctx.L, False)
        return events_frame(st["signal_idx"], st["direction"], entry=st["entry"], stop=st["stop"])


SETUP = SweepShiftObReference()
