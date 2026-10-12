"""Temporary home of the first SMC setup (sweep + shift + order block), used by diagnose_setups.py.
It becomes setups/s10_sweep_shift_ob_reference in the next step of the restructure.
"""
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core import primitives as sc                     # noqa: E402
from core.constants import HTF_MINUTES, WINDOW_START  # noqa: E402
from core.data import load, symbol_info               # noqa: E402
from core.engine import simulate_orders               # noqa: E402


def build_orders(symbol: str, htf: str, L: int = 5, Lh: int = 3, clip: bool = False,
                 bias: str = "dir") -> pd.DataFrame:
    """SMC setups of one symbol filtered by the bias rule.
    bias: 'dir' (base) | 'dir+pd' (adds premium/discount) | 'none' (no higher-timeframe filter)."""
    info = symbol_info()[symbol]
    m15 = load(symbol, "M15")
    ctx = sc.htf_context(m15["time"], load(symbol, htf), HTF_MINUTES[htf], Lh, clip)
    st = sc.find_setups(m15, info["point"], ctx, L, clip)
    if bias == "dir":
        st = st[st.htf_dir == st.direction]
    elif bias == "dir+pd":
        st = st[st.htf_ok]
    elif bias != "none":
        raise ValueError(bias)
    return st.reset_index(drop=True)


def run_symbol(symbol: str, htf: str, start=WINDOW_START, end=None, bias: str = "dir", **kw) -> pd.DataFrame:
    info = symbol_info()[symbol]
    orders = build_orders(symbol, htf, bias=bias, **{k: v for k, v in kw.items() if k in ("L", "Lh", "clip")})
    orders = orders[orders.signal_time >= start]
    if end is not None:
        orders = orders[orders.signal_time < end]
    sim_kw = {k: v for k, v in kw.items() if k in ("rr", "expire_candles", "max_hold_hours")}
    res = simulate_orders(orders, load(symbol, "M5"), info["point"], info["stops_level"], **sim_kw)
    res.insert(0, "symbol", symbol)
    return res
