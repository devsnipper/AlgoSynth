# OB + FVG confluence (s07_ob_fvg_confluence): Stage 1

Primary test: net move after 12 M15 candles (3h), ATR units, spread included,
minus the average of comparable moments. Pass = z >= 3.2, at least 300 events in block A,
and a positive excess in block C. Block B is not touched at Stage 1.

## Verdict

| bias | group | n_A | excess_A | z_A | n_C | excess_C | z_C | verdict |
|---|---|---|---|---|---|---|---|---|
| none | all | 4667 | -0.022 | -0.523 | 12932 | -0.018 | -0.683 | no edge |
| none | Boom | 2383 | -0.079 | -1.332 | 6489 | -0.027 | -0.750 | no edge |
| none | Crash | 2284 | 0.037 | 0.618 | 6443 | -0.008 | -0.216 | no edge |
| h1 | all | 3341 | -0.014 | -0.289 | 9158 | -0.014 | -0.458 | no edge |
| h1 | Boom | 1711 | -0.044 | -0.634 | 4635 | -0.064 | -1.496 | no edge |
| h1 | Crash | 1630 | 0.018 | 0.258 | 4523 | 0.037 | 0.850 | no edge |

## All cells

| bias | block | group | symbols | n | excess_3h | z_3h | excess_1h | z_1h | raw_mean | base_mean | win_pct | mfe_med | mae_med |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | A | all | 10 | 4667 | -0.022 | -0.523 | 0.019 | 0.806 | -0.016 | 0.006 | 50.482 | 1.767 | 1.734 |
| none | A | Boom | 5 | 2383 | -0.079 | -1.332 | -0.013 | -0.403 | -0.069 | 0.010 | 49.433 | 1.698 | 1.784 |
| none | A | Crash | 5 | 2284 | 0.037 | 0.618 | 0.054 | 1.544 | 0.039 | 0.002 | 51.576 | 1.838 | 1.698 |
| none | C | all | 10 | 12932 | -0.018 | -0.683 | 0.004 | 0.281 | -0.027 | -0.009 | 50.356 | 1.772 | 1.734 |
| none | C | Boom | 5 | 6489 | -0.027 | -0.750 | -0.014 | -0.681 | -0.043 | -0.016 | 49.961 | 1.750 | 1.742 |
| none | C | Crash | 5 | 6443 | -0.008 | -0.216 | 0.023 | 1.081 | -0.011 | -0.003 | 50.753 | 1.797 | 1.726 |
| h1 | A | all | 10 | 3341 | -0.014 | -0.289 | 0.005 | 0.190 | -0.032 | -0.018 | 50.165 | 1.730 | 1.775 |
| h1 | A | Boom | 5 | 1711 | -0.044 | -0.634 | -0.008 | -0.189 | -0.080 | -0.036 | 49.445 | 1.667 | 1.816 |
| h1 | A | Crash | 5 | 1630 | 0.018 | 0.258 | 0.019 | 0.462 | 0.019 | 0.001 | 50.920 | 1.784 | 1.719 |
| h1 | C | all | 10 | 9158 | -0.014 | -0.458 | -0.005 | -0.279 | -0.010 | 0.004 | 50.491 | 1.769 | 1.739 |
| h1 | C | Boom | 5 | 4635 | -0.064 | -1.496 | -0.032 | -1.289 | -0.057 | 0.007 | 49.903 | 1.737 | 1.765 |
| h1 | C | Crash | 5 | 4523 | 0.037 | 0.850 | 0.023 | 0.885 | 0.037 | 0.000 | 51.094 | 1.807 | 1.709 |

excess = mean over events of (net move - baseline), in ATR. Baseline = average net move of all comparable moments (same symbol, direction, block and bias condition).
