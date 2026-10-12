"""Replay of the LIVE EMA technique on the spike-free instruments, over the SAME period as backtesting_1.

The rules are the live bot's: M15 trend (EMA5 > EMA13 > EMA50 or the reverse), M5 EMA5/13 cross on a closed
candle on the right side of EMA50, entry at the open of the next candle, fixed TP and SL, one trade at a time
across all symbols, 2-minute pause on a symbol after a loss, stop for the day at +3 $, risk 0.30 $ per trade,
stop filled at the candle's worst price. The functions come from the live `strategy.py` (imported read-only) and
the trade simulation from backtesting_1, so nothing is re-invented.

Two adaptations for instruments that have no spikes and no drift (stated before running):
  direction  the live bot buys every Crash and sells every Boom because of their drift. Here the direction is the
             M15 trend itself (buy or sell).
  TP / SL    the live bot has fixed values per index. Here: SL = (stops level + spread) x 1.2 points, the rule in
             skills/broker-constraints.md, and TP = SL (the live bot's TP:SL is about 1:1 on average).

Usage : backtest/.venv/Scripts/python.exe backtest/backtesting_2/replay.py validate
        backtest/.venv/Scripts/python.exe backtest/backtesting_2/replay.py run
"""
import importlib.util
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, ROOT)                                    # live modules, imported read-only
import strategy                                             # noqa: E402  (live EMA rules)
from config import TP_CONFIG, SYMBOLS as LIVE_SYMBOLS       # noqa: E402

_spec = importlib.util.spec_from_file_location("bt1", os.path.join(HERE, "..", "backtesting_1", "backtest.py"))
bt1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bt1)                               # simulate_trade, lot_for (generic)

def simulate_trade2(m1, info, direction, te, tp_pts, sl_pts, both="sl"):
    """Same as backtesting_1.simulate_trade, with a choice for a candle that touches BOTH levels (order unknown):
    both='sl' (stop first, the first backtest's rule), 'tp' (target first), 'mix' (average of the two outcomes)."""
    times = m1["time"].to_numpy()
    i0 = np.searchsorted(times, np.datetime64(te.floor("min")), side="left")
    if i0 >= len(m1):
        return None
    pt = info["point"]
    o, h, l, c, sp = (m1[x].to_numpy() for x in ("open", "high", "low", "close", "spread"))
    if direction == "buy":
        entry = o[i0] + sp[i0] * pt
        tp_level, sl_level = entry + tp_pts * pt, entry - sl_pts * pt
    else:
        entry = o[i0]
        tp_level, sl_level = entry - tp_pts * pt, entry + sl_pts * pt
    for i in range(i0, len(m1)):
        ask_off = sp[i] * pt
        if direction == "buy":
            hit_sl, hit_tp, extreme = l[i] <= sl_level, h[i] >= tp_level, l[i]
        else:
            hit_sl, hit_tp, extreme = h[i] + ask_off >= sl_level, l[i] + ask_off <= tp_level, h[i] + ask_off
        base = {"entry": entry, "exit_time": m1["time"].iat[i], "spread_pts": sp[i0]}
        if hit_sl and hit_tp:
            if both == "sl":
                return {**base, "exit": extreme, "reason": "SL", "overshoot_pts": abs(extreme - sl_level) / pt, "ambiguous": True}
            if both == "tp":
                return {**base, "exit": tp_level, "reason": "TP", "overshoot_pts": 0.0, "ambiguous": True}
            return {**base, "exit": (tp_level + extreme) / 2, "reason": "MIX", "overshoot_pts": 0.0, "ambiguous": True}
        if hit_sl:
            return {**base, "exit": extreme, "reason": "SL", "overshoot_pts": abs(extreme - sl_level) / pt, "ambiguous": False}
        if hit_tp:
            return {**base, "exit": tp_level, "reason": "TP", "overshoot_pts": 0.0, "ambiguous": False}
    return {"entry": entry, "exit": c[-1], "exit_time": m1["time"].iat[-1], "reason": "END", "overshoot_pts": 0.0,
            "spread_pts": sp[i0], "ambiguous": False}


BT1_DATA = os.path.join(HERE, "..", "backtesting_1", "data")
SMC_DATA = os.path.join(HERE, "..", "smc", "data")
M1_DATA = os.path.join(HERE, "data")
RESULTS = os.path.join(HERE, "results")

