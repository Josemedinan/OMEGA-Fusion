# V7 — electrical closure ECO (iterations 7–15 on top of the V6 baseline)

> Paths in backticks are relative to the repository root. V6 (`docs/results/SIGNOFF_REPORT.md`) is **not** overwritten: it stays the verified baseline. "V7" is the layout produced by nine ECO/re-route iterations on V6; its LibreLane run tag is `OMEGA_V15_RT` (the iteration counter kept running from the V4–V6 series). Evidence: `physical_design/reports/iterations/`, `charts/data/v7_iterations.csv`, `charts/18_eco_iterations_v6_to_v7.png`.

## Result (post-route, extracted SPEF, 9 corners, flow limits unchanged)

| Check | V6 baseline | **V7** |
|---|---|---|
| Setup worst slack | +52.03 ns | **+54.67 ns** (0 violations, 9 corners) |
| Hold worst slack | +0.017 ns (max_ff) | **+0.102 ns** (min_ff; 0 violations, 9 corners) |
| Max slew > 0.75 ns | 158 pins (max_ss) | **0** (all corners) |
| Max cap > 0.2 pF | 18–23 per corner | **0** (all corners) |
| Max fanout > 10 | 83 nets | **1 net — FAIL** (`net2070`, driver `fanout2070`: 11 loads = 10 gates + 1 antenna diode) |
| Antenna after detailed routing | 0 | 0 nets / 0 pins |
| Routing DRC | 0 | 0 |
| DRC Magic / KLayout | 0 / 0 | 0 / 0 |
| LVS (Netgen) | match, 67,494 devices | "Circuits match uniquely", 68,162 devices, 67,003 nets, 0 differences |
| XOR Magic vs KLayout stream-out | 0 | 0 |
| Disconnected pins / illegal overlaps | 0 / 0 | 0 / 0 |
| Gate-level simulation (zero delay) of the final netlist | PASS | PASS (`verification/gate_level_sim_v7.log`) |
| Cells (excl. fill) / std-cell area / utilization | 111,661 / 0.849 mm² / 27.8 % | 112,514 / 0.852 mm² / 27.9 % |
| TritonCTS cells as built | 2,168 buf + 102 inv | 2,168 buf + 102 inv (same tree; the 22 clock-path buffers added by the ECO — 20 clones, 2 root buffers — are not in this count) |
| Timing-repair buffers / antenna diodes | 20,875 / 1,598 | 20,940 / 2,121 |
| Wirelength / vias | 3.318 m / 478,554 | 3.335 m / 481,234 |
| Power (estimate, nom_tt, default activity) | 12.6 mW | 12.7 mW |

**What V7 does not change:** wrapper (Caravel) DRC/LVS/antenna/STA, formal equivalence, SDF simulation and the shuttle pre-check are still UNVERIFIED/FAIL as in V6. The Caravel integration evidence in `docs/results/CARAVEL_INTEGRATION_REPORT.md` was produced with the **V6** macro. With the **V7** macro only the wrapper **PDN stage** was run (`WRAP_V7_PDN`, `physical_design/reports/caravel_v7/`): all 8 power nets connected (PSM-0040), no PSM-0038/0039/0069. Wrapper placement, routing, antenna, STA, DRC and LVS were **not** run with V7. `TAPEOUT_READY` therefore stays **NO**.

## What was wrong in V6, and what each iteration did
Residual V6 violations (158 slew / 23 cap / 83 fanout, flow limits) were **not** only the clock tree. Root causes found by inspecting the routed database:

