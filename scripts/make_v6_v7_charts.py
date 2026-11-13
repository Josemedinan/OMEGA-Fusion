#!/usr/bin/env python3
"""charts/19 (per-corner setup/hold V6 vs V7) and charts/20 (PPA V6 vs V7) from verified reports. Requires matplotlib.
Inputs: physical_design/reports/signoff_v6/sta_independent_summary.csv, physical_design/reports/v7/sta/*_flow.summary.txt,
physical_design/reports/signoff_v6/metrics.json, physical_design/reports/v7/metrics.json."""
import csv, glob, json, os, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
j = lambda *p: os.path.join(root, *p)
v6 = {r['tag'].replace('_flow', ''): r for r in csv.DictReader(open(j('physical_design/reports/signoff_v6/sta_independent_summary.csv'))) if r['tag'].endswith('_flow')}
v7 = {}
for f in glob.glob(j('physical_design/reports/v7/sta/*_flow.summary.txt')):
    d = dict(l.strip().split('=', 1) for l in open(f) if '=' in l); v7[d['tag'].replace('_flow', '')] = d
order = [f'{rc}_{p}' for p in ('tt_025C_1v80', 'ss_100C_1v60', 'ff_n40C_1v95') for rc in ('nom', 'min', 'max')]
short = lambda t: t.replace('_025C_1v80', '').replace('_100C_1v60', '').replace('_n40C_1v95', '')
rows = []
for t in order:
    a = [x for x in v6 if x.startswith(t[:3]) and x.endswith(t[4:])][0]
    rows.append([short(t), float(v6[a]['setup_ws_ns']), float(v6[a]['hold_ws_ns']), float(v7[t]['setup_ws_ns']) if t in v7 else float('nan'), float(v7[t]['hold_ws_ns'])])
with open(j('charts/data/v6_v7_corner_slack.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['corner', 'v6_setup_ws_ns', 'v6_hold_ws_ns', 'v7_setup_ws_ns', 'v7_hold_ws_ns']); w.writerows(rows)
x = range(len(rows)); w = 0.4
fig, ax = plt.subplots(1, 2, figsize=(13, 4.6))
ax[0].bar([i - w / 2 for i in x], [r[1] for r in rows], w, label='V6', color='#888'); ax[0].bar([i + w / 2 for i in x], [r[3] for r in rows], w, label='V7', color='#2d6cdf')
ax[0].set_title('Setup worst slack per corner [ns] (period 100 ns)', fontsize=10); ax[0].legend()
ax[1].bar([i - w / 2 for i in x], [r[2] for r in rows], w, label='V6', color='#888'); ax[1].bar([i + w / 2 for i in x], [r[4] for r in rows], w, label='V7', color='#2d6cdf')
ax[1].axhline(0, color='k', lw=.8); ax[1].set_title('Hold worst slack per corner [ns]', fontsize=10); ax[1].legend()
for a in ax: a.set_xticks(list(x)); a.set_xticklabels([r[0] for r in rows], rotation=45, fontsize=8)
fig.suptitle('V6 vs V7, post-route extracted SPEF, independent OpenROAD STA, SDC v4 (V7: min hold +0.102 ns in min_ff; V6: +0.017 ns in max_ff)', fontsize=10)
fig.tight_layout()
for e in ('png', 'svg'): fig.savefig(j(f'charts/19_v6_v7_slack_per_corner.{e}'), dpi=150)
m6 = json.load(open(j('physical_design/reports/signoff_v6/metrics.json'))); m7 = json.load(open(j('physical_design/reports/v7/metrics.json')))
items = [('Std-cell instances\n(excl. fill) [k]', 'design__instance__count__stdcell', 1e3), ('Std-cell area\n[mm²]', 'design__instance__area__stdcell', 1e6), ('Timing-repair\nbuffers [k]', 'design__instance__count__class:timing_repair_buffer', 1e3),
         ('Antenna\ndiodes [k]', 'design__instance__count__class:antenna_cell', 1e3), ('Wirelength\n[m]', 'route__wirelength', 1e6), ('Vias [k]', 'route__vias', 1e3), ('Power estimate\n[mW]', 'power__total', 1e-3)]
fig, ax = plt.subplots(1, len(items), figsize=(15, 3.6))
csvrows = []
for a, (lab, k, d) in zip(ax, items):
    v = [m6[k] / d, m7[k] / d]; csvrows.append([lab.replace('\n', ' '), k, m6[k], m7[k]])
    a.bar(['V6', 'V7'], v, color=['#888', '#2d6cdf']); a.set_title(lab, fontsize=9)
    for i, y in enumerate(v): a.text(i, y, f'{y:.3g}', ha='center', va='bottom', fontsize=8)
    a.set_ylim(0, max(v) * 1.2)
fig.suptitle('PPA, V6 vs V7 (power = OpenROAD estimate, nom_tt, default activity; area/cells from LibreLane metrics)', fontsize=10)
fig.tight_layout()
for e in ('png', 'svg'): fig.savefig(j(f'charts/20_v6_v7_ppa.{e}'), dpi=150)
with open(j('charts/data/v6_v7_ppa.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['metric', 'key', 'v6', 'v7']); w.writerows(csvrows)
print('ok')
