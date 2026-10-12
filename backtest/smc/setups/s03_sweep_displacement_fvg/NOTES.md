# s03: Sweep + displacement + fair value gap

**Idea:** a sweep followed by a strong move away that leaves a gap shows that the stop run was real.

**Rules (M15)**
1. Start from a sweep of setup 1 or setup 2 (candle `s`, direction `d`).
2. Within the next 6 candles, find the first candle `k` that moves in direction `d` with a body of at least
   1.5 x ATR **and** leaves a fair value gap in that direction (the candle before and the candle after do not overlap).
3. The gap is only known when the candle after `k` closes, so the event is the close of candle `k + 1`.

**Direction:** with the displacement. **Code:** `setup.py` (uses `core/sweeps.py`).
