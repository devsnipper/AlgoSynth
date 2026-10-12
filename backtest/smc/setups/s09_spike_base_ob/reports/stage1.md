# Spike-base OB (s09_spike_base_ob): Stage 1

Primary test: net move after 12 M15 candles (3h), ATR units, spread included,
minus the average of comparable moments. Pass = z >= 3.2, at least 300 events in block A,
and a positive excess in block C. Block B is not touched at Stage 1.

## Verdict

| bias | group | n_A | excess_A | z_A | n_C | excess_C | z_C | verdict |
|---|---|---|---|---|---|---|---|---|
| none | all | 2 | -4.537 | -4.762 | 13 | 1.052 | 1.168 | too few events |
| none | Boom | 1 | -3.584 |  | 8 | 0.599 | 0.492 | too few events |
| none | Crash | 1 | -5.490 |  | 5 | 1.777 | 1.269 | too few events |
| h1 | all | 1 | -3.432 |  | 8 | 1.939 | 1.481 | too few events |
| h1 | Boom | 1 | -3.432 |  | 6 | 1.165 | 0.737 | too few events |
| h1 | Crash | 0 |  |  | 2 | 4.261 | 2.334 | too few events |

## All cells

| bias | block | group | symbols | n | excess_3h | z_3h | excess_1h | z_1h | raw_mean | base_mean | win_pct | mfe_med | mae_med |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | A | all | 10 | 2 | -4.537 | -4.762 | -1.436 | -1.393 | -4.596 | -0.059 | 0.000 | 0.504 | 4.662 |
| none | A | Boom | 5 | 1 | -3.584 |  | -0.405 |  | -3.611 | -0.027 | 0.000 | 1.008 | 3.611 |
| none | A | Crash | 5 | 1 | -5.490 |  | -2.467 |  | -5.582 | -0.091 | 0.000 | 0.000 | 5.714 |
| none | C | all | 10 | 13 | 1.052 | 1.168 | 0.218 | 0.497 | 1.085 | 0.033 | 46.154 | 2.824 | 1.806 |
| none | C | Boom | 5 | 8 | 0.599 | 0.492 | 0.934 | 2.259 | 0.636 | 0.037 | 37.500 | 2.575 | 1.629 |
| none | C | Crash | 5 | 5 | 1.777 | 1.269 | -0.929 | -1.341 | 1.804 | 0.027 | 60.000 | 3.232 | 2.736 |
| h1 | A | all | 10 | 1 | -3.432 |  | -0.349 |  | -3.611 | -0.180 | 0.000 | 1.008 | 3.611 |
| h1 | A | Boom | 5 | 1 | -3.432 |  | -0.349 |  | -3.611 | -0.180 | 0.000 | 1.008 | 3.611 |
| h1 | A | Crash | 5 | 0 |  |  |  |  |  |  |  |  |  |
| h1 | C | all | 10 | 8 | 1.939 | 1.481 | 0.536 | 1.150 | 1.966 | 0.027 | 62.500 | 2.837 | 1.414 |
| h1 | C | Boom | 5 | 6 | 1.165 | 0.737 | 0.909 | 1.678 | 1.188 | 0.023 | 50.000 | 2.739 | 1.320 |
| h1 | C | Crash | 5 | 2 | 4.261 | 2.334 | -0.583 | -6.695 | 4.299 | 0.038 | 100.000 | 5.343 | 2.056 |

excess = mean over events of (net move - baseline), in ATR. Baseline = average net move of all comparable moments (same symbol, direction, block and bias condition).
