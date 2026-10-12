# s06: Fair value gap continuation

**Idea:** in a trending market, price returns once to the gap a strong candle left behind, then continues.

**Rules (M15; the H1 bias is part of the definition, so this setup has no "no bias" variant)**
1. A displacement candle (body at least 1.5 x ATR) leaves a fair value gap in its direction. The gap is known when
   the next candle closes.
2. Event: the **first** time price trades back into the gap, at least 2 candles after the gap completes and within
   24 candles. A touch earlier than that cancels the gap.
3. The H1 structure direction at the touch must equal the trade direction.

**Direction:** with the displacement (and the H1 bias). **Code:** `setup.py`.
