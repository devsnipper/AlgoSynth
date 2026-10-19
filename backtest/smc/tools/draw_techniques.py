"""Illustrative picture of the three live techniques (A, B, C): invented candles drawn to follow the rules in
techniques/SETUPS.md, with the zones, levels, entry, stop, target and the indicators each technique uses.

Not real data. Output: backtest/smc/docs/techniques_illustration.png

Usage : backtest/.venv/Scripts/python.exe backtest/smc/tools/draw_techniques.py
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "techniques_illustration.png")
UP, DOWN = "#2e9e5b", "#d64545"
BLUE, ORANGE, GREY = "#2b6cb0", "#e08a00", "#555555"


def candles(ax, data):
    for i, (o, h, l, c) in enumerate(data):
        col = UP if c >= o else DOWN
        ax.plot([i, i], [l, h], color=col, lw=1.2, zorder=3)
        ax.add_patch(Rectangle((i - 0.3, min(o, c)), 0.6, max(abs(c - o), 0.15), color=col, zorder=4))


def zone(ax, x0, x1, y0, y1, color, alpha=0.2, ls="-", z=1):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor=color, alpha=alpha, edgecolor=color, lw=1.2, ls=ls, zorder=z))


def hline(ax, y, x0, x1, color, ls="--", lw=1.4):
    ax.plot([x0, x1], [y, y], color=color, ls=ls, lw=lw, zorder=5)


def note(ax, x, y, text, color="black", size=9.5, ha="left", bold=False):
    ax.text(x, y, text, color=color, fontsize=size, ha=ha, va="center", fontweight="bold" if bold else "normal", zorder=8,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=color, alpha=0.92, lw=0.8))


def arrow(ax, text, xy, xytext, color="black", size=9.5):
    ax.annotate(text, xy=xy, xytext=xytext, fontsize=size, color=color, zorder=9, ha="left", va="center",
                arrowprops=dict(arrowstyle="->", color=color, lw=1.2),
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=color, alpha=0.95, lw=0.8))


def trade_boxes(ax, x0, x1, entry, sl, tp):
    zone(ax, x0, x1, min(entry, sl), max(entry, sl), DOWN, 0.10, z=0)
    zone(ax, x0, x1, min(entry, tp), max(entry, tp), UP, 0.10, z=0)
    hline(ax, entry, x0, x1, "black", "-", 1.6)
    hline(ax, sl, x0, x1, DOWN, "-", 1.6)
    hline(ax, tp, x0, x1, UP, "-", 1.6)


def indicators_panel(ax, title, lines, rules):
    ax.axis("off")
    ax.text(0, 1.0, "Indicateurs utilisés", fontsize=12, fontweight="bold", va="top", transform=ax.transAxes)
    ax.text(0, 0.93, "\n".join(lines), fontsize=9.6, va="top", linespacing=1.45, transform=ax.transAxes)
    ax.text(0, 0.50, "Règles d'exécution", fontsize=12, fontweight="bold", va="top", transform=ax.transAxes)
    ax.text(0, 0.43, "\n".join(rules), fontsize=9.6, va="top", linespacing=1.45, transform=ax.transAxes)


# ----------------------------------------------------------------------------- data
A_BASE = [(110, 112, 108, 109), (109, 111, 107, 110), (110, 114, 109, 113), (113, 118, 112, 117), (117, 121, 116, 120),
          (120, 124, 119, 122), (122, 123, 118, 119), (119, 120, 114, 115), (115, 116, 111, 112), (112, 113, 108, 109),
          (109, 115, 108.5, 114), (114, 119, 113, 118), (118, 123, 117, 122), (122, 127, 121, 126), (126, 128, 124, 125),
          (125, 126, 121, 122), (122, 123, 117, 118), (118, 119, 113, 114), (114, 115, 111.5, 112), (112, 116, 111, 115.5)]
A_TAIL = [(115.5, 118, 115, 117.5), (117.5, 121, 117, 120), (120, 124, 119.5, 123), (123, 126, 122, 125),
          (125, 129, 124, 128), (128, 131, 127, 130), (130, 133, 129, 132)]
C_TAIL = [(115.5, 118, 115, 117.5), (117.5, 121, 117, 120), (120, 124, 119.5, 123), (123, 126, 122, 125),
          (125, 130, 124, 129), (129, 134, 128, 133), (133, 137, 132, 136), (136, 141, 135, 140)]
B_DATA = [(112, 114, 110, 113), (113, 116, 112, 115), (115, 118, 114, 117), (117, 120, 116, 119), (119, 122, 118, 121),
          (121, 124, 120, 123), (123, 124.5, 121, 122), (122, 123, 118, 120), (120, 123, 119.5, 122), (122, 125, 121, 124),
          (124, 128, 123.5, 124.5), (124.5, 125, 122, 122.5), (122.5, 123, 120.5, 121), (121, 121.5, 117, 117.5),
          (117.5, 118, 114, 114.5), (114.5, 115.5, 111, 111.5), (111.5, 112, 108, 108.5), (108.5, 109.5, 105, 105.5),
          (105.5, 106.5, 102, 102.5), (102.5, 104, 99, 99.5), (99.5, 100.5, 96, 96.5), (96.5, 97.5, 93, 93.5),
          (93.5, 94.5, 90, 90.5), (90.5, 91.5, 87, 87.5), (87.5, 88.5, 83.5, 84.5)]


def panel_a(ax):
    data = A_BASE + A_TAIL
    candles(ax, data)
    ax.set_xlim(-1, 36); ax.set_ylim(98, 146)
    zone(ax, 8.6, 21.5, 108, 113, BLUE, 0.22, "--")
    note(ax, 14.0, 110.5, "ORDER BLOCK H1", BLUE, 9, "center", True)
    note(ax, 14.7, 105.6, "= dernière bougie baissière avant la cassure", BLUE, 8.6, "center")
    hline(ax, 124, 5, 13.5, GREY)
    ax.plot(5, 124.8, marker="v", color=GREY, zorder=6)
    note(ax, 1.5, 129, "Sommet H1 cassé", GREY, 9)
    note(ax, 7.0, 134, "BOS : clôture au-dessus du sommet", GREY, 9)
    trade_boxes(ax, 19, 27.0, 115.5, 107, 132.5)
    ax.plot(19, 115.5, "ko", zorder=9)
    arrow(ax, "① Le prix revient toucher la zone", (18, 111.8), (1.0, 101.6), BLUE)
    arrow(ax, "② DÉCLENCHEUR M15 : clôture hors de la zone → ACHAT", (19, 115.5), (22.5, 104.5), "black")
    hline(ax, 141.5, 13, 27.4, GREY, ":")
    note(ax, 27.7, 141.5, "Prochain sommet H4 :\nau moins 1,5R de place", GREY, 8.8)
    note(ax, 27.7, 132.5, "TP  132,5   (2R)", UP, 9.5, bold=True)
    note(ax, 27.7, 115.5, "ENTRÉE 115,5 (marché)", "black", 9.5, bold=True)
    note(ax, 27.7, 107, "SL 107  (zone − 0,25×ATR H1)", DOWN, 9.5, bold=True)
    note(ax, 0.2, 143, "Biais H4 : HAUSSIER ▲ (dernière cassure vers le haut)", UP, 10, bold=True)


def panel_b(ax):
    candles(ax, B_DATA)
    ax.set_xlim(-1, 37); ax.set_ylim(78, 136)
    hline(ax, 125, 0, 12.5, ORANGE)
    note(ax, 0.3, 132.2, "Niveau de liquidité :\nplus haut de la veille (stops au-dessus),\n"
                         "sommets égaux H1 ou extrême des 20 bougies H1", ORANGE, 9)
    arrow(ax, "BALAYAGE : la mèche dépasse le niveau,\nla bougie clôture de nouveau sous le niveau", (10, 128), (14.0, 134.5), ORANGE)
    zone(ax, 9.6, 10.4, 124.5, 128, ORANGE, 0.35)
    hline(ax, 118, 7, 13.4, BLUE, ":")
    note(ax, 5.0, 112, "Dernier creux M15 connu\n(référence de confirmation)", BLUE, 9)
    arrow(ax, "DÉCLENCHEUR : clôture sous ce creux\n(changement de structure) → VENTE", (13, 117.5), (14.8, 125.5), "black")
    trade_boxes(ax, 13, 25.5, 117.5, 128.75, 83.75)
    ax.plot(13, 117.5, "ko", zorder=9)
    note(ax, 26.0, 128.75, "SL 128,75  (extrême du balayage\n+ 0,25×ATR M15)", DOWN, 9.2, bold=True)
    note(ax, 26.0, 117.5, "ENTRÉE 117,5 (marché)", "black", 9.5, bold=True)
    note(ax, 26.0, 83.75, "TP 83,75  (3R)", UP, 9.5, bold=True)
    note(ax, 0.3, 84, "Pas de filtre de tendance :\ntechnique de retournement", GREY, 9)


def panel_c(ax):
    data = A_BASE + C_TAIL
    zone(ax, -1, 36, 120, 140, DOWN, 0.07, z=0)
    zone(ax, -1, 36, 100, 120, UP, 0.07, z=0)
    candles(ax, data)
    ax.set_xlim(-1, 36); ax.set_ylim(95, 146)
    hline(ax, 120, -1, 36, GREY, "--", 1.2)
    hline(ax, 140, -1, 27.5, GREY, ":", 1.2)
    hline(ax, 100, -1, 36, GREY, ":", 1.2)
    note(ax, 0.2, 137, "PREMIUM (ventes seulement)", DOWN, 9.5, bold=True)
    note(ax, 0.2, 98.2, "DISCOUNT (achats seulement)", UP, 9.5, bold=True)
    note(ax, 27.6, 120.8, "50 % de la fourchette H4", GREY, 9)
    zone(ax, 8.6, 21.5, 108, 113, BLUE, 0.22, "--")
    note(ax, 14.7, 110.5, "ORDER BLOCK H1", BLUE, 8.8, "center", True)
    zone(ax, 9.7, 12.3, 115, 117, ORANGE, 0.55)
    arrow(ax, "FVG : trou de 3 bougies dans le mouvement\nqui a créé l'order block (obligatoire)", (11, 116), (12.4, 128.5), ORANGE)
    trade_boxes(ax, 19, 27.0, 115.5, 107, 140)
    ax.plot(19, 115.5, "ko", zorder=9)
    arrow(ax, "DÉCLENCHEUR M15 : clôture hors de la zone,\nprix SOUS le milieu → ACHAT", (19, 115.5), (21.2, 103.4), "black")
    note(ax, 27.7, 140, "TP 140 = haut de la fourchette H4\n(≥ 2R, plafonné à 3R : ici 2,9R)", UP, 9, bold=True)
    note(ax, 27.7, 115.5, "ENTRÉE 115,5 (marché)", "black", 9.5, bold=True)
    note(ax, 27.7, 107, "SL 107  (zone − 0,25×ATR H1)", DOWN, 9.5, bold=True)
    note(ax, 0.2, 143.5, "Fourchette H4 : dernier creux 100 → dernier sommet 140  |  Biais H4 : HAUSSIER ▲", GREY, 9.5, bold=True)


def main():
    fig = plt.figure(figsize=(19, 22))
    gs = fig.add_gridspec(3, 2, width_ratios=[3.1, 1.05], hspace=0.20, wspace=0.03)
    specs = [
        ("A  —  Tendance + Order Block H1", panel_a,
         ["• Structure H4 : points de retournement (swings, 3 bougies)\n  et cassure de structure → BIAIS",
          "• Structure H1 : cassure + ORDER BLOCK\n  (dernière bougie contraire avant la cassure)",
          "• ATR H1 : marge du stop (0,25 × ATR)",
          "• Sommets/creux H4 confirmés : place avant\n  le prochain obstacle (≥ 1,5R)",
          "• Bougies M15 : toucher de la zone, puis\n  clôture hors de la zone = déclencheur"],
         ["1. Biais H4 = sens de la cassure de l'order block",
          "2. Zone H1 intacte (48 bougies H1 max), touchée\n    une fois par une mèche M15",
          "3. Dans les 4 bougies : clôture M15 hors de la zone",
          "4. Entrée au marché à cette clôture",
          "5. SL au-delà de la zone, TP = 2R",
          "6. Fermeture auto après 24 h"]),
        ("B  —  Balayage de liquidité + retournement", panel_b,
         ["• Niveaux de liquidité : plus haut/bas de la veille,\n  extrême des 20 dernières bougies H1,\n  sommets/creux égaux H1 (écart ≤ 0,15 × ATR)",
          "• Balayage : mèche au-delà du niveau + clôture M15\n  de retour à l'intérieur",
          "• Structure M15 : dernier creux/sommet confirmé\n  (5 bougies) avant le balayage",
          "• ATR M15 : marge du stop (0,25 × ATR)"],
         ["1. Balayage d'un niveau (sens inverse de la mèche)",
          "2. Dans les 12 bougies M15 : clôture au-delà du\n    dernier creux/sommet = déclencheur",
          "3. Annulé si le prix clôture au-delà de l'extrême\n    du balayage avant la confirmation",
          "4. Entrée au marché, SL au-delà de l'extrême,\n    TP = 3R",
          "5. Fermeture auto après 24 h"]),
        ("C  —  Order Block + FVG, zone premium / discount", panel_c,
         ["• Tous les indicateurs de A",
          "• FVG (fair value gap) : 3 bougies dont la 1re et la 3e\n  ne se chevauchent pas, dans le mouvement de l'OB",
          "• Fourchette H4 : dernier creux et dernier sommet\n  confirmés, et son milieu (50 %)",
          "• Achats seulement sous le milieu (discount),\n  ventes seulement au-dessus (premium)"],
         ["1. Comme A, mais l'OB doit contenir un FVG",
          "2. Prix du déclencheur du bon côté du milieu H4",
          "3. TP = autre extrémité de la fourchette H4,\n    au moins 2R, plafonné à 3R (sinon on ignore)",
          "4. Entrée au marché, SL au-delà de la zone",
          "5. Fermeture auto après 24 h"]),
    ]
    for i, (title, fn, ind, rules) in enumerate(specs):
        ax = fig.add_subplot(gs[i, 0])
        fn(ax)
        ax.set_title(title, fontsize=15, fontweight="bold", loc="left", pad=10)
        ax.set_xticks([]); ax.set_ylabel("Prix (fictif)")
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        indicators_panel(fig.add_subplot(gs[i, 1]), title, ind, rules)
    fig.suptitle("Les 3 techniques SMC du bot — schéma illustratif (bougies et prix fictifs, pas des données réelles)",
                 fontsize=16, fontweight="bold", y=0.915)
    fig.text(0.5, 0.075, "Le bot lit les bougies fermées M15, H1 et H4 de MetaTrader ; H4 donne le biais, H1 la zone, M15 le déclencheur.\n"
                         "Les ordres sont au marché (Deriv refuse les ordres en attente). SL et TP sont fixés à l'ouverture.",
             ha="center", fontsize=10.5, color=GREY)
    os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
    fig.savefig(OUT, dpi=100, bbox_inches="tight", facecolor="white")
    print("saved", os.path.abspath(OUT))


if __name__ == "__main__":
    main()
