"""Single entry point for the SMC research code.

    backtest/.venv/Scripts/python.exe backtest/smc/run.py test

More commands (list, study, trade, final) are added in the next steps of docs/BUILD_PLAN.md.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def run_tests() -> int:
    code = 0
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    for name in sorted(f for f in os.listdir(os.path.join(HERE, "tests")) if f.startswith("test_") and f.endswith(".py")):
        print(f"\n== {name}")
        code |= subprocess.run([sys.executable, os.path.join(HERE, "tests", name)], env=env).returncode
    return code


COMMANDS = {"test": run_tests}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd not in COMMANDS:
        print(__doc__)
        print("Commands:", ", ".join(COMMANDS))
        sys.exit(2)
    sys.exit(COMMANDS[cmd]())
