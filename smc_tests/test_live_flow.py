"""Tests of the live flow with a fake terminal: data feed, executor, position monitor and the whole pipeline.

Usage : .venv/Scripts/python.exe smc_tests/test_live_flow.py
"""
import csv
import os
import sys
import tempfile
from datetime import datetime, timedelta
from types import SimpleNamespace as NS

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fake_mt5 import BOOM500, FakeMT5, rates_from_frame                             # noqa: E402
from helpers import check, have_data, real_snapshot, report_and_exit                # noqa: E402

from smc_live import config_smc as cfg                                              # noqa: E402
from smc_live import data_feed, notify, risk                                        # noqa: E402
from smc_live.executor import Executor                                              # noqa: E402
from smc_live.pipeline import Pipeline                                              # noqa: E402
from smc_live.position_monitor import Monitor                                       # noqa: E402
from smc_live.state import State                                                    # noqa: E402
from smc_live.tradelog import TradeLog                                              # noqa: E402
from techniques import registry                                                     # noqa: E402

SYMBOL = "Boom 500 Index"
EPOCH = 1_760_000_000


def rig(execute=True, tmp=None, script=None, bid=5000.0, ask=5000.05):
    """A complete system on a fake terminal with temporary files."""
    d = tmp or tempfile.mkdtemp()
    mt5 = FakeMT5(bid, ask, now_epoch=EPOCH)
    mt5.script = list(script or [])
    log = TradeLog(d)
    log.ensure_headers()
    state = State(os.path.join(d, "state.json"))
    notifier = notify.Notifier(dry=True)
    executor = Executor(mt5, execute, sleep=lambda s: None)
    monitor = Monitor(mt5, state, log, notifier, executor)
    pipe = Pipeline(mt5, state, log, notifier, executor, monitor, execute)
    return NS(mt5=mt5, log=log, state=state, n=notifier, ex=executor, mon=monitor, pipe=pipe, dir=d)


def rows(path):
    return list(csv.DictReader(open(path, newline="", encoding="utf-8")))


def a_real_signal_scenario():
    """A real signal on real data: returns (snapshot cut at its trigger candle, the signal, a price pair that passes risk)."""
    full = real_snapshot("Boom 500 Index")
    for tech in registry.ACTIVE:
        for s in tech.signals(full):
            if s.trigger_idx < 2000:
                continue
            bid = s.entry_ref - 0.025
            ask = s.entry_ref + 0.025
            info = {"point": 0.001, "digits": 3, "contract_size": 1.0, "volume_min": 0.2, "volume_max": 190.0,
                    "volume_step": 0.01, "stops_level": 1173}
            plan, why = risk.make_plan(s, info, bid, ask, 50)
            if why is None:
                return real_snapshot("Boom 500 Index", first_n=s.trigger_idx + 1), s, (bid, ask)
    raise AssertionError("no usable real signal found")


# ---------------------------------------------------------------- data feed
@check("data feed: the forming candle is never included and the requested number of closed candles comes back")
def _():
    full = real_snapshot(SYMBOL)
    mt5 = FakeMT5()
    mt5.rates[(SYMBOL, mt5.TIMEFRAME_M15)] = rates_from_frame(full.m15.iloc[-2000:])
    mt5.rates[(SYMBOL, mt5.TIMEFRAME_H1)] = rates_from_frame(full.h1.iloc[-800:])
    mt5.rates[(SYMBOL, mt5.TIMEFRAME_H4)] = rates_from_frame(full.h4.iloc[-400:])
    snap = data_feed.fetch_snapshot(mt5, SYMBOL)
    assert len(snap.m15) == cfg.CANDLES["M15"] and len(snap.h1) == cfg.CANDLES["H1"] and len(snap.h4) == cfg.CANDLES["H4"]
    assert snap.m15["time"].iloc[-1] == full.m15["time"].iloc[-1], "last candle is the last CLOSED one"
    assert data_feed.last_closed_m15(mt5, SYMBOL) == full.m15["time"].iloc[-1]
    assert snap.point == 0.001 and snap.stops_level == 1173
    assert data_feed.server_now(mt5, SYMBOL) == datetime(2025, 10, 9, 8, 53, 20)


