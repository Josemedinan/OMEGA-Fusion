`timescale 1ns/1ps
`default_nettype none
module tb_omega_caravel_soc;
  logic clk = 0;
  always #5 clk = ~clk;
  logic rst = 1;
  logic cyc = 0, stb = 0, we = 0;
  logic [3:0] sel = 0;
  logic [31:0] adr = 0, dat = 0;
  wire ack;
  wire [31:0] rdat;
  wire [127:0] la_data_out;
  wire [37:0] io_out, io_oeb;
  wire [2:0] user_irq;
  logic [31:0] rom [0:255];

  user_project_wrapper dut (
    .wb_clk_i(clk), .wb_rst_i(rst),
    .wbs_cyc_i(cyc), .wbs_stb_i(stb), .wbs_we_i(we),
    .wbs_sel_i(sel), .wbs_adr_i(adr), .wbs_dat_i(dat),
    .wbs_ack_o(ack), .wbs_dat_o(rdat),
    .la_data_in(128'd0), .la_data_out(la_data_out), .la_oenb(128'hFFFF_FFFF_FFFF_FFFF_FFFF_FFFF_FFFF_FFFF),
    .io_in(38'd0), .io_out(io_out), .io_oeb(io_oeb),
    .user_clock2(clk), .user_irq(user_irq)
  );

  task automatic write_wb(input logic [31:0] address, input logic [31:0] value);
    bit seen;
    @(negedge clk);
    adr=address; dat=value; sel=4'hF; we=1; cyc=1; stb=1;
    seen=0;
    for (int k=0; k<15; k++) begin
      @(posedge clk); #1;
      if (ack) begin seen=1; break; end
    end
    if (!seen) $fatal(1,"Wishbone write timeout: %h",address);
    @(negedge clk); cyc=0; stb=0; we=0; sel=0;
    @(negedge clk);
  endtask

  task automatic read_wb(input logic [31:0] address, output logic [31:0] value);
    bit seen;
    @(negedge clk);
    adr=address; sel=4'hF; we=0; cyc=1; stb=1;
    seen=0;
    for(int k=0;k<15;k++) begin
      @(posedge clk); #1;
      if (ack) begin value=rdat; seen=1; break; end
    end
    if (!seen) $fatal(1,"Wishbone read timeout: %h",address);
    @(negedge clk); cyc=0; stb=0; sel=0;
    @(negedge clk);
  endtask

  initial begin : test_sequence
    logic [31:0] read_value;
    bit success;
    for (int i=0;i<256;i++) rom[i]=32'h00000013;
    $readmemh("firmware/rom/omega_demo.hex",rom);
    repeat(4) @(negedge clk);
    rst=0;
    for (int i=0;i<256;i++) write_wb(32'h400 + 32'(4*i),rom[i]);
    repeat(3) @(negedge clk);
    write_wb(32'h000,32'h2); // Release CPU reset, but remain halted
    repeat(3) @(negedge clk);
    read_wb(32'h004,read_value);
    if(read_value !== 32'd0) $fatal(1,"CPU PC moved while halted: %h",read_value);
    write_wb(32'h000,32'h3); // Run
    success=0;
    for (int j=0;j<1200;j++) begin
      @(negedge clk);
      if (la_data_out[0]) $fatal(1,"CPU illegal instruction, PC=%h",la_data_out[95:64]);
      if (la_data_out[1] && user_irq[0]) begin
        if (la_data_out[63:32] !== 32'd4)
          $fatal(1,"Wrong MAC result: %h",la_data_out[63:32]);
        success=1;
        break;
      end
    end
    if (!success) $fatal(1,"CPU/MAC demo did not complete");
    read_wb(32'h008,read_value);
    if (read_value !== 32'd4) $fatal(1,"Wishbone result readback wrong: %h",read_value);
    read_wb(32'h00c,read_value);
    if (!read_value[1] || !read_value[2] || read_value[0])
      $fatal(1,"Wishbone status wrong: %h",read_value);
    $display("OMEGA_CARAVEL_CPU_MAC=PASS");
    $display("OMEGA_CARAVEL_RESULT=4");
    $display("OMEGA_CARAVEL_IRQ=PASS");
    $finish;
  end
  initial begin #250000; $fatal(1,"Global timeout"); end
endmodule
`default_nettype wire
