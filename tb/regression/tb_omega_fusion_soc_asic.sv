`timescale 1ns/1ps
`default_nettype none
module tb_omega_fusion_soc_asic;
    logic clk = 0;
    logic rst_n = 0;
    logic run = 0;
    logic imem_we = 0;
    logic [7:0] imem_waddr = 0;
    logic [31:0] imem_wdata = 0;
    always #5 clk = ~clk;
    wire [31:0] pc, result, dma_addr;
    wire illegal, valid, irq, dma_read;
    logic [31:0] rom [0:255];
    omega_fusion_soc_asic dut (
        .clk(clk), .rst_n(rst_n), .run(run),
        .imem_we(imem_we), .imem_waddr(imem_waddr), .imem_wdata(imem_wdata),
        .pc(pc), .cpu_illegal(illegal), .result(result),
        .result_valid(valid), .irq(irq),
        .dma_read(dma_read), .dma_addr(dma_addr),
        .dma_ready(1'b0), .dma_rdata(32'd0)
    );
    bit success;
    initial begin
        success = 0;
        for (integer i=0; i<256; i++) rom[i] = 32'h00000013;
        $readmemh("firmware/rom/omega_demo.hex", rom);
        // Program instruction memory while CPU is halted and held in reset.
        for (integer i=0; i<256; i++) begin
            @(negedge clk);
            imem_we=1;
            imem_waddr=8'(i);
            imem_wdata=rom[i];
        end
        @(negedge clk);
        imem_we=0;
        repeat(4) @(negedge clk);
        rst_n=1;
        repeat(3) @(negedge clk);
        if (pc !== 32'h0) $fatal(1,"CPU advanced while run=0, PC=%h",pc);
        run=1;
        for (integer t=0; t<600; t++) begin
            @(negedge clk);
            if (illegal) $fatal(1,"Illegal instruction PC=%h",pc);
            if (valid) begin
                if ($signed(result) !== 32'sd4)
                    $fatal(1,"Result mismatch expected 4, got %0d",$signed(result));
                if (!irq) $fatal(1,"Expected accelerator IRQ");
                success=1;
                break;
            end
        end
        if (!success) $fatal(1,"ASIC SoC timeout PC=%h",pc);
        $display("PASS ASIC SOC: programmed IMEM, RV32 controller, MMIO folded MAC, C00=4, IRQ=1");
        $finish;
    end
endmodule
`default_nettype wire
