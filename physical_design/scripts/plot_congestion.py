import json, numpy as np, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os, sys
TAG = os.environ.get("TAG", ""); MAPS = os.environ.get("MAPS", "../charts/data/v6_final_maps.json"); OUTD = os.environ.get("OUTD", "../visuals")
D = json.load(open(MAPS)); B = D["bin"]; N = D["n"]
pitch = {"met1": .34, "met2": .46, "met3": .68, "met4": .92}   # track pitch [µm] from tech LEF
rows = []
fig, axs = plt.subplots(2, 2, figsize=(13, 13.4), dpi=130)
for ax, ly in zip(axs.flat, ["met1", "met2", "met3", "met4"]):
    wl = np.array(D["wire_len"][ly]); util = wl * pitch[ly] / (B * B)       # routed wire / track capacity of the bin (one direction)
    im = ax.imshow(np.clip(util, 0, 1.2), origin="lower", extent=[0, N*B, 0, N*B], cmap="magma", vmin=0, vmax=1.0)
    ax.set_title(f"{ly}: routed wire / track capacity (30 µm bins)  max {util.max():.2f}  mean(nonzero) {util[util>0].mean():.2f}", fontsize=9)
    ax.set_xlim(0, 1800); ax.set_ylim(0, 1800); plt.colorbar(im, ax=ax, fraction=.046)
    rows.append((ly, float(util.max()), float(util[util > 0].mean()), float(wl.sum())))
fig.suptitle(TAG+"06c Routing congestion (post-route): wire length / track capacity per bin and layer", x=0.01, ha="left", fontweight="bold")
fig.text(0.01, 0.005, f"Source: {D['source']} (final routed DEF, 0 DRC); capacity = bin length x tracks (pitch from sky130 tech LEF). Global-route overflow = 0 in all layers.", fontsize=7.5, family="monospace")
fig.tight_layout(rect=[0, 0.02, 1, .97]); fig.savefig(f"{OUTD}/{TAG.strip().lower()+chr(95) if TAG else chr(0)[:0]}06c_routing_congestion_heatmap_final.png")
import csv
with open(os.environ.get("CSV", "../charts/data/congestion_by_layer.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["layer", "max_util", "mean_util_nonzero", "wirelength_um"]); w.writerows(rows)
print(rows)
