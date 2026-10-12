# Exploratory trade test: all ten setups, one fixed design

Run: `run.py trades`. Not a Stage 2 test: no entry or stop variants were tried, nothing was tuned, and the result
cannot select a setup. It exists so that every setup has win rate, R and profit factor next to a random control.

## Design (fixed before running, identical for all setups)

- Entry: market, at the open of the next M5 candle after the signal closes (ask for buys, bid for sells).
- Stop: 2 x ATR(14) of the signal candle. Target: 2R. Maximum hold: 3 hours, then closed at the candle close.
- Fills: stop at the candle's worst price (spikes jump through), target at its level, spread charged.
- Data: block A only (30 Oct 2025 to 25 May 2026). Blocks B and C untouched.
- Events selected exactly as in Stage 1 (bias, clustering). One position per symbol at a time.
- Control: 4,000 random entries per symbol and bias under the same design (random direction; the H1 direction for the
  H1-bias runs), pooled the same way as each setup.

## Result (all symbols pooled)

| Setup | Bias | Trades | Win % | Stopped % | Avg R | Profit factor | Control avg R | z vs control |
|---|---|---|---|---|---|---|---|---|
| s01 equal highs/lows sweep | none | 323 | 14.2 | 47.1 | -0.068 | 0.88 | -0.046 | -0.3 |
| s02 range sweep | none | 9,455 | 14.8 | 46.9 | -0.054 | 0.90 | -0.046 | -0.7 |
| s02 range sweep | h1 | 3,996 | 14.1 | 45.5 | -0.053 | 0.90 | -0.062 | +0.5 |
| s03 sweep + displacement + FVG | none | 2,926 | 15.4 | 45.6 | -0.037 | 0.93 | -0.046 | +0.4 |
| s04 accumulate/manipulate/distribute | none | 2,828 | 13.7 | 47.2 | -0.078 | 0.87 | -0.046 | -1.4 |
| s05 classic OB retest | none | 5,478 | 13.5 | 45.4 | -0.050 | 0.91 | -0.046 | -0.3 |
| s06 FVG continuation | h1 (built in) | 1,479 | 14.3 | 43.9 | -0.021 | 0.96 | -0.062 | +1.4 |
| s07 OB + FVG | none | 4,661 | 13.4 | 44.8 | -0.039 | 0.93 | -0.046 | +0.4 |
| s08 H1 order block | none | 2,391 | 13.8 | 43.7 | -0.020 | 0.96 | -0.046 | +1.1 |
| s10 sweep + shift + OB (reference) | h1 | 939 | 14.3 | 43.5 | -0.004 | 0.99 | -0.062 | +1.4 |
| s09 spike-base OB | none | 2 | - | - | - | - | - | too few |

The full table (both biases, Boom/Crash split) is in `reports/exploratory_trades.csv`.

## Reading it

- **Every setup loses about as much as random entries**: average R between -0.08 and 0.00, profit factor 0.87 to 0.99,
  against -0.05 R and 0.9 for the control.
- **The best z-score against the control is +1.75** among the 46 cells with at least 300 trades; the worst is -1.41.
  Only 2 of those 46 cells have a positive average R.
- Roughly 14% of trades reach the 2R target, 45% hit the stop and the rest are closed at the 3-hour limit.
- If stops were filled exactly at their level (not at the worst price of the candle), several cells would be around
  zero or slightly positive (up to +0.06 R). Random entries gain by the same amount, so the comparison does not change.
