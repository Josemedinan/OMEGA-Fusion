# SIGNOFF REPORT — omega_fusion_soc_asic, run V6 (final layout)

> **Baseline notice.** This report describes the **V6** layout. The current candidate **V7** (same RTL, ECO-closed slew/cap/hold; 1 fanout net open) is documented in `docs/results/V7_ECO_REPORT.md` and `docs/results/FINAL_STATUS.json`.
> **Path note.** Paths in backticks are relative to the repository root. Large artifacts (SPEF, KLayout GDS, routed DEF, run databases) are not stored in git; their SHA-256 are in `deliverables/SHA256SUMS.original.txt`. `deliverables/lef` and `deliverables/netlist` hold gzip-compressed copies (`*.gz`); GDS, SPEF, KLayout GDS and DEF are GitHub Release assets (`docs/RELEASE_ASSETS.md`).


Legend: PASS = measured and met · FAIL = measured and not met · UNVERIFIED = no evidence produced (never counted as PASS).
Evidence root: `physical_design/reports/signoff_v6/`. Layout checked: the V6 GDS (release asset `omega_fusion_soc_asic_V6.gds.gz`, `docs/RELEASE_ASSETS.md`).

## Verdict: `TAPEOUT_READY = NO`
Blockers: slew/cap/fanout limit violations (FAIL), Caravel wrapper DRC/LVS/antenna and timing closure bookkeeping (UNVERIFIED/open), equivalence check and shuttle pre-check (UNVERIFIED).

## Physical verification (final GDS)
| Criterion | Result | Evidence |
|---|---|---|
| DRC Magic | **PASS** — 0 errors | `magic_drc/drc.magic.rpt` (COUNT 0) |
| DRC KLayout (sky130A deck) | **PASS** — 0 errors | `metrics.json: klayout__drc_error__count=0`, `manufacturability.rpt` |
| Routing DRC (TritonRoute) | **PASS** — 0 (iterations 40→7→2→0…0) | `metrics.json: route__drc_errors` |
| LVS (Netgen) | **PASS** — "Circuits match uniquely", 67,494 devices / 66,673 nets, 0 diff | `lvs/lvs.netgen.rpt` |
| Antenna (post detailed route) | **PASS** — 0 nets / 0 pins | `antenna/`, `manufacturability.rpt` |
| GDS integrity (Magic vs KLayout XOR) | **PASS** — no differences | `xor/` |
| Disconnected pins / shorts / opens | **PASS** — 0 critical disconnected pins; LVS clean covers shorts/opens | `metrics.json` |
| PDN connectivity + IR drop | **PASS** — PSM: all shapes on VDD and VSS connected; worst drop 0.092 mV on VDD (0.005 %), 0.080 mV VSS bounce (nom_ss, 12.6 mW) | `irdrop.rpt` |
| Fill / density rules | PASS (covered by DRC above; 619,567 fill cells) | |

## Timing (post-route, extracted SPEF, 9 corners nom/min/max × tt/ss/ff, SDC v4)
Reproduced by two engines: LibreLane `STAPostPNR` (`sta_multicorner_summary.rpt`) and my independent OpenROAD script (`sta/*.summary.txt`, `sta_independent_summary.csv`). nom_tt, max_ss, max_ff agree exactly with the flow.

| Check | Result |
|---|---|
| Setup (100 ns) | **PASS** all 9 corners, 0 violations; worst +52.03 ns (max_ss); indicative reg-to-reg fmax ≈ 20.8 MHz at max_ss |
| Hold | **PASS** all 9 corners, 0 violations; worst +0.017 ns (max_ff). Thin margin in FF; SS worst +0.051 ns (max_ss) |
| Reset recovery (rst_n) | **PASS** worst +89.9 ns (max_ss) |
| Reset removal (rst_n) | **PASS** worst +0.017 ns (max_ff), +0.64 ns (max_ss) with `rst_n` min input delay 0 ns |
| Unconstrained endpoints / missing constraints | **PASS** `check_setup -verbose` empty for max_ss (rst_n now constrained) |
| Clock skew | worst setup skew 0.46 ns (flow, nom), insertion delay 5.2 ns (SS/max) |

