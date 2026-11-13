#!/usr/bin/env python3
import sys; sys.argv=[sys.argv[0]]
import os; exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"collect_charts.py")).read().split("# ---------------- stage table")[0])
RUNLBL = [("V3 baseline\n(SDC v3, GRT-est. repair)", ARC+"/OMEGA_V3_SIGNOFF/11-openroad-stapostpnr/summary.rpt"),
          ("V4\n(SDC v4, full flow)", ARC+"/OMEGA_V4_FULL/30-openroad-stapostpnr/summary.rpt"),
          ("V5\n(ECO round 1)", ARC+"/OMEGA_V5_ECO/17-openroad-stapostpnr/summary.rpt"),
          ("V6 FINAL\n(ECO round 2)", OF+"/release/reports/signoff_v6/sta_multicorner_summary.rpt")]
T = {l: parse_summary(p) for l, p in RUNLBL if os.path.exists(p)}
json.dump(T, open(f"{DATA}/postroute_sta_by_run_corner.json", "w"), indent=1)
with open(f"{DATA}/postroute_sta_by_run_corner.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["run", "corner", "hold_ws_ns", "setup_ws_ns", "hold_vio", "setup_vio", "cap_vio", "slew_vio"])
    for l, d in T.items():
        for c, v in d.items(): w.writerow([l.replace("\n", " "), c, v["hold_ws"], v["setup_ws"], v["hold_vio"], v["setup_vio"], v["cap_vio"], v["slew_vio"]])
fin = list(T.values())[-1]; short = lambda c: c.replace("_025C_1v80", "").replace("_100C_1v60", "").replace("_n40C_1v95", "")
def corner_bar(key, title, name, ylab, logy=False):
    fig, ax = plt.subplots(figsize=(12, 4.8)); x = np.arange(len(CORNERS)); n = len(T); w = .8/n
    for j, (l, d) in enumerate(T.items()):
        ax.bar(x + (j-(n-1)/2)*w, [d[c][key] if c in d else np.nan for c in CORNERS], w, label=l.replace("\n", " "))
    ax.set_xticks(x); ax.set_xticklabels([short(c) for c in CORNERS], rotation=0, fontsize=8); ax.set_ylabel(ylab); ax.legend(fontsize=7); ax.axhline(0, color="k", lw=.8)
    if logy: ax.set_yscale("symlog", linthresh=1)
    ax.set_title(title + "  [post-route, SPEF extracted, signoff-grade STA]"); save(fig, name)
corner_bar("setup_ws", "3. Setup worst slack by corner and run (period 100 ns)", "03_setup_slack_by_corner", "WNS [ns]")
corner_bar("hold_ws", "4. Hold worst slack by corner and run", "04_hold_slack_by_corner", "WNS [ns]")
corner_bar("slew_vio", "5. Max-slew violations (flow limit 0.75 ns) by corner and run", "05_slew_violations", "violating pins", True)
corner_bar("cap_vio", "6. Max-capacitance violations (flow limit 0.2 pF) by corner and run", "06_cap_violations", "violating pins", True)
corner_bar("hold_vio", "Hold violating endpoints by corner and run", "04b_hold_violations", "endpoints", True)
# 7 fanout: from final metrics per run where available (flow metrics)
fm = json.load(open(OF + "/release/reports/signoff_v6/metrics.json"))
fig, ax = plt.subplots(figsize=(6, 4)); v = [fm.get(f"design__max_fanout_violation__count__corner:{c}") for c in CORNERS[:3]]
ax.bar([short(c) for c in CORNERS[:3]], v); ax.set_title("7. Max-fanout violations (limit 10), FINAL layout\n(16-17 are CTS tree nodes; rest are mux selects)"); ax.set_ylabel("nets")
save(fig, "07_fanout_violations_final")
json.dump({"final_fanout_by_corner": dict(zip(CORNERS[:3], v)), "note": "fanout metric only extracted for final run (LibreLane STAPostPNR); earlier runs: V2 stage metrics 726 (pre-repair, SDC without limits)"}, open(f"{DATA}/fanout_final.json", "w"))
# 8 skew per corner (final, flow metrics + independent)
fig, ax = plt.subplots(figsize=(8, 4.2)); cs = CORNERS[:3]
ax.bar(np.arange(3) - .2, [fm[f"clock__skew__worst_setup__corner:{c}"] for c in cs], .4, label="worst setup skew"); ax.bar(np.arange(3) + .2, [abs(fm[f"clock__skew__worst_hold__corner:{c}"]) for c in cs], .4, label="|worst hold skew|")
ax.set_xticks(range(3)); ax.set_xticklabels([short(c) for c in cs]); ax.set_ylabel("ns"); ax.legend(); ax.set_title("8. Clock skew by corner (final, post-route, 10,323 sinks)"); save(fig, "08_clock_skew_by_corner")
# 10 routing resources per layer (final wire length + GRT usage) + 11 congestion
cg = list(csv.DictReader(open(f"{DATA}/congestion_by_layer.csv")))
fig, axs = plt.subplots(1, 2, figsize=(11, 4.2))
axs[0].bar([r["layer"] for r in cg], [float(r["wirelength_um"])/1e6 for r in cg], color=["#2d6cdf", "#e0472b", "#2da84a", "#d9a400"]); axs[0].set_ylabel("routed wire length [m]"); axs[0].set_title("10. Routed wire length per layer\n(3.318 m total, 478,554 vias)", fontsize=10)
axs[1].bar([r["layer"] for r in cg], [float(r["max_util"]) for r in cg], label="max bin utilization"); axs[1].bar([r["layer"] for r in cg], [float(r["mean_util_nonzero"]) for r in cg], width=.4, label="mean (non-empty bins)")
axs[1].axhline(1, color="r", ls="--"); axs[1].legend(); axs[1].set_title("11. Congestion: routed wire / track capacity\n(30 µm bins; GRT overflow = 0)", fontsize=10); save(fig, "10_11_routing_resources_congestion")
# 12/13 antenna
ANT = [("V2 GRT-stage\npre-repair (violations)", 355, None, None), ("V2 ANTENNA_11\n(316 diodes)", 5, 20, 316), ("V2 ANTENNA_12\n(8 iter, margin 20)", 5, 38, 687),
       ("V3 post-DRT\n(real wires)", 2, 2, None), ("V4 post-DRT", 0, 0, None), ("V5 post-DRT", 0, 0, None), ("V6 FINAL post-DRT", 0, 0, None)]
with open(f"{DATA}/antenna_evolution.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["stage", "violating_nets", "violating_pins", "diodes_inserted_total", "source"])
    for l, n, p, d in ANT: w.writerow([l.replace("\n", " "), n, p, d, "GRT-stage estimate" if "GRT" in l or "ANTENNA" in l else "post-DRT real check (OpenROAD check_antennas)"])
fig, ax = plt.subplots(figsize=(11, 4.6)); x = np.arange(len(ANT))
ax.bar(x - .2, [a[1] for a in ANT], .4, label="violating nets"); ax.bar(x + .2, [a[2] or 0 for a in ANT], .4, label="violating pins")
ax.set_xticks(x); ax.set_xticklabels([a[0] for a in ANT], fontsize=7); ax.legend(); ax.set_title("12. Antenna violations: GRT-stage estimates (V2) vs real post-detailed-route checks (V3-V6)"); save(fig, "12_antenna_evolution")
fig, axs = plt.subplots(1, 3, figsize=(11, 3.8)); 
for ax, (t, v) in zip(axs, [("violating pins", [20, 38]), ("diodes inserted", [316, 687]), ("area of diodes [µm²]", [790.8, 1719.2])]): ax.bar(["11", "12"], v, color=["#2ca02c", "#d62728"]); ax.set_title(t, fontsize=9)
fig.suptitle("13. Antenna-repair variants at the GRT stage (nets violating: 5 in both): 11 is the better base", fontsize=10); save(fig, "13_antenna_variants_11_vs_12")
# 15 DRC/LVS/antenna summary
res = [("Magic DRC", 0), ("KLayout DRC", 0), ("route DRC (TritonRoute)", 0), ("LVS (Netgen) errors", 0), ("Antenna violations", 0), ("XOR Magic vs KLayout", 0), ("disconnected pins", 0), ("PDN grid violations", 0)]
fig, ax = plt.subplots(figsize=(9, 4)); ax.barh([r[0] for r in res], [r[1] for r in res], color="#2ca02c"); ax.set_xlim(0, 5); ax.set_xlabel("violations / errors (all measured = 0)")
ax.set_title("15. Final layout verification results (V6): all counts measured, 0 found"); save(fig, "15_drc_lvs_antenna_final")
# 16 power / IR
fig, ax = plt.subplots(figsize=(7, 4)); ax.bar(["VDD worst drop", "VSS worst bounce"], [fm["design_powergrid__drop__worst__net:VDD"]*1e3, fm["design_powergrid__drop__worst__net:VSS"]*1e3]); ax.set_ylabel("mV")
ax.set_title(f"16. IR drop (nom_ss, {fm['power__total']*1e3:.1f} mW total power, nom_tt activity default)\nworst 0.09 mV = 0.005 %"); save(fig, "16_power_irdrop")
# 17 PPA
fig, axs = plt.subplots(1, 4, figsize=(15, 4.6))
axs[0].bar(["logic+taps\n(no fill)", "with fill"], [fm["design__instance__area"]/1e6 - 2.2054, fm["design__instance__area"]/1e6]); axs[0].set_title("Area [mm²]\n(core 3.055 mm²)")
axs[1].bar(["total", "internal", "switching", "leakage"], [fm["power__total"]*1e3, fm["power__internal__total"]*1e3, fm["power__switching__total"]*1e3, fm["power__leakage__total"]*1e3]); axs[1].set_title("Power [mW]\n(nom_tt, default activity)", fontsize=9); axs[1].tick_params(axis="x", labelrotation=20)
ws = {c: fin[c]["setup_ws"] for c in CORNERS if c in fin}; per = 100.0
axs[2].bar([short(c) for c in ws], [1000/(per - s) for s in ws.values()]); axs[2].set_title("Indicative fmax [MHz]\n1/(100 ns - setup WNS)", fontsize=9); axs[2].tick_params(axis="x", labelrotation=60, labelsize=6)
axs[3].bar(["cells\n(no fill)", "flip-flops", "buffers"], [fm["design__instance__count"] - fm["design__instance__count__class:fill_cell"], fm["design__instance__count__class:sequential_cell"], fm["design__instance__count__class:timing_repair_buffer"]]); axs[3].set_title("Cell counts")
fig.suptitle("17. PPA summary (final V6): power = estimate (default activity); timing = post-route SPEF", y=1.04); fig.tight_layout(); save(fig, "17_ppa_summary")
json.dump({"area_mm2_with_fill": fm["design__instance__area"]/1e6, "area_mm2_logic_taps": fm["design__instance__area"]/1e6-2.2054, "core_mm2": 3.055, "util_nofill": fm["design__instance__utilization"], "power_mW": fm["power__total"]*1e3, "setup_ws_ns_min_over_corners": min(v["setup_ws"] for v in fin.values()), "hold_ws_ns_min_over_corners": min(v["hold_ws"] for v in fin.values()), "kind": "area/power: estimate (default activity); timing: post-route signoff-grade"}, open(f"{DATA}/ppa_final.json", "w"), indent=1)
print("done")
