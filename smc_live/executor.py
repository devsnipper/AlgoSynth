"""Sends market orders and closes positions. `mt5` is injected so the logic can be tested with a fake terminal.

What the broker is known to do (repo notes, skills/broker-constraints.md): pending orders refused (10015), FOK only,
SL accepted at opening, TP accepted on some indices only (10016), no SL/TP change after opening. So: try SL + TP at
opening; if the broker answers "invalid stops", send again with the SL only and let the position monitor watch the TP.
"""
import hashlib
import time
from dataclasses import dataclass

from smc_live import config_smc as cfg

DONE, INVALID_STOPS, ALGO_DISABLED, TOO_MANY = 10009, 10016, 10027, 10036
RETRY_PRICE = (10004, 10020, 10021)                            # requote / price changed / no quote: refresh and retry


@dataclass
class ExecResult:
    ok: bool
    sent: bool                    # False when nothing was sent (alert-only mode)
    ticket: int = None
    price: float = None
    retcode: int = None
    comment: str = ""
    tp_server: bool = True
    algo_disabled: bool = False


def comment_for(technique: str, signal_id: str) -> str:
    return f"smc{cfg.LETTER[technique]}:{hashlib.sha1(signal_id.encode()).hexdigest()[:8]}"


class Executor:
    def __init__(self, mt5, execute: bool, sleep=time.sleep):
        self.mt5, self.execute, self.sleep = mt5, execute, sleep

    # ---- building requests
    def _request(self, plan, with_tp: bool, price: float) -> dict:
        m = self.mt5
        req = {"action": m.TRADE_ACTION_DEAL, "symbol": plan.symbol, "volume": plan.volume,
               "type": m.ORDER_TYPE_BUY if plan.direction == 1 else m.ORDER_TYPE_SELL, "price": price, "sl": plan.sl,
               "deviation": cfg.DEVIATION, "magic": cfg.MAGIC[plan.technique],
               "comment": comment_for(plan.technique, plan.signal_id), "type_filling": m.ORDER_FILLING_FOK}
        if with_tp:
            req["tp"] = plan.tp
        return req

    def _live_price(self, plan) -> float:
        tick = self.mt5.symbol_info_tick(plan.symbol)
        if tick is None:
            return plan.price
        return tick.ask if plan.direction == 1 else tick.bid

    # ---- dry check: asks the broker if the order WOULD be accepted, sends nothing
    def check(self, plan):
        res = self.mt5.order_check(self._request(plan, True, self._live_price(plan)))
        if res is None:
            return False, None, "order_check returned None"
        return res.retcode in (0, DONE), res.retcode, getattr(res, "comment", "")

    # ---- opening
    def open(self, plan) -> ExecResult:
        if not self.execute:
            return ExecResult(ok=False, sent=False, comment="alert-only mode")
        with_tp = True
        for attempt in range(4):
            res = self.mt5.order_send(self._request(plan, with_tp, self._live_price(plan)))
            code = getattr(res, "retcode", None)
            if res is not None and code == DONE:
                return ExecResult(True, True, ticket=res.order, price=res.price, retcode=code, comment=res.comment,
                                  tp_server=with_tp)
            if code == ALGO_DISABLED:
                return ExecResult(False, True, retcode=code, comment=getattr(res, "comment", ""), algo_disabled=True)
            if code == INVALID_STOPS and with_tp:
                with_tp = False                                  # the broker refused the TP at opening: SL only
                continue
            if code == TOO_MANY:
                self.sleep(2)
                continue
            if code in RETRY_PRICE:
                continue
            break
        return ExecResult(False, True, retcode=code, comment=getattr(res, "comment", "no answer"))

    # ---- closing (time stop, bot-side TP)
    def close_position(self, position, reason: str) -> ExecResult:
        if not self.execute:
            return ExecResult(ok=False, sent=False, comment="alert-only mode")
        m = self.mt5
        is_buy = position.type == m.POSITION_TYPE_BUY
        for _ in range(3):
            tick = m.symbol_info_tick(position.symbol)
            req = {"action": m.TRADE_ACTION_DEAL, "symbol": position.symbol, "volume": position.volume,
                   "type": m.ORDER_TYPE_SELL if is_buy else m.ORDER_TYPE_BUY, "position": position.ticket,
                   "price": tick.bid if is_buy else tick.ask, "deviation": cfg.DEVIATION, "magic": position.magic,
                   "comment": f"smc-close-{reason}"[:31], "type_filling": m.ORDER_FILLING_FOK}
            res = m.order_send(req)
            if res is not None and res.retcode == DONE:
                return ExecResult(True, True, ticket=res.order, price=res.price, retcode=res.retcode)
            if getattr(res, "retcode", None) == TOO_MANY:
                self.sleep(2)
        return ExecResult(False, True, retcode=getattr(res, "retcode", None), comment=getattr(res, "comment", ""))