# ---------------------------------------------------------------- executor
def plan_for(direction=1):
    from types import SimpleNamespace
    return risk.make_plan(
        __import__("smc_tests.test_risk_state_log", fromlist=["sig"]).sig(direction), BOOM500_INFO, 4999.95, 5000.0, 50)[0]


BOOM500_INFO = {"point": 0.001, "digits": 3, "contract_size": 1.0, "volume_min": 0.2, "volume_max": 190.0,
                "volume_step": 0.01, "stops_level": 1173}


def a_plan(direction=1):
    from techniques.base import Signal
    e = 5000.0
    s = Signal("SMC_A_OB_TREND", SYMBOL, direction, 5, pd.Timestamp("2026-10-19 10:15"), e, e - 10 * direction,
               e + 20 * direction, 2.0, e - 12, e - 8, direction, "t")
    return risk.make_plan(s, BOOM500_INFO, 4999.95, 5000.0, 50)[0]


@check("executor: a normal order carries SL, TP, the technique's magic number, FOK filling and a traceable comment")
def _():
    r = rig()
    res = r.ex.open(a_plan())
    req = r.mt5.sent[0]
    assert res.ok and res.tp_server and res.ticket == 1000
    assert req["sl"] == 4990.0 and req["tp"] == 5020.0 and req["magic"] == 223401 and req["type_filling"] == 0
    assert req["comment"].startswith("smcA:") and len(req["comment"]) <= 31 and req["deviation"] == 50


@check("executor: if the broker refuses the TP at opening (10016) the order is sent again with the SL only")
def _():
    r = rig(script=[10016])
    res = r.ex.open(a_plan())
    assert res.ok and not res.tp_server and len(r.mt5.sent) == 2 and "tp" in r.mt5.sent[0] and "tp" not in r.mt5.sent[1]


@check("executor: Algo Trading off (10027) is reported, not retried")
def _():
    r = rig(script=[10027])
    res = r.ex.open(a_plan())
    assert not res.ok and res.algo_disabled and len(r.mt5.sent) == 1


@check("executor: too many requests (10036) waits and retries; unknown refusals are not retried forever")
def _():
    r = rig(script=[10036, 10009])
    assert r.ex.open(a_plan()).ok and len(r.mt5.sent) == 2
    r = rig(script=[10013])
    res = r.ex.open(a_plan())
    assert not res.ok and res.retcode == 10013 and len(r.mt5.sent) == 1


@check("executor: alert-only mode sends nothing")
def _():
    r = rig(execute=False)
    res = r.ex.open(a_plan())
    assert not res.ok and not res.sent and r.mt5.sent == []


@check("executor: order_check asks the broker without sending an order")
def _():
    r = rig()
    ok, code, _ = r.ex.check(a_plan())
    assert ok and len(r.mt5.checked) == 1 and r.mt5.sent == []


# ---------------------------------------------------------------- pipeline
@check("pipeline, execute mode: SIGNAL message first, then the order, then EXECUTED; rows in all three CSV files")
def _():
    snap, sig, (bid, ask) = a_real_signal_scenario()
    r = rig(bid=bid, ask=ask)
    now = sig.trigger_time.to_pydatetime() + timedelta(minutes=1)
    out = r.pipe.scan(snap, now)
    traded = [o for o in out if o["status"] == "traded"]
    assert len(traded) == 1, out
    texts = r.n.sent
    assert texts[0].startswith("📡 SIGNAL SMC") and texts[1].startswith("✅ ORDRE EXÉCUTÉ"), [t[:20] for t in texts]
    assert len(r.mt5.sent) == 1 and r.mt5.sent[0]["magic"] == cfg.MAGIC[sig.technique]
    o = rows(r.log.orders)[0]
    assert o["technique"] == sig.technique and o["signal_id"] == sig.signal_id and o["statut"] == "OK" and o["ticket"] == "1000"
    sg = [x for x in rows(r.log.signals) if x["signal_id"] == sig.signal_id][0]
    assert sg["status"] == "traded" and sg["ticket"] == "1000" and sg["sl"] and sg["tp"]
    assert "1000" in r.state.positions and r.state.day_count(sig.technique, now.date().isoformat()) == 1
    assert r.pipe.scan(snap, now + timedelta(seconds=30))[0]["status"] == "duplicate", "the same signal never trades twice"
    assert len(r.mt5.sent) == 1


