#!/usr/bin/env python3
"""Plots charts/18_eco_iterations_v6_to_v7.{png,svg} from charts/data/v7_iterations.csv (values come from the per-iteration
LibreLane STA summaries archived in physical_design/reports/iterations/). Requires matplotlib."""
import csv, os, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
r = list(csv.DictReader(open(os.path.join(root, "charts/data/v7_iterations.csv"))))
lab = [x['iteration'].replace(' (baseline)', '\n(base)').replace(' = V7 final', '\n=V7 final').replace(' r1', '\nr1') for x in r]
x = list(range(len(r)))
fig, ax = plt.subplots(2, 2, figsize=(13, 7.5))
h = [float(v['hold_ws_ns_min_over_corners']) for v in r]
ax[0, 0].bar(x, h, color=['#888'] + ['#d9534f' if v < 0 else '#2d6cdf' for v in h[1:]]); ax[0, 0].axhline(0, color='k', lw=.8)
ax[0, 0].set_title('Worst hold slack over 9 corners [ns]', fontsize=10); ax[0, 0].set_ylim(-0.75, 0.2)
for i, v in enumerate(h): ax[0, 0].text(i, v + 0.02 if v >= 0 else v / 2, f'{v:+.3f}', ha='center', fontsize=7, color='k' if v >= 0 else 'w')
ax[0, 1].plot(x, [float(v['setup_ws_ns']) for v in r], 'o-'); ax[0, 1].set_title('Worst setup slack [ns] (period 100 ns)', fontsize=10)
ax[1, 0].bar(x, [int(v['slew_viol_max_ss']) for v in r], color='#e0872b'); ax[1, 0].set_title('Max-slew violations (limit 0.75 ns), max_ss', fontsize=10)
for i, v in enumerate(r): ax[1, 0].text(i, int(v['slew_viol_max_ss']) + 3, v['slew_viol_max_ss'], ha='center', fontsize=7)
w = 0.38
ax[1, 1].bar([i - w / 2 for i in x], [int(v['cap_viol_worst_corner']) for v in r], w, label='cap > 0.2 pF', color='#2da84a')
ax[1, 1].bar([i + w / 2 for i in x], [int(v['fanout_viol_worst_corner']) for v in r], w, label='fanout > 10 (nets)', color='#8e44ad')
ax[1, 1].set_yscale('symlog'); ax[1, 1].legend(fontsize=8); ax[1, 1].set_title('Cap and fanout violations (symlog)', fontsize=10)
for a in ax.flat:
    a.set_xticks(x); a.set_xticklabels(lab, fontsize=7)
fig.suptitle('ECO iterations V6 -> V7 (post-route SPEF, LibreLane STA, flow limits; antenna 0 and route DRC 0 in every iteration)', fontsize=11)
fig.tight_layout()
for e in ('png', 'svg'): fig.savefig(os.path.join(root, f'charts/18_eco_iterations_v6_to_v7.{e}'), dpi=150)
