# Plan: restructuring the strategy

Based on `REPORT.md`. The goal: find a version that makes money in the backtest on data it was not tuned on, then confirm it on demo.

## What we learned (in short)

- Between spikes, price moves in the bot's favour (73% wins), but each spike costs about 4 wins.
- Spikes jump past any stop we can place, so stop size is not the fix.
- Entry rules, hours of the day and time since the last spike add almost nothing.
- Buying Boom / selling Crash is much worse.
- The 150 indices lose the most (22% of the stop goes to spread, and the stop is inside normal noise).

So: **tuning the current setup will not be enough. The plan is to remove the spike exposure or to find a setup where the gains outweigh it.**

## Pass / fail rule (used for every step)

A setup counts as a success only if all of these hold:
1. Profit above 0 in the **first half** and in the **second half** of the data.
2. At least 300 trades in total.
3. Profit factor of 1.2 or more.
4. Worst single loss no larger than 3× the planned risk.

If nothing passes, we do **not** go live. That is a valid outcome.

## Step 1. Quick cleanup (Boom/Crash only)

Cheap changes to stop the biggest losses:
- Drop Boom 150 and Crash 150 (−113 $ of −135 $). Expected: about −22 $ instead of −135 $.
- Check Boom 600 on its own (+14 $) and the 500/900 pairs, in both halves of the data.
- Keep the daily +3 $ stop.

This will probably not pass the rule by itself. It tells us how far the remaining four symbols are from break-even.

## Step 2. Test instruments without spikes (main candidate)

The account offers many instruments with no Boom/Crash-style jumps, and several have a very low spread and stop level:

| Group | Examples | Why interesting |
|---|---|---|
| Step Index | Step Index, 200, 300, 400, 500 | spread 1–5 points, minimum stop 8–20 points, fixed-size steps, no spikes |
| Range Break | Range Break 100, 200 | spread 10, minimum lot 0.01 |
| Volatility | Volatility 10, 25, 100, 100 (1s), 150 (1s) | smooth random movement, no spikes, but some have high spreads |
| Jump / DEX / Drift Switch | Jump 25, DEX 600 UP, Drift Switch 20 | zero spread; Jump has jumps in both directions, so check carefully |

How to test:
1. Download M1, M5 and M15 data and the symbol settings for 6–10 of these, using `download_data.py`.
2. Run the same backtest engine. The EMA rules need to work in **both directions** here, since these indices have no built-in drift.
3. Run the same exit-size and TP:SL grid, with a train/test split.
4. Apply the pass/fail rule above.

Caveat: these indices are random by design, so there may be no edge at all. The test tells us quickly and cheaply.

## Step 3. Look for structure in the spikes (Boom/Crash, tick data)

Only if Step 2 gives nothing and we still want Boom/Crash:
- Download tick data and measure how long price drifts between spikes and how big the spikes are.
- Test whether a trade that lasts less than 30–60 seconds, with a very small target, avoids most spikes.
- Test whether spike size shrinks or grows with the time since the last one.
- Rebuild the backtest on ticks so the live spike filter is simulated too.

## Step 4. Entry and exit improvements (any instrument that passes Step 1 or 2)

Only apply to a setup that is already close to break-even:
- Compare EMA settings (5/13/50 against slower and faster sets).
- Add a volatility filter (skip entries when the last candles are unusually tall).
- Try one trade per symbol with a time limit (close after N minutes).
- Per-symbol TP/SL instead of one rule for all.

Change one thing at a time, always checking first half against second half.

## Step 5. Risk rules

- Size lots so the **worst realistic loss** (not the planned stop) equals the risk target.
- Add a daily loss limit (for example −3 $), as the best days are capped at +3 $ but bad days are not.
- Pause the symbol for longer after a spike loss.

## Step 6. Demo validation

For any setup that passes Steps 1–5:
1. Run on demo for at least 300 trades or 4 weeks.
2. Compare demo results with the backtest. The win rate, average win and average loss should be within about 15%.
3. If they match and the demo is profitable, consider a small real account. If not, go back to the backtest and find what differs.

## Code changes needed

| Change | File |
|---|---|
| Support any symbol list, both trade directions, and per-symbol settings | `backtest.py` |
| Download data for the new instruments | `download_data.py` |
| Tick-level backtest (Step 3 only) | new file |
| Update `SYMBOLS`, `TP_CONFIG`, `DIRECTION_MAP` for the chosen setup | `config.py`, `main.py` |
| Update the docs that no longer match the code | `README.md`, `skills/*.md` |

## Suggested order

1. Step 1 (about 30 minutes).
2. Step 2 (the main experiment).
3. Decide: continue with the best candidate (Step 4, 5, 6), or Step 3 if Step 2 fails.
