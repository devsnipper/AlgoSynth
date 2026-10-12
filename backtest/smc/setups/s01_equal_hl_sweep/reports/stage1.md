# Equal highs/lows sweep (s01_equal_hl_sweep): Stage 1

Primary test: net move after 12 M15 candles (3h), ATR units, spread included,
minus the average of comparable moments. Pass = z >= 3.2, at least 300 events in block A,
and a positive excess in block C. Block B is not touched at Stage 1.

## Verdict

| bias | group | n_A | excess_A | z_A | n_C | excess_C | z_C | verdict |
|---|---|---|---|---|---|---|---|---|
| none | all | 324 | 0.089 | 0.530 | 964 | -0.122 | -1.325 | no edge |
| none | Boom | 154 | 0.158 | 0.661 | 480 | -0.060 | -0.455 | too few events |
| none | Crash | 170 | 0.027 | 0.114 | 484 | -0.184 | -1.417 | too few events |
| h1 | all | 150 | -0.069 | -0.293 | 417 | -0.184 | -1.384 | too few events |
| h1 | Boom | 64 | -0.225 | -0.724 | 203 | -0.223 | -1.166 | too few events |
| h1 | Crash | 86 | 0.047 | 0.137 | 214 | -0.147 | -0.793 | too few events |

## All cells

| bias | block | group | symbols | n | excess_3h | z_3h | excess_1h | z_1h | raw_mean | base_mean | win_pct | mfe_med | mae_med |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | A | all | 10 | 324 | 0.089 | 0.530 | -0.027 | -0.282 | 0.085 | -0.004 | 47.531 | 1.706 | 1.859 |
| none | A | Boom | 5 | 154 | 0.158 | 0.661 | -0.086 | -0.657 | 0.153 | -0.005 | 45.455 | 1.730 | 1.866 |
| none | A | Crash | 5 | 170 | 0.027 | 0.114 | 0.027 | 0.205 | 0.023 | -0.004 | 49.412 | 1.691 | 1.723 |
| none | C | all | 10 | 964 | -0.122 | -1.325 | 0.012 | 0.223 | -0.130 | -0.008 | 49.585 | 1.654 | 1.804 |
| none | C | Boom | 5 | 480 | -0.060 | -0.455 | 0.048 | 0.648 | -0.072 | -0.013 | 51.667 | 1.682 | 1.702 |
| none | C | Crash | 5 | 484 | -0.184 | -1.417 | -0.024 | -0.322 | -0.188 | -0.004 | 47.521 | 1.624 | 1.876 |
| h1 | A | all | 10 | 150 | -0.069 | -0.293 | -0.129 | -0.925 | -0.093 | -0.024 | 48.667 | 1.527 | 1.881 |
| h1 | A | Boom | 5 | 64 | -0.225 | -0.724 | -0.157 | -0.781 | -0.274 | -0.049 | 40.625 | 1.514 | 1.853 |
| h1 | A | Crash | 5 | 86 | 0.047 | 0.137 | -0.109 | -0.562 | 0.041 | -0.005 | 54.651 | 1.592 | 2.088 |
| h1 | C | all | 10 | 417 | -0.184 | -1.384 | 0.034 | 0.450 | -0.180 | 0.004 | 47.962 | 1.657 | 1.807 |
| h1 | C | Boom | 5 | 203 | -0.223 | -1.166 | -0.074 | -0.628 | -0.210 | 0.014 | 49.754 | 1.572 | 1.759 |
| h1 | C | Crash | 5 | 214 | -0.147 | -0.793 | 0.137 | 1.391 | -0.152 | -0.005 | 46.262 | 1.771 | 1.841 |

excess = mean over events of (net move - baseline), in ATR. Baseline = average net move of all comparable moments (same symbol, direction, block and bias condition).
