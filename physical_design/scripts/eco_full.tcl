# ECO on a routed ODB using REAL SPEF (SS/max for slew,cap,fanout and hold; FF/min for hold).
# env: PDK ODB RCX(dir with max/min spef) SDC OUT(dir) SM CM HM
set lib $::env(PDK)/libs.ref/sky130_fd_sc_hd
read_lef $lib/techlef/sky130_fd_sc_hd__max.tlef
read_lef $lib/lef/sky130_fd_sc_hd.lef
read_db $::env(ODB)
define_corners ss ff
read_liberty -corner ss $lib/lib/sky130_fd_sc_hd__ss_100C_1v60.lib
read_liberty -corner ff $lib/lib/sky130_fd_sc_hd__ff_n40C_1v95.lib
read_sdc $::env(SDC)
set_propagated_clock [all_clocks]
read_spef -corner ss $::env(RCX)/max/omega_fusion_soc_asic.max.spef
read_spef -corner ff $::env(RCX)/min/omega_fusion_soc_asic.min.spef
proc vio {tag} {
  puts "VIO $tag slew=[sta::max_slew_violation_count] cap=[sta::max_capacitance_violation_count] fanout=[sta::max_fanout_violation_count]"
  puts "VIO $tag hold_ws_ss=[sta::worst_slack_cmd min]"
}
vio before
for {set i 0} {$i < 2} {incr i} {
  repair_design -verbose -slew_margin $::env(SM) -cap_margin $::env(CM)
  vio after_repair_design_$i
}
repair_timing -hold -hold_margin $::env(HM) -setup_margin 0.0 -max_buffer_percent 30 -verbose
vio after_hold
detailed_placement -max_displacement {500 100}
check_placement -verbose
# strip signal routing so GRT/DRT re-route consistently with the new netlist
set block [ord::get_db_block]
foreach net [$block getNets] {
  if {[$net getSigType] eq "SIGNAL" || [$net getSigType] eq "CLOCK"} {
    set w [$net getWire]
    if {$w ne "NULL"} { odb::dbWire_destroy $w }
  }
}
report_cell_usage
write_db $::env(OUT)/omega_fusion_soc_asic.odb
write_def $::env(OUT)/omega_fusion_soc_asic.def
write_verilog $::env(OUT)/omega_fusion_soc_asic.nl.v
write_verilog -include_pwr_gnd $::env(OUT)/omega_fusion_soc_asic.pnl.v
