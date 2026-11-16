#!/usr/bin/env python3
"""Caravel user_project_wrapper views with the V7 macro (mprj, orientation FS): floorplan, PDN, placement, routing.
Real DEF files rendered headless by KLayout (LibreLane image) and annotated with matplotlib.
usage: vis_wrapper_v8.py <W8_A run dir> <out dir>"""
import json, os, re, subprocess, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.image as mpimg
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

RUN, OUT = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
H = os.path.expanduser("~"); HERE = os.path.dirname(os.path.abspath(__file__))
PDK = f"{H}/.ciel/ciel/sky130/versions/8afc8346a57fe1ab7934ba5a6056ea8b43078e71/sky130A"
IMG = "ghcr.io/librelane/librelane:3.0.11"
LEFS = [f"{PDK}/libs.ref/sky130_fd_sc_hd/techlef/sky130_fd_sc_hd__nom.tlef", f"{PDK}/libs.ref/sky130_fd_sc_hd/lef/sky130_fd_sc_hd.lef",
        f"{H}/omega-fusion-tapeout/signoff_v7/lef_v2/omega_fusion_soc_asic.v2.lef"]
RAW = os.path.join(OUT, "_raw"); os.makedirs(RAW, exist_ok=True)
BOX = [0, 0, 2920, 3520]; MAC = (560, 860, 1800, 1800)
COL = {"met1": "#2d6cdf", "met2": "#e0472b", "met3": "#2da84a", "met4": "#d9a400", "met5": "#8a3fc0"}


def render(defp, name, layers, box=BOX, w=2200, h=2650, special=True):
    out = f"{RAW}/{name}.png"
    jf = f"{RAW}/{name}.json"
    json.dump({"in": defp, "lefs": LEFS, "special": special, "views": [{"out": out, "layers": layers, "box": box, "w": w, "h": h}]}, open(jf, "w"))
    r = subprocess.run(["docker", "run", "--rm", "--entrypoint", "", "-v", f"{H}:{H}", "-e", f"PDK={PDK}", "-e", f"HOME={H}", IMG,
                        "klayout", "-zz", "-r", f"{HERE}/render_klayout.py", "-rd", f"jobs={jf}"], capture_output=True, text=True)
    if r.returncode or "saved" not in r.stdout:
        print(r.stdout[-500:], r.stderr[-800:]); raise SystemExit("klayout failed")
    return out


def annotate(raw, out, title, caption, legend, box=BOX, mac=True):
    fig, ax = plt.subplots(figsize=(10, 11.6), dpi=150)
    ax.imshow(mpimg.imread(raw), extent=[box[0], box[2], box[1], box[3]], origin="upper", interpolation="nearest")
    ax.set_xlabel("x [µm]"); ax.set_ylabel("y [µm]")
    ax.set_title(title, fontsize=13, fontweight="bold", loc="left")
    ax.add_patch(Rectangle((0, 0), 2920, 3520, fill=False, ec="black", lw=1.4))
    if mac:
        ax.add_patch(Rectangle(MAC[:2], MAC[2], MAC[3], fill=False, ec="#d62728", lw=2.2))
        ax.text(MAC[0] + 40, MAC[1] + MAC[3] - 90, "mprj: omega_fusion_soc_asic 1800 × 1800 µm", color="#d62728", fontsize=10, fontweight="bold")
    ax.legend(handles=[Line2D([0], [0], color=c, lw=5, label=l) for l, c in legend], loc="lower right", fontsize=9, framealpha=.92)
    fig.text(0.01, 0.006, caption, fontsize=8, va="bottom", family="monospace")
    fig.subplots_adjust(bottom=0.08)
    fig.savefig(out, dpi=150); plt.close(fig); print("wrote", out)


r = lambda s, f="user_project_wrapper.def": f"{RUN}/{s}/{f}"
def parse_pins(defp):
    pins, cur, sec = [], None, False
    for line in open(defp):
        if line.startswith("PINS"): sec = True; continue
        if line.startswith("END PINS"): break
        if not sec: continue
        m = re.match(r"\s*-\s+(\S+)\s+\+\s+NET", line)
        if m: cur = m.group(1)
        m = re.search(r"\+\s+(?:PLACED|FIXED)\s+\(\s*(-?\d+)\s+(-?\d+)\s*\)", line)
        if m and cur: pins.append((cur, int(m.group(1)) / 1000, int(m.group(2)) / 1000)); cur = None
    return pins


