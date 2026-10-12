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


def symbols() -> list:
    return list(symbol_info())
