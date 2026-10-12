# Accumulate, manipulate, distribute (s04_accumulate_manipulate_distribute): Stage 1

Primary test: net move after 12 M15 candles (3h), ATR units, spread included,
minus the average of comparable moments. Pass = z >= 3.2, at least 300 events in block A,
and a positive excess in block C. Block B is not touched at Stage 1.

## Verdict

| bias | group | n_A | excess_A | z_A | n_C | excess_C | z_C | verdict |
|---|---|---|---|---|---|---|---|---|
| none | all | 2835 | -0.009 | -0.171 | 8247 | -0.008 | -0.252 | no edge |
| none | Boom | 1411 | -0.071 | -0.910 | 4149 | -0.033 | -0.719 | no edge |
| none | Crash | 1424 | 0.052 | 0.680 | 4098 | 0.017 | 0.364 | no edge |
| h1 | all | 1657 | 0.020 | 0.288 | 4738 | 0.036 | 0.848 | no edge |
| h1 | Boom | 810 | 0.032 | 0.322 | 2389 | 0.044 | 0.743 | no edge |
| h1 | Crash | 847 | 0.009 | 0.089 | 2349 | 0.027 | 0.454 | no edge |

## All cells

| bias | block | group | symbols | n | excess_3h | z_3h | excess_1h | z_1h | raw_mean | base_mean | win_pct | mfe_med | mae_med |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | A | all | 10 | 2835 | -0.009 | -0.171 | -0.033 | -1.089 | -0.023 | -0.014 | 49.065 | 1.714 | 1.846 |
| none | A | Boom | 5 | 1411 | -0.071 | -0.910 | -0.090 | -2.068 | -0.088 | -0.016 | 49.327 | 1.660 | 1.889 |
| none | A | Crash | 5 | 1424 | 0.052 | 0.680 | 0.023 | 0.556 | 0.040 | -0.012 | 48.806 | 1.787 | 1.797 |
| none | C | all | 10 | 8247 | -0.008 | -0.252 | 0.015 | 0.788 | -0.014 | -0.006 | 48.818 | 1.761 | 1.783 |
| none | C | Boom | 5 | 4149 | -0.033 | -0.719 | -0.011 | -0.405 | -0.034 | -0.001 | 48.566 | 1.726 | 1.794 |
| none | C | Crash | 5 | 4098 | 0.017 | 0.364 | 0.040 | 1.547 | 0.007 | -0.010 | 49.073 | 1.785 | 1.769 |
| h1 | A | all | 10 | 1657 | 0.020 | 0.288 | -0.001 | -0.033 | -0.006 | -0.026 | 49.306 | 1.760 | 1.782 |
| h1 | A | Boom | 5 | 810 | 0.032 | 0.322 | -0.025 | -0.452 | -0.012 | -0.044 | 50.988 | 1.756 | 1.818 |
| h1 | A | Crash | 5 | 847 | 0.009 | 0.089 | 0.021 | 0.386 | 0.000 | -0.009 | 47.698 | 1.788 | 1.734 |
| h1 | C | all | 10 | 4738 | 0.036 | 0.848 | 0.037 | 1.533 | 0.042 | 0.007 | 49.409 | 1.777 | 1.743 |
| h1 | C | Boom | 5 | 2389 | 0.044 | 0.743 | 0.046 | 1.315 | 0.074 | 0.029 | 49.979 | 1.769 | 1.721 |
| h1 | C | Crash | 5 | 2349 | 0.027 | 0.454 | 0.029 | 0.843 | 0.010 | -0.016 | 48.829 | 1.785 | 1.772 |

excess = mean over events of (net move - baseline), in ATR. Baseline = average net move of all comparable moments (same symbol, direction, block and bias condition).