def floorplan():
    pins = parse_pins(r("24-openroad-globalplacement"))
    groups = [("wb_ / wbs_ (Wishbone)", ("wb_", "wbs_"), "#2d6cdf"), ("la_ (logic analyzer)", ("la_",), "#2da84a"), ("user_irq", ("user_irq",), "#e0472b"),
              ("io_ / analog / gpio", ("io_", "analog", "gpio"), "#999999"), ("power / other", ("",), "#d9a400")]
    fig, ax = plt.subplots(figsize=(10, 11.6), dpi=150)
    ax.add_patch(Rectangle((0, 0), 2920, 3520, fill=False, ec="black", lw=1.6))
    ax.add_patch(Rectangle(MAC[:2], MAC[2], MAC[3], fc="#fbe3e3", ec="#d62728", lw=2.2))
    ax.text(MAC[0] + MAC[2] / 2, MAC[1] + MAC[3] / 2, "mprj\nomega_fusion_soc_asic\n1800 × 1800 µm\n(orientation FS)", ha="center", va="center", fontsize=14, color="#d62728", fontweight="bold")
    seen = set()
    for n, x, y in pins:
        for lab, pre, col in groups:
            if n.startswith(pre):
                ax.scatter([x], [y], s=14, c=col, label=lab if lab not in seen else None, zorder=3); seen.add(lab); break
    ax.annotate("macro output pins face this edge", xy=(1460, 860), xytext=(1460, 420), ha="center", color="#d62728", arrowprops=dict(arrowstyle="->", color="#d62728"), fontsize=10)
    ax.set_xlim(-100, 3020); ax.set_ylim(-100, 3620); ax.set_aspect("equal"); ax.set_xlabel("x [µm]"); ax.set_ylabel("y [µm]")
    ax.set_title("Caravel user_project_wrapper — floorplan: macro placed facing the south I/O", fontsize=13, fontweight="bold", loc="left")
    ax.legend(loc="upper right", fontsize=9, framealpha=.92)
    fig.text(0.01, 0.006, "Die 2920 × 3520 µm, mprj at (560, 860), orientation FS: the 92 output pins on the macro's top edge now face the wrapper pins on the south edge.\nSource: LibreLane run W8_A steps 13/24 (macro placement; I/O pins applied from the Caravel template), parsed from the DEF.", fontsize=8, va="bottom", family="monospace")
    fig.subplots_adjust(bottom=0.08); fig.savefig(f"{OUT}/w8_01_wrapper_floorplan_macro_pins.png", dpi=150); plt.close(fig)


floorplan()
annotate(render(r("17-openroad-generatepdn"), "w8_pdn", ["met4", "met5"]), f"{OUT}/w8_02_wrapper_pdn.png",
         "Caravel wrapper — power distribution network (8 power nets)",
         "met4 vertical + met5 horizontal stripes of the wrapper over the macro's own met4 straps.\nSource: LibreLane run W8_A step 17 (OpenROAD.GeneratePDN), DEF rendered with KLayout.",
         [("met4", COL["met4"]), ("met5", COL["met5"])])
annotate(render(r("24-openroad-globalplacement"), "w8_place", ["OUTLINE"], special=False), f"{OUT}/w8_03_wrapper_placement.png",
         "Caravel wrapper — global placement of wrapper logic around the macro",
         "Standard-cell outlines of the wrapper glue/buffers (small boxes) around the hard macro.\nSource: LibreLane run W8_A step 24 (OpenROAD.GlobalPlacement), DEF rendered with KLayout.",
         [("cell outlines", "#000000")])
annotate(render(r("41-openroad-detailedrouting"), "w8_route", ["met1", "met2", "met3", "met4", "met5"], special=False), f"{OUT}/w8_04_wrapper_detailed_routing.png",
         "Caravel wrapper — detailed routing (0 route DRC, 0 antenna violations)",
         "Signal routes between the wrapper pins and the macro pins. The macro interior is an opaque LEF abstract.\nSource: LibreLane run W8_A step 41 (OpenROAD.DetailedRouting), DEF rendered with KLayout.",
         [(k, v) for k, v in COL.items()])
