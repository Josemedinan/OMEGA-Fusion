# PHYSICAL DESIGN REPORT — omega_fusion_soc_asic (floorplan → final layout)

> **Baseline notice.** Sections 1–7 describe the flow up to the **V6** layout. The follow-up ECO iterations that produced **V7** are in `docs/results/V7_ECO_REPORT.md`.
> **Path note.** Paths in backticks are relative to the repository root. Large artifacts (SPEF, KLayout GDS, routed DEF, run databases) are not stored in git; their SHA-256 are in `deliverables/SHA256SUMS.original.txt`. `deliverables/lef` and `deliverables/netlist` hold gzip-compressed copies (`*.gz`); GDS, SPEF, KLayout GDS and DEF are GitHub Release assets (`docs/RELEASE_ASSETS.md`).


All numbers come from run artifacts (`charts/data/*.csv|json`, `physical_design/reports/`). Kind of each number: *estimate* (placement/GRT parasitics), *post-route* (extracted SPEF), *signoff tool* (Magic/KLayout/Netgen).

## 1. Starting point and audit
Existing checkpoints (V2 series, untouched): synthesis 43,448 cells → floorplan 1800×1800 µm → PDN → GPL → repair → DPL → CTS → STA → GRT_10 (overflow 0) → two GRT-stage antenna repairs (`ANTENNA_11`, `ANTENNA_12`).

Findings of the audit:
1. **The SDC was under-constrained.** `soc_constraint_omega_v2.sdc` had only `create_clock` and I/O delays. With a custom `PNR_SDC_FILE`, LibreLane does *not* apply its `base.sdc`, so the resizer and STA ran **without** max-fanout/transition/cap limits, driving cell, output load, clock uncertainty/transition and derate. `rst_n` had no input delay, so every `RESET_B` recovery/removal check was unconstrained (this is the "one input without `set_input_delay`" warning: a real omission, not the clock).
2. **Stale SS metrics.** "SS setup +4.700 ns / 39,793 slew violations" are identical in every run from `PDN_FIXED_02` on: a single early measurement (ideal clocks) carried through LibreLane's state, never re-measured. Pre-CTS STA values (e.g. −213 ns) are with an unbuilt clock tree. Neither was used as a result. Only post-CTS estimates and post-route SPEF STA are plotted (`charts/03…06`).
3. **Hold −0.003 ns (FF) vs "no hold violations" in repair.** Not reproducible with ideal-clock or placement-RC audit (independent audit: +0.24 ns FF at GRT_10, `physical_design/reports/audit/grt10`). With the proper SDC and the post-route SPEF the true hold problem is different and large: data inputs (`imem_wdata*`, `dma_rdata*`, …, input delay 2 ns) racing a clock whose insertion delay is 3.3–5.2 ns in SS (V3: −0.605 ns, 260 endpoints; V4: −1.198 ns), plus `rst_n` removal. `repair_timing` did not see them because it ran on GRT-estimated parasitics (clock latency ≈1 ns there) — a 4-5× estimation gap. The exact −0.003 ns path of the old run was not isolated; that SDC/flow state is superseded.

## 2. Floorplan & PDN (preserved)
Die 1800×1800 µm; requested core [25,25,1775,1775]; actual core after row snapping 25.30–1774.68 × 27.20–1773.44 µm (3.055 mm²). `FP_SIZING=absolute`, `PDN_MULTILAYER=false`, `PDN_CORE_RING=false`, `RT_MAX_LAYER=met4`, PDN check on. Power: met1 rails (every 2.72 µm) + met4 straps (pitch 153.6 µm, 1.6 µm wide), VDD/VSS. 179 pins (116 N, 42 S, 11 E, 8 W incl. power). Images `visuals/01*`, `02*`.

## 3. Flow actually used (final = V6)
| Step | What | Result |
|---|---|---|
| GPL → DPL (V4) | SDC v4 + `DEFAULT_CORNER=nom_ss` for resizer; post-GPL `repair_design` with limits | +10,436 buffers (limits now enforced: 726 fanout viol. fixed), area 0.630 → 0.729 mm² (+16 %) |
| CTS (V4) | TritonCTS, 10,323 sinks | 2,168 clock buffers + 102 inverters; insertion 3.3–5.2 ns |
| post-CTS repair | `repair_timing` hold (11,633 endpoints with the new SDC: derate 5 %, uncertainty 0.25 ns) | +10.1k timing-repair buffers (10,611 → 20,698 cumulative), area 0.757 → 0.858 mm²; setup untouched (huge margin) |
| GRT | overflow 0; met1 24.6 %, met2 27.4 %, met3 4.5 %, met4 3.5 % usage (`charts/10_11`) | |
| Antenna | GRT-stage repair + DRT-stage repair loop | V4 DRT: 1 pin left in-loop, 0 at final check |
| DRT (V4) | TritonRoute, 6 threads | DRC 0 |
| **ECO round 1/2** (`physical_design/scripts/eco_full.tcl`) | OpenROAD on the routed DB with **real max/min SPEF**: `repair_design` (SS), `repair_timing -hold` (SS+FF), legalize, strip routes, then re-run GRT+DRT | R1: slew 12,908→231, hold −1.20→+0.055 ns, 115 hold buffers; R2: slew 231→158 |
| Fill, RCX, STA, IR-drop, stream-out, DRC, LVS | LibreLane | see `SIGNOFF_REPORT.md` |

