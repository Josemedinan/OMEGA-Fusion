#!/usr/bin/env python3
"""Builds docs/results/OMEGA_Fusion_V7_presentation.pdf (18 slides, 16:9) from files in this repository only
(images in visuals/, charts in charts/, numbers from physical_design/reports/v7/metrics.json and docs/results/*).
Every picture slide states the version of the layout it shows. Requires matplotlib (+ Pillow via matplotlib)."""
import json, os, textwrap, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.image as mpimg
from matplotlib.backends.backend_pdf import PdfPages
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *a: os.path.join(root, *a)
M7 = json.load(open(P("physical_design/reports/v7/metrics.json"))); M6 = json.load(open(P("physical_design/reports/signoff_v6/metrics.json")))
NAVY, BLUE, GREY, RED, GREEN = "#14233b", "#2d6cdf", "#555555", "#c0392b", "#2d8a4a"
W, H = 13.333, 7.5
pdf = PdfPages(P("docs/results/OMEGA_Fusion_V7_presentation.pdf")); n = [0]

def slide(title, sub=None):
    n[0] += 1
    fig = plt.figure(figsize=(W, H)); fig.patch.set_facecolor("white")
    fig.add_artist(plt.Rectangle((0, 0.915), 1, 0.085, transform=fig.transFigure, color=NAVY))
    fig.text(0.035, 0.945, f"{n[0]:02d}  {title}", color="white", fontsize=20, fontweight="bold", va="center")
    if sub: fig.text(0.035, 0.885, sub, color=GREY, fontsize=11.5, va="center")
    fig.text(0.035, 0.018, "OMEGA-Fusion · SKY130A sky130_fd_sc_hd · V7 candidate = LibreLane run OMEGA_V15_RT (2026-11-13) · TAPEOUT_READY = NO", color=GREY, fontsize=8)
    return fig

def text(fig, x, y, lines, size=12, w=0.9, color=NAVY, bullet=True, gap=1.55):
    yy = y
    for ln in lines:
        head = ln.startswith("**")
        t = ln.strip("*") if head else ln
        for k, part in enumerate(textwrap.wrap(t, int(w * 150 / (size / 11))) or [""]):
            fig.text(x, yy, (("• " if bullet and not head else "") if k == 0 else "   ") + part, fontsize=size, color=BLUE if head else color, fontweight="bold" if head else "normal", va="top")
            yy -= size * gap / 700
        yy -= size * 0.5 / 700

def image(fig, rect, path, caption, border=True):
    ax = fig.add_axes(rect); ax.imshow(mpimg.imread(P(path))); ax.axis("off")
    fig.text(rect[0], rect[1] - 0.012, caption, fontsize=8.5, color=GREY, va="top")
    return ax

def table(fig, rect, rows, colw=None, size=10.5, head=True):
    ax = fig.add_axes(rect); ax.axis("off")
    t = ax.table(cellText=rows[1:] if head else rows, colLabels=rows[0] if head else None, loc="upper left", cellLoc="left", colWidths=colw)
    t.auto_set_font_size(False); t.set_fontsize(size); t.scale(1, 2.05)
    for (r, c), cell in t.get_celld().items():
        cell.set_edgecolor("#cccccc")
        if r == 0 and head: cell.set_facecolor(NAVY); cell.set_text_props(color="white", fontweight="bold")
        else:
            s = cell.get_text().get_text()
            if s.startswith("PASS"): cell.set_text_props(color=GREEN, fontweight="bold")
            elif s.startswith("FAIL"): cell.set_text_props(color=RED, fontweight="bold")
            elif s.startswith("UNVERIFIED"): cell.set_text_props(color="#b36b00", fontweight="bold")
    return t

def done(fig):
    pdf.savefig(fig)
    if os.environ.get("PREVIEW"): fig.savefig(os.path.join(os.environ["PREVIEW"], f"slide_{n[0]:02d}.png"), dpi=60)
    plt.close(fig)

# 1 problem + title
f = slide("OMEGA-Fusion — RV32I-subset SoC with an INT4/INT8 matrix accelerator", "RTL-to-GDSII on SKY130 with open-source tools · problem and motivation")
text(f, 0.04, 0.82, ["**Problem", "Small ML/DSP workloads (INT4/INT8 matrix products) are expensive to run on a general-purpose controller; an accelerator next to a tiny CPU is the classic answer, but few open examples go all the way to a verified layout.",
    "**What this project is", "A deliberately small, single-cycle RV32I SUBSET controller (10 instructions), a 256×32 programmable instruction RAM and a 4×4 INT8/INT4 matrix engine with MMIO + DMA loader, taken from SystemVerilog to a routed, DRC/LVS-checked GDSII macro on SKY130A.",
    "**What it is not", "Not a compliant RISC-V core (no CSR/traps/interrupts/pipeline); not fabricated; not tapeout-ready (see slides 17-18)."], 12.5, 0.5)
