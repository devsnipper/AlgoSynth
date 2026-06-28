# SKILL : Donnees Indices Synthetiques Deriv

## Source
Donnees calculees empiriquement le 2026-06-28 sur compte Standard Deriv.
Methode : test reel via MT5 Python API — ouvertures test avec SL variable, 500 bougies M1 pour spike stats.

---

## Tableau complet — tous les indices

| Indice | Dir | Lot min | Spread | SL min | SL srv | Spike10 | SL/Spk | Score | Loss max | EV 70% |
|--------|-----|---------|--------|--------|--------|---------|--------|-------|---------|--------|
| **Crash 150** | buy | 0.5 | 973 | 2368 | OUI | 34136 | 7% | 5.0/10 | **-0.12 USD** | +3.45 USD |
| **Boom 150** | sell | 0.5 | 912 | 2294 | OUI | 29488 | 8% | 5.0/10 | **-0.11 USD** | +3.56 USD |
| **Crash 500** | buy | 0.2 | 208 | 1361 | OUI | 6700 | 20% | 7.0/10 | **-0.27 USD** | +19.83 USD |
| **Boom 500** | sell | 0.2 | 365 | 1844 | OUI | 11112 | 17% | 7.0/10 | **-0.37 USD** | +16.94 USD |
| **Boom 600** | sell | 0.2 | 330 | 2232 | OUI | 13271 | 17% | 5.5/10 | **-0.45 USD** | +14.60 USD |
| **Boom 900** | sell | 0.2 | 414 | 2041 | OUI | 17559 | 12% | 5.5/10 | **-0.41 USD** | +15.75 USD |
| Boom 300 | sell | 0.5 | 474 | 2569 | OUI | 7307 | 35% | 5.0/10 | -1.28 USD | +31.46 USD |
| Crash 900 | buy | 0.2 | 784 | 3029 | OUI | 29673 | 10% | 4.5/10 | -0.61 USD | +9.81 USD |
| Crash 300 | buy | 0.5 | 609 | 3377 | OUI | 12951 | 26% | 3.5/10 | -1.69 USD | +19.30 USD |
| Crash 600 | buy | 0.2 | 1477 | 4645 | OUI | 51649 | 9% | 2.5/10 | -0.93 USD | +0.17 USD |
| Crash 100 | buy | 0.1 | 6089 | 34890 | OUI | 27721 | 126% | 3.0/10 | -3.49 USD | -90.67 USD |
| Crash 99 | buy | 0.1 | 5798 | 33934 | OUI | 32443 | 105% | 2.0/10 | -3.39 USD | -87.80 USD |
| Crash 200 | buy | 0.1 | 6205 | 35528 | OUI | 41410 | 86% | 1.0/10 | -3.55 USD | -92.58 USD |
| Boom 200 | sell | 0.1 | 6114 | 34934 | OUI | 43543 | 80% | 1.0/10 | -3.49 USD | -90.80 USD |
| Boom 100 | sell | 0.1 | 5967 | 34102 | OUI | 26287 | 130% | 3.0/10 | -3.41 USD | -88.31 USD |
| Boom 99 | sell | 0.1 | 5985 | 34208 | OUI | 26869 | 127% | 3.0/10 | -3.42 USD | -88.62 USD |
| Crash 1000 | buy | 0.2 | 4249 | 14219 | OUI | 120659 | 12% | 0.0/10 | -0.28 USD | -5.74 USD |
| Crash 50 | buy | 0.1 | 7008 | 33803 | OUI | 199549 | 17% | 0.0/10 | -0.34 USD | -8.74 USD |
| Boom 50 | sell | 0.1 | 7430 | 34547 | OUI | 228044 | 15% | 0.0/10 | -0.35 USD | -8.96 USD |
| Boom 1000 | sell | 0.2 | 9865 | 43230 | OUI | 255583 | 17% | 0.0/10 | -0.86 USD | -23.13 USD |

**EV 70% = profit sur 100 trades avec 70% de win rate, TP=2000 pts bot-side**
**Spike10 = moyenne des 10 pires bougies M1 sur 500 — approximation du spike habituel**
**SL/Spk = % du spike moyen couvert par le SL — plus c'est haut, plus on est protege**

---

## Scoring /10 — methode

| Critere | Poids | Logique |
|---------|-------|---------|
| RR (gain/loss) | 4 pts | RR >= 1.0 = 4pts, >= 0.6 = 3pts, >= 0.4 = 2pts |
| Protection spike | 3 pts | SL/Spike >= 120% = 3pts, >= 90% = 2pts, >= 60% = 1pt |
| Win rate seuil | 2 pts | WR min < 50% = 2pts, < 55% = 1.5pts, < 65% = 1pt |
| Spread vs gain | 1 pt | Spread < 30% du gain = 1pt |

---

## Classement par Loss max (SL serveur = priorite)

Le TP est gere par le bot — on peut l'ajuster librement.
Ce qui est fixe et impose par Deriv : le SL minimum. La loss max est donc la metrique cle.

| Priorite | Indice | Loss max | RR actuel | WR min | Commentaire |
|----------|--------|---------|-----------|--------|-------------|
| 1 | **Boom 150** | **-0.11 USD** | 0.87 | 53% | Perte la plus faible — ideal pour debuter |
| 2 | **Crash 150** | **-0.12 USD** | 0.84 | 54% | Quasi identique a Boom 150 |
| 3 | **Crash 500** | **-0.27 USD** | 1.47 | 41% | Meilleur RR du classement |
| 4 | **Crash 1000** | **-0.28 USD** | 0.14 | 88% | Loss ok mais RR tres mauvais |
| 5 | **Boom 500** | **-0.37 USD** | 1.08 | 48% | Bon RR + loss maitrisee |
| 6 | **Boom 900** | **-0.41 USD** | 0.98 | 51% | Proche 1:1 |
| 7 | **Boom 600** | **-0.45 USD** | 0.90 | 53% | Proche 1:1 |

---

## Regle SL serveur — STRICTE

- SL toujours passe dans open_trade — jamais bot-side uniquement
- TP bot-side uniquement — le serveur refuse le TP sur ces indices
- Si SL refuse (retcode 10016) → trade annule, aucune ouverture sans protection

## Formule SL minimum valide

```python
stops  = mt5.symbol_info(symbol).trade_stops_level
spread = round((tick.ask - tick.bid) / pt)
sl_min = round((stops + spread) * 1.2)   # +20% marge securite
```

## Notes pour nouvelles strategies

- TP libre = on peut viser RR 2:1, 3:1 sans contrainte serveur
- Crash/Boom 150 : perte max -0.12 USD → ideal pour tester une nouvelle strategie sans risque
- Crash 500 : meilleur RR naturel (1.47) avec SL serré — le plus efficace si win rate > 41%
- Indices swing (50, 99, 100, 200) : SL serveur OUI, TP libre → trailing stop possible mais EV negatif
- Lot min 0.5 obligatoire sur Crash/Boom 150
- stops_level varie dans le temps → recalculer dynamiquement a chaque ouverture
