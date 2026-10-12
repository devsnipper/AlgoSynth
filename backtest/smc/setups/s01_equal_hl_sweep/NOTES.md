# s01: Equal highs/lows sweep

**Idea:** stops rest above equal highs and below equal lows. When price wicks through them and closes back,
the move was a stop run, and the trade goes the other way.

**Rules (M15, swing length 5, ATR = ATR(14))**
1. A swing high is confirmed 5 candles after it forms. Two or more unbroken swing highs within 0.15 x ATR of each
   other form a pool at the highest one (mirror for lows).
2. The first candle that trades above the pool and **closes back below it** is the sweep. Direction: short.
   (Mirror: wick below an equal-lows pool and close back above = long.)
3. A candle that closes beyond the pool only consumes it. Pools expire after 200 candles.

**Event:** the close of the sweep candle. **Code:** `core/sweeps.py` (`equal_level_sweeps`).
