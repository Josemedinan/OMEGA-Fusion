#!/usr/bin/env bash
# Full host-side regression: Python oracles + RTL lint + all RTL simulations.
set -euo pipefail
source "$(dirname "$0")/_common.sh"
python3 scripts/build_demo_rom.py
python3 scripts/validate_soc_rom.py
python3 scripts/reference.py
bash scripts/run_lint.sh
bash scripts/run_sim.sh
bash scripts/run_soc_sim.sh
bash scripts/run_soc_asic_sim.sh
bash scripts/run_caravel_sim.sh
printf '\nPASS all RTL simulation and software reference checks completed\n'