@check("pipeline, alert-only mode: the SIGNAL message and a CSV row, but no order")
def _():
    snap, sig, (bid, ask) = a_real_signal_scenario()
    r = rig(execute=False, bid=bid, ask=ask)
    out = r.pipe.scan(snap, sig.trigger_time.to_pydatetime() + timedelta(minutes=1))
    assert [o["status"] for o in out if o["signal_id"] == sig.signal_id] == ["alert_only"]
    assert r.mt5.sent == [] and r.n.sent[0].startswith("📡 SIGNAL SMC") and "alerte seule" in r.n.sent[0]
    assert [x["status"] for x in rows(r.log.signals) if x["signal_id"] == sig.signal_id] == ["alert_only"]


@check("pipeline: a stale signal (bot was down), a slipped price and a busy symbol are logged as skipped with a reason")
def _():
    snap, sig, (bid, ask) = a_real_signal_scenario()
    r = rig(bid=bid, ask=ask)
    out = r.pipe.scan(snap, sig.trigger_time.to_pydatetime() + timedelta(hours=2))
    assert out[0]["reason"] == "stale" and r.mt5.sent == []
    r = rig(bid=bid + 50, ask=ask + 50)
    assert r.pipe.scan(snap, sig.trigger_time.to_pydatetime() + timedelta(minutes=1))[0]["reason"] in ("slipped", "price_through_levels")
    r = rig(bid=bid, ask=ask)
    r.mt5.positions.append(NS(ticket=5, symbol=SYMBOL, magic=123456, volume=0.2, type=0, price_open=1.0, sl=0, tp=0, time=EPOCH))
    out = r.pipe.scan(snap, sig.trigger_time.to_pydatetime() + timedelta(minutes=1))
    assert out[0]["reason"] == "symbol_busy", "positions of the old bot (another magic number) count too"
    assert r.mt5.sent == [] and r.n.sent == []
    assert rows(r.log.signals)[0]["status"] == "skipped" and rows(r.log.signals)[0]["skip_reason"] == "symbol_busy"


@check("pipeline: Algo Trading off is announced once, whatever the number of signals")
def _():
    snap, sig, (bid, ask) = a_real_signal_scenario()
    r = rig(bid=bid, ask=ask, script=[10027, 10027])
    r.pipe.scan(snap, sig.trigger_time.to_pydatetime() + timedelta(minutes=1))
    assert sum("Algo Trading" in t for t in r.n.sent) == 1
    r.state.data["processed"].clear()
    r.pipe.scan(snap, sig.trigger_time.to_pydatetime() + timedelta(minutes=2))
    assert sum("Algo Trading" in t for t in r.n.sent) == 1, "no repeat"
    assert [x["status"] for x in rows(r.log.signals)] == ["refused", "refused"]


# ---------------------------------------------------------------- position monitor
def open_one(r, **kw):
    snap, sig, (bid, ask) = a_real_signal_scenario()
    r.mt5.tick.bid, r.mt5.tick.ask = bid, ask
    now = sig.trigger_time.to_pydatetime() + timedelta(minutes=1)
    r.pipe.scan(snap, now)
    return sig, now, r.mt5.positions[0]


@check("monitor: a position closed by its stop is written to trades.csv with the technique, R, reason and duration")
def _():
    r = rig()
    sig, now, pos = open_one(r)
    info = r.state.positions[str(pos.ticket)]
    stop_price = pos.sl
    r.mt5.close_position(pos.ticket, stop_price, r.mt5.DEAL_REASON_SL, profit=-5.1, epoch=EPOCH + 3600)
    r.mon.sync(now + timedelta(hours=1))
    t = rows(r.log.trades)[0]
    assert t["technique"] == sig.technique and t["signal_id"] == sig.signal_id and t["exit_reason"] == "SL"
    assert float(t["profit"]) == -5.1 and abs(float(t["r_multiple"]) - (-1.0)) < 0.01 and t["ticket"] == str(pos.ticket)
    assert t["sl"] and t["tp"] and t["risk_usd"] and t["planned_rr"] and int(t["hold_min"]) >= 0
    assert r.state.positions == {} and r.state.data["closed"][0]["technique"] == sig.technique
    assert r.n.sent[-1].startswith("❌ TRADE FERMÉ")


