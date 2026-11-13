# Gate-level testbench

The gate-level simulation re-uses `tb/regression/tb_omega_fusion_soc_asic.sv` against the post-route netlist:

```bash
PDK_ROOT=$HOME/.ciel bash scripts/run_gate_level_sim.sh
```

It is a **zero-delay functional** simulation (`-DFUNCTIONAL -DUNIT_DELAY='#0'`) with the sky130_fd_sc_hd functional models. It is not an SDF back-annotated simulation (not run).
Result of the last run: `verification/gate_level_sim.log` (PASS).
