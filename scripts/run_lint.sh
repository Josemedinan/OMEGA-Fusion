#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_common.sh"; need verilator
verilator --lint-only -Wno-fatal --top-module omega_fusion "${ACC[@]}"
verilator --lint-only -Wno-fatal --top-module omega_fusion_soc_demo "${ACC[@]}" "${CPU[@]}" "${SOC_DEMO[@]}"
verilator --lint-only -Wno-fatal --top-module omega_fusion_soc_asic "${ACC[@]}" "${CPU[@]}" "${SOC_ASIC[@]}"
echo "PASS lint (warnings are non-fatal; see output above)"
