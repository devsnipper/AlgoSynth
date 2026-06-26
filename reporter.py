import csv
import os
from datetime import datetime, date, timedelta
import calendar

LOG_FILE = os.path.join(os.path.dirname(__file__), "logs", "trades.csv")

POINTS_PER_PIP = {
    "Crash 1000 Index.0": 1.0,
    "Boom 1000 Index.0":  1.0,
    "Crash 1000 Index":   1.0,
    "Boom 1000 Index":    1.0,
}


def _read_trades():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r") as f:
        reader = csv.DictReader(f)
        return list(reader)


def _calc_pips(row):
    entry     = float(row["entry"])
    exit_     = float(row["exit"])
    direction = row["direction"]
    diff      = (exit_ - entry) if direction == "buy" else (entry - exit_)
    point     = POINTS_PER_PIP.get(row["symbol"], 1.0)
    return round(diff / point, 1)


def _filter_by_period(trades, date_from: date, date_to: date):
    result = []
    for t in trades:
        d = datetime.strptime(t["date"], "%Y-%m-%d").date()
        if date_from <= d <= date_to:
            result.append(t)
    return result


def _build_stats(trades):
    stats        = {}
    total_pips   = 0.0
    total_profit = 0.0

    for t in trades:
        sym    = t["symbol"]
        profit = float(t["profit"])
        pips   = _calc_pips(t)

        if sym not in stats:
            stats[sym] = {"wins": 0, "losses": 0, "profit": 0.0, "pips": 0.0}

        if profit >= 0:
            stats[sym]["wins"]   += 1
        else:
            stats[sym]["losses"] += 1

        stats[sym]["profit"] += profit
        stats[sym]["pips"]   += pips
        total_profit         += profit
        total_pips           += pips

    return stats, total_profit, total_pips


def _format_report(title: str, trades, date_label: str) -> str:
    if not trades:
        return f"{title}\n📅 {date_label}\n\nAucun trade effectue."

    stats, total_profit, total_pips = _build_stats(trades)
    lines = [title, f"📅 {date_label}", f"📊 Total trades : {len(trades)}", ""]

    for sym, s in stats.items():
        short   = "Crash 1000" if "Crash" in sym else "Boom 1000"
        total   = s["wins"] + s["losses"]
        winrate = round(s["wins"] / total * 100) if total > 0 else 0
        pnl_emoji = "✅" if s["profit"] >= 0 else "❌"
        pip_emoji = "📈" if s["pips"] >= 0 else "📉"
        lines.append(f"— {short}")
        lines.append(f"  Trades  : {total}  ({s['wins']}W / {s['losses']}L)  {winrate}%")
        lines.append(f"  {pnl_emoji} Profit : {s['profit']:+.2f} $")
        lines.append(f"  {pip_emoji} Pips   : {s['pips']:+.1f}")
        lines.append("")

    pnl_emoji = "🏆" if total_profit >= 0 else "😔"
    lines.append(f"{pnl_emoji} PnL total  : {total_profit:+.2f} $")
    lines.append(f"📍 Pips total : {total_pips:+.1f}")

    return "\n".join(lines)


def daily_report(for_date: date = None) -> str:
    if for_date is None:
        for_date = date.today()
    trades = _filter_by_period(_read_trades(), for_date, for_date)
    label  = for_date.strftime("%d/%m/%Y")
    return _format_report("📋 RAPPORT JOURNALIER", trades, label)


def weekly_report(for_date: date = None) -> str:
    if for_date is None:
        for_date = date.today()
    monday = for_date - timedelta(days=for_date.weekday())
    sunday = monday + timedelta(days=6)
    trades = _filter_by_period(_read_trades(), monday, sunday)
    label  = f"Semaine du {monday.strftime('%d/%m')} au {sunday.strftime('%d/%m/%Y')}"
    return _format_report("📋 RAPPORT HEBDOMADAIRE", trades, label)


def monthly_report(for_date: date = None) -> str:
    if for_date is None:
        for_date = date.today()
    first  = for_date.replace(day=1)
    last   = for_date.replace(day=calendar.monthrange(for_date.year, for_date.month)[1])
    trades = _filter_by_period(_read_trades(), first, last)
    label  = for_date.strftime("%B %Y")
    return _format_report("📋 RAPPORT MENSUEL", trades, label)


def load_today_trade_count() -> int:
    """Recharge le nombre de trades deja faits aujourd'hui au demarrage du bot."""
    trades = _filter_by_period(_read_trades(), date.today(), date.today())
    return len(trades)
