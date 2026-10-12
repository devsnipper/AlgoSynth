# Stage 1 report: does any SMC setup predict direction on Boom/Crash?

Run: `run.py study all`. Ten setups, 10 symbols, blocks A (30 Oct 2025 to 25 May 2026) and C (older months, M15 only).
Block B (26 May 2026 onward) was **not opened**. Rules and thresholds are those frozen in `SETUP_LIST.md`.

## Method in one paragraph

For every event we enter at market at the next open and measure the net move after 3 hours (12 M15 candles), in ATR
units, spread included. From it we subtract the average of all comparable moments (same symbol, direction, block and,
for the H1-bias runs, the same H1 direction). The average of these differences, divided by its standard error, is z.
A cell passes if z >= 3.2, it has at least 300 events in block A, and its excess is positive in block C.
Events of one symbol closer than 12 candles count once.

## Result

| | |
|---|---|
| Cells tested (blocks A and C each) | 57 |
| Cells with at least 300 events | 46 |
| **Cells passing** | **0** |
| Largest z | +2.37 (setup 6, H1 bias, all symbols) |
| Setups dropped as too rare | 9 (spike-base OB, 2 events) |

Largest z-scores in block A, with what happened in block C:

| Setup | Bias | Group | Events (A) | Excess (A) | z (A) | Excess (C) |
|---|---|---|---|---|---|---|
| s06 FVG continuation | H1 (built in) | all | 1,481 | +0.175 ATR | +2.37 | **-0.024** |
| s06 FVG continuation | H1 | Boom | 743 | +0.239 | +2.27 | +0.024 |
| s10 sweep + shift + OB (reference) | H1 | all | 939 | +0.176 | +1.92 | **-0.039** |
| s02 range sweep | none | Crash | 4,723 | +0.065 | +1.48 | +0.009 |
| s03 sweep + displacement + FVG | none | Crash | 1,437 | +0.096 | +1.24 | -0.025 |

## Reading it

- **Nothing is close.** 57 cells were tested; by chance alone about 1.3 would reach z = 2.0. Two did (both setup 6).
  The best result lost its sign on the older months, so it is consistent with luck.
- **The effects are tiny.** Even the largest is 0.24 ATR over three hours, which is smaller than the typical
  spread plus spike cost on these instruments. Most cells are within +-0.1 ATR of zero.
- **Order blocks do nothing.** Setups 5, 7 and 8 (classic, with FVG, on H1) have z between -1.6 and +1.2.
- **No setup is reversed either** (no cell is significantly worse than random), so fading them is no better.
- **Setup 9** (spike-base OB) cannot be judged: on 500/600/900 indices a spike arrives about every candle, so a
  candle 8x the median is almost never found.
- This is consistent with earlier measurements: on Boom/Crash the drift between spikes and the spike cost cancel out,
  and spike timing has no memory.

## Limits

- Stage 1 tests direction after a market entry, with no stop and no target. A setup could in principle help in a
  stop/target design while showing nothing here, but there is nothing to build a design on.
- One horizon (3 h) was the test; 1 h is reported only (`stage1_cells.csv`).
- Definitions are one mechanical reading of each concept. Discretionary SMC includes judgement that is not coded.

## Decision

No finalist, so Stage 2 (entry/stop/target variants) is not run and block B stays unopened. Per the plan, the next
step is the spike-free instruments (Step Index, Range Break, Volatility), with the same pipeline.
