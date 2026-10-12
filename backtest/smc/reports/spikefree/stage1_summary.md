# Stage 1 summary: spikefree, z >= 3.4

Threshold: z >= 3.4 on the 3h excess, at least 300 events in block A, same sign in block C.

Ledger: {'tests_block_A': 57, 'tests_block_C': 57, 'spikefree_tests_block_A': 95, 'spikefree_tests_block_C': 95, 'runs': 3, 'block_B_opened_for': []}. Block B opened for: nobody.

**Cells with enough events: 61 of 95. Passing both blocks: 0.**

## Survivors

None.

## Reversed (significantly worse than random; not a pass)

| setup | bias | group | n_A | excess_A | z_A | n_C | excess_C | z_C |
|---|---|---|---|---|---|---|---|---|
| s05_classic_ob_retest | h1 | all | 5504 | -0.119 | -3.540 | 15159 | 0.020 | 0.976 |
| s07_ob_fvg_confluence | h1 | all | 3721 | -0.147 | -3.823 | 10047 | 0.008 | 0.329 |

## Highest z in block A

| setup | bias | group | n_A | excess_A | z_A | n_C | excess_C | z_C | verdict |
|---|---|---|---|---|---|---|---|---|---|
| s02_range_sweep | none | Step | 5054 | 0.050 | 1.591 | 12378 | -0.005 | -0.228 | no edge |
| s04_accumulate_manipulate_distribute | h1 | Step | 1974 | 0.074 | 1.455 | 4829 | 0.011 | 0.342 | no edge |
| s10_sweep_shift_ob_reference | none | Volatility | 681 | 0.110 | 1.319 | 2311 | 0.006 | 0.124 | no edge |
| s10_sweep_shift_ob_reference | h1 | Volatility | 362 | 0.138 | 1.184 | 1238 | 0.061 | 0.964 | no edge |
| s02_range_sweep | h1 | Step | 2271 | 0.044 | 0.947 | 5522 | -0.022 | -0.718 | no edge |
| s04_accumulate_manipulate_distribute | none | Step | 3245 | 0.031 | 0.786 | 7943 | 0.021 | 0.844 | no edge |
| s08_h1_order_block | h1 | Volatility | 805 | 0.041 | 0.530 | 2721 | -0.044 | -1.008 | no edge |
| s02_range_sweep | h1 | Multi Step | 1366 | 0.029 | 0.473 | 2850 | -0.005 | -0.115 | no edge |

## All verdicts

