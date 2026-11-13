# OMEGA-Fusion SDC v4 (supersedes v2/v3; originals kept untouched).
# v2 only had create_clock + I/O delays: no design-rule limits, driving cell, load,
# uncertainty, transition or derate, so resizer/STA ran under-constrained.
# v4 keeps v2 I/O delays (2 ns) and adds the LibreLane base.sdc defaults for everything else.
create_clock -name core_clk -period 100 [get_ports clk]
set_clock_uncertainty 0.25 [get_clocks core_clk]
set_clock_transition 0.15 [get_clocks core_clk]
set_timing_derate -early 0.95
set_timing_derate -late 1.05

# design-rule limits (same numbers as LibreLane defaults / MAX_*_CONSTRAINT)

# interface model
set all_inputs_wo_clk [lsearch -all -inline -not -exact [all_inputs] [get_ports clk]]
set_driving_cell -lib_cell sky130_fd_sc_hd__inv_2 -pin Y $all_inputs_wo_clk
set_driving_cell -lib_cell sky130_fd_sc_hd__inv_2 -pin Y [get_ports clk]
set_load 0.033442 [all_outputs]

set_input_delay 2 -clock core_clk [get_ports {run imem_we imem_waddr* imem_wdata* dma_ready dma_rdata*}]
set_output_delay 2 -clock core_clk [get_ports {pc* cpu_illegal result* result_valid irq dma_read dma_addr*}]

# rst_n: asserted asynchronously, released by the host relative to clk.
# Constrained so recovery/removal checks on every RESET_B pin are timed (v2 left them unconstrained).
# max 2 ns (recovery, 100 ns period => huge margin); min 0 ns = worst case for removal
# (host may release immediately after the clock edge), so any host release time in [0,2] ns is safe.
set_input_delay -max 2 -clock core_clk [get_ports rst_n]
set_input_delay -min 0 -clock core_clk [get_ports rst_n]
