"""Analyse approfondie des resultats du backtest. Produit des tableaux (texte) et des graphiques.

Usage : .venv/Scripts/python.exe backtest/backtesting_1/analyze.py
"""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = os.path.dirname(__file__)
sys.path.insert(0, HERE)
import backtest as bt
from config import RISK_USD, TP_CONFIG, SYMBOLS

OUT = bt.RESULTS_DIR
os.makedirs(OUT, exist_ok=True)
INFO = json.load(open(os.path.join(bt.DATA_DIR, "symbol_info.json")))
pd.set_option("display.width", 200)


def pf(p):
    loss = -p[p < 0].sum()
    return p[p > 0].sum() / loss if loss > 0 else float("inf")


def section(title):
    print(f"\n{'=' * 70}\n{title}\n{'=' * 70}")


base = bt.run_backtest()
base["day"] = base.entry_time.dt.date
base["dur_min"] = (base.exit_time - base.entry_time).dt.total_seconds() / 60
win, loss = base[base.profit > 0], base[base.profit <= 0]

# ── 1. Vue d'ensemble / anatomie des pertes ───────────────────────────────────
section("1. OVERVIEW")
avg_w, avg_l = win.profit.mean(), -loss.profit.mean()
print(f"trades={len(base)} wins={len(win)} losses={len(loss)} winrate={len(win)/len(base):.3f}")
print(f"total={base.profit.sum():.2f} PF={pf(base.profit):.2f} avg_win={avg_w:.3f} avg_loss={avg_l:.3f}")
print(f"wins needed to pay one loss = {avg_l/avg_w:.2f}")
print(f"break-even win rate = {avg_l/(avg_w+avg_l):.3f}  (actual {len(win)/len(base):.3f})")
print(f"expectancy per trade = {base.profit.mean():.3f}")

section("2. LOSS ANATOMY")
sl = base[base.reason == "SL"].copy()
val = sl.symbol.map(lambda s: INFO[s]["contract_size"] * INFO[s]["point"])
sl["planned"] = -sl.lot * sl.sl_pts * val
sl["extra"] = -(sl.profit - sl.planned)          # perte au dela du SL prevu
sl["spread_cost"] = sl.lot * sl.spread_pts * val
print(f"SL trades={len(sl)}  total loss={sl.profit.sum():.2f}")
print(f"  planned (if SL filled exactly) = {sl.planned.sum():.2f}")
print(f"  extra from jumps past the SL    = {-sl.extra.sum():.2f}  ({sl.extra.sum()/-sl.profit.sum():.0%} of all losses)")
ratio = sl.overshoot_pts / sl.sl_pts
print("overshoot / SL size distribution:")
print(ratio.describe(percentiles=[.5, .75, .9, .95]).round(2).to_string())
for lo, hi in [(0, .1), (.1, .5), (.5, 1), (1, 2), (2, 99)]:
    m = (ratio >= lo) & (ratio < hi)
    print(f"  overshoot {lo}-{hi}x SL: {m.sum():>4} losses, sum={sl.profit[m].sum():8.2f}")
print(f"spread cost on all trades = {(base.lot * base.spread_pts * base.symbol.map(lambda s: INFO[s]['contract_size']*INFO[s]['point'])).sum():.2f}")
print("duration (min):")
print(base.groupby("reason").dur_min.describe()[["count", "mean", "50%", "max"]].round(1).to_string())
print(f"losses hit within the first minute: {(sl.dur_min <= 1).mean():.0%}")

# ── 3. Par symbole ────────────────────────────────────────────────────────────
section("3. PER SYMBOL")
rows = []
for s, g in base.groupby("symbol"):
    m1 = bt._CACHE[("m1", s)]
    pt = INFO[s]["point"]
    cfg = TP_CONFIG[s]
    rows.append({
        "symbol": s, "trades": len(g), "winrate": (g.profit > 0).mean(),
        "avg_win": g.profit[g.profit > 0].mean(), "avg_loss": g.profit[g.profit <= 0].mean(),
        "PF": pf(g.profit), "profit": g.profit.sum(), "worst": g.profit.min(),
        "lot": g.lot.iloc[0], "SL_pts": cfg["sl"],
        "spread/SL%": 100 * g.spread_pts.median() / cfg["sl"],
        "M1range/SL": ((m1.high - m1.low) / pt).median() / cfg["sl"],
        "risk_at_SL$": g.lot.iloc[0] * cfg["sl"] * INFO[s]["contract_size"] * pt,
    })
