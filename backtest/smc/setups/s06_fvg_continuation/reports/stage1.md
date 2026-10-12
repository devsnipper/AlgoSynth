# FVG continuation (H1 bias) (s06_fvg_continuation): Stage 1

Primary test: net move after 12 M15 candles (3h), ATR units, spread included,
minus the average of comparable moments. Pass = z >= 3.2, at least 300 events in block A,
and a positive excess in block C. Block B is not touched at Stage 1.

## Verdict

| bias | group | n_A | excess_A | z_A | n_C | excess_C | z_C | verdict |
|---|---|---|---|---|---|---|---|---|
| h1 | all | 1481 | 0.175 | 2.371 | 4206 | -0.024 | -0.558 | no edge |
| h1 | Boom | 743 | 0.239 | 2.265 | 2114 | 0.024 | 0.390 | no edge |
| h1 | Crash | 738 | 0.111 | 1.072 | 2092 | -0.073 | -1.199 | no edge |

## All cells

| bias | block | group | symbols | n | excess_3h | z_3h | excess_1h | z_1h | raw_mean | base_mean | win_pct | mfe_med | mae_med |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| h1 | A | all | 10 | 1481 | 0.175 | 2.371 | 0.055 | 1.276 | 0.105 | -0.070 | 48.683 | 1.669 | 1.729 |
| h1 | A | Boom | 5 | 743 | 0.239 | 2.265 | 0.107 | 1.730 | 0.135 | -0.104 | 48.318 | 1.646 | 1.729 |
| h1 | A | Crash | 5 | 738 | 0.111 | 1.072 | 0.001 | 0.025 | 0.074 | -0.037 | 49.051 | 1.695 | 1.730 |
| h1 | C | all | 10 | 4206 | -0.024 | -0.558 | -0.021 | -0.858 | -0.011 | 0.013 | 47.884 | 1.611 | 1.786 |
| h1 | C | Boom | 5 | 2114 | 0.024 | 0.390 | -0.014 | -0.392 | 0.062 | 0.038 | 49.101 | 1.652 | 1.762 |
| h1 | C | Crash | 5 | 2092 | -0.073 | -1.199 | -0.029 | -0.827 | -0.086 | -0.012 | 46.654 | 1.579 | 1.831 |

excess = mean over events of (net move - baseline), in ATR. Baseline = average net move of all comparable moments (same symbol, direction, block and bias condition).
