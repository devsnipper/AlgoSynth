import MetaTrader5 as mt5
import time
import os
from datetime import datetime, date
import calendar
from dotenv import load_dotenv

from config   import SYMBOLS, MAX_TRADES
from strategy import check_trend_m15, check_signal_m1, is_spike
from trader   import has_open_position, open_trade, monitor_trade
from notifier import (
    notify_start, notify_trade_open, notify_trade_close,
    notify_spike, notify_max_trades, notify_stop, notify_heartbeat, notify_report
)
from reporter import (
    daily_report, weekly_report, monthly_report, load_today_trade_count
)

HEARTBEAT_SEC = 30 * 60  # 30 minutes

load_dotenv()


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

    info           = mt5.account_info()
    daily_pnl      = 0.0
    last_heartbeat = time.time()

    # Reprendre le compteur du jour si le bot redémarre
    trade_count  = load_today_trade_count()
    current_date = date.today()

    if trade_count > 0:
        print(f"[MAIN] Reprise session — {trade_count} trades deja effectues aujourd'hui")

    notify_start(info.balance, info.currency)
    print(f"[MAIN] Connecte | Balance={info.balance} {info.currency}")

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

            # Limite journaliere atteinte
            if trade_count >= MAX_TRADES:
                time.sleep(60)
                continue

            for key, symbol in SYMBOLS.items():
                direction_map = {"crash": "buy", "boom": "sell"}
                expected_dir  = direction_map[key]

                # 1. Pas de trade actif sur ce symbole
                if has_open_position(symbol):
                    continue

                # 2. Tendance M15
                trend = check_trend_m15(symbol)
                if trend != expected_dir:
                    continue

                # 3. Signal M1
                if not check_signal_m1(symbol, expected_dir):
                    continue

                # 4. Spike filter
                if is_spike(symbol):
                    print(f"[MAIN] Spike detecte sur {symbol}")
                    notify_spike(symbol)
                    continue

                # 5. Ouvrir le trade
                tick        = mt5.symbol_info_tick(symbol)
                entry_price = tick.ask if expected_dir == "buy" else tick.bid
                ticket      = open_trade(symbol, expected_dir)

                if ticket is None:
                    continue

                trade_count += 1
                notify_trade_open(symbol, expected_dir, entry_price)

                # 6. Surveiller jusqu'a TP ou SL
                profit = monitor_trade(symbol, ticket, entry_price, expected_dir)

                if profit is not None:
                    daily_pnl += profit
                    notify_trade_close(symbol, profit, daily_pnl)

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
