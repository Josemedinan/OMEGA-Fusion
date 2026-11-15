# Power, IR-drop and constraint-coverage review (V7 macro)

Date 2026-11-13. Evidence: `OMEGA_V15_RT/17-openroad-stapostpnr/*/power.rpt`, `18-openroad-irdropreport/irdrop.rpt`, `metrics.json`, `sta_independent_summary`.
**Classification: everything in this document is an ESTIMATE. None of it is a signoff certification.**

## What was computed, and how
| Quantity | Value | Method / conditions | Representativeness |
|---|---|---|---|
| Total power (flow STA, nom_tt 25 °C 1.8 V) | 10.77 mW (internal 7.34, switching 3.42, leakage 0.002 mW) | OpenSTA `report_power` on the routed netlist with extracted SPEF, **default activity** (no `set_power_activity`, no VCD/SAIF): default input toggle assumption and ideal clock toggling every cycle | **Not representative**: real activity of the CPU/IMEM/MAC under firmware was not applied. The clock group (3.66 mW, 34 %) and sequential internal power (4.42 mW) dominate because all 10,323 flops are clocked every cycle (no clock gating); that part is largely workload-independent, the combinational/switching part is not. |
| Total power quoted in earlier reports (12.6–12.7 mW) | 12.7 mW | `power__total` metric of the flow (different step/corner than the number above) | same caveat; do not mix the two figures |
| Leakage | ≈ 2 µW (nom_tt); larger at the ff/100 °C corners | Liberty leakage | Corner-dependent; the ss/ff leakage was not reported separately in this pass |
| IR drop, VDD | 86.5 µV worst (0.01 %), 8.15 µV average | `analyze_power_grid` (OpenROAD PSM) at **nom_ss_100C_1v60, total power 8.98 mW**, static (DC) | **Static average-power analysis only.** No peak/dynamic (switching-edge) current, no decap, no package/bump impedance, no vector-based current waveforms. The PDN is met1 rails + met4 straps (153.6 µm pitch) over 3.05 mm²; with ~9 mW average the DC drop is tiny by construction. |
| Ground bounce, VSS | 77.6 µV worst | same | same |
| PDN connectivity | PASS: "All shapes on net VDD/VSS are connected" (PSM-0040) for the macro; 8/8 wrapper nets connected with the V7 macro (stage-only run) | PSM connectivity check | valid (topological) |

## What the numbers do *not* show
1. **Dynamic IR drop / peak current.** All 10,323 flops and 2,270 clock buffers switch on the same clock edge. A DC analysis at average power cannot bound the instantaneous supply droop. A rough bound can be made (peak ≈ clock-tree + flop internal charge delivered within ~100–300 ps), but it was **not** computed here and would need a dynamic/vectored analysis (OpenROAD PSM with `-vcd`/instance-level current profiles, or a commercial tool) plus a decap and package model.
2. **Activity.** No VCD/SAIF-based power was run. The gate-level simulation exists (zero delay) and could drive an OpenROAD `read_vcd` activity annotation; that analysis is listed as pending (needs the simulation VCD of the real firmware and ~GB of disk).
3. **Corners.** IR drop was evaluated at nom_ss only; power at nom_tt only. Worst-case power corner (ff, −40 °C/100 °C, 1.95 V) not analysed.
4. **Thermal.** No thermal model. Order-of-magnitude: ≈ 11–13 mW over 3.2 mm² of die is a very low power density (≈ 4 mW/mm²); self-heating is expected to be negligible, but this is a reasoning, not an analysis.
5. **Package/board.** Supply requirements: `vccd1` 1.8 V (nominal), `vssd1`. The wrapper/Caravel supplies (vccd1 1.8 V) are the pad ring's responsibility; decoupling and bond-wire inductance are outside this design.

## Constraint coverage (setup, hold, recovery, removal) — macro level
| Check | Coverage evidence | Result (V7, 9 corners) | Limitation |
|---|---|---|---|
| Setup / hold | `check_setup -verbose` empty at macro level; all 10,323 flops and all I/O have constraints (SDC v4) | setup ≥ +54.67 ns, hold ≥ +0.102 ns | SDC assumes 2 ns input/output delays and a 100 ns clock; true system clock ≤ 20 MHz (see coherence doc) |
| Recovery / removal (`rst_n`) | `set_input_delay -max 2 / -min 0` on `rst_n` | recovery ≥ +88.7 ns, removal ≥ +0.466 ns | the macro timing model used by the wrapper STA carries `rst_n` as setup/hold-type arcs (setup 8.26 ns, hold −3.0 ns at max_ss), not as native recovery/removal arcs — conservative representation, wrapper result positive |
| Unconstrained / unused | at wrapper level: 68 inputs without input delay (`io_in[37:0]`, `analog_io[28:0]`, `user_clock2` — all unused, no loads) and 30 unconstrained endpoints (`analog_io`, constant output `la_data_out[64]`) | benign | justified by connectivity (no logic behind them) |
| Exceptions | Caravel template multicycle paths (setup 2 / hold 1) through `wbs_cyc_i`, `wbs_stb_i`, `wbs_ack_o`; no OMEGA-added false paths, multicycle, case analysis | present only from the Caravel SDC | inherited from the platform template; not justified by OMEGA's own analysis |
