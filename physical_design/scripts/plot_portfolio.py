#!/usr/bin/env python3
"""Portfolio charts of the final layout: timing slack per PVT corner, where the silicon goes, routing by layer.
Data: charts/data/v6_v7_corner_slack.csv (v7_* columns), charts/data/congestion_by_layer_v7.csv, physical_design/reports/v7/metrics.json.
usage: python plot_portfolio.py <repo root>"""
import csv, json, os, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = os.path.abspath(sys.argv[1]); CH = f"{R}/charts"
INK, MUTED, GRID = "#1b2430", "#6b7686", "#e5e8ec"
BLUE, TEAL, AMBER, PURPLE, RED = "#2d6cdf", "#17a398", "#e6a117", "#8a3fc0", "#e0472b"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID, "axes.axisbelow": True})


def save(fig, name, note):
    fig.text(0.01, 0.005, note, fontsize=7.5, color=MUTED, va="bottom")
    fig.savefig(f"{CH}/{name}.png", dpi=170, bbox_inches="tight"); plt.close(fig); print("wrote", name)


# 1. timing per corner
rows = list(csv.DictReader(open(f"{CH}/data/v6_v7_corner_slack.csv")))
names = [r["corner"] for r in rows]
setup = [float(r["v7_setup_ws_ns"]) for r in rows]; hold = [float(r["v7_hold_ws_ns"]) * 1000 for r in rows]
fig, axs = plt.subplots(1, 2, figsize=(13, 4.8))
for ax, vals, ttl, unit, col, f in [(axs[0], setup, "Setup slack — 10 MHz clock", "ns", BLUE, "+{:.1f}"), (axs[1], hold, "Hold slack", "ps", TEAL, "+{:.0f}")]:
    ax.barh(names[::-1], vals[::-1], color=col, height=.62)
    ax.set_title(ttl, loc="left", fontsize=12.5, fontweight="bold", color=INK); ax.set_xlabel(unit)
    for i, v in enumerate(vals[::-1]): ax.text(v, i, " " + f.format(v), va="center", fontsize=9.5, color=INK, fontweight="bold")
    ax.set_xlim(0, max(vals) * 1.15)
fig.suptitle("Timing closure in 9 PVT corners (3 process × 3 RC extraction), extracted SPEF — every path meets setup and hold", x=0.01, ha="left", fontsize=13.5, fontweight="bold", color=INK)
fig.tight_layout(rect=[0, 0.04, 1, 0.93])
save(fig, "final_01_timing_slack_9_corners", "OpenROAD STA, SKY130A sky130_fd_sc_hd, derate 5 %, clock uncertainty 0.25 ns. Data: charts/data/v6_v7_corner_slack.csv (v7_* columns).")

# 2. where the silicon goes
m = json.load(open(f"{R}/physical_design/reports/v7/metrics.json"))
cls = [("Sequential (flip-flops)", "sequential_cell", BLUE), ("Combinational logic", "multi_input_combinational_cell", TEAL), ("Timing-repair buffers", "timing_repair_buffer", AMBER),
       ("Tap cells", "tap_cell", MUTED), ("Clock tree", None, PURPLE), ("Antenna diodes", "antenna_cell", RED)]
data = []
for lab, k, c in cls:
    if k: a, n = m[f"design__instance__area__class:{k}"], m[f"design__instance__count__class:{k}"]
    else:
        a = m["design__instance__area__class:clock_buffer"] + m["design__instance__area__class:clock_inverter"]
        n = m["design__instance__count__class:clock_buffer"] + m["design__instance__count__class:clock_inverter"]
    data.append((lab, a / 1e6, n, c))
fig, ax = plt.subplots(figsize=(10, 4.4))
ax.barh([d[0] for d in data][::-1], [d[1] for d in data][::-1], color=[d[3] for d in data][::-1], height=.6)
for i, d in enumerate(data[::-1]): ax.text(d[1], i, f"  {d[1]:.3f} mm²  ·  {d[2]:,} cells", va="center", fontsize=9.5, color=INK, fontweight="bold")
ax.set_xlim(0, .62); ax.set_xlabel("standard-cell area [mm²]")
ax.set_title("Where the silicon goes — 0.852 mm² of standard cells in a 3.24 mm² die", loc="left", fontsize=13, fontweight="bold", color=INK)
fig.tight_layout(rect=[0, 0.04, 1, 1])
save(fig, "final_02_cell_composition", "Data: physical_design/reports/v7/metrics.json (OpenROAD instance report, fill cells excluded).")

# 3. routing by layer
cg = list(csv.DictReader(open(f"{CH}/data/congestion_by_layer_v7.csv")))
fig, axs = plt.subplots(1, 2, figsize=(11.5, 4.2))
L = [r["layer"] for r in cg]; cols = [BLUE, RED, "#2da84a", "#d9a400"]
axs[0].bar(L, [float(r["wirelength_um"]) / 1e6 for r in cg], color=cols, width=.6); axs[0].set_ylabel("wire length [m]")
axs[0].set_title("Wire length by layer — 3.34 m in total", loc="left", fontsize=12, fontweight="bold", color=INK)
for i, r in enumerate(cg): axs[0].text(i, float(r["wirelength_um"]) / 1e6 + .02, f"{float(r['wirelength_um']) / 1e6:.2f}", ha="center", fontsize=10, fontweight="bold")
axs[1].bar(L, [float(r["max_util"]) * 100 for r in cg], color=cols, width=.6); axs[1].set_ylabel("peak track usage [%]"); axs[1].set_ylim(0, 100)
axs[1].set_title("Routing headroom — peak usage per bin", loc="left", fontsize=12, fontweight="bold", color=INK)
for i, r in enumerate(cg): axs[1].text(i, float(r["max_util"]) * 100 + 1.5, f"{float(r['max_util']) * 100:.0f} %", ha="center", fontsize=10, fontweight="bold")
fig.tight_layout(rect=[0, 0.05, 1, 1])
save(fig, "final_03_routing_layers", "Data: charts/data/congestion_by_layer_v7.csv (final routed DEF). 481,234 vias, global-routing overflow 0, route DRC 0.")
