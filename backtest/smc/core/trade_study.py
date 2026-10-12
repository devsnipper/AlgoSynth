"""EXPLORATORY trade test: every setup with ONE fixed trade design, against random entries with the same design.

Design (fixed before running, identical for all setups):
    entry   market, at the open of the next M5 candle after the signal closes (ask for buys, bid for sells)
    stop    2 x ATR(14) of the signal candle
    target  2R (R = the stop distance)
    hold    at most 3 hours, then closed at the candle close
    fills   stop at the candle's worst price (spikes jump through), target at its level, spread charged
    block   A only (M5 data needed). Blocks B and C are not touched.
Events are selected exactly as in Stage 1 (block, bias, clustering). One position per symbol at a time.

This is not the Stage 2 of docs/SETUP_LIST.md (entry/stop variants for survivors). It exists to give win rate, R and
profit factor for every setup, so that nothing is hidden behind the Stage 1 gate.
"""
import numpy as np
import pandas as pd

from core import study
from core.context import get_context
from core.data import load, symbol_info
from core.constants import M5_TD, M15_TD
from core.engine import simulate_orders

ATR_STOP = 2.0
RR = 2.0
HOLD_H = 3.0
CONTROL_ORDERS = 4000          # random orders per symbol and bias for the control


def make_orders(ctx, m5, t_idx, directions) -> pd.DataFrame:
    """Market orders at the open of the first M5 candle after each signal candle closes."""
    t_close = ctx.t_close[t_idx]
    i0 = np.searchsorted(m5["time"].to_numpy(), t_close, side="left")
    ok = i0 < len(m5)
    t_idx, directions, t_close, i0 = t_idx[ok], directions[ok], t_close[ok], i0[ok]
    px = m5["open"].to_numpy()[i0]
    spx = m5["spread"].to_numpy()[i0] * ctx.point
    d = directions.astype(int)
    entry = np.where(d == 1, px + spx, px)
    stop = entry - d * ATR_STOP * ctx.atr[t_idx]
    return pd.DataFrame({"signal_time": pd.to_datetime(t_close), "direction": d, "entry": entry, "stop": stop})


def frame_for(symbol: str, block: str):
    """Candles used for fills: M5 for block A; M15 (coarser, more pessimistic) for the older block C."""
    return (load(symbol, "M5"), M5_TD) if block == "A" else (load(symbol, "M15"), M15_TD)


def run_orders(symbol: str, orders: pd.DataFrame, block: str = "A") -> pd.DataFrame:
    info = symbol_info()[symbol]
    frame, td = frame_for(symbol, block)
    res = simulate_orders(orders, frame, info["point"], info["stops_level"], rr=RR, max_hold_hours=HOLD_H, candle_td=td)
    res = res[res.status == "closed"].copy()
    res.insert(0, "symbol", symbol)
    return res


def setup_trades(setup, symbol: str, bias: str, block: str = "A") -> pd.DataFrame:
    ctx = get_context(symbol)
    ev = study.select_events(ctx, setup.detect(ctx), block, bias)
    if ev.empty:
        return pd.DataFrame()
    orders = make_orders(ctx, frame_for(symbol, block)[0], ev["t"].to_numpy(), ev["direction"].to_numpy())
    return run_orders(symbol, orders, block)


def control_trades(symbol: str, bias: str, block: str = "A", seed: int = 5) -> pd.DataFrame:
    """Random entries inside the block under the same design (direction random, or the H1 direction for bias h1)."""
    ctx = get_context(symbol)
    rng = np.random.default_rng(seed + len(symbol))
    valid = np.where(study.block_mask(ctx, block) & np.isfinite(ctx.atr))[0]
    if bias == "h1":
        valid = valid[ctx.h1_dir[valid] != 0]
    t = np.sort(rng.choice(valid, size=min(CONTROL_ORDERS, len(valid)), replace=False))
    d = ctx.h1_dir[t].astype(int) if bias == "h1" else rng.choice([-1, 1], size=len(t))
    return run_orders(symbol, make_orders(ctx, frame_for(symbol, block)[0], t, d), block)


def summarize(tr: pd.DataFrame) -> dict:
    if tr.empty:
        return {"trades": 0}
    r, win, lose = tr["r"], tr["r"][tr["r"] > 0].sum(), -tr["r"][tr["r"] < 0].sum()
    return {"trades": len(tr), "win_pct": 100 * (tr["reason"] == "TP").mean(), "stop_pct": 100 * (tr["reason"] == "SL").mean(),
            "avg_R": r.mean(), "total_R": r.sum(), "profit_factor": win / lose if lose > 0 else np.inf,
            "avg_R_at_stop_level": tr["r_level"].mean(), "worst_R": r.min(), "avg_loss_R": r[r < 0].mean() if (r < 0).any() else np.nan}


def study_trades(setup, symbols: list, controls: dict, blocks=("A", "C"), universe: str = "boomcrash") -> pd.DataFrame:
    """One row per (block, bias, group) for one setup; blocks also include the pooled "A+C".
    `controls` = {(bias, symbol, block): DataFrame of control trades}."""
    biases = ("h1",) if not setup.uses_bias else study.BIASES
    rows = []
    for bias in biases:
        trades = {(s, b): setup_trades(setup, s, bias, b) for s in symbols for b in blocks}
        for gname, prefix in study.group_defs(universe).items():
            syms = [s for s in symbols if study.in_group(s, prefix)]
            for label, bl in [(b, (b,)) for b in blocks] + [("+".join(blocks), tuple(blocks))]:
                parts = [trades[(s, b)] for s in syms for b in bl if not trades[(s, b)].empty]
                tr = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
                ctrl = pd.concat([controls[(bias, s, b)] for s in syms for b in bl], ignore_index=True)
                row = {"setup": setup.name, "bias": bias, "group": gname, "block": label, **summarize(tr),
                       "control_avg_R": ctrl["r"].mean(), "control_win_pct": 100 * (ctrl["reason"] == "TP").mean(),
                       "control_PF": summarize(ctrl)["profit_factor"]}
                if len(tr) > 1:
                    se = tr["r"].std(ddof=1) / np.sqrt(len(tr))
                    row["z_vs_control"] = (tr["r"].mean() - ctrl["r"].mean()) / se if se > 0 else np.nan
                rows.append(row)
    return pd.DataFrame(rows)
