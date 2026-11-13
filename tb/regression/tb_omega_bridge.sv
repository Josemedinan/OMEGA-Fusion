`timescale 1ns/1ps
`default_nettype none
module tb_omega_bridge;
  logic clk = 0;
  always #5 clk = ~clk;
  logic rst = 1;
  logic cyc = 0, stb = 0, we = 0;
  logic [3:0] sel = 0;
  logic [31:0] adr = 0, dat = 0;
  wire ack;
  wire [31:0] rdat;
  wire run, rst_n, imem_we;
  wire [7:0] imem_waddr;
  wire [31:0] imem_wdata;
  logic [31:0] pc = 32'h1234;
  logic illegal = 0, result_valid = 0, irq = 0;
  logic [31:0] result_data = 32'd4;
  logic dma_read = 0;
  logic [31:0] dma_addr = 32'h40001000;
  wire dma_ready;
  wire [31:0] dma_rdata, status, addr_capture;
  int transfers = 0;
  int imem_writes = 0;
  logic [7:0] last_imem_addr;
  logic [31:0] last_imem_data;

  omega_wb_bridge dut (
    .wb_clk_i(clk), .wb_rst_i(rst), .wbs_cyc_i(cyc), .wbs_stb_i(stb),
    .wbs_we_i(we), .wbs_sel_i(sel), .wbs_adr_i(adr), .wbs_dat_i(dat),
    .wbs_ack_o(ack), .wbs_dat_o(rdat), .omega_run(run),
    .omega_rst_n(rst_n), .omega_imem_we(imem_we),
    .omega_imem_waddr(imem_waddr), .omega_imem_wdata(imem_wdata),
    .omega_pc(pc), .omega_cpu_illegal(illegal), .omega_result(result_data),
    .omega_result_valid(result_valid), .omega_irq(irq),
    .omega_dma_read(dma_read), .omega_dma_addr(dma_addr),
    .omega_dma_ready(dma_ready), .omega_dma_rdata(dma_rdata),
    .omega_status(status), .omega_dma_addr_capture(addr_capture)
  );

  always @(posedge clk) begin
    if (!rst) begin
      if (imem_we) begin
        imem_writes <= imem_writes + 1;
        last_imem_addr <= imem_waddr;
        last_imem_data <= imem_wdata;
      end
      if (dma_ready) begin
        if (!dma_read) $fatal(1, "DMA ready with read low");
        if (dma_rdata !== (32'hABCD0000 + transfers))
          $fatal(1, "DMA data mismatch at transfer %0d: %h", transfers, dma_rdata);
        dma_addr <= dma_addr + 32'd4;
        transfers <= transfers + 1;
        if (transfers == 7) dma_read <= 0;
      end
    end
  end

  task automatic write_wb(input logic [31:0] address, input logic [31:0] value);
    bit seen;
    @(negedge clk);
    adr = address; dat = value; sel = 4'hF; we = 1; cyc = 1; stb = 1;
    seen = 0;
    for (int k = 0; k < 15; k++) begin
      @(posedge clk); #1;
      if (ack) begin seen = 1; break; end
    end
    if (!seen) $fatal(1, "WB write timeout at %h", address);
    @(negedge clk); cyc = 0; stb = 0; we = 0; sel = 0;
    @(negedge clk);
  endtask

  task automatic read_wb(input logic [31:0] address, output logic [31:0] value);
    bit seen;
    @(negedge clk);
    adr = address; sel = 4'hF; we = 0; cyc = 1; stb = 1;
    seen = 0;
    for (int k = 0; k < 15; k++) begin
      @(posedge clk); #1;
      if (ack) begin value = rdat; seen = 1; break; end
    end
    if (!seen) $fatal(1, "WB read timeout at %h", address);
    @(negedge clk); cyc = 0; stb = 0; sel = 0;
    @(negedge clk);
  endtask

  initial begin : test_sequence
    logic [31:0] value;
    bit seen;
    repeat (4) @(negedge clk);
    rst = 0;
    write_wb(32'h0000040C, 32'hDEADBEEF); // window index 3
    repeat (2) @(negedge clk);
    if (imem_writes != 1 || last_imem_addr != 3 || last_imem_data != 32'hDEADBEEF)
      $fatal(1,"IMEM write failed count=%0d addr=%0d data=%h",imem_writes,last_imem_addr,last_imem_data);
    read_wb(32'h00000004, value);
    if (value !== pc) $fatal(1,"PC readback failed: %h",value);
    write_wb(32'h00000000, 32'h00000002);
    if (run || !rst_n) $fatal(1,"Halt/reset control failed");
    write_wb(32'h00000000, 32'h00000003);
    if (!run || !rst_n) $fatal(1,"Run control failed");
    @(negedge clk);
    dma_read = 1;
    for (int i=0; i<8; i++) begin
      seen = 0;
      for (int t=0; t<30; t++) begin
        @(negedge clk);
        if (status[4]) begin seen=1; break; end
      end
      if (!seen) $fatal(1,"DMA request %0d not captured",i);
      if (addr_capture !== (32'h40001000 + 32'(4*i)))
        $fatal(1,"DMA address %0d mismatch got=%h",i,addr_capture);
      write_wb(32'h00000014, 32'hABCD0000 + 32'(i));
      write_wb(32'h00000018, 32'd1);
    end
    repeat (4) @(negedge clk);
    if (transfers != 8 || status[4])
      $fatal(1,"DMA incomplete: transferred=%0d pending=%b",transfers,status[4]);
    $display("OMEGA_DMA_8_WORDS=PASS");
    $display("OMEGA_WISHBONE_REGISTERS=PASS");
    $display("OMEGA_IMEM_PROGRAMMING=PASS");
    $finish;
  end
  initial begin #100000; $fatal(1,"Global timeout"); end
endmodule
`default_nettype wire
