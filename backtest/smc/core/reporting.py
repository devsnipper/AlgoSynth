"""Writes Stage 1 results: one folder of reports per setup, plus a summary across all setups."""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from core import study
from core.constants import SMC_DIR


def summary_dir(sub: str = "") -> str:
    return os.path.join(SMC_DIR, "reports", sub)


def _fmt(x, nd=3):
    return "" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{nd}f}"


def _table(df: pd.DataFrame, cols: list) -> str:
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for r in df.itertuples(index=False):
        d = r._asdict()
        lines.append("| " + " | ".join(_fmt(d[c]) if isinstance(d[c], (float, np.floating)) else str(d[c]) for c in cols) + " |")
    return "\n".join(lines)


def write_setup_report(setup, cells: pd.DataFrame, verdict: pd.DataFrame, folder: str, z_min: float):
    cells.to_csv(os.path.join(folder, "stage1_cells.csv"), index=False)
    verdict.to_csv(os.path.join(folder, "stage1_verdict.csv"), index=False)
    md = [f"# {setup.title} ({setup.name}): Stage 1", "",
          f"Primary test: net move after {study.HORIZONS[study.PRIMARY]} M15 candles ({study.PRIMARY}), ATR units, spread included,",
          f"minus the average of comparable moments. Pass = z >= {z_min}, at least {study.MIN_EVENTS} events in block A,",
          "and a positive excess in block C. Block B is not touched at Stage 1.", "",
          "## Verdict", "",
          _table(verdict, ["bias", "group", "n_A", "excess_A", "z_A", "n_C", "excess_C", "z_C", "verdict"]), "",
          "## All cells", "",
          _table(cells, ["bias", "block", "group", "symbols", "n", "excess_3h", "z_3h", "excess_1h", "z_1h",
                         "raw_mean", "base_mean", "win_pct", "mfe_med", "mae_med"]), "",
          "excess = mean over events of (net move - baseline), in ATR. Baseline = average net move of all comparable "
          "moments (same symbol, direction, block and bias condition).", ""]
    with open(os.path.join(folder, "stage1.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))


def write_summary(verdict: pd.DataFrame, cells: pd.DataFrame, ledger_info: dict, folder: str, z_min: float, title: str):
    os.makedirs(folder, exist_ok=True)
    verdict.to_csv(os.path.join(folder, "stage1_verdicts.csv"), index=False)
    cells.to_csv(os.path.join(folder, "stage1_cells.csv"), index=False)
    passed = verdict[verdict.verdict == "PASS"]
    enough = verdict[verdict.enough_events]
    md = [f"# Stage 1 summary: {title}", "",
          f"Threshold: z >= {z_min} on the {study.PRIMARY} excess, at least {study.MIN_EVENTS} events in block A, "
          "same sign in block C.", "",
          f"Ledger: {ledger_info}. Block B opened for: {ledger_info['block_B_opened_for'] or 'nobody'}.", "",
          f"**Cells with enough events: {len(enough)} of {len(verdict)}. Passing both blocks: {len(passed)}.**", ""]
    cols = ["setup", "bias", "group", "n_A", "excess_A", "z_A", "n_C", "excess_C", "z_C"]
    md += ["## Survivors", "", _table(passed, cols) if len(passed) else "None.", ""]
    rev = verdict[verdict.verdict.str.startswith("REVERSED")]
    if len(rev):
        md += ["## Reversed (significantly worse than random; not a pass)", "", _table(rev, cols), ""]
    top = enough.sort_values("z_A", ascending=False).head(8)
    md += ["## Highest z in block A", "", _table(top, cols + ["verdict"]), "",
           "## All verdicts", "", _table(verdict, ["setup", "bias", "group", "n_A", "excess_A", "z_A", "excess_C", "z_C", "verdict"]), ""]
    with open(os.path.join(folder, "stage1_summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    # heatmap of z in block A
    groups = list(dict.fromkeys(verdict["group"]))
    v = verdict.copy()
    v["row"] = v["setup"].str.slice(0, 3) + " " + v["bias"]
    v["z"] = v["z_A"].where(v["enough_events"])
    pv = v.pivot_table(index="row", columns="group", values="z", aggfunc="first")[groups]
    fig, ax = plt.subplots(figsize=(1.2 * len(groups) + 3, 0.4 * len(pv) + 1.5))
    lim = max(4.0, np.nanmax(np.abs(pv.values))) if np.isfinite(pv.values).any() else 4.0
    im = ax.imshow(pv.values, cmap="RdYlGn", vmin=-lim, vmax=lim, aspect="auto")
    ax.set_xticks(range(len(groups)), groups, rotation=20)
    ax.set_yticks(range(len(pv)), pv.index)
    for i in range(pv.shape[0]):
        for j in range(pv.shape[1]):
            val = pv.values[i, j]
            ax.text(j, i, "n/a" if np.isnan(val) else f"{val:.1f}", ha="center", va="center", fontsize=8)
    ax.set_title(f"Block A z-scores (pass at {z_min}; n/a = fewer than {study.MIN_EVENTS} events)")
    fig.colorbar(im)
    fig.tight_layout()
    fig.savefig(os.path.join(folder, "stage1_zscores.png"), dpi=120)
    plt.close(fig)
