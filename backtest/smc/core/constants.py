"""Constants fixed before any result (see docs/SETUP_LIST.md > Data blocks).

Named `constants` on purpose: the live bot has its own top-level module with a different name,
and nothing in backtest/ may share a module name with the live code.
"""
import os

import pandas as pd

SMC_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(SMC_DIR, "data")

M5_TD = pd.Timedelta(minutes=5)
M15_TD = pd.Timedelta(minutes=15)
HTF_MINUTES = {"H4": 240, "H1": 60}

# Data blocks. A: tuning. B: final verdict, looked at once. C: older months, M15 candles only.
WINDOW_START = pd.Timestamp("2025-10-30")     # first M5 candle = start of the main window
SPLIT = pd.Timestamp("2026-05-26")            # A = before, B = from this date on
C_START = pd.Timestamp("2023-12-05")          # first M15 candle (some symbols start 2024-08-30)
