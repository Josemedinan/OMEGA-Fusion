# Experiment: can repair_design clear SS slew/cap/fanout on routed DB? env: PDK ODB SDC OUT
set lib $::env(PDK)/libs.ref/sky130_fd_sc_hd
read_lef $lib/techlef/sky130_fd_sc_hd__nom.tlef
read_lef $lib/lef/sky130_fd_sc_hd.lef
read_db $::env(ODB)
define_corners tt ss ff
read_liberty -corner tt $lib/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
read_liberty -corner ss $lib/lib/sky130_fd_sc_hd__ss_100C_1v60.lib
read_liberty -corner ff $lib/lib/sky130_fd_sc_hd__ff_n40C_1v95.lib
read_sdc $::env(SDC)
set_max_transition 0.75 [current_design]
set_max_capacitance 0.2 [current_design]
set_max_fanout 10 [current_design]
set_propagated_clock [all_clocks]
set_wire_rc -signal -layer met2
set_wire_rc -clock -layer met5
estimate_parasitics -placement
foreach c {tt ss ff} { puts "BEFORE $c"; report_check_types -corner $c -max_slew -max_capacitance -max_fanout -violators > $::env(OUT)/before_$c.rpt }
repair_design -verbose -slew_margin 45 -cap_margin 30
estimate_parasitics -placement
foreach c {tt ss ff} { report_check_types -corner $c -max_slew -max_capacitance -max_fanout -violators > $::env(OUT)/after_$c.rpt }
report_cell_usage
