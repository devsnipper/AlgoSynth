# s02: Range-extreme sweep

**Idea:** the high or low of the recent range holds stops. Taking it out and closing back inside is a stop run.

**Rules (M15)**
1. A candle's high goes above the highest high of the previous 20 candles **and** it closes below that level: short.
2. A candle's low goes below the lowest low of the previous 20 candles and closes above that level: long.
3. A candle that does both is ignored.

**Event:** the close of that candle. **Code:** `core/sweeps.py` (`range_sweeps`).
