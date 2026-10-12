# s05: Classic order block retest (first touch)

**Idea:** the last opposite candle of the move that broke structure marks where large orders sat. Price tends to
return to it once.

**Rules (M15, swing length 5)**
1. Break of structure: a candle **closes** beyond the last confirmed swing high (bullish) or swing low (bearish).
2. The leg starts at the lowest low (bullish) or highest high (bearish) between the broken swing and the break.
3. The order block is the **last opposite-colour candle** in that leg (bullish: last bearish candle). Its zone is
   that candle's high-low range.
4. Event: the **first** candle within 48 candles after the break that trades back into the zone. "Unmitigated" is
   built in, because only the first touch counts.

**Direction:** with the break. **Code:** `core/orderblocks.py`.
