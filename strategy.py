import MetaTrader5 as mt5
import pandas as pd
from config import (
    TF_TREND, TF_SIGNAL, EMA_FAST, EMA_MID, EMA_SLOW,
    CANDLES_NB, SPIKE_THRESHOLD
)


def get_candles(symbol: str, timeframe: int) -> pd.DataFrame:
    """Recupere les candles fermees (index 1+) pour eviter les faux signaux."""
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 1, CANDLES_NB)
    if rates is None or len(rates) == 0:
        return pd.DataFrame()
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    return df


def add_emas(df: pd.DataFrame) -> pd.DataFrame:
    df["ema_fast"] = df["close"].ewm(span=EMA_FAST, adjust=False).mean()
    df["ema_mid"]  = df["close"].ewm(span=EMA_MID,  adjust=False).mean()
    df["ema_slow"] = df["close"].ewm(span=EMA_SLOW,  adjust=False).mean()
    return df


def get_trend_report(symbols: dict, direction_map: dict) -> str:
    """Retourne un rapport Telegram sur la tendance M15 EMA50 de chaque indice."""
    lines = ["📊 Tendance M15 EMA50\n"]
    for key, symbol in symbols.items():
        df = get_candles(symbol, TF_TREND)
        if df.empty:
            lines.append(f"❓ {symbol} — indisponible")
            continue
        df    = add_emas(df)
        last  = df.iloc[-1]
        price = last["close"]
        ema50 = last["ema_slow"]
        expected = direction_map.get(key)

        if price > ema50:
            trend_label = "UP TREND"
            emoji = "📈"
        else:
            trend_label = "DOWN TREND"
            emoji = "📉"

        # Pour Crash (buy) : up trend = favorable. Pour Boom (sell) : down trend = favorable
        if expected == "buy":
            favorable = price > ema50
        else:
            favorable = price < ema50

        status = "trades proches ✅" if favorable else "trades loin ⏳"
        name   = symbol.replace(" Index", "")
        lines.append(f"{emoji} {name} — {trend_label} ({status})")

    return "\n".join(lines)


def trend_from_row(last) -> str | None:
    """Tendance a partir d'une ligne de candle avec EMAs deja calculees."""
    if last["ema_fast"] > last["ema_mid"] > last["ema_slow"]:
        return "buy"
    if last["ema_fast"] < last["ema_mid"] < last["ema_slow"]:
        return "sell"
    return None


def signal_from_rows(prev, last, direction: str) -> bool:
    """Croisement EMA5/13 au-dessus/dessous EMA50 entre deux candles consecutives."""
    if direction == "buy":
        crossed_up = prev["ema_fast"] <= prev["ema_mid"] and last["ema_fast"] > last["ema_mid"]
        above_slow = last["ema_fast"] > last["ema_slow"] and last["ema_mid"] > last["ema_slow"]
        return crossed_up and above_slow

    if direction == "sell":
        crossed_down = prev["ema_fast"] >= prev["ema_mid"] and last["ema_fast"] < last["ema_mid"]
        below_slow   = last["ema_fast"] < last["ema_slow"] and last["ema_mid"] < last["ema_slow"]
        return crossed_down and below_slow

    return False


def check_trend_m15(symbol: str) -> str | None:
    """Retourne 'buy', 'sell' ou None selon la tendance M15."""
    df = get_candles(symbol, TF_TREND)
    if df.empty:
        return None
    df = add_emas(df)
    return trend_from_row(df.iloc[-1])


def check_signal_m1(symbol: str, direction: str) -> bool:
    """Croisement EMA5/13 au-dessus/dessous EMA50 sur le timeframe signal (M5)."""
    df = get_candles(symbol, TF_SIGNAL)
    if len(df) < 2:
        return False
    df = add_emas(df)
    return signal_from_rows(df.iloc[-2], df.iloc[-1], direction)


def is_spike(symbol: str) -> bool:
    """Retourne True si le dernier tick est un spike (variation > 0.5%)."""
    from datetime import datetime, timezone, timedelta
    now   = datetime.now(timezone.utc)
    start = now - timedelta(seconds=10)
    ticks = mt5.copy_ticks_range(symbol, start, now, mt5.COPY_TICKS_ALL)

    if ticks is None or len(ticks) < 2:
        tick  = mt5.symbol_info_tick(symbol)
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 1, 2)
        if tick is None or rates is None or len(rates) < 1:
            return False
        p1 = rates[-1]["close"]
        p2 = tick.ask
    else:
        p1 = ticks[-2]["ask"]
        p2 = ticks[-1]["ask"]

    if p1 == 0:
        return False
    return abs(p2 - p1) / p1 > SPIKE_THRESHOLD
