"""Diagnostic : les setups SMC contiennent-ils de l'information, independamment du design d'entree ?

Pour chaque setup (periode d'entrainement seulement) on entre AU MARCHE a l'ouverture de la bougie M5 suivante,
avec le meme stop que le setup et une cible a 2R (R = distance entree-stop). Puis on compare :
  - la direction du setup           (strategie)
  - la direction inverse            (meme heure, meme distance de stop, sens oppose)
  - des heures aleatoires           (meme distance de stop, sens aleatoire, 30 tirages)
Si les setups avaient une information, la direction du setup battrait nettement les deux autres.

Usage : backtest/.venv/Scripts/python.exe backtest/smc/tools/diagnose_setups.py
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))   # backtest/smc
sys.path.insert(0, os.path.dirname(__file__))
from core import constants as K, data, engine   # noqa: E402
import reference_orders as ref                 # noqa: E402

RNG = np.random.default_rng(7)
N_DRAWS = 30


def market_orders(setups: pd.DataFrame, m5: pd.DataFrame, flip: bool = False) -> pd.DataFrame:
    """Ordres au marche a l'ouverture de la premiere bougie M5 apres le signal, meme distance de stop."""
    t5 = m5["time"].to_numpy()
    i = np.searchsorted(t5, setups["signal_time"].to_numpy(), side="left")
    ok = i < len(m5)
    s, i = setups[ok], i[ok]
    px = m5["open"].to_numpy()[i]
    sp = m5["spread"].to_numpy()[i]
    return s, i, px, sp


def build(setups, m5, point, flip=False):
    s, i, px, sp = market_orders(setups, m5)
    d = s["direction"].to_numpy().copy()
    dist = np.abs(px - s["stop"].to_numpy())
    if flip:
        d = -d
    # achat : entree a l'ask ; vente : entree au bid. L'ordre limite est place au prix courant -> rempli a l'ouverture.
    entry = np.where(d == 1, px + sp * point, px)
    stop = entry - d * dist
    return pd.DataFrame({"signal_time": s["signal_time"].to_numpy(), "direction": d, "entry": entry, "stop": stop})


def random_orders(setups, m5, point, rng, dists):
    t5 = m5["time"]
    lo = max(K.WINDOW_START, t5.iloc[0])
    pool = np.where((t5 >= lo) & (t5 < K.SPLIT))[0]
    pick = rng.choice(pool, size=len(dists), replace=False)
    pick.sort()
    px = m5["open"].to_numpy()[pick]
    sp = m5["spread"].to_numpy()[pick]
    d = rng.choice([-1, 1], size=len(dists))
    # memes distances de stop (entree au marche -> stop) que les vrais setups
    dist = rng.permutation(dists)[: len(pick)]
    entry = np.where(d == 1, px + sp * point, px)
    return pd.DataFrame({"signal_time": t5.to_numpy()[pick], "direction": d, "entry": entry, "stop": entry - d * dist})


def stats(res):
    cl = res[res.status == "closed"]
    return {"trades": len(cl), "win%": (cl.reason == "TP").mean() * 100 if len(cl) else np.nan,
            "mean_R": cl.r.mean(), "mean_R_at_stop_level": cl.r_level.mean()}


def main():
    info = data.symbol_info()
    rows = []
    for htf in ("H4", "H1"):
        for bias_name, bias in (("with bias filter", "dir"), ("no bias filter", "none")):
            agg = {"setup": [], "flipped": []}
            rnd = [[] for _ in range(N_DRAWS)]
            for s in info:
                m5 = data.load(s, "M5")
                p, sl = info[s]["point"], info[s]["stops_level"]
                setups = ref.build_orders(s, htf, bias=bias)
                setups = setups[(setups.signal_time >= K.WINDOW_START) & (setups.signal_time < K.SPLIT)]
                if len(setups) < 5:
                    continue
                base = build(setups, m5, p)
                dists = np.abs(base["entry"].to_numpy() - base["stop"].to_numpy())
                for name, flip in (("setup", False), ("flipped", True)):
                    o = build(setups, m5, p, flip)
                    r = engine.simulate_orders(o, m5, p, sl)
                    agg[name].append(r[r.status == "closed"])
                rng = np.random.default_rng(100 + len(s))
                for k in range(N_DRAWS):
                    o = random_orders(setups, m5, p, rng, dists)
                    r = engine.simulate_orders(o, m5, p, sl)
                    rnd[k].append(r[r.status == "closed"])
            a = pd.concat(agg["setup"]); f = pd.concat(agg["flipped"])
            means = np.array([pd.concat(x).r.mean() for x in rnd])
            wins = np.array([(pd.concat(x).reason == "TP").mean() * 100 for x in rnd])
            ntr = np.mean([len(pd.concat(x)) for x in rnd])
            rows += [
                {"HTF": htf, "filter": bias_name, "entries": "SMC setup direction", "trades": len(a),
                 "win%": (a.reason == "TP").mean() * 100, "mean_R": a.r.mean()},
                {"HTF": htf, "filter": bias_name, "entries": "same time, opposite direction", "trades": len(f),
                 "win%": (f.reason == "TP").mean() * 100, "mean_R": f.r.mean()},
                {"HTF": htf, "filter": bias_name, "entries": f"random time/direction (mean of {N_DRAWS})",
                 "trades": ntr, "win%": wins.mean(), "mean_R": means.mean()},
                {"HTF": htf, "filter": bias_name, "entries": "   random: 5th-95th percentile of mean R",
                 "trades": np.nan, "win%": np.nan,
                 "mean_R": f"{np.percentile(means, 5):.3f} to {np.percentile(means, 95):.3f}"},
            ]
    out = pd.DataFrame(rows)
    pd.set_option("display.width", 200)
    print(f"Market-entry diagnostic, TRAIN ONLY ({K.WINDOW_START.date()} -> {K.SPLIT.date()}), target 2R\n")
    print(out.to_string(index=False, float_format=lambda x: f"{x:.3f}"))


if __name__ == "__main__":
    main()
