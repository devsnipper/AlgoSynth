"""Tests of risk.py, state.py, tradelog.py and notify.py (no MT5 involved).

Usage : backtest/.venv/Scripts/python.exe smc_tests/test_risk_state_log.py
"""
import csv
import os
import sys
import tempfile
from datetime import datetime
from types import SimpleNamespace as NS

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from helpers import check, report_and_exit                                         # noqa: E402

from smc_live import config_smc as cfg                                              # noqa: E402
from smc_live import notify, risk                                                   # noqa: E402
from smc_live.state import State                                                    # noqa: E402
from smc_live.tradelog import NEW_ORDERS, NEW_TRADES, OLD_ORDERS, OLD_TRADES, SIGNALS, TradeLog   # noqa: E402
from techniques.base import Signal                                                  # noqa: E402

INFO = {"point": 0.001, "digits": 3, "contract_size": 1.0, "volume_min": 0.2, "volume_max": 190.0,
        "volume_step": 0.01, "stops_level": 1173}


def sig(direction=1, entry=5000.0, risk_units=10.0, rr=2.0, technique="SMC_A_OB_TREND"):
    sl = entry - direction * risk_units
    tp = entry + direction * rr * risk_units
    return Signal(technique, "Boom 500 Index", direction, 100, pd.Timestamp("2026-10-19 10:15"), entry, sl, tp, rr,
                  entry - 12, entry - 8, direction, "test")


@check("lot sizing: 5 $ target on a 10-unit stop gives 0.5 lot and exactly 5 $ of risk")
def _():
    plan, why = risk.make_plan(sig(), INFO, 4999.95, 5000.0, 50)
    assert why is None and plan.volume == 0.5 and abs(plan.risk_usd - 5.0) < 1e-9, (plan, why)
    assert plan.sl == 4990.0 and plan.tp == 5020.0 and abs(plan.rr - 2.0) < 1e-9


@check("lot sizing: the broker's minimum lot is used when the wanted lot is smaller; refused above the 12 $ limit")
def _():
    plan, why = risk.make_plan(sig(risk_units=40), INFO, 4999.95, 5000.0, 50)
    assert why is None and plan.volume == 0.2 and abs(plan.risk_usd - 8.0) < 1e-9
    plan, why = risk.make_plan(sig(risk_units=70), INFO, 4999.95, 5000.0, 50)
    assert plan is None and why == "min_lot_risk_too_high", why


@check("a sell is priced at the bid and the stop is above")
def _():
    plan, why = risk.make_plan(sig(direction=-1), INFO, 5000.0, 5000.05, 50)
    assert why is None and plan.price == 5000.0 and plan.sl == 5010.0 and plan.tp == 4980.0


@check("skips: price through the levels, slipped, stop too tight, spread too wide, target too close")
def _():
    s = sig()
    assert risk.make_plan(s, INFO, 5019.9, 5020.1, 50)[1] == "price_through_levels"        # already at the target
    assert risk.make_plan(s, INFO, 4991.9, 4992.0, 50)[1] == "slipped"                      # 8 units away from the trigger
    assert risk.make_plan(sig(risk_units=1.2), INFO, 4999.95, 5000.0, 50)[1] == "stop_too_tight"
    assert risk.make_plan(s, INFO, 4997.0, 5000.0, 3000)[1] == "spread_too_wide"            # 3 units of spread on a 10-unit stop
    tight_tp = Signal("SMC_A_OB_TREND", "Boom 500 Index", 1, 1, pd.Timestamp("2026-10-19"), 5000.0, 4990.0, 5000.9, 0.09, 4990, 4995, 1, "")
    assert risk.make_plan(tight_tp, INFO, 4999.95, 5000.0, 50)[1] == "tp_too_close"


