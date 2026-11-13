# Synthesis

Synthesis is the first step of the LibreLane flow (Yosys 0.62, ABC, `sky130_fd_sc_hd`); there is no separate synthesis script in this repository.
Input RTL: `rtl/accelerators/*.sv`, `rtl/cpu/omega_rv32_controller.sv`, `rtl/soc/omega_fusion_soc_asic.sv` (listed in `physical_design/config/config_v5.json`).
Result recorded in the V2 checkpoint series: **43,448 cells** after synthesis (before floorplan, tap cells, buffering, CTS and repair), see `docs/physical_design/PHYSICAL_DESIGN_REPORT.md` §1.
Memory: the 256×32 instruction RAM maps to flip-flops and muxes (`SYNTH_MEMORY_MAX_BITS` was raised in the earlier ORFS attempt; LibreLane maps it the same way).
The V2 synthesis run directory is a recovery checkpoint kept in the work tree, not in this repository.
