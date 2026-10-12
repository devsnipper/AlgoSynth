"""Tests de smc_causal.py : cas faits a la main, absence de look-ahead, comparaison a la librairie.

Usage : backtest/.venv/Scripts/python.exe backtest/smc/tests/test_primitives.py
"""
import os
import sys
import traceback

os.environ["SMC_CREDIT"] = "0"        # coupe le message de la librairie

import numpy as np
import pandas as pd

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, ".."))     # backtest/smc

from core import primitives as sc        # noqa: E402
from core.data import load as _load      # noqa: E402
RESULTS = []


def check(name):
    def deco(fn):
        try:
            msg = fn()
            RESULTS.append((name, True, msg or ""))
        except Exception as e:  # noqa: BLE001
            RESULTS.append((name, False, f"{type(e).__name__}: {e}\n{traceback.format_exc(limit=2)}"))
        return fn
    return deco


def frame(o, h, l, c, spread=0):
    n = len(o)
    return pd.DataFrame({"time": pd.date_range("2026-01-01", periods=n, freq="15min"),
                         "open": o, "high": h, "low": l, "close": c, "spread": spread})


# Serie construite a la main (L=2). Explication dans le commentaire de chaque bloc.
#  idx 2 : swing high 15 (confirme a t=4)      idx 5 : swing low 6 (confirme a t=7)
#  idx 8 : sweep (low 5 < 6, close 8 > 6)      idx 11 : close 15.5 > 15 -> cassure de structure
# Un swing n'est calculable qu'a partir de l'indice 2L-1 (meme regle que la librairie) : on ajoute donc
# 3 bougies de remplissage tres au-dessus du reste, ce qui decale tous les indices de 3.
O = [27, 26, 25] + [10, 10, 11, 14, 12, 10, 7, 8, 9, 8, 10, 12]
H = [30, 29, 28] + [11, 12, 15, 14, 13, 11, 9, 10, 10, 11, 13, 16]
Lw = [25, 24, 23] + [9, 10, 11, 11, 9, 6, 7, 8, 5, 7, 9, 11]
C = [27, 26, 25] + [10, 11, 14, 12, 10, 7, 8, 9, 8, 10, 12, 15.5]


@check("swing connu seulement L bougies apres sa formation")
def _():
    st = sc.structure(np.array(H, float), np.array(Lw, float), np.array(C, float), L=2)
    # swing high (15) en idx 5 -> confirme a t=7 -> visible dans prev_sh a partir de t=8
    assert np.isnan(st["prev_sh"][7]), "swing visible trop tot"
    assert st["prev_sh"][8] == 15, st["prev_sh"][8]
    # swing low (6) en idx 8 -> confirme a t=10 -> visible dans prev_sl a partir de t=11
    assert np.isnan(st["prev_sl"][10]) or st["prev_sl"][10] != 6, "swing low visible trop tot"
    assert st["prev_sl"][11] == 6, st["prev_sl"][11]


@check("cassure de structure (BOS) a la fermeture, une seule fois")
def _():
    st = sc.structure(np.array(H, float), np.array(Lw, float), np.array(C, float), L=2)
    assert st["dir"][13] != 1 and st["dir"][14] == 1, st["dir"]


@check("setup long : sweep + shift + order block + stop (cas main)")
def _():
    s = sc.find_setups(frame(O, H, Lw, C), point=1.0, L=2)
    assert len(s) == 1, s
    r = s.iloc[0]
    assert r.direction == 1 and r.signal_idx == 14 and r.sweep_idx == 11 and r.ob_idx == 11, r.to_dict()
    assert r.entry == 7.5 and r.stop == 5.0, (r.entry, r.stop)
    assert r.expire_idx == 22


@check("setup short : meme cas en miroir")
def _():
    f = frame([20 - x for x in O], [20 - x for x in Lw], [20 - x for x in H], [20 - x for x in C])
    s = sc.find_setups(f, point=1.0, L=2)
    assert len(s) == 1, s
    r = s.iloc[0]
    assert r.direction == -1 and r.signal_idx == 14 and r.ob_idx == 11, r.to_dict()
    assert r.entry == 12.5 and r.stop == 15.0, (r.entry, r.stop)


@check("le spread elargit le stop")
def _():
    s = sc.find_setups(frame(O, H, Lw, C, spread=2), point=0.5, L=2)
    assert s.iloc[0].stop == 4.0, s.iloc[0].stop     # 5 - 2*0.5