image(f, [0.56, 0.12, 0.40, 0.70], "visuals/00_hero_final_gds_klayout.png", "V7 final GDS (met1–met4), KLayout 0.30.7 — run OMEGA_V15_RT"); done(f)
# 2 architecture
f = slide("SoC architecture", "every block exists in the RTL (rtl/, caravel/rtl/)")
image(f, [0.04, 0.10, 0.62, 0.76], "docs/architecture/soc_block_diagram.png", "Block diagram generated from the RTL facts (scripts/make_architecture_diagram.py)")
text(f, 0.69, 0.84, ["**Key facts", "CPU: LUI ADD ADDI SLLI ANDI LW SW BEQ BLT JAL; 32×32 register file; halts on illegal instruction.", "IMEM: 256×32 flip-flops, loaded through pins while run=0 (no SRAM macro).", "Accelerator: 16 lanes × 4 steps (folded), INT8/INT4 signed, 32-bit results; 8-word DMA loader; IRQ level output.", "Host: one-cycle MMIO bus, not AXI. Caravel: Wishbone bridge in caravel/rtl."], 11, 0.28); done(f)
# 3 flow
f = slide("RTL-to-GDSII flow", "LibreLane 3.0.11 (Classic) in Docker — every stage is resumable")
steps = [("RTL", "SystemVerilog\nVerilator/Icarus"), ("Synthesis", "Yosys 0.62\n43,448 cells"), ("Floorplan\n+ PDN", "1800×1800 µm\nmet1/met4 grid"), ("Placement", "global → legal\nOpenROAD"), ("CTS", "TritonCTS\n10,323 sinks"), ("Routing", "GRT → TritonRoute\nantenna repair"), ("ECO", "real-SPEF resize,\nhold & closure"), ("Signoff", "Magic/KLayout DRC\nNetgen LVS, STA")]
ax = f.add_axes([0.03, 0.30, 0.94, 0.45]); ax.axis("off"); ax.set_xlim(0, 8); ax.set_ylim(0, 1)
for i, (a, b) in enumerate(steps):
    ax.add_patch(plt.Rectangle((i + 0.05, 0.25), 0.82, 0.5, color=BLUE if i < 7 else NAVY, alpha=0.9)); ax.text(i + 0.46, 0.6, a, ha="center", va="center", color="white", fontsize=10.5, fontweight="bold"); ax.text(i + 0.46, 0.38, b, ha="center", va="center", color="white", fontsize=8)
    if i < 7: ax.annotate("", xy=(i + 1.05, 0.5), xytext=(i + 0.87, 0.5), arrowprops=dict(arrowstyle="-|>", color=GREY))
text(f, 0.04, 0.26, ["Tools: LibreLane 3.0.11 · OpenROAD dcf36133a3 · Yosys 0.62 · Magic 8.3.623 · KLayout 0.30.7 · Netgen 1.5.316 · SKY130A (ciel 8afc8346…).", "Host: 8 GB MacBook Air M3 — flow ran one Docker job at a time; wrapper-level DRC/LVS did not fit (documented)."], 11.5, 0.9); done(f)
# 4 RTL sim
f = slide("RTL simulation and functional verification", "2026-11-13, Verilator 5.053 + Icarus Verilog, from the repository layout (verification/*.log)")
table(f, [0.04, 0.25, 0.92, 0.6], [["Check", "Result", "Scope / limit"],
    ["Python reference, 4,000 random INT4/INT8 tiles", "PASS", "software oracle only"], ["Firmware emulator (instruction level)", "PASS", "124 instructions, C[0,0]=4"],
    ["Directed accelerator test, FOLDED=0 and 1", "PASS", "8 matrix cases, 128 outputs; INT8/INT4, host/DMA, IRQ, error paths"],
    ["SoC demo + ASIC SoC (IMEM → CPU → MMIO MAC)", "PASS", "C[0,0]=4, IRQ=1"], ["Caravel wrapper lint, Wishbone/DMA, wrapper→SoC", "PASS", "RTL only"],
    ["Gate-level, V7 post-route netlist (zero delay)", "PASS", "same test as RTL; functional cell models"], ["SDF back-annotated simulation", "UNVERIFIED", "not run"], ["Formal equivalence (EQY)", "UNVERIFIED", "not run"]], [0.42, 0.14, 0.44])
