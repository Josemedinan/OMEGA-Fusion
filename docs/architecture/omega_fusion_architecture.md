> **Scope note.** This is the architectural contract of the `omega_fusion` accelerator (MMIO + DMA loader + MAC), written for release v0.2.
> Sentences saying that no CPU is included refer to this accelerator package only: the repository now also contains the RV32I-subset controller
> (`rtl/cpu/`) and the SoC top (`rtl/soc/omega_fusion_soc_asic.sv`), documented in `asic_soc_integration.md`.
> "Not measured" statements below predate the physical flow; measured results live in `docs/results/`.

# OMEGA-Fusion architectural contract

## Scope

This is a 4x4 tile matrix accelerator intended as a memory-mapped peripheral for a RISC-V SoC. The CPU itself is **not** included in this package. The accelerator executes one signed 4x4 matrix multiplication per command. 16 output dot products run concurrently; each dot product contains four multiplications. The products are implemented as combinational logic feeding registers; this is **not** a pipelined systolic mesh.

## Numeric formats

* INT8: 8-bit signed two's complement A and B elements.
* INT4: only the low nibble of each input byte is significant; sign extended from bit 3. Values range from -8 through +7.
* Each output C[r,c] = sum(A[r,k]*B[k,c], k=0..3) is 32-bit signed, no quantization or saturation. These shapes cannot overflow 32 bits.
* A, B, and C are row-major.

## Host interface

Single-cycle, 32-bit word MMIO interface, aligned accesses only, `bus_ready=bus_valid` (no backpressure). The host must hold its access stable until the active clock edge. Reads are combinational. Operations take multiple internal cycles; software polls status or uses the IRQ level. Writes during busy to operand windows are rejected and raise error. It is a register interface, **not** AXI or AHB.

| Offset | Mode | Definition |
|---|---|---|
| `0x000` | WO/RW | CONTROL: bit0 start, bit1 INT4 select, bit2 DMA+start, bit3 clear DONE/ERROR/IRQ |
| `0x004` | RO | STATUS: bit0 busy, bit1 done sticky, bit2 error sticky, bit3 IRQ |
| `0x008` | RW | DMA_SRC: byte address, 4-byte aligned |
| `0x00C` | RO | CAPS: ACC_W / N / version / features |
| `0x100..0x13C` | RW | A[0:15], low 8 bits only |
| `0x200..0x23C` | RW | B[0:15], low 8 bits only |
| `0x300..0x33C` | RO | C[0:15], full signed 32-bit result |

## DMA read interface

The DMA is a **read-only linear loader**, not a full system DMA controller. It makes eight sequential, aligned reads to `dma_addr`; transfer completes on a cycle when `dma_read && dma_ready` and `dma_rdata` is valid. Bytes are little-endian within each word. First four words load A, next four load B. It does not implement AXI, arbitration, cache coherence, or address translation. The parent SoC is responsible for bus integration, valid addresses, access permissions, and memory latency. `dma_read` remains asserted while stalled. Changes to the external read data without `dma_ready` are ignored.

## Timing and safety

`clk` is rising-edge active, `rst_n` is asynchronous active-low. Reset assertion clears all state and operand storage. Release must be synchronized by the parent SoC. `irq` stays high on completion until the next command or explicit clear. Output data is stable after completion until a new calculation finishes. Neither PPA nor physical signoff is claimed before tool execution.

## Design decisions and tradeoffs

The fully unrolled 4x4 combinational MAC makes early functionality and a simple one-shot programming model easy to demonstrate; area and critical path may be high on SKY130. The implementation intentionally uses neither an SRAM macro nor hardware clock gating. Scratchpad registers are not area-efficient and should be replaced by SRAM/compiled memories for a more capable system. A true systolic array with operand reuse and pipelining is a future architectural alternative, not a property of this version.

## Dual architecture and integration demo (v0.2)

`omega_fusion` has a parameter `FOLDED` (default 1). With `FOLDED=0`, `omega_fusion_mac.sv` computes the four partial products for each of 16 output lanes in combinational logic. With `FOLDED=1`, `omega_fusion_mac_folded.sv` copies operands on `start`, performs one signed multiplication per output lane on each of four subsequent clock edges, accumulates each output into a 32-bit result register, and pulses `done` on the final step. The host controller remains busy until the MAC completion pulse has been sampled. The protocol is unchanged across architectures.

`rtl/soc/omega_rv32_controller.sv` is a small **RV32I instruction subset**, not a substitute for a complete CPU. The demonstration implements LUI, ADD/ADDI, SLLI, ANDI, LW, SW, BEQ, BLT and JAL, and has no machine-mode support, exceptions, interrupt handling, alignment traps, instruction/data memory arbitration or pipeline. Its ROM is provided by the *simulation testbench*. The SoC demonstration tests MMIO integration only; the standalone accelerator remains the ASIC physical top. Actual OMEGA-32 sources must be provided and integrated separately.

The ROM at `firmware/rom/omega_demo.hex` is generated from `scripts/build_demo_rom.py`. Its behavior is to write 16 ones to A and B, start a tile, poll the completion flag, read output zero, and write expected result 4 to a monitoring register outside the accelerator's MMIO aperture. This is a firmware-driven integration smoke test rather than complete ISA or hardware verification.

The 16-lane folded datapath reduces the number of multiplier operators by four compared with the combinational baseline, but should not be claimed to reduce area, energy or latency without matching synthesized and physical measurements. It currently uses flip-flop arrays rather than a true SRAM scratchpad, and its DMA is limited to eight read handshakes, not a full memory subsystem.