M5, M15 = pd.Timedelta(minutes=5), pd.Timedelta(minutes=15)
LOSS_COOLDOWN = pd.Timedelta(seconds=120)
DAILY_TARGET = 3.0
WARMUP = 100
WINDOW_START = pd.Timestamp("2026-08-03 22:44")             # first M1 candle of the first backtest
WINDOW_END = pd.Timestamp("2026-10-12 08:05")               # last exit of the first backtest
COMMON_START = pd.Timestamp("2026-08-04 07:00")             # the new M1 files start at 06:59: both sides start here


def fname(symbol, tf):
    return f"{symbol.replace(' ', '_')}_{tf}.csv"


def load_frames(symbol, legacy):
    """legacy = the six symbols of the first backtest, read from its own data folder (exact reproduction)."""
    if legacy:
        d1 = d5 = d15 = BT1_DATA
    else:
        d1, d5, d15 = M1_DATA, SMC_DATA, SMC_DATA
    rd = lambda d, tf: pd.read_csv(os.path.join(d, fname(symbol, tf)), parse_dates=["time"])
    return rd(d1, "M1"), rd(d5, "M5"), rd(d15, "M15")


def symbol_info(legacy):
    return json.load(open(os.path.join(BT1_DATA if legacy else SMC_DATA, "symbol_info.json")))


def candidates(symbol, m5, m15, direction_mode, start=None):
    """direction_mode: 'buy' / 'sell' (fixed, like the live bot) or 'trend' (the M15 trend decides)."""
    m5 = strategy.add_emas(m5.copy())
    m15 = strategy.add_emas(m15.copy())
    m5r = m5.to_dict("records")
    m15_avail = (m15["time"] + M15).to_numpy()
    trend = [strategy.trend_from_row(r) for r in m15.to_dict("records")]
    times = m5["time"].to_numpy()
    start = start or WINDOW_START
    out = []
    for k in range(max(WARMUP, 1), len(m5r)):
        t0 = pd.Timestamp(times[k]) + M5
        if t0 < start:
            continue
        j = np.searchsorted(m15_avail, np.datetime64(t0), side="right") - 1
        if j < 0 or trend[j] is None:
            continue
        d = trend[j] if direction_mode == "trend" else direction_mode
        if trend[j] != d or not strategy.signal_from_rows(m5r[k - 1], m5r[k], d):
            continue
        out.append({"symbol": symbol, "direction": d, "t0": t0, "window_end": t0 + M5})
    return out


def auto_tpsl(info, spread_pts):
    sl = int(round((info["stops_level"] + spread_pts) * 1.2))
    return {"tp": sl, "sl": sl}


def run(symbols, legacy, direction_of, tpsl, live_like=True, start=None, end=None, both="sl"):
    """live_like=True: one trade at a time across all symbols, +3 $/day stop (the live bot).
    live_like=False: each symbol on its own (no global lock, no daily stop) for clean per-symbol statistics."""
    end = end or WINDOW_END
    info = symbol_info(legacy)
    frames = {s: load_frames(s, legacy) for s in symbols}
    cands = []
    for s in symbols:
        m1, m5, m15 = frames[s]
        cands += candidates(s, m5, m15, direction_of(s), start)
    order = {s: n for n, s in enumerate(symbols)}
    cands.sort(key=lambda c: (c["t0"], order[c["symbol"]]))

    trades, busy_until, cooldown = [], pd.Timestamp.min, {}
    sym_busy = {}
    daily, stopped = {}, set()
    for c in cands:
        s = c["symbol"]
        if live_like:
            te = max(c["t0"], busy_until, cooldown.get(s, pd.Timestamp.min))
        else:
            te = max(c["t0"], sym_busy.get(s, pd.Timestamp.min), cooldown.get(s, pd.Timestamp.min))
        if te >= c["window_end"] or te > end:
            continue
        day = te.date()
        if live_like and day in stopped:
            continue
        cfg = tpsl[s]
        res = simulate_trade2(frames[s][0], info[s], c["direction"], te, cfg["tp"], cfg["sl"], both)
        if res is None:
            continue
        lot = bt1.lot_for(info[s], cfg["sl"])
        diff = (res["exit"] - res["entry"]) * (1 if c["direction"] == "buy" else -1)
        profit = diff * info[s]["contract_size"] * lot
        planned = lot * cfg["sl"] * info[s]["contract_size"] * info[s]["point"]
        busy_until = res["exit_time"]
        sym_busy[s] = res["exit_time"]
        if profit < 0:
            cooldown[s] = res["exit_time"] + LOSS_COOLDOWN
        daily[day] = daily.get(day, 0.0) + profit
        if live_like and daily[day] >= DAILY_TARGET:
            stopped.add(day)
        trades.append({"symbol": s, "direction": c["direction"], "entry_time": te, "exit_time": res["exit_time"],
                       "lot": lot, "tp_pts": cfg["tp"], "sl_pts": cfg["sl"], "entry": res["entry"], "exit": res["exit"],
                       "reason": res["reason"], "profit": profit, "planned_risk": planned, "r": profit / planned,
                       "overshoot_pts": res["overshoot_pts"], "spread_pts": res["spread_pts"], "ambiguous": res["ambiguous"]})
    return pd.DataFrame(trades)


