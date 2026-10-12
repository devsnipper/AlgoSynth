# s04: Accumulate, manipulate, distribute

**Idea:** price sits in a tight range (accumulation), pokes through one side to trigger stops (manipulation),
then moves to the other side (distribution).

**Rules (M15)**
1. Accumulation: the last 12 candles have a total width (highest high minus lowest low) of at most 3 x ATR.
2. Manipulation: within the next 6 candles, a candle wicks beyond one side of that range and **closes back inside**.
   The range must not have been pierced before.
3. If one candle wicks beyond both sides, or closes outside, there is no event.

**Direction:** towards the opposite side of the range (wick above the range: short). **Event:** the close of the
manipulation candle. **Code:** `setup.py`.
