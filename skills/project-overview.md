# SKILL : Project Overview — money_housse

## Description
Bot de scalping automatique sur indices synthétiques Deriv (Crash/Boom) via MetaTrader 5.
Stratégie EMA crossover M15 + M1. Compte Standard Deriv.

---

## Architecture des fichiers

```
money_housse/
├── main.py          # Boucle principale, orchestration
├── config.py        # Paramètres centraux (symboles, TP/SL, lots)
├── strategy.py      # Logique EMA — signaux M15 + M1
├── trader.py        # Ouverture / fermeture / surveillance des trades
├── notifier.py      # Notifications Telegram
├── reporter.py      # Rapports journalier / hebdo / mensuel
├── logs/
│   ├── trades.csv   # Historique trades (date, heure, symbol, direction, lot, entry, exit, profit)
│   └── orders.csv   # Log chaque ordre MT5 (open/close, retcode, statut)
├── tests/
│   ├── test_ordre_complet.py   # Test ouverture + fermeture + logs CSV
│   └── test_sl_detection.py    # Test détection SL fermé par MT5
└── skills/          # Ce dossier — documentation agents
```

---

## Flux d'exécution

```
main.py
  └── connect_mt5()
  └── boucle while True (toutes les 1s)
        ├── Pour chaque symbole dans SYMBOLS
        │     ├── has_open_position() → skip si trade actif
        │     ├── check_trend_m15()  → tendance M15 (EMA 5/13/50)
        │     ├── check_signal_m1()  → croisement M1
        │     ├── is_spike()         → filtre spike
        │     ├── open_trade()       → envoie ordre MT5 avec SL+TP serveur
        │     └── monitor_trade()    → surveille jusqu'à TP/SL
        ├── Heartbeat Telegram toutes les 30min
        └── Rapport 23h59 (journalier + hebdo + mensuel)
```

---

## Paramètres actuels (config.py)

```python
SYMBOLS = {
    "crash500": "Crash 500 Index",
    "boom600":  "Boom 600 Index",
    "boom900":  "Boom 900 Index",
    "boom300":  "Boom 300 Index",
    "crash300": "Crash 300 Index",
    "crash900": "Crash 900 Index",
}

# Direction par indice
# Crash → BUY (tendance haussière avec spikes baissiers)
# Boom  → SELL (tendance baissière avec spikes haussiers)

TP_CONFIG = {
    "Crash 500 Index": {"tp": 2724, "sl": 1362},
    "Boom 600 Index":  {"tp": 4464, "sl": 2232},
    "Boom 900 Index":  {"tp": 4082, "sl": 2041},
    "Boom 300 Index":  {"tp": 5140, "sl": 2570},
    "Crash 300 Index": {"tp": 6754, "sl": 3377},
    "Crash 900 Index": {"tp": 6058, "sl": 3029},
}

LOT   = 0.55
MAGIC = 123456
```

---

## Compte MT5

- **Broker** : Deriv
- **Type** : Standard (pas Swap-Free, pas Zero Spread)
- **Serveur** : Deriv-Demo (à changer en live)
- **Login** : dans `.env` (ne jamais hardcoder)

---

## Points clés à retenir

- SL et TP sont placés **côté serveur MT5** à l'ouverture du trade
- Le SL doit respecter `stops_level + spread` pour être accepté par Deriv
- `deviation = 50` pour éviter les refus sur indices volatils
- Profit lu depuis `history_deals_get(position=ticket)` après fermeture
- Si retcode `10029` → position déjà fermée par serveur (normal au TP)
- Les logs CSV séparent date et heure, incluent le lot
