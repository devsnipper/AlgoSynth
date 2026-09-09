import MetaTrader5 as mt5
import time
import os
import threading
import requests
from datetime import datetime, date
import calendar
from dotenv import load_dotenv

from config   import SYMBOLS, MAX_TRADES, TP_CONFIG
from strategy import check_trend_m15, check_signal_m1, is_spike, get_trend_report
from trader   import has_open_position, open_trade, monitor_trade
from notifier import (
    notify_start, notify_trade_open, notify_trade_close,
    notify_spike, notify_max_trades, notify_stop, notify_heartbeat, notify_report, send
)
from reporter import (
    daily_report, weekly_report, monthly_report, load_today_trade_count, load_today_pnl
)

HEARTBEAT_SEC = 30 * 60  # 30 minutes

load_dotenv()

DIRECTION_MAP = {
    "boom150":   "sell",
    "crash150":  "buy",
    "crash500":  "buy",
    "boom600":   "sell",
    "boom500":   "sell",
    "boom900":   "sell",
}


def telegram_listener():
    """Thread qui ecoute les messages Telegram et repond aux commandes."""
    token   = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return

    base    = f"https://api.telegram.org/bot{token}"
    offset  = 0

    while True:
        try:
            r = requests.get(f"{base}/getUpdates", params={"offset": offset, "timeout": 30}, timeout=35)
            updates = r.json().get("result", [])
            for upd in updates:
                offset = upd["update_id"] + 1
                msg    = upd.get("message", {})
                text   = msg.get("text", "").strip().lower()
                if text == "trend":
                    report = get_trend_report(SYMBOLS, DIRECTION_MAP)
                    requests.post(f"{base}/sendMessage",
                                  data={"chat_id": chat_id, "text": report}, timeout=10)
        except Exception:
            time.sleep(5)


def connect_mt5() -> bool:
    if not mt5.initialize():
        print(f"[MAIN] initialize() echoue : {mt5.last_error()}")
        return False

    login    = int(os.getenv("MT5_LOGIN"))
    password = os.getenv("MT5_PASSWORD")
    server   = os.getenv("MT5_SERVER")

    if not mt5.login(login, password=password, server=server):
        print(f"[MAIN] login() echoue : {mt5.last_error()}")
        mt5.shutdown()
        return False

    return True


