# s09: Spike-base order block

**Idea:** on Boom/Crash, an order block at the base of a spike might behave differently from a normal one.

**Rules:** exactly setup 5, but only for order blocks whose leg contains a spike candle (range above 8 x the median
range of the previous 200 candles).

**Known limit:** on Boom/Crash 500, 600 and 900 a spike arrives roughly every candle, so a candle 8 times taller than
the median is rare. This setup finds very few events (about 20 in 34 months across ten symbols). Under the frozen rule
(at least 300 events) it is dropped as too rare to judge. Changing the definition after seeing this would break the
pre-registration, so it stays as it is.

**Code:** `core/orderblocks.py`, flag `has_spike`.
