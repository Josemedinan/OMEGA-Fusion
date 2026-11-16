#!/usr/bin/env python3
"""Portfolio charts 21-24 (GDSII quality evolution, wrapper placement exploration, sign-off scoreboard, V6 vs V7 layout).
All numbers come from charts/data/*.csv and docs/results/WRAPPER_SIGNOFF_V7.md; nothing is estimated here.
usage: python plot_portfolio.py <repo root>"""
import csv, os, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.image as mpimg
from matplotlib.patches import Rectangle

R = os.path.abspath(sys.argv[1]); CH = f"{R}/charts"
INK, MUTED, GRID = "#1b2430", "#6b7686", "#e5e8ec"
BLUE, TEAL, AMBER, RED, GREEN = "#2d6cdf", "#17a398", "#e6a117", "#d64545", "#2f9e5b"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID, "axes.axisbelow": True})


def save(fig, name, note):
    fig.text(0.01, 0.01, note, fontsize=7.5, color=MUTED, va="bottom")
    fig.savefig(f"{CH}/{name}.png", dpi=170, bbox_inches="tight"); fig.savefig(f"{CH}/{name}.svg", bbox_inches="tight"); plt.close(fig); print("wrote", name)


# ---- 21: GDSII quality evolution -------------------------------------------------------------------------------------------
rows = list(csv.DictReader(open(f"{CH}/data/postroute_sta_by_run_corner.csv")))
def worst(run_prefix, key, fn):
    return fn(float(r[key]) for r in rows if r["run"].startswith(run_prefix) and r["corner"].startswith("max_ss"))
ver = ["V3", "V4", "V6", "V7"]
slew = [worst("V3", "slew_vio", max), worst("V4", "slew_vio", max), worst("V6", "slew_vio", max), 0]
cap = [worst("V3", "cap_vio", max), worst("V4", "cap_vio", max), worst("V6", "cap_vio", max), 0]
hold_ps = [worst("V3", "hold_ws_ns", min) * 1000, worst("V4", "hold_ws_ns", min) * 1000, 16.9, 101.8]   # V6/V7: 9-corner worst (v6_v7_corner_slack.csv)
fan = [None, None, 83, 1]
fig, axs = plt.subplots(1, 4, figsize=(15, 4.3))
cols = [MUTED, MUTED, BLUE, TEAL]
for ax, vals, ttl, unit in [(axs[0], hold_ps, "Worst hold slack", "ps"), (axs[1], slew, "Max-slew violations", "pins"), (axs[2], cap, "Max-cap violations", "pins")]:
    ax.bar(ver, [v for v in vals], color=cols, width=.62)
    ax.set_title(ttl, loc="left", fontsize=12, fontweight="bold", color=INK); ax.set_ylabel(unit)
    for i, v in enumerate(vals): ax.text(i, v + (0.02 * (max(vals) - min(min(vals), 0))) * (1 if v >= 0 else -1), f"{v:,.0f}", ha="center", va="bottom" if v >= 0 else "top", fontsize=10, color=INK, fontweight="bold")
axs[0].axhline(0, color=INK, lw=1); axs[0].set_ylim(-1500, 330)
axs[1].set_yscale("symlog", linthresh=10); axs[1].set_ylim(0, 40000)
axs[2].set_ylim(0, 300)
axs[3].bar(["V6", "V7"], [83, 1], color=[BLUE, TEAL], width=.5); axs[3].set_title("Fanout-limit nets", loc="left", fontsize=12, fontweight="bold", color=INK); axs[3].set_ylabel("nets")
for i, v in enumerate([83, 1]): axs[3].text(i, v + 2, f"{v}", ha="center", fontsize=10, fontweight="bold", color=INK)
axs[3].set_ylim(0, 100)
fig.suptitle("GDSII quality across layout versions — timing and electrical closure (worst PVT corner, extracted SPEF)", x=0.01, ha="left", fontsize=14, fontweight="bold", color=INK)
fig.tight_layout(rect=[0, 0.05, 1, 0.94])
save(fig, "21_gds_quality_evolution", "Data: charts/data/postroute_sta_by_run_corner.csv (V3, V4, V6 at max_ss) and v6_v7_corner_slack.csv (V6/V7 hold = worst of 9 corners). V7 = nine ECO + re-route iterations on V6.")

# ---- 22: wrapper macro placement exploration ---------------------------------------------------------------------------------
names = ["N @ y=860\n+ repeater ECO", "N @ y=860\nplain", "FS @ y=860\nplain", "FS @ y=200\nplain"]
w_slew, w_cap, w_setup = [876, 850, 566, 1141], [100, 26, 57, 104], [8.81, 9.48, 10.66, 11.82]
fig, axs = plt.subplots(1, 3, figsize=(15, 4.6))
x = range(4); cl = [MUTED, MUTED, TEAL, MUTED]
axs[0].bar(x, w_slew, color=cl, width=.62); axs[0].set_title("Slew violations (worst corner)", loc="left", fontsize=12, fontweight="bold")
axs[1].bar(x, w_cap, color=cl, width=.62); axs[1].set_title("Cap violations (worst corner)", loc="left", fontsize=12, fontweight="bold")
axs[2].bar(x, w_setup, color=cl, width=.62); axs[2].set_title("Worst setup slack, 9 corners [ns]", loc="left", fontsize=12, fontweight="bold")
for ax, vals, f in zip(axs, [w_slew, w_cap, w_setup], ["{:,.0f}", "{:,.0f}", "+{:.2f}"]):
    ax.set_xticks(list(x)); ax.set_xticklabels(names, fontsize=8.5)
    for i, v in enumerate(vals): ax.text(i, v * 1.02, f.format(v), ha="center", va="bottom", fontsize=10, fontweight="bold", color=INK)
    ax.set_ylim(0, max(vals) * 1.15)
