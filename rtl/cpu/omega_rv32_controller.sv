`timescale 1ns/1ps
`default_nettype none
// Educational, single-cycle RV32I SUBSET controller for the SoC smoke test.
// Implements LUI, ADD, ADDI, SLLI, ANDI, LW, SW, BEQ, BLT, JAL.
// NO interrupts, exceptions, CSRs, pipeline, memory arbitration or full RV32I compliance.
module omega_rv32_controller (
    input wire clk,
    input wire rst_n,
    input wire enable,
    input wire [31:0] instruction,
    output logic [31:0] pc,
    output logic mem_valid,
    output logic mem_write,
    output logic [31:0] mem_addr,
    output logic [31:0] mem_wdata,
    input wire [31:0] mem_rdata,
    output logic illegal
);
    logic [31:0] regs[0:31];
    wire [6:0] opcode=instruction[6:0];
    wire [4:0] rd=instruction[11:7],rs1=instruction[19:15],rs2=instruction[24:20];
    wire [2:0] funct3=instruction[14:12];
    wire [6:0] funct7=instruction[31:25];
    wire signed [31:0] imm_i={{20{instruction[31]}},instruction[31:20]};
    wire signed [31:0] imm_s={{20{instruction[31]}},instruction[31:25],instruction[11:7]};
    wire signed [31:0] imm_b={{19{instruction[31]}},instruction[31],instruction[7],instruction[30:25],instruction[11:8],1'b0};
    wire signed [31:0] imm_j={{11{instruction[31]}},instruction[31],instruction[19:12],instruction[20],instruction[30:21],1'b0};
    wire [31:0] a=(rs1==0)?32'd0:regs[rs1];
    wire [31:0] b=(rs2==0)?32'd0:regs[rs2];
    logic wr_rd;
    logic [31:0] next_pc,rd_data;
    always_comb begin
        mem_valid=1'b0;mem_write=1'b0;mem_addr=32'd0;mem_wdata=b;
        next_pc=pc+32'd4;wr_rd=1'b0;rd_data=32'd0;
        illegal=1'b0;
        case(opcode)
            7'b0110111:begin wr_rd=1;rd_data={instruction[31:12],12'd0};end
            7'b0010011:begin
                wr_rd=1;
                case(funct3)
                    3'b000:rd_data=a+imm_i;
                    3'b111:rd_data=a&imm_i;
                    3'b001:if(funct7==7'd0)rd_data=a<<instruction[24:20];else illegal=1;
                    default:illegal=1;
                endcase
            end
            7'b0110011:begin
                wr_rd=1;
                if(funct3==0 && funct7==0)rd_data=a+b;
                else illegal=1;
            end
            7'b0000011:begin
                if(funct3==3'b010)begin
                    mem_valid=1;mem_addr=a+imm_i;
                    wr_rd=1;rd_data=mem_rdata;
                end else illegal=1;
            end
            7'b0100011:begin
                if(funct3==3'b010)begin
                    mem_valid=1;mem_write=1;mem_addr=a+imm_s;
                end else illegal=1;
            end
            7'b1100011:begin
                case(funct3)
                    3'b000:if(a==b)next_pc=pc+imm_b;
                    3'b100:if($signed(a)<$signed(b))next_pc=pc+imm_b;
                    default:illegal=1;
                endcase
            end
            7'b1101111:begin wr_rd=1;rd_data=pc+4;next_pc=pc+imm_j;end
            default:illegal=1;
        endcase
        if(mem_valid && mem_addr[1:0]!=2'b00)illegal=1;
    end
    always_ff @(posedge clk or negedge rst_n)begin
        if(!rst_n)begin
            pc<=32'd0;
            for(integer i=0;i<32;i=i+1)regs[i]<=0;
        end else if(enable && !illegal)begin
            pc<=next_pc;
            if(wr_rd && rd!=0)regs[rd]<=rd_data;
        end
    end
endmodule
`default_nettype wire
