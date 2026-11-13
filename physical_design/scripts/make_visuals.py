#!/usr/bin/env python3
"""Render REAL physical views (KLayout headless in the LibreLane image) and annotate with matplotlib.
Every PNG is produced from the DEF/GDS named in its caption; nothing is synthetic.
usage: make_visuals.py <spec_name|all>   (specs defined below; paths via env RUN_V4 RUN_FINAL GDS)"""
import json, os, subprocess, sys, re
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.image as mpimg
from matplotlib.patches import Rectangle
H = os.path.expanduser("~"); OF = H + "/omega-fusion-tapeout"; VIS = OF + "/release/visuals"; TMP = VIS + "/_raw"
PDKV = "8afc8346a57fe1ab7934ba5a6056ea8b43078e71"; PDK = f"{H}/.ciel/ciel/sky130/versions/{PDKV}/sky130A"
IMG = "ghcr.io/librelane/librelane:3.0.11"
LEFS = [f"{PDK}/libs.ref/sky130_fd_sc_hd/techlef/sky130_fd_sc_hd__nom.tlef", f"{PDK}/libs.ref/sky130_fd_sc_hd/lef/sky130_fd_sc_hd.lef"]
os.makedirs(TMP, exist_ok=True)
RUNS = OF + "/openlane/omega_fusion_soc_v2/runs"
COL = {"li1": "#9a9a9a", "met1": "#2d6cdf", "met2": "#e0472b", "met3": "#2da84a", "met4": "#d9a400", "met5": "#8a3fc0"}

def klayout(path, views, lefs=True):
    """views: list of dict(out, layers, box, w, h)"""
    job = {"in": path, "lefs": LEFS if lefs else [], "views": views}
    jf = f"{TMP}/job_{abs(hash(path+str(views)))}.json"; json.dump(job, open(jf, "w"))
    cmd = ["docker", "run", "--rm", "--entrypoint", "", "-v", f"{H}:{H}", "-e", f"PDK={PDK}", "-e", f"HOME={H}", IMG,
           "klayout", "-zz", "-r", f"{OF}/release/scripts/render_klayout.py", "-rd", f"jobs={jf}"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode or "saved" not in r.stdout: print(r.stdout[-500:], r.stderr[-800:]); raise SystemExit("klayout failed")

def annotate(raw, out, box, title, source, notes="", legend=None, extra=None, dpi=150):
    img = mpimg.imread(raw)
    fig, ax = plt.subplots(figsize=(11, 11.8), dpi=dpi)
    ax.imshow(img, extent=[box[0], box[2], box[1], box[3]], origin="upper", interpolation="nearest")
    ax.set_xlabel("x [µm]"); ax.set_ylabel("y [µm]")
    ax.set_title(title, fontsize=13, fontweight="bold", loc="left")
    if legend:
        from matplotlib.lines import Line2D
        ax.legend(handles=[Line2D([0], [0], color=c, lw=5, label=l) for l, c in legend], loc="upper right", fontsize=9, framealpha=.9)
    if extra: extra(ax)
    fig.text(0.01, 0.005, f"Source: {source}\n{notes}", fontsize=7.5, va="bottom", family="monospace")
    fig.subplots_adjust(bottom=0.09)
    fig.savefig(out, dpi=dpi); plt.close(fig); print("wrote", out)

def parse_def_pins(defp):
    pins = []; insec = False; cur = None
    for line in open(defp):
        if line.startswith("PINS"): insec = True; continue
        if line.startswith("END PINS"): break
        if not insec: continue
        m = re.match(r"\s*-\s+(\S+)\s+\+\s+NET", line)
        if m: cur = m.group(1)
        m = re.search(r"\+\s+(?:PLACED|FIXED)\s+\(\s*(-?\d+)\s+(-?\d+)\s*\)", line)
        if m and cur: pins.append((cur, int(m.group(1)) / 1000, int(m.group(2)) / 1000)); cur = None
    return pins

def full_box(): return [0, 0, 1800, 1800]
