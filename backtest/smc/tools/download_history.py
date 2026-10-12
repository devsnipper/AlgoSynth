"""Step 1 : telecharge le maximum d'historique M15 et M5 pour les indices Boom/Crash,
construit H1 et H4 a partir de M15, et verifie l'alignement contre H1/H4 de MT5.

Usage : backtest/.venv/Scripts/python.exe backtest/smc/tools/download_history.py
"""
import json
import os
import sys

import MetaTrader5 as mt5
import pandas as pd
from dotenv import load_dotenv

HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, "..", "..", "..")     # repo root (.env lives there, read only)
load_dotenv(os.path.join(ROOT, ".env"))

DATA_DIR = os.path.join(HERE, "..", "data")
SYMBOLS = [f"{kind} {n} Index" for kind in ("Boom", "Crash") for n in (300, 500, 600, 900, 1000)]
MAX_BARS = 99999           # le terminal refuse exactement 100000 (maxbars)
OHLC = {"open": "first", "high": "max", "low": "min", "close": "last",
        "tick_volume": "sum", "spread": "max", "real_volume": "sum"}


def fname(symbol: str, tf: str) -> str:
    return os.path.join(DATA_DIR, f"{symbol.replace(' ', '_')}_{tf}.csv")


def fetch(symbol: str, tf: int) -> pd.DataFrame:
    rates = mt5.copy_rates_from_pos(symbol, tf, 0, MAX_BARS)
    if rates is None or len(rates) == 0:
        return pd.DataFrame()
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    return df.drop_duplicates("time").sort_values("time").reset_index(drop=True)


def resample(m15: pd.DataFrame, rule: str) -> pd.DataFrame:
    """H1/H4 depuis M15. La bougie est datee a son ouverture, comme dans MT5."""
    r = m15.set_index("time").resample(rule, origin="epoch", label="left", closed="left").agg(OHLC)
    r = r.dropna(subset=["open"]).reset_index()
    return r


def main():
    if not mt5.initialize(login=int(os.getenv("MT5_LOGIN")), password=os.getenv("MT5_PASSWORD"),
                          server=os.getenv("MT5_SERVER")):
        print(f"initialize() echoue : {mt5.last_error()}")
        sys.exit(1)
    os.makedirs(DATA_DIR, exist_ok=True)

    info, rows = {}, []
    for s in SYMBOLS:
        if not mt5.symbol_select(s, True) or mt5.symbol_info(s) is None:
            print(f"{s}: symbole indisponible")
            continue
        i = mt5.symbol_info(s)
        info[s] = {"point": i.point, "digits": i.digits, "contract_size": i.trade_contract_size,
                   "volume_min": i.volume_min, "volume_step": i.volume_step,
                   "stops_level": i.trade_stops_level}

        m15, m5 = fetch(s, mt5.TIMEFRAME_M15), fetch(s, mt5.TIMEFRAME_M5)
        if m15.empty or m5.empty:
            print(f"{s}: pas de donnees")
            continue
        h1, h4 = resample(m15, "1h"), resample(m15, "4h")
        for tf, df in (("M15", m15), ("M5", m5), ("H1", h1), ("H4", h4)):
            df.to_csv(fname(s, tf), index=False)

        # Verification : H1/H4 construits vs H1/H4 de MT5 (sur la zone commune)
        chk = {}
        for tf, built, code in (("H1", h1, mt5.TIMEFRAME_H1), ("H4", h4, mt5.TIMEFRAME_H4)):
            ref = fetch(s, code)
            m = built.merge(ref, on="time", suffixes=("", "_mt5"))
            m = m[m.time >= built.time.iloc[0] + pd.Timedelta(days=1)]   # ignore la 1ere bougie partielle
            m = m[m.time < built.time.iloc[-1]]                          # et la derniere (incomplete)
            ok = ((m.open - m.open_mt5).abs() + (m.high - m.high_mt5).abs()
                  + (m.low - m.low_mt5).abs() + (m.close - m.close_mt5).abs()) < 1e-9
            chk[tf] = f"{ok.mean():.1%} of {len(m)}"

        rows.append({"symbol": s,
                     "M15_bars": len(m15), "M15_from": m15.time.iloc[0].date(), "M15_to": m15.time.iloc[-1].date(),
                     "months": round((m15.time.iloc[-1] - m15.time.iloc[0]).days / 30.4, 1),
                     "M5_bars": len(m5), "M5_from": m5.time.iloc[0].date(),
                     "H1_match": chk["H1"], "H4_match": chk["H4"],
                     "spread_med_pts": int(m15.spread.median())})
        print(f"{s}: done")

    with open(os.path.join(DATA_DIR, "symbol_info.json"), "w") as f:
        json.dump(info, f, indent=2)
    mt5.shutdown()

    pd.set_option("display.width", 220)
    print("\n" + pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