def run():
    if not connect_mt5():
        return

    threading.Thread(target=telegram_listener, daemon=True).start()
    print("[MAIN] Listener Telegram demarre — commande disponible : trend")

    info           = mt5.account_info()
    last_heartbeat = time.time()

    # Reprendre le compteur et le PnL du jour si le bot redémarre
    trade_count  = load_today_trade_count()
    daily_pnl    = load_today_pnl()
    current_date = date.today()

    if trade_count > 0:
        print(f"[MAIN] Reprise session — {trade_count} trades deja effectues aujourd'hui")

    notify_start(info.balance, info.currency)
    print(f"[MAIN] Connecte | Balance={info.balance} {info.currency}")

    active_symbols  = set()  # symboles dont monitor_trade est en cours
    loss_cooldown   = {}     # symbole -> timestamp fin cooldown apres perte
    pending_signal  = {}     # symbole -> timestamp bougie M5 qui a genere le signal

    LOSS_COOLDOWN_SEC = 120  # 2 min de pause apres un SL
    spike_cooldown = {}      # symbole -> timestamp fin cooldown apres spike detecte

    try:
        while True:
            now  = datetime.now()
            today = date.today()

            # Minuit — nouveau jour
            if today != current_date:
                trade_count  = 0
                daily_pnl    = 0.0
                current_date = today
                print(f"[MAIN] Nouveau jour : {today}")

            # Objectif journalier atteint
            if daily_pnl >= 3.0:
                send(f"🎯 Objectif journalier atteint — PnL : +{daily_pnl:.2f} $\n🛑 Bot en pause jusqu'à minuit")
                print(f"[MAIN] Objectif +3 USD atteint — arret des trades")
                while date.today() == current_date:
                    time.sleep(60)
                continue

            # Limite journaliere atteinte
            if trade_count >= MAX_TRADES:
                time.sleep(60)
                continue

            for key, symbol in SYMBOLS.items():
                expected_dir = DIRECTION_MAP[key]

                # 1. Symbole deja surveille par monitor_trade
                if symbol in active_symbols:
                    continue

                # 2. Cooldown apres une perte
                if time.time() < loss_cooldown.get(symbol, 0):
                    continue

                # 3. Pas de trade actif sur ce symbole
                if has_open_position(symbol):
                    continue

                # 4. Tendance M15
                trend = check_trend_m15(symbol)
                if trend != expected_dir:
                    continue

                # 5. Signal M5 sur bougie fermee
                if not check_signal_m1(symbol, expected_dir):
                    pending_signal.pop(symbol, None)
                    continue

                # 6. Guardrail : entrer uniquement sur la bougie SUIVANT le signal
                last_closed = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 1, 1)
                current     = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 1)
                if last_closed is None or current is None:
                    continue
                signal_candle_time  = int(last_closed[0]["time"])
                current_candle_time = int(current[0]["time"])

                if symbol not in pending_signal:
                    # Signal detecte — on enregistre et on attend la prochaine bougie
                    pending_signal[symbol] = signal_candle_time
                    print(f"[MAIN] Signal en attente sur {symbol} — prochaine bougie M5")
                    continue

                if current_candle_time <= pending_signal[symbol]:
                    # Nouvelle bougie pas encore ouverte
                    continue

                # Nouvelle bougie ouverte — signal confirme, on peut entrer
                pending_signal.pop(symbol, None)

                # 7. Spike filter
                if is_spike(symbol):
                    print(f"[MAIN] Spike detecte sur {symbol}")
                    continue

                # 8. Ouvrir le trade — SL serveur strict, TP bot-side uniquement
                tick        = mt5.symbol_info_tick(symbol)
                entry_price = tick.ask if expected_dir == "buy" else tick.bid
                cfg         = TP_CONFIG.get(symbol, {})
                ticket      = open_trade(symbol, expected_dir, sl_points=cfg.get("sl"))

                if ticket is None:
                    continue

                trade_count += 1
                notify_trade_open(symbol, expected_dir, entry_price)

                # 8. Surveiller jusqu'a TP ou SL
                active_symbols.add(symbol)
                cfg    = TP_CONFIG.get(symbol, {})
                profit = monitor_trade(symbol, ticket, entry_price, expected_dir,
                                       tp_points=cfg.get("tp"), sl_points=cfg.get("sl"))
                active_symbols.discard(symbol)

                if profit is not None:
                    daily_pnl += profit
                    notify_trade_close(symbol, profit, daily_pnl)
                    if profit < 0:
                        loss_cooldown[symbol] = time.time() + LOSS_COOLDOWN_SEC
                        print(f"[MAIN] Pause 120s sur {symbol} apres perte")

            # Heartbeat toutes les 30 minutes
            if time.time() - last_heartbeat >= HEARTBEAT_SEC:
                notify_heartbeat()
                last_heartbeat = time.time()

            # Rapport 23h59 — journalier + hebdo (dimanche) + mensuel (dernier jour du mois)
            if now.hour == 23 and now.minute == 59 and now.second < 10:
                notify_report(daily_report(today))

                if today.weekday() == 6:  # dimanche
                    notify_report(weekly_report(today))

                last_day = calendar.monthrange(today.year, today.month)[1]
                if today.day == last_day:
                    notify_report(monthly_report(today))

                time.sleep(55)  # eviter d'envoyer plusieurs fois dans la meme minute

            time.sleep(1)

    except KeyboardInterrupt:
        print("[MAIN] Arret manuel")

    finally:
        notify_stop(daily_pnl)
        mt5.shutdown()
        print(f"[MAIN] Bot arrete | PnL jour = {daily_pnl:.2f}")


if __name__ == "__main__":
    run()
