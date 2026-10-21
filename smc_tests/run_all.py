"""Runs every test file of smc_tests/ and returns a non-zero code if any fails.

Usage : backtest/.venv/Scripts/python.exe smc_tests/run_all.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
code = 0
total = passed = 0
for name in sorted(f for f in os.listdir(HERE) if f.startswith("test_") and f.endswith(".py")):
    out = subprocess.run([sys.executable, os.path.join(HERE, name)], env=env, capture_output=True, text=True,
                         encoding="utf-8", errors="replace")
    p, f = out.stdout.count("PASS  "), out.stdout.count("FAIL  ")
    total, passed = total + p + f, passed + p
    print(f"{name:<34} {p} passed, {f} failed")
    if out.returncode != 0:
        code = 1
        print(out.stdout[-3000:], out.stderr[-1500:])
print(f"\n{passed} of {total} checks passed")
sys.exit(code)
