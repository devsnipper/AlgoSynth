from techniques.base import Technique
from techniques.ob_retest import ob_retest_signals


class PDObFvg(Technique):
    name = "SMC_C_PD_OB_FVG"
    title = "C: premium/discount order block with a fair value gap (strictest)"

    def signals(self, snap):
        return ob_retest_signals(snap, self.name, require_fvg=True, premium_discount=True)


TECHNIQUE = PDObFvg()
