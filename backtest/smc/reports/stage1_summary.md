# Stage 1 summary

Threshold: z >= 3.2 on the 3h excess, at least 300 events in block A, same sign in block C.

Tests used so far (distinct cells): block A 57, block C 57. Block B opened for: nobody.

**Cells with enough events: 46 of 57. Passing both blocks: 0.**

## Survivors

None.

## All verdicts

| setup | bias | group | n_A | excess_A | z_A | excess_C | z_C | verdict |
|---|---|---|---|---|---|---|---|---|
| s01_equal_hl_sweep | none | all | 324 | 0.089 | 0.530 | -0.122 | -1.325 | no edge |
| s01_equal_hl_sweep | none | Boom | 154 | 0.158 | 0.661 | -0.060 | -0.455 | too few events |
| s01_equal_hl_sweep | none | Crash | 170 | 0.027 | 0.114 | -0.184 | -1.417 | too few events |
| s01_equal_hl_sweep | h1 | all | 150 | -0.069 | -0.293 | -0.184 | -1.384 | too few events |
| s01_equal_hl_sweep | h1 | Boom | 64 | -0.225 | -0.724 | -0.223 | -1.166 | too few events |
| s01_equal_hl_sweep | h1 | Crash | 86 | 0.047 | 0.137 | -0.147 | -0.793 | too few events |
| s02_range_sweep | none | all | 9463 | 0.033 | 1.094 | -0.015 | -0.796 | no edge |
| s02_range_sweep | none | Boom | 4740 | 0.002 | 0.041 | -0.039 | -1.485 | no edge |
| s02_range_sweep | none | Crash | 4723 | 0.065 | 1.483 | 0.009 | 0.365 | no edge |
| s02_range_sweep | h1 | all | 3999 | 0.016 | 0.342 | 0.016 | 0.585 | no edge |
| s02_range_sweep | h1 | Boom | 2015 | -0.057 | -0.887 | -0.018 | -0.447 | no edge |
| s02_range_sweep | h1 | Crash | 1984 | 0.089 | 1.343 | 0.049 | 1.288 | no edge |
| s03_sweep_displacement_fvg | none | all | 2927 | 0.032 | 0.594 | -0.017 | -0.529 | no edge |
| s03_sweep_displacement_fvg | none | Boom | 1490 | -0.031 | -0.418 | -0.010 | -0.214 | no edge |
| s03_sweep_displacement_fvg | none | Crash | 1437 | 0.096 | 1.241 | -0.025 | -0.532 | no edge |
| s03_sweep_displacement_fvg | h1 | all | 942 | 0.040 | 0.427 | -0.055 | -0.981 | no edge |
| s03_sweep_displacement_fvg | h1 | Boom | 502 | 0.041 | 0.337 | -0.059 | -0.754 | no edge |
| s03_sweep_displacement_fvg | h1 | Crash | 440 | 0.038 | 0.268 | -0.052 | -0.637 | no edge |
| s04_accumulate_manipulate_distribute | none | all | 2835 | -0.009 | -0.171 | -0.008 | -0.252 | no edge |
| s04_accumulate_manipulate_distribute | none | Boom | 1411 | -0.071 | -0.910 | -0.033 | -0.719 | no edge |
| s04_accumulate_manipulate_distribute | none | Crash | 1424 | 0.052 | 0.680 | 0.017 | 0.364 | no edge |
| s04_accumulate_manipulate_distribute | h1 | all | 1657 | 0.020 | 0.288 | 0.036 | 0.848 | no edge |
| s04_accumulate_manipulate_distribute | h1 | Boom | 810 | 0.032 | 0.322 | 0.044 | 0.743 | no edge |
| s04_accumulate_manipulate_distribute | h1 | Crash | 847 | 0.009 | 0.089 | 0.027 | 0.454 | no edge |
| s05_classic_ob_retest | none | all | 5485 | -0.036 | -0.933 | -0.026 | -1.082 | no edge |
| s05_classic_ob_retest | none | Boom | 2769 | -0.089 | -1.621 | -0.049 | -1.483 | no edge |
| s05_classic_ob_retest | none | Crash | 2716 | 0.017 | 0.309 | -0.002 | -0.054 | no edge |
| s05_classic_ob_retest | h1 | all | 4035 | -0.013 | -0.284 | -0.016 | -0.577 | no edge |
| s05_classic_ob_retest | h1 | Boom | 2041 | -0.061 | -0.959 | -0.082 | -2.126 | no edge |
| s05_classic_ob_retest | h1 | Crash | 1994 | 0.037 | 0.579 | 0.051 | 1.294 | no edge |
| s06_fvg_continuation | h1 | all | 1481 | 0.175 | 2.371 | -0.024 | -0.558 | no edge |
| s06_fvg_continuation | h1 | Boom | 743 | 0.239 | 2.265 | 0.024 | 0.390 | no edge |
| s06_fvg_continuation | h1 | Crash | 738 | 0.111 | 1.072 | -0.073 | -1.199 | no edge |
| s07_ob_fvg_confluence | none | all | 4667 | -0.022 | -0.523 | -0.018 | -0.683 | no edge |
| s07_ob_fvg_confluence | none | Boom | 2383 | -0.079 | -1.332 | -0.027 | -0.750 | no edge |
| s07_ob_fvg_confluence | none | Crash | 2284 | 0.037 | 0.618 | -0.008 | -0.216 | no edge |
| s07_ob_fvg_confluence | h1 | all | 3341 | -0.014 | -0.289 | -0.014 | -0.458 | no edge |
| s07_ob_fvg_confluence | h1 | Boom | 1711 | -0.044 | -0.634 | -0.064 | -1.496 | no edge |
| s07_ob_fvg_confluence | h1 | Crash | 1630 | 0.018 | 0.258 | 0.037 | 0.850 | no edge |
| s08_h1_order_block | none | all | 2392 | 0.033 | 0.579 | 0.014 | 0.391 | no edge |
| s08_h1_order_block | none | Boom | 1195 | 0.065 | 0.799 | -0.022 | -0.432 | no edge |
| s08_h1_order_block | none | Crash | 1197 | 0.002 | 0.021 | 0.050 | 0.992 | no edge |
| s08_h1_order_block | h1 | all | 2085 | 0.036 | 0.596 | -0.014 | -0.373 | no edge |
| s08_h1_order_block | h1 | Boom | 1047 | 0.103 | 1.188 | -0.049 | -0.901 | no edge |
| s08_h1_order_block | h1 | Crash | 1038 | -0.030 | -0.350 | 0.021 | 0.384 | no edge |
| s09_spike_base_ob | none | all | 2 | -4.537 | -4.762 | 1.052 | 1.168 | too few events |
| s09_spike_base_ob | none | Boom | 1 | -3.584 |  | 0.599 | 0.492 | too few events |
| s09_spike_base_ob | none | Crash | 1 | -5.490 |  | 1.777 | 1.269 | too few events |
| s09_spike_base_ob | h1 | all | 1 | -3.432 |  | 1.939 | 1.481 | too few events |
| s09_spike_base_ob | h1 | Boom | 1 | -3.432 |  | 1.165 | 0.737 | too few events |
| s09_spike_base_ob | h1 | Crash | 0 |  |  | 4.261 | 2.334 | too few events |
| s10_sweep_shift_ob_reference | none | all | 1791 | 0.032 | 0.470 | 0.018 | 0.451 | no edge |
| s10_sweep_shift_ob_reference | none | Boom | 921 | 0.025 | 0.267 | 0.000 | 0.001 | no edge |
| s10_sweep_shift_ob_reference | none | Crash | 870 | 0.039 | 0.401 | 0.035 | 0.636 | no edge |
| s10_sweep_shift_ob_reference | h1 | all | 939 | 0.176 | 1.921 | -0.039 | -0.737 | no edge |
| s10_sweep_shift_ob_reference | h1 | Boom | 476 | 0.195 | 1.508 | -0.094 | -1.245 | no edge |
| s10_sweep_shift_ob_reference | h1 | Crash | 463 | 0.158 | 1.205 | 0.015 | 0.205 | no edge |
