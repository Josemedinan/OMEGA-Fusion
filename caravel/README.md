# Caravel integration (candidate, not fabrication-ready)

* `rtl/` — `user_project_wrapper.v`, `omega_wb_bridge.v` (Wishbone slave → OMEGA control/IMEM/DMA), macro black box, Caravel includes.
* `openlane/` — wrapper configuration (`config_final.json`), macro placement (`macro.cfg`: `mprj 560 860 N`), IO-sync compatible SDC, pin order, Efabless template files (`fixed_dont_change/`).
  `config_final.json` refers to the macro files through `$OMEGA_RELEASE` (unpack `deliverables/` and the SPEF/netlist assets there; the SPEF files are not in git). Not re-run after the path rewrite for this repository layout.
* Results and open items: `docs/results/CARAVEL_INTEGRATION_REPORT.md`.
* Simulation: `bash scripts/run_caravel_sim.sh` (wrapper lint, bridge/DMA test, wrapper→SoC test; RTL only).
