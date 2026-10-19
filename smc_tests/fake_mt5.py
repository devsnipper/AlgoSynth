"""A scriptable stand-in for the MetaTrader5 module, enough for the executor, monitor, data feed and pipeline tests."""
from types import SimpleNamespace as NS

import numpy as np

BOOM500 = {"point": 0.001, "digits": 3, "trade_contract_size": 1.0, "volume_min": 0.2, "volume_max": 190.0,
           "volume_step": 0.01, "trade_stops_level": 1173}


class FakeMT5:
    # constants used by the code under test
    TRADE_ACTION_DEAL = 1
    ORDER_TYPE_BUY, ORDER_TYPE_SELL = 0, 1
    ORDER_FILLING_FOK = 0
    POSITION_TYPE_BUY, POSITION_TYPE_SELL = 0, 1
    DEAL_ENTRY_IN, DEAL_ENTRY_OUT = 0, 1
    DEAL_REASON_EXPERT, DEAL_REASON_SL, DEAL_REASON_TP = 3, 4, 5
    TIMEFRAME_M15, TIMEFRAME_H1, TIMEFRAME_H4 = 15, 16385, 16388

    def __init__(self, bid=5000.0, ask=5000.05, info=None, now_epoch=1_760_000_000):
        self.tick = NS(bid=bid, ask=ask, time=now_epoch)
        self.info = NS(**(info or BOOM500))
        self.sent = []                     # every order_send request
        self.checked = []
        self.script = []                   # retcodes returned by successive order_send calls (default: done)
        self.next_ticket = 1000
        self.positions = []
        self.deals = {}                    # position ticket -> list of deals
        self.rates = {}                    # (symbol, timeframe) -> structured array INCLUDING the forming candle

    # --- market data
    def symbol_info(self, symbol):
        return self.info

    def symbol_info_tick(self, symbol):
        return self.tick

    def copy_rates_from_pos(self, symbol, timeframe, pos, count):
        arr = self.rates.get((symbol, timeframe))
        if arr is None:
            return None
        end = len(arr) - pos                           # pos 0 = the forming candle, pos 1 = the last closed one
        return arr[max(0, end - count):end]

    # --- trading
    def order_send(self, req):
        self.sent.append(dict(req))
        code = self.script.pop(0) if self.script else 10009
        if code == 10009:
            ticket = self.next_ticket
            self.next_ticket += 1
            if "position" not in req:
                self.positions.append(NS(ticket=ticket, symbol=req["symbol"], magic=req["magic"], volume=req["volume"],
                                         type=req["type"], price_open=req["price"], sl=req.get("sl", 0.0), tp=req.get("tp", 0.0),
                                         time=self.tick.time))
            return NS(retcode=10009, order=ticket, price=req["price"], comment="done")
        return NS(retcode=code, order=0, price=0.0, comment=f"refused {code}")

    def order_check(self, req):
        self.checked.append(dict(req))
        return NS(retcode=0, comment="ok")

    def positions_get(self, symbol=None):
        ps = [p for p in self.positions if symbol is None or p.symbol == symbol]
        return tuple(ps) if ps else None

    def history_deals_get(self, position=None):
        return tuple(self.deals.get(position, ())) or None

    # --- helpers for tests
    def close_position(self, ticket, price, reason, profit, epoch=None, volume=None):
        pos = next(p for p in self.positions if p.ticket == ticket)
        self.positions = [p for p in self.positions if p.ticket != ticket]
        deal_in = NS(entry=self.DEAL_ENTRY_IN, price=pos.price_open, profit=0.0, commission=0.0, swap=0.0, reason=3, time=pos.time)
        deal_out = NS(entry=self.DEAL_ENTRY_OUT, price=price, profit=profit, commission=0.0, swap=0.0, reason=reason,
                      time=epoch or self.tick.time)
        self.deals[ticket] = [deal_in, deal_out]


def rates_from_frame(df, extra=1):
    """Structured array like MT5 returns (time as epoch seconds). `extra` copies of the last candle are appended at the
    end: they play the role of the candle that is still forming (position 0 in copy_rates_from_pos)."""
    import pandas as pd
    d = df.reset_index(drop=True)
    step = d["time"].iloc[-1] - d["time"].iloc[-2]
    times = list(d["time"]) + [d["time"].iloc[-1] + step * (i + 1) for i in range(extra)]
    rows = list(range(len(d))) + [len(d) - 1] * extra
    arr = np.zeros(len(times), dtype=[("time", "i8"), ("open", "f8"), ("high", "f8"), ("low", "f8"), ("close", "f8"), ("spread", "i4")])
    arr["time"] = pd.DatetimeIndex(times).astype("datetime64[s]").astype("i8")
    for c in ("open", "high", "low", "close"):
        arr[c] = d[c].to_numpy(float)[rows]
    arr["spread"] = d["spread"].to_numpy(int)[rows]
    return arr