text(f, 0.04, 0.2, ["Depth is modest: one firmware program, one directed accelerator test (8 cases), a random-tile oracle. No ISA compliance suite, coverage or constrained-random RTL regression."], 11, 0.9); done(f)
# 5 synthesis
f = slide("Synthesis", "Yosys 0.62 → sky130_fd_sc_hd (V2 checkpoint, unchanged by V7)")
text(f, 0.04, 0.82, ["43,448 cells after synthesis (before taps, buffering, CTS, repair).", f"Final V7 layout: {M7['design__instance__count__stdcell']:,} instances incl. 43,470 tap cells and {M7['design__instance__count__class:sequential_cell']:,} flip-flops; {M7['design__instance__count__class:fill_cell']:,} fill cells on top.", "The 256×32 instruction RAM and the register file map to flip-flops and muxes (no SRAM macro) — this dominates the area and is the first thing to change in a next revision.", "Programmable IMEM was chosen on purpose: a ROM baked into the netlist lets synthesis prune parts of the datapath.", "The folded MAC cuts multiplier operators 4× (64 → 16) but the area/energy gain versus the parallel variant was NOT measured."], 12.5, 0.88); done(f)
# 6 floorplan
f = slide("Floorplan — V7 (shared with V4–V6)", "die 1800×1800 µm, core 3.055 mm², 179 pins")
image(f, [0.04, 0.08, 0.50, 0.80], "visuals/v7/v7_01_floorplan_die_core_pins.png", "V7 01 — floorplan stage database (unchanged through V7); OpenROAD-extracted geometry")
text(f, 0.57, 0.82, ["Requested outline kept: 1800×1800 µm; core 1749.4×1746.2 µm after row snapping.", "179 pins: 116 N, 42 S, 11 E, 8 W (incl. power).", "43,470 tap cells, utilization ≈ 28 % — easy routing and antenna closure, but area-inefficient."], 12, 0.38); done(f)
# 7 PDN
f = slide("Power distribution network — V7 (shared with V4–V6)", "met1 rails + met4 straps, VDD/VSS, no core ring")
image(f, [0.03, 0.08, 0.44, 0.78], "visuals/v7/v7_02a_pdn_full_vdd_vss.png", "V7 02a — PDN-only database (grid generated once, shared by V4–V7)")
image(f, [0.52, 0.30, 0.44, 0.56], "visuals/v7/v7_02b_pdn_zoom_40um.png", "V7 02b — 40 µm zoom; via cuts are not drawn by the DEF importer (connectivity proven by PSM)")
text(f, 0.52, 0.22, ["Rails every 2.72 µm; straps pitch 153.6 µm, 1.6 µm wide.", "IR drop (V6 run, nom_ss, 12.6 mW): 0.09 mV worst — PDN is far from limiting."], 10.5, 0.44); done(f)
# 8 placement
f = slide("Placement — global (V4 base) and final detailed (V7)", "titles on the images state which run each comes from")
image(f, [0.02, 0.10, 0.31, 0.74], "visuals/v7/v4_03_global_placement_full.png", "V4 03 — global placement of the V4 base run (NOT the V7 final)")
image(f, [0.345, 0.10, 0.31, 0.74], "visuals/v7/v7_04a_detailed_placement_full.png", "V7 04a — final detailed placement, cells by class")
image(f, [0.67, 0.10, 0.31, 0.74], "visuals/v7/v7_03b_placement_density_heatmap.png", "V7 03b — density (cell area / 30 µm bin)"); done(f)
# 9 CTS
f = slide("Clock tree synthesis — V7", "TritonCTS tree + 22 ECO clock-path buffers (clones of 16+4 drivers, 2 root buffers)")
image(f, [0.03, 0.08, 0.46, 0.78], "visuals/v7/v7_05a_cts_clock_tree_full.png", "V7 05a — clock net connectivity (straight lines, not wires), 10,323 sinks")
image(f, [0.52, 0.30, 0.44, 0.56], "visuals/v7/v7_05b_cts_clock_tree_zoom_250um.png", "V7 05b — 250 µm zoom")
text(f, 0.52, 0.22, [f"As built by TritonCTS: {M7['design__instance__count__class:clock_buffer']:,} buffers + {M7['design__instance__count__class:clock_inverter']} inverters; insertion delay 3.3–5.2 ns in SS.", "Legend counts by cell name (clkbuf*/clkinv*) include non-CTS buffers; the flow metric above is authoritative."], 10.5, 0.44); done(f)
# 10 routing
f = slide("Routing — V7", "global-routing guides, congestion and final detailed routing (route DRC = 0)")
image(f, [0.02, 0.10, 0.31, 0.74], "visuals/v7/v7_06b_global_routing_guides_overlay.png", "V7 06b — GRT guides (OMEGA_V15_RT/01), overflow 0")
image(f, [0.345, 0.10, 0.31, 0.74], "visuals/v7/v7_06c_routing_congestion_heatmap_final.png", "V7 06c — routed wire / track capacity, max 0.41/0.62/0.70/0.56 (met1–4)")
image(f, [0.67, 0.10, 0.31, 0.74], "visuals/v7/v7_07a_detailed_routing_all_layers.png", "V7 07a — final routed DEF, met1–met4"); done(f)
# 11 GDS
f = slide("Final GDSII — V7", f"Magic stream-out, sha256 275337f0…; wirelength {M7['route__wirelength']/1e6:.3f} m, {M7['route__vias']:,} vias (all single-cut)")
image(f, [0.03, 0.08, 0.40, 0.78], "visuals/v7/v7_08a_final_gds_full_chip.png", "V7 08a — full chip, KLayout, sky130A layer colours")
image(f, [0.45, 0.08, 0.26, 0.78], "visuals/v7/v7_08b_final_gds_core_zoom_120um.png", "V7 08b — 120×120 µm core")
image(f, [0.73, 0.08, 0.26, 0.78], "visuals/v7/v7_08d_final_gds_cell_level_22um.png", "V7 08d — 22×22 µm: diff, poly, li1, mcon, met1"); done(f)
# 12 phys verification
f = slide("Physical verification — V7 (run on the V7 files themselves)", "V6 evidence is not reused; V7 values from physical_design/reports/v7/")
table(f, [0.04, 0.22, 0.92, 0.62], [["Check", "Result", "Evidence"],
    ["DRC Magic / KLayout (sky130A deck)", "PASS 0 / 0", "metrics.json: magic__drc_error__count, klayout__drc_error__count"], ["Routing DRC (TritonRoute)", "PASS 0", "route__drc_errors"],
    ["LVS (Netgen)", "PASS match", "68,162 devices / 67,003 nets, 0 differences"], ["XOR Magic vs KLayout stream-out", "PASS 0", "design__xor_difference__count"],
    ["Antenna after detailed routing", "PASS 0 / 0", "0 nets, 0 pins (184 before repair)"], ["Disconnected pins / illegal overlaps", "PASS 0 / 0", "metrics.json"],
    ["Max slew 0.75 ns / cap 0.2 pF (9 corners)", "PASS 0 / 0", "flow STA + independent STA agree"], ["Max fanout 10", "FAIL 1 net", "net2070: 10 gates + 1 diode = 11 loads; see NET2070_ANALYSIS.md"]], [0.34, 0.14, 0.52])
