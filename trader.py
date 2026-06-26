import MetaTrader5 as mt5
import csv
import os
import time
from datetime import datetime
from config import LOT, TP_POINTS, SL_POINTS, MAGIC

LOG_FILE    = os.path.join(os.path.dirname(__file__), "logs", "trades.csv")
ORDER_LOG   = os.path.join(os.path.dirname(__file__), "logs", "orders.csv")


def _init_log():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "heure", "symbol", "direction", "lot", "entry", "exit", "profit"])


def _init_order_log():
    if not os.path.exists(ORDER_LOG):
        with open(ORDER_LOG, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "heure", "type", "symbol", "direction", "prix", "retcode", "statut"])


def _log_order(order_type: str, symbol: str, direction: str, prix: float, retcode, statut: str):
    _init_order_log()
    with open(ORDER_LOG, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d"),
            datetime.now().strftime("%H:%M:%S"),
            order_type, symbol, direction, prix, retcode, statut
        ])


def has_open_position(symbol: str) -> bool:
    positions = mt5.positions_get(symbol=symbol)
    return positions is not None and len(positions) > 0


def open_trade(symbol: str, direction: str) -> int | None:
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return None

    if direction == "buy":
        order_type = mt5.ORDER_TYPE_BUY
        price = tick.ask
    else:
        order_type = mt5.ORDER_TYPE_SELL
        price = tick.bid

    request = {
        "action":       mt5.TRADE_ACTION_DEAL,
        "symbol":       symbol,
        "volume":       LOT,
        "type":         order_type,
        "price":        price,
        "deviation":    50,
        "magic":        MAGIC,
        "comment":      "deriv-scalper",
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    result = mt5.order_send(request)
    if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
        code = result.retcode if result else "None"
        print(f"[TRADER] Ouverture refusee ({code}) sur {symbol}")
        _log_order("OPEN", symbol, direction, price, code, "REFUSE")
        return None

    print(f"[TRADER] Trade ouvert  | {direction.upper()} {symbol} @ {price} | ticket={result.order}")
    _log_order("OPEN", symbol, direction, price, result.retcode, "OK")
    return result.order


def close_trade(symbol: str, ticket: int, entry_price: float, direction: str) -> float | None:
    positions = mt5.positions_get(symbol=symbol)
    if not positions:
        return None

    pos = next((p for p in positions if p.ticket == ticket), None)
    if pos is None:
        return None

    if direction == "buy":
        close_type = mt5.ORDER_TYPE_SELL
    else:
        close_type = mt5.ORDER_TYPE_BUY

    for attempt in range(10):
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            time.sleep(0.5)
            continue

        close_price = tick.bid if direction == "buy" else tick.ask

        request = {
            "action":       mt5.TRADE_ACTION_DEAL,
            "symbol":       symbol,
            "volume":       LOT,
            "type":         close_type,
            "position":     ticket,
            "price":        close_price,
            "deviation":    50,
            "magic":        MAGIC,
            "comment":      "deriv-scalper-close",
            "type_filling": mt5.ORDER_FILLING_FOK,
        }

        result = mt5.order_send(request)
        if result is not None and result.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"[TRADER] Trade ferme   | {symbol} | profit={pos.profit:.2f}")
            _log_order("CLOSE", symbol, direction, close_price, result.retcode, "OK")
            _init_log()
            with open(LOG_FILE, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%H:%M:%S"),
                    symbol, direction, LOT, entry_price, close_price, pos.profit
                ])
            return pos.profit

        code = result.retcode if result else "None"
        print(f"[TRADER] Fermeture refusee ({code}) sur {symbol} — tentative {attempt + 1}/10")
        _log_order("CLOSE", symbol, direction, close_price, code, f"REFUSE_{attempt+1}")
        time.sleep(0.5)

    print(f"[TRADER] Fermeture impossible apres 10 tentatives sur {symbol}")
    return None


def monitor_trade(symbol: str, ticket: int, entry_price: float, direction: str) -> float | None:
    info = mt5.symbol_info(symbol)
    if info is None:
        return None
    point = info.point

    tp_level = entry_price + TP_POINTS * point if direction == "buy" else entry_price - TP_POINTS * point
    sl_level = entry_price - SL_POINTS * point if direction == "buy" else entry_price + SL_POINTS * point

    while True:
        positions = mt5.positions_get(symbol=symbol)
        if not positions or not any(p.ticket == ticket for p in positions):
            deals = mt5.history_deals_get(position=ticket)
            if deals:
                profit = sum(d.profit for d in deals)
                exit_price = deals[-1].price
                print(f"[TRADER] Position {ticket} fermee par MT5 | profit={profit:.2f}")
                _init_log()
                with open(LOG_FILE, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%H:%M:%S"),
                        symbol, direction, LOT, entry_price, exit_price, profit
                    ])
                return profit
            print(f"[TRADER] Position {ticket} introuvable, aucun deal trouve")
            return None

        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            continue

        price = tick.bid if direction == "buy" else tick.ask

        if direction == "buy":
            hit_tp = price >= tp_level
            hit_sl = price <= sl_level
        else:
            hit_tp = price <= tp_level
            hit_sl = price >= sl_level

        if hit_tp:
            print(f"[TRADER] TP atteint @ {price:.3f}")
            return close_trade(symbol, ticket, entry_price, direction)

        if hit_sl:
            print(f"[TRADER] SL atteint @ {price:.3f}")
            return close_trade(symbol, ticket, entry_price, direction)
