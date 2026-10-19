# The three SMC techniques

The code is in this folder; this file says the same thing in words. If the two ever disagree, the code is what runs.
All three work the same way: **H4 gives the bias, H1 gives the zone, M15 gives the trigger.** The scan runs on every
M15 candle close, using closed candles only. When a technique's conditions are met, the system sends the signal on
Telegram and opens a **market order** (Deriv synthetic indices do not accept pending orders).

| Technique | Id in the CSV | Magic | Idea |
|---|---|---|---|
| A | `SMC_A_OB_TREND` | 223401 | Trade with the trend when price returns to a fresh H1 order block |
| B | `SMC_B_SWEEP_REV` | 223402 | Trade the reversal after price grabs a liquidity level and snaps back |
| C | `SMC_C_PD_OB_FVG` | 223403 | Technique A, but only the best entries: right half of the range, gap in the move |

Priority when two techniques signal on the same symbol on the same candle: **C, then A, then B**. The first trades,
the others are logged as skipped (`symbol_busy`) with their entry, SL and TP, so they can be compared later.

## Words used

- **Bias:** the direction of the last break of structure on H4. A break of structure is a candle that *closes* beyond
  the last confirmed swing high (up) or swing low (down). A swing is confirmed 3 candles after it forms.
- **Order block (OB):** the last opposite-colour candle of the move that broke structure. Its high-low range is the zone.
- **Fair value gap (FVG):** three candles where the first and third do not overlap; the middle one moved fast.
- **R:** the distance from entry to stop loss. A 2R target is twice that distance.

## A: trend continuation at an H1 order block

1. H4 bias is up (down).
2. An H1 order block exists, formed by a break in that direction, within the last 48 H1 candles, not touched since.
3. Price comes back into the zone (M15 wick), and within 4 M15 candles an M15 candle **closes back out of the zone** in
   the bias direction. That close is the trigger. A close beyond the zone's far edge cancels the zone.
4. **Entry:** market, at the trigger candle's close.
5. **Stop loss:** beyond the zone's far edge, plus 0.25 x the H1 ATR.
6. **Take profit:** 2R. Skipped if the next confirmed H4 swing in the trade direction is closer than 1.5R.

## B: liquidity sweep and structure shift

1. A liquidity level is traded through and the M15 candle **closes back inside**. Levels used: the previous calendar day's
   high or low, the extreme of the last 20 closed H1 candles, and pools of equal highs or lows on H1 (two swings
   within 0.15 x ATR). The direction is opposite to the wick (high swept: sell).
2. Within 12 M15 candles, a candle **closes beyond the last confirmed M15 swing on the other side** (known before the
   sweep). That close is the trigger. If price closes beyond the sweep extreme first, the idea is cancelled.
3. **Entry:** market, at the trigger candle's close.
4. **Stop loss:** beyond the sweep extreme, plus 0.25 x the M15 ATR. **Take profit:** 3R.

No bias filter: this is a reversal technique.

## C: premium/discount order block with a fair value gap

Everything in A, with extra conditions:
1. The order block's move contains a fair value gap in the same direction.
2. **Buys only in the discount half** of the H4 range (below its midpoint), **sells only in the premium half**. The range
   runs from the last confirmed H4 swing low to the last confirmed H4 swing high.
3. **Take profit:** the other end of the H4 range, capped at 3R. If that end is closer than 2R, the signal is skipped.
   (Reward-to-risk is therefore always between 1:2 and 1:3 for C, 1:2 for A and 1:3 for B.)
4. The "next H4 swing" room check of A is replaced by this range check.

## How often they signal (measured on 34 months of history, per symbol, before any risk filter)

| Technique | Signals per week per symbol | Over the bot's six symbols |
|---|---|---|
| A | 0.2 to 0.3 | about 1.5 per week |
| C | 0.35 to 0.45 | about 2.2 per week |
| B | about 5 | about 28 per week |

A and C together are close to the "4 good positions a week" you asked for. B, as specified, is far too frequent. About
half of its signals come from the previous-day levels and half from the 20-candle H1 range; equal-high/low pools almost
never form (0.07 per week). Tightening B is a decision for the owner and is not applied here.

## What the system cannot do (broker limits)

Deriv synthetic indices refuse pending orders and refuse SL/TP changes after opening. So there is **no break-even, no
trailing stop and no partial exit**: a trade ends at its stop, its target or the 24-hour time stop.

## Identity of a signal

`signal_id = technique | symbol | direction | trigger time`. The same signal found again on the next scan or after a
restart has the same id, so it is never traded twice.
