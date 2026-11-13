#!/usr/bin/env python3
"""Collect real per-checkpoint metrics from LibreLane runs into CSV/JSON (no interpolation)."""
import json, csv, glob, os, sys
RUNS = os.path.expanduser("~/omega-fusion-tapeout/openlane/omega_fusion_soc_v2/runs")
OUT = os.path.expanduser("~/omega-fusion-tapeout/release/charts/data")
ORDER = ["OMEGA_V2_SYNTH_01","OMEGA_V2_PDN_FIXED_02","OMEGA_V2_TIMING_03","OMEGA_V2_GPL_04","OMEGA_V2_REPAIR_05",
         "OMEGA_V2_DPL_06","OMEGA_V2_CTS_07","OMEGA_V2_POSTCTS_REPAIR_09","OMEGA_V2_GRT_10","OMEGA_V2_ANTENNA_11","OMEGA_V2_ANTENNA_12"]
ORDER += sorted(os.path.basename(p) for p in glob.glob(RUNS+"/OMEGA_V3_*"))
rows = {}
for r in ORDER:
    f = f"{RUNS}/{r}/final/metrics.json"
    if os.path.exists(f):
        rows[r] = json.load(open(f))
keys = sorted({k for m in rows.values() for k in m})
os.makedirs(OUT, exist_ok=True)
json.dump(rows, open(f"{OUT}/metrics_all_runs.json","w"), indent=1)
with open(f"{OUT}/metrics_all_runs.csv","w",newline="") as fh:
    w = csv.writer(fh); w.writerow(["metric"]+list(rows))
    for k in keys: w.writerow([k]+[rows[r].get(k,"") for r in rows])
print(len(rows),"runs",len(keys),"metrics")
