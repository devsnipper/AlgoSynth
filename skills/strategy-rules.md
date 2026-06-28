# SKILL : Règles de Stratégie EMA

## Stratégie actuelle : EMA Crossover M15 + M1

### Principe
Double confirmation : tendance M15 + signal M1 dans le même sens.

---

## Conditions d'entrée

### 1. Filtre tendance M15 (check_trend_m15)
```
EMA_FAST (5) > EMA_MID (13) > EMA_SLOW (50) → tendance BUY
EMA_FAST (5) < EMA_MID (13) < EMA_SLOW (50) → tendance SELL
Sinon → pas de trade
```

### 2. Signal M1 (check_signal_m1)
```
BUY  : EMA5 croise EMA13 vers le haut (prev EMA5 <= EMA13, now EMA5 > EMA13)
       ET prix > EMA50
SELL : EMA5 croise EMA13 vers le bas (prev EMA5 >= EMA13, now EMA5 < EMA13)
       ET prix < EMA50
```

### 3. Filtre spike (is_spike)
```
Variation du dernier tick > 0.5% → trade ignoré
```

### 4. Pas de position ouverte sur ce symbole

---

## Direction par type d'indice

| Indice | Direction | Raison |
|--------|-----------|--------|
| Crash XXX | BUY | Tendance haussière avec spikes baissiers ponctuels |
| Boom XXX | SELL | Tendance baissière avec spikes haussiers ponctuels |

---

## Paramètres EMA

```python
EMA_FAST   = 5
EMA_MID    = 13
EMA_SLOW   = 50
CANDLES_NB = 100   # candles fermées (index 1+ pour éviter faux signaux)
TF_TREND   = M15
TF_SIGNAL  = M1
```

---

## Gestion des trades

- **SL et TP placés côté serveur MT5** à l'ouverture
- **Ratio TP:SL = 2:1** sur tous les indices retenus
- **monitor_trade** surveille le prix en boucle (1s) comme backup
- Si position fermée par serveur → profit lu via `history_deals_get`

---

## Pistes pour nouvelles stratégies

### Stratégies compatibles avec les indices disponibles

| Stratégie | Indices conseillés | Notes |
|-----------|-------------------|-------|
| EMA scalp (actuelle) | Crash 500, Boom 600, Boom 900, Boom 300, Crash 300, Crash 900 | SL+TP serveur, ratio 2:1 |
| Swing EMA | Crash/Boom 50, 99, 100, 200, 1000 | TP libre, grands mouvements |
| Breakout | Tous indices spread < 500 pts | Adapter SL au stops_level |
| Mean reversion | Crash/Boom 150 (spread faible) | Mais TP min très contraignant |

### Pour implémenter une nouvelle stratégie
1. Consulter `indices-data.md` pour choisir les indices
2. Vérifier SL serveur accepté (colonne "SL srv")
3. Calculer SL = (stops_level + spread) × 1.2
4. Définir TP = SL × ratio désiré (min 2.0 recommandé)
5. Vérifier TP >= tp_min de l'indice
6. Ajouter dans `config.py` → SYMBOLS + TP_CONFIG + direction_map dans main.py
