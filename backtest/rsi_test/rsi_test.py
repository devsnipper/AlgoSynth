"""Test RSI sur Boom/Crash : l'RSI predit-il un spike ? Marque-t-il de meilleures zones ?

Usage : .venv/Scripts/python.exe backtest/rsi_test/rsi_test.py
Donnees : backtest/backtesting_1/data (telechargees par download_data.py)
"""
import json
import os

import numpy as np
import pandas as pd

HERE     = os.path.dirname(__file__)
DATA_DIR = os.path.join(HERE, "..", "backtesting_1", "data")
INFO     = json.load(open(os.path.join(DATA_DIR, "symbol_info.json")))
SYMBOLS  = ["Boom 150 Index", "Boom 500 Index", "Boom 600 Index", "Boom 900 Index",
            "Crash 150 Index", "Crash 500 Index"]

RSI_PERIOD = 14
BINS   = [0, 20, 30, 50, 70, 80, 101]
LABELS = ["<20", "20-30", "30-50", "50-70", "70-80", ">80"]
SPIKE_MULT = 8          # barre-spike : amplitude > 8x la mediane
SPIKE_WINDOW = 5        # un spike dans les 5 prochaines barres
Z = 1.96


def rsi(close: pd.Series, n: int = RSI_PERIOD) -> pd.Series:
    """RSI de Wilder, causal (n'utilise que les barres passees)."""
    d = close.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn.replace(0, np.nan))


def load(symbol: str, tf: str) -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, f"{symbol.replace(' ', '_')}_{tf}.csv"), parse_dates=["time"])


def wilson(k: int, n: int):
    if n == 0:
        return np.nan, np.nan
    p = k / n
    den = 1 + Z ** 2 / n
    c = (p + Z ** 2 / (2 * n)) / den
    h = Z * np.sqrt(p * (1 - p) / n + Z ** 2 / (4 * n ** 2)) / den
    return c - h, c + h


def prepare(symbol: str, tf: str) -> dict:
    df = load(symbol, tf)
    pt = INFO[symbol]["point"]
    sign = -1 if symbol.startswith("Boom") else 1       # +1 = mouvement favorable au bot
    rng = df.high - df.low
    against = (df.close - df.open) * (-sign) > 0         # barre dans le sens du spike
    spike = ((rng > SPIKE_MULT * rng.median()) & against).to_numpy()
    r = rsi(df.close).to_numpy()
    close = df.close.to_numpy()
    # spike dans les SPIKE_WINDOW barres suivantes (barres i+1 .. i+W)
    cs = np.concatenate([[0], np.cumsum(spike)])
    n = len(df)
    nxt = np.full(n, np.nan)
    for i in range(n - SPIKE_WINDOW):
        nxt[i] = (cs[i + 1 + SPIKE_WINDOW] - cs[i + 1]) > 0
    return {"df": df, "pt": pt, "sign": sign, "spike": spike, "rsi": r, "close": close, "next_spike": nxt, "n": n}


def spike_table(d: dict) -> pd.DataFrame:
    ok = ~np.isnan(d["rsi"]) & ~np.isnan(d["next_spike"]) & (np.arange(d["n"]) >= 200)
    cat = pd.cut(pd.Series(d["rsi"][ok]), BINS, labels=LABELS, right=False)
    y = d["next_spike"][ok]
    base = y.mean()
    rows = []
    for lab in LABELS:
        m = (cat == lab).to_numpy()
        n, k = int(m.sum()), int(y[m].sum())
        lo, hi = wilson(k, n)
        rows.append({"rsi": lab, "bars": n, "P(spike)": k / n if n else np.nan,
                     "ci_lo": lo, "ci_hi": hi,
                     "differs": bool(n >= 100 and (lo > base or hi < base))})
    t = pd.DataFrame(rows)
    t.attrs["base"] = base
    return t


def forward_table(d: dict, horizons) -> pd.DataFrame:
    """Rendement signe (points) apres k barres, par zone RSI. Echantillon espace de k barres
    pour que les fenetres ne se chevauchent pas (sinon l'erreur est sous-estimee)."""
    n = d["n"]
    rows = []
    for k in horizons:
        idx = np.arange(200, n - k, k)
        ret = (d["close"][idx + k] - d["close"][idx]) / d["pt"] * d["sign"]
        r = d["rsi"][idx]
        base = ret.mean()
        half = len(idx) // 2
        cat = pd.cut(pd.Series(r), BINS, labels=LABELS, right=False)
        for lab in LABELS:
            m = (cat == lab).to_numpy()
            x = ret[m]
            if len(x) < 30:
                rows.append({"k": k, "rsi": lab, "n": len(x)})
                continue
            se = x.std(ddof=1) / np.sqrt(len(x))
            t = (x.mean() - base) / se if se > 0 else np.nan
            h1 = ret[m & (np.arange(len(idx)) < half)]
            h2 = ret[m & (np.arange(len(idx)) >= half)]
            rows.append({"k": k, "rsi": lab, "n": len(x), "mean_pts": x.mean(), "base_pts": base,
                         "t_vs_base": t,
                         "half1": h1.mean() if len(h1) else np.nan, "half2": h2.mean() if len(h2) else np.nan})
    return pd.DataFrame(rows)


def main():
    pd.set_option("display.width", 200)
    total_tests = flagged = 0
    robust = []
    for tf, horizons in [("M1", (5, 15, 30)), ("M5", (1, 3, 6))]:
        print(f"\n{'#' * 70}\n# TIMEFRAME {tf}\n{'#' * 70}")
        for s in SYMBOLS:
            d = prepare(s, tf)
            st = spike_table(d)
            print(f"\n== {s} {tf} : P(spike against the bot in next {SPIKE_WINDOW} bars) by RSI "
                  f"(overall {st.attrs['base']:.3f})")
            print(st.round(3).to_string(index=False))
            total_tests += int((st.bars >= 100).sum())
            flagged += int(st.differs.sum())

            ft = forward_table(d, horizons)
            print(f"-- signed forward return (pts, + = good for bot), non-overlapping")
            print(ft.round(1).to_string(index=False))
            ok = ft.dropna(subset=["t_vs_base"])
            total_tests += len(ok)
            sig = ok[ok.t_vs_base.abs() > 2]
            flagged += len(sig)
            for _, row in sig.iterrows():
                same = np.sign(row.half1) == np.sign(row.half2) == np.sign(row.mean_pts - row.base_pts)
                if same:
                    robust.append((s, tf, row.k, row.rsi, row.mean_pts, row.base_pts, row.t_vs_base))

    print(f"\n{'=' * 70}\nSUMMARY\n{'=' * 70}")
    print(f"tests run: {total_tests} | flagged (|t|>2 or CI excludes baseline): {flagged} "
          f"| expected by pure chance (~5%): {total_tests * 0.05:.0f}")
    print(f"flagged AND same direction in both halves: {len(robust)}")
    for x in robust:
        print("  ", x)


if __name__ == "__main__":
    main()