@check("monitor: take profit closes with a gain; the history not being ready yet is retried, not lost")
def _():
    r = rig()
    sig, now, pos = open_one(r)
    r.mt5.positions = []                                            # closed, but the deal history is not available yet
    r.mon.sync(now + timedelta(minutes=5))
    assert rows(r.log.trades) == [] and str(pos.ticket) in r.state.positions, "kept for the next call"
    r.mt5.deals[pos.ticket] = [NS(entry=0, price=pos.price_open, profit=0, commission=0, swap=0, reason=3, time=EPOCH),
                               NS(entry=1, price=pos.tp, profit=10.4, commission=0, swap=0, reason=r.mt5.DEAL_REASON_TP, time=EPOCH + 600)]
    r.mon.sync(now + timedelta(minutes=10))
    t = rows(r.log.trades)[0]
    assert t["exit_reason"] == "TP" and float(t["profit"]) == 10.4 and float(t["r_multiple"]) > 1.5
    assert r.n.sent[-1].startswith("✅ TRADE FERMÉ")


@check("monitor: the 24 h time stop closes the position and is recorded as TIME")
def _():
    r = rig()
    sig, now, pos = open_one(r)
    r.mon.sync(now + timedelta(hours=23))
    assert len(r.mt5.sent) == 1, "not yet"
    r.mon.sync(now + timedelta(hours=24, minutes=1))
    assert len(r.mt5.sent) == 2 and r.mt5.sent[1]["position"] == pos.ticket and r.mt5.sent[1]["comment"].startswith("smc-close")
    r.mt5.close_position(pos.ticket, pos.price_open, r.mt5.DEAL_REASON_EXPERT, profit=0.3, epoch=EPOCH + 90000)
    r.mon.sync(now + timedelta(hours=24, minutes=2))
    assert rows(r.log.trades)[0]["exit_reason"] == "TIME"


@check("monitor: a position whose TP could not be placed on the server is closed by the bot when the TP is reached")
def _():
    r = rig(script=[10016])
    sig, now, pos = open_one(r)
    assert r.state.positions[str(pos.ticket)]["tp_server"] is False and pos.tp == 0.0
    tp = r.state.positions[str(pos.ticket)]["tp"]
    d = r.state.positions[str(pos.ticket)]["direction"]
    r.mt5.tick.bid, r.mt5.tick.ask = (tp + 0.1, tp + 0.2) if d == 1 else (tp - 0.2, tp - 0.1)
    r.mon.sync(now + timedelta(minutes=30))
    # sent: [0] refused order with TP, [1] the order again with the SL only, [2] the bot's market close
    assert len(r.mt5.sent) == 3 and r.mt5.sent[2]["position"] == pos.ticket
    assert r.state.positions[str(pos.ticket)]["closing_reason"] == "TP"


@check("monitor: an SMC position unknown to the state (after a crash) is adopted, others' positions are ignored")
def _():
    r = rig()
    r.mt5.positions.append(NS(ticket=900, symbol=SYMBOL, magic=223402, volume=0.2, type=0, price_open=5000.0, sl=4990.0, tp=5030.0, time=EPOCH))
    r.mt5.positions.append(NS(ticket=901, symbol="Crash 500 Index", magic=123456, volume=0.2, type=1, price_open=3000.0, sl=0, tp=0, time=EPOCH))
    r.mon.sync(datetime(2025, 10, 9, 9, 0))
    assert list(r.state.positions) == ["900"] and r.state.positions["900"]["technique"] == "SMC_B_SWEEP_REV"
    assert any("reprise en charge" in t for t in r.n.sent)


@check("the weekly breaker uses closed results written by the monitor")
def _():
    r = rig()
    now = datetime(2026, 10, 21, 12, 0)
    r.state.add_closed("SMC_B_SWEEP_REV", "2026-10-20T08:00:00", -4.2)
    assert risk.check_limits("SMC_B_SWEEP_REV", SYMBOL, now, r.state, 0, 0) == "weekly_breaker"


if __name__ == "__main__":
    report_and_exit()