text(f, 0.04, 0.14, ["net2070 is a project SDC rule (Liberty defines no max_fanout): load 0.067 pF (33 % of limit), slew 0.287 ns (38 %), paths through it have +76 ns setup / +5 ns hold slack. Left open on purpose; limit not relaxed."], 10.5, 0.92); done(f)
# 13 timing
f = slide("Multicorner timing — V6 vs V7", "9 PVT/RC corners, extracted SPEF, SDC v4, independent OpenROAD STA (flow STA agrees)")
image(f, [0.03, 0.30, 0.94, 0.58], "charts/19_v6_v7_slack_per_corner.png", "charts/19 — per-corner worst setup and hold slack (data: charts/data/v6_v7_corner_slack.csv)")
text(f, 0.04, 0.23, ["V7: setup +54.67 ns (max_ss), hold ≥ +0.102 ns; recovery +88.7 ns, removal +0.466 ns on rst_n; check_setup empty.", "Honest detail: in min_ff the V7 hold slack (+0.1018 ns) is 2 ps below V6 (+0.1037 ns); the big gain is max_ff (+0.017 → +0.104 ns) and the SS corners."], 11, 0.9); done(f)
# 14 evolution
f = slide("Evolution V6 → V7", "nine ECO/re-route iterations, each measured post-route (antenna 0 and route DRC 0 every time)")
image(f, [0.03, 0.20, 0.94, 0.68], "charts/18_eco_iterations_v6_to_v7.png", "charts/18 — data: charts/data/v7_iterations.csv; report: docs/results/V7_ECO_REPORT.md")
text(f, 0.04, 0.15, ["Root causes: clock-tree nodes with 16–17 sinks; weak drivers on long wires; antenna diodes left far from their driver after net splits; diodes counted as fanout. V14 had no GDS/DRC/LVS (flow stopped), so V7 = V15."], 10.5, 0.92); done(f)
# 15 PPA
f = slide("Results: PPA", "V6 vs V7; power is an OpenROAD estimate (nom_tt, default activity), not a measurement")
image(f, [0.03, 0.36, 0.94, 0.50], "charts/20_v6_v7_ppa.png", "charts/20 — data: charts/data/v6_v7_ppa.csv")
text(f, 0.04, 0.30, [f"Target 10 MHz (100 ns). V7: {M7['design__instance__area__stdcell']/1e6:.3f} mm² std cells in a 3.24 mm² die ({M7['design__instance__utilization']*100:.1f} % utilization), {M7['power__total']*1e3:.1f} mW estimate.", "Setup slack of +54.7 ns at 100 ns shows the clock is far below the logic's limit; the design was not timing-optimized for speed.", "No energy-per-tile or throughput measurement exists; no comparison against other implementations is claimed."], 11, 0.9); done(f)
# 16 applications
f = slide("Potential applications (details: docs/INDUSTRIAL_APPLICATIONS.md)", "demonstrated · possible next · still needs validation")
table(f, [0.04, 0.18, 0.92, 0.66], [["Area", "Demonstrated here", "Needs validation / future"],
    ["Education & RISC-V research", "Complete, inspectable RTL→GDSII example incl. failures and fixes", "Full RV32I/compliance, pipeline, CSR/interrupts"],
    ["Open hardware", "Reproducible LibreLane configs, SDC, ECO scripts, hashes", "Re-run from scratch on a ≥16 GB host; license decision"], ["Embedded prototyping", "MMIO accelerator + Wishbone bridge simulated end to end", "Wrapper DRC/LVS/STA, bring-up on silicon or FPGA"],
    ["PPA research", "Measured V6→V7 closure methodology; folded vs parallel MAC RTL", "Side-by-side physical comparison of the two MACs"], ["Specialized workloads", "INT4/INT8 4×4 tile engine, functionally verified", "Throughput/energy measurements; larger tiles; SRAM"],
    ["Talent development", "Documented pitfalls and root-cause analyses", "Guided exercises, course material"], ["Accessible EDA flows", "Open tools only, 8 GB laptop to routed macro", "CI for the physical flow"]], [0.2, 0.42, 0.38], size=9.5); done(f)