axs[0].annotate("−35 % vs ECO baseline", xy=(2, 566), xytext=(2, 1000), ha="center", color=TEAL, fontsize=10, fontweight="bold", arrowprops=dict(arrowstyle="->", color=TEAL))
fig.suptitle("Caravel wrapper: macro orientation and position exploration (V7 macro, all runs route DRC 0 and antenna 0)", x=0.01, ha="left", fontsize=14, fontweight="bold", color=INK)
fig.tight_layout(rect=[0, 0.05, 1, 0.93])
save(fig, "22_wrapper_macro_placement_sweep", "Data: docs/results/WRAPPER_SIGNOFF_V7.md and docs/results/wrapper_experiments/*.rpt (OpenROAD STA, 9 PVT corners, extracted SPEF). FS = flipped south: the 92 output pins face the south I/O.")

# ---- 23: sign-off scoreboard ---------------------------------------------------------------------------------------------------
checks = ["Route DRC (TritonRoute)", "Magic DRC", "KLayout DRC", "LVS (Netgen)", "GDS XOR Magic vs KLayout", "Antenna after routing", "Setup, 9 PVT corners", "Hold, 9 PVT corners", "Max slew", "Max cap", "Max fanout", "Gate-level simulation"]
cols_ = ["Macro V6", "Macro V7", "Caravel wrapper\n(V7 macro)"]
P, T, N_ = ("PASS", GREEN), ("tuning", AMBER), ("roadmap", "#b9c0cb")
M = [[P, P, P], [P, P, P], [P, P, ("FEOL pass", GREEN)], [P, P, N_], [P, P, P], [P, P, P], [P, P, P], [P, P, P],
     [("158", AMBER), P, T], [("23", AMBER), P, T], [("83", AMBER), ("1 net", AMBER), T], [P, P, N_]]
fig, ax = plt.subplots(figsize=(9.6, 7.2)); ax.axis("off"); ax.grid(False)
for j, c in enumerate(cols_): ax.text(1.0 + j * 1.0 + .5, len(checks) + .35, c, ha="center", va="bottom", fontsize=11, fontweight="bold", color=INK)
for i, ch in enumerate(checks):
    y = len(checks) - 1 - i
    ax.text(0.9, y + .5, ch, ha="right", va="center", fontsize=10.5, color=INK)
    for j, (t, c) in enumerate(M[i]):
        ax.add_patch(Rectangle((1.0 + j + .04, y + .06), .92, .88, fc=c, ec="white", alpha=.92 if t != "roadmap" else .55))
        ax.text(1.0 + j + .5, y + .5, t, ha="center", va="center", fontsize=10, color="white" if c != "#b9c0cb" else INK, fontweight="bold")
ax.set_xlim(-1.6, 4.1); ax.set_ylim(-.2, len(checks) + 1)
ax.set_title("Sign-off scoreboard", loc="left", fontsize=14, fontweight="bold", color=INK)
save(fig, "23_signoff_scoreboard", "Sources: docs/results/SIGNOFF_REPORT.md (V6), V7_ECO_REPORT.md (V7), WRAPPER_SIGNOFF_V7.md (wrapper). Amber numbers are remaining electrical-limit counts; V7 cuts them from 158/23/83 to 0/0/1.")

# ---- 24: V6 vs V7 GDSII side by side ---------------------------------------------------------------------------------------------
a, b = mpimg.imread(f"{R}/visuals/v4_v6/00_hero_v6_gds_klayout.png"), mpimg.imread(f"{R}/visuals/00_hero_final_gds_klayout.png")
fig = plt.figure(figsize=(14, 9))
gs = fig.add_gridspec(2, 2, height_ratios=[5, 1.5], hspace=.08, wspace=.04)
for k, (im, t) in enumerate([(a, "V6 — verified baseline GDSII"), (b, "V7 — electrical-closure GDSII (9 ECO iterations)")]):
    ax = fig.add_subplot(gs[0, k]); ax.imshow(im); ax.axis("off"); ax.set_title(t, fontsize=12.5, fontweight="bold", color=INK)
stats = [("Hold slack (worst, 9 corners)", "+17 ps", "+102 ps"), ("Slew violations", "158", "0"), ("Cap violations", "23", "0"), ("Fanout-limit nets", "83", "1"), ("DRC / LVS / XOR / antenna", "0 / match / 0 / 0", "0 / match / 0 / 0")]
for k in range(2):
    ax = fig.add_subplot(gs[1, k]); ax.axis("off")
    txt = "\n".join(f"{x[0]}: {x[1 + k]}" for x in stats)
    ax.text(.5, .5, txt, ha="center", va="center", fontsize=9.6, color=INK, fontweight="bold", bbox=dict(boxstyle="round,pad=.5", fc="#eef6f4" if k else "#f2f4f7", ec=TEAL if k else MUTED))
fig.suptitle("OMEGA-Fusion GDSII, SKY130A — same 1800 × 1800 µm die, 0.3 % more cell area, a much cleaner electrical profile", x=0.01, ha="left", fontsize=14, fontweight="bold", color=INK)
save(fig, "24_gds_v6_vs_v7", "KLayout renders of the real GDS files (met1–met4). V7 = V6 + 22 clock-path buffers, hold/slew/cap repair buffers and re-routing; RTL, SDC and limits untouched.")
