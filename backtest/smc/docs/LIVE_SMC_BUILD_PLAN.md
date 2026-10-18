# Building plan: three SMC techniques running live (demo), next to the existing EMA bot

Status: **approved by the owner on 18 Oct 2026, with one change (D3, below). Branch `feature/smc-live` created. Implementation starts once the guard is adjusted (D7).**

## 1. Goal

Run three order-block techniques (A, B, C) at the same time on the instruments the bot already trades. For every signal
the system (1) sends a Telegram message with the technique, entry, SL and TP, then (2) opens the position at market.
Every signal and every trade is logged with the technique that produced it, so the techniques can be compared.

## 2. Facts found while preparing this plan (they shape the design)

| Fact | Consequence |
|---|---|
| The bot is **not running**. On 12 Oct it ran 13:00 to 17:00 and opened nothing: all 741 logged orders were refused with code 10027. | **MT5 "Algo Trading" is OFF** (confirmed today). It must be switched on, or nothing will ever be traded. The new system checks this at start and tells you on Telegram instead of retrying. |
| The account is **hedging** (several positions per symbol allowed). | The SMC system and the EMA bot can coexist on the same symbol without cancelling each other. |
| Deriv synthetic indices **refuse pending orders** (code 10015), and the repo notes say SL/TP cannot be changed after opening (10016). | Entries are **market orders at the trigger**, not limit orders. SL and TP are fixed at opening. **No break-even, no trailing stop, no partial exits** unless a demo test shows they work. |
| Minimum lots are 0.2 (Boom/Crash 500, 600, 900) and 0.5 (150). | With SMC stops of several price units the real risk is above the formula's: e.g. Boom 500, lot 0.2, stop 8 units = about 1.6 $. Risk is checked before each order. |
| `reporter.py` reads `trades.csv` by column **name**; `main.py` restores the day's PnL from the same file. | New columns appended at the end are safe. But SMC rows must not count towards the EMA bot's +3 $/day stop (see section 7). |
| Our research found **no edge** for these ideas on these indices (z-scores and trade tests, 24 instruments). Long holds also meet more spikes (a spike every ~18 minutes on Boom 500). | This is a **forward test with measured outcomes, on demo**. The expectation, from the evidence, is a result near or below zero. It is not a plan to make money. |

## 3. Decisions I need from you

Recommended answer first.

| # | Question | Recommendation |
|---|---|---|
| D1 | Instruments | The bot's six: Boom 150, Boom 500, Boom 600, Boom 900, Crash 150, Crash 500 (from `config.SYMBOLS`). The list is a setting, so forex or gold can be added later without code changes. |
| D2 | Architecture | A **separate process** (`smc_bot.py`) next to `main.py`. An SMC bug cannot crash the EMA bot, each restarts on its own, `main.py` stays almost untouched. |
| D3 | EMA bot | **CHANGED by the owner:** the EMA bot is **stopped** when the SMC bot goes up. It stays in the repository, untouched, and is not run in parallel. Its history stays in the CSV as `EMA_M5`. No edit to `main.py`, `trader.py`, `reporter.py` or `notifier.py` is needed. |
| D4 | Risk per SMC trade | Target **1.00 $** (0.01% of the 10,000 $ demo). Skip the signal if the minimum lot already risks more than **2.50 $**. |
| D5 | Limits | 1 SMC position per symbol; 4 open at once; 3 new entries per day; pause until Monday after **-4R** in a week; time stop at **24 h**. |
| D6 | Where to build | **Done:** branch `feature/smc-live` exists. The owner checks it out (the guard blocks that git command for Claude). Merge into `main` only after the tests pass. |
| D7 | Guard | The hook blocks edits outside `backtest/`. **Replace it by "guard v2"**, which also allows the new paths (`techniques/`, `smc_live/`, `smc_tests/`, `smc_bot.py`) and keeps `main.py`, `config.py`, `strategy.py`, `trader.py`, `notifier.py`, `reporter.py` and `.env` protected. Only the owner can edit it. |
| D8 | Overlap | When two techniques signal on the same symbol at the same time, the first one trades and the other is logged as `skipped: symbol_busy`. Skipped signals keep their entry/SL/TP so I can replay them offline and compare the techniques fairly. |

## 4. The three techniques (full text goes in `techniques/SETUPS.md`)

Common frame: H4 gives the **bias** (direction of the last break of structure), H1 gives the **zone**, M15 gives the
**trigger**. The scan runs on every M15 close. Entry is a market order on the trigger candle's close.

