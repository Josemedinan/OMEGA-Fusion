# ECO: repair_design driven by real (max) SPEF in SS corner. env: PDK ODB SDC SPEF OUT
set lib $::env(PDK)/libs.ref/sky130_fd_sc_hd
read_lef $lib/techlef/sky130_fd_sc_hd__max.tlef
read_lef $lib/lef/sky130_fd_sc_hd.lef
read_db $::env(ODB)
read_liberty $lib/lib/sky130_fd_sc_hd__ss_100C_1v60.lib
read_sdc $::env(SDC)
set_propagated_clock [all_clocks]
read_spef $::env(SPEF)
puts "slew-vio-before [sta::max_slew_violation_count]  cap-vio-before [sta::max_capacitance_violation_count] fanout-vio-before [sta::max_fanout_violation_count]"
repair_design -verbose -slew_margin $::env(SM) -cap_margin $::env(CM)
puts "slew-vio-after [sta::max_slew_violation_count]  cap-vio-after [sta::max_capacitance_violation_count] fanout-vio-after [sta::max_fanout_violation_count]"
report_cell_usage
