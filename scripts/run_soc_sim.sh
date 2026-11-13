#!/usr/bin/env bash
# Firmware-driven SoC demo (fixed ROM supplied by the testbench).
set -euo pipefail
source "$(dirname "$0")/_common.sh"; need verilator; need python3
python3 scripts/build_demo_rom.py
verilator --binary --timing --assert -Wno-fatal --top-module tb_omega_fusion_soc \
  --Mdir "$BUILD/obj_soc" -o omega_soc_sim \
  "${ACC[@]}" "${CPU[@]}" "${SOC_DEMO[@]}" tb/regression/tb_omega_fusion_soc.sv
"$BUILD/obj_soc/omega_soc_sim"
