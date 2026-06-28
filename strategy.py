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


def check_trend_m15(symbol: str) -> str | None:
    """Retourne 'buy', 'sell' ou None selon la tendance M15."""
    df = get_candles(symbol, TF_TREND)
    if df.empty:
        return None
    df = add_emas(df)
    last = df.iloc[-1]

    if last["ema_fast"] > last["ema_mid"] > last["ema_slow"]:
        return "buy"
    if last["ema_fast"] < last["ema_mid"] < last["ema_slow"]:
        return "sell"
    return None


def is_atr_calm(symbol: str) -> bool:
    """Retourne True si la volatilite actuelle est sous le 80e percentile recent (auto-calibre par indice)."""
    rates = mt5.copy_rates_from_pos(symbol, TF_SIGNAL, 1, 50)
    if rates is None or len(rates) < 10:
        return True
    tr_values = sorted([r["high"] - r["low"] for r in rates])
    current_tr   = tr_values[-1]
    threshold_80 = tr_values[int(len(tr_values) * 0.80)]
    return current_tr < threshold_80


def check_signal_m1(symbol: str, direction: str) -> bool:
    """Croisement EMA5/13 au-dessus/dessous EMA50 en M1 + filtre ATR percentile."""
    df = get_candles(symbol, TF_SIGNAL)
    if len(df) < 2:
        return False
    df = add_emas(df)

    prev = df.iloc[-2]
    last = df.iloc[-1]

    if direction == "buy":
        crossed_up  = prev["ema_fast"] <= prev["ema_mid"] and last["ema_fast"] > last["ema_mid"]
        above_slow  = last["ema_fast"] > last["ema_slow"] and last["ema_mid"] > last["ema_slow"]
        calm        = is_atr_calm(symbol)
        return crossed_up and above_slow and calm

    if direction == "sell":
        crossed_down = prev["ema_fast"] >= prev["ema_mid"] and last["ema_fast"] < last["ema_mid"]
        below_slow   = last["ema_fast"] < last["ema_slow"] and last["ema_mid"] < last["ema_slow"]
        calm         = is_atr_calm(symbol)
        return crossed_down and below_slow and calm

    return False


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
