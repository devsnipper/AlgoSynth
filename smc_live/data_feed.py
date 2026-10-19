"""Candles from MT5 as a techniques.Snapshot. Only CLOSED candles: the request starts at position 1, so the candle that
is still forming is never included. `mt5` is passed in, so tests can use a fake terminal."""
from datetime import datetime, timezone

import pandas as pd

from smc_live import config_smc as cfg
from techniques.base import Snapshot

TF_ATTR = {"M15": "TIMEFRAME_M15", "H1": "TIMEFRAME_H1", "H4": "TIMEFRAME_H4"}


def to_frame(rates) -> pd.DataFrame:
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")          # MT5 server time, naive (same as the downloaded history)
    return df[["time", "open", "high", "low", "close", "spread"]].reset_index(drop=True)


def broker_info(mt5, symbol: str) -> dict:
    i = mt5.symbol_info(symbol)
    if i is None:
        raise RuntimeError(f"{symbol}: symbol not available")
    return {"point": i.point, "digits": i.digits, "contract_size": i.trade_contract_size, "volume_min": i.volume_min,
            "volume_max": i.volume_max, "volume_step": i.volume_step, "stops_level": i.trade_stops_level}


def last_closed_m15(mt5, symbol: str):
    rates = mt5.copy_rates_from_pos(symbol, getattr(mt5, TF_ATTR["M15"]), 1, 1)
    if rates is None or len(rates) == 0:
        return None
    return pd.Timestamp(int(rates[0]["time"]), unit="s")


def fetch_snapshot(mt5, symbol: str):
    """Returns a Snapshot, or None when the terminal has no data yet."""
    info = broker_info(mt5, symbol)
    frames = {}
    for name, count in cfg.CANDLES.items():
        rates = mt5.copy_rates_from_pos(symbol, getattr(mt5, TF_ATTR[name]), 1, count)
        if rates is None or len(rates) < count // 2:
            return None
        frames[name] = to_frame(rates)
    return Snapshot(symbol, info["point"], info["stops_level"], frames["M15"], frames["H1"], frames["H4"])


def server_now(mt5, symbol: str):
    """Current MT5 server time (naive), from the last tick: avoids any confusion with the PC's time zone."""
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return None
    return datetime.fromtimestamp(tick.time, tz=timezone.utc).replace(tzinfo=None)
