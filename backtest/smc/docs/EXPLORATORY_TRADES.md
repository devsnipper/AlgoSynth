# Exploratory trade test: all ten setups, one fixed design, 29 months

Run: `run.py trades`. Not a Stage 2 test: no entry or stop variants were tried, nothing was tuned, and the result
cannot select a setup. It exists so that every setup has win rate, R and profit factor next to a random control.

## Design (fixed before running, identical for all setups)

- Entry: market, at the open of the next candle after the signal closes (ask for buys, bid for sells).
- Stop: 2 x ATR(14) of the signal candle. Target: 2R. Maximum hold: 3 hours, then closed at the candle close.
- Fills: stop at the candle's worst price (spikes jump through), target at its level, spread charged.
  A candle that touches both stop and target counts as a stop.
- Block A (30 Oct 2025 to 25 May 2026): M5 candles for fills. Block C (Dec 2023 to 29 Oct 2025): only M15 candles
  exist, so fills are coarser and more pessimistic. The control uses the same fills, so the comparison stays fair.
- Block B (26 May 2026 onward) was **not** opened.
- Events selected exactly as in Stage 1 (bias, clustering). One position per symbol at a time.
- Control: 4,000 random entries per symbol, bias and block under the same design (random direction; the H1
  direction for the H1-bias runs).

## Result (all symbols pooled, 29 months)

| Setup | Bias | Trades (A+C) | Avg R in A | Avg R in C | Avg R A+C | Profit factor | z vs control |
|---|---|---|---|---|---|---|---|
| s01 equal highs/lows sweep | none | 1,287 | -0.068 | -0.125 | -0.110 | 0.82 | -1.3 |
| s01 equal highs/lows sweep | h1 | 566 | -0.110 | -0.145 | -0.136 | 0.78 | -1.2 |
| s02 range sweep | none | 35,861 | -0.054 | -0.099 | -0.087 | 0.85 | **-3.5** |
| s02 range sweep | h1 | 15,340 | -0.053 | -0.074 | -0.069 | 0.88 | +0.5 |
| s03 sweep + displacement + FVG | none | 10,826 | -0.037 | -0.116 | -0.094 | 0.84 | -2.6 |
| s03 sweep + displacement + FVG | h1 | 3,468 | -0.057 | -0.121 | -0.104 | 0.82 | -1.5 |
| s04 accumulate/manipulate/distribute | none | 11,075 | -0.078 | -0.081 | -0.080 | 0.86 | -1.4 |
| s04 accumulate/manipulate/distribute | h1 | 6,391 | -0.057 | -0.061 | -0.060 | 0.90 | +0.9 |
| s05 classic OB retest | none | 20,721 | -0.050 | -0.093 | -0.082 | 0.86 | -2.0 |
| s05 classic OB retest | h1 | 15,125 | -0.062 | -0.083 | -0.077 | 0.87 | -0.4 |
| s06 FVG continuation | h1 (built in) | 5,685 | -0.021 | -0.087 | -0.070 | 0.87 | +0.2 |
| s07 OB + FVG | none | 17,593 | -0.039 | -0.084 | -0.072 | 0.88 | -0.8 |
| s07 OB + FVG | h1 | 12,497 | -0.064 | -0.078 | -0.074 | 0.88 | -0.1 |
| s08 H1 order block | none | 8,940 | -0.020 | -0.088 | -0.070 | 0.88 | -0.4 |
| s08 H1 order block | h1 | 7,679 | -0.036 | -0.091 | -0.076 | 0.87 | -0.2 |
| s10 sweep + shift + OB (reference) | none | 7,035 | -0.051 | -0.063 | -0.060 | 0.90 | +0.3 |
| s10 sweep + shift + OB (reference) | h1 | 3,728 | -0.004 | -0.100 | -0.076 | 0.87 | -0.2 |
| s09 spike-base OB | | 9 to 15 | | | | | too few |
| **Random entries (control)** | none | | -0.046 | -0.076 | **-0.065** | 0.89 | |
| **Random entries (control)** | h1 | | -0.062 | -0.080 | **-0.073** | 0.88 | |

The full table (Boom/Crash split, all blocks) is in `reports/exploratory_trades.csv`.

## Reading it

- **No setup makes money.** Of the 50 cells with at least 300 trades over 29 months, **none has a positive average R**.
  The best is -0.046 R (FVG continuation, H1 bias, Boom). Profit factors run from 0.78 to 0.90.
- **No setup beats random entries.** The best z-score against the control is +1.33; none reaches 3.2.
- **The older months are worse than the recent ones** (control -0.076 R in block C against -0.046 R in block A), mostly
  because the coarser M15 fills charge more for stops. The pattern is the same for setups and control.
- **Some setups are slightly worse than random.** The range sweep without a bias filter is -0.087 R against -0.065 R
  for the control (z = -3.5, over 35,861 trades), and sweep + displacement + FVG is -2.6. Doing the opposite would be
  about 0.02 R better than random, which is still negative after costs, so this is not a usable edge.
- Roughly 14% of trades reach the 2R target, about 45% hit the stop and the rest close at the 3-hour limit.
