"""Trade engine: replays limit orders on M5 candles (see docs/SMC_STRATEGY.md > Fill rules).

It knows nothing about SMC. It receives orders (time, direction, entry, stop), so the random controls
and every setup run through exactly the same code.
"""
import numpy as np
import pandas as pd

from core.constants import M5_TD, M15_TD


def simulate_orders(orders: pd.DataFrame, m5: pd.DataFrame, point: float, stops_level: float,
                    rr: float = 2.0, expire_candles: int = 8, max_hold_hours: float = 3.0) -> pd.DataFrame:
    """orders: signal_time (order is live from this time), direction (+1 buy / -1 sell), entry, stop.
    Returns one row per order with status: closed, nofill, tooclose, busy, nodata."""
    t5 = m5["time"].to_numpy()
    o, h, l, c = (m5[x].to_numpy() for x in ("open", "high", "low", "close"))
    sp = m5["spread"].to_numpy() * point
    n = len(m5)
    order_life = M15_TD * expire_candles
    hold = pd.Timedelta(hours=max_hold_hours)

    rows = []
    busy_until = pd.Timestamp.min
    for od in orders.sort_values("signal_time").itertuples():
        base = {"signal_time": od.signal_time, "direction": od.direction, "entry": od.entry, "stop": od.stop}
        if od.signal_time < busy_until:
            rows.append({**base, "status": "busy"})
            continue
        i0 = int(np.searchsorted(t5, np.datetime64(od.signal_time), side="left"))
        if i0 >= n:
            rows.append({**base, "status": "nodata"})
            continue
        i_end = int(np.searchsorted(t5, np.datetime64(od.signal_time + order_life), side="left"))
        d = int(od.direction)

        if abs(od.entry - od.stop) < stops_level * point + sp[i0]:
            rows.append({**base, "status": "tooclose"})
            continue

        # --- limit order fill
        fill_i, fill = -1, np.nan
        for i in range(i0, min(i_end, n)):
            if d == 1 and l[i] + sp[i] <= od.entry:
                fill_i, fill = i, min(od.entry, o[i] + sp[i])
                break
            if d == -1 and h[i] >= od.entry:
                fill_i, fill = i, max(od.entry, o[i])
                break
        if fill_i < 0:
            busy_until = od.signal_time + order_life
            rows.append({**base, "status": "nofill"})
            continue

        R = abs(fill - od.stop)
        tp = fill + d * rr * R
        i_hold = int(np.searchsorted(t5, t5[fill_i] + np.timedelta64(int(hold.total_seconds()), "s"), side="left"))
        last = min(i_hold, n) - 1

        reason, j = "TIME", last
        ex_extreme = ex_level = c[last] + (sp[last] if d == -1 else 0.0)
        for j_ in range(fill_i, last + 1):
            if d == 1:
                hit_sl, hit_tp, extreme = l[j_] <= od.stop, h[j_] >= tp, l[j_]
            else:
                hit_sl, hit_tp, extreme = h[j_] + sp[j_] >= od.stop, l[j_] + sp[j_] <= tp, h[j_] + sp[j_]
            if hit_sl:                                   # stop wins, also inside the fill candle
                reason, j, ex_extreme, ex_level = "SL", j_, extreme, od.stop
                break
            if hit_tp and j_ > fill_i:                   # target ignored inside the fill candle (order of events unknown)
                reason, j, ex_extreme, ex_level = "TP", j_, tp, tp
                break
        if reason == "TIME" and i_hold > n:
            reason = "END"

        busy_until = pd.Timestamp(t5[j]) + M5_TD
        rows.append({**base, "status": "closed", "fill_time": pd.Timestamp(t5[fill_i]), "fill": fill,
                     "R_price": R, "tp": tp, "exit_time": busy_until, "reason": reason,
                     "exit_extreme": ex_extreme, "exit_level": ex_level,
                     "r": d * (ex_extreme - fill) / R, "r_level": d * (ex_level - fill) / R,
                     "held_min": (busy_until - pd.Timestamp(t5[fill_i])).total_seconds() / 60})
    return pd.DataFrame(rows)