**A, `SMC_A_OB_TREND`: trend continuation at an H1 order block.**
H4 bias up (down). An H1 order block created by a break in that direction, not touched yet (within 48 H1 candles).
Trigger: price touches the zone and an M15 candle then closes back out of it in the bias direction (within 4 M15
candles of the touch). SL: beyond the zone's far edge plus 0.25 x H1 ATR. TP: 2R. Skip if the next H4 swing is closer
than 1.5R (no room).

**B, `SMC_B_SWEEP_REV`: liquidity sweep and reverse.**
A candle (M15 or H1) wicks through a liquidity level and closes back inside. Levels: the previous server-day high or
low, equal highs/lows (two H1 swings within 0.15 x ATR), the 20-candle H1 range extreme. Trigger: within 12 M15 candles
an M15 candle closes beyond the last M15 swing in the opposite direction (structure shift). SL: beyond the sweep wick
plus a small buffer. TP: 3R.

**C, `SMC_C_PD_OB_FVG`: A with the strictest filters.**
Same as A, plus: buys only in the **discount** half of the H4 range (below 50%), sells only in the **premium** half, and
the H1 order block's leg must contain a fair value gap. TP: the opposite H4 range extreme if it is at least 2R away
(capped at 4R), otherwise skip.

Rules shared by all: minimum stop distance = (broker stops level + spread) x 1.2; skip when the spread is above 25% of
the stop; skip while a major spike candle (range above 8 x median) is forming on M15; no entry in the first 5 minutes
after a restart.

## 5. Code structure

New files, all at the repository root so the live process can import them. Nothing under `backtest/` is imported by live
code, and the backtest side can import `techniques/` read-only for parity tests.

```
techniques/                      pure logic: no MT5, no files, no network (fully unit-testable)
  base.py                        Signal (dataclass) and Technique (interface)
  structure.py                   swings, structure breaks, order blocks, fair value gaps, sweeps, premium/discount
  setup_a_ob_trend.py
  setup_b_sweep_reversal.py
  setup_c_pd_ob_fvg.py
  registry.py                    the list of active techniques
  SETUPS.md                      the three techniques, in words (the document you asked for)

smc_live/                        impure glue
  config_smc.py                  all settings (symbols, risk, caps, flags, magic numbers)
  data_feed.py                   H4/H1/M15 candles from MT5, detects a newly closed M15 candle
  risk.py                        lot size, minimum-lot check, caps, weekly -R breaker, spread guard
  executor.py                    market order with SL/TP, retcodes (10027, 10016, 10036), refusal back-off
  position_monitor.py            non-blocking: follows open SMC positions, detects closes, applies the 24 h time stop
  notify.py                      Telegram messages: signal, execution, close, alerts (send only, never polls)
  smc_report.py                  daily and weekly summaries per technique
  tradelog.py                    all CSV writing, header migration, file lock
  state.json                     signal ids already handled (survives restarts), weekly counters

smc_bot.py                       entry point: connect, check Algo Trading, run the loop
smc_tests/                       tests for techniques/ and smc_live/ (hand-built cases + look-ahead checks)
```

**Signal.** One object with: `signal_id`, `technique`, `symbol`, `direction`, `trigger_time`, `entry_ref`, `sl`, `tp`,
`planned_rr`, `zone_lo`, `zone_hi`, `bias_dir`, `notes`. A technique only returns Signals. It never touches MT5.

**How the techniques live together.** On each new M15 candle, for each symbol: `data_feed` gives the candles, the
registry runs A, B and C on the same snapshot, and the results go through one pipeline: dedupe by `signal_id` ->
filters -> risk -> log -> Telegram "SIGNAL" -> market order -> log -> Telegram "EXECUTED". Each technique has its own MT5
magic number (A 223401, B 223402, C 223403; the EMA bot keeps 123456) and a comment `smcA:<id>`, so any position can be
traced back. Adding a fourth technique means adding one file and one line in `registry.py`.

**Position checks.** Before entering, the system looks at **all** positions on the symbol, any magic. The EMA bot
already does the same, so an open SMC position also keeps the EMA bot out of that symbol.

## 6. Telegram messages

1. **Signal:** technique, symbol, BUY/SELL, entry, SL, TP, risk in R and in $, lot, zone, bias.
2. **Execution:** ticket and fill price, or the refusal code and what the system does next.
3. **Close:** result in $ and R, reason (TP, SL, time stop), duration.
4. **Alerts:** Algo Trading off, weekly breaker hit, repeated refusals (one message, then silence).

## 7. CSV changes (for the analysis you want)

