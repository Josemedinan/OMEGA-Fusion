`timescale 1ns/1ps
`default_nettype none
// 32-bit memory mapped controller. One outstanding bus access, combinational reads.
// DMA reads 32 consecutive bytes from an external read-only 32-bit word interface.
// word[7:0] is byte 0 (little endian); A first, B second.
module omega_fusion #(
    parameter int N = 4,
    parameter int ACC_W = 32,
    parameter bit FOLDED = 1'b1
) (
    input wire clk,
    input wire rst_n,
    input wire bus_valid,
    input wire bus_write,
    input wire [11:0] bus_addr,
    input wire [31:0] bus_wdata,
    output wire bus_ready,
    output logic [31:0] bus_rdata,
    output logic irq,
    output wire [31:0] dma_addr,
    output wire dma_read,
    input wire [31:0] dma_rdata,
    input wire dma_ready
);
    localparam int COUNT=N*N;
    localparam logic [11:0] REG_CONTROL=12'h000;
    localparam logic [11:0] REG_STATUS =12'h004;
    localparam logic [11:0] REG_DMA_SRC=12'h008;
    localparam logic [11:0] REG_CAPS   =12'h00c;
    localparam logic [11:0] REG_A_BASE =12'h100;
    localparam logic [11:0] REG_B_BASE =12'h200;
    localparam logic [11:0] REG_C_BASE =12'h300;

    logic [7:0] mem_a [0:COUNT-1];
    logic [7:0] mem_b [0:COUNT-1];
    logic [COUNT*8-1:0] a_flat, b_flat;
    wire [COUNT*ACC_W-1:0] c_flat;
    logic mode_int4;
    logic busy, done_sticky, error_sticky, mac_start;
    wire mac_done;
    logic [31:0] dma_src;
    logic [3:0] dma_index; // 8 x 32-bit words, 4 for A and 4 for B.
    typedef enum logic [1:0] {IDLE, DMA, COMPUTE, WAIT_MAC} state_t;
    state_t state;

    // Constant, one-cycle host handshake. DMA progresses independently.
    assign bus_ready=bus_valid;
    assign dma_read=(state==DMA);
    assign dma_addr=dma_src + {26'd0,dma_index,2'b00};
    always_comb begin
        for (integer i=0;i<COUNT;i=i+1) begin
            a_flat[i*8+:8]=mem_a[i];
            b_flat[i*8+:8]=mem_b[i];
        end
    end
    generate
        if (FOLDED) begin : g_folded
            omega_fusion_mac_folded #(.N(N),.ACC_W(ACC_W)) u_mac (
                .clk(clk),.rst_n(rst_n),.start(mac_start),.mode_int4(mode_int4),
                .a_flat(a_flat),.b_flat(b_flat),.done(mac_done),.c_flat(c_flat)
            );
        end else begin : g_parallel
            omega_fusion_mac #(.N(N),.ACC_W(ACC_W)) u_mac (
                .clk(clk),.rst_n(rst_n),.start(mac_start),.mode_int4(mode_int4),
                .a_flat(a_flat),.b_flat(b_flat),.done(mac_done),.c_flat(c_flat)
            );
        end
    endgenerate

    logic [3:0] index_a,index_b,index_c;
    logic in_a,in_b,in_c;
    always_comb begin
        in_a=(bus_addr>=REG_A_BASE && bus_addr<(REG_A_BASE+12'(COUNT*4)));
        in_b=(bus_addr>=REG_B_BASE && bus_addr<(REG_B_BASE+12'(COUNT*4)));
        in_c=(bus_addr>=REG_C_BASE && bus_addr<(REG_C_BASE+12'(COUNT*4)));
        index_a=bus_addr[5:2];
        index_b=bus_addr[5:2];
        index_c=bus_addr[5:2];
        bus_rdata=32'd0;
        if (bus_addr[1:0]==2'b00) begin
            if (bus_addr==REG_CONTROL) bus_rdata={30'd0,mode_int4,1'b0};
            else if (bus_addr==REG_STATUS) bus_rdata={28'd0,irq,error_sticky,done_sticky,busy};
            else if (bus_addr==REG_DMA_SRC) bus_rdata=dma_src;
            else if (bus_addr==REG_CAPS) bus_rdata={8'(ACC_W),8'(N),8'd1,8'd1};
            else if (in_a) bus_rdata={24'd0,mem_a[index_a]};
            else if (in_b) bus_rdata={24'd0,mem_b[index_b]};
            else if (in_c) bus_rdata=c_flat[index_c*ACC_W+:32];
        end
    end
    integer j;
    always_ff @(posedge clk or negedge rst_n) begin
        if(!rst_n) begin
            state<=IDLE;busy<=1'b0;done_sticky<=1'b0;error_sticky<=1'b0;
            mode_int4<=1'b0;mac_start<=1'b0;dma_src<=32'd0;dma_index<=4'd0;irq<=1'b0;
            for(integer z=0;z<COUNT;z=z+1)begin mem_a[z]<=8'd0; mem_b[z]<=8'd0; end
        end else begin
            mac_start<=1'b0;
            // Host MMIO writes: control bit0=start (no DMA), bit2=DMA+start,
            // bit1=INT4, bit3=clear flags. Reject commands while busy.
            if(bus_valid && bus_write && bus_ready) begin
                if (bus_addr[1:0]!=2'b00) error_sticky<=1'b1;
                else if(bus_addr==REG_CONTROL) begin
                    if(bus_wdata[3]) begin done_sticky<=1'b0;error_sticky<=1'b0;irq<=1'b0;end
                    if(!busy) begin
                        mode_int4<=bus_wdata[1];
                        if(bus_wdata[2]) begin
                            if(dma_src[1:0]!=2'b00) error_sticky<=1'b1;
                            else begin state<=DMA;dma_index<=4'd0;busy<=1'b1;done_sticky<=1'b0;irq<=1'b0;end
                        end else if(bus_wdata[0]) begin
                            state<=COMPUTE;busy<=1'b1;done_sticky<=1'b0;irq<=1'b0;
                        end
                    end else if(bus_wdata[2] || bus_wdata[0]) error_sticky<=1'b1;
                end else if(bus_addr==REG_DMA_SRC) begin
                    if(!busy) dma_src<=bus_wdata;
                    else error_sticky<=1'b1;
                end else if(in_a) begin
                    if(!busy) mem_a[index_a]<=bus_wdata[7:0];
                    else error_sticky<=1'b1;
                end else if(in_b) begin
                    if(!busy) mem_b[index_b]<=bus_wdata[7:0];
                    else error_sticky<=1'b1;
                end else error_sticky<=1'b1;
            end
            case(state)
                IDLE: begin end
                DMA: if(dma_ready) begin
                    // Capture 4 bytes per word, first 16 bytes -> A, next 16 -> B.
                    for(j=0;j<4;j=j+1) begin
                        if(dma_index<4) mem_a[4*dma_index+j]<=dma_rdata[8*j+:8];
                        else mem_b[4*(int'(dma_index)-4)+j]<=dma_rdata[8*j+:8];
                    end
                    if(dma_index==7) state<=COMPUTE;
                    else dma_index<=dma_index+1'b1;
                end
                COMPUTE: begin mac_start<=1'b1;state<=WAIT_MAC;end
                WAIT_MAC: if(mac_done) begin
                    state<=IDLE;busy<=1'b0;done_sticky<=1'b1;irq<=1'b1;
                end
                default: state<=IDLE;
            endcase
        end
    end
endmodule
`default_nettype wire
