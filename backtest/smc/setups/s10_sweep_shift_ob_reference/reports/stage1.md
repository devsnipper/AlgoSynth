# Sweep + structure shift + OB (reference) (s10_sweep_shift_ob_reference): Stage 1

Primary test: net move after 12 M15 candles (3h), ATR units, spread included,
minus the average of comparable moments. Pass = z >= 3.2, at least 300 events in block A,
and a positive excess in block C. Block B is not touched at Stage 1.

## Verdict

| bias | group | n_A | excess_A | z_A | n_C | excess_C | z_C | verdict |
|---|---|---|---|---|---|---|---|---|
| none | all | 1791 | 0.032 | 0.470 | 5244 | 0.018 | 0.451 | no edge |
| none | Boom | 921 | 0.025 | 0.267 | 2616 | 0.000 | 0.001 | no edge |
| none | Crash | 870 | 0.039 | 0.401 | 2628 | 0.035 | 0.636 | no edge |
| h1 | all | 939 | 0.176 | 1.921 | 2789 | -0.039 | -0.737 | no edge |
| h1 | Boom | 476 | 0.195 | 1.508 | 1396 | -0.094 | -1.245 | no edge |
| h1 | Crash | 463 | 0.158 | 1.205 | 1393 | 0.015 | 0.205 | no edge |

## All cells

| bias | block | group | symbols | n | excess_3h | z_3h | excess_1h | z_1h | raw_mean | base_mean | win_pct | mfe_med | mae_med |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | A | all | 10 | 1791 | 0.032 | 0.470 | -0.018 | -0.447 | 0.018 | -0.014 | 50.810 | 1.759 | 1.767 |
| none | A | Boom | 5 | 921 | 0.025 | 0.267 | -0.035 | -0.638 | 0.008 | -0.017 | 50.814 | 1.745 | 1.784 |
| none | A | Crash | 5 | 870 | 0.039 | 0.401 | 0.001 | 0.022 | 0.028 | -0.011 | 50.805 | 1.769 | 1.746 |
| none | C | all | 10 | 5244 | 0.018 | 0.451 | 0.010 | 0.421 | 0.011 | -0.006 | 49.905 | 1.697 | 1.703 |
| none | C | Boom | 5 | 2616 | 0.000 | 0.001 | 0.024 | 0.768 | -0.003 | -0.003 | 49.771 | 1.712 | 1.745 |
| none | C | Crash | 5 | 2628 | 0.035 | 0.636 | -0.005 | -0.164 | 0.025 | -0.010 | 50.038 | 1.680 | 1.672 |
| h1 | A | all | 10 | 939 | 0.176 | 1.921 | -0.023 | -0.431 | 0.148 | -0.029 | 52.183 | 1.763 | 1.710 |
| h1 | A | Boom | 5 | 476 | 0.195 | 1.508 | -0.004 | -0.051 | 0.147 | -0.048 | 52.941 | 1.847 | 1.668 |
| h1 | A | Crash | 5 | 463 | 0.158 | 1.205 | -0.042 | -0.557 | 0.149 | -0.009 | 51.404 | 1.709 | 1.718 |
| h1 | C | all | 10 | 2789 | -0.039 | -0.737 | -0.006 | -0.200 | -0.032 | 0.007 | 49.731 | 1.681 | 1.739 |
| h1 | C | Boom | 5 | 1396 | -0.094 | -1.245 | 0.005 | 0.114 | -0.077 | 0.017 | 49.355 | 1.690 | 1.817 |
| h1 | C | Crash | 5 | 1393 | 0.015 | 0.205 | -0.018 | -0.389 | 0.013 | -0.003 | 50.108 | 1.663 | 1.692 |

excess = mean over events of (net move - baseline), in ATR. Baseline = average net move of all comparable moments (same symbol, direction, block and bias condition).
