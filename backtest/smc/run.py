"""Single entry point for the SMC research code.

    backtest/.venv/Scripts/python.exe backtest/smc/run.py list
    backtest/.venv/Scripts/python.exe backtest/smc/run.py study s02_range_sweep     (or just: study s02)
    backtest/.venv/Scripts/python.exe backtest/smc/run.py study all
    backtest/.venv/Scripts/python.exe backtest/smc/run.py counts                    (events per setup, no statistics)
    backtest/.venv/Scripts/python.exe backtest/smc/run.py test

`study` is Stage 1 (blocks A and C only). Block B is never opened here.
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def cmd_list(_args) -> int:
    from setups import registry
    for name, s in registry.load_all().items():
        print(f"{name:<42} {s.title}{'' if s.uses_bias else '   (bias is part of the definition)'}")
    return 0


def cmd_counts(_args) -> int:
    """Raw event counts per setup and symbol (before block, bias and clustering filters)."""
    import pandas as pd
    from core.context import get_context
    from core.data import symbols
    from setups import registry
    rows = []
    for name, s in registry.load_all().items():
        row = {"setup": name}
        for sym in symbols():
            row[sym.replace(" Index", "")] = len(s.detect(get_context(sym)))
        rows.append(row)
    df = pd.DataFrame(rows).set_index("setup")
    df["total"] = df.sum(axis=1)
    pd.set_option("display.width", 250)
    print(df.to_string())
    return 0


def cmd_study(args) -> int:
    import pandas as pd
    from core import ledger, reporting, study
    from core.data import symbols
    from setups import registry

    if not args:
        print(__doc__)
        return 2
    chosen = list(registry.load_all().values()) if args[0] == "all" else [registry.get(args[0])]
    syms = symbols()
    all_cells, all_verdicts = [], []
    for s in chosen:
        t0 = time.time()
        cells = study.study_setup(s, syms)
        verdict = study.verdicts(cells)
        reporting.write_setup_report(s, cells, verdict, registry.report_dir(s.name))
        all_cells.append(cells)
        all_verdicts.append(verdict)
        best = verdict[verdict.enough_events].sort_values("z_A", ascending=False).head(1)
        top = "no cell with enough events" if best.empty else \
            f"best z_A {best.iloc[0].z_A:+.2f} ({best.iloc[0].bias}/{best.iloc[0].group}, n={best.iloc[0].n_A})"
        print(f"{s.name:<42} {time.time() - t0:5.1f}s  {top}")
    cells = pd.concat(all_cells, ignore_index=True)
    verdict = pd.concat(all_verdicts, ignore_index=True)
    info = ledger.record_study("study " + " ".join(args), cells)
    if args[0] == "all":
        reporting.write_summary(verdict, cells, info)
        print(f"\nSummary written to {reporting.SUMMARY_DIR}")
    print(f"Ledger: {info}")
    print(f"Pass: {int((verdict.verdict == 'PASS').sum())} of {int(verdict.enough_events.sum())} cells with enough events")
    return 0


def cmd_test(_args) -> int:
    code = 0
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    files = [os.path.join(HERE, "tests", f) for f in sorted(os.listdir(os.path.join(HERE, "tests")))
             if f.startswith("test_") and f.endswith(".py")]
    sdir = os.path.join(HERE, "setups")
    for d in sorted(os.listdir(sdir)):
        f = os.path.join(sdir, d, "test_setup.py")
        if os.path.isfile(f):
            files.append(f)
    for f in files:
        print(f"\n== {os.path.relpath(f, HERE)}")
        code |= subprocess.run([sys.executable, f], env=env).returncode
    return code


COMMANDS = {"list": cmd_list, "counts": cmd_counts, "study": cmd_study, "test": cmd_test}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd not in COMMANDS:
        print(__doc__)
        sys.exit(2)
    sys.exit(COMMANDS[cmd](sys.argv[2:]))
