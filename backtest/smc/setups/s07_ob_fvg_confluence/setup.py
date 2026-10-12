from core.orderblocks import first_touches, ob_zones
from setups.base import Setup, events_frame

WINDOW = 48


class ObFvgConfluence(Setup):
    name = "s07_ob_fvg_confluence"
    title = "OB + FVG confluence"

    def detect(self, ctx):
        zones = [z for z in ob_zones(ctx.o, ctx.h, ctx.l, ctx.c, ctx.L, ctx.fvg_bull, ctx.fvg_bear, ctx.spike)
                 if z["has_fvg"]]
        hits = first_touches(zones, ctx.h, ctx.l, WINDOW)
        return events_frame([k for k, _ in hits], [z["dir"] for _, z in hits],
                            zone_lo=[z["lo"] for _, z in hits], zone_hi=[z["hi"] for _, z in hits])


SETUP = ObFvgConfluence()
