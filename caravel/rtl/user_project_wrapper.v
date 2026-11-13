// SPDX-FileCopyrightText: 2020 Efabless Corporation
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
// SPDX-License-Identifier: Apache-2.0

`default_nettype none
/*
 *-------------------------------------------------------------
 *
 * user_project_wrapper
 *
 * This wrapper enumerates all of the pins available to the
 * user for the user project.
 *
 * An example user project is provided in this wrapper.  The
 * example should be removed and replaced with the actual
 * user project.
 *
 *-------------------------------------------------------------
 */

module user_project_wrapper #(
    parameter BITS = 32
) (
`ifdef USE_POWER_PINS
    inout vdda1,	// User area 1 3.3V supply
    inout vdda2,	// User area 2 3.3V supply
    inout vssa1,	// User area 1 analog ground
    inout vssa2,	// User area 2 analog ground
    inout vccd1,	// User area 1 1.8V supply
    inout vccd2,	// User area 2 1.8v supply
    inout vssd1,	// User area 1 digital ground
    inout vssd2,	// User area 2 digital ground
`endif

    // Wishbone Slave ports (WB MI A)
    input wb_clk_i,
    input wb_rst_i,
    input wbs_stb_i,
    input wbs_cyc_i,
    input wbs_we_i,
    input [3:0] wbs_sel_i,
    input [31:0] wbs_dat_i,
    input [31:0] wbs_adr_i,
    output wbs_ack_o,
    output [31:0] wbs_dat_o,

    // Logic Analyzer Signals
    input  [127:0] la_data_in,
    output [127:0] la_data_out,
    input  [127:0] la_oenb,

    // IOs
    input  [`MPRJ_IO_PADS-1:0] io_in,
    output [`MPRJ_IO_PADS-1:0] io_out,
    output [`MPRJ_IO_PADS-1:0] io_oeb,

    // Analog (direct connection to GPIO pad---use with caution)
    // Note that analog I/O is not available on the 7 lowest-numbered
    // GPIO pads, and so the analog_io indexing is offset from the
    // GPIO indexing by 7 (also upper 2 GPIOs do not have analog_io).
    inout [`MPRJ_IO_PADS-10:0] analog_io,

    // Independent clock (on independent integer divider)
    input   user_clock2,

    // User maskable interrupt signals
    output [2:0] user_irq
);

/* OMEGA-Fusion integration candidate: management Wishbone -> hard macro. */
wire omega_run, omega_rst_n, omega_imem_we;
wire [7:0] omega_imem_waddr;
wire [31:0] omega_imem_wdata;
wire [31:0] omega_pc, omega_result, omega_dma_addr;
wire [31:0] omega_dma_rdata, omega_status, omega_dma_addr_capture;
wire omega_cpu_illegal, omega_result_valid, omega_irq, omega_dma_read, omega_dma_ready;

omega_wb_bridge u_omega_wb (
    .wb_clk_i(wb_clk_i), .wb_rst_i(wb_rst_i),
    .wbs_cyc_i(wbs_cyc_i), .wbs_stb_i(wbs_stb_i),
    .wbs_we_i(wbs_we_i), .wbs_sel_i(wbs_sel_i),
    .wbs_adr_i(wbs_adr_i), .wbs_dat_i(wbs_dat_i),
    .wbs_ack_o(wbs_ack_o), .wbs_dat_o(wbs_dat_o),
    .omega_run(omega_run), .omega_rst_n(omega_rst_n),
    .omega_imem_we(omega_imem_we), .omega_imem_waddr(omega_imem_waddr),
    .omega_imem_wdata(omega_imem_wdata), .omega_pc(omega_pc),
    .omega_cpu_illegal(omega_cpu_illegal), .omega_result(omega_result),
    .omega_result_valid(omega_result_valid), .omega_irq(omega_irq),
    .omega_dma_read(omega_dma_read), .omega_dma_addr(omega_dma_addr),
    .omega_dma_ready(omega_dma_ready), .omega_dma_rdata(omega_dma_rdata),
    .omega_status(omega_status), .omega_dma_addr_capture(omega_dma_addr_capture)
);

omega_fusion_soc_asic mprj (
`ifdef USE_POWER_PINS
    .VDD(vccd1), .VSS(vssd1),
`endif
    .clk(wb_clk_i), .rst_n(omega_rst_n), .run(omega_run),
    .imem_we(omega_imem_we), .imem_waddr(omega_imem_waddr),
    .imem_wdata(omega_imem_wdata), .pc(omega_pc),
    .cpu_illegal(omega_cpu_illegal), .result(omega_result),
    .result_valid(omega_result_valid), .irq(omega_irq),
    .dma_read(omega_dma_read), .dma_addr(omega_dma_addr),
    .dma_ready(omega_dma_ready), .dma_rdata(omega_dma_rdata)
);

assign user_irq = {2'b00, omega_irq};
assign la_data_out = {omega_dma_addr_capture, omega_pc, omega_result, omega_status};
assign io_out = {`MPRJ_IO_PADS{1'b0}};
assign io_oeb = {`MPRJ_IO_PADS{1'b1}};
// No GPIO or analog pads are driven by this integration candidate.
endmodule
`default_nettype wire
