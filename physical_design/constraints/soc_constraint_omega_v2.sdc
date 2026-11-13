create_clock -name core_clk -period 100 [get_ports clk]
set_input_delay 2 -clock core_clk [get_ports {run imem_we imem_waddr* imem_wdata* dma_ready dma_rdata*}]
set_output_delay 2 -clock core_clk [get_ports {pc* cpu_illegal result* result_valid irq dma_read dma_addr*}]
# rst_n is asynchronous and excluded from data input delays.
# Recovery/removal and CDC/reset integration still require independent verification.
