`timescale 1ns/1ps
`default_nettype none
// Integration smoke-test harness. Instruction ROM lives in TESTBENCH.
// CPU is RV32I subset, not the separately developed OMEGA-32 core.
module omega_fusion_soc_demo (
    input wire clk,
    input wire rst_n,
    input wire [31:0] instruction,
    output wire [31:0] pc,
    output wire cpu_illegal,
    output logic [31:0] demo_result,
    output logic demo_result_valid,
    output wire irq
);
    wire cpu_valid,cpu_write;
    wire [31:0] cpu_addr,cpu_wdata,cpu_rdata;
    wire acc_ready;
    wire [31:0] acc_rdata;
    wire [31:0] dma_addr;
    wire dma_read;
    wire acc_access = cpu_valid && cpu_addr[31:12]==20'h40000 && cpu_addr[11:0]<12'h400;
    wire result_access = cpu_valid && cpu_addr==32'h4000_0400;
    omega_rv32_controller u_cpu (
        .clk(clk),.rst_n(rst_n),.enable(1'b1),.instruction(instruction),.pc(pc),
        .mem_valid(cpu_valid),.mem_write(cpu_write),.mem_addr(cpu_addr),
        .mem_wdata(cpu_wdata),.mem_rdata(cpu_rdata),.illegal(cpu_illegal)
    );
    omega_fusion #(.FOLDED(1'b1)) u_acc (
        .clk(clk),.rst_n(rst_n),
        .bus_valid(acc_access),.bus_write(cpu_write),
        .bus_addr(cpu_addr[11:0]),.bus_wdata(cpu_wdata),
        .bus_ready(acc_ready),.bus_rdata(acc_rdata),.irq(irq),
        .dma_addr(dma_addr),.dma_read(dma_read),
        .dma_ready(1'b0),.dma_rdata(32'd0)
    );
    assign cpu_rdata=acc_access ? acc_rdata :
                     result_access ? demo_result : 32'd0;
    always_ff @(posedge clk or negedge rst_n)begin
        if(!rst_n)begin demo_result<=0;demo_result_valid<=0;end
        else if(result_access && cpu_write)begin
            demo_result<=cpu_wdata;demo_result_valid<=1;
        end
    end
endmodule
`default_nettype wire
