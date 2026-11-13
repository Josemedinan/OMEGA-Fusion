`timescale 1ns/1ps
`default_nettype none
module tb_omega_fusion #(parameter bit FOLDED = 1'b1);
    logic clk=1'b0;
    always #5 clk=~clk;
    logic rst_n=0;
    logic bus_valid=0,bus_write=0;
    logic [11:0] bus_addr=0;
    logic [31:0] bus_wdata=0;
    wire bus_ready;
    wire [31:0] bus_rdata;
    wire irq;
    wire [31:0] dma_addr;
    wire dma_read;
    logic [31:0] dma_rdata;
    logic dma_ready;
    reg [7:0] external_bytes[0:31];
    reg signed [7:0] a[0:15],b[0:15];
    integer test_count=0;
    logic [1:0] dma_stall_phase=0;
    always_ff @(posedge clk) begin
        if(!rst_n) dma_stall_phase<=0;
        else if(dma_read) dma_stall_phase<=dma_stall_phase+1'b1;
    end
    integer seed=32'h01234567;
    omega_fusion #(.FOLDED(FOLDED)) dut(.*);
    // External memory is a combinational, little-endian word read interface;
    // responses are VALID on asserted ready, including deliberate stalls.
    always_comb begin
        dma_ready=dma_read && (dma_stall_phase!=2'b01);
        dma_rdata=32'd0;
        if (dma_read && dma_addr<=28) begin
            for(integer z=0;z<4;z=z+1)
                dma_rdata[8*z+:8]=external_bytes[dma_addr+z];
        end
    end
    task automatic mmio_write(input logic [11:0] addr,input logic [31:0] data);
        @(negedge clk);
        bus_valid=1;bus_write=1;bus_addr=addr;bus_wdata=data;
        @(negedge clk);
        bus_valid=0;bus_write=0;bus_addr=0;bus_wdata=0;
    endtask
    task automatic mmio_read(input logic [11:0] addr,output logic [31:0] data);
        @(negedge clk);
        bus_valid=1;bus_write=0;bus_addr=addr;
        #1;data=bus_rdata;
        @(negedge clk);
        bus_valid=0;bus_addr=0;
    endtask
    function automatic integer value(input logic [7:0] x,input bit int4);
        if(int4) begin
            if(x[3]) value=$signed({{28{1'b1}},x[3:0]});
            else value=$signed({28'd0,x[3:0]});
        end else value=$signed({{24{x[7]}},x});
    endfunction
    task automatic check_matrix(input bit int4,input bit use_dma);
        logic [31:0] status,got;
        integer expected,aa,bb;
        for(integer r=0;r<4;r=r+1)
            for(integer c=0;c<4;c=c+1) begin
                expected=0;
                for(integer k=0;k<4;k=k+1) begin
                    aa=value(a[r*4+k],int4);
                    bb=value(b[k*4+c],int4);
                    expected=expected+aa*bb;
                end
                mmio_read(12'(12'h300+4*(r*4+c)),got);
                if($signed(got)!==expected)
                    $fatal(1,"Mismatch mode=%b dma=%b C[%0d,%0d]: got=%0d expected=%0d",int4,use_dma,r,c,$signed(got),expected);
            end
        mmio_read(12'h004,status);
        if((status & 32'hb) !==32'hA || irq!==1'b1)
            $fatal(1,"Bad completion status=%h irq=%b",status,irq);
        test_count=test_count+1;
    endtask
    task automatic launch_case(input bit int4,input bit use_dma);
        logic [31:0] status;
        integer polls;
        mmio_write(12'h000,32'h8);
        if(use_dma) begin
            for(integer i=0;i<16;i=i+1) begin
                external_bytes[i]=a[i];
                external_bytes[i+16]=b[i];
            end
            mmio_write(12'h008,32'h0);
            mmio_write(12'h000,32'h4|(int4?32'h2:32'h0));
        end else begin
            for(integer i=0;i<16;i=i+1) begin
                mmio_write(12'(12'h100+4*i),{24'd0,a[i]});
                mmio_write(12'(12'h200+4*i),{24'd0,b[i]});
            end
            mmio_write(12'h000,32'h1|(int4?32'h2:32'h0));
        end
        polls=0;
        status=0;
        while(!status[1] && polls<100)begin
            mmio_read(12'h004,status);
            polls=polls+1;
        end
        if(!status[1])$fatal(1,"Timeout case=%0d",test_count);
        check_matrix(int4,use_dma);
    endtask
    initial begin
        repeat(3)@(negedge clk);
        rst_n=1;
        for(integer t=0;t<8;t=t+1) begin
            for(integer i=0;i<16;i=i+1) begin
                case(t)
                    0:begin a[i]=8'(i-8);b[i]=8'(i-8);end
                    1:begin a[i]=8'h80;b[i]=8'h7f;end
                    2:begin a[i]=8'hf8;b[i]=8'h07;end
                    3:begin a[i]=8'h07;b[i]=8'h08;end
                    4:begin a[i]=8'd0;b[i]=8'd0;end
                    default:begin a[i]=8'($random(seed));b[i]=8'($random(seed));end
                endcase
            end
            launch_case(t[0],t[1]);
        end
        // Controlled error behavior: refuse unaligned DMA source.
        mmio_write(12'h008,32'h1);
        mmio_write(12'h000,32'h4);
        begin
            logic [31:0] status;
            mmio_read(12'h004,status);
            if((status & 32'h4)==0)$fatal(1,"unaligned DMA not rejected");
        end
        $display("PASS: %0d matrix cases, %0d outputs, INT8/INT4, host/DMA, IRQ and error",test_count,test_count*16);
        $finish;
    end
endmodule
`default_nettype wire
