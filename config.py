import MetaTrader5 as mt5

# ── Symboles ──────────────────────────────────────────────────────────────────
SYMBOLS = {
    "crash": "Crash 1000 Index.0",
    "boom":  "Boom 1000 Index.0",
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
LOT          = 0.20    # lot minimum Deriv
TP_POINTS    = 150     # take profit en points
SL_POINTS    = 100     # stop loss en points
MAX_TRADES   = 20      # max trades par jour (toutes paires confondues)
MAGIC        = 123456  # identifiant unique du bot

# ── Spike filter ──────────────────────────────────────────────────────────────
SPIKE_THRESHOLD = 0.005   # 0.5%
