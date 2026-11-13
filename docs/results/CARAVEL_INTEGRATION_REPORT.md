# CARAVEL INTEGRATION REPORT — macro `mprj` in `user_project_wrapper`

> **Notice.** Every result below was obtained with the **V6** macro. With the **V7** macro only the PDN stage was run (`WRAP_V7_PDN`, 2026-11-13, evidence `physical_design/reports/caravel_v7/pdn_generatepdn_v7.log`): PSM-0040 "All shapes … are connected" for vccd1, vccd2, vdda1, vdda2, vssd1, vssd2, vssa1, vssa2; no PSM-0038/0039/0069; only the same informational PDN-0110 warnings (macro-obstruction shapes of nets `mprj` does not use). Wrapper placement/routing/antenna/STA/DRC/LVS are UNVERIFIED for V7.
> **Path note.** Paths in backticks are relative to the repository root. Large artifacts (SPEF, KLayout GDS, routed DEF, run databases) are not stored in git; their SHA-256 are in `deliverables/SHA256SUMS.original.txt`. `deliverables/lef` and `deliverables/netlist` hold gzip-compressed copies (`*.gz`); GDS, SPEF, KLayout GDS and DEF are GitHub Release assets (`docs/RELEASE_ASSETS.md`).


Evidence: `physical_design/reports/caravel/`, images `visuals/09a–09c`. Wrapper variant (original untouched): `openlane/user_project_wrapper_v6/` (config `physical_design/config/config_final.json`). Original wrapper dir `openlane/user_project_wrapper/` and `integration_backup_omega/` are unchanged.

## Root cause of the old PSM-0038 / PSM-0039 / PSM-0069
The earlier macro LEF (`deliverables/lef/` from the ORFS-era netlist) exposed `VDD`/`VSS` **on met5 as horizontal stripes**. The wrapper grid is met4 (vertical) + met5 (horizontal); a met5 macro pin parallel to wrapper met5 stripes gets no via, so `mprj/VDD` and `mprj/VSS` stayed unconnected ("Unconnected instance mprj/VDD", "Check connectivity failed on vssd1"). Limiting the macro's *signal* routing to met4 did not fix this by itself: the old LEF came from a different run. The new macro (PDN on met1+met4, `PDN_MULTILAYER=false`) exposes its power pins on **met4 vertical straps**; wrapper met5 horizontal stripes cross them and `pdn` drops via4 stacks.

## What was checked, on the final macro files
| Item | Result |
|---|---|
| Macro size vs wrapper | LEF `SIZE 1800 BY 1800`, `CLASS BLOCK`; wrapper die 2920×3520 µm; placement (560, 860) N → occupies x 560–2360, y 860–2660: inside the die with margins 560 µm left/right and 860 µm top/bottom → OK |
| Orientation | N, as in `macro.cfg` (`mprj 560 860 N`) |
| Port correspondence | 179 LEF pins = 177 signals (clk, rst_n, run, imem_*, pc, result, irq, dma_*, …) + VDD + VSS; wrapper `omega_wb_bridge` drives the same names; synthesis of the wrapper linked them (`CheckMacroInstances` OK) |
| Power connection | `PDN_MACRO_CONNECTIONS = "mprj vccd1 vssd1 VDD VSS"` |
| **PDN connectivity (PSM-0040)** | **PASS** for all 8 nets: vccd1, vccd2, vdda1, vdda2, vssa1, vssa2, vssd1, vssd2; **no PSM-0038/0039/0069** (`physical_design/reports/caravel/pdn_generatepdn.log`, run `WRAP_FINAL_PDN`) |
| Via warnings | `PDN-0110` "No via inserted between met4 and met5" at 2 shapes of vccd2/vdda1 inside the macro obstruction — nets not used by `mprj`; informational |
| Metal layers used | macro: li1–met4 signal, met1+met4 power; wrapper: routing ≤ met4, PDN met4/met5 |
| Clock/reset interface | `wb_clk_i → mprj.clk` (CLOCK_NET `mprj.clk`), `omega_rst_n` from bridge. Wrapper SDC (Caravel standard) models clock latency 4.65–5.57 ns, consistent with the macro's 3.3–5.2 ns insertion delay |
| Wrapper routing (after fill-free DRT) | 105,048 instances, 1,753 nets, 814,785 µm, **route DRC 0** |
| Wrapper antenna after DRT | **FAIL: 1 net / 1 pin** (wrapper logic; not repaired) |
| Wrapper flat STA with macro netlist + SPEF, 9 corners (clock 25 ns) | setup WNS ≥ **+2.58 ns** (max_ss), hold ≥ **+0.091 ns** (max_ff) — `physical_design/reports/caravel/wrapper_sta_worst_slack.csv`. LibreLane's last bookkeeping step (`filter unannotated nets`) was SIGKILLed (OOM) at every attempt, even with `-j 1`, so this is reported as raw per-corner evidence, **not** as a closed STA signoff |
| Wrapper DRC (Magic/KLayout), LVS, XOR | **UNVERIFIED** — not run: wrapper GDS embeds the 156 MB macro GDS plus the fill cells and the 8 GB host runs out of memory (the wrapper linking STA with the *filled* netlist already hit OOM: exit 137) |
| Shuttle (Efabless/ChipIgnite) pre-check | UNVERIFIED — not run |

## Verdict
Macro ↔ wrapper power connectivity is **fixed and verified** (the specific PSM errors are gone). The wrapper is **not** declared fabrication-ready: wrapper DRC/LVS/antenna (1 open violation) and a closed STA signoff are missing. Suggested next step: run the wrapper stream-out/DRC/LVS on a machine with ≥ 16 GB, and fix the 1 wrapper antenna net (diode/jumper) first.

## Notes for the integrator
* Use `deliverables/netlist/omega_fusion_soc_asic.nl.nofill.v` (non-powered) for hierarchical STA/simulation; the filled netlist (112 MB) exhausts memory in the wrapper STA.
* `config_final.json` is based on `config_omega_iosync.json` + `omega_iosync_compat.sdc` (sets `IO_SYNC` which LibreLane does not export).
