"""Telegram messages of the SMC system. Send only: it never polls getUpdates, so it cannot clash with any other bot
that uses the same token. The message builders are pure functions (easy to test); Notifier does the sending.
"""
import os

import requests

from smc_live import config_smc as cfg


def _side(d):
    return "🟢 ACHAT" if d == 1 else "🔴 VENTE"


def _fmt(x, digits=3):
    return f"{x:.{digits}f}"


def signal_message(sig, plan, mode_execute: bool, digits=3) -> str:
    title = cfg.SHORT_TITLE.get(sig.technique, sig.technique)
    bias = {1: "haussier", -1: "baissier", 0: "—"}.get(sig.bias_dir, "—")
    return (f"📡 SIGNAL SMC — {title}\n"
            f"{_side(sig.direction)} {sig.symbol}\n"
            f"🎯 Entrée ≈ {_fmt(plan.price, digits)}\n"
            f"🛑 SL : {_fmt(plan.sl, digits)}  (risque {_fmt(plan.risk_price, digits)})\n"
            f"✅ TP : {_fmt(plan.tp, digits)}  (RR 1:{plan.rr:.1f})\n"
            f"💵 Risque ≈ {plan.risk_usd:.2f} $ | lot {plan.volume:g}\n"
            f"🧭 Biais H4 : {bias} | zone {_fmt(sig.zone_lo, digits)}–{_fmt(sig.zone_hi, digits)}\n"
            f"📝 {sig.notes}\n"
            f"🆔 {sig.signal_id}\n"
            f"{'⚡ Ordre envoyé à l’instant' if mode_execute else '👁️ Mode alerte seule : aucun ordre envoyé'}")


def executed_message(plan, result) -> str:
    where = "SL et TP posés côté serveur" if result.tp_server else "SL côté serveur, TP surveillé par le bot"
    return (f"✅ ORDRE EXÉCUTÉ — {plan.symbol}\n"
            f"{_side(plan.direction)} | ticket {result.ticket}\n"
            f"💱 Prix de remplissage : {result.price:.3f}\n"
            f"🛡️ {where}\n"
            f"🆔 {plan.signal_id}")


def refused_message(plan, result) -> str:
    return (f"❌ ORDRE REFUSÉ — {plan.symbol}\n"
            f"Code {result.retcode} : {result.comment}\n"
            f"🆔 {plan.signal_id}")


def skipped_message(sig, reason: str) -> str:
    return (f"⏭️ Signal ignoré — {cfg.LETTER.get(sig.technique, '?')} {sig.symbol} "
            f"{'achat' if sig.direction == 1 else 'vente'}\nRaison : {reason}\n🆔 {sig.signal_id}")


def closed_message(symbol, technique, profit, r, reason, minutes, ticket) -> str:
    head = "✅ TRADE FERMÉ — GAIN" if profit >= 0 else "❌ TRADE FERMÉ — PERTE"
    hours = f"{int(minutes // 60)} h {int(minutes % 60):02d} min"
    return (f"{head}\n📊 {symbol} | {cfg.SHORT_TITLE.get(technique, technique)}\n"
            f"💵 {profit:+.2f} $  ({r:+.2f} R)\n🏁 Sortie : {reason} | durée {hours}\n🎫 ticket {ticket}")


def start_message(balance, currency, mode_execute: bool, symbols, notes=()) -> str:
    extra = "".join(f"\n• {n}" for n in notes)
    return (f"🤖 Bot SMC démarré — {'MODE EXÉCUTION' if mode_execute else 'mode alerte seule'}\n"
            f"💰 Balance : {balance} {currency}\n📈 {len(symbols)} indices surveillés{extra}")


class Notifier:
    def __init__(self, token=None, chat_id=None, dry=False, post=requests.post):
        self.token = token if token is not None else os.getenv("TELEGRAM_TOKEN")
        self.chat_id = chat_id if chat_id is not None else os.getenv("TELEGRAM_CHAT_ID")
        self.dry, self.post = dry, post
        self.sent = []                                   # kept in memory for tests and debugging

    def send(self, text: str) -> bool:
        self.sent.append(text)
        if self.dry or not self.token or not self.chat_id:
            print(f"[NOTIFY] {text.splitlines()[0]}")
            return False
        try:
            r = self.post(f"https://api.telegram.org/bot{self.token}/sendMessage",
                          data={"chat_id": self.chat_id, "text": text}, timeout=30)
            return getattr(r, "ok", True)
        except Exception as e:  # noqa: BLE001 - a Telegram problem must never stop trading logic
            print(f"[NOTIFY] Telegram error: {e}")
            return False

    def alert_once(self, state, key: str, text: str):
        """Send an alert only the first time a problem appears (until clear_alert is called)."""
        if not state.alert_sent(key):
            state.mark_alert(key)
            self.send(text)
