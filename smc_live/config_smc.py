"""All settings of the SMC system in one place. Change values here, not in the code.

Decisions behind these values: backtest/smc/docs/LIVE_SMC_BUILD_PLAN.md (sections 3, 10 and 11).
"""
import os

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# --- instruments: the six the EMA bot traded (kept here, not imported, so the two systems stay independent)
SYMBOLS = ["Boom 150 Index", "Boom 500 Index", "Boom 600 Index", "Boom 900 Index", "Crash 150 Index", "Crash 500 Index"]

# --- techniques
MAGIC = {"SMC_A_OB_TREND": 223401, "SMC_B_SWEEP_REV": 223402, "SMC_C_PD_OB_FVG": 223403}
LETTER = {"SMC_A_OB_TREND": "A", "SMC_B_SWEEP_REV": "B", "SMC_C_PD_OB_FVG": "C"}
SHORT_TITLE = {"SMC_A_OB_TREND": "A: tendance + order block H1",
               "SMC_B_SWEEP_REV": "B: balayage de liquidité + retournement",
               "SMC_C_PD_OB_FVG": "C: order block + FVG, zone premium/discount"}

# --- execution mode. Default is ALERT-ONLY (Telegram + CSV, no order). Orders need --execute (or SMC_EXECUTE=1).
EXECUTE = os.getenv("SMC_EXECUTE", "0") == "1"
DEVIATION = 50                    # points of slippage accepted by the broker
FILLING = "FOK"                   # the only filling mode accepted on Deriv indices

# --- risk per trade (dollars) at the broker's minimum lot, see the plan, section 10
RISK_USD = 5.0                    # target
MAX_RISK_USD = 12.0               # skip the signal if even the minimum lot risks more than this
MIN_STOP_FACTOR = 1.2             # stop must be at least (stops level + spread) x 1.2 away
SPREAD_MAX_FRAC = 0.25            # skip if the spread is more than 25% of the stop distance
MAX_SLIPPAGE_FRAC = 0.5           # skip if the live price moved more than half a stop since the trigger close
HOLD_HOURS = 24                   # time stop

# --- limits. Each technique has its own budget so that a frequent one cannot starve the others.
MAX_OPEN_TOTAL = 4
MAX_OPEN_PER_SYMBOL = 1           # counted over ALL positions on the symbol, whatever their magic number
MAX_PER_DAY = {"SMC_A_OB_TREND": 2, "SMC_C_PD_OB_FVG": 2, "SMC_B_SWEEP_REV": 3}
WEEKLY_BREAKER_R = -4.0           # per technique: no new entry after this many R lost in the ISO week

# --- data
CANDLES = {"M15": 1500, "H1": 600, "H4": 300}      # closed candles requested per scan
STALE_AFTER_MIN = 20              # a signal older than this (bot was down) is not traded

# --- timing
LOOP_SECONDS = 5
HEARTBEAT_MIN = 60
DAILY_REPORT_HOUR = 23            # local time

# --- files
LOG_DIR = os.path.join(ROOT, "logs")
STATE_PATH = os.path.join(ROOT, "smc_live", "state.json")
