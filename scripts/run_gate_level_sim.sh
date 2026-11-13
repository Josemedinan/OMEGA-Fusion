#!/usr/bin/env bash
# Zero-delay functional gate-level simulation of the post-route netlist (NOT an SDF simulation).
# Needs: iverilog, the SKY130A PDK (set PDK_ROOT) and the netlist (default deliverables/v7/netlist/*.nl.v.gz; set NETLIST=deliverables/netlist/omega_fusion_soc_asic.nl.v.gz for V6).
set -euo pipefail
source "$(dirname "$0")/_common.sh"; need iverilog; need python3
: "${PDK_ROOT:?set PDK_ROOT to the directory containing sky130A}"
V=$PDK_ROOT/sky130A/libs.ref/sky130_fd_sc_hd/verilog
mkdir -p "$BUILD/gl"
python3 scripts/build_demo_rom.py
gzip -dc "${NETLIST:-deliverables/v7/netlist/omega_fusion_soc_asic.nl.v.gz}" > "$BUILD/gl/netlist.v"
iverilog -g2012 -DFUNCTIONAL -DUNIT_DELAY='#0' -o "$BUILD/gl/gl_sim.vvp" \
  "$V/primitives.v" "$V/sky130_fd_sc_hd.v" "$BUILD/gl/netlist.v" tb/regression/tb_omega_fusion_soc_asic.sv
vvp "$BUILD/gl/gl_sim.vvp" | tee "$BUILD/gl/gate_level_sim.log"
grep -q '^PASS ASIC SOC' "$BUILD/gl/gate_level_sim.log"