1. **Clock tree (TritonCTS, 16 level-4 nodes with 16–17 sinks, 0.21–0.26 pF) and ~50 clock leaf buffers with 11 sinks.** Fixed by cloning the driving `clkbuf` and moving half of the sinks (no extra clock level), and by moving single sinks to neighbouring leaf buffers with room.
2. **Clock root.** The `clk` port is modelled with an `inv_2` driving cell; a long wire to `clkbuf_0` plus a stray antenna diode gave 1.77 ns slew. Fixed by a `clkbuf_16` near the pin, a repeater half way, and removing the diode from the port net.
3. **Weak drivers on long wires** (`nor4_4`, `o31ai_4`, `clkdlybuf4s15_1`, ...): buffers inserted half way did not help; buffers placed **next to the driver** did.
4. **Stranded antenna diodes.** When a net was split behind buffers, its antenna diodes stayed on the original net, 100–1,400 µm from the driver (e.g. net8662: driver at y = 1666 µm, diodes at y = 208 µm), hanging long wires and capacitance on weak gates. Fixed by re-homing every diode onto the buffer net nearest to it.
5. **Diodes counted as fanout.** The STA counts antenna diodes as loads; nets with up to 11 diodes exceeded the limit of 10. Fixed by placing a sink and its diode cluster behind one `buf_6`.
6. **Convergence is slow** because every re-route changes wires and the antenna repair re-inserts diodes: V13 and V14 each ended with 3 and 1 fanout nets again. Iteration 15 reduced it to the single net above; it was left as a declared FAIL after the last round.

Also learned: (a) OpenROAD's `repair_antennas` crashed (SIGSEGV in `grt::RepairAntennas::setDiodeLoc`, twice) after diodes had been deleted leaving gaps in the `ANTENNA_<n>` numbering; renumbering the diodes contiguously removed the crash (cause not proven, observed effect only). (b) The first ECO (buffer at the clock root) broke hold (−0.637 ns) because input hold margin was only 17 ps; a SPEF-based `repair_timing -hold` with 0.08–0.10 ns margin restored it with 25 buffers.

## Iterations (flow STA, flow limits; antenna and routing DRC were 0 in every iteration)
`charts/data/v7_iterations.csv`, chart `charts/18_eco_iterations_v6_to_v7.png`.

| Iteration | Hold WS [ns] | Setup WS [ns] | Slew (max_ss) | Cap (worst corner) | Fanout nets |
|---|---:|---:|---:|---:|---:|
| V6 baseline | +0.017 | +52.03 | 158 | 23 | 83 |
| V7 r1 | −0.637 | +52.94 | 106 | 11 | 4 |
| V8 | −0.014 | +54.39 | 73 | 9 | 3 |
| V9 | +0.104 | +54.37 | 87 | 3 | 0 |
| V10 | +0.102 | +54.14 | 38 | 2 | 2 |
| V11 | +0.101 | +54.78 | 11 | 0 | 3 |
| V12 | +0.102 | +54.84 | 11 | 0 | 1 |
| V13 | +0.103 | +54.91 | 0 | 0 | 3 |
| V14 | +0.102 | +54.96 | 0 | 0 | 1 |
| **V15 = V7 final** | **+0.102** | **+54.67** | **0** | **0** | **1** |

## Method and scripts (`physical_design/scripts/`)
`eco_v7.tcl` (clock clones, root buffer, data nets) → `eco_v7b.tcl` (fanout of clock leaves) → `eco_v7c.tcl` (diodes inflating fanout) → `eco_v7d.tcl` (diode renumbering) → `eco_full.tcl` (resize + hold repair with the real SPEF) → `eco_v9.tcl` … `eco_v15.tcl`. Each ECO reads the routed database and the extracted SPEF of the previous iteration, edits only buffers, buffer placement, cell sizes and antenna diodes (never RTL, SDC or limits), strips the routing and hands over to LibreLane for global routing → detailed routing → antenna repair → RCX → STA. Instances created are prefixed `v7_`, `v9_`, … so they can be audited. The SDC (v4) and the flow limits (0.75 ns / 0.2 pF / 10) were not touched.

## Caveats
* The intermediate run databases were deleted to keep the disk from filling (99 % full several times); only each iteration's STA summary, state metrics and antenna logs are kept (`physical_design/reports/iterations/`). The final V15 run is kept in the work tree.
* ECO estimates printed by OpenROAD after an edit (e.g. "slew=0") were often optimistic because new nets have no SPEF; only the post-route numbers above count.
* One manual specificity: `eco_v10.tcl`–`eco_v15.tcl` evolved from each other and contain historical headers; `eco_v13.tcl`+ apply the same rules with new instance prefixes to avoid name collisions.
* Functional equivalence of V7 to the RTL is supported by the zero-delay gate-level simulation only (same test as the RTL); formal equivalence was not run.
