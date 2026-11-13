# env: PDK ODB SDC SPEF OUT CORNERLIB(e.g. ss_100C_1v60). Classifies max-slew/cap violators by net.
set lib $::env(PDK)/libs.ref/sky130_fd_sc_hd
read_lef $lib/techlef/sky130_fd_sc_hd__max.tlef
read_lef $lib/lef/sky130_fd_sc_hd.lef
read_db $::env(ODB)
read_liberty $lib/lib/sky130_fd_sc_hd__$::env(CORNERLIB).lib
read_sdc $::env(SDC)
set_max_transition 0.75 [current_design]
set_max_capacitance 0.2 [current_design]
set_max_fanout 10 [current_design]
read_spef $::env(SPEF)
set_propagated_clock [all_clocks]
report_check_types -max_slew -max_capacitance -max_fanout -violators -digits 4 > $::env(OUT)/viol_raw.rpt
set fh [open $::env(OUT)/viol_raw.rpt r]; set mode ""
set outf [open $::env(OUT)/viol_nets.csv w]; puts $outf "kind,pin,net,fanout,driver_cell,value,slack"
while {[gets $fh line] >= 0} {
  if {[regexp {^max (slew|capacitance|fanout)} $line -> m]} {set mode $m; continue}
  if {[regexp {^(\S+)\s+([-0-9.]+)\s+([-0-9.]+)\s+([-0-9.]+) \(VIOLATED\)} $line -> p lim val sl]} {
    set pins [get_pins -quiet $p]; if {$pins eq ""} continue
    set net [get_nets -quiet -of_objects $pins]; if {$net eq ""} continue
    set fo [llength [get_pins -quiet -of_objects $net -filter "direction==input"]]
    set drv [get_pins -quiet -of_objects $net -filter "direction==output"]
    set dc ""; if {$drv ne ""} {set dc [get_property [get_lib_cells -of_objects [get_cells -of_objects [lindex $drv 0]]] name]}
    puts $outf "$mode,$p,[get_full_name $net],$fo,$dc,$val,$sl"
  }
}
close $outf; close $fh
