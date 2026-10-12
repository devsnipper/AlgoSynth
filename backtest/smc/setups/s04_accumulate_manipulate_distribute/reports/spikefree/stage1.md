# Accumulate, manipulate, distribute (s04_accumulate_manipulate_distribute): Stage 1

Primary test: net move after 12 M15 candles (3h), ATR units, spread included,
minus the average of comparable moments. Pass = z >= 3.4, at least 300 events in block A,
and a positive excess in block C. Block B is not touched at Stage 1.

## Verdict

| bias | group | n_A | excess_A | z_A | n_C | excess_C | z_C | verdict |
|---|---|---|---|---|---|---|---|---|
| none | all | 7908 | -0.012 | -0.471 | 21191 | 0.019 | 1.143 | no edge |
| none | Step | 3245 | 0.031 | 0.786 | 7943 | 0.021 | 0.844 | no edge |
| none | Range Break | 198 | -0.183 | -0.548 | 721 | -0.007 | -0.036 | too few events |
| none | Multi Step | 1924 | -0.039 | -0.739 | 4064 | 0.011 | 0.317 | no edge |
| none | Volatility | 2541 | -0.035 | -0.772 | 8463 | 0.023 | 0.900 | no edge |
| h1 | all | 4778 | -0.014 | -0.418 | 12917 | 0.044 | 2.081 | no edge |
| h1 | Step | 1974 | 0.074 | 1.455 | 4829 | 0.011 | 0.342 | no edge |
| h1 | Range Break | 106 | -0.383 | -0.876 | 369 | 0.386 | 1.505 | too few events |
| h1 | Multi Step | 1177 | 0.020 | 0.303 | 2473 | 0.044 | 0.978 | no edge |
| h1 | Volatility | 1521 | -0.129 | -2.267 | 5246 | 0.049 | 1.548 | no edge |

## All cells

| bias | block | group | symbols | n | excess_3h | z_3h | excess_1h | z_1h | raw_mean | base_mean | win_pct | mfe_med | mae_med |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | A | all | 14 | 7908 | -0.012 | -0.471 | -0.016 | -1.044 | -0.045 | -0.033 | 48.963 | 1.446 | 1.528 |
| none | A | Step | 5 | 3245 | 0.031 | 0.786 | -0.016 | -0.698 | 0.005 | -0.026 | 49.769 | 1.487 | 1.524 |
| none | A | Range Break | 2 | 198 | -0.183 | -0.548 | 0.081 | 0.427 | -0.208 | -0.026 | 50.000 | 1.208 | 0.930 |
| none | A | Multi Step | 3 | 1924 | -0.039 | -0.739 | -0.042 | -1.402 | -0.076 | -0.037 | 48.960 | 1.447 | 1.561 |
| none | A | Volatility | 4 | 2541 | -0.035 | -0.772 | -0.004 | -0.151 | -0.074 | -0.039 | 47.855 | 1.427 | 1.550 |
| none | C | all | 14 | 21191 | 0.019 | 1.143 | 0.011 | 1.157 | -0.012 | -0.031 | 49.809 | 1.499 | 1.492 |
| none | C | Step | 5 | 7943 | 0.021 | 0.844 | 0.013 | 0.915 | -0.004 | -0.025 | 49.641 | 1.513 | 1.492 |
| none | C | Range Break | 2 | 721 | -0.007 | -0.036 | 0.088 | 0.834 | -0.027 | -0.020 | 52.427 | 1.330 | 0.986 |
| none | C | Multi Step | 3 | 4064 | 0.011 | 0.317 | 0.030 | 1.486 | -0.023 | -0.034 | 49.803 | 1.510 | 1.488 |
| none | C | Volatility | 4 | 8463 | 0.023 | 0.900 | -0.007 | -0.479 | -0.014 | -0.037 | 49.746 | 1.503 | 1.537 |
| h1 | A | all | 14 | 4778 | -0.014 | -0.418 | -0.019 | -0.985 | -0.048 | -0.034 | 48.744 | 1.446 | 1.511 |
| h1 | A | Step | 5 | 1974 | 0.074 | 1.455 | 0.004 | 0.132 | 0.051 | -0.023 | 49.899 | 1.522 | 1.506 |
| h1 | A | Range Break | 2 | 106 | -0.383 | -0.876 | 0.134 | 0.684 | -0.403 | -0.021 | 46.226 | 1.307 | 0.959 |
| h1 | A | Multi Step | 3 | 1177 | 0.020 | 0.303 | -0.059 | -1.532 | -0.021 | -0.041 | 48.938 | 1.404 | 1.533 |
| h1 | A | Volatility | 4 | 1521 | -0.129 | -2.267 | -0.028 | -0.833 | -0.172 | -0.043 | 47.272 | 1.424 | 1.556 |
| h1 | C | all | 14 | 12917 | 0.044 | 2.081 | 0.022 | 1.766 | -0.005 | -0.049 | 49.756 | 1.499 | 1.515 |
| h1 | C | Step | 5 | 4829 | 0.011 | 0.342 | 0.009 | 0.496 | -0.020 | -0.031 | 49.389 | 1.508 | 1.511 |
| h1 | C | Range Break | 2 | 369 | 0.386 | 1.505 | 0.287 | 1.773 | 0.336 | -0.050 | 56.640 | 1.403 | 0.941 |
| h1 | C | Multi Step | 3 | 2473 | 0.044 | 0.978 | 0.046 | 1.779 | -0.019 | -0.063 | 49.454 | 1.505 | 1.510 |
| h1 | C | Volatility | 4 | 5246 | 0.049 | 1.548 | 0.003 | 0.157 | -0.009 | -0.058 | 49.752 | 1.499 | 1.561 |

excess = mean over events of (net move - baseline), in ATR. Baseline = average net move of all comparable moments (same symbol, direction, block and bias condition).
