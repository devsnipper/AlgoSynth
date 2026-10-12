"""Rejoue les regles du bot live sur les donnees historiques (voir PLAN.md).

Usage : .venv/Scripts/python.exe backtest/backtesting_1/backtest.py
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", ".."))

import strategy
from config import SYMBOLS, TP_CONFIG, RISK_USD

DATA_DIR    = os.path.join(HERE, "data")
RESULTS_DIR = os.path.join(HERE, "results")

LOSS_COOLDOWN = pd.Timedelta(seconds=120)   # pause sur le symbole apres une perte
DAILY_TARGET  = 3.0                         # arret du jour quand le PnL atteint +3 $
M5            = pd.Timedelta(minutes=5)
M15           = pd.Timedelta(minutes=15)
WARMUP        = 100                         # candles M5 ignorees au debut (EMA stables)


INVERT = False   # True = test de la direction opposee (Boom achat, Crash vente)


def direction_of(symbol: str) -> str:
    d = "buy" if symbol.startswith("Crash") else "sell"
    if INVERT:
        d = "sell" if d == "buy" else "buy"
    return d


def load(symbol: str, tf: str) -> pd.DataFrame:
    path = os.path.join(DATA_DIR, f"{symbol.replace(' ', '_')}_{tf}.csv")
    return pd.read_csv(path, parse_dates=["time"])


def find_candidates(symbol: str, start: pd.Timestamp, mode: str = "full") -> list[dict]:
    """Signaux valides : tendance M15 OK + croisement M5 sur bougie fermee.
    Le bot entre des l'ouverture de la bougie M5 suivante (t0) et jusqu'a
    la fin de cette bougie (t0 + 5 min) tant que le signal est encore le dernier.

    mode : "full" = regles du bot live ; "no_m15" = sans filtre tendance M15 ;
           "every_candle" = entree a chaque bougie M5, sans aucun filtre (reference aleatoire)."""
    direction = direction_of(symbol)

    m5  = strategy.add_emas(load(symbol, "M5"))
    m15 = strategy.add_emas(load(symbol, "M15"))
    m5r, m15r = m5.to_dict("records"), m15.to_dict("records")

    # une bougie M15 est utilisable une fois fermee
    m15_avail = (m15["time"] + M15).to_numpy()
    m15_trend = [strategy.trend_from_row(r) for r in m15r]

    out = []
    for k in range(max(WARMUP, 1), len(m5r)):
        if mode != "every_candle" and not strategy.signal_from_rows(m5r[k - 1], m5r[k], direction):
            continue
        t0 = m5.at[k, "time"] + M5                      # fermeture de la bougie signal
        if t0 < start:
            continue
        if mode == "full":
            j = np.searchsorted(m15_avail, np.datetime64(t0), side="right") - 1
            if j < 0 or m15_trend[j] != direction:
                continue
        out.append({"symbol": symbol, "direction": direction, "t0": t0, "window_end": t0 + M5})
    return out


def lot_for(info: dict, sl_points: int) -> float:
    val_pt  = info["contract_size"] * info["point"]
    lot_raw = RISK_USD / (sl_points * val_pt) if val_pt > 0 else info["volume_min"]
    return max(info["volume_min"], round(lot_raw / info["volume_step"]) * info["volume_step"])


def simulate_trade(m1: pd.DataFrame, info: dict, direction: str, te: pd.Timestamp,
                   tp_pts: int, sl_pts: int):
    """Entre a l'ouverture de la bougie M1 de te, suit les bougies M1 jusqu'au TP/SL.
    Retourne un dict (entry, exit, exit_time, reason) ou None si pas de donnees."""
    times = m1["time"].to_numpy()
    i0 = np.searchsorted(times, np.datetime64(te.floor("min")), side="left")
    if i0 >= len(m1):
        return None

    pt = info["point"]
    o, h, l, c, sp = (m1[x].to_numpy() for x in ("open", "high", "low", "close", "spread"))

    # Les bougies MT5 sont en prix bid. Achat a l'ask (bid + spread), vente au bid.
    if direction == "buy":
        entry    = o[i0] + sp[i0] * pt
        tp_level = entry + tp_pts * pt
        sl_level = entry - sl_pts * pt
    else:
        entry    = o[i0]
        tp_level = entry - tp_pts * pt
        sl_level = entry + sl_pts * pt

    for i in range(i0, len(m1)):
        ask_off = sp[i] * pt
        if direction == "buy":
            hit_sl = l[i] <= sl_level
            hit_tp = h[i] >= tp_level
            extreme = l[i]
        else:
            hit_sl = h[i] + ask_off >= sl_level
            hit_tp = l[i] + ask_off <= tp_level
            extreme = h[i] + ask_off

        # TP et SL dans la meme bougie : on compte la perte (hypothese prudente)
        if hit_sl:
            # Un spike saute le SL : le fill se fait au prix atteint, pas au niveau du SL.
            # On prend l'extreme de la bougie (pire cas, proche du live).
            exit_p = extreme
            return {"entry": entry, "exit": exit_p, "exit_time": m1["time"].iat[i], "reason": "SL",
                    "overshoot_pts": abs(exit_p - sl_level) / pt, "spread_pts": sp[i0]}
        if hit_tp:
            return {"entry": entry, "exit": tp_level, "exit_time": m1["time"].iat[i], "reason": "TP",
                    "overshoot_pts": 0.0, "spread_pts": sp[i0]}

    return {"entry": entry, "exit": c[-1], "exit_time": m1["time"].iat[-1], "reason": "END",
            "overshoot_pts": 0.0, "spread_pts": sp[i0]}


_CACHE = {}


def run_backtest(tp_override=None, sl_override=None, tp_sl_ratio=None, sl_mult=None,
                 daily_target=DAILY_TARGET, symbols=None, mode="full",
                 period=None) -> pd.DataFrame:
    """tp_override / sl_override : points fixes pour tous les symboles.
    sl_mult : multiplie le SL de config.py. tp_sl_ratio : TP = SL * ratio.
    mode : voir find_candidates. period : (debut, fin) pour limiter les entrees."""
    with open(os.path.join(DATA_DIR, "symbol_info.json")) as f:
        sym_info = json.load(f)

    symbols = symbols or list(SYMBOLS.values())
    for s in symbols:
        if ("m1", s) not in _CACHE:
            _CACHE[("m1", s)] = load(s, "M1")
    m1_data = {s: _CACHE[("m1", s)] for s in symbols}
    start = max(df["time"].iloc[0] for df in m1_data.values())   # debut commun des donnees M1
    end   = min(df["time"].iloc[-1] for df in m1_data.values())

    cands = []
    for s in symbols:
        if (mode, s, INVERT) not in _CACHE:
            _CACHE[(mode, s, INVERT)] = find_candidates(s, start, mode)
        cands += _CACHE[(mode, s, INVERT)]
    if period:
        cands = [c for c in cands if period[0] <= c["t0"] < period[1]]
    order = {s: n for n, s in enumerate(symbols)}
    cands.sort(key=lambda c: (c["t0"], order[c["symbol"]]))

    trades, busy_until, cooldown = [], pd.Timestamp.min, {}
    daily_pnl, stopped_day = {}, set()

    for c in cands:
        s = c["symbol"]
        # Le bot ne gere qu'un trade a la fois (monitor_trade bloque la boucle)
        te = max(c["t0"], busy_until, cooldown.get(s, pd.Timestamp.min))
        if te >= c["window_end"] or te > end:
            continue
        day = te.date()
        if day in stopped_day:
            continue

        cfg = TP_CONFIG[s]
        sl  = sl_override or (round(cfg["sl"] * sl_mult) if sl_mult else cfg["sl"])
        tp  = tp_override or (round(sl * tp_sl_ratio) if tp_sl_ratio else cfg["tp"])
        res = simulate_trade(m1_data[s], sym_info[s], c["direction"], te, tp, sl)
        if res is None:
            continue

        lot    = lot_for(sym_info[s], sl)
        diff   = (res["exit"] - res["entry"]) * (1 if c["direction"] == "buy" else -1)
        profit = diff * sym_info[s]["contract_size"] * lot

        busy_until = res["exit_time"]
        if profit < 0:
            cooldown[s] = res["exit_time"] + LOSS_COOLDOWN
        daily_pnl[day] = daily_pnl.get(day, 0.0) + profit
        if daily_pnl[day] >= daily_target:
            stopped_day.add(day)

        trades.append({
            "symbol": s, "direction": c["direction"], "entry_time": te,
            "exit_time": res["exit_time"], "lot": lot, "tp_pts": tp, "sl_pts": sl,
            "entry": res["entry"], "exit": res["exit"], "reason": res["reason"],
            "profit": profit,
            "overshoot_pts": res["overshoot_pts"], "spread_pts": res["spread_pts"],
        })

    return pd.DataFrame(trades)


def summarize(df: pd.DataFrame) -> str:
    if df.empty:
        return "Aucun trade."
    wins, losses = df[df.profit > 0], df[df.profit <= 0]
    gross_loss = -losses.profit.sum()
    pf = wins.profit.sum() / gross_loss if gross_loss > 0 else float("inf")
    equity = df.profit.cumsum()
    max_dd = (equity.cummax() - equity).max()

    lines = [
        f"Periode        : {df.entry_time.min()} -> {df.exit_time.max()}",
        f"Trades         : {len(df)}  (gagnes {len(wins)}, perdus {len(losses)})",
        f"Win rate       : {len(wins) / len(df):.1%}",
        f"Profit total   : {df.profit.sum():+.2f} $",
        f"Profit factor  : {pf:.2f}",
        f"Drawdown max   : {max_dd:.2f} $",
        f"Sorties        : {df.reason.value_counts().to_dict()}",
        "",
        "Par symbole :",
    ]
    by = df.groupby("symbol").agg(trades=("profit", "size"),
                                  win_rate=("profit", lambda p: (p > 0).mean()),
                                  profit=("profit", "sum")).round(2)
    lines.append(by.to_string())
    return "\n".join(lines)


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    df = run_backtest()
    df.to_csv(os.path.join(RESULTS_DIR, "trades_all.csv"), index=False)
    print(summarize(df))


if __name__ == "__main__":
    main()
