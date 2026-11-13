`timescale 1ns/1ps
`default_nettype none
// Synthesizable ASIC integration: RV32I-subset CPU + writable instruction RAM
// + MMIO INT4/INT8 folded accelerator. No fixed firmware is baked into silicon.
// Program the 256 x 32-bit instruction memory with run=0; assert rst_n=0
// at least one clock edge before starting CPU operation with run=1.
// Instruction RAM is implemented in flip-flops for SKY130HD, not an SRAM macro.
module omega_fusion_soc_asic (
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
    // Stores are only accepted while CPU is halted. Host is responsible for
    // loading code and asserting reset before each new execution.
    logic [31:0] imem [0:255];
    always_ff @(posedge clk) begin
        if (imem_we && !run)
            imem[imem_waddr] <= imem_wdata;
    end

    wire [31:0] instruction = (pc[31:10] == 22'd0)
        ? imem[pc[9:2]] : 32'h00000000;
    wire cpu_valid, cpu_write, acc_ready;
    wire [31:0] cpu_addr, cpu_wdata, cpu_rdata, acc_rdata;
    wire acc_access = cpu_valid &&
                      cpu_addr[31:12] == 20'h40000 &&
                      cpu_addr[11:0] < 12'h400;
    wire result_access = cpu_valid && cpu_addr == 32'h4000_0400;
    logic [31:0] result_q;
    logic result_valid_q;

    omega_rv32_controller u_cpu (
        .clk(clk), .rst_n(rst_n), .enable(run), .instruction(instruction),
        .pc(pc), .mem_valid(cpu_valid), .mem_write(cpu_write),
        .mem_addr(cpu_addr), .mem_wdata(cpu_wdata),
        .mem_rdata(cpu_rdata), .illegal(cpu_illegal)
    );
    omega_fusion #(.FOLDED(1'b1)) u_acc (
        .clk(clk), .rst_n(rst_n),
        .bus_valid(acc_access && run), .bus_write(cpu_write),
        .bus_addr(cpu_addr[11:0]), .bus_wdata(cpu_wdata),
        .bus_ready(acc_ready), .bus_rdata(acc_rdata), .irq(irq),
        .dma_addr(dma_addr), .dma_read(dma_read),
        .dma_ready(dma_ready), .dma_rdata(dma_rdata)
    );
    assign cpu_rdata = acc_access ? acc_rdata :
                       result_access ? result_q : 32'd0;
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            result_q <= 32'd0;
            result_valid_q <= 1'b0;
        end else if (run && result_access && cpu_write) begin
            result_q <= cpu_wdata;
            result_valid_q <= 1'b1;
        end
    end
    assign result = result_q;
    assign result_valid = result_valid_q;
endmodule
`default_nettype wire
