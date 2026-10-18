"""Hand-built cases for the building blocks of the techniques (zone trigger, sweeps, shift, previous-day levels).

Usage : backtest/.venv/Scripts/python.exe smc_tests/test_units.py
"""
import os
import sys
from types import SimpleNamespace

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from helpers import check, report_and_exit                                         # noqa: E402

from techniques import setup_b_sweep_reversal as B                                  # noqa: E402
from techniques import structure as st                                              # noqa: E402
from techniques.ob_retest import first_trigger                                      # noqa: E402


def path(rows):
    """rows: (high, low, close) per candle -> arrays."""
    h = np.array([r[0] for r in rows], float)
    l = np.array([r[1] for r in rows], float)
    c = np.array([r[2] for r in rows], float)
    return c, h, l


ZONE = (10.0, 12.0)       # a buy zone: price must come back down into it, then close above 12


@check("buy zone: wick into the zone and a close back above it triggers on the touch candle")
def _():
    c, h, l = path([(14, 13, 13.5), (13, 11.5, 12.5), (13, 12, 12.8)])
    assert first_trigger(c, h, l, 1, *ZONE, 0, 3, 4) == 1


@check("buy zone: the close can come a few candles after the touch (within 4)")
def _():
    c, h, l = path([(14, 13, 13.5), (13, 11.5, 11.0), (12, 10.5, 11.5), (12.5, 11, 12.4)])
    assert first_trigger(c, h, l, 1, *ZONE, 0, 4, 4) == 3


@check("buy zone: too late (the 6th candle after the touch) gives nothing")
def _():
    rows = [(14, 13, 13.5), (13, 11.5, 11.0)] + [(12, 10.5, 11.0)] * 4 + [(13, 11, 12.9)]
    c, h, l = path(rows)
    assert first_trigger(c, h, l, 1, *ZONE, 0, 7, 4) is None


@check("buy zone: a close beyond the far edge kills the zone")
def _():
    c, h, l = path([(14, 13, 13.5), (13, 9.5, 9.6), (14, 9, 13.0)])
    assert first_trigger(c, h, l, 1, *ZONE, 0, 3, 4) is None


@check("buy zone: no touch inside the window gives nothing")
def _():
    c, h, l = path([(14, 13, 13.5), (14, 13, 13.6), (14, 11, 12.9)])
    assert first_trigger(c, h, l, 1, *ZONE, 0, 2, 4) is None          # the touch is at index 2, outside the window


@check("sell zone mirrors the buy zone")
def _():
    c, h, l = path([(9, 7, 8.0), (10.5, 8, 9.5), (9.5, 7, 8.0)])
    assert first_trigger(c, h, l, -1, 10.0, 12.0, 0, 3, 4) == 1       # high 10.5 enters the zone, close 9.5 is below it
    c, h, l = path([(9, 7, 8.0), (12.5, 8, 12.4), (13, 8, 12.6)])
    assert first_trigger(c, h, l, -1, 10.0, 12.0, 0, 3, 4) is None    # closes above the far edge: dead


def fake_prepared(h, l, c, prev_sl=None, prev_sh=None):
    n = len(c)
    t = np.arange("2026-01-01", n * 15, dtype="datetime64[m]")[::15][:n]
    t = np.array([np.datetime64("2026-01-01T00:00") + np.timedelta64(15 * i, "m") for i in range(n)])
    return SimpleNamespace(n=n, t_open=t, h=np.array(h, float), l=np.array(l, float), c=np.array(c, float),
                           m15_struct={"prev_sl": np.array(prev_sl if prev_sl is not None else [np.nan] * n, float),
                                       "prev_sh": np.array(prev_sh if prev_sh is not None else [np.nan] * n, float)})


NAN = np.nan


@check("sweep: wick above the previous-day high with a close back below is a short sweep")
def _():
    p = fake_prepared([9, 9, 9, 10.5, 9], [8, 8, 8, 9, 8], [8.5, 8.5, 8.5, 9.8, 8.5])
    prev_hi = np.array([10.0] * 5)
    nanarr = np.full(5, NAN)
    s = B.find_sweeps(p, [], prev_hi, nanarr, nanarr, nanarr)
    assert s == [(3, -1, 10.5, "previous-day high")], s


@check("sweep: a close above the level is a breakout, not a sweep")
def _():
    p = fake_prepared([9, 9, 9, 10.5, 9], [8, 8, 8, 9, 8], [8.5, 8.5, 8.5, 10.2, 8.5])
    nanarr = np.full(5, NAN)
    assert B.find_sweeps(p, [], np.array([10.0] * 5), nanarr, nanarr, nanarr) == []


@check("sweep: wick below the previous-day low with a close back above is a long sweep")
def _():
    p = fake_prepared([9, 9, 9, 9, 9], [8, 8, 8, 6.5, 8], [8.5, 8.5, 8.5, 7.5, 8.5])
    nanarr = np.full(5, NAN)
    s = B.find_sweeps(p, [], nanarr, np.array([7.0] * 5), nanarr, nanarr)
    assert s == [(3, 1, 6.5, "previous-day low")], s


