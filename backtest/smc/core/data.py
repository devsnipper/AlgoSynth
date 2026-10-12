"""Loading of candle files and symbol settings (written by tools/download_history.py)."""
import json
import os

import pandas as pd

from core.constants import DATA_DIR


def load(symbol: str, tf: str) -> pd.DataFrame:
    """Candles for one symbol. tf is one of M5, M15, H1, H4. The `time` column is the candle OPEN time."""
    path = os.path.join(DATA_DIR, f"{symbol.replace(' ', '_')}_{tf}.csv")
    return pd.read_csv(path, parse_dates=["time"])


def symbol_info() -> dict:
    """{symbol: {point, digits, contract_size, volume_min, volume_step, stops_level}}"""
    with open(os.path.join(DATA_DIR, "symbol_info.json")) as f:
        return json.load(f)


def group_of(symbol: str, info: dict) -> str:
    """'boomcrash' or 'spikefree'. Older entries have no group tag, so they are inferred from the name."""
    return info.get("group") or ("boomcrash" if symbol.startswith(("Boom", "Crash")) else "spikefree")


def symbols(group: str = "boomcrash") -> list:
    """Symbols of one universe. The default keeps every earlier result reproducible. Use group='all' for everything."""
    info = symbol_info()
    return [s for s, v in info.items() if group == "all" or group_of(s, v) == group]
