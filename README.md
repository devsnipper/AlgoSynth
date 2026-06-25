# Money Housse — Deriv Scalper Bot

Bot de scalping automatique pour les indices synthétiques **Crash 1000** et **Boom 1000** de Deriv, via MetaTrader 5.

## Fonctionnement

Le bot tourne en boucle et, pour chaque symbole configuré :

1. Vérifie qu'aucun trade n'est déjà ouvert sur ce symbole
2. Analyse la **tendance M15** (EMA 5 / 13 / 50) — BUY sur Crash, SELL sur Boom
3. Confirme le **signal M1** dans le sens de la tendance
4. Applique un **filtre anti-spike** (variation > 0.5 % ignorée)
5. Ouvre le trade avec TP et SL fixes en points
6. Surveille le trade jusqu'à la clôture (TP ou SL)

Un **heartbeat Telegram** est envoyé toutes les 30 minutes. Des **rapports** sont générés chaque soir à 23h59 (journalier), le dimanche (hebdomadaire) et le dernier jour du mois (mensuel).

## Structure

```
main.py       — boucle principale, connexion MT5
config.py     — paramètres (symboles, EMA, lot, TP/SL, limites)
strategy.py   — logique tendance M15 et signal M1
trader.py     — ouverture / surveillance des trades
notifier.py   — notifications Telegram
reporter.py   — rapports journalier / hebdo / mensuel
```

## Configuration

Créer un fichier `.env` à la racine :

```env
MT5_LOGIN=<votre_login>
MT5_PASSWORD=<votre_mot_de_passe>
MT5_SERVER=<serveur_deriv>
TELEGRAM_TOKEN=<token_bot_telegram>
TELEGRAM_CHAT_ID=<votre_chat_id>
```

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install MetaTrader5 python-dotenv requests
python main.py
```

## Paramètres clés (`config.py`)

| Paramètre        | Valeur par défaut | Description                        |
|------------------|-------------------|------------------------------------|
| `LOT`            | 0.20              | Taille de position                 |
| `TP_POINTS`      | 150               | Take Profit en points              |
| `SL_POINTS`      | 100               | Stop Loss en points                |
| `MAX_TRADES`     | 20                | Limite de trades par jour          |
| `SPIKE_THRESHOLD`| 0.5 %             | Seuil de rejet spike               |
| `EMA_FAST/MID/SLOW` | 5 / 13 / 50   | Périodes EMA pour la tendance      |
