#!/usr/bin/env bash
# Caravel wrapper lint + Wishbone bridge/DMA test + end-to-end wrapper->SoC test (RTL).
set -euo pipefail
source "$(dirname "$0")/_common.sh"; need verilator
mkdir -p "$BUILD"
CAR=caravel/rtl
verilator --lint-only -Wno-fatal -DMPRJ_IO_PADS=38 --top-module user_project_wrapper \
  $CAR/user_project_wrapper.v $CAR/omega_wb_bridge.v $CAR/omega_fusion_soc_asic_bb.v
echo OMEGA_WRAPPER_LINT=PASS
verilator --binary --timing -j 2 -Wno-fatal --top-module tb_omega_bridge -Mdir "$BUILD/obj_bridge" \
  tb/regression/tb_omega_bridge.sv $CAR/omega_wb_bridge.v
"$BUILD/obj_bridge/Vtb_omega_bridge" | grep '^OMEGA_'
verilator --binary --timing -j 2 -Wno-fatal -DMPRJ_IO_PADS=38 --top-module tb_omega_caravel_soc -Mdir "$BUILD/obj_caravel_soc" \
  tb/regression/tb_omega_caravel_soc.sv $CAR/user_project_wrapper.v $CAR/omega_wb_bridge.v \
  "${SOC_ASIC[@]}" "${CPU[@]}" "${ACC[@]}"
"$BUILD/obj_caravel_soc/Vtb_omega_caravel_soc" | grep '^OMEGA_'
