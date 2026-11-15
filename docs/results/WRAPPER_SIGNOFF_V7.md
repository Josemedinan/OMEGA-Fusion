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

Root cause found: all functional wrapper pins (`wb_*`, `wbs_*`, `la_*`, `user_irq`) are on the **south** edge (`pin_order.cfg`), while the macro is placed with orientation `N` at (560, 860), so its 176 signal pins are on its **north** face (y = 2659.72). Each net must go around the 1.8 mm macro, about 1.8 mm of wire with 0.77 pF, and repeaters cannot be placed over the macro. The macro driver therefore sees a long first segment and the slew is high.

Proposed fix (not applied): place the macro with a flipped orientation (`FS`) in `macro.cfg` so its pins face the south edge, about 860 µm from the wrapper pins, with no macro crossing. This changes only the wrapper floorplan, not the frozen macro. It requires re-running the whole wrapper chain and every check above (Magic DRC alone is about 6 h on this host).

## What is still required before TAPEOUT_READY can become YES

1. Re-run the wrapper with the `FS` macro orientation (or another fix) and obtain 0 slew/cap/fanout violations, or a written waiver by the owner.
2. Finish KLayout DRC (BEOL) and run wrapper LVS, which was not attempted on this host.
3. Run formal equivalence (EQY), the SDF simulation and the real shuttle pre-check (ChipFoundry `cf precheck`).
4. Resolve the macro fanout failure on `net2070` (see `NET2070_ANALYSIS.md`), or waive it in writing.

Related review documents: `POWER_IR_REVIEW.md` (all figures are estimates), `TESTABILITY_DFT_ASSESSMENT.md` (no class-A blockers; IMEM readback, scan/BIST and debug are missing), `CLOCK_RESET_COHERENCE.md` (supported `wb_clk_i` ≤ 20 MHz).