Why the ECO works: `repair_design` run against estimated parasitics finds 590 violating nets; run against the SPEF it finds the real 2,513 and **resizes** 2,475 drivers (area −0.8 %) instead of inserting buffers. Hold repair against SPEF needed 115 buffers on the input ports (vs 11,633 endpoints violating under estimates).

## 4. Antenna: root cause and decision
* `RESET_B` of 10,323 flops is a single net (`rst_n`). `repair_design` buffered it as a **daisy chain of 7 `clkbuf_16`** each driving 100–170 pins (`net1083…1097`, fanout 139/171/159/137 in DRT warnings), routed mostly on met1. Partial ratio on those pins 770–780 vs limit 400. The GRT-stage antenna estimate also counted jumper/diode insertions that detailed routing later re-did.
* Comparison of the two GRT-stage attempts (objective): `ANTENNA_11` 5 nets/20 pins, 316 diodes, +790 µm²; `ANTENNA_12` (8 iterations, margin 20) 5 nets/38 pins, 687 diodes, +1,719 µm²: **11 is better** (fewer pins, half the diodes). More iterations did not converge (5 nets from iteration 5 on) — `charts/12,13`.
* Decision: do not iterate further at GRT stage. Add post-GRT `repair_design`/hold repair *before* antenna repair, rely on the DRT-stage repair on real wires, and check after DRT. Result: V3 2 pins → V4/V5/V6 **0**. The reset is functionally unchanged.
* Remaining reset-tree weakness: still a deep buffer chain (SS latency ≈10 ns to the last `RESET_B`); recovery slack +89.9 ns, removal +0.017…+0.64 ns.

## 5. Electrical (slew/cap/fanout)
Drivers found with SPEF (`physical_design/reports/signoff_v6/viol_max_ss`, scripts `classify_viol.tcl`): V3: reset chain and mux-select nets driven by `clkbuf_16`/`buf_12` (7-deep `max_cap` chains on register-file selects). V4: weak hold cells (`clkdlybuf4s25_1`) on long wires, 9,340 pins. After ECO: 38 nets slew, mostly hold cells and single-fanout `o21ai/a21boi`; CTS nodes `clknet_4_*` (fanout 16–17, 0.21–0.26 pF).
No Liberty limit was relaxed and no checker was disabled. Residual violations are against the *flow's* stricter limits and are reported as FAIL.

## 6. SDC v4 (what changed and why)
`physical_design/constraints/soc_constraint_omega_v4.sdc`: v2 I/O delays kept (2 ns); added `set_clock_uncertainty 0.25`, `set_clock_transition 0.15`, ±5 % derate, `set_max_fanout 10`/`transition 0.75`/`capacitance 0.2`, `inv_2` driving cell on inputs and clock, 33.4 fF output load, and `rst_n`: `-max 2` / `-min 0`. Justification for `rst_n`: assertion is asynchronous (not timed), release is host-driven relative to `clk`; min 0 ns is the worst case for removal, max 2 ns matches other host inputs; the 100 ns period gives recovery margin ≈90 ns. I deliberately did **not** reuse "set_input_delay 2" blindly: removal was verified in all corners (+0.017 ns min, FF) and `check_setup` is clean. No false paths, no multicycle, no case analysis were added.

## 7. Final result (V6, post-route)
Cells 111,661 non-fill (+619,567 fill), core utilization 27.8 % (non-fill), area 0.849 mm² logic+taps, wirelength 3.318 m (met1 1.371, met2 1.494, met3 0.287, met4 0.166), 478,554 vias (all single-cut), power 12.6 mW (nom_tt, default activity, estimate), IR drop 0.09 mV. Images: `visuals/01…10`; charts: `charts/`.
The die is sparsely used (28 %), which made routing and antenna closure easy but is area-inefficient; the 1800×1800 µm outline was kept as requested.
