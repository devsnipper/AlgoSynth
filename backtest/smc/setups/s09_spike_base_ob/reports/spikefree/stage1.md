# Spike-base OB (s09_spike_base_ob): Stage 1

Primary test: net move after 12 M15 candles (3h), ATR units, spread included,
minus the average of comparable moments. Pass = z >= 3.4, at least 300 events in block A,
and a positive excess in block C. Block B is not touched at Stage 1.

## Verdict

| bias | group | n_A | excess_A | z_A | n_C | excess_C | z_C | verdict |
|---|---|---|---|---|---|---|---|---|
| none | all | 150 | 0.146 | 0.527 | 525 | 0.114 | 0.785 | too few events |
| none | Step | 0 |  |  | 0 |  |  | too few events |
| none | Range Break | 150 | 0.146 | 0.527 | 525 | 0.114 | 0.785 | too few events |
| none | Multi Step | 0 |  |  | 0 |  |  | too few events |
| none | Volatility | 0 |  |  | 0 |  |  | too few events |
| h1 | all | 111 | 0.194 | 0.572 | 381 | 0.076 | 0.475 | too few events |
| h1 | Step | 0 |  |  | 0 |  |  | too few events |
| h1 | Range Break | 111 | 0.194 | 0.572 | 381 | 0.076 | 0.475 | too few events |
| h1 | Multi Step | 0 |  |  | 0 |  |  | too few events |
| h1 | Volatility | 0 |  |  | 0 |  |  | too few events |

## All cells

| bias | block | group | symbols | n | excess_3h | z_3h | excess_1h | z_1h | raw_mean | base_mean | win_pct | mfe_med | mae_med |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | A | all | 14 | 150 | 0.146 | 0.527 | 0.149 | 1.120 | 0.128 | -0.018 | 57.333 | 0.714 | 0.484 |
| none | A | Step | 5 | 0 |  |  |  |  |  |  |  |  |  |
| none | A | Range Break | 2 | 150 | 0.146 | 0.527 | 0.149 | 1.120 | 0.128 | -0.018 | 57.333 | 0.714 | 0.484 |
| none | A | Multi Step | 3 | 0 |  |  |  |  |  |  |  |  |  |
| none | A | Volatility | 4 | 0 |  |  |  |  |  |  |  |  |  |
| none | C | all | 14 | 525 | 0.114 | 0.785 | -0.063 | -0.767 | 0.098 | -0.016 | 53.524 | 0.742 | 0.600 |
| none | C | Step | 5 | 0 |  |  |  |  |  |  |  |  |  |
| none | C | Range Break | 2 | 525 | 0.114 | 0.785 | -0.063 | -0.767 | 0.098 | -0.016 | 53.524 | 0.742 | 0.600 |
| none | C | Multi Step | 3 | 0 |  |  |  |  |  |  |  |  |  |
| none | C | Volatility | 4 | 0 |  |  |  |  |  |  |  |  |  |
| h1 | A | all | 14 | 111 | 0.194 | 0.572 | 0.023 | 0.143 | 0.202 | 0.007 | 55.856 | 0.726 | 0.753 |
| h1 | A | Step | 5 | 0 |  |  |  |  |  |  |  |  |  |
| h1 | A | Range Break | 2 | 111 | 0.194 | 0.572 | 0.023 | 0.143 | 0.202 | 0.007 | 55.856 | 0.726 | 0.753 |
| h1 | A | Multi Step | 3 | 0 |  |  |  |  |  |  |  |  |  |
| h1 | A | Volatility | 4 | 0 |  |  |  |  |  |  |  |  |  |
| h1 | C | all | 14 | 381 | 0.076 | 0.475 | -0.019 | -0.214 | 0.026 | -0.050 | 52.231 | 0.686 | 0.600 |
| h1 | C | Step | 5 | 0 |  |  |  |  |  |  |  |  |  |
| h1 | C | Range Break | 2 | 381 | 0.076 | 0.475 | -0.019 | -0.214 | 0.026 | -0.050 | 52.231 | 0.686 | 0.600 |
| h1 | C | Multi Step | 3 | 0 |  |  |  |  |  |  |  |  |  |
| h1 | C | Volatility | 4 | 0 |  |  |  |  |  |  |  |  |  |

excess = mean over events of (net move - baseline), in ATR. Baseline = average net move of all comparable moments (same symbol, direction, block and bias condition).
