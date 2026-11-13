# Physical design (LibreLane 3.0.11, SKY130A)

| Path | Content |
|---|---|
| `config/config_v4.json`, `config_v5.json` | flow configuration of the V4 base run and the V5/V6 re-route (post-GRT repair off). `config.json`, `config_*_0x.json` are the earlier V2-series configs (kept for the record). |
| `constraints/` | `soc_constraint_omega_v4.sdc` (**used**: limits, driving cell, load, uncertainty, derate, `rst_n` constrained), v2/v3 (superseded, kept), `*_liberty_only.sdc` (diagnostic variant) |
| `scripts/eco_full.tcl` | ECO on the routed DB with real SPEF: `repair_design` + `repair_timing -hold`, legalize, strip routes |
| `scripts/run_sta_all.sh`, `sta_final.tcl` | independent 9-corner STA with extracted SPEF |
| `scripts/write_lef.tcl` | abstract LEF via OpenROAD (`write_abstract_lef`), because Magic's WriteLEF produced an empty file in this flow |
| `scripts/*.py` | image/chart generators (need the ODB/DEF/GDS of a run; `OMEGA_RELEASE` for the release dir) |
| `scripts/reproduce.sh` | the reference command sequence (documentation, not a one-click script) |
| `reports/signoff_v6/` | DRC, LVS, XOR, antenna, IR drop, 9-corner STA, violation classification of the final layout |
| `reports/signoff_history/`, `reports/eco/`, `reports/audit/` | evidence of earlier runs (V3/V4/V5), ECO rounds and the independent audit |
| `reports/v7/`, `reports/iterations/` | final V7 signoff evidence (DRC, LVS, antenna, STA incl. independent run, metrics) and the per-iteration STA summaries V7 r1 … V15 |
| `reports/caravel/` | wrapper PDN/route/STA evidence (V6 macro) |
| `scripts/eco_v7*.tcl`, `eco_v9.tcl` … `eco_v15.tcl` | the electrical-closure ECOs of V7 (see `docs/results/V7_ECO_REPORT.md`) |

Run databases (ODB, DEF, SPEF, SDF, stream-out GDS) are large and stay outside git. Key flow rules learned: custom `PNR_SDC_FILE` bypasses LibreLane's `base.sdc`; resizer decisions depend on whether parasitics are estimated or extracted; run **one** Docker job at a time on small hosts.
