# Sweep + displacement + fair value gap (s03_sweep_displacement_fvg): Stage 1

Primary test: net move after 12 M15 candles (3h), ATR units, spread included,
minus the average of comparable moments. Pass = z >= 3.4, at least 300 events in block A,
and a positive excess in block C. Block B is not touched at Stage 1.

## Verdict

| bias | group | n_A | excess_A | z_A | n_C | excess_C | z_C | verdict |
|---|---|---|---|---|---|---|---|---|
| none | all | 889 | -0.036 | -0.481 | 2535 | 0.027 | 0.560 | no edge |
| none | Step | 353 | 0.001 | 0.009 | 787 | 0.197 | 2.374 | no edge |
| none | Range Break | 71 | -0.339 | -0.912 | 267 | 0.172 | 0.760 | too few events |
| none | Multi Step | 196 | -0.001 | -0.006 | 449 | 0.024 | 0.228 | too few events |
| none | Volatility | 269 | -0.028 | -0.216 | 1032 | -0.138 | -1.980 | too few events |
| h1 | all | 328 | -0.132 | -1.022 | 905 | 0.171 | 2.016 | no edge |
| h1 | Step | 116 | 0.014 | 0.070 | 265 | 0.393 | 2.682 | too few events |
| h1 | Range Break | 38 | -0.512 | -0.952 | 112 | 0.764 | 2.091 | too few events |
| h1 | Multi Step | 74 | 0.096 | 0.366 | 163 | 0.009 | 0.056 | too few events |
| h1 | Volatility | 100 | -0.324 | -1.523 | 365 | -0.101 | -0.828 | too few events |

## All cells

| bias | block | group | symbols | n | excess_3h | z_3h | excess_1h | z_1h | raw_mean | base_mean | win_pct | mfe_med | mae_med |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | A | all | 14 | 889 | -0.036 | -0.481 | -0.032 | -0.737 | -0.066 | -0.030 | 48.031 | 1.447 | 1.436 |
| none | A | Step | 5 | 353 | 0.001 | 0.009 | 0.016 | 0.267 | -0.020 | -0.021 | 49.008 | 1.427 | 1.377 |
| none | A | Range Break | 2 | 71 | -0.339 | -0.912 | -0.294 | -1.408 | -0.356 | -0.017 | 38.028 | 1.646 | 1.373 |
| none | A | Multi Step | 3 | 196 | -0.001 | -0.006 | 0.030 | 0.359 | -0.041 | -0.040 | 50.510 | 1.523 | 1.419 |
| none | A | Volatility | 4 | 269 | -0.028 | -0.216 | -0.071 | -0.837 | -0.068 | -0.039 | 47.584 | 1.352 | 1.532 |
| none | C | all | 14 | 2535 | 0.027 | 0.560 | -0.028 | -1.009 | -0.003 | -0.030 | 50.375 | 1.390 | 1.440 |
| none | C | Step | 5 | 787 | 0.197 | 2.374 | 0.055 | 1.185 | 0.171 | -0.026 | 52.732 | 1.412 | 1.392 |
| none | C | Range Break | 2 | 267 | 0.172 | 0.760 | -0.060 | -0.448 | 0.156 | -0.016 | 47.940 | 1.184 | 1.278 |
| none | C | Multi Step | 3 | 449 | 0.024 | 0.228 | -0.091 | -1.544 | -0.010 | -0.034 | 51.670 | 1.348 | 1.499 |
| none | C | Volatility | 4 | 1032 | -0.138 | -1.980 | -0.055 | -1.408 | -0.174 | -0.036 | 48.643 | 1.397 | 1.470 |
| h1 | A | all | 14 | 328 | -0.132 | -1.022 | -0.034 | -0.468 | -0.164 | -0.032 | 41.768 | 1.242 | 1.565 |
| h1 | A | Step | 5 | 116 | 0.014 | 0.070 | 0.162 | 1.641 | -0.000 | -0.014 | 46.552 | 1.463 | 1.419 |
| h1 | A | Range Break | 2 | 38 | -0.512 | -0.952 | -0.602 | -1.983 | -0.547 | -0.035 | 34.211 | 1.046 | 1.413 |
| h1 | A | Multi Step | 3 | 74 | 0.096 | 0.366 | 0.122 | 0.899 | 0.060 | -0.036 | 44.595 | 1.244 | 1.343 |
| h1 | A | Volatility | 4 | 100 | -0.324 | -1.523 | -0.162 | -1.144 | -0.373 | -0.048 | 37.000 | 1.117 | 1.872 |
| h1 | C | all | 14 | 905 | 0.171 | 2.016 | 0.025 | 0.519 | 0.126 | -0.045 | 52.928 | 1.414 | 1.357 |
| h1 | C | Step | 5 | 265 | 0.393 | 2.682 | 0.105 | 1.405 | 0.366 | -0.027 | 56.604 | 1.446 | 1.325 |
| h1 | C | Range Break | 2 | 112 | 0.764 | 2.091 | 0.235 | 1.064 | 0.747 | -0.017 | 56.250 | 1.792 | 0.718 |
| h1 | C | Multi Step | 3 | 163 | 0.009 | 0.056 | -0.104 | -1.088 | -0.050 | -0.059 | 53.374 | 1.329 | 1.543 |
| h1 | C | Volatility | 4 | 365 | -0.101 | -0.828 | -0.040 | -0.569 | -0.161 | -0.060 | 49.041 | 1.347 | 1.466 |

excess = mean over events of (net move - baseline), in ATR. Baseline = average net move of all comparable moments (same symbol, direction, block and bias condition).
