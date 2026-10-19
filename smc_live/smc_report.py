"""Daily and weekly summaries per technique, built from trades.csv and signals.csv (no pandas needed)."""
import csv
import os
from collections import Counter, defaultdict
from datetime import date, timedelta

from smc_live import config_smc as cfg


def _rows(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _num(x, default=0.0):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def summarize(log_dir: str, start: date, end: date) -> dict:
    """Per technique, between two dates (inclusive)."""
    out = {t: {"signals": Counter(), "trades": [], } for t in cfg.MAGIC}
    for r in _rows(os.path.join(log_dir, "signals.csv")):
        d = date.fromisoformat(r["time"][:10])
        if start <= d <= end and r["technique"] in out:
            out[r["technique"]]["signals"][r["skip_reason"] if r["status"] == "skipped" else r["status"]] += 1
    for r in _rows(os.path.join(log_dir, "trades.csv")):
        if r.get("technique") in out and start <= date.fromisoformat(r["date"]) <= end:
            out[r["technique"]]["trades"].append(r)
    return out


def _block(title, data, lines):
    lines.append(title)
    for tech, d in data.items():
        trades = d["trades"]
        sig = d["signals"]
        total = sum(sig.values())
        taken = sig.get("traded", 0) + sig.get("alert_only", 0)
        skipped = ", ".join(f"{k} {v}" for k, v in sig.items() if k not in ("traded", "alert_only", "refused"))
        lines.append(f"\n— {cfg.SHORT_TITLE[tech]}")
        lines.append(f"  Signaux : {total} (suivis {taken}" + (f" | ignorés : {skipped}" if skipped else "") + ")")
        if trades:
            wins = sum(1 for t in trades if _num(t["profit"]) >= 0)
            r = [_num(t["r_multiple"]) for t in trades]
            lines.append(f"  Trades fermés : {len(trades)} ({wins} gagnants, {len(trades) - wins} perdants) | "
                         f"{sum(_num(t['profit']) for t in trades):+.2f} $ | {sum(r):+.2f} R | R moyen {sum(r) / len(r):+.2f}")
        else:
            lines.append("  Trades fermés : 0")


def daily_text(log_dir: str, day: date) -> str:
    lines = [f"📋 RAPPORT SMC — {day:%d/%m/%Y}"]
    _block("", summarize(log_dir, day, day), lines)
    return "\n".join(lines)


def weekly_text(log_dir: str, day: date) -> str:
    monday = day - timedelta(days=day.weekday())
    lines = [f"📋 RAPPORT SMC HEBDOMADAIRE — semaine du {monday:%d/%m} au {(monday + timedelta(days=6)):%d/%m/%Y}"]
    data = summarize(log_dir, monday, monday + timedelta(days=6))
    _block("", data, lines)
    all_t = [t for d in data.values() for t in d["trades"]]
    if all_t:
        lines.append(f"\nTotal : {len(all_t)} trades | {sum(_num(t['profit']) for t in all_t):+.2f} $ | "
                     f"{sum(_num(t['r_multiple']) for t in all_t):+.2f} R")
    return "\n".join(lines)
