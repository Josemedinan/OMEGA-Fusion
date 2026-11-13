// OMEGA-Fusion Wishbone register adapter for Caravel (integration candidate).
// Classic Wishbone: one registered acknowledgement; only aligned, full-word writes.
// The OMEGA core is clocked by wb_clk_i, which must respect its actual STA limit.
`default_nettype none
module omega_wb_bridge (
    input  wire        wb_clk_i,
    input  wire        wb_rst_i,
    input  wire        wbs_cyc_i,
    input  wire        wbs_stb_i,
    input  wire        wbs_we_i,
    input  wire [3:0]  wbs_sel_i,
    input  wire [31:0] wbs_adr_i,
    input  wire [31:0] wbs_dat_i,
    output reg         wbs_ack_o,
    output reg  [31:0] wbs_dat_o,

    output reg         omega_run,
    output reg         omega_rst_n,
    output reg         omega_imem_we,
    output reg  [7:0]  omega_imem_waddr,
    output reg  [31:0] omega_imem_wdata,
    input  wire [31:0] omega_pc,
    input  wire        omega_cpu_illegal,
    input  wire [31:0] omega_result,
    input  wire        omega_result_valid,
    input  wire        omega_irq,
    input  wire        omega_dma_read,
    input  wire [31:0] omega_dma_addr,
    output reg         omega_dma_ready,
    output reg  [31:0] omega_dma_rdata,
    output wire [31:0] omega_status,
    output wire [31:0] omega_dma_addr_capture
);
    reg        dma_pending;
    // After dma_ready is pulsed, wait for the core to advance dma_addr.
    // The OMEGA DMA engine keeps dma_read HIGH across all eight words.
    reg        dma_service_holdoff;
    reg [31:0] dma_addr_latched;

    assign omega_status = {27'd0, dma_pending, omega_dma_read,
                           omega_irq, omega_result_valid, omega_cpu_illegal};
    assign omega_dma_addr_capture = dma_addr_latched;

    wire bus_request = wbs_cyc_i && wbs_stb_i && !wbs_ack_o;
    wire word_write = wbs_we_i && (wbs_sel_i == 4'hf) &&
                      (wbs_adr_i[1:0] == 2'b00);
    wire imem_window = (wbs_adr_i[11:10] == 2'b01);

    always @(posedge wb_clk_i) begin
        if (wb_rst_i) begin
            wbs_ack_o          <= 1'b0;
            wbs_dat_o          <= 32'd0;
            omega_run          <= 1'b0;
            omega_rst_n        <= 1'b0;
            omega_imem_we      <= 1'b0;
            omega_imem_waddr   <= 8'd0;
            omega_imem_wdata   <= 32'd0;
            omega_dma_ready    <= 1'b0;
            omega_dma_rdata    <= 32'd0;
            dma_pending        <= 1'b0;
            dma_service_holdoff <= 1'b0;
            dma_addr_latched   <= 32'd0;
        end else begin
            wbs_ack_o       <= 1'b0;
            omega_imem_we   <= 1'b0;
            omega_dma_ready <= 1'b0;
            // In the cycle following a service request, the core consumes
            // omega_dma_ready and increments dma_addr. Do not capture
            // the pre-increment address on that cycle.
            if (dma_service_holdoff)
                dma_service_holdoff <= 1'b0;

            // Latch DMA requests even when the management CPU polls slowly.
            if (omega_dma_read && !dma_pending &&
                !dma_service_holdoff && !omega_dma_ready) begin
                dma_pending      <= 1'b1;
                dma_addr_latched <= omega_dma_addr;
            end

            if (bus_request) begin
                wbs_ack_o <= 1'b1;
                // OMEGA register window is word addressed, 4-byte aligned.
                if (imem_window) begin
                    wbs_dat_o <= 32'd0; // Instruction RAM reads are not exposed.
                    if (word_write && !omega_run) begin
                        omega_imem_waddr <= wbs_adr_i[9:2];
                        omega_imem_wdata <= wbs_dat_i;
                        omega_imem_we    <= 1'b1;
                    end
                end else begin
                    case (wbs_adr_i[11:0])
                        12'h000: begin
                            wbs_dat_o <= {30'd0, omega_rst_n, omega_run};
                            if (word_write) begin
                                omega_run   <= wbs_dat_i[0];
                                omega_rst_n <= wbs_dat_i[1];
                            end
                        end
                        12'h004: wbs_dat_o <= omega_pc;
                        12'h008: wbs_dat_o <= omega_result;
                        12'h00c: wbs_dat_o <= omega_status;
                        12'h010: wbs_dat_o <= dma_addr_latched;
                        12'h014: begin
                            wbs_dat_o <= omega_dma_rdata;
                            if (word_write) omega_dma_rdata <= wbs_dat_i;
                        end
                        12'h018: begin
                            wbs_dat_o <= {31'd0, dma_pending};
                            if (word_write && wbs_dat_i[0] && dma_pending) begin
                                omega_dma_ready    <= 1'b1;
                                dma_pending        <= 1'b0;
                                dma_service_holdoff <= 1'b1;
                            end
                        end
                        default: wbs_dat_o <= 32'd0;
                    endcase
                end
            end
        end
    end
endmodule
`default_nettype wire
