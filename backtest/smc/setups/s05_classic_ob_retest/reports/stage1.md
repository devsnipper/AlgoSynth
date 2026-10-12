# Classic OB retest (first touch) (s05_classic_ob_retest): Stage 1

Primary test: net move after 12 M15 candles (3h), ATR units, spread included,
minus the average of comparable moments. Pass = z >= 3.2, at least 300 events in block A,
and a positive excess in block C. Block B is not touched at Stage 1.

## Verdict

| bias | group | n_A | excess_A | z_A | n_C | excess_C | z_C | verdict |
|---|---|---|---|---|---|---|---|---|
| none | all | 5485 | -0.036 | -0.933 | 15243 | -0.026 | -1.082 | no edge |
| none | Boom | 2769 | -0.089 | -1.621 | 7654 | -0.049 | -1.483 | no edge |
| none | Crash | 2716 | 0.017 | 0.309 | 7589 | -0.002 | -0.054 | no edge |
| h1 | all | 4035 | -0.013 | -0.284 | 11093 | -0.016 | -0.577 | no edge |
| h1 | Boom | 2041 | -0.061 | -0.959 | 5596 | -0.082 | -2.126 | no edge |
| h1 | Crash | 1994 | 0.037 | 0.579 | 5497 | 0.051 | 1.294 | no edge |

## All cells

| bias | block | group | symbols | n | excess_3h | z_3h | excess_1h | z_1h | raw_mean | base_mean | win_pct | mfe_med | mae_med |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | A | all | 10 | 5485 | -0.036 | -0.933 | 0.016 | 0.717 | -0.038 | -0.002 | 50.009 | 1.760 | 1.776 |
| none | A | Boom | 5 | 2769 | -0.089 | -1.621 | -0.019 | -0.593 | -0.088 | 0.001 | 48.935 | 1.694 | 1.816 |
| none | A | Crash | 5 | 2716 | 0.017 | 0.309 | 0.051 | 1.602 | 0.013 | -0.004 | 51.105 | 1.839 | 1.726 |
| none | C | all | 10 | 15243 | -0.026 | -1.082 | -0.001 | -0.091 | -0.034 | -0.008 | 49.715 | 1.748 | 1.768 |
| none | C | Boom | 5 | 7654 | -0.049 | -1.483 | -0.030 | -1.533 | -0.060 | -0.011 | 49.530 | 1.736 | 1.775 |
| none | C | Crash | 5 | 7589 | -0.002 | -0.054 | 0.027 | 1.405 | -0.007 | -0.005 | 49.901 | 1.759 | 1.762 |
| h1 | A | all | 10 | 4035 | -0.013 | -0.284 | 0.013 | 0.496 | -0.036 | -0.023 | 50.062 | 1.738 | 1.782 |
| h1 | A | Boom | 5 | 2041 | -0.061 | -0.959 | -0.012 | -0.336 | -0.102 | -0.041 | 48.996 | 1.667 | 1.818 |
| h1 | A | Crash | 5 | 1994 | 0.037 | 0.579 | 0.039 | 1.035 | 0.032 | -0.004 | 51.153 | 1.815 | 1.721 |
| h1 | C | all | 10 | 11093 | -0.016 | -0.577 | 0.001 | 0.063 | -0.011 | 0.005 | 49.959 | 1.759 | 1.759 |
| h1 | C | Boom | 5 | 5596 | -0.082 | -2.126 | -0.042 | -1.882 | -0.071 | 0.011 | 49.518 | 1.733 | 1.786 |
| h1 | C | Crash | 5 | 5497 | 0.051 | 1.294 | 0.045 | 1.928 | 0.049 | -0.002 | 50.409 | 1.792 | 1.726 |

excess = mean over events of (net move - baseline), in ATR. Baseline = average net move of all comparable moments (same symbol, direction, block and bias condition).
