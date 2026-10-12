# Equal highs/lows sweep (s01_equal_hl_sweep): Stage 1

Primary test: net move after 12 M15 candles (3h), ATR units, spread included,
minus the average of comparable moments. Pass = z >= 3.4, at least 300 events in block A,
and a positive excess in block C. Block B is not touched at Stage 1.

## Verdict

| bias | group | n_A | excess_A | z_A | n_C | excess_C | z_C | verdict |
|---|---|---|---|---|---|---|---|---|
| none | all | 1206 | -0.054 | -0.704 | 3366 | -0.017 | -0.355 | no edge |
| none | Step | 496 | -0.050 | -0.500 | 1216 | -0.069 | -1.080 | no edge |
| none | Range Break | 225 | -0.381 | -1.432 | 756 | -0.016 | -0.111 | too few events |
| none | Multi Step | 248 | 0.077 | 0.509 | 537 | 0.170 | 1.798 | too few events |
| none | Volatility | 237 | 0.110 | 0.773 | 857 | -0.060 | -0.784 | too few events |
| h1 | all | 596 | -0.079 | -0.683 | 1539 | -0.024 | -0.333 | no edge |
| h1 | Step | 239 | -0.099 | -0.675 | 557 | -0.105 | -1.099 | too few events |
| h1 | Range Break | 128 | -0.356 | -0.945 | 379 | 0.079 | 0.381 | too few events |
| h1 | Multi Step | 120 | 0.005 | 0.023 | 233 | -0.024 | -0.168 | too few events |
| h1 | Volatility | 109 | 0.199 | 0.940 | 370 | -0.006 | -0.055 | too few events |

## All cells

| bias | block | group | symbols | n | excess_3h | z_3h | excess_1h | z_1h | raw_mean | base_mean | win_pct | mfe_med | mae_med |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | A | all | 14 | 1206 | -0.054 | -0.704 | -0.060 | -1.399 | -0.081 | -0.027 | 48.259 | 1.346 | 1.477 |
| none | A | Step | 5 | 496 | -0.050 | -0.500 | -0.140 | -2.434 | -0.074 | -0.025 | 47.782 | 1.318 | 1.559 |
| none | A | Range Break | 2 | 225 | -0.381 | -1.432 | -0.203 | -1.364 | -0.396 | -0.015 | 46.667 | 0.799 | 1.408 |
| none | A | Multi Step | 3 | 248 | 0.077 | 0.509 | 0.132 | 1.647 | 0.045 | -0.032 | 48.387 | 1.522 | 1.335 |
| none | A | Volatility | 4 | 237 | 0.110 | 0.773 | 0.040 | 0.496 | 0.074 | -0.036 | 50.633 | 1.414 | 1.381 |
| none | C | all | 14 | 3366 | -0.017 | -0.355 | -0.018 | -0.655 | -0.045 | -0.028 | 49.228 | 1.374 | 1.462 |
| none | C | Step | 5 | 1216 | -0.069 | -1.080 | -0.060 | -1.653 | -0.095 | -0.026 | 46.711 | 1.416 | 1.539 |
| none | C | Range Break | 2 | 756 | -0.016 | -0.111 | 0.042 | 0.512 | -0.033 | -0.017 | 49.074 | 1.064 | 1.128 |
| none | C | Multi Step | 3 | 537 | 0.170 | 1.798 | 0.028 | 0.507 | 0.136 | -0.034 | 53.259 | 1.523 | 1.395 |
| none | C | Volatility | 4 | 857 | -0.060 | -0.784 | -0.039 | -0.851 | -0.097 | -0.037 | 50.408 | 1.387 | 1.563 |
| h1 | A | all | 14 | 596 | -0.079 | -0.683 | -0.097 | -1.487 | -0.110 | -0.032 | 48.154 | 1.326 | 1.492 |
| h1 | A | Step | 5 | 239 | -0.099 | -0.675 | -0.214 | -2.411 | -0.119 | -0.020 | 46.862 | 1.265 | 1.712 |
| h1 | A | Range Break | 2 | 128 | -0.356 | -0.945 | -0.184 | -0.874 | -0.379 | -0.023 | 46.094 | 0.959 | 1.316 |
| h1 | A | Multi Step | 3 | 120 | 0.005 | 0.023 | -0.017 | -0.153 | -0.047 | -0.052 | 47.500 | 1.451 | 1.439 |
| h1 | A | Volatility | 4 | 109 | 0.199 | 0.940 | 0.173 | 1.483 | 0.155 | -0.045 | 54.128 | 1.489 | 1.258 |
| h1 | C | all | 14 | 1539 | -0.024 | -0.333 | -0.029 | -0.706 | -0.064 | -0.041 | 48.993 | 1.340 | 1.443 |
| h1 | C | Step | 5 | 557 | -0.105 | -1.099 | -0.093 | -1.678 | -0.137 | -0.032 | 45.961 | 1.354 | 1.585 |
| h1 | C | Range Break | 2 | 379 | 0.079 | 0.381 | 0.124 | 1.075 | 0.059 | -0.020 | 50.396 | 1.052 | 1.102 |
| h1 | C | Multi Step | 3 | 233 | -0.024 | -0.168 | -0.040 | -0.492 | -0.089 | -0.065 | 49.356 | 1.426 | 1.330 |
| h1 | C | Volatility | 4 | 370 | -0.006 | -0.055 | -0.081 | -1.162 | -0.066 | -0.060 | 51.892 | 1.393 | 1.565 |

excess = mean over events of (net move - baseline), in ATR. Baseline = average net move of all comparable moments (same symbol, direction, block and bias condition).
