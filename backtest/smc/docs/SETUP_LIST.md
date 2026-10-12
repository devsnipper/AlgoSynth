# Frozen setup list (written before any result)

All setups run on M15 candles (ATR = ATR(14) on M15), use closed candles only, and have no look-ahead. Parameters below are fixed and not tuned afterwards. Swing length `L = 5`.

## Data blocks and how often each may be opened

| Block | Period | Used for | Looks allowed |
|---|---|---|---|
| **A** | 30 Oct 2025 to 26 May 2026 (first 60% of the main window, M5 available) | Stage 1 and all Stage 2 tuning | As many runs as needed, but every different idea or setting counts as a test |
| **C** | Dec 2023 to 29 Oct 2025 (M15 only, 22 months; 600/900 from Aug 2024) | Consistency check at Stage 1, extra check at the end | Once per finalist |
| **B** | 26 May 2026 to 12 Oct 2026 (last 40% of the main window) | The final verdict only | **Once** per finalist, never repeated. If the rules change after looking at B, B is spent |

Re-running the same code on the same block is fine. Looking at results and then changing rules is what spends a block.

## Stage 1: event study (does the pattern predict anything?)

For each occurrence the event time is the close of the signal candle. We then enter at market at the next M5 open and measure the net move in the setup's direction (after spread), in ATR units, 1 hour and 3 hours later, plus the best and worst excursion. The result is compared with random moments of the same symbol and period.

| # | Setup | Event and direction |
|---|---|---|
| 1 | **Equal highs/lows sweep** | A pool of 2 or more confirmed swing points within 0.15 × ATR. A candle wicks beyond the pool and closes back inside. Direction: opposite the wick. |
| 2 | **Range-extreme sweep** | High (low) of a candle goes beyond the highest high (lowest low) of the previous 20 candles and closes back inside. Direction: opposite the wick. |
| 3 | **Sweep + displacement + FVG** | After a sweep (1 or 2), within 6 candles a candle with a body of at least 1.5 × ATR moves the opposite way and leaves a fair value gap. Event at the close of the candle after it. Direction: with the displacement. |
| 4 | **Accumulate, manipulate, distribute** | A range of at least 12 candles with total width of at most 3 × ATR. Within the next 6 candles a candle wicks beyond one side and closes back inside. Direction: toward the other side of the range. |
| 5 | **Classic OB retest** | A break of structure (M15 close beyond the last confirmed swing). The order block is the last opposite-colour candle in the leg that made the break. Event: the first time price trades back into the block, within 48 candles. Direction: with the break. "Unmitigated" is part of the definition, because only the first touch counts. |
| 6 | **FVG continuation** | In the direction of the H1 bias, a displacement candle (body at least 1.5 × ATR) leaves a fair value gap. Event: the first time price trades back into the gap, after at least 2 candles and within 24 candles. Direction: the bias. |
| 7 | **OB + FVG confluence** | Setup 5, but only when the leg that made the break also contains a fair value gap in the same direction. |
| 8 | **H1 order block** | Setup 5 detected on H1 candles. Event: first touch, measured on M15. |
| 9 | **Spike-base OB** | Setup 5, but only when the leg that made the break contains a spike candle (range above 8 × the median range of the previous 200 candles). |
| 10 | **Sweep + shift + OB (reference)** | The setup tested in Gates 2 and 3, for the same metric. |

Each setup runs with the **H1 bias**, with **no bias**, and split into **Boom**, **Crash** and **all symbols**. That is 10 setups × 2 × 3 = 60 comparisons.

Setups 3, 6, 7, 8 and 9 reuse the same events as 1, 2, 5 with extra conditions, so they are tested as separate setups but overlap.

### Rules for Stage 1

- **One event per symbol per 12 candles**: clustered events count once.
- **At least 300 events** pooled for a setup, otherwise it is dropped as too rare to judge.
- **Threshold:** the average move must beat the random average by at least **3.2 standard errors** (a 0.05 error rate divided over 60 comparisons).
- **Consistency:** the effect must have the same sign on block A (first 60% of the main window) and on block C (the 22 older months, M15 candles only, entry at the next M15 open). Block B is not used at Stage 1.
- A setup that passes all three goes to Stage 2. We take at most the top 3.

## Stage 2: can it be traded? (survivors only)

On the first 60% of the data only, with the existing engine:

- **Entry:** near edge of the zone, midpoint, far edge, fair value gap midpoint, or an M5 candle closing back out of the zone after touching it.
- **Stop:** beyond the sweep wick, beyond the zone's far edge, or 2 × ATR.
- That is 15 entry/stop combinations, with the target fixed at 2R and the hold at 3 hours. Only the best combination goes further, and then target (1.5R, 2R, 3R) and hold (3 h, 12 h) are tuned on it.
- Every combination is compared with matched random entries using the same stop distances.

Then the pass bar from `SMC_STRATEGY.md`: positive in both parts of the data, at least 300 trades, profit factor of at least 1.2, a clear win over random entries. The last 40% is opened once. The older 22 months (M15 only) are a third check.

## Build order

Simplest first: 2, 1, 3, 5, 7, 8, 9, 6, 4, with look-ahead tests for each. Setup 10 reuses existing code.
