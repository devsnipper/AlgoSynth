# Sweep + displacement + fair value gap (s03_sweep_displacement_fvg): Stage 1

Primary test: net move after 12 M15 candles (3h), ATR units, spread included,
minus the average of comparable moments. Pass = z >= 3.2, at least 300 events in block A,
and a positive excess in block C. Block B is not touched at Stage 1.

## Verdict

| bias | group | n_A | excess_A | z_A | n_C | excess_C | z_C | verdict |
|---|---|---|---|---|---|---|---|---|
| none | all | 2927 | 0.032 | 0.594 | 7900 | -0.017 | -0.529 | no edge |
| none | Boom | 1490 | -0.031 | -0.418 | 3942 | -0.010 | -0.214 | no edge |
| none | Crash | 1437 | 0.096 | 1.241 | 3958 | -0.025 | -0.532 | no edge |
| h1 | all | 942 | 0.040 | 0.427 | 2526 | -0.055 | -0.981 | no edge |
| h1 | Boom | 502 | 0.041 | 0.337 | 1263 | -0.059 | -0.754 | no edge |
| h1 | Crash | 440 | 0.038 | 0.268 | 1263 | -0.052 | -0.637 | no edge |

## All cells

| bias | block | group | symbols | n | excess_3h | z_3h | excess_1h | z_1h | raw_mean | base_mean | win_pct | mfe_med | mae_med |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | A | all | 10 | 2927 | 0.032 | 0.594 | 0.027 | 0.882 | -0.019 | -0.051 | 46.976 | 1.705 | 1.811 |
| none | A | Boom | 5 | 1490 | -0.031 | -0.418 | 0.010 | 0.221 | -0.095 | -0.065 | 45.436 | 1.665 | 1.828 |
| none | A | Crash | 5 | 1437 | 0.096 | 1.241 | 0.046 | 1.031 | 0.060 | -0.036 | 48.573 | 1.780 | 1.788 |
| none | C | all | 10 | 7900 | -0.017 | -0.529 | -0.008 | -0.397 | -0.020 | -0.002 | 47.038 | 1.588 | 1.919 |
| none | C | Boom | 5 | 3942 | -0.010 | -0.214 | -0.020 | -0.735 | 0.008 | 0.018 | 46.905 | 1.580 | 1.924 |
| none | C | Crash | 5 | 3958 | -0.025 | -0.532 | 0.005 | 0.183 | -0.047 | -0.023 | 47.170 | 1.592 | 1.915 |
| h1 | A | all | 10 | 942 | 0.040 | 0.427 | -0.035 | -0.662 | -0.034 | -0.074 | 45.435 | 1.629 | 1.807 |
| h1 | A | Boom | 5 | 502 | 0.041 | 0.337 | -0.057 | -0.825 | -0.064 | -0.105 | 45.418 | 1.676 | 1.808 |
| h1 | A | Crash | 5 | 440 | 0.038 | 0.268 | -0.009 | -0.114 | -0.000 | -0.038 | 45.455 | 1.582 | 1.807 |
| h1 | C | all | 10 | 2526 | -0.055 | -0.981 | -0.013 | -0.386 | -0.041 | 0.014 | 46.239 | 1.473 | 1.860 |
| h1 | C | Boom | 5 | 1263 | -0.059 | -0.754 | -0.042 | -0.897 | -0.020 | 0.039 | 47.110 | 1.464 | 1.854 |
| h1 | C | Crash | 5 | 1263 | -0.052 | -0.637 | 0.016 | 0.346 | -0.062 | -0.010 | 45.368 | 1.483 | 1.861 |

excess = mean over events of (net move - baseline), in ATR. Baseline = average net move of all comparable moments (same symbol, direction, block and bias condition).
