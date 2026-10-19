"""State that must survive a restart: signals already handled, open SMC positions, closed results, daily counters.

Written atomically (temp file, then replace) so a crash can never leave a half-written file.
"""
import json
import os
from datetime import datetime, timedelta

KEEP_DAYS = 60


class State:
    def __init__(self, path: str):
        self.path = path
        self.data = {"processed": {}, "last_scan": {}, "positions": {}, "closed": [], "daily": {}, "alerts": {}}
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as f:
                    self.data.update(json.load(f))
            except (OSError, ValueError):
                os.replace(path, path + ".corrupt")               # keep the broken file, start clean

    def save(self):
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=1, default=str)
        os.replace(tmp, self.path)

    # --- signals already handled (dedupe across scans and restarts)
    def seen(self, signal_id: str) -> bool:
        return signal_id in self.data["processed"]

    def mark_seen(self, signal_id: str, when: str):
        self.data["processed"][signal_id] = when
        cutoff = (datetime.now() - timedelta(days=KEEP_DAYS)).isoformat()
        if len(self.data["processed"]) > 5000:
            self.data["processed"] = {k: v for k, v in self.data["processed"].items() if v >= cutoff}

    # --- candle scanned last, per symbol
    def last_scan(self, symbol: str):
        return self.data["last_scan"].get(symbol)

    def set_last_scan(self, symbol: str, iso: str):
        self.data["last_scan"][symbol] = iso

    # --- open SMC positions, by ticket
    @property
    def positions(self) -> dict:
        return self.data["positions"]

    def add_position(self, ticket: int, info: dict):
        self.data["positions"][str(ticket)] = info

    def remove_position(self, ticket: int):
        self.data["positions"].pop(str(ticket), None)

    # --- closed trades (for the weekly breaker)
    def add_closed(self, technique: str, exit_time: str, r: float):
        self.data["closed"].append({"technique": technique, "exit_time": exit_time, "r": r})
        newest = max(datetime.fromisoformat(c["exit_time"]) for c in self.data["closed"])
        cutoff = (newest - timedelta(days=KEEP_DAYS)).isoformat()                  # relative to the data, not the PC clock
        self.data["closed"] = [c for c in self.data["closed"] if c["exit_time"] >= cutoff]

    def week_r(self, technique: str, week_start: str, week_end: str) -> float:
        return sum(c["r"] for c in self.data["closed"]
                   if c["technique"] == technique and week_start <= c["exit_time"] < week_end)

    # --- entries per technique per day
    def day_count(self, technique: str, day: str) -> int:
        return self.data["daily"].get(day, {}).get(technique, 0)

    def add_day_count(self, technique: str, day: str):
        d = self.data["daily"].setdefault(day, {})
        d[technique] = d.get(technique, 0) + 1
        for old in sorted(self.data["daily"])[:-30]:
            self.data["daily"].pop(old)

    # --- alerts already sent (so a persistent problem is reported once)
    def alert_sent(self, key: str) -> bool:
        return key in self.data["alerts"]

    def mark_alert(self, key: str):
        self.data["alerts"][key] = datetime.now().isoformat(timespec="seconds")

    def clear_alert(self, key: str):
        self.data["alerts"].pop(key, None)
