# net2070 — the single open fanout violation of V7

> Paths are relative to the repository root. Data: `physical_design/reports/v7/net2070/`; scripts: `physical_design/scripts/net2070_analyze.tcl`, `net2070_diode.tcl` (OpenROAD, run on the V7 routed database with the max-corner extracted SPEF, Liberty `ss_100C_1v60`).

## Facts
| Question | Answer (measured) |
|---|---|
| Net / driver / loads | `net2070`, driver `fanout2070` (`buf_2`), 11 loads: 5 × `and2_2` + 5 × `nor2_2` + 1 × `diode_2` (`ANTENNA_2107`) |
| Where does the limit of 10 come from? | **The project SDC**: `set_max_fanout 10 [current_design]` in `physical_design/constraints/soc_constraint_omega_v4.sdc` (the value equals LibreLane's default `MAX_FANOUT_CONSTRAINT`). The sky130_fd_sc_hd Liberty files define **no** `max_fanout` attribute (0 occurrences); they only set `default_max_transition 1.5 ns`. So this is a design-rule constraint of this project/flow, not a cell-library limit. |
| Effective capacitance | 0.065–0.067 pF (pin 0.029–0.031 pF + wire 0.036 pF) against the 0.2 pF limit: **33 %** of the limit |
| Real slew | **0.287 ns** at the driver output in max_ss, against the 0.75 ns limit: **38 %** of the limit |
| Timing risk | None demonstrable (max_ss library, max-corner SPEF): the worst setup path through the net has **+76.1 ns** of slack (period 100 ns; `fanout2070` contributes 0.55 ns) and the worst hold path through it **+5.0 ns**; no slew or capacitance violation on the net |
| Is the diode needed? | Not strictly for the OpenROAD antenna check on this net: with the diode `check_antennas` reports the worst pin at 8 % of the allowed ratio; **without** it, 0 violations, worst pin `_51016_/A` at **81 %** of the allowed ratio (the diode's wire stub was left in place, so the figure is conservative). The diode therefore buys a 10× larger margin; the flow's own antenna repair works with a 10 % margin (90 % threshold), which 81 % still satisfies — but with little room. |
| Can it be fixed locally? | Deleting the diode would also leave its routing stub; a clean fix needs that net re-routed, i.e. a detailed re-route of (at least) the net plus RCX, STA, DRC/LVS re-runs. Every re-route in iterations V11–V15 let the antenna repair re-insert diodes and move the single violation to a different net (V13: 3 nets, V14: 1, V15: 1). |

## Decision
No further ECO. The violation does not threaten function, timing, slew or capacitance, and a local fix cannot be made without a re-route that has shown to move the problem rather than remove it. **V7 is kept as is, and the violation stays documented as FAIL against the project's own fanout rule.** The fanout limit was **not** changed or waived in the SDC, and the checker was not modified. If a later iteration wants to close it, the recommended minimal ECO is: delete `ANTENNA_2107`, re-route only `net2070` incrementally on a large-memory host, then re-run RCX, STA, antenna check, DRC and LVS.
