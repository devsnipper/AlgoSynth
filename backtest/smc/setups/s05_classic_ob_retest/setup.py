from core.orderblocks import first_touches, ob_zones
from setups.base import Setup, events_frame

WINDOW = 48     # candles after the break in which the first touch must happen


class ClassicObRetest(Setup):
    name = "s05_classic_ob_retest"
    title = "Classic OB retest (first touch)"

    def detect(self, ctx):
        zones = ob_zones(ctx.o, ctx.h, ctx.l, ctx.c, ctx.L, ctx.fvg_bull, ctx.fvg_bear, ctx.spike)
        hits = first_touches(zones, ctx.h, ctx.l, WINDOW)
        return events_frame([k for k, _ in hits], [z["dir"] for _, z in hits],
                            zone_lo=[z["lo"] for _, z in hits], zone_hi=[z["hi"] for _, z in hits])


SETUP = ClassicObRetest()
