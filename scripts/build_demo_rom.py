#!/usr/bin/env python3
"""Deterministically assemble RV32I-subset firmware without external cross toolchain."""
from pathlib import Path
import argparse

def check(x, width):
    if not (-(1<<(width-1)) <= x < (1<<(width-1))):
        raise ValueError((x,width))

def i(op, rd, f3, rs1, imm):
    check(imm,12)
    return ((imm&4095)<<20)|(rs1<<15)|(f3<<12)|(rd<<7)|op

def r(rd,rs1,rs2,f3=0):return (rs2<<20)|(rs1<<15)|(f3<<12)|(rd<<7)|0x33

def encode_sw(rs2,rs1,imm):
    check(imm,12);v=imm&4095
    return ((v>>5)<<25)|(rs2<<20)|(rs1<<15)|(2<<12)|((v&31)<<7)|0x23

def sw(rs2,rs1,imm):emit(encode_sw(rs2,rs1,imm))

def branch(rs1,rs2,dist,f3):
    check(dist,13)
    assert not dist&1
    v=dist&8191
    return (((v>>12)&1)<<31)|(((v>>5)&63)<<25)|(rs2<<20)|(rs1<<15)|(f3<<12)|(((v>>1)&15)<<8)|(((v>>11)&1)<<7)|0x63

def jal(rd,dist):
    check(dist,21)
    assert not dist&1
    v=dist&((1<<21)-1)
    return (((v>>20)&1)<<31)|(((v>>1)&1023)<<21)|(((v>>11)&1)<<20)|(((v>>12)&255)<<12)|(rd<<7)|0x6f

prog=[];labels={};patch=[]
def emit(v):prog.append(v)
def label(x):labels[x]=len(prog)
def addi(rd,rs1,imm):emit(i(0x13,rd,0,rs1,imm))
def lw(rd,rs1,imm):emit(i(0x03,rd,2,rs1,imm))
def andi(rd,rs1,imm):emit(i(0x13,rd,7,rs1,imm))
def slli(rd,rs1,sh):emit(i(0x13,rd,1,rs1,sh))
def blt(rs1,rs2,dest):patch.append((len(prog),"blt",rs1,rs2,dest));emit(0)
def beq(rs1,rs2,dest):patch.append((len(prog),"beq",rs1,rs2,dest));emit(0)
def jump(dest):patch.append((len(prog),"jal",0,0,dest));emit(0)
# Fill A and B with 1; software starts INT8 4x4 multiply; C[0,0] == 4.
emit((0x40000<<12)|(1<<7)|0x37) # x1 = MMIO base 0x40000000
addi(2,0,1);addi(3,0,16);addi(4,0,0)
addi(6,1,0x100);addi(7,1,0x200)
label("fill")
slli(5,4,2)
emit(r(10,6,5));sw(2,10,0)
emit(r(11,7,5));sw(2,11,0)
addi(4,4,1);blt(4,3,"fill")
sw(2,1,0)
label("poll")
lw(8,1,4);andi(8,8,2);beq(8,0,"poll")
lw(9,1,0x300);sw(9,1,0x400)
label("stop");jump("stop")
for pos,typ,rs1,rs2,dest in patch:
    d=(labels[dest]-pos)*4
    prog[pos]=branch(rs1,rs2,d,4 if typ=="blt" else 0) if typ!="jal" else jal(0,d)
parser=argparse.ArgumentParser();parser.add_argument('--out',default='firmware/rom/omega_demo.hex')
args=parser.parse_args();p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True)
p.write_text(''.join(f'{v:08x}\n' for v in prog))
print(f'Generated {len(prog)} RV32I-subset instructions -> {p}')
