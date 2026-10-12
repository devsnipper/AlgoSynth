# Sweep + structure shift + OB (reference) (s10_sweep_shift_ob_reference): Stage 1

Primary test: net move after 12 M15 candles (3h), ATR units, spread included,
minus the average of comparable moments. Pass = z >= 3.4, at least 300 events in block A,
and a positive excess in block C. Block B is not touched at Stage 1.

## Verdict

| bias | group | n_A | excess_A | z_A | n_C | excess_C | z_C | verdict |
|---|---|---|---|---|---|---|---|---|
| none | all | 2226 | -0.000 | -0.009 | 6165 | -0.027 | -0.886 | no edge |
| none | Step | 874 | -0.046 | -0.620 | 2101 | -0.023 | -0.472 | no edge |
| none | Range Break | 169 | 0.044 | 0.136 | 619 | -0.108 | -0.712 | too few events |
| none | Multi Step | 502 | -0.086 | -0.878 | 1134 | -0.060 | -0.933 | no edge |
| none | Volatility | 681 | 0.110 | 1.319 | 2311 | 0.006 | 0.124 | no edge |
| h1 | all | 1205 | -0.055 | -0.750 | 3335 | 0.004 | 0.095 | no edge |
| h1 | Step | 470 | -0.058 | -0.571 | 1167 | -0.031 | -0.485 | no edge |
| h1 | Range Break | 95 | -0.740 | -1.488 | 326 | 0.038 | 0.179 | too few events |
| h1 | Multi Step | 278 | -0.065 | -0.488 | 604 | -0.064 | -0.715 | too few events |
| h1 | Volatility | 362 | 0.138 | 1.184 | 1238 | 0.061 | 0.964 | no edge |

## All cells

| bias | block | group | symbols | n | excess_3h | z_3h | excess_1h | z_1h | raw_mean | base_mean | win_pct | mfe_med | mae_med |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | A | all | 14 | 2226 | -0.000 | -0.009 | -0.069 | -2.344 | -0.031 | -0.030 | 50.404 | 1.427 | 1.482 |
| none | A | Step | 5 | 874 | -0.046 | -0.620 | -0.038 | -0.880 | -0.071 | -0.025 | 49.085 | 1.457 | 1.467 |
| none | A | Range Break | 2 | 169 | 0.044 | 0.136 | -0.043 | -0.246 | 0.042 | -0.002 | 49.704 | 1.033 | 0.926 |
| none | A | Multi Step | 3 | 502 | -0.086 | -0.878 | -0.129 | -2.206 | -0.122 | -0.036 | 49.801 | 1.409 | 1.597 |
| none | A | Volatility | 4 | 681 | 0.110 | 1.319 | -0.069 | -1.453 | 0.071 | -0.039 | 52.717 | 1.505 | 1.459 |
| none | C | all | 14 | 6165 | -0.027 | -0.886 | -0.020 | -1.153 | -0.058 | -0.030 | 48.516 | 1.396 | 1.492 |
| none | C | Step | 5 | 2101 | -0.023 | -0.472 | -0.007 | -0.236 | -0.048 | -0.025 | 48.310 | 1.405 | 1.498 |
| none | C | Range Break | 2 | 619 | -0.108 | -0.712 | -0.029 | -0.336 | -0.126 | -0.018 | 43.134 | 0.834 | 1.202 |
| none | C | Multi Step | 3 | 1134 | -0.060 | -0.933 | -0.046 | -1.206 | -0.095 | -0.035 | 47.795 | 1.416 | 1.539 |
| none | C | Volatility | 4 | 2311 | 0.006 | 0.124 | -0.019 | -0.682 | -0.030 | -0.036 | 50.498 | 1.462 | 1.505 |
| h1 | A | all | 14 | 1205 | -0.055 | -0.750 | -0.086 | -2.096 | -0.087 | -0.033 | 48.797 | 1.352 | 1.511 |
| h1 | A | Step | 5 | 470 | -0.058 | -0.571 | 0.000 | 0.003 | -0.078 | -0.020 | 48.723 | 1.443 | 1.419 |
| h1 | A | Range Break | 2 | 95 | -0.740 | -1.488 | -0.290 | -1.149 | -0.748 | -0.008 | 38.947 | 0.345 | 1.327 |
| h1 | A | Multi Step | 3 | 278 | -0.065 | -0.488 | -0.143 | -1.735 | -0.107 | -0.042 | 48.201 | 1.354 | 1.638 |
| h1 | A | Volatility | 4 | 362 | 0.138 | 1.184 | -0.100 | -1.563 | 0.089 | -0.049 | 51.934 | 1.511 | 1.531 |
| h1 | C | all | 14 | 3335 | 0.004 | 0.095 | -0.006 | -0.264 | -0.042 | -0.046 | 48.546 | 1.405 | 1.502 |
| h1 | C | Step | 5 | 1167 | -0.031 | -0.485 | 0.003 | 0.077 | -0.063 | -0.033 | 47.301 | 1.400 | 1.540 |
| h1 | C | Range Break | 2 | 326 | 0.038 | 0.179 | -0.060 | -0.494 | 0.019 | -0.018 | 45.399 | 0.704 | 1.207 |
| h1 | C | Multi Step | 3 | 604 | -0.064 | -0.715 | -0.045 | -0.856 | -0.126 | -0.063 | 46.026 | 1.346 | 1.521 |
| h1 | C | Volatility | 4 | 1238 | 0.061 | 0.964 | 0.018 | 0.488 | 0.002 | -0.059 | 51.777 | 1.504 | 1.486 |

excess = mean over events of (net move - baseline), in ATR. Baseline = average net move of all comparable moments (same symbol, direction, block and bias condition).
