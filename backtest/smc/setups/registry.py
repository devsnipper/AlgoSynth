"""Finds every setup by scanning setups/sNN_*/setup.py. Each module exposes a `SETUP` object."""
import importlib
import os
import re

from setups.base import Setup

_DIR = os.path.dirname(__file__)


def folder_names() -> list:
    return sorted(d for d in os.listdir(_DIR)
                  if re.fullmatch(r"s\d\d_[a-z0-9_]+", d) and os.path.isfile(os.path.join(_DIR, d, "setup.py")))


def load_all() -> dict:
    out = {}
    for d in folder_names():
        setup = importlib.import_module(f"setups.{d}.setup").SETUP
        assert isinstance(setup, Setup) and setup.name == d, f"{d}: SETUP.name must equal the folder name"
        out[d] = setup
    return out


def get(name: str) -> Setup:
    setups = load_all()
    matches = [k for k in setups if k == name or k.startswith(name)]
    if len(matches) != 1:
        raise KeyError(f"'{name}' matches {matches or 'nothing'}; known: {list(setups)}")
    return setups[matches[0]]


def report_dir(name: str) -> str:
    path = os.path.join(_DIR, name, "reports")
    os.makedirs(path, exist_ok=True)
    return path
