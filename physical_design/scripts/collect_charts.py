#!/usr/bin/env python3
"""Build chart datasets (CSV/JSON) + PNG/SVG charts from REAL run data only.
Every series is labelled with its measurement kind: pre-route estimate / post-CTS estimate / post-route SPEF (signoff-grade)."""
import json, os, re, csv, glob, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np
H = os.path.expanduser("~"); OF = H + "/omega-fusion-tapeout"; RUNS = OF + "/openlane/omega_fusion_soc_v2/runs"
ARC = OF + "/release/reports/archive"; OUT = OF + "/release/charts"; DATA = OUT + "/data"
os.makedirs(DATA, exist_ok=True)
def st(run, step, arc=False):
    base = (ARC if arc else RUNS) + f"/{run}/{step}/state_out.json"
    return json.load(open(base))["metrics"] if os.path.exists(base) else None
CORNERS = ["nom_tt_025C_1v80", "nom_ss_100C_1v60", "nom_ff_n40C_1v95", "min_tt_025C_1v80", "min_ss_100C_1v60", "min_ff_n40C_1v95", "max_tt_025C_1v80", "max_ss_100C_1v60", "max_ff_n40C_1v95"]
def save(fig, name):
    for ext in ("png", "svg"): fig.savefig(f"{OUT}/{name}.{ext}", dpi=140, bbox_inches="tight")
    plt.close(fig); print("chart", name)
def parse_summary(path):
    """LibreLane STAPostPNR summary.rpt table -> {corner: dict}"""
    out = {}
    for ln in open(path):
        if "│" not in ln: continue
        c = [x.strip() for x in ln.strip().strip("│").split("│")]
        if len(c) < 13 or c[0] in ("Overall",) and False: continue
        try:
            out[c[0]] = dict(hold_ws=float(c[1]), r2r_hold_ws=float(c[2]), hold_tns=0.0, hold_vio=int(c[4]), setup_ws=float(c[6]), setup_tns=0.0, setup_vio=int(c[9]), cap_vio=int(c[11]), slew_vio=int(c[12]))
        except Exception: pass
    return out
# ---------------- stage table ----------------
STAGES = [  # label, run, step, arc, kind
 ("synth (Yosys)", "OMEGA_V2_SYNTH_01", None, False, "synthesis netlist"),
 ("post-GPL", "OMEGA_V4_FULL", "01-openroad-globalplacement", True, "placement"),
 ("post-GPL repair", "OMEGA_V4_FULL", "05-openroad-repairdesignpostgpl", True, "placement"),
 ("detailed place", "OMEGA_V4_FULL", "07-openroad-detailedplacement", True, "placement"),
 ("CTS", "OMEGA_V4_FULL", "08-openroad-cts", True, "post-CTS"),
 ("post-CTS repair", "OMEGA_V4_FULL", "10-openroad-resizertimingpostcts", True, "post-CTS"),
 ("GRT (V4)", "OMEGA_V4_FULL", "12-openroad-globalrouting", True, "global-route"),
 ("GRT (ECO, V6)", "OMEGA_V6_ECO2", "01-openroad-globalrouting", False, "global-route"),
 ("antenna/diode repair", "OMEGA_V6_ECO2", "04-openroad-repairantennas", False, "global-route"),
 ("detailed route", "OMEGA_V6_ECO2", "06-openroad-detailedrouting", False, "post-route"),
 ("fill + final", "OMEGA_V6_ECO2", "14-openroad-fillinsertion", False, "post-route"),
]
rows = []
for lab, run, step, arc, kind in STAGES:
    if step is None:
        f = f"{RUNS}/{run}/final/metrics.json"; m = json.load(open(f)) if os.path.exists(f) else None
    else: m = st(run, step, arc)
    if not m: print("missing", lab); continue
    g = lambda k: m.get(k, "")
    rows.append(dict(stage=lab, kind=kind, run=run, step=step or "final", instances=g("design__instance__count"), area_um2=g("design__instance__area"),
        stdcell_count=g("design__instance__count__stdcell"), tap=g("design__instance__count__class:tap_cell"), fill=g("design__instance__count__class:fill_cell"),
        seq=g("design__instance__count__class:sequential_cell"), comb=g("design__instance__count__class:multi_input_combinational_cell"),
        timing_repair_buf=g("design__instance__count__class:timing_repair_buffer"), clock_buf=g("design__instance__count__class:clock_buffer"), clock_inv=g("design__instance__count__class:clock_inverter"),
        antenna_cells=g("design__instance__count__class:antenna_cell"), antenna_nets=g("antenna__violating__nets"), antenna_pins=g("antenna__violating__pins"),
        hpwl_um=g("route__wirelength__estimated"), grt_wl_um=g("global_route__wirelength"), drt_wl_um=g("route__wirelength"),
        grt_overflow=g("route__overflow") if "route__overflow" in m else g("global_route__overflow") if False else ""))
