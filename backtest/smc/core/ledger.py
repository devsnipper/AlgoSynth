"""LEDGER.json: an automatic log of every evaluation, so the multiple-testing budget and the rule
"block B is looked at once" are enforced by code and not by memory.

hypotheses  every distinct (setup, bias, group, block) cell evaluated, with the first time it was evaluated
runs        one entry per runner command
block_B     list of finalists whose verdict opened block B (Stage 2, not used yet)
"""
import json
import os
from datetime import datetime

from core.constants import SMC_DIR

PATH = os.path.join(SMC_DIR, "LEDGER.json")


def _load() -> dict:
    if os.path.exists(PATH):
        with open(PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"hypotheses": {}, "runs": [], "block_B": [], "exploratory": []}


def record_study(command: str, cells) -> dict:
    """Log a Stage 1 run. `cells` is the DataFrame returned by study_setup (all setups concatenated)."""
    led = _load()
    now = datetime.now().isoformat(timespec="seconds")
    for r in cells[["setup", "bias", "block", "group"]].drop_duplicates().itertuples(index=False):
        key = f"{r.setup}|{r.bias}|{r.group}|{r.block}"
        led["hypotheses"].setdefault(key, now)
    led["runs"].append({"time": now, "command": command, "stage": 1,
                        "setups": sorted(cells["setup"].unique().tolist()), "cells": int(len(cells))})
    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(led, f, indent=2)
    return summary(led)


def record_exploratory(command: str, design: str, cells: int):
    """Log a run that is NOT a Stage 1/2 test (it never counts towards selection)."""
    led = _load()
    led.setdefault("exploratory", []).append({"time": datetime.now().isoformat(timespec="seconds"),
                                              "command": command, "design": design, "cells": cells, "blocks": ["A"]})
    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(led, f, indent=2)


def summary(led: dict = None) -> dict:
    led = led or _load()
    keys = list(led["hypotheses"])
    return {"tests_block_A": sum(k.endswith("|A") for k in keys), "tests_block_C": sum(k.endswith("|C") for k in keys),
            "runs": len(led["runs"]), "block_B_opened_for": led["block_B"]}
