import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN   = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URL     = f"https://api.telegram.org/bot{TOKEN}/sendMessage"


def send(message: str):
    if not TOKEN or not CHAT_ID:
        print(f"[NOTIFIER] Telegram non configure | {message}")
        return
    try:
        requests.post(URL, data={"chat_id": CHAT_ID, "text": message}, timeout=5)
    except Exception as e:
        print(f"[NOTIFIER] Erreur envoi Telegram : {e}")


def notify_start(balance: float, currency: str):
    send(
        f"🤖 Bot démarré\n"
        f"💰 Balance : {balance} {currency}"
    )


def notify_trade_open(symbol: str, direction: str, price: float):
    arrow = "📈" if direction == "buy" else "📉"
    send(
        f"{arrow} Trade ouvert\n"
        f"{'🟢 BUY' if direction == 'buy' else '🔴 SELL'} {symbol}\n"
        f"🎯 Entrée : {price:.3f}"
    )


def notify_trade_close(symbol: str, profit: float, daily_pnl: float):
    if profit >= 0:
        send(
            f"✅ Trade fermé — GAIN\n"
            f"📊 {symbol}\n"
            f"💵 Profit  : +{profit:.2f} $\n"
            f"📈 PnL jour : {daily_pnl:.2f} $"
        )
    else:
        send(
            f"❌ Trade fermé — PERTE\n"
            f"📊 {symbol}\n"
            f"💸 Perte   : {profit:.2f} $\n"
            f"📉 PnL jour : {daily_pnl:.2f} $"
        )


def notify_spike(symbol: str):
    send(
        f"⚡ Spike détecté\n"
        f"📊 {symbol}\n"
        f"⏭️ Trade ignoré"
    )


def notify_max_trades():
    send(
        f"🛑 Limite atteinte\n"
        f"20 trades effectués — bot arrêté pour aujourd'hui"
    )


def notify_stop(daily_pnl: float):
    emoji = "🏆" if daily_pnl >= 0 else "😔"
    send(
        f"{emoji} Bot arrêté\n"
        f"💰 PnL final journalier : {daily_pnl:.2f} $"
    )


def notify_heartbeat():
    send("💓 Bot actif")


def notify_report(report: str):
    send(report)
