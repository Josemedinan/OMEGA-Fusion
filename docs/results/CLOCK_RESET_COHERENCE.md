# Clock and reset coherence: Caravel `wb_clk_i` (25 ns constraint) vs OMEGA-Fusion (100 ns macro signoff)

Date 2026-11-13. Evidence in `../wrapper/runs/W7_B/01-openroad-stapostpnr/`, `../clock_study/out/`.

## Architecture facts (from `caravel/rtl/user_project_wrapper.v` and `omega_wb_bridge.v`)
* The macro `mprj` is clocked **directly by `wb_clk_i`**: `.clk(wb_clk_i)`. No divider, no generated clock, no second clock domain. `user_clock2` is unused.
* Bridge and macro are therefore **one synchronous domain**. There is no clock-domain crossing. `omega_rst_n`, `omega_run`, `imem_*`, `dma_*` are flops of the bridge (same clock) feeding the macro.
* `omega_rst_n` is a registered output (glitch-free). It asserts with `wb_rst_i` (synchronously sampled) and is released only by firmware (write to reg 0x000 bit 1). The macro uses it as an asynchronous reset (recovery/removal checks apply).
* The Caravel base SDC (Efabless) defines the clock from `CLOCK_PERIOD`; its documented default for user projects is 25 ns (40 MHz), with source latency 4.65–5.57 ns and standard I/O delays. The Caravel SDC also contains `set_multicycle_path -setup 2 -hold 1` through `wbs_cyc_i`, `wbs_stb_i`, `wbs_ack_o` (the management side gives two cycles on these handshakes; this exception comes from the Caravel template and is not an OMEGA decision).

## What the numbers say
1. **The wrapper flow ran at 25 ns** (the `pdk::sky130*` block of the config overrides `CLOCK_PERIOD` to 25; my attempt to set 100 at top level had no effect — verified in `resolved.json`). Wrapper STA at 25 ns, extracted wrapper parasitics, macro timing model per corner:
   | Corner | worst setup slack [ns] | min clock period reg→reg [ns] |
   |---|---:|---:|
   | max_ss | **−14.06** (path `mprj/clk → mprj/cpu_illegal → la_data_out[0]`) | 34.38 (29.1 MHz) |
   | nom_ss | −12.76 | 33.11 |
   | min_ss | −11.49 | 31.90 |
   | max_tt | +3.14 | 18.29 |
   | max_ff | +9.09 | 11.98 |
   Hold ≥ +0.215 ns in all corners.
2. The cause is the macro itself: `cpu_illegal` is combinational from the instruction memory (pc → 256:1 mux → decode), 33.5 ns clock-to-output in max_ss. It was never a 40 MHz design: macro-only STA at 25 ns also fails max_ss by −20.3 ns (independent check, `clock_study/out/`).
3. Earlier statements (V6 report) that the wrapper STA had "setup ≥ +2.58 ns" were obtained with the flattened macro and are **not** consistent with these results; they must not be used.

## Conclusion
OMEGA-Fusion is **not** timing-coherent with the Caravel default 25 ns `wb_clk`: in the slow corner it needs a period of at least ~39 ns (limited by the combinational `cpu_illegal`/LA output path against the Caravel I/O constraints) and ~34.4 ns for register-to-register paths. It is coherent with a `wb_clk` period ≥ 50 ns (≤ 20 MHz), where the slow-corner slack is ≥ +10 ns (to be confirmed by the 50 ns STA run, see `ACCEPTANCE_MATRIX.md`). The 100 ns of the macro signoff is the macro's own constraint; the integrated system must be signed off at the real `wb_clk` period.
**Supported operating condition to document and enforce in firmware: `wb_clk_i` ≤ 20 MHz.** The Caravel management SoC powers up on the external clock (typically 10 MHz on evaluation boards) — firmware that enables the PLL above 20 MHz while OMEGA runs is outside the signed-off envelope. A hardware divider/clock gate was **not** added: it would be a design change (new generated clock + CDC between bridge and macro) requiring a new variant and full re-verification.