## Electrical limits
Limits = flow defaults (max_transition 0.75 ns, max_capacitance 0.2 pF, max_fanout 10), written explicitly in SDC v4. **Not relaxed.**

| Check | Result |
|---|---|
| Max slew @ 0.75 ns | **FAIL** — 158 pins max_ss (105 nom_ss, 71 min_ss), 16 nom_tt, 2 max_ff, 0 nom_ff/min_ff. Was 12,908 before ECO (V4) |
| Max cap @ 0.2 pF | **FAIL** — 18–23 pins per corner; 17 are CTS tree nodes (`clknet_4_*`, `clkbuf_8`, cap 0.21–0.26 pF) + 6 data nets |
| Max fanout @ 10 | **FAIL** — 83 nets per corner (16–17 are CTS tree nodes with fanout 16–17; rest mux-select/decode nets, fanout 11–17) |
| Liberty-only limits (same SDC without `set_max_*`) | max_ff, max_tt, nom_ss: **0/0/0**. max_ss: **3 slew** (net `clk` 1.56 ns at the CTS root and the diode on it) — artifact of modelling the clock port with an `inv_2` driving cell into the 0.2 pF root load. Caravel drives `wb_clk_i` from its own tree. |

Classification of the residuals (`physical_design/reports/signoff_v6/viol_max_ss/`): 25 slew nets (dlygate/clkdlybuf hold cells and o21ai/a21boi long single-fanout wires), 6 cap, 8 fanout non-clock nets; plus CTS nodes. A third ECO round (resize + re-route, ≈2.5 h) would remove most data nets; the CTS nodes need a different CTS clustering (not done).

## Functional / equivalence
| Check | Result |
|---|---|
| RTL regression (`run_soc_asic_sim.sh`) | **PASS** (`verification/rtl_soc_asic_sim.log`) |
| Gate-level simulation of final post-route netlist (Icarus, sky130 functional models, zero delay) | **PASS** — IMEM programmed, RV32 controller, MMIO folded MAC, C00=4, IRQ=1 (`verification/gate_level_sim.log`) |
| SDF back-annotated gate simulation | UNVERIFIED (not run) |
| Formal equivalence RTL vs netlist (Yosys EQY) | UNVERIFIED (`RUN_EQY` off; not run) |
| RTL changes | none; ECO touches only buffers/cell sizes |

## Integration (Caravel) — see `CARAVEL_INTEGRATION_REPORT.md`
| Check | Result |
|---|---|
| Macro LEF/GDS/netlist/SPEF consumed by wrapper | PASS (wrapper flow ran) |
| Wrapper PDN: vccd1/2, vdda1/2, vssd1/2, vssa1/2 connected; no PSM-0038/0039/0069 | **PASS** |
| Wrapper detailed routing DRC | PASS (0) |
| Wrapper post-route antenna | **FAIL** — 1 net / 1 pin (wrapper logic, not the macro) |
| Wrapper flat STA (9 corners, wb_clk 25 ns) | setup ≥ +2.58 ns, hold ≥ +0.091 ns (raw per-corner reports); LibreLane's final bookkeeping step was killed (OOM) → treated as **UNVERIFIED** formally |
| Wrapper DRC (Magic/KLayout), LVS, XOR | **UNVERIFIED** (not run; memory) |
| Shuttle pre-check / platform rules | **UNVERIFIED** |

## History of the evidence (what changed between runs)
| Run | SDC | Post-route hold worst (max_ss) | Slew viol. (max_ss) | Antenna (post-DRT) |
|---|---|---|---|---|
| V3 baseline (repair on GRT estimate, SDC v3) | v3 | −0.605 ns (260 endpoints in max_ss; 552 over all corners) | 8,559 | 2 nets / 2 pins |
| V4 (SDC v4 full flow) | v4 | −1.198 ns (642) | 12,908 | 0 |
| V5 (ECO 1: repair_design with real SPEF + hold) | v4 | +0.055 | 231 | 0 |
| **V6 final (ECO 2)** | v4 | **+0.051** | **158** | **0** |
(`charts/03…06`, `charts/data/postroute_sta_by_run_corner.csv`)

## Items that must not be quoted as PASS
Slew/cap/fanout "0 violations", wrapper-level DRC/LVS/antenna/timing, equivalence, shuttle readiness.