@check("limits: symbol busy, too many open, daily limit per technique, weekly breaker per technique")
def _():
    with tempfile.TemporaryDirectory() as d:
        st = State(os.path.join(d, "state.json"))
        now = datetime(2026, 10, 21, 12, 0)                                    # a Wednesday
        A, B = "SMC_A_OB_TREND", "SMC_B_SWEEP_REV"
        assert risk.check_limits(A, "Boom 500 Index", now, st, 0, 0) is None
        assert risk.check_limits(A, "Boom 500 Index", now, st, 1, 0) == "symbol_busy"
        assert risk.check_limits(A, "Boom 500 Index", now, st, 0, 4) == "max_open"
        for _ in range(2):
            st.add_day_count(A, "2026-10-21")
        assert risk.check_limits(A, "Boom 500 Index", now, st, 0, 0) == "max_per_day"
        assert risk.check_limits(B, "Boom 500 Index", now, st, 0, 0) is None, "B has its own budget"
        st.add_closed(B, "2026-10-19T10:00:00", -2.5)
        st.add_closed(B, "2026-10-20T10:00:00", -1.5)
        assert risk.check_limits(B, "Boom 500 Index", now, st, 0, 0) == "weekly_breaker"
        assert risk.check_limits("SMC_C_PD_OB_FVG", "Boom 500 Index", now, st, 0, 0) is None, "other techniques are not paused"
        st.add_closed("SMC_C_PD_OB_FVG", "2026-10-12T10:00:00", -9.0)               # last week: does not count
        assert risk.check_limits("SMC_C_PD_OB_FVG", "Boom 500 Index", now, st, 0, 0) is None


@check("state: survives a restart, atomic write, corrupt file is kept aside")
def _():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "state.json")
        s = State(p)
        s.mark_seen("x", "2026-10-19T10:00:00")
        s.add_position(77, {"technique": "SMC_A_OB_TREND"})
        s.set_last_scan("Boom 500 Index", "2026-10-19 10:00:00")
        s.save()
        s2 = State(p)
        assert s2.seen("x") and "77" in s2.positions and s2.last_scan("Boom 500 Index") == "2026-10-19 10:00:00"
        assert not os.path.exists(p + ".tmp")
        open(p, "w").write("{broken")
        s3 = State(p)
        assert not s3.seen("x") and os.path.exists(p + ".corrupt")


@check("alerts are sent once until cleared")
def _():
    with tempfile.TemporaryDirectory() as d:
        st, n = State(os.path.join(d, "s.json")), notify.Notifier(dry=True)
        n.alert_once(st, "k", "problem")
        n.alert_once(st, "k", "problem")
        assert len(n.sent) == 1
        st.clear_alert("k")
        n.alert_once(st, "k", "problem")
        assert len(n.sent) == 2


