# SMC strategy: exact rules for the backtest

Two tests, one difference between them:

| | Test 1 | Test 2 |
|---|---|---|
| Higher timeframe (bias) | **H4** | **H1** |
| Execution timeframe | M15 | M15 |
| Everything else | identical | identical |

Test 2 should produce more trades, because an H1 bias changes more often than an H4 bias. Because only one thing differs, any gap between the two results comes from the higher timeframe.

All higher-timeframe candles are built from the M15 data. An H4 or H1 candle is only used after it has closed.

## No-look-ahead rules (apply to everything)

1. **Swing point.** A swing high is a candle whose high is above the `L` candles before and after it. It is only known `L` candles after it formed, so the code may use it only from then on. Default `L = 5` on M15, `L = 3` on H1/H4.
2. **Signals are used on the candle after they form.** A candle can't be both the signal and the fill.
3. **Stops fill at the candle's worst price**, as in the EMA backtest. The cost is the spread from each candle.
4. Every result is measured in **R**: profit divided by the planned loss. 1R is the distance from entry to stop.

## Step 1: Higher-timeframe bias (H4 in Test 1, H1 in Test 2)

**Base rule (decided at Gate 2, before any profit result): bias direction only.**
- Bullish if the last confirmed break of structure on this timeframe is upward (a close above the last swing high), bearish if downward. Long setups need a bullish bias, short setups a bearish bias.

**Why premium/discount was removed from the base rule.** Combined with the direction rule it left only 211 setups with H4 and 55 with H1 in 11.5 months (against about 1,600 for direction only). After a bullish break, price usually sits in the premium half of the range, so "bullish bias and price in the discount half" is rare.

**Premium/discount stays as an ablation step.** Midpoint of the last confirmed swing low and swing high: long only below it, short only above it. It is kept only if it improves the out-of-sample result, and it is judged on the longer M15-only history, where it has enough trades.

## Step 2: M15 setup (long example; short is the mirror)

1. **Liquidity sweep.** An M15 candle trades below the last confirmed swing low but closes back above it.
2. **Structure shift.** Within 12 candles after the sweep, an M15 candle closes above the last confirmed swing high that existed before the sweep.
3. **Order block.** The lowest-low candle between the sweep and the shift. Its range is the entry zone. (This is how the `smartmoneyconcepts` library defines it.)
4. **Fair value gap (side test).** The bullish three-candle gap left by the move, if there is one.

## Step 3: Entry, stop and target

- **Entry:** limit order at the middle of the order block. It expires after 8 M15 candles if not filled.
- **Stop:** just below the sweep low (one spread below). If the stop distance is smaller than Deriv's minimum (stops level plus spread), the setup is skipped.
- **Target (first run):** a single target at **2R**.
- **Time limit:** close after 3 hours (12 M15 candles), at the market price.
- Stops and targets are checked on M5 candles, so fills follow what really happened inside each M15 candle. The last 70 days are cross-checked with M1.

### Fill rules (engine)

- **Entry (limit order):** a buy fills when the ask (candle low + spread) reaches the entry price; a sell fills when the bid (candle high) reaches it. If the candle opens past the entry price, the fill is at the open.
- **Stop:** buys stop out when the low reaches the stop; sells when the high plus spread reaches it. The headline result fills at the candle's worst price. A second figure, "R at the stop level", is shown for comparison.
- **Target:** 2R from the fill price, where 1R is the distance from the fill to the stop.
- **Same candle touches both stop and target, or fills and hits the stop:** counted as a stop.
- **Time limit:** 3 hours after the fill, closed at the candle's closing price (bid for buys, ask for sells).
- **One position or pending order per symbol.** A setup arriving while the symbol is busy is ignored.
- **Minimum stop:** setups with a stop closer than the stops level plus spread are skipped and counted.
- **Risk per trade:** 1R. Results are reported in R, so the account size doesn't matter.

## Spike handling (tested both ways)

Spikes are very tall candles that would create fake structure.
- **Version A (raw):** use the candles as they are.
- **Version B (clipped):** when marking swings, sweeps and order blocks, shrink any spike candle's wick to 1 normal candle range beyond its body. A spike candle is one taller than 8 times the median range of the last 200 candles. Fills are always tested against the real prices.

## Directions

Structure chooses the direction on every symbol, long or short. As a side test, the result is also split into "with the drift" (sell Boom, buy Crash) and "with the spikes" (buy Boom, sell Crash).

## Controls (the strategy must beat these)

- **Random entries:** random M15 candle, random direction, same stop distance and 2R target as the real setups.
- **Bias-only:** the HTF bias and premium/discount rules with a random entry. Shows what the M15 sweep and structure shift add.

## Parameters kept small (to avoid over-fitting)

Swing length `L` in {3, 5, 8} and spike handling in {raw, clipped}. Reward-to-risk is fixed at 2 for the first run. Nothing else is tuned.

## Pass bar (set now, before any result)

1. Positive total R in the **first 60%** and the **last 40%** of the data (settings chosen on the first part only). The split falls on 26 May 2026. Gate 3 looks at the first 60% only; the last 40% is opened once, in Step 4.
2. At least **300 trades** in total.
3. Profit factor of **1.2** or more.
4. A clear win over the random control, confirmed by a bootstrap (the strategy's average R must sit above the control's 95% range).
5. Worst single loss no worse than **−2R** on average per symbol (this catches the spike-gap problem).
