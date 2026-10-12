"""Side-by-side comparison of the live EMA technique: Boom/Crash (what the bot trades) vs the spike-free indices.

Usage : backtest/.venv/Scripts/python.exe backtest/backtesting_2/compare.py
"""
import json
import os

import numpy as np
import pandas as pd

import replay

R = replay.RESULTS
FAMILY = {"Step": "Step Index", "Range Break": "Range Break", "Multi Step": "Multi Step", "Volatility": "Volatility"}
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 30)


def family(symbol):
    for k, v in FAMILY.items():
        if symbol.startswith(k):
            return v
    return "Boom/Crash"


def table(df, by=None):
    rows = []
    groups = [("all", df)] if by is None else list(df.groupby(by))
    for name, g in groups:
        s = replay.summary(g)
        rows.append({"group": name, **s})
    return pd.DataFrame(rows)


def main():
    live = pd.read_csv(os.path.join(R, "trades_live_like.csv"), parse_dates=["entry_time", "exit_time"])
    solo = pd.read_csv(os.path.join(R, "trades_per_symbol.csv"), parse_dates=["entry_time", "exit_time"])
    b_live = pd.read_csv(os.path.join(R, "trades_boomcrash_live_like.csv"), parse_dates=["entry_time", "exit_time"])
    b_solo = pd.read_csv(os.path.join(R, "trades_boomcrash_per_symbol.csv"), parse_dates=["entry_time", "exit_time"])
    tpsl = json.load(open(os.path.join(R, "tpsl_used.json")))
    for d in (live, solo, b_live, b_solo):
        d["family"] = d.symbol.map(family)

    cols = ["trades", "win_pct", "avg_win", "avg_loss", "profit_factor", "total_usd", "avg_R", "total_R", "max_dd_usd", "worst_R"]
    out = []
    print("=== A. As the live bot runs it (one trade at a time, +3 $/day stop), same period ===")
    a = pd.concat([table(b_live).assign(group="Boom/Crash (6 symbols, live settings)"),
                   table(live).assign(group="Spike-free (14 symbols, adapted)")])
    print(a[["group"] + cols].round(3).to_string(index=False))
    out.append(("A_live_like", a))

    print("\n=== B. Each symbol on its own (no global lock, no daily stop): by family ===")
    b = pd.concat([table(b_solo, "family"), table(solo, "family")])
    print(b[["group"] + cols].round(3).to_string(index=False))
    out.append(("B_by_family", b))

    print("\n=== C. Each symbol on its own: every symbol ===")
    c = pd.concat([table(b_solo, "symbol"), table(solo, "symbol")])
    c["tp_sl_pts"] = c.group.map(lambda s: tpsl.get(s, {}).get("sl", np.nan))
    print(c[["group", "tp_sl_pts", "trades", "win_pct", "avg_R", "total_R", "profit_factor", "worst_R"]].round(3).to_string(index=False))
    out.append(("C_by_symbol", c))

    print("\n=== D. Loss anatomy (per-symbol runs): average winning and losing trade in R ===")
    for name, d in (("Boom/Crash", b_solo), ("Spike-free", solo)):
        w, l = d[d.r > 0], d[d.r <= 0]
        be = -l.r.mean() / (w.r.mean() - l.r.mean())
        print(f"{name:<11} avg win {w.r.mean():+.3f} R | avg loss {l.r.mean():+.3f} R | wins needed per loss {-l.r.mean() / w.r.mean():.2f} | "
              f"break-even win rate {100 * be:.1f}% | actual {100 * (d.r > 0).mean():.1f}% | stops hit {100 * (d.reason == 'SL').mean():.0f}%")

    print("\n=== E. Planned risk vs the 0.30 $ target (minimum lots) ===")
    for name, d in (("Boom/Crash", b_solo), ("Spike-free", solo)):
        pr = d.groupby("symbol").planned_risk.first()
        print(f"{name:<11} planned risk per trade: min {pr.min():.2f} $, median {pr.median():.2f} $, max {pr.max():.2f} $")

    print("\n=== F. Bracket for candles that touch BOTH stop and target (order unknown) - per-symbol runs ===")
    rows = []
    for label, suffix in (("stop first (pessimistic, first backtest's rule)", ""), ("average of both outcomes", "_both_mix"),
                          ("target first (optimistic)", "_both_tp")):
        for name, file in (("Boom/Crash", f"trades_boomcrash_per_symbol{suffix}.csv"), ("Spike-free", f"trades_per_symbol{suffix}.csv")):
            d = pd.read_csv(os.path.join(R, file))
            d["family"] = d.symbol.map(family)
            w, l = d[d.r > 0], d[d.r <= 0]
            rows.append({"markets": name, "rule": label, "trades": len(d), "ambiguous_pct": 100 * d.ambiguous.mean(),
                         "win_pct": 100 * (d.r > 0).mean(), "avg_R": d.r.mean(),
                         "profit_factor": w.r.sum() / -l.r.sum() if l.r.sum() < 0 else np.inf})
            if name == "Spike-free":
                for fam, g in d.groupby("family"):
                    wf, lf = g[g.r > 0], g[g.r <= 0]
                    rows.append({"markets": "  " + fam, "rule": label, "trades": len(g), "ambiguous_pct": 100 * g.ambiguous.mean(),
                                 "win_pct": 100 * (g.r > 0).mean(), "avg_R": g.r.mean(),
                                 "profit_factor": wf.r.sum() / -lf.r.sum() if lf.r.sum() < 0 else np.inf})
    f = pd.DataFrame(rows)
    print(f.round(3).to_string(index=False))
    out.append(("F_bracket", f))

    for name, df in out:
        df.to_csv(os.path.join(R, f"compare_{name}.csv"), index=False)


if __name__ == "__main__":
    main()
