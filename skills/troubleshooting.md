# SKILL : Troubleshooting — Erreurs fréquentes

## Erreurs MT5

### Retcode 10016 — Invalid Stops
**Symptôme** : Ouverture refusée avec SL/TP  
**Cause** : SL/TP trop proche du prix (< stops_level + spread)  
**Fix** :
```python
stops  = mt5.symbol_info(symbol).trade_stops_level
spread = round((tick.ask - tick.bid) / pt)
sl_pts = round((stops + spread) * 1.2)
```

### Retcode 10027 — Algo trading désactivé
**Symptôme** : Tous les ordres refusés  
**Cause** : MT5 a le trading automatique désactivé  
**Fix** : MT5 → Outils → Options → Expert Advisors → cocher "Autoriser le trading automatique"

### Retcode 10029 — Position déjà fermée
**Symptôme** : Fermeture refusée  
**Cause** : MT5 a fermé la position au TP serveur avant notre ordre  
**Fix** : C'est normal. Retourner `None` et lire le profit depuis `history_deals_get`

### Retcode 10036 — Trop de requêtes
**Symptôme** : Ordres refusés par rafale  
**Cause** : Bot envoie plusieurs ordres de fermeture trop rapidement  
**Fix** : `time.sleep(2)` après chaque tentative échouée

### Retcode 10014 — Volume invalide
**Symptôme** : Ouverture refusée  
**Cause** : Lot 0.2 sur indice qui requiert 0.5 minimum  
**Fix** : Utiliser `mt5.symbol_info(symbol).volume_min`

---

## Erreurs Python

### ModuleNotFoundError
```bash
.venv\Scripts\pip install MetaTrader5 pandas python-dotenv requests
```

### UnicodeEncodeError sur emoji
**Cause** : Windows cmd ne supporte pas les emojis  
**Fix** : Remplacer ✅ par [OK], ❌ par [X] dans les prints

### PermissionError sur trades.csv
**Cause** : Fichier ouvert dans Excel  
**Fix** : Fermer Excel avant de relancer le bot

---

## Erreurs de stratégie

### Bot ne déclenche pas de trades
**Vérifier** :
1. Tendance M15 alignée ? `check_trend_m15(symbol)` → doit retourner la bonne direction
2. Croisement M1 récent ? Les croisements sont rares (quelques fois par heure)
3. Spike détecté ? `is_spike()` bloque temporairement
4. Position déjà ouverte sur ce symbole ? `has_open_position()`

### Profit affiché ≠ profit MT5
**Cause** : `pos.profit` est stale (snapshot au moment de l'envoi d'ordre)  
**Fix** : Lire depuis `history_deals_get(position=ticket)` — filtrer `DEAL_ENTRY_OUT`

### SL touché immédiatement
**Cause** : SL_POINTS < stops_level + spread  
**Fix** : Recalculer SL avec la formule `(stops + spread) * 1.2`

### Timeout Telegram
**Cause** : Congestion réseau (surtout en journée)  
**Fix** : Timeout à 60s dans notifier.py — le bot continue même si Telegram échoue

---

## Commandes de diagnostic

```python
# Vérifier connexion MT5
mt5.initialize()
mt5.login(...)
print(mt5.account_info())

# Vérifier symbole disponible
info = mt5.symbol_info("Crash 500 Index")
print(info.trade_stops_level, info.volume_min)

# Vérifier positions ouvertes
print(mt5.positions_get())

# Vérifier historique deals
deals = mt5.history_deals_get(position=TICKET)
for d in deals:
    print(d.entry, d.profit, d.price)
```

---

## Relancer le bot

```bash
cd c:\Users\eyram\pproject\money_housse
.venv\Scripts\python.exe main.py
```

Le bot reprend automatiquement le compteur et le PnL du jour depuis `trades.csv`.
