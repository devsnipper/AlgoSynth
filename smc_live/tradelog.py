"""CSV logs: trades.csv, orders.csv (existing files, new columns appended at the END) and signals.csv (new).

The 8 old columns of trades.csv and the 8 of orders.csv never move, so reporter.py (which reads by column name)
and any old analysis keep working. Migration copies the old file to a backup first and deletes nothing.
"""
import csv
import os
import shutil
import time
from datetime import datetime

OLD_TRADES = ["date", "heure", "symbol", "direction", "lot", "entry", "exit", "profit"]
NEW_TRADES = ["technique", "signal_id", "ticket", "magic", "sl", "tp", "risk_usd", "planned_rr", "r_multiple",
              "exit_reason", "hold_min", "bias_dir", "zone_lo", "zone_hi", "spread_pts", "trigger_tf", "notes"]
OLD_ORDERS = ["date", "heure", "type", "symbol", "direction", "prix", "retcode", "statut"]
NEW_ORDERS = ["technique", "signal_id", "ticket", "volume", "sl", "tp"]
SIGNALS = ["signal_id", "time", "technique", "symbol", "direction", "trigger_tf", "entry_ref", "sl", "tp", "planned_rr",
           "risk_usd_est", "lot_est", "zone_lo", "zone_hi", "bias_dir", "status", "skip_reason", "ticket", "notes"]
TRADES_COLS, ORDERS_COLS = OLD_TRADES + NEW_TRADES, OLD_ORDERS + NEW_ORDERS


class TradeLog:
    def __init__(self, log_dir: str):
        self.dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.trades = os.path.join(log_dir, "trades.csv")
        self.orders = os.path.join(log_dir, "orders.csv")
        self.signals = os.path.join(log_dir, "signals.csv")

    # ---- header handling
    def ensure_headers(self) -> list:
        """Create or migrate the three files. Returns a list of what was done (for the startup message)."""
        done = []
        for path, old, new, legacy_value in ((self.trades, OLD_TRADES, NEW_TRADES, "EMA_M5"),
                                             (self.orders, OLD_ORDERS, NEW_ORDERS, "EMA_M5")):
            cols = old + new
            if not os.path.exists(path):
                self._write_header(path, cols)
                done.append(f"created {os.path.basename(path)}")
                continue
            with open(path, newline="", encoding="utf-8") as f:
                header = next(csv.reader(f), [])
            if header == cols:
                continue
            if header == old:                                    # the old 8-column file: migrate
                backup = os.path.join(self.dir, f"{os.path.splitext(os.path.basename(path))[0]}_backup_{datetime.now():%Y%m%d_%H%M%S}.csv")
                shutil.copy2(path, backup)
                with open(path, newline="", encoding="utf-8") as f:
                    rows = list(csv.DictReader(f))
                with open(path, "w", newline="", encoding="utf-8") as f:
                    w = csv.DictWriter(f, fieldnames=cols)
                    w.writeheader()
                    for r in rows:
                        w.writerow({**r, "technique": legacy_value})
                done.append(f"migrated {os.path.basename(path)} ({len(rows)} rows, backup {os.path.basename(backup)})")
                continue
            raise RuntimeError(f"{path}: unexpected header {header}; refusing to touch it")
        if not os.path.exists(self.signals):
            self._write_header(self.signals, SIGNALS)
            done.append("created signals.csv")
        return done

    @staticmethod
    def _write_header(path, cols):
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(cols)

    # ---- appends (one lock file, short retry, so two writers never interleave a row)
    def _append(self, path, cols, row: dict):
        lock = path + ".lock"
        for _ in range(100):
            try:
                fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                break
            except FileExistsError:
                if time.time() - os.path.getmtime(lock) > 30:      # stale lock from a crashed writer
                    os.remove(lock)
                time.sleep(0.05)
        else:
            raise RuntimeError(f"could not lock {path}")
        try:
            with open(path, "a", newline="", encoding="utf-8") as f:
                csv.DictWriter(f, fieldnames=cols, extrasaction="ignore").writerow(row)
        finally:
            os.close(fd)
            os.remove(lock)

    def trade(self, row: dict):
        now = datetime.now()
        self._append(self.trades, TRADES_COLS, {"date": now.strftime("%Y-%m-%d"), "heure": now.strftime("%H:%M:%S"), **row})

    def order(self, row: dict):
        now = datetime.now()
        self._append(self.orders, ORDERS_COLS, {"date": now.strftime("%Y-%m-%d"), "heure": now.strftime("%H:%M:%S"), **row})

    def signal(self, row: dict):
        self._append(self.signals, SIGNALS, row)

    def update_signal(self, signal_id: str, **changes):
        """Rewrite one row of signals.csv (status / ticket change after the order result). Small file, rare call."""
        with open(self.signals, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        for r in rows:
            if r["signal_id"] == signal_id:
                r.update({k: ("" if v is None else v) for k, v in changes.items()})
        tmp = self.signals + ".tmp"
        with open(tmp, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=SIGNALS)
            w.writeheader()
            w.writerows(rows)
        os.replace(tmp, self.signals)
