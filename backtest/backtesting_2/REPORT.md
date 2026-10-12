# The live EMA technique on spike-free instruments, same period as backtesting_1

Window: 4 Aug 2026 07:00 to 12 Oct 2026 08:05 (69 days). The first backtest started 8 hours earlier (3 Aug 22:44);
the new M1 files start at 06:59, so both sides here start at 07:00. Code: `replay.py`, `compare.py`.
Control: the replay reproduces backtesting_1 exactly on the six original symbols (1,194 trades, -135.44 $).

## What was replayed

The live bot's rules, with its own functions from `strategy.py` (read only): M15 trend EMA5 > EMA13 > EMA50 (or the
reverse), M5 EMA5/13 cross on the right side of EMA50, entry at the next candle, fixed TP and SL, one trade at a
time across all symbols, 2-minute pause after a loss, stop for the day at +3 $, risk 0.30 $ per trade, stop filled at
the candle's worst price.

Two adaptations, fixed before running:
- **Direction.** The live bot buys every Crash and sells every Boom because of their drift. These indices have no drift,
  so the direction is the M15 trend itself.
- **TP/SL.** The live bot has fixed values per index. Here: SL = (stops level + spread) x 1.2 points (the rule in
  `skills/broker-constraints.md`) and TP = SL. Values used: Step Index 11 to 30 points, Range Break 91, Multi Step
  96 to 155, Volatility 10 / 25 / 75 / 100: 1,090 / 869 / 14,921 / 197 (`results/tpsl_used.json`).

The comparison is in **R** (profit divided by the planned loss), because the planned risk is not 0.30 $ on the new
indices: their minimum lots are larger (median planned risk 1.43 $, up to 3.00 $, against 0.33 $ on Boom/Crash).

## Result

| | Trades | Win % | Profit factor | Avg R | Total | Max drawdown |
|---|---|---|---|---|---|---|
| **Boom/Crash**, 6 symbols, live settings, as the bot runs | 1,187 | 73.0 | 0.70 | -0.38 | -137 $ | 140 $ |
| **Spike-free**, 14 symbols, adapted, as the bot runs | 3,709 | 39.1 | 0.45 | -0.54 | -2,313 $ | 2,321 $ |

Each symbol on its own (no global lock, no daily stop), by family:

| | Trades | Win % | Profit factor | Avg R |
|---|---|---|---|---|
| Boom/Crash (6) | 1,260 | 72.4 | 0.68 | -0.40 |
| Multi Step (3) | 1,293 | 42.8 | 0.53 | -0.40 |
| Range Break (2) | 1,045 | 28.7 | 0.26 | -0.83 |
| Step Index (5) | 2,070 | 39.0 | 0.37 | -0.65 |
| Volatility (4) | 1,745 | 42.5 | 0.61 | -0.35 |

**All 14 spike-free indices lose.** Average R per symbol runs from -0.20 (Volatility 75) to -0.97 (Step Index 300).
Profit factors are between 0.25 and 0.69. The full per-symbol table is in `results/compare_C_by_symbol.csv`.

## Why the win rate drops from 73% to 39%

- On Boom/Crash the technique trades *with the drift* (sells Boom, buys Crash). That gives 73% small wins, and the
  spikes cause rare, large losses (average loss -4.1 R, worst -15.6 R). It needs 80% wins to break even and gets 72%.
- The spike-free indices have no drift. A 1:1 TP/SL then behaves like a coin flip with a cost: a buy enters at the ask,
  and the stop is only a few points away, so the spread is 10 to 20% of the stop on Step Index. That alone drops the
  win rate to about 42%. Losses average -1.53 R (the stop fills at the candle's worst price), so the technique needs 60%
  wins to break even and gets 39%.
- So the 73% on Boom/Crash was not skill of the EMA rules: it came from the drift. Without the drift there is nothing left.

## Is it an artefact of the "stop first" rule?

When one M1 candle touches both the stop and the target, the order is unknown and the first backtest counts a loss.
Here that happens on only 2.4% of trades (7.0% on Step Index, 0% on Range Break). Re-running with the target first
(optimistic) and with the average of both outcomes:

| Markets | Stop first | Average | Target first |
|---|---|---|---|
| Boom/Crash, avg R | -0.40 | -0.30 | -0.20 |
| Spike-free, avg R | -0.54 | -0.51 | -0.49 |

Even in the most favourable case the spike-free indices lose about 0.5 R per trade. The conclusion does not depend on it.

## Limits

- TP/SL for the new indices follow the broker-minimum rule the live bot uses. Wider stops or other TP:SL ratios were not
  tried here; they would be a different strategy, not the live technique.
- 69 days of one market period.
- Dollar figures are not comparable between the two sides because of the minimum lots; use R.
