# Pending verification and tapeout steps (V7)

`TAPEOUT_READY = NO`. This document lists every mandatory item that is open, why, what it needs and how to run it. Scripts are in `scripts/pending/`; except where stated they were **not executed** (the host was an 8 GB MacBook Air; memory, not logic, was the blocker). Do not treat a script's existence as a result.

| # | Item | State for V7 | Why open | Needs | How |
|---|---|---|---|---|---|
| 1 | Wrapper PDN with V7 macro | **PASS** (stage-only) | — | done on the 8 GB host | `WRAP_V7_PDN`; evidence `physical_design/reports/caravel_v7/pdn_generatepdn_v7.log` (PSM-0040 for 8/8 nets, no PSM-0038/0039/0069) |
| 2 | Wrapper placement, routing, antenna | UNVERIFIED (V6 macro: route DRC 0, **antenna 1 net FAIL**) | not run with V7; the V6 antenna net was never repaired | ≥ 16 GB RAM | `scripts/pending/run_wrapper_signoff.sh`, then fix the wrapper antenna net (diode/jumper) and re-check |
| 3 | Wrapper STA (9 corners, `wb_clk` 25 ns) | UNVERIFIED (V6: raw per-corner slack ≥ +2.58 ns setup, ≥ +0.091 ns hold, bookkeeping step killed by OOM) | the filled macro netlist exhausted memory; use the V7 **non-filled** netlist (`deliverables/v7/netlist/*nofill*`) | ≥ 16 GB RAM | same script |
| 4 | Wrapper DRC (Magic, KLayout), LVS, XOR | UNVERIFIED | wrapper GDS embeds the 156 MB macro GDS plus fill; Magic/KLayout/Netgen did not fit in 8 GB | ≥ 16 GB RAM, ≥ 60 GB disk | same script (stages after stream-out) |
| 5 | Formal equivalence | UNVERIFIED | `RUN_EQY` never enabled; EQY covers RTL vs post-synthesis netlist only, not the PnR edits | CPU time; ≥ 16 GB for a 43k-cell netlist | `scripts/pending/run_eqy.sh` (untested); post-route vs RTL needs a netlist-level equivalence tool not provided here. The zero-delay gate-level simulation of the V7 netlist passes but is not a proof |
| 6 | SDF back-annotated simulation | UNVERIFIED | not attempted; Icarus' SDF support is partial and sky130 UDP flops need careful reset handling | SDF files from the run (~30 MB each, not in git) | `scripts/pending/run_sdf_sim.sh` (untested) |
| 7 | Shuttle pre-check | UNVERIFIED | needs a signed-off wrapper GDS and the current program rules | Docker, ≥ 16 GB | `scripts/pending/run_precheck.sh` (stub with instructions) |
| 8 | Fanout rule on `net2070` | FAIL (1 net) | deliberately left; see `NET2070_ANALYSIS.md` | a re-route on a large host | recommended minimal ECO documented there |
| 9 | Physical flow reproduction from this repository layout | NOT DONE | only RTL + gate-level re-run from it | ≥ 16 GB, ~10 h | `physical_design/scripts/reproduce.sh` (reference sequence) |
| 10 | License of the original sources | OPEN | owner's decision | — | `docs/LICENSES_AND_SECURITY_AUDIT.md` §3 |

Requirements for items 2–4 and 9: ≥ 16 GB RAM, ≥ 60 GB free disk, Docker, LibreLane 3.0.11, SKY130A (ciel `8afc8346a57fe1ab7934ba5a6056ea8b43078e71`), the V7 release assets unpacked into one directory (`docs/RELEASE_ASSETS.md`) and `OMEGA_RELEASE_V7` pointing to it (layout described in the script header). The wrapper config for V7 is `caravel/openlane/config_v7.json` (paths via `$OMEGA_RELEASE`).

`TAPEOUT_READY` becomes YES only when items 2–7 are PASS (and 8 is PASS or formally waived by the owner with a written rationale), with evidence in the repository.
