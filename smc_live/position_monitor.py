"""Follows the SMC positions without ever blocking the main loop (the old bot's monitor_trade blocked it).

Each call to sync():
  - finds positions that have closed since the last call and writes their result (trades.csv, Telegram, weekly R);
  - applies the 24 h time stop and the bot-side TP (only for positions whose TP could not be placed on the server);
  - adopts SMC positions found in MT5 but unknown to the state (after a crash), with the little information available.
"""
from datetime import datetime, timedelta, timezone

from smc_live import config_smc as cfg
from smc_live import notify


def _naive_server(epoch: int) -> datetime:
    return datetime.fromtimestamp(epoch, tz=timezone.utc).replace(tzinfo=None)


class Monitor:
    def __init__(self, mt5, state, log, notifier, executor):
        self.mt5, self.state, self.log, self.notifier, self.executor = mt5, state, log, notifier, executor

    # ---- queries used by the pipeline
    def smc_positions(self) -> list:
        magics = set(cfg.MAGIC.values())
        return [p for p in (self.mt5.positions_get() or []) if p.magic in magics]

    def positions_on_symbol(self, symbol: str) -> int:
        return len(self.mt5.positions_get(symbol=symbol) or [])

    # ---- main entry point
    def sync(self, now: datetime):
        live = {p.ticket: p for p in self.smc_positions()}
        for tk, info in list(self.state.positions.items()):
            if int(tk) not in live:
                self._finalize(int(tk), info)
        for ticket, p in live.items():
            if str(ticket) not in self.state.positions:
                self._adopt(p)
        for ticket, p in live.items():
            info = self.state.positions.get(str(ticket))
            if info:
                self._manage(p, info, now)
        self.state.save()

    # ---- helpers
    def _adopt(self, p):
        tech = next((t for t, m in cfg.MAGIC.items() if m == p.magic), "UNKNOWN")
        self.state.add_position(p.ticket, {
            "signal_id": f"adopted|{p.ticket}", "technique": tech, "symbol": p.symbol,
            "direction": 1 if p.type == self.mt5.POSITION_TYPE_BUY else -1, "volume": p.volume, "entry": p.price_open,
            "sl": p.sl, "tp": p.tp, "risk_usd": None, "rr": None, "open_time": _naive_server(p.time).isoformat(),
            "tp_server": bool(p.tp), "zone_lo": None, "zone_hi": None, "bias_dir": None, "spread_pts": None,
            "notes": "adopted after a restart (no signal information)", "magic": p.magic})
        self.notifier.send(f"♻️ Position {p.symbol} #{p.ticket} reprise en charge après un redémarrage")

    def _manage(self, p, info, now: datetime):
        opened = datetime.fromisoformat(info["open_time"])
        if now - opened >= timedelta(hours=cfg.HOLD_HOURS):
            res = self.executor.close_position(p, "time")
            if res.ok:
                info["closing_reason"] = "TIME"
            return
        if not info.get("tp_server") and info.get("tp"):
            tick = self.mt5.symbol_info_tick(p.symbol)
            if tick is None:
                return
            d = info["direction"]
            reached = tick.bid >= info["tp"] if d == 1 else tick.ask <= info["tp"]
            if reached:
                res = self.executor.close_position(p, "tp")
                if res.ok:
                    info["closing_reason"] = "TP"

    def _finalize(self, ticket: int, info: dict):
        m = self.mt5
        deals = m.history_deals_get(position=ticket) or []
        outs = [d for d in deals if d.entry == m.DEAL_ENTRY_OUT]
        if not outs:                                             # the history is not available yet: try again next time
            info["waiting"] = info.get("waiting", 0) + 1
            if info["waiting"] > 120:                            # about 10 minutes: give up and say so
                self.notifier.send(f"⚠️ Position #{ticket} fermée mais son historique est introuvable")
                self.state.remove_position(ticket)
            return
        last = outs[-1]
        profit = sum(d.profit + d.commission + d.swap for d in deals)
        d = info["direction"]
        risk = abs(info["entry"] - info["sl"]) if info.get("sl") else None
        r = d * (last.price - info["entry"]) / risk if risk else 0.0
        if info.get("closing_reason"):
            reason = info["closing_reason"]
        elif last.reason == m.DEAL_REASON_SL:
            reason = "SL"
        elif last.reason == m.DEAL_REASON_TP:
            reason = "TP"
        else:
            reason = "CLOSED"
        exit_time = _naive_server(last.time)
        minutes = (exit_time - datetime.fromisoformat(info["open_time"])).total_seconds() / 60
        self.log.trade({
            "symbol": info["symbol"], "direction": "buy" if d == 1 else "sell", "lot": info["volume"], "entry": info["entry"],
            "exit": last.price, "profit": round(profit, 2), "technique": info["technique"], "signal_id": info["signal_id"],
            "ticket": ticket, "magic": info.get("magic"), "sl": info.get("sl"), "tp": info.get("tp"),
            "risk_usd": info.get("risk_usd"), "planned_rr": info.get("rr"), "r_multiple": round(r, 3),
            "exit_reason": reason, "hold_min": round(minutes), "bias_dir": info.get("bias_dir"),
            "zone_lo": info.get("zone_lo"), "zone_hi": info.get("zone_hi"), "spread_pts": info.get("spread_pts"),
            "trigger_tf": "M15", "notes": info.get("notes", "")})
        self.state.add_closed(info["technique"], exit_time.isoformat(), r)
        self.state.remove_position(ticket)
        self.notifier.send(notify.closed_message(info["symbol"], info["technique"], profit, r, reason, minutes, ticket))
