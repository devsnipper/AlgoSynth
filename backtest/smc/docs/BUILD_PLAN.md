> **Status update (restructure done).** Steps 1 to 3 below are finished (data downloaded, no-look-ahead pieces and trade
> engine built and tested). The folder layout in this file is superseded: the code now lives in `backtest/smc/`
> (see `../README.md`): `core/` (shared code), `tools/`, `tests/`, `docs/`, and `setups/` for the ten setups in
> `SETUP_LIST.md`. The pass bar and the data-block rules in `SETUP_LIST.md` are the ones that apply.

# SMC backtest: build plan

Rules are in `SMC_STRATEGY.md`. This file is the order of work. Each step ends at a **gate**: we stop, look at the result, and decide before going on.

## Folder layout (all new, nothing in the live bot changes)

```
backtest/smc/
  SMC_STRATEGY.md        exact rules
  BUILD_PLAN.md          this file
  download_history.py    step 1: long M15 and M5 history, 10 symbols
  smc_causal.py          step 2: swings, structure break, sweep, order block, FVG, bias (no look-ahead)
  test_smc_causal.py     step 2: unit tests + comparison with the library
  backtest_smc.py        step 3: the trade engine
  run_compare.py         step 4: Test 1 vs Test 2 vs controls
  data/                  price files (git-ignored)
  results/               trade lists, tables, charts
  REPORT.md              step 5: findings
```

## Step 1: Get the data

- Download M15 and M5 candles for: Boom 300, 500, 600, 900, 1000 and Crash 300, 500, 600, 900, 1000. The 150 indices are dropped.
- Ask for as much history as the terminal and server allow (up to 100,000 candles, roughly 2 years of M15). Also save each symbol's point size, spread and stop level.
- Build H1 and H4 candles from M15 by resampling, and check that they line up.
- Save to `data/` and make sure the CSV pattern is in `.gitignore` (the existing rule `backtest/**/data/*.csv` already covers it).

**Gate 1:** report how many months of data we really got for each symbol. This decides how many trades we can reach. If the history is too short to reach 300 trades, we say so now and decide whether to continue.

## Step 2: Build the SMC pieces (no look-ahead) and prove them

Write `smc_causal.py` with functions that take candles and return results available only after the right delay:
1. Swing highs and lows (confirmed after `L` candles).
2. Break of structure and the higher-timeframe bias, including premium/discount.
3. Liquidity sweep and structure shift on M15.
4. Order block and fair value gap.
5. Spike clipping for version B.

Tests in `test_smc_causal.py`:
- **Look-ahead test:** compute every result on the first N candles, then on N+50, and check that all values for the first N candles are identical. Any difference means a function used the future.
- **Library check:** install `smartmoneyconcepts` as a development tool only (`pip install --no-deps`, never imported by the bot) and compare. Our swings must match its swings after the delay, and our order blocks must match its order blocks where its swings are stable.
- **Hand-made cases:** a few tiny price series where we know the right answer.

**Gate 2:** all tests pass. We also print 5 setups from real data, side by side with the numbers, so you can see them make sense.

## Step 3: The trade engine

`backtest_smc.py` takes a setup and plays it through the M5 candles:
1. Wait for the limit order to fill (or expire after 8 M15 candles).
2. Follow stop, target and the 3-hour time limit, checking both stop and target on each M5 candle. If both are in the same candle, count the stop.
3. Fill stops at the candle's worst price, including spikes. Include the spread.
4. Record entry, stop, target, result in R, and the reason for the exit.
5. Only one open trade per symbol. No daily stop and no cool-down, since those hide the raw edge.

**Gate 3:** run on one symbol. Check ten trades by hand against the price chart numbers. Check that the trade count and the stop sizes look sane.

## Step 4: Run the comparison

`run_compare.py` runs, on all symbols:
- Test 1 (H4 bias) and Test 2 (H1 bias), each with `L` in {3, 5, 8} and spike handling raw/clipped.
- The two controls (random entries, bias-only).
- The settings are chosen on the first 60% of the data only, then the last 40% is used once to judge.
- A bootstrap to compare each strategy's average R with the control's range.

Outputs: a table per run (trades, win rate, average R, profit factor, drawdown in R, worst loss), a split by symbol and by direction, an equity curve in R, and the pass/fail against the bar.

**Gate 4:** read the numbers together before writing anything.

## Step 5: Report and decision

`REPORT.md` with: the Test 1 vs Test 2 comparison, what each SMC piece added (or didn't), results against the control, the pass/fail verdict, and the limits (for example the spike filter is not simulated, and fills are approximate).

Outcomes and what comes next:
- **Passes the bar:** run it on the demo account, with a small risk, for at least 300 trades or 4 weeks.
- **Fails but one piece looks promising:** one follow-up test on that piece only, using the 40% data we haven't tuned on.
- **Fails:** we stop on Boom/Crash and move to the spike-free instruments in `backtest/backtesting_1/STRATEGY_PLAN.md`.

## Rules for ourselves

- The pass bar is fixed before any result is seen.
- The test period is used once.
- Nothing is changed in `main.py`, `strategy.py` or the live bot until a demo run confirms a result.
- Commit after each gate.
