#!/usr/bin/env bash
# UNTESTED. SDF back-annotated gate-level simulation of the V7 netlist (nom_tt corner) with Icarus Verilog's $sdf_annotate.
# Needs the V7 SDF from the LibreLane run (runs/OMEGA_V15_RT/final/sdf/nom_tt_025C_1v80/*.sdf, ~30 MB, not in git), the unfilled or filled netlist and the PDK.
# Known risks: sky130 UDP flip-flops start with X until reset; Icarus' SDF support is partial. If it does not work, use a commercial/other simulator.
set -euo pipefail
: "${PDK_ROOT:?}" "${SDF:?path to omega_fusion_soc_asic__nom_tt_025C_1v80.sdf}"
cd "$(dirname "$0")/../.."; mkdir -p build/sdf pending_results
V=$PDK_ROOT/sky130A/libs.ref/sky130_fd_sc_hd/verilog
gzip -dc deliverables/v7/netlist/omega_fusion_soc_asic.nl.v.gz > build/sdf/netlist.v
cat > build/sdf/tb_sdf.sv <<'TB'
`timescale 1ns/1ps
module sdf_wrap; tb_omega_fusion_soc_asic t(); initial $sdf_annotate(`SDF_FILE, t.dut, , "sdf.log", "TYPICAL"); endmodule
TB
python3 scripts/build_demo_rom.py
iverilog -g2012 -DFUNCTIONAL=0 -DSDF_FILE="\"$SDF\"" -o build/sdf/sdf.vvp "$V/primitives.v" "$V/sky130_fd_sc_hd.v" build/sdf/netlist.v tb/regression/tb_omega_fusion_soc_asic.sv build/sdf/tb_sdf.sv
vvp build/sdf/sdf.vvp | tee pending_results/sdf_sim.log
grep -q '^PASS ASIC SOC' pending_results/sdf_sim.log
