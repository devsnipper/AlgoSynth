"""The interface every setup follows.

A setup answers one question: "on which M15 candles did this pattern complete, and in which direction
should we trade?" Everything else (entry, stop, statistics, reports) is done by core/.

    detect(ctx) -> DataFrame with columns
        t           index of the M15 candle whose CLOSE completes the pattern (the signal)
        direction   +1 (long) or -1 (short)
    plus optional extra columns (zone_lo, zone_hi, ...), kept for the trading stage.

Rules for detect():
  - use only candles <= t when deciding about candle t (no look-ahead; tests/test_setups_causal.py checks it)
  - do not read files; everything comes from ctx
"""
import pandas as pd


class Setup:
    name: str = ""            # same as the folder name, e.g. "s02_range_sweep"
    title: str = ""
    uses_bias: bool = True    # False when the H1 bias is part of the definition itself (setup 6)

    def detect(self, ctx) -> pd.DataFrame:
        raise NotImplementedError


def events_frame(t, direction, **extra) -> pd.DataFrame:
    """Build a normalized events table: sorted by t, one row per (t, direction)."""
    df = pd.DataFrame({"t": list(t), "direction": list(direction), **{k: list(v) for k, v in extra.items()}})
    if df.empty:
        return pd.DataFrame({"t": pd.Series(dtype=int), "direction": pd.Series(dtype=int), **{k: pd.Series(dtype=float) for k in extra}})
    df["t"] = df["t"].astype(int)
    df["direction"] = df["direction"].astype(int)
    return df.drop_duplicates(["t", "direction"]).sort_values(["t", "direction"]).reset_index(drop=True)
