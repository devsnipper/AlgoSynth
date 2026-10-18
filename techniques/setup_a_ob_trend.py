from techniques.base import Technique
from techniques.ob_retest import ob_retest_signals


class OBTrend(Technique):
    name = "SMC_A_OB_TREND"
    title = "A: trend continuation at an H1 order block"

    def signals(self, snap):
        return ob_retest_signals(snap, self.name, require_fvg=False, premium_discount=False)


TECHNIQUE = OBTrend()
