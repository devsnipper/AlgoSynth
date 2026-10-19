"""Checks on the real signals of the three techniques: geometry, ids, and no look-ahead.

Usage : backtest/.venv/Scripts/python.exe smc_tests/test_signals.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from helpers import check, have_data, real_snapshot, report_and_exit               # noqa: E402

from techniques import registry                                                     # noqa: E402

SYMBOLS = [s for s in ("Boom 500 Index", "Crash 500 Index", "Boom 900 Index", "Crash 900 Index") if have_data(s)]
N = 30000                                                                          # candles kept for the truncation test


@check("every signal has a valid geometry and matches its trigger candle")
def _():
    counts = {}
    for sym in SYMBOLS:
        snap = real_snapshot(sym)
        m15 = snap.m15
        for tech in registry.ACTIVE:
            sigs = tech.signals(snap)
            ids = [s.signal_id for s in sigs]
            assert len(ids) == len(set(ids)), f"{sym} {tech.name}: duplicate ids"
            assert [s.trigger_idx for s in sigs] == sorted(s.trigger_idx for s in sigs)
            for s in sigs:
                s.check()
                i = s.trigger_idx
                assert abs(s.entry_ref - m15["close"].iloc[i]) < 1e-9, "entry is the close of the trigger candle"
                assert s.trigger_time == m15["time"].iloc[i] + np.timedelta64(15, "m"), "signal exists at the candle close"
                if tech.name != "SMC_B_SWEEP_REV":
                    assert s.bias_dir == s.direction, "A and C trade with the H4 bias"
                    assert (s.sl < s.zone_lo) if s.direction == 1 else (s.sl > s.zone_hi), "SL beyond the zone"
                if tech.name == "SMC_A_OB_TREND":
                    assert abs(s.rr - 2.0) < 1e-9
                if tech.name == "SMC_B_SWEEP_REV":
                    assert abs(s.rr - 3.0) < 1e-9
                if tech.name == "SMC_C_PD_OB_FVG":
                    assert 2.0 - 1e-9 <= s.rr <= 3.0 + 1e-9, "C targets between 1:2 and 1:3"
            counts[tech.name] = counts.get(tech.name, 0) + len(sigs)
    assert all(v > 0 for v in counts.values()), counts
    return ", ".join(f"{k.split('_')[1]}={v}" for k, v in sorted(counts.items())) + f" signals on {len(SYMBOLS)} symbols"


@check("no look-ahead: the signals before candle N are identical whether or not the later history exists")
def _():
    lines = []
    for sym in SYMBOLS[:2]:
        full, cut = real_snapshot(sym), real_snapshot(sym, first_n=N)
        for tech in registry.ACTIVE:
            a = [(s.trigger_idx, s.direction, round(s.entry_ref, 6), round(s.sl, 6), round(s.tp, 6))
                 for s in tech.signals(full) if s.trigger_idx < N]
            b = [(s.trigger_idx, s.direction, round(s.entry_ref, 6), round(s.sl, 6), round(s.tp, 6))
                 for s in tech.signals(cut)]
            assert a == b, f"{sym} {tech.name}: {len(a)} vs {len(b)} signals differ"
            lines.append(f"{tech.name.split('_')[1]}:{len(a)}")
    return "identical for " + " ".join(lines)


@check("the live-style scan (a window of recent candles) finds the same signals as the full history")
def _():
    sym = SYMBOLS[0]
    full = real_snapshot(sym)
    window = real_snapshot(sym, last_n=1500)
    offset = len(full.m15) - len(window.m15)
    checked = 0
    for tech in registry.ACTIVE:
        full_ids = {s.signal_id for s in tech.signals(full)}
        for s in tech.signals(window):
            if s.trigger_idx >= 800:                      # leave the warm-up part of the window out
                assert s.signal_id in full_ids, f"{tech.name}: {s.signal_id} appears only in the window"
                checked += 1
    return f"{checked} window signals all present in the full history"


@check("registry: priority order is C, A, B and signals come sorted by candle then priority")
def _():
    assert [t.name for t in registry.ACTIVE] == ["SMC_C_PD_OB_FVG", "SMC_A_OB_TREND", "SMC_B_SWEEP_REV"]
    snap = real_snapshot(SYMBOLS[0], last_n=6000)
    rank = {t.name: i for i, t in enumerate(registry.ACTIVE)}
    sigs = registry.all_signals(snap)
    keys = [(s.trigger_idx, rank[s.technique]) for s in sigs]
    assert keys == sorted(keys) and len(sigs) > 0


if __name__ == "__main__":
    report_and_exit()
