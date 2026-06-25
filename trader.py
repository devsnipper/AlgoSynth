import MetaTrader5 as mt5
import csv
import os
import time
from datetime import datetime
from config import LOT, TP_POINTS, SL_POINTS, MAGIC

LOG_FILE = os.path.join(os.path.dirname(__file__), "logs", "trades.csv")


def _init_log():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "heure", "symbol", "direction", "lot", "entry", "exit", "profit"])


def has_open_position(symbol: str) -> bool:
    positions = mt5.positions_get(symbol=symbol)
    return positions is not None and len(positions) > 0


def open_trade(symbol: str, direction: str) -> int | None:
    """Ouvre un trade sans SL/TP (gere par Python). Retourne le ticket ou None."""
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
        "action":      mt5.TRADE_ACTION_DEAL,
        "symbol":      symbol,
        "volume":      LOT,
        "type":        order_type,
        "price":       price,
        "deviation":   10,
        "magic":       MAGIC,
        "comment":     "deriv-scalper",
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    result = mt5.order_send(request)
    if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
        code = result.retcode if result else "None"
        print(f"[TRADER] Ordre refuse ({code}) sur {symbol}")
        return None

    print(f"[TRADER] Trade ouvert  | {direction.upper()} {symbol} @ {price} | ticket={result.order}")
    return result.order


def close_trade(symbol: str, ticket: int, entry_price: float, direction: str) -> float | None:
    """Ferme la position et log le trade. Retourne le profit ou None."""
    positions = mt5.positions_get(symbol=symbol)
    if not positions:
        return None

    pos = next((p for p in positions if p.ticket == ticket), None)
    if pos is None:
        return None

    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return None

    if direction == "buy":
        close_type  = mt5.ORDER_TYPE_SELL
        close_price = tick.bid
    else:
        close_type  = mt5.ORDER_TYPE_BUY
        close_price = tick.ask

    request = {
        "action":      mt5.TRADE_ACTION_DEAL,
        "symbol":      symbol,
        "volume":      LOT,
        "type":        close_type,
        "position":    ticket,
        "price":       close_price,
        "deviation":   10,
        "magic":       MAGIC,
        "comment":     "deriv-scalper-close",
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    for attempt in range(3):
        result = mt5.order_send(request)
        if result is not None and result.retcode == mt5.TRADE_RETCODE_DONE:
            break
        code = result.retcode if result else "None"
        print(f"[TRADER] Fermeture refusee ({code}) sur {symbol} — tentative {attempt + 1}/3")
        time.sleep(1)
    else:
        print(f"[TRADER] Fermeture impossible apres 3 tentatives sur {symbol}")
        return None

    profit = pos.profit
    print(f"[TRADER] Trade ferme   | {symbol} | profit={profit:.2f}")
    _init_log()
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%H:%M:%S"),
            symbol, direction, LOT, entry_price, close_price, profit
        ])
    return profit


def monitor_trade(symbol: str, ticket: int, entry_price: float, direction: str) -> float | None:
    """
    Surveille le prix tick par tick.
    Ferme quand TP ou SL est atteint. Retourne le profit ou None si position deja fermee.
    """
    info = mt5.symbol_info(symbol)
    if info is None:
        return None
    point = info.point

    tp_level = entry_price + TP_POINTS * point if direction == "buy" else entry_price - TP_POINTS * point
    sl_level = entry_price - SL_POINTS * point if direction == "buy" else entry_price + SL_POINTS * point

    while True:
        positions = mt5.positions_get(symbol=symbol)
        if not positions or not any(p.ticket == ticket for p in positions):
            # Position fermée par MT5 (spike, déconnexion...) — récupérer le profit réel
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
