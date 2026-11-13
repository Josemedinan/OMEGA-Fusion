# Timing signoff summary (V6, post-route, extracted SPEF)

Corners: nom/min/max RC × tt/ss/ff (9). SDC: `physical_design/constraints/soc_constraint_omega_v4.sdc`. Two engines (LibreLane `STAPostPNR` and an independent OpenROAD script) agree for nom_tt, max_ss, max_ff.
Table: `physical_design/reports/signoff_v6/sta_independent_summary.csv`.

| Corner | setup WS [ns] | hold WS [ns] | slew viol. | cap viol. | fanout viol. |
|---|---:|---:|---:|---:|---:|
| max_ss | +52.03 | +0.051 | 158 | 23 | 83 |
| nom_ss | +53.23 | +0.294 | 105 | 20 | 83 |
| min_ss | +54.64 | +0.465 | 71 | 18 | 83 |
| max_tt | +75.15 | +0.086 | 16 | 23 | 83 |
| nom_tt | +75.86 | +0.193 | 16 | 20 | 83 |
| min_tt | +76.65 | +0.273 | 5 | 18 | 83 |
| max_ff | +84.16 | **+0.017** | 2 | 23 | 83 |
| nom_ff | +84.65 | +0.093 | 0 | 21 | 83 |
| min_ff | +85.17 | +0.104 | 0 | 18 | 83 |

* Setup and hold: PASS in all corners; the thin point is hold in max_ff (+17 ps).
* Reset: recovery ≥ +89.9 ns, removal ≥ +0.017 ns; `rst_n` input delay −max 2 / −min 0 ns (worst case for removal).
* Slew/cap/fanout columns are against the **flow limits** (0.75 ns / 0.2 pF / 10): FAIL. Liberty-only limits: 0/0/0 in max_ff, max_tt, nom_ss; 3 slew violations on the `clk` root in max_ss.
* Clock: insertion delay 3.3–5.2 ns in SS; worst setup skew 0.46 ns (flow, nom).
* Why V3/V4 looked worse and why the early "+4.7 ns SS" figure is not used: `docs/physical_design/PHYSICAL_DESIGN_REPORT.md` §1 and §3.
