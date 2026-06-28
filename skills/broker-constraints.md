# SKILL : Contraintes Broker Deriv

## Compte Standard Deriv — Restrictions MT5

---

## SL / TP côté serveur

| Action | Résultat | Retcode |
|--------|----------|---------|
| SL dans requête d'ouverture | Accepté si distance >= stops_level + spread | 10009 |
| SL trop proche | Refusé | 10016 |
| TP dans requête d'ouverture | Accepté sur certains indices seulement | 10009 / 10016 |
| TRADE_ACTION_SLTP après ouverture | Refusé sur tous les synthétiques | 10016 |
| TRADE_ACTION_MODIFY | Refusé | None |
| Pending order comme SL synthétique | Refusé (10015) | 10015 |

## Retcodes MT5 importants

| Code | Signification | Action |
|------|--------------|--------|
| 10009 | TRADE_RETCODE_DONE — succès | OK |
| 10013 | Requête invalide (position déjà fermée) | Arrêter les tentatives |
| 10014 | Volume invalide | Utiliser lot_min de l'indice |
| 10015 | Pending order refusé | Non supporté sur ces indices |
| 10016 | Invalid stops — SL/TP non accepté | Augmenter distance ou abandon |
| 10027 | Algo trading désactivé | Activer dans MT5 → Outils → Options → Expert Advisors |
| 10029 | Position déjà fermée par serveur | Normal au TP — lire profit depuis history_deals |
| 10036 | Trop de requêtes | Ajouter sleep(2) entre tentatives |

---

## Formule SL valide

```python
info   = mt5.symbol_info(symbol)
tick   = mt5.symbol_info_tick(symbol)
pt     = info.point
stops  = info.trade_stops_level    # distance minimum broker
spread = round((tick.ask - tick.bid) / pt)
sl_pts = round((stops + spread) * 1.2)   # +20% marge sécurité
```

---

## Déviation

- Minimum recommandé : **50 points**
- En dessous → ordres refusés sur indices volatils (spikes)
- Ne jamais mettre à 0

---

## Lot minimum par indice

| Groupe | Lot min |
|--------|---------|
| Crash/Boom 50, 99, 100, 200, 1000 | 0.1 |
| Crash/Boom 150 | 0.5 |
| Crash/Boom 300, 500, 600, 900 | 0.2 |

---

## Filling mode

- Utiliser uniquement `ORDER_FILLING_FOK` sur indices Deriv
- `ORDER_FILLING_IOC` et `ORDER_FILLING_RETURN` sont refusés

---

## Spécificités indices synthétiques

- Spikes instantanés : le prix peut sauter 5000+ pts en 1 tick
- SL serveur protège contre le slippage sur spike
- Sans SL serveur → fermeture bot peut avoir slippage important
- Le TP serveur ferme instantanément sans latence bot
- `history_deals_get(position=ticket)` retourne les deals IN + OUT
  → Filtrer `d.entry == mt5.DEAL_ENTRY_OUT` pour le profit réel

---

## Horaires de trading

- Indices synthétiques : **24h/24, 7j/7**
- Meilleure activité EMA : **23h00 → 05h00** (réseau moins chargé)
- Congestion réseau en journée → timeout Telegram possible (60s configuré)