sym = pd.DataFrame(rows).set_index("symbol").round(3)
print(sym.to_string())
sym.to_csv(os.path.join(OUT, "per_symbol.csv"))

# ── 4. Temps ──────────────────────────────────────────────────────────────────
section("4. WHEN IT LOSES")
base["hour"] = base.entry_time.dt.hour
by_hour = base.groupby("hour").profit.agg(["size", "sum", lambda p: (p > 0).mean()])
by_hour.columns = ["trades", "profit", "winrate"]
print(by_hour.round(2).T.to_string())
base["dow"] = base.entry_time.dt.day_name()
print(base.groupby("dow").profit.agg(["size", "sum"]).round(2).to_string())
base["week"] = base.entry_time.dt.to_period("W").astype(str)
by_week = base.groupby("week").profit.agg(["size", "sum", lambda p: (p > 0).mean()])
by_week.columns = ["trades", "profit", "winrate"]
print(by_week.round(2).to_string())
daily = base.groupby("day").profit.sum()
print(f"days={len(daily)} positive={int((daily > 0).sum())} negative={int((daily < 0).sum())} "
      f"best={daily.max():.2f} worst={daily.min():.2f}")
# series de pertes
streak = best = 0
for p in base.profit:
    streak = streak + 1 if p <= 0 else 0
    best = max(best, streak)
print(f"longest losing streak = {best}")
after_loss = base.profit.shift(1) <= 0
print(f"win rate after a loss = {(base.profit[after_loss] > 0).mean():.3f} | after a win = {(base.profit[~after_loss] > 0).mean():.3f}")

# ── 5. Qualite d'entree ───────────────────────────────────────────────────────
section("5. ENTRY QUALITY")
rows = []
for name, mode in [("full rules (M15 + M5 cross)", "full"), ("no M15 filter", "no_m15"),
                   ("random: every M5 candle", "every_candle")]:
    d = bt.run_backtest(mode=mode)
    rows.append({"entry": name, "trades": len(d), "winrate": (d.profit > 0).mean(),
                 "profit": d.profit.sum(), "per_trade": d.profit.mean(), "PF": pf(d.profit)})
entry = pd.DataFrame(rows).set_index("entry").round(3)
print(entry.to_string())

# Temps depuis le dernier spike (hypothese : le spike est sans memoire)
section("5b. TIME SINCE LAST SPIKE (memoryless test)")
base["since_spike"] = np.nan
for s, g in base.groupby("symbol"):
    m1 = bt._CACHE[("m1", s)]
    rng = (m1.high - m1.low)
    spike_t = m1.time[rng > 8 * rng.median()].to_numpy()
    idx = np.searchsorted(spike_t, g.entry_time.to_numpy(), side="left") - 1   # strictement avant la bougie d'entree
    ok = idx >= 0
    since = np.full(len(g), np.nan)
    since[ok] = (g.entry_time.to_numpy()[ok] - spike_t[idx[ok]]) / np.timedelta64(1, "m")
    base.loc[g.index, "since_spike"] = since
bins = [0, 2, 5, 15, 60, 1e9]
base["since_bin"] = pd.cut(base.since_spike, bins, right=False)
print(base.groupby("since_bin", observed=True).profit.agg(
    trades="size", winrate=lambda p: (p > 0).mean(), per_trade="mean", total="sum").round(3).to_string())

# ── 6. Reglages de sortie : balayage SL x ratio, train / test ─────────────────
section("6. EXIT SETTINGS (SL multiplier x TP:SL ratio)")
t0, t1 = base.entry_time.min(), base.exit_time.max()
mid = t0 + (t1 - t0) / 2
print(f"train: {t0.date()} -> {mid.date()} | test: {mid.date()} -> {t1.date()}")
grid_rows = []
for slm in [1, 1.5, 2, 3, 4]:
    for rr in [0.5, 1, 1.5, 2, 3]:
        tr = bt.run_backtest(sl_mult=slm, tp_sl_ratio=rr, period=(t0, mid))
        te = bt.run_backtest(sl_mult=slm, tp_sl_ratio=rr, period=(mid, t1 + pd.Timedelta(days=1)))
        grid_rows.append({"sl_mult": slm, "tp:sl": rr,
                          "train_profit": tr.profit.sum(), "train_trades": len(tr),
                          "test_profit": te.profit.sum(), "test_trades": len(te),
                          "test_winrate": (te.profit > 0).mean() if len(te) else np.nan})