`logs/trades.csv`: the 8 existing columns stay in place. Appended: `technique, signal_id, ticket, magic, sl, tp, risk_usd,
planned_rr, r_multiple, exit_reason, hold_min, bias_dir, zone_lo, zone_hi, spread_pts, trigger_tf, notes`.
`logs/orders.csv`: appended `technique, signal_id, ticket, volume, sl, tp`.
`logs/signals.csv` (new): every signal, sent or skipped: `signal_id, time, technique, symbol, direction, trigger_tf,
entry_ref, sl, tp, planned_rr, risk_usd_est, lot_est, zone_lo, zone_hi, bias_dir, status, skip_reason, ticket, notes`.

Migration: the old file is copied to `logs/trades_backup_<date>.csv`, then rewritten with the new header and empty new
fields; old rows get `technique = EMA_M5`. Nothing is deleted.

Edits to existing files: **none.** With the EMA bot stopped (D3), `main.py`, `trader.py`, `reporter.py` and `notifier.py`
stay exactly as they are. The only change to existing data is the CSV migration above (a copy is kept). If the EMA bot is
ever restarted, its rows are written with the 8 old columns and an empty `technique`, which is read as `EMA_M5`.
The SMC system sends its own daily and weekly summaries per technique (`smc_live/smc_report.py`).

## 8. Work plan and gates

| Phase | What | Gate to continue |
|---|---|---|
| P0 | Plan approved (done). Owner: install guard v2 and check out the branch. Algo Trading is switched on later, at P5. | Guard v2 active and the branch checked out. |
| P1 | `techniques/` + `SETUPS.md` + tests: hand-built cases, a look-ahead check on real data, a parity check against the backtest code. | All tests pass. |
| P2 | Replay the techniques on 29 months of history (backtest side). Measure signals per week per technique and the R distribution. Caps are tuned from this, not the rules. | Signals per week are in a workable range; you review the numbers. |
| P3 | `smc_live/` + `smc_bot.py` + CSV migration. One demo test order of 0.2 lot to check what the broker accepts: SL and TP at opening, TP refused or not, SL change refused or not, comment length, fill mode. | The broker test is documented; the plan is adjusted to what it shows. |
| P4 | **Alert-only mode** (no orders) for at least 3 days: Telegram signals and `signals.csv` only. | Messages are right; signal count matches P2; no crashes. |
| P5 | **Execute mode** on the demo account. | Runs for 8 weeks. |
| P6 | A weekly analysis script reads the CSVs: per technique, R, win rate, profit factor, skipped-signal replay. | You decide to keep, change or stop each technique. |

## 9. Limits you should know

- No break-even, trailing or partial exits are possible (point 2). Managing a trade means SL, TP and the 24 h time stop.
- At 4 trades a week, 8 weeks give about 30 trades: enough to check that the system works, not enough to prove an edge.
  The replay of skipped signals and the P2 history are what give statistical weight.
- Holds of hours cross many spikes on Boom/Crash; stops can be jumped and filled at much worse prices (the average
  loss in our backtests was 4 R on these indices).
- Results at P6 are likely to match the research: close to zero or negative.
- The new process uses the same MT5 terminal as the EMA bot. They do not interfere (hedging account), but Algo Trading
  must stay on for both.

## 10. Results of P1 and P2 (18 Oct 2026)

**P1 done.** `techniques/` (A, B, C), `techniques/SETUPS.md`, and `smc_tests/` (22 checks: hand-built cases, identical to
the backtest code on 4,255 order-block zones, signal geometry on real data, no look-ahead by truncation).

**P2 done** (`backtest/smc/tools/replay_live_techniques.py`, report in `backtest/smc/reports/live_replay/`): the live
code replayed on 48 weeks of the bot's six symbols with M5 fills.

1. **The risk numbers of section 3 (D4) do not work.** At the broker's minimum lot, these signals risk **4 to 13 $** per
   trade (median: A 5.2 $, C 5.6 $, B 7.8 $). With a 1 $ target and a 2.50 $ limit, 1,724 of 1,756 signals are rejected
   and nothing would ever trade. Proposed: target 5 $, accepted up to 12 $ (0.05 to 0.12% of the 10,000 $ demo).
2. **Technique B is far too frequent**: 33 signals a week over the six symbols, 12 trades a week under the caps, 90% of all
   trades; it also triggers the weekly -4R breaker 433 times. A and C together give only about 1.4 trades a week.
   Measured alternatives for B (signals a week over six symbols, after the risk limit): as specified 27.7; previous-day
   and equal levels only 17.0; those levels in the H4-bias direction only 4.6; those levels in the bias direction and
   in the matching half of the H4 range 2.5.
3. **Results on history (not significant):** capped trades: C 44 trades +0.20 R average, A 23 trades -0.08 R, B 574
   trades -0.02 R, all 641 trades -6 R in total. Each technique on its own over all signals: C +0.00 R (113), A -0.14 R
   (65), B -0.04 R (1,326). Sample sizes are small and the differences are within chance.
