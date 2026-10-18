"""P2: replay the three live techniques on history, with the live risk rules, to calibrate frequency and caps.

It uses the SAME `techniques/` code that the live bot will run (imported read only), M5 candles for fills, and the rules
of docs/LIVE_SMC_BUILD_PLAN.md: market entry at the open of the first M5 candle after the trigger, SL/TP as given by the
signal, stop filled at the candle's worst price, a candle that touches both levels counts as a stop, 24 h time stop,
minimum stop distance, spread guard, risk target RISK_USD per trade with the broker's minimum lot, skip when the lot risk
is above MAX_RISK_USD, one SMC position per symbol, 4 open at once, 3 entries per day, pause for the week after -4 R.

Usage : backtest/.venv/Scripts/python.exe backtest/smc/tools/replay_live_techniques.py
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ROOT)
from techniques import registry                                      # noqa: E402  (live code, read only)
from techniques.base import Snapshot                                  # noqa: E402

DATA = os.path.join(HERE, "..", "data")
OUT = os.path.join(HERE, "..", "reports", "live_replay")
SYMBOLS = ["Boom 150 Index", "Boom 500 Index", "Boom 600 Index", "Boom 900 Index", "Crash 150 Index", "Crash 500 Index"]

RISK_USD, MAX_RISK_USD = 5.0, 12.0                # dollars; override: --risk 5 --max-risk 12
for _i, _a in enumerate(sys.argv):
    if _a == "--risk":
        RISK_USD = float(sys.argv[_i + 1])
    if _a == "--max-risk":
        MAX_RISK_USD = float(sys.argv[_i + 1])
HOLD = pd.Timedelta(hours=24)
SPREAD_MAX_FRAC = 0.25
MAX_OPEN, MAX_PER_DAY, WEEK_BREAKER_R = 4, 3, -4.0
M5 = pd.Timedelta(minutes=5)


def load(sym):
    info = json.load(open(os.path.join(DATA, "symbol_info.json")))[sym]
    rd = lambda tf: pd.read_csv(os.path.join(DATA, f"{sym.replace(' ', '_')}_{tf}.csv"), parse_dates=["time"])
    return info, Snapshot(sym, info["point"], info["stops_level"], rd("M15"), rd("H1"), rd("H4")), rd("M5")


def simulate(sig, m5, point):
    """Fill at the next M5 open, then follow SL / TP / time stop. Returns a dict or a skip reason string."""
    t = m5["time"].to_numpy()
    i0 = int(np.searchsorted(t, np.datetime64(sig.trigger_time), side="left"))
    if i0 >= len(m5):
        return "no_data"
    o, h, l, c = (m5[x].to_numpy() for x in ("open", "high", "low", "close"))
    sp = m5["spread"].to_numpy() * point
    d = sig.direction
    entry = o[i0] + sp[i0] if d == 1 else o[i0]                    # buy at the ask, sell at the bid
    if (sig.sl - entry) * d >= 0 or (sig.tp - entry) * d <= 0:
        return "gap_through_levels"
    risk = abs(entry - sig.sl)
    last = min(int(np.searchsorted(t, t[i0] + np.timedelta64(int(HOLD.total_seconds()), "s"), side="left")), len(m5)) - 1
    reason, j, exit_px = "TIME", last, c[last] + (sp[last] if d == -1 else 0.0)
    for k in range(i0, last + 1):
        if d == 1:
            hit_sl, hit_tp, ext = l[k] <= sig.sl, h[k] >= sig.tp, l[k]
        else:
            hit_sl, hit_tp, ext = h[k] + sp[k] >= sig.sl, l[k] + sp[k] <= sig.tp, h[k] + sp[k]
        if hit_sl:
            reason, j, exit_px = "SL", k, ext
            break
        if hit_tp and k > i0:
            reason, j, exit_px = "TP", k, sig.tp
            break
    return {"fill_time": pd.Timestamp(t[i0]), "exit_time": pd.Timestamp(t[j]) + M5, "entry": entry, "exit": exit_px,
            "reason": reason, "risk_price": risk, "r": d * (exit_px - entry) / risk, "spread_pts": float(m5["spread"].iloc[i0])}


def prefilter(sig, info, spread_pts):
    """The risk rules that do not depend on other trades. Returns (reason or None, lot, risk_usd)."""
    pt = info["point"]
    risk = sig.risk_price
    if risk / pt < (info["stops_level"] + spread_pts) * 1.2:
        return "stop_too_tight", 0.0, 0.0
    if spread_pts * pt > SPREAD_MAX_FRAC * risk:
        return "spread_too_wide", 0.0, 0.0
    val = info["contract_size"]
    lot = max(info["volume_min"], np.floor(RISK_USD / (risk * val) / info["volume_step"]) * info["volume_step"])
    risk_usd = lot * risk * val
    if risk_usd > MAX_RISK_USD:
        return "min_lot_risk_too_high", lot, risk_usd
    return None, lot, risk_usd


def pf(r):
    w, lo = r[r > 0].sum(), -r[r < 0].sum()
    return w / lo if lo > 0 else np.inf


def main():
    os.makedirs(OUT, exist_ok=True)
    rows, start, end = [], None, None
    for sym in SYMBOLS:
        info, snap, m5 = load(sym)
        lo, hi = m5["time"].iloc[0], m5["time"].iloc[-1] - HOLD
        start = lo if start is None else max(start, lo)
        end = hi if end is None else min(end, hi)
        for tech in registry.ACTIVE:
            rank = [t.name for t in registry.ACTIVE].index(tech.name)
            for sig in tech.signals(snap):
                if not (m5["time"].iloc[0] <= sig.trigger_time <= m5["time"].iloc[-1] - HOLD):
                    continue
                sp = float(snap.m15["spread"].iloc[sig.trigger_idx])
                why, lot, risk_usd = prefilter(sig, info, sp)
                res = simulate(sig, m5, info["point"]) if why is None else None
                if isinstance(res, str):
                    why, res = res, None
                rows.append({"signal_id": sig.signal_id, "technique": tech.name, "rank": rank, "symbol": sym,
                             "time": sig.trigger_time, "direction": sig.direction, "rr_planned": sig.rr, "lot": lot,
                             "risk_usd": risk_usd, "prefilter": why, **(res or {})})
    df = pd.DataFrame(rows).sort_values(["time", "rank"]).reset_index(drop=True)
    start, end = max(start, df.time.min()), end
    df = df[(df.time >= start) & (df.time <= end)].reset_index(drop=True)
    weeks = (end - start).days / 7
    df["r_usd"] = df.r * df.risk_usd

    # ---- capped pipeline: the live rules across techniques and symbols
    status, open_trades, closed, day_count = [], [], [], {}
    paused_week = None
    for i, s in df.iterrows():
        if isinstance(s.prefilter, str):               # (NaN is truthy in Python, so test the type)
            status.append(s.prefilter)
            continue
        now = s.time
        closed += [(t["exit"], t["r"]) for t in open_trades if t["exit"] <= now]
        open_trades = [t for t in open_trades if t["exit"] > now]
        week = (now - pd.Timedelta(days=now.weekday())).date()
        week_r = sum(r for ex, r in closed if (ex - pd.Timedelta(days=ex.weekday())).date() == week)
        day = now.date()
        if week_r <= WEEK_BREAKER_R:
            status.append("weekly_breaker")
        elif any(t["symbol"] == s.symbol for t in open_trades):
            status.append("symbol_busy")
        elif len(open_trades) >= MAX_OPEN:
            status.append("max_open")
        elif day_count.get(day, 0) >= MAX_PER_DAY:
            status.append("max_per_day")
        else:
            status.append("TRADED")
            day_count[day] = day_count.get(day, 0) + 1
            open_trades.append({"symbol": s.symbol, "exit": s.exit_time, "r": s.r})
    df["status"] = status
    df.to_csv(os.path.join(OUT, "replay_signals.csv"), index=False)

    traded = df[df.status == "TRADED"]
    lines = [f"# Live techniques replayed on history\n",
             f"Window: {start:%Y-%m-%d} to {end:%Y-%m-%d} ({weeks:.0f} weeks), the bot's six symbols, M5 fills, rules of the plan.\n",
             "## Signals and what happens to them\n",
             "| Technique | Signals | Per week (6 symbols) | Rejected by risk rules | Capped out | Traded | Traded per week |",
             "|---|---|---|---|---|---|---|"]
    for name in [t.name for t in registry.ACTIVE]:
        g = df[df.technique == name]
        rej = int(g.prefilter.notna().sum())
        cap = int(((g.prefilter.isna()) & (g.status != "TRADED")).sum())
        tr = int((g.status == "TRADED").sum())
        lines.append(f"| {name} | {len(g)} | {len(g) / weeks:.1f} | {rej} | {cap} | {tr} | {tr / weeks:.2f} |")
    lines += ["", f"All techniques together: {len(traded)} trades in {weeks:.0f} weeks = {len(traded) / weeks:.2f} per week.", "",
              "Reasons signals did not trade:", ""]
    lines += [f"- {k}: {v}" for k, v in df[df.status != "TRADED"].status.value_counts().items()]

    def block(title, d):
        out = [f"\n## {title}\n", "| Technique | Trades | Win % | Avg R | Total R | Profit factor | Worst R | Total $ |",
               "|---|---|---|---|---|---|---|---|"]
        for name in [t.name for t in registry.ACTIVE] + ["ALL"]:
            g = d if name == "ALL" else d[d.technique == name]
            g = g[g.r.notna()]
            if len(g) == 0:
                continue
            out.append(f"| {name} | {len(g)} | {100 * (g.r > 0).mean():.1f} | {g.r.mean():+.3f} | {g.r.sum():+.1f} | "
                       f"{pf(g.r):.2f} | {g.r.min():.1f} | {g.r_usd.sum():+.1f} |")
        return out

    lines += block("Results of the trades the live rules would take (capped)", traded)
    lines += block("Results of every signal that passes the risk rules, each technique on its own (no caps; larger sample)",
                   df[df.prefilter.isna()])
    ok = df[df.prefilter.isna() & df.r.notna()]
    lines += ["\n## Exits (every signal that passes the risk rules)\n", ""]
    for name in [t.name for t in registry.ACTIVE]:
        g = ok[ok.technique == name]
        if len(g):
            vc = g.reason.value_counts(normalize=True) * 100
            lines.append(f"- {name}: " + ", ".join(f"{k} {v:.0f}%" for k, v in vc.items()) + f"; average risk {g.risk_usd.mean():.2f} $")
    if len(traded):
        wk = traded.groupby((traded.time - pd.to_timedelta(traded.time.dt.weekday, unit="D")).dt.date).size()
        lines += ["", f"Trades per week under the caps: mean {wk.mean():.1f}, median {wk.median():.0f}, max {wk.max()} "
                      f"(weeks with at least one trade: {len(wk)} of {weeks:.0f})."]
        by_sym = traded.groupby("symbol").agg(trades=("r", "size"), avg_R=("r", "mean"), total_R=("r", "sum")).round(2)
        lines += ["", "By symbol (capped trades):", "", by_sym.to_markdown()]
    open(os.path.join(OUT, "replay_report.md"), "w", encoding="utf-8").write("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
