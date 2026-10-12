# s08: H1 order block, touch measured on M15

**Idea:** order blocks on a higher timeframe are respected more than M15 ones.

**Rules**
1. Setup 5 detected on H1 candles (swing length 3): break of structure, leg, last opposite candle, zone.
2. The break is known when its H1 candle closes. From that moment, the event is the first **M15** candle that
   trades back into the zone, within 48 H1 candles (48 hours).

**Direction:** with the break. **Code:** `setup.py` (uses `core/orderblocks.py`).
