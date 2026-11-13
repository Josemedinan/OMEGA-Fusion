# env: PDK ODB SDC OUT. Electrical violators + propagated hold per corner.
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
set_max_fanout 10 [current_design]
set_propagated_clock [all_clocks]
set_wire_rc -signal -layer met2
set_wire_rc -clock -layer met5
estimate_parasitics -placement
set o $::env(OUT)
foreach c {tt ss ff} {
  report_check_types -corner $c -max_slew -max_capacitance -max_fanout -violators -digits 4 > $o/elec_$c.rpt
  report_checks -corner $c -path_delay min -group_path_count 3 -format full_clock_expanded -fields {slew cap fanout} -digits 4 > $o/hold_$c.rpt
  report_checks -corner $c -path_delay max -group_path_count 1 -format full_clock_expanded -digits 4 > $o/setup_$c.rpt
}
report_clock_skew -setup > $o/skew.rpt
