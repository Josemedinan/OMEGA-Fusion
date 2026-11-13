#!/usr/bin/env python3
"""Instruction-level smoke test of DEMO firmware. NOT an RTL/ISA conformance test."""
from pathlib import Path
from build_demo_rom import prog, labels
from reference import matmul

def sext(x,bits):return (x ^ (1<<(bits-1))) - (1<<(bits-1))
def run():
    regs=[0]*32;pc=0;mem={};mmio_base=0x40000000
    a=[0]*16;b=[0]*16;status=0;result=0
    iterations=0
    while iterations<500:
        iterations+=1
        assert pc%4==0 and 0<=pc//4<len(prog),f'PC invalid {pc}'
        ins=prog[pc//4]
        opc=ins&127;rd=(ins>>7)&31;f3=(ins>>12)&7
        rs1=(ins>>15)&31;rs2=(ins>>20)&31
        v1=regs[rs1];v2=regs[rs2]
        nxt=pc+4;write=None
        if opc==0x37:write=ins&0xfffff000
        elif opc==0x13:
            imm=sext(ins>>20,12)
            if f3==0:write=(v1+imm)&0xffffffff
            elif f3==7:write=v1&imm
            elif f3==1:write=(v1<<(imm&31))&0xffffffff
            else:raise AssertionError('unsupported I')
        elif opc==0x33 and f3==0:write=(v1+v2)&0xffffffff
        elif opc==0x23 and f3==2:
            imm=sext(((ins>>25)<<5)|rd,12);addr=(v1+imm)&0xffffffff
            assert addr&3==0
            off=addr-mmio_base
            if 0x100<=off<0x140:a[(off-0x100)//4]=v2&255
            elif 0x200<=off<0x240:b[(off-0x200)//4]=v2&255
            elif off==0:
                result=matmul(a,b,False)[0];status=2
            elif off==0x400:
                assert v2==4 and result==4
                print(f'PASS firmware emulator: {iterations} instructions, matrix C[0,0]={v2}')
                return
            else:raise AssertionError(f'Unexpected MMIO store 0x{addr:x}')
        elif opc==0x03 and f3==2:
            imm=sext(ins>>20,12);off=(v1+imm)-mmio_base
            if off==4:write=status
            elif off==0x300:write=result&0xffffffff
            else:raise AssertionError(f'Unexpected MMIO load {off}')
        elif opc==0x63:
            imm=((ins>>31)&1)<<12|((ins>>7)&1)<<11|((ins>>25)&63)<<5|((ins>>8)&15)<<1
            imm=sext(imm,13)
            if (f3==0 and v1==v2) or (f3==4 and sext(v1,32)<sext(v2,32)):
                nxt=pc+imm
        elif opc==0x6f:
            write=pc+4
            imm=((ins>>31)&1)<<20|((ins>>12)&255)<<12|((ins>>20)&1)<<11|((ins>>21)&1023)<<1
            nxt=pc+sext(imm,21)
        else:raise AssertionError(f'unsupported instruction {ins:08x} at {pc}')
        if write is not None and rd:regs[rd]=write&0xffffffff
        regs[0]=0;pc=nxt
    raise AssertionError('Firmware did not complete')
if __name__=='__main__':run()
