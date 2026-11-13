# V7 ECO pass 4: renumber antenna diodes contiguously. After eco_v7c deleted diodes, the numbering of the remaining
# ANTENNA_<n> instances has gaps; OpenROAD's repair_antennas names new diodes from a counter and then dereferences
# the (null) result when that name already exists -> SIGSEGV in grt::RepairAntennas::setDiodeLoc (observed twice).
# env: ODB OUT
set lib $::env(PDK)/libs.ref/sky130_fd_sc_hd
read_lef $lib/techlef/sky130_fd_sc_hd__max.tlef
read_lef $lib/lef/sky130_fd_sc_hd.lef
read_db $::env(ODB)
set block [ord::get_db_block]
set dio {}
foreach i [$block getInsts] { if {[string match ANTENNA_* [$i getName]]} { lappend dio $i } }
puts "DIODES [llength $dio]"
set k 0
foreach i $dio { $i rename TMPDIODE_$k; incr k }
set k 0
foreach i $dio { $i rename ANTENNA_$k; incr k }
puts "RENUMBERED $k (ANTENNA_0..ANTENNA_[expr {$k-1}])"
write_db $::env(OUT)/omega_fusion_soc_asic.odb
write_def $::env(OUT)/omega_fusion_soc_asic.def
write_verilog $::env(OUT)/omega_fusion_soc_asic.nl.v
write_verilog -include_pwr_gnd $::env(OUT)/omega_fusion_soc_asic.pnl.v
puts "ECO_V7D_DONE"
