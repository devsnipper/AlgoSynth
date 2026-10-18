# Live techniques replayed on history

Window: 2025-11-05 to 2026-10-11 (48 weeks), the bot's six symbols, M5 fills, rules of the plan.

## Signals and what happens to them

| Technique | Signals | Per week (6 symbols) | Rejected by risk rules | Capped out | Traded | Traded per week |
|---|---|---|---|---|---|---|
| SMC_C_PD_OB_FVG | 113 | 2.3 | 0 | 69 | 44 | 0.91 |
| SMC_A_OB_TREND | 65 | 1.3 | 0 | 42 | 23 | 0.47 |
| SMC_B_SWEEP_REV | 1578 | 32.6 | 252 | 752 | 574 | 11.85 |

All techniques together: 641 trades in 48 weeks = 13.24 per week.

Reasons signals did not trade:

- weekly_breaker: 433
- min_lot_risk_too_high: 252
- max_per_day: 234
- symbol_busy: 196

## Results of the trades the live rules would take (capped)

| Technique | Trades | Win % | Avg R | Total R | Profit factor | Worst R | Total $ |
|---|---|---|---|---|---|---|---|
| SMC_C_PD_OB_FVG | 44 | 36.4 | +0.196 | +8.6 | 1.28 | -1.5 | +60.1 |
| SMC_A_OB_TREND | 23 | 34.8 | -0.080 | -1.8 | 0.88 | -1.2 | -9.3 |
| SMC_B_SWEEP_REV | 574 | 34.0 | -0.023 | -12.9 | 0.97 | -2.2 | -48.3 |
| ALL | 641 | 34.2 | -0.010 | -6.2 | 0.99 | -2.2 | +2.4 |

## Results of every signal that passes the risk rules, each technique on its own (no caps; larger sample)

| Technique | Trades | Win % | Avg R | Total R | Profit factor | Worst R | Total $ |
|---|---|---|---|---|---|---|---|
| SMC_C_PD_OB_FVG | 113 | 31.9 | +0.002 | +0.3 | 1.00 | -1.5 | +11.0 |
| SMC_A_OB_TREND | 65 | 32.3 | -0.139 | -9.1 | 0.80 | -1.2 | -49.0 |
| SMC_B_SWEEP_REV | 1326 | 33.5 | -0.043 | -56.8 | 0.94 | -2.2 | -309.8 |
| ALL | 1504 | 33.3 | -0.044 | -65.6 | 0.94 | -2.2 | -347.8 |

## Exits (every signal that passes the risk rules)


- SMC_C_PD_OB_FVG: SL 67%, TP 18%, TIME 15%; average risk 5.99 $
- SMC_A_OB_TREND: SL 66%, TP 28%, TIME 6%; average risk 5.84 $
- SMC_B_SWEEP_REV: SL 62%, TIME 24%, TP 14%; average risk 7.42 $

Trades per week under the caps: mean 13.1, median 15, max 21 (weeks with at least one trade: 49 of 48).

By symbol (capped trades):

| symbol          |   trades |   avg_R |   total_R |
|:----------------|---------:|--------:|----------:|
| Boom 150 Index  |      120 |    0.03 |      3.67 |
| Boom 500 Index  |      110 |    0.04 |      3.89 |
| Boom 600 Index  |      106 |   -0.2  |    -20.81 |
| Boom 900 Index  |       85 |   -0.03 |     -2.54 |
| Crash 150 Index |      117 |    0.12 |     13.66 |
| Crash 500 Index |      103 |   -0.04 |     -4.03 |