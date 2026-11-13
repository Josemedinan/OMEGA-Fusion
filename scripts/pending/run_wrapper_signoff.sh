#!/usr/bin/env bash
# UNTESTED END-TO-END. Caravel user_project_wrapper flow with the V7 macro: PDN, placement, routing, STA, stream-out, DRC (Magic/KLayout), LVS, antenna.
# Needs: Docker, LibreLane 3.0.11 CLI, SKY130A PDK (PDK_ROOT), >= 16 GB RAM, >= 60 GB disk.
# Env: OMEGA_RELEASE_V7 = directory with the unpacked V7 files:  gds/omega_fusion_soc_asic.gds  lef/omega_fusion_soc_asic.lef
#      netlist/omega_fusion_soc_asic.nl.nofill.v (non-filled netlist; the filled one ran out of memory on an 8 GB host)  spef/{nom,min,max}/omega_fusion_soc_asic.<c>.spef
set -euo pipefail
: "${OMEGA_RELEASE_V7:?}" "${PDK_ROOT:?}"
REPO=$(cd "$(dirname "$0")/../.." && pwd); mkdir -p pending_results
export OMEGA_RELEASE=$OMEGA_RELEASE_V7
cd "$REPO/caravel/openlane"
librelane --dockerized -m "$REPO" -m "$OMEGA_RELEASE_V7" --pdk-root "$PDK_ROOT" --pdk sky130A --run-tag WRAP_V7_FULL config_v7.json 2>&1 | tee "$OLDPWD/pending_results/wrapper_v7_full.log"
# Evidence to read afterwards: runs/WRAP_V7_FULL/*-magic-drc, *-klayout-drc, *-netgen-lvs, *-checkantennas*, *-stapostpnr/summary.rpt
