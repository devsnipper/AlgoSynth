"""Briques SMC sans look-ahead (voir SMC_STRATEGY.md).

Regle d'or : chaque valeur indexee t n'utilise que les bougies <= t (bougie t fermee).
 - un swing en i n'est connu qu'a la fermeture de la bougie i + L
 - une bougie HTF n'est utilisee qu'une fois fermee
 - un setup detecte a la fermeture de t sert a placer un ordre a partir de t + 1
"""
import numpy as np
import pandas as pd

M15_MIN = 15


def clip_spikes(df: pd.DataFrame, mult: float = 8.0, window: int = 200) -> pd.DataFrame:
    """Version B : reduit les meches des bougies-spike (amplitude > mult x mediane des 200 bougies
    precedentes) a 1 amplitude normale au-dela du corps. Causal (mediane sur le passe)."""
    rng = df["high"] - df["low"]
    med = rng.shift(1).rolling(window, min_periods=20).median()
    spike = (rng > mult * med).fillna(False)
    out = df.copy()
    body_hi = np.maximum(df["open"], df["close"])
    body_lo = np.minimum(df["open"], df["close"])
    out.loc[spike, "high"] = np.minimum(df["high"], body_hi + med)[spike]
    out.loc[spike, "low"] = np.maximum(df["low"], body_lo - med)[spike]
    return out


def raw_swings(high: np.ndarray, low: np.ndarray, L: int):
    """Meme definition que la librairie smartmoneyconcepts : swing high en i si
    high[i] == max(high[i-L+1 .. i+L]). Connu a la fermeture de la bougie i + L."""
    roll_hi = pd.Series(high).shift(-L).rolling(2 * L).max().to_numpy()
    roll_lo = pd.Series(low).shift(-L).rolling(2 * L).min().to_numpy()
    return high == roll_hi, low == roll_lo


def fvg_flags(o, h, l, c):
    """FVG haussier/baissier sur la bougie j (3 bougies j-1, j, j+1). Connu a la fermeture de j+1."""
    n = len(o)
    bull = np.zeros(n, bool)
    bear = np.zeros(n, bool)
    bull[1:-1] = (h[:-2] < l[2:]) & (c[1:-1] > o[1:-1])
    bear[1:-1] = (l[:-2] > h[2:]) & (c[1:-1] < o[1:-1])
    return bull, bear


def structure(high, low, close, L: int) -> dict:
    """Machine d'etat causale : dernier swing high/low confirmes, cassures (BOS), direction.
    Les tableaux *_prev decrivent l'etat AVANT la bougie t, les autres l'etat APRES (connu a la fermeture de t)."""
    n = len(close)
    sh, sl = raw_swings(high, low, L)
    direction = np.zeros(n, np.int8)
    rl = np.full(n, np.nan)
    rh = np.full(n, np.nan)
    prev_sh = np.full(n, np.nan)
    prev_sl = np.full(n, np.nan)
    last_sh = last_sl = np.nan
    sh_open = sl_open = False      # niveau pas encore casse
    d = 0
    for t in range(n):
        prev_sh[t], prev_sl[t] = last_sh, last_sl
        i = t - L
        if i >= 0:
            if sh[i]:
                last_sh, sh_open = high[i], True
            if sl[i]:
                last_sl, sl_open = low[i], True
        if sh_open and close[t] > last_sh:
            d, sh_open = 1, False
        elif sl_open and close[t] < last_sl:
            d, sl_open = -1, False
        direction[t], rl[t], rh[t] = d, last_sl, last_sh
    return {"dir": direction, "range_low": rl, "range_high": rh, "prev_sh": prev_sh, "prev_sl": prev_sl}


def htf_context(m15_time: pd.Series, htf: pd.DataFrame, htf_minutes: int, Lh: int = 3,
                clip: bool = False) -> dict:
    """Pour chaque bougie M15 t : direction et plage de la derniere bougie HTF FERMEE a la fermeture de t."""
    h = clip_spikes(htf) if clip else htf
    st = structure(h["high"].to_numpy(), h["low"].to_numpy(), h["close"].to_numpy(), Lh)
    htf_close = (htf["time"] + pd.Timedelta(minutes=htf_minutes)).to_numpy()
    m15_close = (m15_time + pd.Timedelta(minutes=M15_MIN)).to_numpy()
    k = np.searchsorted(htf_close, m15_close, side="right") - 1
    ok = k >= 0
    kk = np.where(ok, k, 0)
    return {"dir": np.where(ok, st["dir"][kk], 0),
            "range_low": np.where(ok, st["range_low"][kk], np.nan),
            "range_high": np.where(ok, st["range_high"][kk], np.nan)}


