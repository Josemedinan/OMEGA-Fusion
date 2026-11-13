# Programmable SoC ASIC integration — design contract

## Synthesis top
`omega_fusion_soc_asic` contains the RV32I-subset controller, a 256x32-bit writable
instruction memory, the folded INT4/INT8 matrix accelerator, its 32-byte operand
storage, and MMIO result registers. Unlike the prior `omega_fusion` GDSII,
this flow includes CPU and program memory within the physical layout.

**Scope limit:** the CPU executes only a subset of RV32I. It is not a complete
compliant RISC-V core, nor a replacement for the independent OMEGA-32 pipeline.
Program memory currently maps to standard-cell flop/mux logic; there is no
SRAM macro or software stack/data memory in this version. CPU instruction fetch
is combinational, while IMEM writes are synchronous. No AXI/AHB, cache, clock
or reset synchronizer, protected DMA host memory, pin ring, ESD or packaging.
This is a fully integrated *programmable demonstration SoC*, not production IP.

## Boot and host interface
1. Drive `rst_n=0`, `run=0`.
2. Fill 256 instruction words by pulsing `imem_we` (one word per rising edge),
   `imem_waddr` and `imem_wdata`; unused addresses should be NOP `0x00000013`.
3. Drive `imem_we=0`; deassert `rst_n` and hold `run=0` for several cycles.
4. Drive `run=1` synchronized to `clk`. The CPU begins executing from PC=0.
5. Observe `result_valid`, `result`, `irq`; observe `cpu_illegal` for bad opcodes.
6. Optionally connect `dma_read/dma_addr/dma_ready/dma_rdata` to a real
   external reader, otherwise tie `dma_ready=0` and `dma_rdata=0`.

Reset is asynchronous for the controller and datapath, and its release must be
synchronized externally. This input protocol is not a hardware reset controller.

## MMIO map
- `0x4000_0000`: accelerator control
- `0x4000_0004`: status
- `0x4000_0100..0x4000_013c`: operand A bytes (one byte per 32-bit word)
- `0x4000_0200..0x4000_023c`: operand B bytes
- `0x4000_0300..0x4000_033c`: result C (16 x 32-bit signed)
- `0x4000_0400`: demo result mailbox (written by firmware)

## Reproduction
RTL simulation: `bash scripts/run_soc_asic_sim.sh` (all RTL checks: `bash scripts/run_all.sh`).
Physical implementation: LibreLane 3.0.11 Classic flow, see `physical_design/README.md` and
`docs/methodology/reproduction.md`. Results of the final run (V6) are in `docs/results/SIGNOFF_REPORT.md`.
The earlier OpenROAD-Flow-Scripts (ORFS) attempt for this SoC was superseded by the LibreLane flow and is not part of this repository.

## Known architecture concerns
- Original RV32 subset assumes combinational memory reads; this is not an
  SRAM-backed production CPU interface.
- Unknown/invalid MMIO addresses return zero and the controller lacks bus
  fault/exceptions.
- CPU is not clock-gated during halt; register updates are disabled, while
  combinational logic can still switch with external signal changes.
- Recovery/removal and 9-corner post-route STA were run for the V6 layout (see `docs/results/SIGNOFF_REPORT.md`).
- The standard-cell instruction memory is area-heavy; next physical revision
  should use a real SKY130 SRAM macro and compatible memory timing.
