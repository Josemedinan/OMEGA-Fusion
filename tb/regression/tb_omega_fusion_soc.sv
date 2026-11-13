`timescale 1ns/1ps
`default_nettype none
module tb_omega_fusion_soc;
    logic clk=0,rst_n=0;
    always #5 clk=~clk;
    logic [31:0] rom[0:255];
    wire [31:0] pc;
    wire illegal,irq;
    wire [31:0] result;
    wire valid;
    wire [31:0] instruction=(pc<1024)?rom[pc[9:2]]:32'd0;
    omega_fusion_soc_demo dut(.clk(clk),.rst_n(rst_n),.instruction(instruction),
        .pc(pc),.cpu_illegal(illegal),.demo_result(result),
        .demo_result_valid(valid),.irq(irq));
    bit success;
    initial begin
        success=1'b0;
        for(integer z=0;z<256;z=z+1)rom[z]=32'h00000013;
        $readmemh("firmware/rom/omega_demo.hex",rom);
        repeat(4)@(negedge clk);
        rst_n=1;
        for(integer t=0;t<500;t=t+1) begin
            @(negedge clk);
            if(illegal)$fatal(1,"CPU illegal PC=%h instruction=%h",pc,instruction);
            if(valid)begin
                if($signed(result)!==4)$fatal(1,"CPU result mismatch %0d",$signed(result));
                if(!irq)$fatal(1,"Expected IRQ high");
                success=1'b1;
                break;
            end
        end
        if(!success) $fatal(1,"SoC timeout PC=%h",pc);
        $display("PASS SOC: CPU RV32I-subset firmware executed, MMIO matrix multiply -> C[0,0]=%0d, IRQ=%b",$signed(result),irq);
        $finish;
    end
endmodule
`default_nettype wire
