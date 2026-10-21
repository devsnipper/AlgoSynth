"""Telegram messages of the SMC system. Send only: it never polls getUpdates, so it cannot clash with any other bot
that uses the same token. The message builders are pure functions (easy to test); Notifier does the sending.
"""
import json
import os
import time
from datetime import datetime

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


PERMANENT_HTTP_ERRORS = (400, 401, 403, 404)      # retrying cannot fix these: bad token, bad chat id, blocked bot
MAX_QUEUE = 50
MAX_RETRY_AFTER = 10                              # seconds: longest pause we accept to honour a Telegram 429


class Notifier:
    """Sends Telegram messages. A failed send is retried; a message that still cannot be delivered (network down, Telegram
    overloaded) is kept in a queue (and on disk when queue_path is given) and sent again by flush(), marked as delayed."""

    def __init__(self, token=None, chat_id=None, dry=False, post=requests.post, sleep=time.sleep, retries=3, queue_path=None):
        self.token = token if token is not None else os.getenv("TELEGRAM_TOKEN")
        self.chat_id = chat_id if chat_id is not None else os.getenv("TELEGRAM_CHAT_ID")
        self.dry, self.post, self.sleep, self.retries, self.queue_path = dry, post, sleep, retries, queue_path
        self.sent = []                                   # kept in memory for tests and debugging
        self.pending = self._load_queue()

    # --- persistence of the queue
    def _load_queue(self) -> list:
        if not self.queue_path or not os.path.exists(self.queue_path):
            return []
        try:
            with open(self.queue_path, encoding="utf-8") as f:
                data = json.load(f)
            return [m for m in data if isinstance(m, dict) and "text" in m][-MAX_QUEUE:]
        except (OSError, ValueError):
            return []

    def _save_queue(self):
        if not self.queue_path:
            return
        try:
            tmp = self.queue_path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.pending, f, ensure_ascii=False)
            os.replace(tmp, self.queue_path)
        except OSError as e:
            print(f"[NOTIFY] cannot save the queue: {e}")

    # --- one delivery, with retries. Returns "ok", "retry_later" or "permanent"
    def _deliver(self, text: str, attempts: int) -> str:
        outcome = "retry_later"
        for i in range(attempts):
            pause = i + 1                                # 1 s, 2 s between attempts
            try:
                r = self.post(f"https://api.telegram.org/bot{self.token}/sendMessage",
                              data={"chat_id": self.chat_id, "text": text}, timeout=30)
                if getattr(r, "ok", True):
                    return "ok"
                code = getattr(r, "status_code", "?")
                print(f"[NOTIFY] Telegram refused the message: HTTP {code} {str(getattr(r, 'text', ''))[:200]}")
                if code in PERMANENT_HTTP_ERRORS:
                    return "permanent"
                if code == 429:
                    try:
                        pause = min(float(r.json()["parameters"]["retry_after"]), MAX_RETRY_AFTER)
                    except Exception:  # noqa: BLE001 - keep the default pause
                        pass
            except Exception as e:  # noqa: BLE001 - a Telegram problem must never stop trading logic
                print(f"[NOTIFY] Telegram error: {e}")
            if i < attempts - 1:
                self.sleep(pause)
        return outcome

    def flush(self):
        """Try to send the queued messages, oldest first, one attempt each; stop at the first failure."""
        if self.dry or not self.token or not self.chat_id:
            return
        while self.pending:
            m = self.pending[0]
            result = self._deliver(f"⏱️ (message retardé, prévu à {m.get('time', '?')})\n{m['text']}", 1)
            if result == "retry_later":
                break
            self.pending.pop(0)                          # sent, or permanently refused: either way do not keep it
            self._save_queue()
        self._save_queue()

    def send(self, text: str) -> bool:
        self.sent.append(text)
        if self.dry or not self.token or not self.chat_id:
            print(f"[NOTIFY] {text.splitlines()[0]}")
            return False
        if self.pending:
            self.flush()                                 # older messages go first
        if self.pending:                                 # still cannot reach Telegram: queue behind the others, no retries
            self._enqueue(text)
            return False
        result = self._deliver(text, self.retries)
        if result == "retry_later":
            self._enqueue(text)
        return result == "ok"

    def _enqueue(self, text: str):
        self.pending.append({"time": datetime.now().strftime("%d/%m %H:%M"), "text": text})
        del self.pending[:-MAX_QUEUE]
        self._save_queue()
        print(f"[NOTIFY] message kept for later ({len(self.pending)} waiting)")

    def alert_once(self, state, key: str, text: str):
        """Send an alert only the first time a problem appears (until clear_alert is called)."""
        if not state.alert_sent(key):
            state.mark_alert(key)
            self.send(text)
