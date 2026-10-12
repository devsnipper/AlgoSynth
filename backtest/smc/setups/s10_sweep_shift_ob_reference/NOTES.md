# s10: Sweep + structure shift + order block (reference)

**Idea:** the setup tested earlier (Gates 2 and 3): a sweep of a swing point, then a close back beyond the opposite
swing within 12 candles, leaving an order block.

**Rules (M15, swing length 5)**
1. A candle wicks beyond the last confirmed swing low and closes back above it (or the mirror for highs).
2. Within 12 candles, a candle closes beyond the last confirmed swing high that existed before the sweep.
3. Event: the close of that shift candle.

**Direction:** reversal (sweep of lows: long). This is the only setup kept from the earlier work; it gives the
same metric for comparison. The order block entry price and stop that Stage 2 would use are kept as extra columns.

**Code:** `core/primitives.py` (`find_setups`).
