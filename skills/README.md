# Skills — money_housse

Documentation pour agents IA travaillant sur ce projet.

## Index

| Skill | Fichier | Usage |
|-------|---------|-------|
| Vue d'ensemble du projet | [project-overview.md](project-overview.md) | Comprendre l'architecture, le flux, les paramètres actuels |
| Données indices synthétiques | [indices-data.md](indices-data.md) | Choisir les bons indices pour une nouvelle stratégie |
| Règles de stratégie EMA | [strategy-rules.md](strategy-rules.md) | Comprendre et modifier la stratégie de trading |
| Contraintes broker Deriv | [broker-constraints.md](broker-constraints.md) | Retcodes MT5, SL/TP serveur, déviation, filling |
| Analyse de performance | [performance-analysis.md](performance-analysis.md) | Lire les logs CSV, évaluer la rentabilité |
| Troubleshooting | [troubleshooting.md](troubleshooting.md) | Résoudre les erreurs fréquentes |

## Ordre de lecture recommandé

1. `project-overview.md` — toujours lire en premier
2. `broker-constraints.md` — avant toute modification de trader.py
3. `indices-data.md` — avant d'ajouter de nouveaux indices
4. `strategy-rules.md` — avant de modifier la stratégie
5. `troubleshooting.md` — en cas de bug
6. `performance-analysis.md` — pour évaluer les résultats
