"""Stage 1: does a pattern predict anything? (docs/SETUP_LIST.md)

For every event (a setup's signal on the close of M15 candle t) we enter AT MARKET at the next open and measure
the net move in the setup's direction after `horizon` candles, in ATR units, spread included. That move is compared
with the average move of ALL comparable moments of the same symbol, direction and block (comparable = same H1
bias condition). The difference is the event's excess. Cells are tested at Z_THRESHOLD standard errors.

Frozen choices (set before any result):
  primary horizon  3 h (12 candles); 1 h (4 candles) is reported but not tested
  clustering       events of one symbol closer than 12 candles count once (the first)
  threshold        z >= 3.2 and at least 300 events in block A, and the same sign in block C
"""
import numpy as np
import pandas as pd

from core.constants import SPLIT, WINDOW_START
from core.context import get_context

HORIZONS = {"1h": 4, "3h": 12}
PRIMARY = "3h"
CLUSTER = 12
Z_THRESHOLD = 3.2
MIN_EVENTS = 300
WARMUP = 250                      # candles ignored at the start of every symbol (ATR and swings settle)
GROUPS = {"all": None, "Boom": "Boom", "Crash": "Crash"}
BIASES = ("none", "h1")
BLOCKS = ("A", "C")


def assert_block_allowed(block: str):
    if block not in BLOCKS:
        raise ValueError(f"Block '{block}' is not available at Stage 1. Block B is only opened by the final verdict.")


def block_mask(ctx, block: str) -> np.ndarray:
    assert_block_allowed(block)
    tc = pd.DatetimeIndex(ctx.t_close)
    idx = np.arange(ctx.n) >= WARMUP
    if block == "A":
        return idx & (tc >= WINDOW_START) & (tc < SPLIT)
    return idx & (tc < WINDOW_START)


def forward(ctx, hbars: int) -> dict:
    """Net moves (ATR units) of a market entry at the open of t+1, exit at the close of t+hbars."""
    key = ("forward", hbars)
    if key in ctx.cache:
        return ctx.cache[key]
    n, o, h, l, c, sp, atr = ctx.n, ctx.o, ctx.h, ctx.l, ctx.c, ctx.sp, ctx.atr
    nan = np.full(n, np.nan)
    ent, spe, ex, spx = nan.copy(), nan.copy(), nan.copy(), nan.copy()
    ent[:-1], spe[:-1] = o[1:], sp[1:]
    ex[:n - hbars], spx[:n - hbars] = c[hbars:], sp[hbars:]
    win_hi, win_lo = nan.copy(), nan.copy()
    sw_h = np.lib.stride_tricks.sliding_window_view(h, hbars)           # row r = h[r : r + hbars]
    sw_l = np.lib.stride_tricks.sliding_window_view(l, hbars)
    win_hi[:n - hbars], win_lo[:n - hbars] = sw_h[1:].max(axis=1), sw_l[1:].min(axis=1)   # candles t+1 .. t+hbars
    ask = ent + spe
    with np.errstate(invalid="ignore", divide="ignore"):
        out = {
            1: {"net": (ex - ask) / atr, "mfe": (win_hi - ask) / atr, "mae": (ask - win_lo) / atr},
            -1: {"net": (ent - (ex + spx)) / atr, "mfe": (ent - win_lo) / atr, "mae": (win_hi - ent) / atr},
        }
    ctx.cache[key] = out
    return out


def cluster(t: np.ndarray) -> np.ndarray:
    """Boolean keep-mask: the first event of every group of events closer than CLUSTER candles."""
    keep = np.zeros(len(t), bool)
    last = -10 ** 9
    for i, v in enumerate(t):
        if v - last >= CLUSTER:
            keep[i] = True
            last = v
    return keep


