// Synthesis-only blackbox for hardened OMEGA-Fusion macro.
// Do not include together with RTL implementation in a simulation build.
`default_nettype none
(* blackbox *) module omega_fusion_soc_asic (
`ifdef USE_POWER_PINS
    inout wire VDD,
    inout wire VSS,
`endif
    input  wire        clk,
    input  wire        rst_n,
    input  wire        run,
    input  wire        imem_we,
    input  wire [7:0]  imem_waddr,
    input  wire [31:0] imem_wdata,
    output wire [31:0] pc,
    output wire        cpu_illegal,
    output wire [31:0] result,
    output wire        result_valid,
    output wire        irq,
    output wire        dma_read,
    output wire [31:0] dma_addr,
    input  wire        dma_ready,
    input  wire [31:0] dma_rdata
);
endmodule
`default_nettype wire
