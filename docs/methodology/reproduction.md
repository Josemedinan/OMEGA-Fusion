# Reproduction guide

## 1. RTL and gate-level simulation (verified from this repository layout, 2026-11-12)
Requirements: Python ≥ 3.10, Verilator ≥ 5 with `--binary --timing` (tested 5.053), Icarus Verilog (tested: oss-cad-suite build 14.0-devel), SKY130A PDK for the gate-level cell models.
```bash
bash scripts/run_all.sh                  # ~25 s on an Apple M3
PDK_ROOT=$HOME/.ciel bash scripts/run_gate_level_sim.sh   # ~20 s, zero-delay
```
The SKY130A PDK can be installed with `ciel` (`pip install ciel`; `ciel enable --pdk-family sky130 8afc8346a57fe1ab7934ba5a6056ea8b43078e71`). Check the exact CLI of your ciel version.

## 2. Physical flow (documented, NOT re-run from this layout)
* Tools: LibreLane 3.0.11 (Docker image `ghcr.io/librelane/librelane:3.0.11`), see `docs/methodology/tool_versions_container.txt`. Docker is required.
* Resources: **≥ 16 GB RAM, ≥ 40 GB free disk recommended.** On an 8 GB MacBook Air M3 the flow worked only with a single Docker job at a time and several restarts after swap/disk exhaustion; the wrapper-level DRC/LVS and the wrapper STA bookkeeping step ran out of memory (exit 137) there.
* Sequence: `physical_design/scripts/reproduce.sh` (reference, one LibreLane run tag per stage, resumable with `-i <state_out.json>`). Config paths in `physical_design/config/*.json` were rewritten to the repository layout (`dir::../../rtl/...`) and verified to resolve, but the flow was not executed again after the rewrite.
* Known flow pitfalls (details in `docs/physical_design/PHYSICAL_DESIGN_REPORT.md`): custom `PNR_SDC_FILE` bypasses `base.sdc`; `--docker-no-tty` must precede `--dockerized`; Magic's `WriteLEF` produced an empty LEF (use `physical_design/scripts/write_lef.tcl`); skip `Odb.CheckDesignAntennaProperties` when the LEF comes from OpenROAD.

## 3. Inspect results
```bash
# GDS files are release assets (docs/RELEASE_ASSETS.md); after downloading and checking the sha256:
gunzip -k omega_fusion_soc_asic_V7.gds.gz && klayout omega_fusion_soc_asic_V7.gds
less physical_design/reports/signoff_v6/sta_independent_summary.csv
less physical_design/reports/signoff_v6/lvs/lvs.netgen.rpt
```

## 4. Regenerate figures
`python3 scripts/make_architecture_diagram.py` (matplotlib). Layout images/charts need run databases (ODB/DEF/GDS, not in git) and the scripts in `physical_design/scripts/` (`make_visuals.py`, `vis_final.py`, `collect_charts*.py`, `render_klayout.py`); chart data in `charts/data/` can be re-plotted without the databases.
