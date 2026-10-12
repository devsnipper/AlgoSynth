# The ten SMC setups on the 14 spike-free instruments

Instruments: Step Index (+200, 300, 400, 500), Range Break 100 and 200, Multi Step 2, 3, 4, Volatility 10, 25, 75, 100.
Rules, blocks and thresholds as in `SETUP_LIST.md` and its addendum (written before the run). Block B (26 May 2026
onward) was **not opened**. Results: `reports/spikefree/`.

## Stage 1: does the pattern predict direction? (3 h excess, z >= 3.4)

| | |
|---|---|
| Cells tested | 95 (61 with at least 300 events in block A) |
| **Cells passing** | **0** |
| Best z in block A | +1.59 (s02 range sweep, Step family) |
| Cells at z >= 2 / z <= -2 in block A | 0 / 11 (mean z -0.88) |
| Cells at z >= 2 / z <= -2 in block C | 4 / 1 (mean z +0.34) |
| Cells with the same sign in A and C | 26 of 61 |

The effect changes sign between the recent months (block A) and the older ones (block C), so nothing is stable.
Range Break, the family with built-in breakouts, gives z between -2.9 and +0.6 (order-block setups are the worst there).
Setup 9 (spike-base OB) now finds 150 to 525 events on Range Break, but too few per cell to be judged.

## Exploratory trade test (one fixed design, 29 months, same as for Boom/Crash)

Market entry, 2 ATR stop, 2R target, 3 h hold, stops at the candle's worst price; random-entry control under the same
design. All 14 symbols pooled (blocks A and C together):

| Setup | Bias | Trades | Win % | Avg R | Profit factor | Control avg R | z vs control |
|---|---|---|---|---|---|---|---|
| s01 equal highs/lows | none | 4,570 | 8.8 | -0.115 | 0.79 | -0.085 | -1.7 |
| s02 range sweep | none | 45,404 | 7.2 | -0.069 | 0.86 | -0.085 | +3.3 |
| s02 range sweep | h1 | 20,477 | 7.2 | -0.073 | 0.85 | -0.089 | +2.1 |
| s03 sweep + displacement + FVG | none | 3,423 | 7.9 | -0.074 | 0.85 | -0.085 | +0.6 |
| s04 accumulate/manipulate/distribute | none | 29,083 | 7.7 | -0.077 | 0.85 | -0.085 | +1.3 |
| s05 classic OB retest | none | 28,422 | 8.2 | -0.096 | 0.82 | -0.085 | -1.5 |
| s06 FVG continuation | h1 | 5,287 | 11.7 | -0.126 | 0.79 | -0.089 | -2.1 |
| s07 OB + FVG | none | 19,563 | 7.1 | -0.091 | 0.82 | -0.085 | -0.7 |
| s08 H1 order block | none | 12,988 | 8.9 | -0.100 | 0.82 | -0.085 | -1.4 |
| s09 spike-base OB | none | 675 | 15.0 | -0.120 | 0.80 | -0.085 | -0.6 |
| s10 sweep + shift + OB (reference) | none | 8,386 | 7.5 | -0.088 | 0.83 | -0.085 | -0.2 |

(The H1-bias variants are in `reports/spikefree/exploratory_trades.csv`; they look the same.)

- Of 87 cells with at least 300 trades, **one has a positive average R**: s03 with the H1 bias on the Step family (+0.086 R,
  381 trades, z = +2.7 against random). Its result comes entirely from block C (+0.125 R over 265 trades); in the recent
  block A it is -0.002 R over 116 trades. With 87 comparisons, one cell at z = 2.7 is what chance produces.
- The largest z against the control is s02 range sweep (+3.3, below the 3.4 threshold). It loses -0.069 R per trade
  against -0.085 R for random entries, in both blocks: slightly less bad than random, still a loss (profit factor 0.86).
- Only about 7 to 9% of trades reach the 4 ATR target in 3 hours on these slow indices; about 37% hit the stop.

## Conclusion

On 24 instruments (10 Boom/Crash, 14 spike-free), with three kinds of tests (direction after the pattern, trades with a
fixed design, and the live EMA technique), no SMC setup and no EMA rule shows an edge that survives the thresholds, the
older months and the random control. The spike-free indices are random-walk-like markets designed to be unpredictable,
and the results look like that. The EMA technique that "works" at 73% on Boom/Crash does so only because of the drift
between spikes (see `backtesting_2/REPORT.md`).

What was not tried: stop/target and entry variants (Stage 2), because no cell passed Stage 1; other timeframes;
the discretionary side of SMC; and block B, which stays unopened.