def summary(df):
    if df.empty:
        return {"trades": 0}
    w, l = df[df.profit > 0], df[df.profit <= 0]
    eq = df.sort_values("exit_time").profit.cumsum()
    return {"trades": len(df), "win_pct": 100 * len(w) / len(df), "avg_win": w.profit.mean() if len(w) else np.nan,
            "avg_loss": l.profit.mean() if len(l) else np.nan,
            "profit_factor": w.profit.sum() / -l.profit.sum() if l.profit.sum() < 0 else np.inf,
            "total_usd": df.profit.sum(), "avg_R": df.r.mean(), "total_R": df.r.sum(),
            "max_dd_usd": (eq.cummax() - eq).max(), "worst_R": df.r.min()}


def legacy_setup():
    syms = list(LIVE_SYMBOLS.values())
    fixed = lambda s: "buy" if s.startswith("Crash") else "sell"
    return syms, fixed, {s: TP_CONFIG[s] for s in syms}


def cmd_validate():
    """The replay on the six original symbols must reproduce backtesting_1's trades exactly."""
    syms, fixed, tpsl = legacy_setup()
    mine = run(syms, True, fixed, tpsl, live_like=True)
    ref = pd.read_csv(os.path.join(HERE, "..", "backtesting_1", "results", "trades_all.csv"))
    print(f"replay: {len(mine)} trades, {mine.profit.sum():+.2f} $   |   backtesting_1: {len(ref)} trades, {ref.profit.sum():+.2f} $")
    ok = len(mine) == len(ref) and abs(mine.profit.sum() - ref.profit.sum()) < 1e-6
    print("(uses simulate_trade2 with both='sl'; the original function gave the same totals before this change)")
    print("MATCH" if ok else "MISMATCH")
    return 0 if ok else 1


def cmd_run():
    os.makedirs(RESULTS, exist_ok=True)
    info = symbol_info(False)
    syms = [s for s, v in info.items() if v.get("group") == "spikefree"]
    tpsl = {}
    for s in syms:
        m15 = pd.read_csv(os.path.join(SMC_DATA, fname(s, "M15")), parse_dates=["time"])
        w = m15[(m15.time >= WINDOW_START) & (m15.time <= WINDOW_END)]
        tpsl[s] = auto_tpsl(info[s], float(np.median(w["spread"])))
    json.dump(tpsl, open(os.path.join(RESULTS, "tpsl_used.json"), "w"), indent=2)
    trend = lambda s: "trend"
    live = run(syms, False, trend, tpsl, live_like=True, start=COMMON_START)
    solo = run(syms, False, trend, tpsl, live_like=False, start=COMMON_START)
    live.to_csv(os.path.join(RESULTS, "trades_live_like.csv"), index=False)
    solo.to_csv(os.path.join(RESULTS, "trades_per_symbol.csv"), index=False)

    # baseline: the six Boom/Crash symbols with the live bot's own settings, same rules, same period
    bsyms, bfixed, btpsl = legacy_setup()
    base_live = run(bsyms, True, bfixed, btpsl, live_like=True, start=COMMON_START)
    base_solo = run(bsyms, True, bfixed, btpsl, live_like=False, start=COMMON_START)
    base_live.to_csv(os.path.join(RESULTS, "trades_boomcrash_live_like.csv"), index=False)
    base_solo.to_csv(os.path.join(RESULTS, "trades_boomcrash_per_symbol.csv"), index=False)
    for rule in ("tp", "mix"):
        run(syms, False, trend, tpsl, live_like=False, start=COMMON_START, both=rule).to_csv(
            os.path.join(RESULTS, f"trades_per_symbol_both_{rule}.csv"), index=False)
        run(bsyms, True, bfixed, btpsl, live_like=False, start=COMMON_START, both=rule).to_csv(
            os.path.join(RESULTS, f"trades_boomcrash_per_symbol_both_{rule}.csv"), index=False)
    print("done:", len(live), "live-like trades,", len(solo), "per-symbol trades on", len(syms), "symbols")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    sys.exit({"validate": cmd_validate, "run": cmd_run}.get(cmd, lambda: print(__doc__) or 2)())
