#!/usr/bin/env python3
"""GRT guide visualisation from the REAL after_grt.guide file. usage: plot_grt.py <guide> <outdir> <source-label>"""
import sys, numpy as np, collections
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
guide, outdir, src = sys.argv[1:4]
import os; TAG = os.environ.get("TAG", "")   # e.g. "V7 " : prefix for titles and file names
L = collections.defaultdict(list); nets = 0; cur = None
for ln in open(guide):
    p = ln.split()
    if len(p) == 5: L[p[4]].append((int(p[0])/1000, int(p[1])/1000, int(p[2])/1000, int(p[3])/1000))
    elif len(p) == 1 and p[0] not in "()": nets += 1
B = 30.0; N = int(1800//B)+1
cap_pitch = {"met1": .34, "met2": .46, "met3": .68, "met4": .92}
tot = {k: sum((r[2]-r[0])*(r[3]-r[1]) for r in v) for k, v in L.items()}
fig, axs = plt.subplots(2, 2, figsize=(13, 13.4), dpi=130)
for ax, ly in zip(axs.flat, ["met1", "met2", "met3", "met4"]):
    g = np.zeros((N, N))
    for x1, y1, x2, y2 in L[ly]:
        i0, i1 = int(x1//B), int((x2-1e-6)//B); j0, j1 = int(y1//B), int((y2-1e-6)//B)
        for j in range(j0, j1+1):
            for i in range(i0, i1+1):
                ox = min(x2, (i+1)*B)-max(x1, i*B); oy = min(y2, (j+1)*B)-max(y1, j*B)
                if ox > 0 and oy > 0: g[j, i] += ox*oy
    f = g/(B*B)
    im = ax.imshow(np.clip(f, 0, 1), origin="lower", extent=[0, N*B, 0, N*B], cmap="viridis", vmin=0, vmax=1)
    ax.set_title(f"{ly}: GRT guide coverage per 30 µm bin ({len(L[ly])} guide rects)", fontsize=9)
    ax.set_xlim(0, 1800); ax.set_ylim(0, 1800); plt.colorbar(im, ax=ax, fraction=.046, label="guide area / bin area")
    np.save(f"{outdir}/grt_guide_cov_{ly}.npy", f)
fig.suptitle(TAG+"06 Global routing - guides per layer (met1-met4)", x=0.01, ha="left", fontweight="bold")
fig.text(0.01, 0.005, f"Source: {src}  ({nets} nets, global routing overflow 0).  Guide coverage is the routed-demand footprint, not final wires.", fontsize=7.5, family="monospace")
fig.tight_layout(rect=[0, 0.02, 1, .97]); fig.savefig(f"{outdir}/{TAG.strip().lower().replace(chr(32),chr(95))+chr(95) if TAG else chr(0)[:0]}06_global_routing_guides_by_layer.png"); print("wrote 06")
# overview: all guides, metal layers coloured
fig, ax = plt.subplots(figsize=(11, 11.6), dpi=150)
for ly, c in [("met1", "#2d6cdf"), ("met2", "#e0472b"), ("met3", "#2da84a"), ("met4", "#d9a400")]:
    polys = [[(a, b), (c_, b), (c_, d), (a, d)] for a, b, c_, d in L[ly]]
    ax.add_collection(PolyCollection(polys, facecolors=c, edgecolors="none", alpha=.45, label=f"{ly} guides"))
ax.set_xlim(0, 1800); ax.set_ylim(0, 1800); ax.set_aspect("equal"); ax.legend(loc="upper right")
ax.set_title(TAG+"06 Global routing - all guide segments met1-met4 (overlay)", loc="left", fontweight="bold"); ax.set_xlabel("x [µm]"); ax.set_ylabel("y [µm]")
fig.text(0.01, 0.005, f"Source: {src}", fontsize=7.5, family="monospace"); fig.subplots_adjust(bottom=.07)
fig.savefig(f"{outdir}/{TAG.strip().lower().replace(chr(32),chr(95))+chr(95) if TAG else chr(0)[:0]}06b_global_routing_guides_overlay.png"); print("wrote 06b")