@check("sweep: an equal-highs pool is used from the moment it is known, and only once")
def _():
    t0 = np.datetime64("2026-01-01T00:00")
    p = fake_prepared([9, 10.5, 10.6, 9, 9], [8, 8, 8, 8, 8], [8.5, 9.8, 10.7, 8.5, 8.5])
    known = t0 + np.timedelta64(15, "m")                   # known from the opening of candle 1
    pools = [(1, 10.0, known, known + np.timedelta64(1000, "h"))]
    nanarr = np.full(5, NAN)
    s = B.find_sweeps(p, pools, nanarr, nanarr, nanarr, nanarr)
    assert s == [(1, -1, 10.5, "equal highs")], s           # candle 2 closes above the used pool: no second sweep


@check("sweep: a pool that is not known yet is ignored")
def _():
    t0 = np.datetime64("2026-01-01T00:00")
    p = fake_prepared([9, 10.5, 9], [8, 8, 8], [8.5, 9.8, 8.5])
    known = t0 + np.timedelta64(30, "m")                   # known only from candle 2
    pools = [(1, 10.0, known, known + np.timedelta64(1000, "h"))]
    nanarr = np.full(3, NAN)
    assert B.find_sweeps(p, pools, nanarr, nanarr, nanarr, nanarr) == []


@check("shift: after a short sweep, a close below the last swing low triggers; a close above the sweep high cancels")
def _():
    prev_sl = [8.0] * 8
    p = fake_prepared([9, 9, 9, 10.5, 9.8, 9.6, 9.0, 9.0], [8.5, 8.5, 8.5, 9, 9.2, 8.8, 7.5, 7.5],
                      [8.9, 8.9, 8.9, 9.8, 9.5, 9.0, 7.9, 7.9], prev_sl=prev_sl)
    out = B.shift_triggers(p, [(3, -1, 10.5, "x")])
    assert out == [(6, -1, 10.5, "x", 3)], out
    p2 = fake_prepared([9, 9, 9, 10.5, 10.8, 9.6, 9.0, 9.0], [8.5, 8.5, 8.5, 9, 9.5, 8.8, 7.5, 7.5],
                       [8.9, 8.9, 8.9, 9.8, 10.7, 9.0, 7.9, 7.9], prev_sl=prev_sl)
    assert B.shift_triggers(p2, [(3, -1, 10.5, "x")]) == []         # candle 4 closes above 10.5 first


@check("shift: a swing low that is already above the sweep candle's close is not used")
def _():
    p = fake_prepared([9, 9, 9, 10.5, 9], [8, 8, 8, 9, 8], [8.5, 8.5, 8.5, 9.8, 8.5], prev_sl=[9.9] * 5)
    assert B.shift_triggers(p, [(3, -1, 10.5, "x")]) == []


@check("previous-day levels: the day before, only if it is complete and adjacent")
def _():
    day = np.timedelta64(1, "D")
    d0 = np.datetime64("2026-03-01")
    t = np.concatenate([d0 + np.arange(96) * np.timedelta64(15, "m"),                 # day 1: complete
                        d0 + day + np.arange(96) * np.timedelta64(15, "m"),           # day 2: complete
                        d0 + 2 * day + np.arange(40) * np.timedelta64(15, "m"),       # day 3: partial
                        d0 + 4 * day + np.arange(96) * np.timedelta64(15, "m")])      # day 5: day 4 is missing
    h = np.concatenate([np.full(96, 10.0), np.full(96, 20.0), np.full(40, 30.0), np.full(96, 40.0)])
    l = h - 1
    hi, lo = B.previous_day_levels(t.astype("datetime64[ns]"), h, l)
    assert np.isnan(hi[:96]).all()                                   # no previous day
    assert (hi[96:192] == 10.0).all() and (lo[96:192] == 9.0).all()
    assert (hi[192:232] == 20.0).all()                               # day 3 sees day 2
    assert np.isnan(hi[232:]).all()                                  # day 5: previous calendar day is missing


@check("map_htf: a higher-timeframe candle is only used after it has closed")
def _():
    h1_open = np.array(["2026-01-01T00:00", "2026-01-01T01:00", "2026-01-01T02:00"], dtype="datetime64[ns]")
    m15_open = np.array(["2026-01-01T00:45", "2026-01-01T01:00", "2026-01-01T01:45"], dtype="datetime64[ns]")
    out = st.map_htf(h1_open, 60, m15_open, [10.0, 20.0, 30.0])
    # M15 at 00:45 closes at 01:00 -> H1 #0 (closes 01:00) is usable; M15 at 01:00 closes 01:15 -> still H1 #0;
    # M15 at 01:45 closes 02:00 -> H1 #1 (closes 02:00) is usable
    assert out.tolist() == [10.0, 10.0, 20.0], out


if __name__ == "__main__":
    report_and_exit()