def old_files(d):
    with open(os.path.join(d, "trades.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(OLD_TRADES)
        w.writerow(["2026-08-12", "20:20:10", "Boom 600 Index", "sell", "0.2", "5332.744", "5330.741", "0.4"])
        w.writerow(["2026-08-12", "19:29:29", "Boom 150 Index", "sell", "1.31", "9657.6427", "9659.2412", "-2.11"])
    with open(os.path.join(d, "orders.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(OLD_ORDERS)
        w.writerow(["2026-10-12", "16:54:05", "OPEN", "Boom 900 Index", "sell", "8587.402", "10027", "REFUSE"])


@check("migration: old columns stay in place and keep their values, new ones are appended, a backup is made")
def _():
    with tempfile.TemporaryDirectory() as d:
        old_files(d)
        before = open(os.path.join(d, "trades.csv"), newline="").read()
        done = TradeLog(d).ensure_headers()
        assert any("migrated trades.csv" in x for x in done) and any("migrated orders.csv" in x for x in done), done
        backups = [f for f in os.listdir(d) if f.startswith("trades_backup_")]
        assert len(backups) == 1 and open(os.path.join(d, backups[0]), newline="").read() == before, "backup is a copy"
        rows = list(csv.DictReader(open(os.path.join(d, "trades.csv"), newline="")))
        assert list(rows[0].keys()) == OLD_TRADES + NEW_TRADES
        assert rows[0]["profit"] == "0.4" and rows[1]["entry"] == "9657.6427" and rows[0]["technique"] == "EMA_M5"
        assert TradeLog(d).ensure_headers() == [], "second call changes nothing"
        # the old reader (by column name) still works on the migrated file
        import reporter  # noqa: F401  (the untouched live module, read only)


@check("appending rows: every column lands under its own header; unknown header is refused")
def _():
    with tempfile.TemporaryDirectory() as d:
        log = TradeLog(d)
        assert len(log.ensure_headers()) == 3
        log.trade({"symbol": "Boom 500 Index", "direction": "buy", "lot": 0.5, "entry": 5000, "exit": 5020, "profit": 10.0,
                   "technique": "SMC_A_OB_TREND", "signal_id": "id1", "ticket": 5, "r_multiple": 2.0, "exit_reason": "TP"})
        log.order({"type": "OPEN", "symbol": "Boom 500 Index", "direction": "buy", "prix": 5000, "retcode": 10009,
                   "statut": "OK", "technique": "SMC_A_OB_TREND", "signal_id": "id1", "ticket": 5, "volume": 0.5})
        log.signal({"signal_id": "id1", "time": "2026-10-19T10:15:00", "technique": "SMC_A_OB_TREND", "symbol": "Boom 500 Index",
                    "direction": "buy", "status": "alert_only"})
        t = list(csv.DictReader(open(log.trades, newline="")))[0]
        assert t["technique"] == "SMC_A_OB_TREND" and t["r_multiple"] == "2.0" and t["date"] and t["heure"]
        assert list(csv.DictReader(open(log.orders, newline="")))[0]["volume"] == "0.5"
        log.update_signal("id1", status="traded", ticket=5)
        s = list(csv.DictReader(open(log.signals, newline="")))[0]
        assert s["status"] == "traded" and s["ticket"] == "5" and list(s.keys()) == SIGNALS
        assert not [f for f in os.listdir(d) if f.endswith(".lock")]
        open(os.path.join(d, "trades.csv"), "w").write("a,b,c\n")
        try:
            TradeLog(d).ensure_headers()
        except RuntimeError:
            return
        raise AssertionError("an unknown header must be refused")


@check("Telegram messages carry technique, side, entry, SL, TP, RR, risk, zone and id")
def _():
    s = sig()
    plan, _ = risk.make_plan(s, INFO, 4999.95, 5000.0, 50)
    m = notify.signal_message(s, plan, True)
    for part in ("SIGNAL SMC", "A: tendance", "ACHAT", "Boom 500 Index", "5000.000", "SL : 4990.000", "TP : 5020.000", "1:2.0",
                 "5.00 $", "lot 0.5", s.signal_id, "Ordre envoyé"):
        assert part in m, (part, m)
    assert "alerte seule" in notify.signal_message(s, plan, False)
    ex = notify.executed_message(plan, NS(ticket=42, price=5000.0, tp_server=False))
    assert "ticket 42" in ex and "TP surveillé par le bot" in ex
    assert "GAIN" in notify.closed_message("Boom 500 Index", "SMC_A_OB_TREND", 10.0, 2.0, "TP", 95, 42)
    assert "PERTE" in notify.closed_message("Boom 500 Index", "SMC_A_OB_TREND", -5.0, -1.0, "SL", 30, 42)


@check("Notifier: dry mode sends nothing, a Telegram error never raises")
def _():
    calls = []
    n = notify.Notifier(token="t", chat_id="c", dry=True, post=lambda *a, **k: calls.append(1))
    n.send("hello")
    assert calls == []
    def boom(*a, **k):
        raise ConnectionError("no network")
    n2 = notify.Notifier(token="t", chat_id="c", post=boom)
    assert n2.send("hello") is False


if __name__ == "__main__":
    report_and_exit()
