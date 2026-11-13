# env: PDK ODB SDC SPEF
set lib $::env(PDK)/libs.ref/sky130_fd_sc_hd
read_lef $lib/techlef/sky130_fd_sc_hd__max.tlef
read_lef $lib/lef/sky130_fd_sc_hd.lef
read_db $::env(ODB)
read_liberty $lib/lib/sky130_fd_sc_hd__ss_100C_1v60.lib
read_sdc $::env(SDC)
set_propagated_clock [all_clocks]
read_spef $::env(SPEF)
puts "=== net2070 loads"
set block [ord::get_db_block]
set net [$block findNet net2070]
foreach it [$net getITerms] { puts "ITERM [[$it getInst] getName] [[[$it getInst] getMaster] getName] [$it getMTerm] sig=[[$it getMTerm] getSigType] io=[[$it getMTerm] getIoType]" }
puts "=== report_net"
report_net -digits 4 net2070
puts "=== fanout limit sources"
puts "sta max_fanout design: [sta::max_fanout_violation_count]"
report_check_types -max_fanout -violators -digits 3
puts "=== worst path through net2070"
report_checks -through [get_nets net2070] -path_delay max -format full -fields {slew cap fanout} -digits 4
report_checks -through [get_nets net2070] -path_delay min -format full -fields {slew cap fanout} -digits 4
puts "=== slews of loads (max_ss)"
foreach p [get_pins -of_objects [get_nets net2070]] { puts "PINSLEW [get_full_name $p] [sta::format_time [sta::pin_slew $p max] 4]" }
