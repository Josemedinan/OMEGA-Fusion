# Industrial and academic applications of OMEGA-Fusion

Every claim below is classified as **Demonstrated** (backed by a report, log or measurement in this repository), **Possible next** (technically plausible, not done) or **Needs validation** (cannot be asserted from current evidence). There are no performance, power-efficiency or commercial claims: no throughput, energy-per-operation or silicon measurement exists for this design.

What the project actually is: a small single-cycle RV32I-**subset** controller (10 instructions, no CSR/traps/interrupts/pipeline), a 256×32 flip-flop instruction RAM, and a 4×4 INT8/INT4 matrix engine with MMIO and an 8-word DMA loader, implemented as a 1800×1800 µm SKY130A macro. Verified: RTL and zero-delay gate-level simulation, DRC/LVS/antenna/9-corner STA of the V7 macro. Not verified: wrapper-level signoff, formal equivalence, SDF simulation, shuttle pre-check, silicon. `TAPEOUT_READY = NO`.

## 1. Education and research in RISC-V architecture
* **Demonstrated:** a complete, readable path from SystemVerilog (`rtl/`) through simulation (`scripts/run_all.sh`) to a routed GDS, with every failure and fix documented (`docs/results/V7_ECO_REPORT.md`, `docs/physical_design/PHYSICAL_DESIGN_REPORT.md`). The CPU is small enough to read in one sitting (`rtl/cpu/omega_rv32_controller.sv`, 85 lines).
* **Possible next:** extend the subset toward RV32I (shifts, logic ops, SLT, byte/half accesses), add CSR/trap support, a pipeline with hazard handling; use the existing testbench and flow as a regression base.
* **Needs validation:** any statement of ISA compliance (no RISC-V compliance suite has been run; the core is explicitly not compliant), software toolchain support beyond the in-repo mini-assembler.

## 2. Open hardware development
* **Demonstrated:** open tools only (LibreLane/OpenROAD/Yosys/Magic/KLayout/Netgen, SKY130A PDK); configs, SDC (v2→v4), flow and ECO scripts, per-iteration evidence and SHA-256 manifests are in the repository; both the V6 baseline and the V7 candidate are kept side by side.
* **Possible next:** CI for the physical flow on a large runner; publishing the physical release as GitHub Release assets; a `make`-style wrapper around the LibreLane stages.
* **Needs validation:** end-to-end reproduction from a clean checkout (only the RTL regression and the gate-level simulation were re-run from the repository layout; the physical flow was not re-run from it).

## 3. Embedded-system prototyping
* **Demonstrated:** program loading through IMEM pins, CPU execution of an MMIO program that drives the accelerator (C[0,0]=4, IRQ=1) in RTL and gate level; a Wishbone bridge with an 8-word DMA handshake simulated end to end (`tb/regression/`).
* **Possible next:** FPGA prototype of the same RTL for software bring-up (not attempted); replacing the flip-flop IMEM with an SRAM macro; a real DMA master.
* **Needs validation:** wrapper integration beyond the PDN stage with the V7 macro (only PDN connectivity was run), clocking at the Caravel `wb_clk` frequency, any silicon behavior, power on a board.

## 4. PPA optimization research
* **Demonstrated:** a measured post-route closure methodology (V6 → V7): hold +0.017 → +0.102 ns, slew violations 158 → 0, capacitance 23 → 0, fanout 83 → 1 net, area +0.3 %, with the iteration table (`charts/18_eco_iterations_v6_to_v7.png`, `charts/data/v7_iterations.csv`). Findings of general interest: STA counts antenna diodes as fanout; diodes must follow their sinks when nets are split; ECO-time estimates are optimistic without SPEF for new nets.
* **Possible next:** physical comparison of the folded (16-multiplier) and parallel (64-multiplier) MAC variants under identical constraints (both exist in RTL; only the folded one went through the physical flow); utilization/area studies (the die is 28 % utilized); CTS clustering experiments.
* **Needs validation:** any statement that the folded MAC saves area or energy (not measured); power numbers (only an OpenROAD estimate at default activity exists).

## 5. Acceleration of specialized workloads
* **Demonstrated:** functional correctness of a 4×4 signed INT8/INT4 matrix product with 32-bit accumulation, against a Python oracle (4,000 random tiles) and in RTL directed tests (8 cases, host and DMA paths).
* **Possible next:** larger tiles, accumulation across tiles, sparse or mixed-precision variants, a tighter CPU–accelerator interface.
* **Needs validation:** throughput, latency in a real system, energy per operation, comparison against software on the same CPU or against other accelerators — none of these have been measured. At 10 MHz with a 4-cycle folded MAC the absolute performance is modest by construction.

## 6. ASIC design talent development
* **Demonstrated:** a documented example that includes real obstacles: under-constrained SDC, stale tool metrics, antenna and hold closure, memory/disk limits of an 8 GB laptop, a tool crash and its workaround. `docs/methodology/` and `docs/results/` can serve as case studies.
* **Possible next:** exercises derived from the iteration table (e.g. "why did hold break at iteration V7 r1?"), lab handouts, a guided reproduction.
* **Needs validation:** effectiveness as teaching material (no course or user feedback exists).

## 7. Reproducible and accessible EDA flows
* **Demonstrated:** the complete flow ran on a consumer laptop (8 GB) with open tools, one job at a time, resumable per stage; honest resource notes are in `docs/methodology/reproduction.md`.
* **Possible next:** ≥ 16 GB reference configuration, containerized end-to-end script, cached run artifacts as release assets.
* **Needs validation:** the same flow on other hosts/architectures, determinism of results across runs and machines (not tested).

## What would be needed before any industrial use
Full-SoC integration signoff (wrapper DRC/LVS/antenna/STA), formal equivalence, SDF simulation, shuttle pre-check, a fixed licensing position, and silicon evidence. Until then the design is a research/teaching artefact.
