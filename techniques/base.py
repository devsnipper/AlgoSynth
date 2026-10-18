"""The two objects every technique works with.

Snapshot  what a technique may look at: closed candles of one symbol on M15, H1 and H4 (never the forming candle).
Signal    what a technique returns: where to trade, in which direction, with which SL and TP, and why.

A technique never touches MT5, files or the network. The live code builds the Snapshot and executes the Signals.
"""
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

M15_MIN = 15
COLUMNS = ["time", "open", "high", "low", "close", "spread"]


@dataclass
class Snapshot:
    symbol: str
    point: float
    stops_level: int            # broker minimum stop distance, in points
    m15: pd.DataFrame           # candle OPEN time in `time`; closed candles only, ascending
    h1: pd.DataFrame
    h4: pd.DataFrame
    cache: dict = field(default_factory=dict)      # shared work between techniques (computed once per snapshot)

    def __post_init__(self):
        for name in ("m15", "h1", "h4"):
            df = getattr(self, name)
            missing = [c for c in COLUMNS if c not in df.columns]
            if missing:
                raise ValueError(f"{name} is missing columns {missing}")
            if not df["time"].is_monotonic_increasing:
                raise ValueError(f"{name} must be sorted by time")


@dataclass(frozen=True)
class Signal:
    technique: str              # e.g. SMC_A_OB_TREND
    symbol: str
    direction: int              # +1 buy, -1 sell
    trigger_idx: int            # index of the trigger candle in snapshot.m15
    trigger_time: pd.Timestamp  # CLOSE time of the trigger candle: the moment the signal exists
    entry_ref: float            # close of the trigger candle (the order is a market order right after)
    sl: float
    tp: float
    rr: float                   # planned reward / risk
    zone_lo: float
    zone_hi: float
    bias_dir: int               # H4 structure direction at the trigger (0 = not used)
    notes: str = ""

    @property
    def risk_price(self) -> float:
        return abs(self.entry_ref - self.sl)

    @property
    def signal_id(self) -> str:
        """Stable id: the same signal found again (next scan, restart) gets the same id."""
        return f"{self.technique}|{self.symbol}|{self.direction:+d}|{self.trigger_time:%Y%m%d%H%M}"

    def check(self):
        """Basic geometry. Raises if the signal is impossible."""
        d = self.direction
        assert d in (1, -1), "direction"
        assert (self.sl - self.entry_ref) * d < 0, f"{self.signal_id}: SL must be on the losing side"
        assert (self.tp - self.entry_ref) * d > 0, f"{self.signal_id}: TP must be on the winning side"
        assert abs(self.rr - abs(self.tp - self.entry_ref) / self.risk_price) < 1e-6, f"{self.signal_id}: rr mismatch"
        assert self.zone_lo <= self.zone_hi, "zone"


class Technique:
    name: str = ""
    title: str = ""

    def signals(self, snap: Snapshot) -> list:
        """ALL signals found in the snapshot, oldest first. Live code keeps those whose trigger is the latest candle;
        a replay over history keeps all of them. Must only use candles up to each trigger (no look-ahead)."""
        raise NotImplementedError


def as_arrays(df: pd.DataFrame):
    return (df["open"].to_numpy(float), df["high"].to_numpy(float), df["low"].to_numpy(float), df["close"].to_numpy(float))


def times_open(df: pd.DataFrame) -> np.ndarray:
    return df["time"].to_numpy(dtype="datetime64[ns]")
