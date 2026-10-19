"""What happens to a signal, in order (this is the whole decision chain of the live system):

  duplicate? -> stale? -> mark as handled -> live price and spread -> spike candle? -> risk plan (lot, stop, target)
  -> limits -> Telegram SIGNAL -> market order (execute mode) -> Telegram result -> CSV rows -> state

Every signal, traded or not, ends up as one row of signals.csv with a status and a reason.
"""
from datetime import datetime

from smc_live import config_smc as cfg
from smc_live import data_feed, notify, risk
from techniques import registry
from techniques import structure as st


class Pipeline:
    def __init__(self, mt5, state, log, notifier, executor, monitor, execute: bool, techniques=None):
        self.mt5, self.state, self.log, self.notifier = mt5, state, log, notifier
        self.executor, self.monitor, self.execute = executor, monitor, execute
        self.techniques = techniques if techniques is not None else registry.ACTIVE

    def scan(self, snap, now: datetime) -> list:
        """Signals whose trigger is the latest closed M15 candle of the snapshot. Returns one outcome dict per signal."""
        last = len(snap.m15) - 1
        rank = {t.name: i for i, t in enumerate(self.techniques)}
        sigs = [s for t in self.techniques for s in t.signals(snap) if s.trigger_idx == last]
        sigs.sort(key=lambda s: rank[s.technique])                # strictest technique first (C, A, B)
        spike = bool(st.spike_flags(snap.m15["high"].to_numpy(float), snap.m15["low"].to_numpy(float))[last])
        return [self._handle(s, now, spike) for s in sigs]

    # ------------------------------------------------------------------
    def _row(self, s, status, reason="", plan=None, ticket=None):
        return {"signal_id": s.signal_id, "time": s.trigger_time.isoformat(), "technique": s.technique, "symbol": s.symbol,
                "direction": "buy" if s.direction == 1 else "sell", "trigger_tf": "M15", "entry_ref": s.entry_ref,
                "sl": s.sl, "tp": s.tp, "planned_rr": round(s.rr, 3),
                "risk_usd_est": round(plan.risk_usd, 2) if plan else "", "lot_est": plan.volume if plan else "",
                "zone_lo": s.zone_lo, "zone_hi": s.zone_hi, "bias_dir": s.bias_dir, "status": status,
                "skip_reason": reason, "ticket": ticket or "", "notes": s.notes}

    def _handle(self, s, now: datetime, spike: bool) -> dict:
        if self.state.seen(s.signal_id):
            return {"signal_id": s.signal_id, "status": "duplicate"}
        self.state.mark_seen(s.signal_id, now.isoformat())
        self.state.save()                                          # before anything else: a crash must never repeat an order

        def skip(reason, plan=None):
            self.log.signal(self._row(s, "skipped", reason, plan))
            return {"signal_id": s.signal_id, "status": "skipped", "reason": reason}

        age_min = (now - s.trigger_time.to_pydatetime()).total_seconds() / 60
        if age_min > cfg.STALE_AFTER_MIN:
            return skip("stale")
        if spike:
            return skip("spike_candle")
        tick = self.mt5.symbol_info_tick(s.symbol)
        if tick is None:
            return skip("no_tick")
        info = data_feed.broker_info(self.mt5, s.symbol)
        spread_pts = round((tick.ask - tick.bid) / info["point"])
        plan, why = risk.make_plan(s, info, tick.bid, tick.ask, spread_pts)
        if why:
            return skip(why)
        why = risk.check_limits(s.technique, s.symbol, now, self.state,
                                self.monitor.positions_on_symbol(s.symbol), len(self.monitor.smc_positions()))
        if why:
            return skip(why, plan)

        digits = info["digits"]
        self.notifier.send(notify.signal_message(s, plan, self.execute, digits))          # 1. the signal
        if not self.execute:
            self.log.signal(self._row(s, "alert_only", "", plan))
            return {"signal_id": s.signal_id, "status": "alert_only"}

        result = self.executor.open(plan)                                                 # 2. then the market order
        self.log.order({"type": "OPEN", "symbol": s.symbol, "direction": "buy" if s.direction == 1 else "sell",
                        "prix": result.price if result.ok else plan.price, "retcode": result.retcode,
                        "statut": "OK" if result.ok else "REFUSE", "technique": s.technique, "signal_id": s.signal_id,
                        "ticket": result.ticket or "", "volume": plan.volume, "sl": plan.sl, "tp": plan.tp})
        if result.ok:
            self.state.add_position(result.ticket, {
                "signal_id": s.signal_id, "technique": s.technique, "symbol": s.symbol, "direction": s.direction,
                "volume": plan.volume, "entry": result.price, "sl": plan.sl, "tp": plan.tp, "risk_usd": round(plan.risk_usd, 2),
                "rr": round(plan.rr, 3), "open_time": now.isoformat(), "tp_server": result.tp_server,
                "zone_lo": s.zone_lo, "zone_hi": s.zone_hi, "bias_dir": s.bias_dir, "spread_pts": spread_pts,
                "notes": s.notes, "magic": cfg.MAGIC[s.technique]})
            self.state.add_day_count(s.technique, now.date().isoformat())
            self.notifier.send(notify.executed_message(plan, result))
            self.log.signal(self._row(s, "traded", "", plan, result.ticket))
            self.state.clear_alert("algo_disabled")
            self.state.save()
            return {"signal_id": s.signal_id, "status": "traded", "ticket": result.ticket}

        if result.algo_disabled:                                  # MT5 "Algo Trading" is off: say it once, not at every signal
            self.notifier.alert_once(self.state, "algo_disabled",
                                     "🚫 Ordres refusés (code 10027) : le bouton « Algo Trading » de MetaTrader 5 est désactivé.\n"
                                     "Activez-le pour que le bot SMC puisse ouvrir des positions.")
        else:
            self.notifier.send(notify.refused_message(plan, result))
        self.log.signal(self._row(s, "refused", f"{result.retcode}", plan))
        self.state.save()
        return {"signal_id": s.signal_id, "status": "refused", "retcode": result.retcode}
