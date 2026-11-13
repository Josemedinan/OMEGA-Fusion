#!/usr/bin/env python3
"""Builds VISUAL_GALLERY.md, INDEX.md and the presentation PDF from the files that exist (no content is invented)."""
import os, json, glob
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.image as mpimg
from matplotlib.backends.backend_pdf import PdfPages
R = os.path.expanduser("~/omega-fusion-tapeout/release/")
V = {  # file -> (what it shows, source)
"01_floorplan_die_core_pins.png": ("Floorplan: die 1800x1800 µm, core 1749.4x1746.2 µm (3.055 mm²), 179 IO pins by side, 43,470 tap cells (grey lines). Dimension arrows in µm.", "ODB OMEGA_V4_FULL/01 (floorplan/IO/tap content)"),
"02a_pdn_full_vdd_vss.png": ("Power grid: met1 rails + met4 straps, VDD/VSS alternating (full die).", "DEF with PDN only (V4/01), same grid as final"),
"02b_pdn_zoom_40um_straps_rails.png": ("PDN zoom: rails crossing two met4 straps. Via cuts are not drawn by the DEF importer; connectivity proven by PSM, not by this image.", "same"),
"03_global_placement_full.png": ("Global placement: flip-flop arrays (red) left/bottom, datapath logic (blue) right/top; the die is ~28 % used.", "ODB V4/01"),
"03b_placement_density_heatmap.png": ("Placement density heatmap (functional cell area / bin area, 30 µm bins).", "ODB V4/07 (after detailed placement)"),
"04a_detailed_placement_full.png": ("Legalized placement, full chip, cells coloured by class (comb, flop, clock, delay/IO, repair buffers).", "ODB V4/07"),
"04b_detailed_placement_zoom_100um.png": ("Legalized standard cells, 100x100 µm zoom (tap cells = grey dashes).", "ODB V4/07"),
"05a_cts_clock_tree_full.png": ("Clock tree: 4,267 clock buffers/inverters, upper-level (black) and leaf (green) driver→load connectivity. Straight lines are connectivity, not routed wires.", "ODB V4/08"),
"05b_cts_clock_tree_zoom_250um.png": ("Clock tree zoom 250x250 µm.", "ODB V4/08"),
"06_global_routing_guides_by_layer.png": ("Global-routing guide coverage per layer met1–met4 (guides saturate met1/met2 bins; overflow was 0). Not final wires.", "after_grt.guide V6/01"),
"06b_global_routing_guides_overlay.png": ("All global-routing guides overlaid, colour per layer.", "after_grt.guide V6/01"),
"06c_routing_congestion_heatmap_final.png": ("Congestion: final routed wire length / track capacity per 30 µm bin and layer (max 0.42/0.65/0.67/0.47 for met1–met4).", "routed DEF (final)"),
"07a_detailed_routing_all_layers.png": ("Final detailed routing, all layers (met1 blue, met2 red, met3 green, met4 yellow).", "final routed DEF"),
"07b_detailed_routing_met1.png": ("Detailed routing, met1 only (incl. power rails).", "final routed DEF"),
"07c_detailed_routing_met2.png": ("Detailed routing, met2 only (vertical).", "final routed DEF"),
"07d_detailed_routing_met3.png": ("Detailed routing, met3 only (horizontal).", "final routed DEF"),
"07e_detailed_routing_met4.png": ("Detailed routing, met4 only (vertical, straps + routes).", "final routed DEF"),
"07f_detailed_routing_zoom_60um.png": ("Detailed routing zoom 60x60 µm, all layers.", "final routed DEF"),
"08a_final_gds_full_chip.png": ("Final GDS, full chip in KLayout (met1–met4 with sky130A layer colours).", "release/gds/omega_fusion_soc_asic.gds"),
"08b_final_gds_core_zoom_120um.png": ("Final GDS core zoom 120x120 µm.", "same"),
"08c_final_gds_interconnect_30um.png": ("Final GDS interconnect detail 30x30 µm (li1, mcon, met1, via, met2, via2, met3).", "same"),
"08d_final_gds_cell_level_22um.png": ("Final GDS cell level 22x22 µm (diff, poly, licon, li1, mcon, met1).", "same"),
"09a_caravel_wrapper_pdn_mprj.png": ("Caravel wrapper 2920x3520 µm with macro mprj outlined (560,860); wrapper met4/met5 power grid; PSM: all 8 nets connected.", "wrapper run WRAP_FINAL_PDN"),
"09b_caravel_wrapper_routed_overview.png": ("Wrapper after detailed routing (route DRC 0).", "wrapper run WRAP_FINAL_PNR"),
"09c_caravel_macro_corner_power_connection.png": ("Macro corner: wrapper power stripes crossing the macro boundary.", "wrapper run WRAP_FINAL_PDN"),
"10_signoff_evidence.png": ("Signoff evidence: PASS/FAIL/UNVERIFIED table, post-route STA slack map (9 corners), violations still failing, Liberty-only check.", "reports/signoff_v6/*"),
}
CH = sorted(os.path.basename(p) for p in glob.glob(R + "charts/*.png"))
g = ["# VISUAL GALLERY\n", "Every image is rendered from a real physical file (ODB/DEF/GDS/guide) by OpenROAD-extracted geometry + matplotlib, or by headless KLayout. Nothing is synthetic. Missing: no images exist for Caravel wrapper DRC/LVS (not run) and no Magic screenshots (Magic is only used in batch mode).\n"]
for f, (t, s) in V.items():
    if os.path.exists(R + "visuals/" + f): g.append(f"## {f}\n![{f}](visuals/{f})\n\n{t}\n\n*Source:* `{s}`\n")
