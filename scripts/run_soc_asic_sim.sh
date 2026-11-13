#!/usr/bin/env bash
# RTL simulation of the synthesizable ASIC top (programmable IMEM).
set -euo pipefail
source "$(dirname "$0")/_common.sh"; need verilator; need python3
python3 scripts/build_demo_rom.py
verilator --binary --timing --assert -Wno-fatal --top-module tb_omega_fusion_soc_asic \
  --Mdir "$BUILD/obj_soc_asic" -o omega_soc_asic_sim \
  "${ACC[@]}" "${CPU[@]}" "${SOC_ASIC[@]}" tb/regression/tb_omega_fusion_soc_asic.sv
"$BUILD/obj_soc_asic/omega_soc_asic_sim"
