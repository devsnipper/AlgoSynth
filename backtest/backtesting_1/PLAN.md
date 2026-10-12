# Backtesting plan

Goal: replay the live bot's rules on past data to see if the strategy and its TP/SL settings make money.

## Step 1 — Get the data  (`download_data.py`)
- Connect to MT5 and download M1, M5 and M15 candles for each symbol in `config.py`.
- Save to `backtest/backtesting_1/data/<symbol>_<timeframe>.csv`.
- Print how far back the data goes. This decides how long the test can be.
- Done when: every symbol has 3 CSV files and we know the date range.

## Step 2 — Reusable strategy logic  (`strategy.py` change)
- Split the EMA checks so they work on a DataFrame, not only on live MT5 calls.
- The live bot keeps the same behavior.
- Done when: the same candles give the same signals in live code and in the backtest.

## Step 3 — The backtest engine  (`backtest.py`)
Walk through the M5 candles one by one and apply the live rules:
1. The M15 trend must match the symbol's direction (Crash = buy, Boom = sell).
2. The M5 EMA5/13 cross must happen above/below EMA50.
3. Enter on the candle after the signal.
4. Only one open trade per symbol.
5. Pause 2 minutes after a loss.
6. Stop for the day when daily profit reaches +$3.
7. Lot size comes from `RISK_USD` and the SL distance, like the live bot.
8. Exits use M1 candles. If a candle touches both TP and SL, count it as a loss.
9. Subtract the spread as a cost.
- Done when: it runs on one symbol and produces a trade list.

## Step 4 — Results  (`report`)
- Trade list saved to `backtest/backtesting_1/results/trades_<symbol>.csv`.
- Summary: trades, win rate, total profit, profit factor, worst drawdown.
- Breakdown per symbol and per day.
- Equity curve chart.

## Step 5 — Sanity check
- Compare a few backtest trades with real trades in `logs/trades.csv`.
- If they differ a lot, find out why before trusting the results.

## Step 6 — Experiments
Using the same engine, compare:
- Current TP/SL (about 1:1) against 2:1.
- Which symbols are profitable and which lose.
- With and without the daily +$3 stop.
- Different EMA periods.

## Limits to remember
- Candles can't reproduce the live spike filter exactly.
- Real slippage on spikes will be worse than in the test.
- Boom/Crash prices are random, so a good result is a hint, not a guarantee.
