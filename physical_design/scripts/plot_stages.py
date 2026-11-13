#!/usr/bin/env python3
"""Plots from REAL ODB geometry dumps (dump_insts.py). usage: plot_stages.py <kind> <geom.json> <out.png> <stage-label> <source-odb> [zoom x1,y1,x2,y2]
kind: floorplan | placement | density | cts"""
import sys, json, re, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection, LineCollection
from matplotlib.patches import Rectangle
kind, gj, out, label, src = sys.argv[1:6]
zoom = [float(v) for v in sys.argv[6].split(",")] if len(sys.argv) > 6 else None
D = json.load(open(gj)); I = D["insts"]; die = D["die"]; core = D["core"]
COL = {"tap": "#bbbbbb", "fill": "#dddddd", "seq": "#d62728", "comb": "#1f77b4", "clk": "#2ca02c", "delay": "#ff7f0e", "buf": "#9467bd", "antenna": "#000000"}
NAME = {"tap": "tap cells", "seq": "flip-flops/latches", "comb": "combinational", "clk": "clkbuf*/clkinv* cells (counted by name, includes non-CTS buffers)", "delay": "delay/hold/IO buffers", "buf": "repair buffers/inv", "antenna": "antenna diodes", "fill": "fill"}
fig, ax = plt.subplots(figsize=(11, 11.6), dpi=150)
box = zoom if zoom else die
ax.set_xlim(box[0], box[2]); ax.set_ylim(box[1], box[3]); ax.set_aspect("equal")
def inbox(r): return not (r[5] < box[0] or r[3] > box[2] or r[6] < box[1] or r[4] > box[3])
sel = [r for r in I if inbox(r)]
if kind in ("floorplan", "placement", "cts"):
    order = ["fill", "tap", "comb", "buf", "delay", "seq", "clk", "antenna"]
    show = {"floorplan": ["tap"], "placement": order, "cts": order}[kind]
    for c in order:
        if c not in show: continue
        rs = [r for r in sel if r[2] == c and (r[7] or kind == "floorplan")]
        if not rs: continue
        polys = [[(r[3], r[4]), (r[5], r[4]), (r[5], r[6]), (r[3], r[6])] for r in rs]
        ax.add_collection(PolyCollection(polys, facecolors=COL[c], edgecolors="none" if not zoom else "#00000033", linewidths=0.2, label=f"{NAME[c]} ({sum(1 for r in I if r[2]==c)})"))
    ax.set_facecolor("white")
if kind == "cts":
    pos = {r[0]: ((r[3] + r[5]) / 2, (r[4] + r[6]) / 2) for r in I}
    lv = lambda n: int(m.group(1)) if (m := re.match(r"clknet_(\d+)_", n)) else (0 if n.startswith("clknet_0") else 9)
    segs = {}
    for nm, drv, loads in D["clk_edges"]:
        if drv not in pos: continue
        k = "leaf" if "leaf" in nm else ("upper" if re.match(r"clknet_\d+_", nm) or nm == "clknet_0_clk" else "other")
        for l in loads:
            if l in pos: segs.setdefault(k, []).append([pos[drv], pos[l]])
    for k, c, lw in [("upper", "#111111", 0.9 if not zoom else 1.4), ("leaf", "#2ca02c55", 0.25 if not zoom else 0.6)]:
        if k in segs: ax.add_collection(LineCollection(segs[k], colors=c, linewidths=lw, label=f"clock net connectivity (driver->load, straight lines, not routed wires): {k} ({len(segs[k])})"))
if kind == "floorplan":
    ax.add_patch(Rectangle((die[0], die[1]), die[2]-die[0], die[3]-die[1], fill=False, ec="black", lw=2, label=f"die {die[2]-die[0]:.0f} x {die[3]-die[1]:.0f} µm"))
    ax.add_patch(Rectangle((core[0], core[1]), core[2]-core[0], core[3]-core[1], fill=False, ec="#d62728", lw=1.5, ls="--", label=f"core {core[2]-core[0]:.1f} x {core[3]-core[1]:.1f} µm (origin {core[0]:.1f},{core[1]:.1f})"))
    side = {"N": [], "S": [], "E": [], "W": []}
    for n, x1, y1, x2, y2, t in D["pins"]:
        cx, cy = (x1+x2)/2, (y1+y2)/2
        s = "S" if cy < 5 else "N" if cy > die[3]-5 else "W" if cx < 5 else "E" if cx > die[2]-5 else None
        if s: side[s].append((cx, cy))
    for s, pts in side.items():
        if pts: ax.scatter(*zip(*pts), s=14, marker="s", label=f"IO pins {s}: {len(pts)}", zorder=5)
    ax.annotate("", xy=(die[2], -30), xytext=(die[0], -30), arrowprops=dict(arrowstyle="<->")); ax.text(900, -75, f"{die[2]-die[0]:.0f} µm", ha="center")
    ax.annotate("", xy=(-30, die[3]), xytext=(-30, die[1]), arrowprops=dict(arrowstyle="<->")); ax.text(-85, 900, f"{die[3]-die[1]:.0f} µm", rotation=90, va="center")
    ax.set_xlim(-140, die[2]+60); ax.set_ylim(-140, die[3]+60)
    area = sum((r[5]-r[3])*(r[6]-r[4]) for r in I if r[2] not in ("tap", "fill"))
    ax.set_title(f"{label}\nusable core {(core[2]-core[0])*(core[3]-core[1])/1e6:.3f} mm² | die {(die[2]-die[0])*(die[3]-die[1])/1e6:.2f} mm²", loc="left", fontsize=11, fontweight="bold")
elif kind == "density":
    B = 30.0; nx = int((box[2]-box[0])//B)+1; ny = int((box[3]-box[1])//B)+1; g = np.zeros((ny, nx))
    for r in I:
        if r[2] in ("tap", "fill"): continue
        cx, cy = (r[3]+r[5])/2, (r[4]+r[6])/2
        g[min(int((cy-box[1])//B), ny-1), min(int((cx-box[0])//B), nx-1)] += (r[5]-r[3])*(r[6]-r[4])
    util = g / (B*B)
    im = ax.imshow(util, origin="lower", extent=[box[0], box[0]+nx*B, box[1], box[1]+ny*B], cmap="inferno", vmin=0, vmax=max(0.6, util.max()))
    plt.colorbar(im, ax=ax, fraction=0.04, label="std-cell area / bin area (functional cells, 30 µm bins)")
    ax.set_title(f"{label}\nmax bin utilization {util.max():.2f}, mean {util[util>0].mean():.2f}", loc="left", fontsize=11, fontweight="bold")
else:
    ax.set_title(label, loc="left", fontsize=12, fontweight="bold")
if kind != "density": ax.legend(loc="upper right", fontsize=7.5, framealpha=.92)
ax.set_xlabel("x [µm]"); ax.set_ylabel("y [µm]")
fig.text(0.01, 0.005, f"Source: {src}\nReal instance geometry extracted from the ODB with OpenROAD (dump_insts.py); {len(I)} instances.", fontsize=7.5, family="monospace", va="bottom")
fig.subplots_adjust(bottom=0.08)
fig.savefig(out); print("wrote", out)
