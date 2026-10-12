# RSI test on Boom/Crash

Question: does RSI(14) help us avoid spikes or find better entry zones?
Data: 6 symbols, 70 days of M1 candles and 90 days of M5 candles. Script: `rsi_test.py`. Full tables: `results/output.txt`.

## Result

**No. RSI does not predict spikes and does not mark better entry zones.**

## 1. Does RSI predict a spike? (M1 candles)

For each RSI zone, how often a spike against the bot arrives in the next 5 minutes:

| Symbol | Overall | Lowest zone | Highest zone | Spread between zones |
|---|---|---|---|---|
| Boom 500 | 24.7% | 23.8% (RSI 20–30) | 25.9% (RSI < 20) | 2 points |
| Boom 600 | 23.6% | 23.1% | 26.0% (RSI > 80, few candles) | 3 points |
| Boom 900 | 20.4% | 19.6% | 21.2% | 2 points |
| Crash 500 | 24.7% | 24.3% | 30.2% (RSI < 20, 698 candles) | 6 points |

- In the large zones the chance of a spike moves by 1–2 percentage points, which is too small to trade.
- The zones that look different are the ones with few candles (RSI above 80 or below 20), and they do not agree between symbols. Boom 500 has more spikes at low RSI, Crash 500 at low RSI too, but Boom 600 at high RSI.
- This matches the earlier finding: Deriv draws a spike at random on every tick, so past price, and therefore RSI, cannot tell you when it comes.

The same table on M5 candles is not useful, because with 5-minute candles the spike rule rarely flags anything. The M1 result is the one to use.

## 2. Does RSI mark a better zone? (M1 and M5 candles)

For each RSI zone, the average profit in the bot's direction (sell Boom, buy Crash) over the next 5, 15 and 30 minutes (M1) or 1, 3 and 6 candles (M5), compared with the average over all candles. Windows do not overlap, so a lucky stretch is not counted many times.

- **255 comparisons were run. 16 looked different from average, and pure chance would give about 13.**
- Only 4 of those 16 pointed the same way in both halves of the data. They are in four different zones and have opposite signs, for example Boom 150 at RSI 20–30 is better and Crash 150 at RSI 70–80 is worse. That is what random noise looks like.
- The 150 indices have very few candles in some zones, so even their strongest results are not reliable.

## 3. Does an RSI filter fix the strategy?

Not tested. The plan said to add an RSI condition to the EMA backtest only if a zone stood out in section 2. None did.

## Conclusion

RSI adds nothing on Boom and Crash. We keep the EMA rules as they are and move on to SMC (see `../backtesting_1/STRATEGY_PLAN.md` for the pass bar to use).
