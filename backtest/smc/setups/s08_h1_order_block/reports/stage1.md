# H1 order block, touch measured on M15 (s08_h1_order_block): Stage 1

Primary test: net move after 12 M15 candles (3h), ATR units, spread included,
minus the average of comparable moments. Pass = z >= 3.2, at least 300 events in block A,
and a positive excess in block C. Block B is not touched at Stage 1.

## Verdict

| bias | group | n_A | excess_A | z_A | n_C | excess_C | z_C | verdict |
|---|---|---|---|---|---|---|---|---|
| none | all | 2392 | 0.033 | 0.579 | 6549 | 0.014 | 0.391 | no edge |
| none | Boom | 1195 | 0.065 | 0.799 | 3314 | -0.022 | -0.432 | no edge |
| none | Crash | 1197 | 0.002 | 0.021 | 3235 | 0.050 | 0.992 | no edge |
| h1 | all | 2085 | 0.036 | 0.596 | 5595 | -0.014 | -0.373 | no edge |
| h1 | Boom | 1047 | 0.103 | 1.188 | 2809 | -0.049 | -0.901 | no edge |
| h1 | Crash | 1038 | -0.030 | -0.350 | 2786 | 0.021 | 0.384 | no edge |

## All cells

| bias | block | group | symbols | n | excess_3h | z_3h | excess_1h | z_1h | raw_mean | base_mean | win_pct | mfe_med | mae_med |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | A | all | 10 | 2392 | 0.033 | 0.579 | 0.010 | 0.290 | 0.030 | -0.003 | 51.714 | 1.804 | 1.697 |
| none | A | Boom | 5 | 1195 | 0.065 | 0.799 | -0.007 | -0.146 | 0.064 | -0.001 | 52.720 | 1.798 | 1.678 |
| none | A | Crash | 5 | 1197 | 0.002 | 0.021 | 0.027 | 0.557 | -0.004 | -0.006 | 50.710 | 1.815 | 1.719 |
| none | C | all | 10 | 6549 | 0.014 | 0.391 | -0.009 | -0.442 | 0.006 | -0.008 | 49.885 | 1.751 | 1.745 |
| none | C | Boom | 5 | 3314 | -0.022 | -0.432 | -0.047 | -1.584 | -0.031 | -0.010 | 49.638 | 1.695 | 1.767 |
| none | C | Crash | 5 | 3235 | 0.050 | 0.992 | 0.030 | 1.047 | 0.044 | -0.006 | 50.139 | 1.807 | 1.733 |
| h1 | A | all | 10 | 2085 | 0.036 | 0.596 | -0.000 | -0.005 | 0.012 | -0.025 | 51.511 | 1.790 | 1.716 |
| h1 | A | Boom | 5 | 1047 | 0.103 | 1.188 | 0.008 | 0.167 | 0.060 | -0.043 | 52.722 | 1.769 | 1.673 |
| h1 | A | Crash | 5 | 1038 | -0.030 | -0.350 | -0.009 | -0.177 | -0.036 | -0.006 | 50.289 | 1.799 | 1.756 |
| h1 | C | all | 10 | 5595 | -0.014 | -0.373 | -0.020 | -0.907 | -0.010 | 0.005 | 49.741 | 1.755 | 1.747 |
| h1 | C | Boom | 5 | 2809 | -0.049 | -0.901 | -0.061 | -1.849 | -0.038 | 0.011 | 49.769 | 1.707 | 1.780 |
| h1 | C | Crash | 5 | 2786 | 0.021 | 0.384 | 0.020 | 0.657 | 0.019 | -0.002 | 49.713 | 1.795 | 1.729 |

excess = mean over events of (net move - baseline), in ATR. Baseline = average net move of all comparable moments (same symbol, direction, block and bias condition).