grid = pd.DataFrame(grid_rows).round(2)
print(grid.to_string(index=False))
grid.to_csv(os.path.join(OUT, "sweep_exit.csv"), index=False)

# ── 7. Regles de gestion ──────────────────────────────────────────────────────
section("7. RISK RULES")
nostop = bt.run_backtest(daily_target=1e9)
print(f"daily +3$ stop ON : trades={len(base)} profit={base.profit.sum():.2f}")
print(f"daily +3$ stop OFF: trades={len(nostop)} profit={nostop.profit.sum():.2f}")
print("risk if SL is hit at planned level vs target "
      f"{RISK_USD}$ -> see per-symbol risk_at_SL$ above")

# ── 8. Direction opposee ──────────────────────────────────────────────────────
section("8. STRUCTURAL TEST: OPPOSITE DIRECTION (Boom buy / Crash sell)")
bt.INVERT = True
rows = []
for slm in [1, 2, 3, 4]:
    for rr in [1, 2, 3]:
        tr = bt.run_backtest(sl_mult=slm, tp_sl_ratio=rr, period=(t0, mid))
        te = bt.run_backtest(sl_mult=slm, tp_sl_ratio=rr, period=(mid, t1 + pd.Timedelta(days=1)))
        rows.append({"sl_mult": slm, "tp:sl": rr, "train_profit": tr.profit.sum(), "train_trades": len(tr),
                     "test_profit": te.profit.sum(), "test_trades": len(te),
                     "test_winrate": (te.profit > 0).mean() if len(te) else np.nan})
inv = pd.DataFrame(rows).round(2)
print(inv.to_string(index=False))
inv.to_csv(os.path.join(OUT, "sweep_inverse.csv"), index=False)
dinv = bt.run_backtest()
print(f"\ninverse with current TP/SL: trades={len(dinv)} winrate={(dinv.profit>0).mean():.3f} profit={dinv.profit.sum():.2f}")
print(dinv.groupby("symbol").profit.agg(["size", "sum"]).round(2).to_string())
bt.INVERT = False

# ── Graphiques ────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(base.exit_time, base.profit.cumsum(), lw=1.2, color="#c0392b")
ax.axhline(0, color="grey", lw=.6)
ax.set(title="Equity curve (all symbols)", ylabel="cumulative profit ($)")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "equity.png"), dpi=120); plt.close(fig)

fig, ax = plt.subplots(figsize=(9, 4))
ax.hist(base.profit, bins=60, color="#34495e")
ax.set(title="Trade result distribution", xlabel="profit per trade ($)", ylabel="trades")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "profit_hist.png"), dpi=120); plt.close(fig)

fig, ax = plt.subplots(figsize=(9, 4))
colors = ["#27ae60" if v > 0 else "#c0392b" for v in sym.profit]
ax.bar([s.replace(" Index", "") for s in sym.index], sym.profit, color=colors)
ax.set(title="Profit by symbol", ylabel="$"); ax.axhline(0, color="grey", lw=.6)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "by_symbol.png"), dpi=120); plt.close(fig)

fig, ax = plt.subplots(figsize=(9, 4))
colors = ["#27ae60" if v > 0 else "#c0392b" for v in by_hour.profit]
ax.bar(by_hour.index, by_hour.profit, color=colors)
ax.set(title="Profit by entry hour (server time)", xlabel="hour", ylabel="$"); ax.axhline(0, color="grey", lw=.6)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "by_hour.png"), dpi=120); plt.close(fig)

pv = grid.pivot(index="sl_mult", columns="tp:sl", values="test_profit")
fig, ax = plt.subplots(figsize=(6, 4))
im = ax.imshow(pv.values, cmap="RdYlGn", aspect="auto")
ax.set_xticks(range(len(pv.columns)), pv.columns); ax.set_yticks(range(len(pv.index)), pv.index)
for i in range(pv.shape[0]):
    for j in range(pv.shape[1]):
        ax.text(j, i, f"{pv.values[i, j]:.0f}", ha="center", va="center", fontsize=8)
ax.set(title="Test-period profit ($)", xlabel="TP:SL ratio", ylabel="SL multiplier")
fig.colorbar(im); fig.tight_layout(); fig.savefig(os.path.join(OUT, "sweep_heatmap.png"), dpi=120); plt.close(fig)
print("\ncharts saved in", OUT)
