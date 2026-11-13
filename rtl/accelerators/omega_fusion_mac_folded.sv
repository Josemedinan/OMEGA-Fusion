`timescale 1ns/1ps
`default_nettype none
// Four sequential dot-product steps, 16 independent output lanes.
// 16 multipliers rather than 64. Result latency: 4 active cycles.
module omega_fusion_mac_folded #(
    parameter int N=4,
    parameter int ACC_W=32
)(
    input wire clk,
    input wire rst_n,
    input wire start,
    input wire mode_int4,
    input wire [N*N*8-1:0] a_flat,
    input wire [N*N*8-1:0] b_flat,
    output logic done,
    output logic [N*N*ACC_W-1:0] c_flat
);
    localparam int STEP_W=(N>1)?$clog2(N):1;
    logic running;
    logic [STEP_W-1:0] step;
    // Inputs are copied on start so host changes cannot affect in-flight math.
    logic [N*N*8-1:0] a_q,b_q;
    logic int4_q;
    function automatic signed [7:0] val(input logic [7:0] x,input logic int4);
        if (int4) val={{4{x[3]}},x[3:0]};
        else val=$signed(x);
    endfunction
    logic signed [ACC_W-1:0] term [0:N*N-1];
    always_comb begin
        for (integer r=0;r<N;r=r+1) begin
            for (integer c=0;c<N;c=c+1) begin
                term[r*N+c] = $signed(val(a_q[8*(r*N+int'(step))+:8],int4_q)) *
                              $signed(val(b_q[8*(int'(step)*N+c)+:8],int4_q));
            end
        end
    end
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            running<=1'b0;step<='0;done<=1'b0;
            a_q<='0;b_q<='0;int4_q<=1'b0;c_flat<='0;
        end else begin
            done<=1'b0;
            if (start && !running) begin
                a_q<=a_flat;b_q<=b_flat;int4_q<=mode_int4;
                c_flat<='0;step<='0;running<=1'b1;
            end else if (running) begin
                for (integer j=0;j<N*N;j=j+1)
                    c_flat[j*ACC_W+:ACC_W]<= $signed(c_flat[j*ACC_W+:ACC_W]) + term[j];
                if(step==STEP_W'(N-1)) begin
                    running<=1'b0;done<=1'b1;
                end else step<=step+1'b1;
            end
        end
    end
endmodule
`default_nettype wire
