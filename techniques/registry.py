"""The active techniques, in PRIORITY order.

When two techniques signal on the same symbol on the same candle, the first one in this list trades and the others are
logged as skipped (one SMC position per symbol). The strictest technique comes first: C, then A, then B.
Adding a technique = one file + one line here.
"""
from techniques import setup_a_ob_trend, setup_b_sweep_reversal, setup_c_pd_ob_fvg

ACTIVE = [
    setup_c_pd_ob_fvg.TECHNIQUE,
    setup_a_ob_trend.TECHNIQUE,
    setup_b_sweep_reversal.TECHNIQUE,
]


def by_name(name: str):
    return next(t for t in ACTIVE if t.name == name)


def all_signals(snapshot) -> list:
    """Signals of every active technique, sorted by trigger candle, then by priority."""
    rank = {t.name: i for i, t in enumerate(ACTIVE)}
    sigs = [s for t in ACTIVE for s in t.signals(snapshot)]
    sigs.sort(key=lambda s: (s.trigger_idx, rank[s.technique]))
    return sigs
