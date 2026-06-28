# SKILL : Analyse de Performance

## Fichiers de logs

### trades.csv
```
date, heure, symbol, direction, lot, entry, exit, profit
```
- Une ligne par trade fermé
- `profit` = profit réel lu depuis `history_deals_get` (DEAL_ENTRY_OUT)

### orders.csv
```
date, heure, type, symbol, direction, prix, retcode, statut
```
- Une ligne par tentative d'ordre (OPEN ou CLOSE)
- `statut` = OK / REFUSE_1 / REFUSE_2... / OK_SERVEUR
- Permet de diagnostiquer les refus MT5

---

## Métriques clés à surveiller

### Rentabilité
```python
pnl_total    = sum(profit)
win_rate     = nb_trades_positifs / nb_trades_total
expected_val = (win_rate * avg_gain) - ((1 - win_rate) * avg_loss)
```

### Ratio minimum pour être rentable
```
Ratio TP:SL = 2:1 → win_rate minimum = 33%
Ratio TP:SL = 1.5:1 → win_rate minimum = 40%
Ratio TP:SL = 1:1 → win_rate minimum = 50%
```

### Signes d'alerte
- SL touché immédiatement → SL trop proche du spread
- Profit = 0 → position fermée par serveur mais deal pas encore dans historique (timing)
- Profit affiché ≠ MT5 → `pos.profit` stale, utiliser `history_deals_get`
- Beaucoup de REFUSE dans orders.csv → déviation trop faible ou retcode 10016

---

## Comment lire les rapports Telegram

### Rapport journalier (23h59)
```
📋 RAPPORT JOURNALIER
📅 27/06/2026
📊 Total trades : X

— Crash 500
  Trades  : 5  (4W / 1L)  80%
  ✅ Profit : +1.20 $
  📈 Pips   : +12.5

🏆 PnL total  : +2.50 $
📍 Pips total : +25.0
```

### Heartbeat (toutes les 30min)
- `💓 Bot actif` → bot tourne normalement
- Absence de heartbeat → bot planté, relancer

---

## Commandes utiles pour analyser les logs

```python
import pandas as pd

df = pd.read_csv('logs/trades.csv')

# Stats du jour
today = df[df['date'] == '2026-06-27']
print(f"PnL : {today['profit'].sum():.2f}")
print(f"Win rate : {(today['profit'] > 0).mean():.0%}")
print(f"Meilleur : {today['profit'].max():.2f}")
print(f"Pire : {today['profit'].min():.2f}")

# Par symbole
print(today.groupby('symbol')['profit'].sum())
```

---

## Performance de référence

| Compte | TP | SL | Ratio | Win rate observé |
|--------|----|----|-------|-----------------|
| Swap-Free (ancien) | 150 pts | 100 pts | 1.5:1 | ~95% |
| Standard (actuel) | 2x SL | SL min | 2:1 | à mesurer |

---

## Checklist quotidienne

- [ ] Balance MT5 correspond au PnL logs CSV
- [ ] Pas de position restée ouverte dans MT5
- [ ] orders.csv ne contient pas trop de REFUSE
- [ ] Heartbeat Telegram reçu dans les 30 dernières minutes
- [ ] Bot.py tourne (vérifier processus Python)
