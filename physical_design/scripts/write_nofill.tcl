set lib $::env(PDK)/libs.ref/sky130_fd_sc_hd
read_lef $lib/techlef/sky130_fd_sc_hd__max.tlef
read_lef $lib/lef/sky130_fd_sc_hd.lef
read_db $::env(ODB)
write_verilog $::env(OUT)/omega_fusion_soc_asic.nl.nofill.v
write_verilog -include_pwr_gnd $::env(OUT)/omega_fusion_soc_asic.pnl.nofill.v
