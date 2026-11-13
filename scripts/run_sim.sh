#!/usr/bin/env bash
# Directed test of the accelerator, both datapath variants (FOLDED=0 / 1).
set -euo pipefail
source "$(dirname "$0")/_common.sh"; need verilator
for folded in 0 1; do
  echo "=== MAC ARCHITECTURE FOLDED=$folded ==="
  verilator --binary --timing --assert -Wno-fatal -GFOLDED=$folded \
    --top-module tb_omega_fusion --Mdir "$BUILD/obj_mac_$folded" -o omega_fusion_sim \
    "${ACC[@]}" tb/directed/tb_omega_fusion.sv
  "$BUILD/obj_mac_$folded/omega_fusion_sim"
done
