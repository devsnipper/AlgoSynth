# Range-extreme sweep (20 candles) (s02_range_sweep): Stage 1

Primary test: net move after 12 M15 candles (3h), ATR units, spread included,
minus the average of comparable moments. Pass = z >= 3.2, at least 300 events in block A,
and a positive excess in block C. Block B is not touched at Stage 1.

## Verdict

| bias | group | n_A | excess_A | z_A | n_C | excess_C | z_C | verdict |
|---|---|---|---|---|---|---|---|---|
| none | all | 9463 | 0.033 | 1.094 | 26406 | -0.015 | -0.796 | no edge |
| none | Boom | 4740 | 0.002 | 0.041 | 13151 | -0.039 | -1.485 | no edge |
| none | Crash | 4723 | 0.065 | 1.483 | 13255 | 0.009 | 0.365 | no edge |
| h1 | all | 3999 | 0.016 | 0.342 | 11344 | 0.016 | 0.585 | no edge |
| h1 | Boom | 2015 | -0.057 | -0.887 | 5584 | -0.018 | -0.447 | no edge |
| h1 | Crash | 1984 | 0.089 | 1.343 | 5760 | 0.049 | 1.288 | no edge |

## All cells

| bias | block | group | symbols | n | excess_3h | z_3h | excess_1h | z_1h | raw_mean | base_mean | win_pct | mfe_med | mae_med |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | A | all | 10 | 9463 | 0.033 | 1.094 | 0.011 | 0.623 | 0.012 | -0.022 | 49.435 | 1.776 | 1.856 |
| none | A | Boom | 5 | 4740 | 0.002 | 0.041 | 0.003 | 0.113 | -0.025 | -0.027 | 49.494 | 1.740 | 1.883 |
| none | A | Crash | 5 | 4723 | 0.065 | 1.483 | 0.019 | 0.765 | 0.049 | -0.017 | 49.375 | 1.810 | 1.831 |
| none | C | all | 10 | 26406 | -0.015 | -0.796 | -0.004 | -0.402 | -0.021 | -0.006 | 48.962 | 1.760 | 1.846 |
| none | C | Boom | 5 | 13151 | -0.039 | -1.485 | -0.016 | -1.059 | -0.040 | -0.001 | 48.620 | 1.735 | 1.861 |
| none | C | Crash | 5 | 13255 | 0.009 | 0.365 | 0.007 | 0.493 | -0.003 | -0.012 | 49.302 | 1.788 | 1.831 |
| h1 | A | all | 10 | 3999 | 0.016 | 0.342 | 0.022 | 0.821 | -0.020 | -0.036 | 49.437 | 1.749 | 1.816 |
| h1 | A | Boom | 5 | 2015 | -0.057 | -0.887 | 0.041 | 1.083 | -0.115 | -0.058 | 49.082 | 1.748 | 1.804 |
| h1 | A | Crash | 5 | 1984 | 0.089 | 1.343 | 0.003 | 0.074 | 0.076 | -0.014 | 49.798 | 1.758 | 1.834 |
| h1 | C | all | 10 | 11344 | 0.016 | 0.585 | 0.004 | 0.271 | 0.023 | 0.007 | 50.009 | 1.781 | 1.783 |
| h1 | C | Boom | 5 | 5584 | -0.018 | -0.447 | -0.004 | -0.188 | 0.004 | 0.022 | 49.713 | 1.751 | 1.790 |
| h1 | C | Crash | 5 | 5760 | 0.049 | 1.288 | 0.013 | 0.568 | 0.041 | -0.008 | 50.295 | 1.808 | 1.773 |

excess = mean over events of (net move - baseline), in ATR. Baseline = average net move of all comparable moments (same symbol, direction, block and bias condition).