g.append("\n# Charts (`charts/`, data in `charts/data/`)\n")
for f in CH: g.append(f"* `charts/{f}` (+ SVG)\n")
open(R + "VISUAL_GALLERY.md", "w").write("\n".join(g))
# presentation PDF
os.makedirs(R + "docs", exist_ok=True)
with PdfPages(R + "docs/OMEGA_Fusion_physical_design_presentation.pdf") as pdf:
    def text_page(title, lines):
        fig = plt.figure(figsize=(11.7, 8.3)); fig.text(.05, .92, title, fontsize=22, fontweight="bold")
        for i, l in enumerate(lines): fig.text(.06, .82 - i * .045, l, fontsize=12)
        pdf.savefig(fig); plt.close(fig)
    text_page("OMEGA-Fusion V2 — from RTL to SKY130 layout", ["omega_fusion_soc_asic: RV32I controller + 256x32 IMEM + INT4/INT8 MAC accelerator", "Die 1800 x 1800 µm, 10 MHz, sky130_fd_sc_hd, met1–met4", "Final layout (V6): DRC 0, LVS clean, antenna 0, setup/hold met in 9 corners", "Still failing: slew/cap/fanout vs flow limits (clock-tree nodes); Caravel wrapper DRC/LVS not run", "Verdict: TAPEOUT_READY = NO  (see SIGNOFF_REPORT.md)", "", "All images in this deck are real renders of the physical files."])
    for f, (t, s) in V.items():
        p = R + "visuals/" + f
        if not os.path.exists(p): continue
        fig = plt.figure(figsize=(11.7, 8.3)); ax = fig.add_axes([0, .12, 1, .88]); ax.imshow(mpimg.imread(p)); ax.axis("off")
        fig.text(.03, .06, t[:170], fontsize=10); fig.text(.03, .025, "Source: " + s, fontsize=8, family="monospace"); pdf.savefig(fig, dpi=110); plt.close(fig)
    for f in CH:
        fig = plt.figure(figsize=(11.7, 8.3)); ax = fig.add_axes([0.02, .08, .96, .88]); ax.imshow(mpimg.imread(R + "charts/" + f)); ax.axis("off"); fig.text(.03, .02, "charts/" + f + "  (data: charts/data/)", fontsize=8, family="monospace"); pdf.savefig(fig, dpi=110); plt.close(fig)
print("docs built")
