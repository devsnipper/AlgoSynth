import MetaTrader5 as mt5
import csv
import os
import time
from datetime import datetime
from config import RISK_USD, TP_POINTS, SL_POINTS, MAGIC

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


def open_trade(symbol: str, direction: str, tp_points: int = None, sl_points: int = None) -> int | None:
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return None

    info = mt5.symbol_info(symbol)
    if info is None:
        return None

    if direction == "buy":
        order_type = mt5.ORDER_TYPE_BUY
        price = tick.ask
    else:
        order_type = mt5.ORDER_TYPE_SELL
        price = tick.bid

    # Lot dynamique : RISK_USD / (sl_pts * valeur_point)
    sl_pts_calc = sl_points if sl_points else SL_POINTS
    val_pt = info.trade_contract_size * info.point
    lot_raw = RISK_USD / (sl_pts_calc * val_pt) if val_pt > 0 else info.volume_min
    lot = max(info.volume_min, round(lot_raw / info.volume_step) * info.volume_step)

    request = {
        "action":       mt5.TRADE_ACTION_DEAL,
        "symbol":       symbol,
        "volume":       lot,
        "type":         order_type,
        "price":        price,
        "deviation":    50,
        "magic":        MAGIC,
        "comment":      "deriv-scalper",
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    pt = info.point
    if tp_points:
        if direction == "buy":
            request["tp"] = round(price + tp_points * pt, info.digits)
        else:
            request["tp"] = round(price - tp_points * pt, info.digits)

    if sl_points:
        if direction == "buy":
            request["sl"] = round(price - sl_points * pt, info.digits)
        else:
            request["sl"] = round(price + sl_points * pt, info.digits)

    result = mt5.order_send(request)
    if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
        code = result.retcode if result else "None"
        print(f"[TRADER] Ouverture refusee ({code}) sur {symbol}")
        _log_order("OPEN", symbol, direction, price, code, "REFUSE")
        return None

    tp_info = f" | TP serveur={request.get('tp', 'none')}" if tp_points else ""
    print(f"[TRADER] Trade ouvert  | {direction.upper()} {symbol} @ {price} | ticket={result.order}{tp_info}")
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
            "volume":       pos.volume,
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
            time.sleep(0.5)
            deals     = mt5.history_deals_get(position=ticket)
            out_deals = [d for d in deals if d.entry == mt5.DEAL_ENTRY_OUT] if deals else []
            profit    = sum(d.profit for d in out_deals) if out_deals else pos.profit
            exit_p    = out_deals[-1].price if out_deals else close_price
            print(f"[TRADER] Trade ferme   | {symbol} | profit={profit:.2f}")
            _log_order("CLOSE", symbol, direction, exit_p, result.retcode, "OK")
            _init_log()
            with open(LOG_FILE, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%H:%M:%S"),
                    symbol, direction, pos.volume, entry_price, exit_p, profit
                ])
            return profit

        code = result.retcode if result else "None"

        # 10029 = position deja fermee par le serveur (TP serveur atteint)
        # On laisse monitor_trade detecter la position disparue et lire l'historique
        if result is not None and result.retcode == 10029:
            return None

        print(f"[TRADER] Fermeture refusee ({code}) sur {symbol} — tentative {attempt + 1}/10")
        _log_order("CLOSE", symbol, direction, close_price, code, f"REFUSE_{attempt+1}")
        time.sleep(0.5)

    print(f"[TRADER] Fermeture impossible apres 10 tentatives sur {symbol}")
    return None


def monitor_trade(symbol: str, ticket: int, entry_price: float, direction: str,
                  tp_points: int = None, sl_points: int = None) -> float | None:
    info = mt5.symbol_info(symbol)
    if info is None:
        return None
    point = info.point

    tp_pts = tp_points if tp_points else TP_POINTS
    sl_pts = sl_points if sl_points else SL_POINTS

    tp_level = entry_price + tp_pts * point if direction == "buy" else entry_price - tp_pts * point
    sl_level = entry_price - sl_pts * point if direction == "buy" else entry_price + sl_pts * point

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
                        symbol, direction, deals[-1].volume, entry_price, exit_price, profit
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
            result = close_trade(symbol, ticket, entry_price, direction)
            if result is not None:
                return result
            time.sleep(2)  # attendre que MT5 retire la position de sa liste

        if hit_sl:
            print(f"[TRADER] SL atteint @ {price:.3f}")
            result = close_trade(symbol, ticket, entry_price, direction)
            if result is not None:
                return result
            time.sleep(2)