def find_setups(m15: pd.DataFrame, point: float, ctx: dict | None = None, L: int = 5,
                clip: bool = False, shift_window: int = 12, expire: int = 8) -> pd.DataFrame:
    """Detecte les setups M15 : sweep de liquidite puis cassure de structure (voir SMC_STRATEGY.md).
    Retourne toutes les occurrences avec les drapeaux HTF ; le filtrage se fait ensuite (ablation)."""
    s_df = clip_spikes(m15) if clip else m15
    o, h, l, c = (s_df[x].to_numpy() for x in ("open", "high", "low", "close"))
    spread = m15["spread"].to_numpy() * point
    times = m15["time"].to_numpy()
    n = len(c)
    st = structure(h, l, c, L)
    prev_sh, prev_sl = st["prev_sh"], st["prev_sl"]

    pend_l, pend_s = [], []
    last_lvl_l = last_lvl_s = np.nan
    rows = []

    def make(direction, s, t, ob, stop_ref):
        ob_mid = (h[ob] + l[ob]) / 2.0
        stop = stop_ref - spread[t] if direction == 1 else stop_ref + spread[t]
        # FVG dans le mouvement (info de test, pas utilise en version de base)
        fvg_mid = np.nan
        for j in range(max(s, 1), t):
            if direction == 1 and h[j - 1] < l[j + 1] and c[j] > o[j]:
                fvg_mid = (h[j - 1] + l[j + 1]) / 2.0
                break
            if direction == -1 and l[j - 1] > h[j + 1] and c[j] < o[j]:
                fvg_mid = (l[j - 1] + h[j + 1]) / 2.0
                break
        hd, rl, rh = 0, np.nan, np.nan
        if ctx is not None:
            hd, rl, rh = int(ctx["dir"][t]), ctx["range_low"][t], ctx["range_high"][t]
        pos = (c[t] - rl) / (rh - rl) if (rh > rl) else np.nan
        htf_ok = bool((direction == 1 and hd == 1 and pos < 0.5) or (direction == -1 and hd == -1 and pos > 0.5))
        rows.append({"signal_idx": t, "signal_time": pd.Timestamp(times[t]) + pd.Timedelta(minutes=M15_MIN),
                     "direction": direction, "sweep_idx": s, "ob_idx": ob, "entry": ob_mid, "stop": stop,
                     "fvg_mid": fvg_mid, "htf_dir": hd, "htf_pos": pos, "htf_ok": htf_ok,
                     "expire_idx": t + expire})

    for t in range(n):
        # 1. setups en attente
        for p in pend_l[:]:
            if c[t] > p["ref"]:
                s = p["s"]
                seg = l[s:t]
                ob = s + (len(seg) - 1 - int(np.argmin(seg[::-1])))     # plus bas, derniere occurrence
                make(1, s, t, ob, float(l[s:t + 1].min()))
                pend_l.remove(p)
            elif c[t] < p["ext"] or t - p["s"] >= shift_window:
                pend_l.remove(p)
            else:
                p["ext"] = min(p["ext"], l[t])
        for p in pend_s[:]:
            if c[t] < p["ref"]:
                s = p["s"]
                seg = h[s:t]
                ob = s + (len(seg) - 1 - int(np.argmax(seg[::-1])))     # plus haut, derniere occurrence
                make(-1, s, t, ob, float(h[s:t + 1].max()))
                pend_s.remove(p)
            elif c[t] > p["ext"] or t - p["s"] >= shift_window:
                pend_s.remove(p)
            else:
                p["ext"] = max(p["ext"], h[t])

        # 2. nouveaux sweeps (niveaux confirmes AVANT t)
        lv, hv = prev_sl[t], prev_sh[t]
        if not (np.isnan(lv) or np.isnan(hv)):
            if l[t] < lv and lv < c[t] < hv and lv != last_lvl_l:
                pend_l.append({"s": t, "ref": hv, "ext": l[t]})
                last_lvl_l = lv
            if h[t] > hv and lv < c[t] < hv and hv != last_lvl_s:
                pend_s.append({"s": t, "ref": lv, "ext": h[t]})
                last_lvl_s = hv

    cols = ["signal_idx", "signal_time", "direction", "sweep_idx", "ob_idx", "entry", "stop",
            "fvg_mid", "htf_dir", "htf_pos", "htf_ok", "expire_idx"]
    return pd.DataFrame(rows, columns=cols)


def atr(high: np.ndarray, low: np.ndarray, close: np.ndarray, n: int = 14) -> np.ndarray:
    """Wilder ATR. Causal: value at t uses candles <= t. NaN for the first n-1 candles."""
    prev_close = np.concatenate([[np.nan], close[:-1]])
    tr = np.nanmax(np.vstack([high - low, np.abs(high - prev_close), np.abs(low - prev_close)]), axis=0)
    out = pd.Series(tr).ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean().to_numpy()
    return out


def spike_flags(high: np.ndarray, low: np.ndarray, mult: float = 8.0, window: int = 200) -> np.ndarray:
    """True for candles whose range is above mult x the median range of the previous `window` candles."""
    rng = pd.Series(high - low)
    med = rng.shift(1).rolling(window, min_periods=20).median()
    return (rng > mult * med).fillna(False).to_numpy()