def symbol_excess(ctx, events: pd.DataFrame, block: str, bias: str) -> dict:
    """Excess results of one symbol's events for one block and bias condition."""
    mask = block_mask(ctx, block)
    ev = events[(events["t"] >= 0) & (events["t"] < ctx.n)]
    ev = ev[mask[ev["t"].to_numpy()]]
    if bias == "h1":
        ev = ev[ctx.h1_dir[ev["t"].to_numpy()] == ev["direction"].to_numpy()]
    ev = ev.sort_values("t")
    ev = ev[cluster(ev["t"].to_numpy())]
    out = {"n": len(ev), "direction": ev["direction"].to_numpy(), "t": ev["t"].to_numpy()}
    for name, hb in HORIZONS.items():
        fw = forward(ctx, hb)
        net = np.full(len(ev), np.nan)
        base = np.full(len(ev), np.nan)
        mfe = np.full(len(ev), np.nan)
        mae = np.full(len(ev), np.nan)
        for d in (1, -1):
            sel = ev["direction"].to_numpy() == d
            if not sel.any():
                continue
            tt = ev["t"].to_numpy()[sel]
            net[sel], mfe[sel], mae[sel] = fw[d]["net"][tt], fw[d]["mfe"][tt], fw[d]["mae"][tt]
            moments = mask & np.isfinite(fw[d]["net"])
            if bias == "h1":
                moments &= ctx.h1_dir == d
            base[sel] = fw[d]["net"][moments].mean() if moments.any() else np.nan
        ok = np.isfinite(net) & np.isfinite(base)
        out[name] = {"net": net[ok], "base": base[ok], "mfe": mfe[ok], "mae": mae[ok], "n": int(ok.sum())}
    return out


def cell_stats(parts: list) -> dict:
    """Pool the per-symbol results of one cell."""
    row = {"n": int(sum(p["n"] for p in parts))}
    for name in HORIZONS:
        net = np.concatenate([p[name]["net"] for p in parts]) if parts else np.array([])
        base = np.concatenate([p[name]["base"] for p in parts]) if parts else np.array([])
        ex = net - base
        n = len(ex)
        se = ex.std(ddof=1) / np.sqrt(n) if n > 1 else np.nan
        row[f"excess_{name}"] = ex.mean() if n else np.nan
        row[f"z_{name}"] = ex.mean() / se if n > 1 and se > 0 else np.nan
        if name == PRIMARY:
            mfe = np.concatenate([p[name]["mfe"] for p in parts]) if parts else np.array([])
            mae = np.concatenate([p[name]["mae"] for p in parts]) if parts else np.array([])
            row["raw_mean"] = net.mean() if n else np.nan
            row["base_mean"] = base.mean() if n else np.nan
            row["win_pct"] = 100 * (net > 0).mean() if n else np.nan
            row["mfe_med"] = np.median(mfe) if n else np.nan
            row["mae_med"] = np.median(mae) if n else np.nan
    return row


def study_setup(setup, symbols: list, blocks=BLOCKS, biases=BIASES) -> pd.DataFrame:
    """All cells of one setup: bias x block x symbol group. Returns one row per cell."""
    if not setup.uses_bias:
        biases = ("h1",)                                  # the bias is part of the definition
    events = {s: setup.detect(get_context(s)) for s in symbols}
    rows = []
    for bias in biases:
        for block in blocks:
            per_symbol = {s: symbol_excess(get_context(s), events[s], block, bias) for s in symbols}
            for gname, prefix in GROUPS.items():
                parts = [p for s, p in per_symbol.items() if prefix is None or s.startswith(prefix)]
                row = {"setup": setup.name, "bias": bias, "block": block, "group": gname,
                       "symbols": len(parts), **cell_stats(parts)}
                rows.append(row)
    return pd.DataFrame(rows)


def verdicts(cells: pd.DataFrame) -> pd.DataFrame:
    """One row per (setup, bias, group): the Stage 1 verdict from blocks A and C."""
    out = []
    for (setup, bias, group), g in cells.groupby(["setup", "bias", "group"], sort=False):
        a = g[g.block == "A"].iloc[0]
        c = g[g.block == "C"].iloc[0] if (g.block == "C").any() else None
        enough = a["n"] >= MIN_EVENTS
        z_ok = bool(enough and a[f"z_{PRIMARY}"] >= Z_THRESHOLD)
        c_ok = bool(c is not None and c[f"excess_{PRIMARY}"] > 0)
        reverse = bool(enough and a[f"z_{PRIMARY}"] <= -Z_THRESHOLD)
        out.append({"setup": setup, "bias": bias, "group": group, "n_A": a["n"],
                    "excess_A": a[f"excess_{PRIMARY}"], "z_A": a[f"z_{PRIMARY}"],
                    "n_C": None if c is None else c["n"], "excess_C": None if c is None else c[f"excess_{PRIMARY}"],
                    "z_C": None if c is None else c[f"z_{PRIMARY}"],
                    "enough_events": enough, "pass_A": z_ok, "same_sign_C": c_ok,
                    "verdict": "PASS" if (z_ok and c_ok) else ("fails C" if z_ok else
                               ("REVERSED (loses at 3.2 SE)" if reverse else ("too few events" if not enough else "no edge")))})
    return pd.DataFrame(out)