# 17 limitations
f = slide("Limitations and open work", "TAPEOUT_READY = NO — what is implemented is a physical MACRO, not a verified full-SoC tapeout")
table(f, [0.04, 0.22, 0.92, 0.62], [["Item", "State", "Note"], ["Physical macro implemented (V7)", "PASS", "DRC, LVS, XOR, antenna, 9-corner STA on the V7 files"], ["Fanout limit", "FAIL 1 net", "net2070, see analysis"],
    ["Caravel wrapper PDN with V7 macro", "PASS", "8/8 power nets connected (PSM-0040); stage-only run"], ["Caravel wrapper route/antenna/STA with V7", "UNVERIFIED", "not run; V6 macro: route DRC pass, antenna 1 net FAIL"], ["Wrapper DRC / LVS / STA", "UNVERIFIED", "memory (8 GB host); script provided for a large host"],
    ["Formal equivalence", "UNVERIFIED", "not run"], ["SDF gate-level simulation", "UNVERIFIED", "not run"], ["Shuttle pre-check", "UNVERIFIED", "not run"], ["Full SoC tapeout verified", "NO", "requires all rows above"]], [0.34, 0.14, 0.52]); done(f)
# 18 conclusions
f = slide("Technical conclusions", "what a reader can rely on")
text(f, 0.04, 0.82, ["A complete, reproducible-in-principle open RTL-to-GDSII path exists for this SoC: simulation PASS, routed macro with 0 DRC, LVS match, 0 antenna violations, setup/hold met in 9 corners.", "V7 vs V6: hold margin +17 → +102 ps, slew 158 → 0, capacitance 23 → 0, fanout 83 → 1 net, area +0.3 %. One net remains over the project's fanout rule; documented, not waived.",
    "The most transferable lessons: STA counts antenna diodes as fanout; diodes must follow the sinks when a net is split; estimates from an ECO are optimistic — only post-route SPEF numbers count.",
    "The CPU is a teaching-grade RV32I subset; the accelerator is a small 4×4 tile engine. Value is in the verified flow and its documentation, not in raw performance.", "Next: re-run the Caravel wrapper with the V7 macro on a ≥16 GB host, run EQY/SDF/pre-check, close net2070, replace flip-flop IMEM by SRAM."], 12.5, 0.9)
fig = f; done(f); pdf.close(); print("slides:", n[0])
