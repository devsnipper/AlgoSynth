import MetaTrader5 as mt5

# ── Symboles ──────────────────────────────────────────────────────────────────
SYMBOLS = {
    "crash": "Crash 1000 Index",
    "boom":  "Boom 1000 Index",
}

# ── Timeframes ────────────────────────────────────────────────────────────────
TF_TREND  = mt5.TIMEFRAME_M15   # filtre tendance
TF_SIGNAL = mt5.TIMEFRAME_M1    # signal d'entree

# ── EMAs ──────────────────────────────────────────────────────────────────────
EMA_FAST   = 5
EMA_MID    = 13
EMA_SLOW   = 50
CANDLES_NB = 100   # nb de candles a recuperer (on utilise les fermees : index 1+)

# ── Gestion des trades ────────────────────────────────────────────────────────
LOT          = 0.55   # lot minimum Deriv
TP_POINTS    = 2000    # ~0.11 USD net par trade
SL_POINTS    = 10000  # SL au dela du spread
MAX_TRADES   = 999999  # pas de limite
MAGIC        = 123456  # identifiant unique du bot

# ── Spike filter ──────────────────────────────────────────────────────────────
SPIKE_THRESHOLD = 0.005   # 0.5%
