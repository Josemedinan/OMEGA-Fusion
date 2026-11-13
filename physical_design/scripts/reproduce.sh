#!/usr/bin/env bash
# Reference command sequence of the V6 physical-design flow (LibreLane 3.0.11 Classic, Docker).
# This documents what was run; it is NOT a one-click script: every stage is a separate, resumable LibreLane run tag
# and the ECO stage (eco_full.tcl) is run by hand inside the container. Run ONE Docker job at a time.
# Memory: the flow wedged Docker on an 8 GB host (swap exhausted); use >= 16 GB RAM and >= 40 GB free disk.
set -euo pipefail
REPO=${REPO:-$(cd "$(dirname "$0")/../.." && pwd)}      # this repository
WORK=${WORK:-$HOME/omega-work}                            # scratch dir for LibreLane runs (tens of GB)
PDK_ROOT=${PDK_ROOT:-$HOME/.ciel}                         # ciel hash: see docs/methodology/tool_versions.md
LL=${LIBRELANE:-librelane}
RL="$LL --docker-no-tty --dockerized -m $REPO --pdk-root $PDK_ROOT --pdk sky130A --condensed --hide-progress-bar"
mkdir -p "$WORK"; cd "$REPO/physical_design/config"
# 1. synthesis .. GPL checkpoint (V2 series: config.json, config_pdn_fixed_02.json ...) was produced earlier; see docs.
# 2. GPL -> DRT with SDC v4:
$RL --run-tag OMEGA_V4_FULL --run-dir-base "$WORK" --from OpenROAD.GlobalPlacement \
    --skip Magic.WriteLEF --skip Odb.CheckDesignAntennaProperties config_v4.json
# 3. ECO with real SPEF (physical_design/scripts/eco_full.tcl, env: PDK SM CM HM ODB SDC RCX OUT), twice, then:
#    $RL --run-tag OMEGA_V6_ECO2 --from OpenROAD.GlobalRouting --skip Magic.WriteLEF --skip Odb.CheckDesignAntennaProperties -i <state_eco_e2.json> config_v5.json
# 4. Signoff: --from KLayout.StreamOut ... (Magic DRC, KLayout DRC, XOR, SPEF extraction, Netgen LVS)
# 5. Independent STA: physical_design/scripts/run_sta_all.sh ; LEF: write_lef.tcl ; visuals/charts: make_visuals.py, vis_final.py, collect_charts*.py
# 6. Caravel wrapper: config_final.json (OMEGA_RELEASE must point to the unpacked deliverables)
echo "Reference sequence only - see physical_design/README.md"
