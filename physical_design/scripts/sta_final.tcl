# Independent post-route signoff STA for one corner. env: PDK ODB SDC SPEF LIBC(e.g. ss_100C_1v60) TLEF(nom|min|max) OUT TAG [NOLIMITS=1]
set lib $::env(PDK)/libs.ref/sky130_fd_sc_hd
read_lef $lib/techlef/sky130_fd_sc_hd__$::env(TLEF).tlef
read_lef $lib/lef/sky130_fd_sc_hd.lef
read_db $::env(ODB)
read_liberty $lib/lib/sky130_fd_sc_hd__$::env(LIBC).lib
read_sdc $::env(SDC)
if {[info exists ::env(NOLIMITS)]} { unset_case_analysis -quiet; }
set_propagated_clock [all_clocks]
read_spef $::env(SPEF)
set o $::env(OUT); set t $::env(TAG)
set f [open $o/$t.summary.txt w]
proc ws {m} { return [sta::worst_slack_cmd $m] }
puts $f "tag=$t"
puts $f "setup_ws_ns=[expr [ws max]*1e9]"
puts $f "hold_ws_ns=[expr [ws min]*1e9]"
puts $f "setup_tns=[sta::total_negative_slack_cmd max]"
puts $f "hold_tns=[sta::total_negative_slack_cmd min]"
puts $f "slew_vio=[sta::max_slew_violation_count]"
puts $f "cap_vio=[sta::max_capacitance_violation_count]"
puts $f "fanout_vio=[sta::max_fanout_violation_count]"
close $f
report_checks -path_delay min -path_group asynchronous -group_path_count 2 -format full_clock_expanded -digits 3 > $o/$t.removal.rpt
report_checks -path_delay max -path_group asynchronous -group_path_count 2 -format full_clock_expanded -digits 3 > $o/$t.recovery.rpt
report_checks -path_delay min -group_path_count 1 -format full_clock_expanded -digits 3 > $o/$t.hold_worst.rpt
report_checks -path_delay max -group_path_count 1 -format full_clock_expanded -digits 3 > $o/$t.setup_worst.rpt
report_clock_skew -setup > $o/$t.skew_setup.rpt
report_clock_skew -hold > $o/$t.skew_hold.rpt
check_setup -verbose > $o/$t.check_setup.rpt
report_check_types -max_slew -max_capacitance -max_fanout -violators -digits 4 > $o/$t.limits_violators.rpt
