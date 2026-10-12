"""Single entry point for the SMC research code.

    backtest/.venv/Scripts/python.exe backtest/smc/run.py list
    backtest/.venv/Scripts/python.exe backtest/smc/run.py study s02_range_sweep     (or just: study s02)
    backtest/.venv/Scripts/python.exe backtest/smc/run.py study all [--universe spikefree]
    backtest/.venv/Scripts/python.exe backtest/smc/run.py counts   [--universe spikefree]
    backtest/.venv/Scripts/python.exe backtest/smc/run.py trades   [--universe spikefree]   (exploratory: win rate / R)
    backtest/.venv/Scripts/python.exe backtest/smc/run.py test

`study` is Stage 1 (blocks A and C only). Block B is never opened here.
The default universe is boomcrash (10 symbols). spikefree = the 14 spike-free indices. Spike-free results are written
under reports/spikefree/ so the Boom/Crash results are never overwritten.
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def parse(args):
    """Returns (positional args, universe)."""
    universe = "boomcrash"
    rest = []
    it = iter(args)
    for a in it:
        if a == "--universe":
            universe = next(it)
        else:
            rest.append(a)
    return rest, universe


def sub_of(universe: str) -> str:
    return "" if universe == "boomcrash" else universe


def cmd_list(_args) -> int:
    from setups import registry
    for name, s in registry.load_all().items():
        print(f"{name:<42} {s.title}{'' if s.uses_bias else '   (bias is part of the definition)'}")
    return 0


def cmd_counts(args) -> int:
    """Raw event counts per setup and symbol (before block, bias and clustering filters)."""
    import pandas as pd
    from core.context import get_context
    from core.data import symbols
    from setups import registry
    _, universe = parse(args)
    syms = symbols(universe)
    rows = []
    for name, s in registry.load_all().items():
        row = {"setup": name}
        for sym in syms:
            row[sym.replace(" Index", "")] = len(s.detect(get_context(sym)))
        rows.append(row)
    df = pd.DataFrame(rows).set_index("setup")
    df["total"] = df.sum(axis=1)
    pd.set_option("display.width", 300)
    print(df.to_string())
    return 0


def cmd_study(args) -> int:
    import pandas as pd
    from core import ledger, reporting, study
    from core.data import symbols
    from setups import registry

    args, universe = parse(args)
    if not args:
        print(__doc__)
        return 2
    z_min = study.z_threshold(universe)
    sub = sub_of(universe)
    chosen = list(registry.load_all().values()) if args[0] == "all" else [registry.get(args[0])]
    syms = symbols(universe)
    all_cells, all_verdicts = [], []
    for s in chosen:
        t0 = time.time()
        cells = study.study_setup(s, syms, universe=universe)
        verdict = study.verdicts(cells, z_min)
        reporting.write_setup_report(s, cells, verdict, registry.report_dir(s.name, sub), z_min)
        all_cells.append(cells)
        all_verdicts.append(verdict)
        best = verdict[verdict.enough_events].sort_values("z_A", ascending=False).head(1)
        top = "no cell with enough events" if best.empty else \
            f"best z_A {best.iloc[0].z_A:+.2f} ({best.iloc[0].bias}/{best.iloc[0].group}, n={best.iloc[0].n_A})"
        print(f"{s.name:<42} {time.time() - t0:5.1f}s  {top}")
    cells = pd.concat(all_cells, ignore_index=True)
    verdict = pd.concat(all_verdicts, ignore_index=True)
    info = ledger.record_study("study " + " ".join(args) + f" --universe {universe}", cells, universe)
    if args[0] == "all":
        reporting.write_summary(verdict, cells, info, reporting.summary_dir(sub), z_min, f"{universe}, z >= {z_min}")
        print(f"\nSummary written to {reporting.summary_dir(sub)}")
    print(f"Ledger: {info}")
    print(f"Pass: {int((verdict.verdict == 'PASS').sum())} of {int(verdict.enough_events.sum())} cells with enough events (z >= {z_min})")
    return 0


def cmd_trades(args) -> int:
    """EXPLORATORY: one fixed trade design for every setup on blocks A (M5 fills) and C (M15 fills), against random entries."""
    import pandas as pd
    from core import ledger, reporting, study, trade_study
    from core.data import symbols
    from setups import registry

    _, universe = parse(args)
    syms = symbols(universe)
    t0 = time.time()
    controls = {(b, s, blk): trade_study.control_trades(s, b, blk) for b in study.BIASES for s in syms for blk in ("A", "C")}
    print(f"controls done ({time.time() - t0:.0f}s)")
    out = []
    for s in registry.load_all().values():
        t1 = time.time()
        df = trade_study.study_trades(s, syms, controls, universe=universe)
        out.append(df)
        best = df[(df.block == "A+C") & (df.trades >= 300)].sort_values("avg_R", ascending=False).head(1)
        top = "no A+C cell with 300 trades" if best.empty else f"best A+C avg_R {best.iloc[0].avg_R:+.3f} ({best.iloc[0].bias}/{best.iloc[0].group}, n={int(best.iloc[0].trades)})"
        print(f"{s.name:<42} {time.time() - t1:5.1f}s  {top}")
    res = pd.concat(out, ignore_index=True)
    folder = reporting.summary_dir(sub_of(universe))
    os.makedirs(folder, exist_ok=True)
    res.to_csv(os.path.join(folder, "exploratory_trades.csv"), index=False)
    ledger.record_exploratory(f"trades --universe {universe}", f"market entry, stop {trade_study.ATR_STOP} ATR, target {trade_study.RR}R, hold {trade_study.HOLD_H} h", len(res))
    print(f"Written to {folder}")
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


COMMANDS = {"list": cmd_list, "counts": cmd_counts, "study": cmd_study, "trades": cmd_trades, "test": cmd_test}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd not in COMMANDS:
        print(__doc__)
        sys.exit(2)
    sys.exit(COMMANDS[cmd](sys.argv[2:]))