@check("clip_spikes est causal et reduit seulement les spikes")
def _():
    rng = np.random.default_rng(1)
    base = 100 + np.cumsum(rng.normal(0, 0.1, 400))
    f = frame(base, base + 0.1, base - 0.1, base + 0.02)
    f.loc[300, "high"] = base[300] + 50                   # spike
    a = sc.clip_spikes(f)
    assert a.loc[300, "high"] < 101 and (a.drop(index=300)["high"] == f.drop(index=300)["high"]).all()
    b = sc.clip_spikes(f.iloc[:310].copy())               # tronque : memes valeurs sur le debut
    assert np.allclose(a.iloc[:310][["high", "low"]].to_numpy(), b[["high", "low"]].to_numpy())


load = _load


@check("pas de look-ahead sur donnees reelles (sorties identiques si on tronque)")
def _():
    out = []
    for symbol in ("Boom 500 Index", "Crash 500 Index"):
        m15, h1, h4 = load(symbol, "M15"), load(symbol, "H1"), load(symbol, "H4")
        for htf, mins in ((h4, 240), (h1, 60)):
            for clip in (False, True):
                N = 30000
                full_ctx = sc.htf_context(m15["time"], htf, mins, 3, clip)
                full = sc.find_setups(m15, 0.001, full_ctx, 5, clip)
                a = m15.iloc[:N].reset_index(drop=True)
                last_close = a["time"].iloc[-1] + pd.Timedelta(minutes=15)
                htf_a = htf[htf["time"] + pd.Timedelta(minutes=mins) <= last_close].reset_index(drop=True)
                part_ctx = sc.htf_context(a["time"], htf_a, mins, 3, clip)
                part = sc.find_setups(a, 0.001, part_ctx, 5, clip)
                ref = full[full.signal_idx < N].reset_index(drop=True)
                # un setup tout pres de N peut ne pas avoir fini sa fenetre : on compare ceux fermes avant N
                pd.testing.assert_frame_equal(part, ref, check_dtype=False, rtol=1e-9)
                out.append(f"{symbol[:10]}/{mins}m/clip={clip}: {len(part)} setups identiques")
    return "; ".join(out[:2]) + f" ... ({len(out)} combinaisons)"


@check("memes swings que la librairie smartmoneyconcepts (interieur des donnees)")
def _():
    try:
        from smartmoneyconcepts import smc
    except ImportError:
        return "SKIP (librairie non installee)"
    m15 = load("Boom 500 Index", "M15").iloc[:20000].reset_index(drop=True)
    L = 5
    lib = smc.swing_highs_lows(m15[["open", "high", "low", "close"]], swing_length=L)
    sh, sl = sc.raw_swings(m15["high"].to_numpy(), m15["low"].to_numpy(), L)
    interior = slice(4 * L, len(m15) - 4 * L)                     # on ignore les bords forces par la librairie
    lib_hi = (lib["HighLow"].to_numpy() == 1)
    lib_lo = (lib["HighLow"].to_numpy() == -1)
    hi_missing = (lib_hi & ~sh)[interior].sum()
    lo_missing = (lib_lo & ~sl)[interior].sum()
    assert hi_missing == 0 and lo_missing == 0, (hi_missing, lo_missing)
    # nos swings = ceux de la librairie + ceux qu'elle supprime (swings consecutifs du meme type)
    ours = int(sh[interior].sum() + sl[interior].sum())
    theirs = int(lib_hi[interior].sum() + lib_lo[interior].sum())
    # niveaux identiques
    lvl_ok = np.allclose(lib["Level"].to_numpy()[interior][lib_hi[interior]],
                         m15["high"].to_numpy()[interior][lib_hi[interior]])
    assert lvl_ok
    return f"swings librairie: {theirs}, les notres: {ours} (tous ceux de la librairie sont inclus, niveaux egaux)"


@check("memes FVG que la librairie")
def _():
    try:
        from smartmoneyconcepts import smc
    except ImportError:
        return "SKIP (librairie non installee)"
    m15 = load("Crash 500 Index", "M15").iloc[:20000].reset_index(drop=True)
    lib = smc.fvg(m15[["open", "high", "low", "close"]])["FVG"].to_numpy()
    bull, bear = sc.fvg_flags(*(m15[x].to_numpy() for x in ("open", "high", "low", "close")))
    assert np.array_equal(lib == 1, bull) and np.array_equal(lib == -1, bear)
    return f"{int(bull.sum())} haussiers, {int(bear.sum())} baissiers identiques"


if __name__ == "__main__":
    for name, ok, msg in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"\n      {msg}" if msg else ""))
    sys.exit(0 if all(ok for _, ok, _ in RESULTS) else 1)
