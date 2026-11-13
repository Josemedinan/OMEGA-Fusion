#!/usr/bin/env python3
"""Draws the block diagram of omega_fusion_soc_asic from facts present in the RTL
(rtl/soc/omega_fusion_soc_asic.sv, rtl/cpu/omega_rv32_controller.sv, rtl/accelerators/*.sv,
caravel/rtl/omega_wb_bridge.v). Output: docs/architecture/soc_block_diagram.{png,svg}.
Requires matplotlib. Every box below corresponds to a module/array that exists in the RTL."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "architecture")
fig, ax = plt.subplots(figsize=(14, 9.2))
ax.set_xlim(0, 130); ax.set_ylim(-9, 82); ax.axis("off")

def box(x, y, w, h, title, sub="", fc="#eef3fb", ec="#2b4a7a", fs=10, lw=1.4):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=1.2", fc=fc, ec=ec, lw=lw))
    ax.text(x + w / 2, y + h - 2.6, title, ha="center", va="top", fontsize=fs, fontweight="bold", color="#14233b")
    if sub:
        ax.text(x + w / 2, y + h - 6.0, sub, ha="center", va="top", fontsize=7.8, color="#33425a", linespacing=1.35)

def arrow(p, q, label="", both=False, color="#2b4a7a", ls="-", lx=0, ly=1.3):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="<|-|>" if both else "-|>", mutation_scale=11, lw=1.3, color=color, linestyle=ls))
    if label:
        ax.text((p[0] + q[0]) / 2 + lx, (p[1] + q[1]) / 2 + ly, label, ha="center", fontsize=7.4, color=color)

# Caravel side (integration candidate, not part of the macro)
box(2, 52, 24, 26, "Caravel management SoC", "RISC-V management core\n(Efabless, not part of this repo)\nWishbone master", fc="#f3f3f3", ec="#777", fs=9)
box(2, 20, 24, 26, "omega_wb_bridge", "Wishbone slave adapter\nregisters: run, rst_n, IMEM\nwindow, status, DMA service\ncaravel/rtl/omega_wb_bridge.v", fc="#fff4e0", ec="#a86a00", fs=9)
arrow((14, 52), (14, 46), "wbs_*", both=True, color="#777", lx=5)

# Macro boundary
ax.add_patch(FancyBboxPatch((33, 7), 94, 71, boxstyle="round,pad=0.3,rounding_size=1.5", fc="none", ec="#14233b", lw=2.0, linestyle="--"))
ax.text(35, 76.2, "omega_fusion_soc_asic  (hard macro 'mprj', 1800 x 1800 um, SKY130A sky130_fd_sc_hd, clk 10 MHz)", fontsize=9.2, fontweight="bold", color="#14233b", va="top")

box(37, 50, 26, 22, "IMEM  256 x 32", "flip-flop array (no SRAM macro)\nwrite port: imem_we / waddr /\nwdata, accepted only while run=0\ncombinational fetch", fc="#eaf6ea", ec="#2d6a2d")
box(37, 18, 26, 28, "omega_rv32_controller", "single-cycle RV32I SUBSET\nLUI ADD ADDI SLLI ANDI\nLW SW BEQ BLT JAL\n32 x 32 register file\nno CSR / trap / IRQ / pipeline\nillegal-instruction halt flag", fc="#eaf6ea", ec="#2d6a2d")
box(72, 54, 50, 18, "MMIO decode (in omega_fusion_soc_asic)", "0x4000_0000-0x4000_03FF -> accelerator\n0x4000_0400 -> result mailbox register (result, result_valid)\nother addresses read as 0", fc="#f6efe0", ec="#8a6d1a", fs=9)
box(72, 8, 54, 42, "omega_fusion  (MMIO accelerator)", "", fc="#e9eefb", ec="#2b4a7a")
box(75, 29, 24, 16, "Registers + FSM", "CONTROL, STATUS,\nDMA_SRC, CAPS\nIDLE/DMA/COMPUTE/WAIT_MAC\nsticky DONE/ERROR, irq", fs=8.4, fc="#ffffff")
box(75, 11, 24, 15, "Operand scratchpad", "A: 16 x 8 b   B: 16 x 8 b\n(flip-flops)\nDMA loader: 8 aligned\n32-bit reads (linear)", fs=8.4, fc="#ffffff")
box(102, 11, 22, 34, "mac_folded", "omega_fusion_mac_folded\nFOLDED=1 (used in ASIC)\n16 INT8/INT4 signed lanes\n1 multiplier per lane\n4 accumulate steps\nC: 16 x 32 b signed\n(FOLDED=0 option: 64\nmultipliers, mac.sv)", fs=8.0, fc="#ffffff")

arrow((50, 50), (50, 46), "instruction", lx=7, ly=-0.3)
arrow((63, 30), (75, 36), "load/store", lx=-1, ly=-3.2)
arrow((63, 40), (72, 60), "", color="#8a6d1a")
arrow((99, 37), (102, 37), "")
arrow((99, 18), (102, 18), "")
arrow((87, 29), (87, 26), "")

# external pins
ax.annotate("", xy=(37, 66), xytext=(26, 36), arrowprops=dict(arrowstyle="<|-|>", lw=1.2, color="#a86a00", connectionstyle="arc3,rad=-0.25"))
ax.text(29.5, 76.2, "", fontsize=7)
ax.text(30.5, 3.0, "control pins: run, rst_n, imem_we/waddr/wdata (bridge -> macro)   status pins: pc, cpu_illegal, result, result_valid, irq (macro -> bridge)", fontsize=7.2, color="#a86a00", ha="left")
ax.annotate("", xy=(72, 10), xytext=(26, 24), arrowprops=dict(arrowstyle="<|-|>", lw=1.2, color="#a86a00", connectionstyle="arc3,rad=0.25"))
ax.text(50, 4.8, "DMA pins: dma_read, dma_addr[31:0] (macro -> bridge);  dma_ready, dma_rdata[31:0] (bridge -> macro)", fontsize=7.2, color="#a86a00", ha="center")

ax.text(2, -4.0, "Not implemented (deliberately absent from this diagram): pipeline, caches, AXI/AHB, DMA controller/arbiter, CSR/interrupt handling in the CPU, SRAM macro.\n"
        "Source: rtl/ and caravel/rtl/ in this repository. 'irq' is a level output of the accelerator, not a CPU interrupt input.", fontsize=7.4, color="#444", va="top")
os.makedirs(out, exist_ok=True)
for ext in ("png", "svg"):
    fig.savefig(os.path.join(out, f"soc_block_diagram.{ext}"), dpi=170, bbox_inches="tight")
print("written", out)