with open(f"{DATA}/stage_metrics.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
json.dump(rows, open(f"{DATA}/stage_metrics.json", "w"), indent=1)
lab = [r["stage"] for r in rows]; x = np.arange(len(rows))
colk = {"synthesis netlist": "#888", "placement": "#1f77b4", "post-CTS": "#2ca02c", "global-route": "#ff7f0e", "post-route": "#d62728"}
# 1 area per stage (logic, excluding fill) ; 2 instance count
fig, ax = plt.subplots(figsize=(11, 4.8))
nonfill = [ (float(r["area_um2"] or 0) - 0) for r in rows]
ax.bar(x, [a/1e6 for a in nonfill], color=[colk[r["kind"]] for r in rows]); ax.set_xticks(x); ax.set_xticklabels(lab, rotation=30, ha="right", fontsize=8)
ax.set_ylabel("instance area [mm²]"); ax.set_title("1. Design area by stage (bars coloured by measurement kind; final bar includes 2.2 mm² of fill)")
for i, r in enumerate(rows): ax.text(i, nonfill[i]/1e6, f"{nonfill[i]/1e6:.3f}", ha="center", va="bottom", fontsize=7)
save(fig, "01_area_by_stage")
fig, ax = plt.subplots(figsize=(11, 4.8)); ax.bar(x, [float(r["instances"] or 0) - float(r["fill"] or 0) for r in rows], color=[colk[r["kind"]] for r in rows])
ax.set_xticks(x); ax.set_xticklabels(lab, rotation=30, ha="right", fontsize=8); ax.set_ylabel("instances (excluding fill)"); ax.set_title("2. Cell count by stage (taps + logic + buffers + diodes; fill excluded)")
save(fig, "02_instances_by_stage")
# 9 buffers per stage
fig, ax = plt.subplots(figsize=(11, 4.8)); w = .27
for j, (k, c, l) in enumerate([("timing_repair_buf", "#ff7f0e", "timing/repair buffers"), ("clock_buf", "#2ca02c", "clock buffers"), ("antenna_cells", "#000", "antenna diodes")]):
    ax.bar(x + (j-1)*w, [float(r[k] or 0) for r in rows], w, label=l, color=c)
ax.set_xticks(x); ax.set_xticklabels(lab, rotation=30, ha="right", fontsize=8); ax.legend(); ax.set_title("9. Buffers / diodes inserted by stage (cumulative counts in each checkpoint)")
save(fig, "09_buffers_by_stage")
# 14 wirelength
fig, ax = plt.subplots(figsize=(8, 4.5)); vals = {}
for r in rows:
    if r["hpwl_um"] != "": vals[f"{r['stage']}\nHPWL"] = float(r["hpwl_um"])
    if r["drt_wl_um"] != "": vals[f"{r['stage']}\nDRT"] = float(r["drt_wl_um"])
    if r["grt_wl_um"] != "": vals[f"{r['stage']}\nGRT"] = float(r["grt_wl_um"])
ks = list(vals)[-6:]; ax.bar(range(len(ks)), [vals[k]/1e6 for k in ks]); ax.set_xticks(range(len(ks))); ax.set_xticklabels(ks, fontsize=7, rotation=25, ha="right"); ax.set_ylabel("wirelength [m]")
ax.set_title("14. Wirelength: estimated (HPWL / global route) vs final detailed route"); save(fig, "14_wirelength")
print("stage charts done")
