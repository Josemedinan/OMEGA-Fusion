`timescale 1ns/1ps
`default_nettype none
// One 4x4 output tile: C[r,c] = sum(k=0..3) A[r,k]*B[k,c].
// INT4 mode sign-extends the LOW nibble of each byte; INT8 uses entire byte.
// All 16 output lanes are calculated concurrently and registered on start.
module omega_fusion_mac #(
    parameter int N = 4,
    parameter int ACC_W = 32
) (
    input  wire                      clk,
    input  wire                      rst_n,
    input  wire                      start,
    input  wire                      mode_int4,
    input  wire [N*N*8-1:0]          a_flat,
    input  wire [N*N*8-1:0]          b_flat,
    output logic                     done,
    output logic [N*N*ACC_W-1:0]    c_flat
);
    function automatic signed [7:0] unpack_value(input logic [7:0] x, input logic int4);
        if (int4) unpack_value = {{4{x[3]}},x[3:0]};
        else unpack_value = $signed(x);
    endfunction

    logic signed [ACC_W-1:0] sum [0:N*N-1];
    logic signed [7:0] av, bv;
    integer r, c, k;
    always_comb begin
        for (integer i=0; i<N*N; i=i+1) sum[i]='0;
        for (r=0; r<N; r=r+1) begin
            for (c=0; c<N; c=c+1) begin
                for (k=0; k<N; k=k+1) begin
                    av=unpack_value(a_flat[8*(r*N+k)+:8],mode_int4);
                    bv=unpack_value(b_flat[8*(k*N+c)+:8],mode_int4);
                    sum[r*N+c]=sum[r*N+c]+(av*bv);
                end
            end
        end
        av='0;
        bv='0;
    end
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            done<=1'b0;
            c_flat<='0;
        end else begin
            done<=start;
            if (start) begin
                for (integer j=0; j<N*N; j=j+1)
                    c_flat[j*ACC_W+:ACC_W]<=sum[j];
            end
        end
    end
endmodule
`default_nettype wire
