"""Work shared by all techniques, computed once per snapshot: arrays on the M15 timeline and the H1/H4 context."""
from dataclasses import dataclass

import numpy as np

from techniques import structure as st
from techniques.base import Snapshot, as_arrays, times_open

H4_L = 3          # swing length on H1 and H4
M15_L = 5         # swing length on M15


@dataclass
class Prepared:
    n: int
    o: np.ndarray
    h: np.ndarray
    l: np.ndarray
    c: np.ndarray
    t_open: np.ndarray
    t_close: np.ndarray
    atr15: np.ndarray
    atr1: np.ndarray            # H1 ATR as known at each M15 close
    bias: np.ndarray            # H4 structure direction at each M15 close (+1 / -1 / 0)
    rl4: np.ndarray             # last confirmed H4 swing low at each M15 close
    rh4: np.ndarray             # last confirmed H4 swing high at each M15 close
    h1_zones: list              # order blocks on H1
    h1_open: np.ndarray
    sw4_high_lvl: np.ndarray    # confirmed H4 swing highs and when each became known
    sw4_high_at: np.ndarray
    sw4_low_lvl: np.ndarray
    sw4_low_at: np.ndarray
    m15_struct: dict            # structure() on M15 (prev_sl / prev_sh used by technique B)
    h1_o: np.ndarray
    h1_h: np.ndarray
    h1_l: np.ndarray
    h1_c: np.ndarray


def prepare(snap: Snapshot) -> Prepared:
    if "prepared" in snap.cache:
        return snap.cache["prepared"]
    o, h, l, c = as_arrays(snap.m15)
    t_open = times_open(snap.m15)
    t_close = t_open + np.timedelta64(15, "m")

    h1o, h1h, h1l, h1c = as_arrays(snap.h1)
    h1_t = times_open(snap.h1)
    fb, fr = st.fvg_flags(h1o, h1h, h1l, h1c)
    zones = st.ob_zones(h1o, h1h, h1l, h1c, H4_L, fb, fr, st.spike_flags(h1h, h1l)) if len(h1c) > 2 * H4_L + 2 else []
    atr1 = st.map_htf(h1_t, 60, t_open, st.atr(h1h, h1l, h1c))

    h4o, h4h, h4l, h4c = as_arrays(snap.h4)
    h4_t = times_open(snap.h4)
    if len(h4c) > 2 * H4_L + 2:
        s4 = st.structure(h4h, h4l, h4c, H4_L)
        bias = st.map_htf(h4_t, 240, t_open, s4["dir"], fill=0).astype(int)
        rl4 = st.map_htf(h4_t, 240, t_open, s4["range_low"])
        rh4 = st.map_htf(h4_t, 240, t_open, s4["range_high"])
        shl, sha, sll, sla = st.confirmed_swings(h4h, h4l, H4_L, h4_t, 240)
    else:
        bias = np.zeros(len(c), int)
        rl4 = rh4 = np.full(len(c), np.nan)
        shl = sha = sll = sla = np.array([])
    p = Prepared(n=len(c), o=o, h=h, l=l, c=c, t_open=t_open, t_close=t_close, atr15=st.atr(h, l, c), atr1=atr1,
                 bias=bias, rl4=rl4, rh4=rh4, h1_zones=zones, h1_open=h1_t, sw4_high_lvl=shl, sw4_high_at=sha,
                 sw4_low_lvl=sll, sw4_low_at=sla, m15_struct=st.structure(h, l, c, M15_L),
                 h1_o=h1o, h1_h=h1h, h1_l=h1l, h1_c=h1c)
    snap.cache["prepared"] = p
    return p


def nearest_swing_ahead(p: Prepared, t: int, entry: float, direction: int):
    """Nearest confirmed H4 swing in the trade direction (above entry for a buy, below for a sell) known by the close
    of candle t, or None. Used to check that there is room to the target."""
    now = p.t_close[t]
    if direction == 1:
        m = (p.sw4_high_at <= now) & (p.sw4_high_lvl > entry)
        return float(p.sw4_high_lvl[m].min()) if m.any() else None
    m = (p.sw4_low_at <= now) & (p.sw4_low_lvl < entry)
    return float(p.sw4_low_lvl[m].max()) if m.any() else None