| setup | bias | group | n_A | excess_A | z_A | excess_C | z_C | verdict |
|---|---|---|---|---|---|---|---|---|
| s01_equal_hl_sweep | none | all | 1206 | -0.054 | -0.704 | -0.017 | -0.355 | no edge |
| s01_equal_hl_sweep | none | Step | 496 | -0.050 | -0.500 | -0.069 | -1.080 | no edge |
| s01_equal_hl_sweep | none | Range Break | 225 | -0.381 | -1.432 | -0.016 | -0.111 | too few events |
| s01_equal_hl_sweep | none | Multi Step | 248 | 0.077 | 0.509 | 0.170 | 1.798 | too few events |
| s01_equal_hl_sweep | none | Volatility | 237 | 0.110 | 0.773 | -0.060 | -0.784 | too few events |
| s01_equal_hl_sweep | h1 | all | 596 | -0.079 | -0.683 | -0.024 | -0.333 | no edge |
| s01_equal_hl_sweep | h1 | Step | 239 | -0.099 | -0.675 | -0.105 | -1.099 | too few events |
| s01_equal_hl_sweep | h1 | Range Break | 128 | -0.356 | -0.945 | 0.079 | 0.381 | too few events |
| s01_equal_hl_sweep | h1 | Multi Step | 120 | 0.005 | 0.023 | -0.024 | -0.168 | too few events |
| s01_equal_hl_sweep | h1 | Volatility | 109 | 0.199 | 0.940 | -0.006 | -0.055 | too few events |
| s02_range_sweep | none | all | 12448 | -0.006 | -0.316 | 0.018 | 1.392 | no edge |
| s02_range_sweep | none | Step | 5054 | 0.050 | 1.591 | -0.005 | -0.228 | no edge |
| s02_range_sweep | none | Range Break | 181 | -0.365 | -1.221 | -0.036 | -0.221 | too few events |
| s02_range_sweep | none | Multi Step | 3063 | -0.028 | -0.699 | 0.039 | 1.377 | no edge |
| s02_range_sweep | none | Volatility | 4150 | -0.044 | -1.250 | 0.030 | 1.550 | no edge |
| s02_range_sweep | h1 | all | 5615 | -0.018 | -0.594 | 0.031 | 1.648 | no edge |
| s02_range_sweep | h1 | Step | 2271 | 0.044 | 0.947 | -0.022 | -0.718 | no edge |
| s02_range_sweep | h1 | Range Break | 101 | -0.423 | -1.015 | 0.413 | 1.780 | too few events |
| s02_range_sweep | h1 | Multi Step | 1366 | 0.029 | 0.473 | -0.005 | -0.115 | no edge |
| s02_range_sweep | h1 | Volatility | 1877 | -0.105 | -2.045 | 0.076 | 2.665 | no edge |
| s03_sweep_displacement_fvg | none | all | 889 | -0.036 | -0.481 | 0.027 | 0.560 | no edge |
| s03_sweep_displacement_fvg | none | Step | 353 | 0.001 | 0.009 | 0.197 | 2.374 | no edge |
| s03_sweep_displacement_fvg | none | Range Break | 71 | -0.339 | -0.912 | 0.172 | 0.760 | too few events |
| s03_sweep_displacement_fvg | none | Multi Step | 196 | -0.001 | -0.006 | 0.024 | 0.228 | too few events |
| s03_sweep_displacement_fvg | none | Volatility | 269 | -0.028 | -0.216 | -0.138 | -1.980 | too few events |
| s03_sweep_displacement_fvg | h1 | all | 328 | -0.132 | -1.022 | 0.171 | 2.016 | no edge |
| s03_sweep_displacement_fvg | h1 | Step | 116 | 0.014 | 0.070 | 0.393 | 2.682 | too few events |
| s03_sweep_displacement_fvg | h1 | Range Break | 38 | -0.512 | -0.952 | 0.764 | 2.091 | too few events |
| s03_sweep_displacement_fvg | h1 | Multi Step | 74 | 0.096 | 0.366 | 0.009 | 0.056 | too few events |
| s03_sweep_displacement_fvg | h1 | Volatility | 100 | -0.324 | -1.523 | -0.101 | -0.828 | too few events |
| s04_accumulate_manipulate_distribute | none | all | 7908 | -0.012 | -0.471 | 0.019 | 1.143 | no edge |
| s04_accumulate_manipulate_distribute | none | Step | 3245 | 0.031 | 0.786 | 0.021 | 0.844 | no edge |
| s04_accumulate_manipulate_distribute | none | Range Break | 198 | -0.183 | -0.548 | -0.007 | -0.036 | too few events |
| s04_accumulate_manipulate_distribute | none | Multi Step | 1924 | -0.039 | -0.739 | 0.011 | 0.317 | no edge |
| s04_accumulate_manipulate_distribute | none | Volatility | 2541 | -0.035 | -0.772 | 0.023 | 0.900 | no edge |
| s04_accumulate_manipulate_distribute | h1 | all | 4778 | -0.014 | -0.418 | 0.044 | 2.081 | no edge |
| s04_accumulate_manipulate_distribute | h1 | Step | 1974 | 0.074 | 1.455 | 0.011 | 0.342 | no edge |
| s04_accumulate_manipulate_distribute | h1 | Range Break | 106 | -0.383 | -0.876 | 0.386 | 1.505 | too few events |
| s04_accumulate_manipulate_distribute | h1 | Multi Step | 1177 | 0.020 | 0.303 | 0.044 | 0.978 | no edge |
| s04_accumulate_manipulate_distribute | h1 | Volatility | 1521 | -0.129 | -2.267 | 0.049 | 1.548 | no edge |
| s05_classic_ob_retest | none | all | 7544 | -0.066 | -2.271 | -0.008 | -0.424 | no edge |
| s05_classic_ob_retest | none | Step | 2791 | -0.071 | -1.684 | 0.046 | 1.735 | no edge |
| s05_classic_ob_retest | none | Range Break | 955 | -0.250 | -1.934 | -0.046 | -0.669 | no edge |
| s05_classic_ob_retest | none | Multi Step | 1634 | -0.048 | -0.854 | 0.013 | 0.360 | no edge |
| s05_classic_ob_retest | none | Volatility | 2164 | 0.008 | 0.171 | -0.050 | -1.915 | no edge |
| s05_classic_ob_retest | h1 | all | 5504 | -0.119 | -3.540 | 0.020 | 0.976 | REVERSED (significantly worse than random) |
| s05_classic_ob_retest | h1 | Step | 2024 | -0.109 | -2.223 | 0.058 | 1.857 | no edge |
| s05_classic_ob_retest | h1 | Range Break | 713 | -0.399 | -2.744 | 0.075 | 0.984 | no edge |
| s05_classic_ob_retest | h1 | Multi Step | 1209 | -0.073 | -1.134 | -0.020 | -0.462 | no edge |
| s05_classic_ob_retest | h1 | Volatility | 1558 | -0.040 | -0.712 | -0.022 | -0.714 | no edge |
| s06_fvg_continuation | h1 | all | 1331 | -0.102 | -1.142 | -0.016 | -0.316 | no edge |
| s06_fvg_continuation | h1 | Step | 319 | -0.116 | -0.902 | -0.019 | -0.233 | no edge |
| s06_fvg_continuation | h1 | Range Break | 587 | -0.160 | -0.921 | 0.016 | 0.179 | no edge |
| s06_fvg_continuation | h1 | Multi Step | 170 | -0.067 | -0.393 | -0.043 | -0.411 | too few events |
| s06_fvg_continuation | h1 | Volatility | 255 | 0.025 | 0.181 | -0.071 | -0.954 | too few events |
| s07_ob_fvg_confluence | none | all | 5251 | -0.088 | -2.679 | -0.006 | -0.324 | no edge |
| s07_ob_fvg_confluence | none | Step | 2059 | -0.093 | -1.902 | 0.044 | 1.419 | no edge |
| s07_ob_fvg_confluence | none | Range Break | 354 | -0.355 | -1.689 | 0.046 | 0.424 | no edge |
| s07_ob_fvg_confluence | none | Multi Step | 1203 | -0.094 | -1.450 | -0.002 | -0.050 | no edge |
| s07_ob_fvg_confluence | none | Volatility | 1635 | -0.019 | -0.352 | -0.066 | -2.215 | no edge |
| s07_ob_fvg_confluence | h1 | all | 3721 | -0.147 | -3.823 | 0.008 | 0.329 | REVERSED (significantly worse than random) |
| s07_ob_fvg_confluence | h1 | Step | 1462 | -0.140 | -2.404 | 0.048 | 1.288 | no edge |
| s07_ob_fvg_confluence | h1 | Range Break | 239 | -0.472 | -1.883 | 0.097 | 0.770 | too few events |
| s07_ob_fvg_confluence | h1 | Multi Step | 869 | -0.132 | -1.752 | -0.044 | -0.870 | no edge |
| s07_ob_fvg_confluence | h1 | Volatility | 1151 | -0.102 | -1.576 | -0.024 | -0.664 | no edge |
| s08_h1_order_block | none | all | 3445 | -0.080 | -1.770 | 0.005 | 0.190 | no edge |
| s08_h1_order_block | none | Step | 1167 | -0.048 | -0.767 | 0.032 | 0.790 | no edge |
| s08_h1_order_block | none | Range Break | 671 | -0.364 | -2.379 | 0.003 | 0.036 | no edge |
| s08_h1_order_block | none | Multi Step | 691 | 0.010 | 0.112 | 0.069 | 1.205 | no edge |
| s08_h1_order_block | none | Volatility | 916 | 0.021 | 0.279 | -0.048 | -1.164 | no edge |
| s08_h1_order_block | h1 | all | 2924 | -0.080 | -1.673 | 0.012 | 0.407 | no edge |
| s08_h1_order_block | h1 | Step | 1016 | -0.019 | -0.281 | 0.002 | 0.054 | no edge |
| s08_h1_order_block | h1 | Range Break | 490 | -0.522 | -2.909 | 0.071 | 0.744 | no edge |
| s08_h1_order_block | h1 | Multi Step | 613 | 0.012 | 0.127 | 0.076 | 1.246 | no edge |
| s08_h1_order_block | h1 | Volatility | 805 | 0.041 | 0.530 | -0.044 | -1.008 | no edge |
| s09_spike_base_ob | none | all | 150 | 0.146 | 0.527 | 0.114 | 0.785 | too few events |
| s09_spike_base_ob | none | Step | 0 |  |  |  |  | too few events |
| s09_spike_base_ob | none | Range Break | 150 | 0.146 | 0.527 | 0.114 | 0.785 | too few events |
| s09_spike_base_ob | none | Multi Step | 0 |  |  |  |  | too few events |
| s09_spike_base_ob | none | Volatility | 0 |  |  |  |  | too few events |
| s09_spike_base_ob | h1 | all | 111 | 0.194 | 0.572 | 0.076 | 0.475 | too few events |
| s09_spike_base_ob | h1 | Step | 0 |  |  |  |  | too few events |
| s09_spike_base_ob | h1 | Range Break | 111 | 0.194 | 0.572 | 0.076 | 0.475 | too few events |
| s09_spike_base_ob | h1 | Multi Step | 0 |  |  |  |  | too few events |
| s09_spike_base_ob | h1 | Volatility | 0 |  |  |  |  | too few events |
| s10_sweep_shift_ob_reference | none | all | 2226 | -0.000 | -0.009 | -0.027 | -0.886 | no edge |
| s10_sweep_shift_ob_reference | none | Step | 874 | -0.046 | -0.620 | -0.023 | -0.472 | no edge |
| s10_sweep_shift_ob_reference | none | Range Break | 169 | 0.044 | 0.136 | -0.108 | -0.712 | too few events |
| s10_sweep_shift_ob_reference | none | Multi Step | 502 | -0.086 | -0.878 | -0.060 | -0.933 | no edge |
| s10_sweep_shift_ob_reference | none | Volatility | 681 | 0.110 | 1.319 | 0.006 | 0.124 | no edge |
| s10_sweep_shift_ob_reference | h1 | all | 1205 | -0.055 | -0.750 | 0.004 | 0.095 | no edge |
| s10_sweep_shift_ob_reference | h1 | Step | 470 | -0.058 | -0.571 | -0.031 | -0.485 | no edge |
| s10_sweep_shift_ob_reference | h1 | Range Break | 95 | -0.740 | -1.488 | 0.038 | 0.179 | too few events |
| s10_sweep_shift_ob_reference | h1 | Multi Step | 278 | -0.065 | -0.488 | -0.064 | -0.715 | too few events |
| s10_sweep_shift_ob_reference | h1 | Volatility | 362 | 0.138 | 1.184 | 0.061 | 0.964 | no edge |
