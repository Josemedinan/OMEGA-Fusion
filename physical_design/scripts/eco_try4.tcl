# Experiment: can repair_design clear SS slew/cap/fanout on routed DB? env: PDK ODB SDC OUT
set lib $::env(PDK)/libs.ref/sky130_fd_sc_hd
read_lef $lib/techlef/sky130_fd_sc_hd__nom.tlef
read_lef $lib/lef/sky130_fd_sc_hd.lef
read_db $::env(ODB)
read_liberty $lib/lib/sky130_fd_sc_hd__ss_100C_1v60.lib
read_sdc $::env(SDC)
set_max_transition 0.75 [current_design]
set_max_capacitance 0.2 [current_design]
set_max_fanout 10 [current_design]
set_propagated_clock [all_clocks]
set_wire_rc -signal -layer met2
set_wire_rc -clock -layer met5
estimate_parasitics -placement
foreach c {x} { puts "BEFORE"; report_check_types -max_slew -max_capacitance -max_fanout -violators > $::env(OUT)/before_ss.rpt }
repair_design -verbose -slew_margin 20 -cap_margin 20
estimate_parasitics -placement
foreach c {x} { report_check_types -max_slew -max_capacitance -max_fanout -violators > $::env(OUT)/after_ss.rpt }
report_cell_usage
