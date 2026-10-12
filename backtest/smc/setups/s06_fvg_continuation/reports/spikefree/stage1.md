# FVG continuation (H1 bias) (s06_fvg_continuation): Stage 1

Primary test: net move after 12 M15 candles (3h), ATR units, spread included,
minus the average of comparable moments. Pass = z >= 3.4, at least 300 events in block A,
and a positive excess in block C. Block B is not touched at Stage 1.

## Verdict

| bias | group | n_A | excess_A | z_A | n_C | excess_C | z_C | verdict |
|---|---|---|---|---|---|---|---|---|
| h1 | all | 1331 | -0.102 | -1.142 | 3957 | -0.016 | -0.316 | no edge |
| h1 | Step | 319 | -0.116 | -0.902 | 739 | -0.019 | -0.233 | no edge |
| h1 | Range Break | 587 | -0.160 | -0.921 | 1914 | 0.016 | 0.179 | no edge |
| h1 | Multi Step | 170 | -0.067 | -0.393 | 413 | -0.043 | -0.411 | too few events |
| h1 | Volatility | 255 | 0.025 | 0.181 | 891 | -0.071 | -0.954 | too few events |

## All cells

| bias | block | group | symbols | n | excess_3h | z_3h | excess_1h | z_1h | raw_mean | base_mean | win_pct | mfe_med | mae_med |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| h1 | A | all | 14 | 1331 | -0.102 | -1.142 | -0.074 | -1.461 | -0.128 | -0.026 | 48.835 | 1.277 | 1.372 |
| h1 | A | Step | 5 | 319 | -0.116 | -0.902 | -0.104 | -1.380 | -0.141 | -0.025 | 47.022 | 1.396 | 1.578 |
| h1 | A | Range Break | 2 | 587 | -0.160 | -0.921 | -0.117 | -1.214 | -0.178 | -0.018 | 49.574 | 0.947 | 0.826 |
| h1 | A | Multi Step | 3 | 170 | -0.067 | -0.393 | -0.068 | -0.671 | -0.111 | -0.044 | 45.294 | 1.451 | 1.502 |
| h1 | A | Volatility | 4 | 255 | 0.025 | 0.181 | 0.059 | 0.706 | -0.011 | -0.036 | 51.765 | 1.472 | 1.414 |
| h1 | C | all | 14 | 3957 | -0.016 | -0.316 | -0.028 | -1.000 | -0.057 | -0.041 | 49.684 | 1.232 | 1.355 |
| h1 | C | Step | 5 | 739 | -0.019 | -0.233 | -0.001 | -0.020 | -0.045 | -0.027 | 47.767 | 1.382 | 1.445 |
| h1 | C | Range Break | 2 | 1914 | 0.016 | 0.179 | -0.017 | -0.335 | -0.016 | -0.032 | 51.829 | 0.992 | 0.846 |
| h1 | C | Multi Step | 3 | 413 | -0.043 | -0.411 | -0.133 | -2.232 | -0.107 | -0.063 | 46.005 | 1.294 | 1.539 |
| h1 | C | Volatility | 4 | 891 | -0.071 | -0.954 | -0.027 | -0.642 | -0.131 | -0.060 | 48.373 | 1.409 | 1.540 |

excess = mean over events of (net move - baseline), in ATR. Baseline = average net move of all comparable moments (same symbol, direction, block and bias condition).
