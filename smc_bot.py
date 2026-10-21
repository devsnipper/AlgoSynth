"""SMC bot: three order-block techniques, signals on Telegram, market orders (execute mode).

    python smc_bot.py                 alert-only: Telegram + signals.csv, NO order is ever sent
    python smc_bot.py --execute       also opens the positions (needs MT5 "Algo Trading" switched on)
    python smc_bot.py --once          one scan of every symbol, then exit (to test the connection and the data)

It is a separate process from main.py and is designed to run INSTEAD of it (the EMA bot is stopped). It does not import
main.py, config.py, strategy.py, trader.py, notifier.py or reporter.py.
"""
import argparse
import os
import sys
import time
from datetime import date, datetime

import MetaTrader5 as mt5
from dotenv import load_dotenv

from smc_live import config_smc as cfg
from smc_live import data_feed, notify, smc_report
from smc_live.executor import Executor
from smc_live.pipeline import Pipeline
from smc_live.position_monitor import Monitor
from smc_live.state import State
from smc_live.tradelog import TradeLog

load_dotenv(os.path.join(cfg.ROOT, ".env"))                 # credentials, read only


def connect() -> bool:
    ok = mt5.initialize(login=int(os.getenv("MT5_LOGIN")), password=os.getenv("MT5_PASSWORD"), server=os.getenv("MT5_SERVER"))
    if not ok:
        print(f"[SMC] initialize() failed: {mt5.last_error()}")
    return ok


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true", help="send real orders (default: alert-only)")
    ap.add_argument("--once", action="store_true", help="scan every symbol once and exit")
    ap.add_argument("--dry-notify", action="store_true", help="print messages instead of sending them to Telegram")
    ap.add_argument("--symbols", nargs="*", default=None)
    args = ap.parse_args(argv)
    execute = args.execute or cfg.EXECUTE
    symbols = args.symbols or cfg.SYMBOLS

    if not connect():
        return 1
    notifier = notify.Notifier(dry=args.dry_notify,
                               queue_path=os.path.join(os.path.dirname(cfg.STATE_PATH), "telegram_pending.json"))
    log = TradeLog(cfg.LOG_DIR)
    notes = log.ensure_headers()
    state = State(cfg.STATE_PATH)
    executor = Executor(mt5, execute)
    monitor = Monitor(mt5, state, log, notifier, executor)
    pipeline = Pipeline(mt5, state, log, notifier, executor, monitor, execute)

    algo_on = bool(mt5.terminal_info().trade_allowed)
    if execute and not algo_on:
        notes.append("⚠️ Algo Trading est DÉSACTIVÉ dans MT5 : aucun ordre ne passera tant qu'il l'est")
    acc = mt5.account_info()
    notifier.send(notify.start_message(acc.balance, acc.currency, execute, symbols, notes))
    print(f"[SMC] started | execute={execute} | algo trading in MT5: {algo_on} | symbols: {len(symbols)}")

    last_heartbeat, last_report_day = time.time(), None
    try:
        while True:
            now_server = data_feed.server_now(mt5, symbols[0])
            if now_server is not None:
                monitor.sync(now_server)
            for sym in symbols:
                closed = data_feed.last_closed_m15(mt5, sym)
                if closed is None or state.last_scan(sym) == closed.isoformat():
                    continue
                snap = data_feed.fetch_snapshot(mt5, sym)
                now = data_feed.server_now(mt5, sym)
                if snap is None or now is None:
                    continue
                state.set_last_scan(sym, closed.isoformat())
                outcomes = pipeline.scan(snap, now)
                for o in outcomes:
                    print(f"[SMC] {sym}: {o.get('status')} {o.get('reason', '')} {o['signal_id']}")
                state.save()
            notifier.flush()                                             # resend messages Telegram refused earlier
            if args.once:
                break

            if time.time() - last_heartbeat >= cfg.HEARTBEAT_MIN * 60:
                notifier.send("💓 Bot SMC actif")
                last_heartbeat = time.time()
            local = datetime.now()
            if local.hour == cfg.DAILY_REPORT_HOUR and last_report_day != local.date():
                notifier.send(smc_report.daily_text(cfg.LOG_DIR, local.date()))
                if local.weekday() == 6:
                    notifier.send(smc_report.weekly_text(cfg.LOG_DIR, local.date()))
                last_report_day = local.date()
            time.sleep(cfg.LOOP_SECONDS)
    except KeyboardInterrupt:
        print("[SMC] manual stop")
    finally:
        state.save()
        notifier.send("🛑 Bot SMC arrêté")
        mt5.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
