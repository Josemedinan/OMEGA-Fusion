# Wrapper sign-off with the V7 macro (`user_project_wrapper`)

Date: 2026-11-15. Status: **TAPEOUT_READY = NO**.

This document records what was actually run on the Caravel `user_project_wrapper` that instantiates the frozen V7 macro `omega_fusion_soc_asic`, and what is still open. Every number below comes from a run directory on the build host (LibreLane 3.0.11 in Docker, SKY130A ciel `8afc8346a57fe1ab7934ba5a6056ea8b43078e71`, 5.8 GB Docker memory). Nothing here was relaxed to obtain a better status.

## Setup of the runs

* Macro LEF used by the wrapper: `signoff_v7/lef_v2/omega_fusion_soc_asic.v2.lef` (full-area obstructions). With the original LEF, Magic reported 357 met2.2 marks caused by wrapper routes crossing the macro.
* Boundary buffers and a repeater ECO (`repair_design -max_wire_length 400`) were applied on the 176 macro-pin nets before global routing.
* Final route/stream-out run: `W7_G`; XOR and DRC run: `W7_H`.

## Results

| Check | Result | Evidence / note |
|---|---|---|
| Route DRC (OpenROAD) | PASS, 0 | `route__drc_errors = 0` |
| Antenna (post-route) | PASS, 0 nets / 0 pins | `antenna__violating__nets = 0` |
| IR drop (static) | 72 µV worst, 0.21 µV average | estimate, static only; see `POWER_IR_REVIEW.md` |
| Setup, 9 corners | PASS | worst slack +8.81 ns (`max_ss_100C_1v60`), 0 violations |
| Hold, 9 corners | PASS | worst slack +0.182 ns (`min_ff_n40C_1v95`), 0 violations |
| GDS XOR (Magic vs KLayout stream-out) | PASS, 0 differences | `design__xor_difference__count = 0` |
| Magic DRC (full wrapper GDS) | PASS, 0 errors | `magic__drc_error__count = 0`, runtime about 6 h |
| KLayout DRC, FEOL part | PASS, 0 items | run split in FEOL and BEOL to fit memory |
| KLayout DRC, BEOL part | RUNNING at time of writing | single thread; the one-shot run was killed by the OS for memory (SIGKILL) |
| LVS (wrapper) | NOT RUN | |
| Max slew / max cap / max fanout | **FAIL** | 876 slew, 100 cap, 58 fanout violations (worst corner `max_ss`) |
| EQY, SDF simulation, shuttle pre-check | NOT RUN | |

## Open failure: slew / capacitance / fanout

Setup and hold close with margin, because the STA already includes the delay of the slow edges. The design-rule limits (max transition 1.5 ns) are nevertheless violated: worst slew 4.16 ns, mostly on `ANTENNA_*` diode pins and on `wire*` repeater inputs.

Root cause (corrected 2026-11-15; the first version of this document said all macro pins were on one face, which was wrong): all functional wrapper pins (`wb_*`, `wbs_*`, `la_*`, `user_irq`) are on the **south** edge (`pin_order.cfg`), while the macro LEF has its 179 pins on all four edges: 92 outputs on the top edge, 8 outputs and 34 inputs on the bottom, 24 inputs on the top, 11 on the right and 8 on the left. With orientation `N` at (560, 860) the 92 top outputs are about 1.8 mm of wire away from the south pins, around the macro (0.7 pF per net), and repeaters cannot be placed over the macro, so the first segment is long and the slew is high. Antenna diodes added on those long nets are counted as extra load/fanout and violate the slew limit themselves.

Experiments on the plain flow (no ECO), worst corner `max_ss_100C_1v60`, all with route DRC 0 and antenna 0:

| Run | Macro placement | Slew | Cap | Fanout | Worst setup / worst hold (any of 9 corners) |
|---|---|---|---|---|---|
| `W7_G` (previous, with repeater ECO) | `N` at (560, 860) | 876 | 100 | 58 | +8.81 / +0.182 ns |
| `W8_C` | `N` at (560, 860) | 850 | 26 | not counted | +9.48 / +0.162 ns |
| `W8_B` | `FS` at (560, 860) | 566 | 57 | not counted (17 nets in the sampled list) | +10.66 / +0.069 ns |
| `W8_D` | `FS` at (560, 200) | 1141 | 104 | 35 (flow metric) | +11.82 / +0.148 ns |

`FS` at y = 860 is the best placement tried: it brings the 92 output pins to the south side, but the 34 bottom inputs move to the far side. Lowering the macro to y = 200 made it **worse** (1141 slew violations), so the best candidate is `W8_B`. No run reaches zero violations, so the criterion remains a **FAIL**; the remaining nets (about 40 pins on the far side of the macro, plus diodes counted as load on long nets) need a buffering ECO placed in the free channels around the macro, or a written owner waiver. Timing (setup and hold) closes in all 9 corners in every run.

## What is still required before TAPEOUT_READY can become YES

1. Re-run the wrapper with the `FS` macro orientation (or another fix) and obtain 0 slew/cap/fanout violations, or a written waiver by the owner.
2. Finish KLayout DRC (BEOL) and run wrapper LVS, which was not attempted on this host.
3. Run formal equivalence (EQY), the SDF simulation and the real shuttle pre-check (ChipFoundry `cf precheck`).
4. Resolve the macro fanout failure on `net2070` (see `NET2070_ANALYSIS.md`), or waive it in writing.

Related review documents: `POWER_IR_REVIEW.md` (all figures are estimates), `TESTABILITY_DFT_ASSESSMENT.md` (no class-A blockers; IMEM readback, scan/BIST and debug are missing), `CLOCK_RESET_COHERENCE.md` (supported `wb_clk_i` ≤ 20 MHz).
