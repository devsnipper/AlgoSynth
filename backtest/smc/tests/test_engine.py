"""Tests du moteur de trades avec des series M5 faites a la main (resultats connus).

Usage : backtest/.venv/Scripts/python.exe backtest/smc/tests/test_engine.py
"""
import os
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))   # backtest/smc
from core import engine as bs   # noqa: E402

T0 = pd.Timestamp("2026-01-01 00:00")
RESULTS = []


def check(name):
    def deco(fn):
        try:
            fn()
            RESULTS.append((name, True, ""))
        except Exception as e:  # noqa: BLE001
            RESULTS.append((name, False, f"{type(e).__name__}: {e}\n{traceback.format_exc(limit=2)}"))
        return fn
    return deco


def m5(rows, spread=0):
    """rows : liste de (open, high, low, close). Une bougie toutes les 5 minutes depuis T0."""
    return pd.DataFrame({"time": [T0 + pd.Timedelta(minutes=5 * i) for i in range(len(rows))],
                         "open": [r[0] for r in rows], "high": [r[1] for r in rows],
                         "low": [r[2] for r in rows], "close": [r[3] for r in rows], "spread": spread})


def order(direction, entry, stop, k=0):
    return pd.DataFrame([{"signal_time": T0 + pd.Timedelta(minutes=5 * k), "direction": direction,
                          "entry": entry, "stop": stop}])


def run(rows, direction, entry, stop, spread=0, point=1.0, stops_level=0, **kw):
    return bs.simulate_orders(order(direction, entry, stop), m5(rows, spread), point, stops_level, **kw).iloc[0]


FLAT_UP = [(101, 101.5, 100.5, 101)] * 3        # prix au-dessus de l'entree 100 : pas de remplissage


@check("achat : remplissage puis TP a +2R")
def _():
    r = run([(101, 102, 101, 101), (101, 101, 99.5, 100.5), (100.5, 105, 100, 104)], 1, 100, 98)
    assert r.status == "closed" and r.fill == 100 and r.reason == "TP", r.to_dict()
    assert r.r == 2 and r.r_level == 2 and r.tp == 104


@check("achat : SL, resultat au pire prix (-1.5R) et au niveau du stop (-1R)")
def _():
    r = run([(101, 102, 101, 101), (101, 101, 99.5, 100.5), (100, 100.5, 97, 97.5)], 1, 100, 98)
    assert r.reason == "SL" and r.r == -1.5 and r.r_level == -1, r.to_dict()


@check("pas de remplissage : l'ordre expire apres 8 bougies M15")
def _():
    r = run([(101, 101.5, 100.5, 101)] * 40, 1, 100, 98)
    assert r.status == "nofill", r.to_dict()


@check("remplissage et SL dans la meme bougie : perte")
def _():
    r = run([(101, 101, 97, 98)], 1, 100, 98)
    assert r.reason == "SL" and r.r == -1.5, r.to_dict()


@check("TP dans la bougie de remplissage ignore (ordre des evenements inconnu)")
def _():
    r = run([(101, 106, 99, 105), (105, 106, 103, 104)], 1, 100, 98)
    assert r.reason == "TP" and r.exit_time == T0 + pd.Timedelta(minutes=10), r.to_dict()


@check("ouverture au-dela de l'entree : remplissage au prix d'ouverture (achat)")
def _():
    r = run([(99, 99.5, 98.5, 99), (99, 105, 99, 104)], 1, 100, 97)
    assert r.fill == 99 and r.R_price == 2, r.to_dict()


@check("sortie par le temps apres 3 heures, au cours de cloture")
def _():
    # 36 bougies M5 = 3 h. Les bougies apres la 36e (close 100.9) ne doivent pas compter.
    rows = [(101, 101, 99.5, 100.5)] + [(100.5, 101, 99.5, 100.5)] * 35 + [(100.5, 101, 99.5, 100.9)] * 5
    r = run(rows, 1, 100, 98)
    assert r.reason == "TIME" and abs(r.r - 0.25) < 1e-9 and r.held_min == 180, r.to_dict()


@check("vente : TP et SL en miroir")
def _():
    r = run([(99, 99.5, 98, 99), (99, 100.5, 99, 99.5), (99.5, 100, 95, 96)], -1, 100, 102)
    assert r.fill == 100 and r.reason == "TP" and r.r == 2, r.to_dict()
    r = run([(99, 99.5, 98, 99), (99, 100.5, 99, 99.5), (100, 103, 99.5, 102.5)], -1, 100, 102)
    assert r.reason == "SL" and r.r == -1.5 and r.r_level == -1, r.to_dict()


@check("le spread retarde le remplissage d'un achat et agrandit le cout")
def _():
    # spread 1 : ask = bid + 1. bougie 1 : low 99.5 -> ask 100.5 > 100, pas rempli ; bougie 2 : low 98.9 -> ask 99.9
    r = run([(101, 102, 101, 101), (101, 101, 99.5, 100.5), (100.5, 101, 98.9, 99)], 1, 100, 97, spread=1)
    assert r.fill_time == T0 + pd.Timedelta(minutes=10), r.to_dict()


@check("stop trop proche (stops level + spread) : ordre ignore")
def _():
    r = run([(101, 101, 99, 100)], 1, 100, 99.6, spread=0, stops_level=1)
    assert r.status == "tooclose", r.to_dict()


@check("une seule position a la fois par symbole")
def _():
    orders = pd.concat([order(1, 100, 98, 0), order(1, 100, 98, 2)], ignore_index=True)
    rows = [(101, 101, 99.5, 100.5), (100.5, 101, 100, 100.5), (100.5, 101, 100, 100.5), (100.5, 105, 100, 104)]
    res = bs.simulate_orders(orders, m5(rows), 1.0, 0)
    assert list(res.status) == ["closed", "busy"], res


if __name__ == "__main__":
    for name, ok, msg in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"\n      {msg}" if msg else ""))
    sys.exit(0 if all(ok for _, ok, _ in RESULTS) else 1)
