"""Risk rules: turn a Signal into an order plan, or say why not. Pure functions, no MT5.

Order of the checks matters only for the reason that gets logged; every failed check means "no trade".
"""
import math
from dataclasses import dataclass
from datetime import datetime, timedelta

from smc_live import config_smc as cfg


@dataclass
class Plan:
    signal_id: str
    technique: str
    symbol: str
    direction: int
    volume: float
    price: float               # live price the order is sent at (ask for a buy, bid for a sell)
    sl: float
    tp: float
    risk_price: float          # distance price -> SL
    risk_usd: float
    rr: float
    spread_pts: float


def make_plan(signal, info: dict, bid: float, ask: float, spread_pts: float):
    """info: point, digits, contract_size, volume_min, volume_max, volume_step, stops_level (from the broker).
    Returns (Plan, None) or (None, reason)."""
    d = signal.direction
    point = info["point"]
    price = ask if d == 1 else bid
    sl, tp = round(signal.sl, info["digits"]), round(signal.tp, info["digits"])

    if (sl - price) * d >= 0 or (tp - price) * d <= 0:
        return None, "price_through_levels"                      # the market already passed the stop or the target
    risk_price = abs(price - sl)
    if abs(price - signal.entry_ref) > cfg.MAX_SLIPPAGE_FRAC * signal.risk_price:
        return None, "slipped"
    min_dist = (info["stops_level"] + spread_pts) * point
    if risk_price < cfg.MIN_STOP_FACTOR * min_dist:
        return None, "stop_too_tight"
    if abs(tp - price) < min_dist:
        return None, "tp_too_close"
    if spread_pts * point > cfg.SPREAD_MAX_FRAC * risk_price:
        return None, "spread_too_wide"

    contract = info["contract_size"]
    step = info["volume_step"]
    wanted = cfg.RISK_USD / (risk_price * contract)
    volume = max(info["volume_min"], math.floor(wanted / step + 1e-9) * step)
    volume = min(volume, info["volume_max"])
    volume = round(volume, 8)
    risk_usd = volume * risk_price * contract
    if risk_usd > cfg.MAX_RISK_USD:
        return None, "min_lot_risk_too_high"
    return Plan(signal.signal_id, signal.technique, signal.symbol, d, volume, price, sl, tp, risk_price, risk_usd,
                abs(tp - price) / risk_price, spread_pts), None


def week_bounds(when: datetime):
    """ISO week containing `when`: (monday 00:00, next monday 00:00) as ISO strings."""
    monday = (when - timedelta(days=when.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    return monday.isoformat(), (monday + timedelta(days=7)).isoformat()


def check_limits(technique: str, symbol: str, now: datetime, state, positions_on_symbol: int, open_total: int):
    """The limits of the plan. `positions_on_symbol` counts ALL positions on that symbol (any magic number);
    `open_total` counts the SMC positions. Returns a reason or None."""
    if positions_on_symbol >= cfg.MAX_OPEN_PER_SYMBOL:
        return "symbol_busy"
    if open_total >= cfg.MAX_OPEN_TOTAL:
        return "max_open"
    if state.day_count(technique, now.date().isoformat()) >= cfg.MAX_PER_DAY[technique]:
        return "max_per_day"
    start, end = week_bounds(now)
    if state.week_r(technique, start, end) <= cfg.WEEKLY_BREAKER_R:
        return "weekly_breaker"
    return None
