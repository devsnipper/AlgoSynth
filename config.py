import MetaTrader5 as mt5

# ── Symboles ──────────────────────────────────────────────────────────────────
SYMBOLS = {
    "boom150":   "Boom 150 Index",
    "crash150":  "Crash 150 Index",
    "crash500":  "Crash 500 Index",
    "boom600":   "Boom 600 Index",
    "boom500":   "Boom 500 Index",
    "boom900":   "Boom 900 Index",
}

# ── Timeframes ────────────────────────────────────────────────────────────────
TF_TREND  = mt5.TIMEFRAME_M15   # filtre tendance
TF_SIGNAL = mt5.TIMEFRAME_M5    # signal d'entree

# ── EMAs ──────────────────────────────────────────────────────────────────────
EMA_FAST   = 5
EMA_MID    = 13
EMA_SLOW   = 50
CANDLES_NB = 100   # nb de candles a recuperer (on utilise les fermees : index 1+)

# ── Gestion des trades ────────────────────────────────────────────────────────
RISK_USD  = 0.30   # risque max par trade en USD — lot calcule dynamiquement

# TP/SL par indice — lot retire, calcule depuis RISK_USD a l'ouverture
TP_CONFIG = {
    "Boom 150 Index":   {"tp": 2000, "sl": 2294},
    "Crash 150 Index":  {"tp": 2000, "sl": 2368},
    "Crash 500 Index":  {"tp": 2000, "sl": 1361},
    "Boom 600 Index":   {"tp": 2000, "sl": 2232},
    "Boom 500 Index":   {"tp": 2000, "sl": 1844},
    "Boom 900 Index":   {"tp": 2000, "sl": 2041},
}
TP_POINTS    = 2000   # fallback
SL_POINTS    = 2000   # fallback
MAX_TRADES   = 999999  # pas de limite
MAGIC        = 123456  # identifiant unique du bot

# ── Spike filter ──────────────────────────────────────────────────────────────
SPIKE_THRESHOLD = 0.005   # 0.5%
