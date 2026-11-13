# v3: v2 constraints + rst_n coverage (v2 left rst_n with no input delay).
create_clock -name core_clk -period 100 [get_ports clk]
set_input_delay 2 -clock core_clk [get_ports {run imem_we imem_waddr* imem_wdata* dma_ready dma_rdata*}]
set_output_delay 2 -clock core_clk [get_ports {pc* cpu_illegal result* result_valid irq dma_read dma_addr*}]
# rst_n: asynchronous assertion, host deasserts it relative to clk. Give it the same
# 2 ns input delay as other synchronous host inputs so recovery/removal are timed
# against the reset tree (async assertion path itself is not a timed data path).
set_input_delay 2 -clock core_clk [get_ports rst_n]
