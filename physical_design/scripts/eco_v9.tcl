# V9 ECO (third iteration, on the routed V8 database with REAL SPEF). Targets what V8 still failed after re-route:
#  * hold -14 ps (1 endpoint, max_ss)  -> repair_timing -hold with SPEF at the end
#  * clk root: slew 1.77 ns (antenna diode far from the pin hangs on the port net) and cap 0.248 pF on the root-buffer -> clkbuf_0 wire
#       -> delete the antenna diode(s) on net `clk` (re-checked/re-inserted by the antenna repair of the re-route),
#          add a repeater (clkbuf_16) half way on the long root wire
#  * level-2 clock nodes clknet_2_*_0_clk (cap 0.22-0.23 pF after the level-4 clones increased their load) -> clone each driver, half of the sinks
#  * remaining data nets (viol_nets.csv from classify_viol.tcl on V8): single-sink long wires get buf_6 at the midpoint,
#       multi-sink nets are split in 2 groups behind buf_6 placed near the group centroid
# No SDC / limit change. New objects are prefixed v9_.
# env: PDK ODB RCX SDC OUT VIOL SM CM HM
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
set block [ord::get_db_block]
proc vio {tag} {
  puts "VIO $tag slew=[sta::max_slew_violation_count] cap=[sta::max_capacitance_violation_count] fanout=[sta::max_fanout_violation_count] hold_ws_ss=[sta::worst_slack_cmd min]"
}
vio before
proc master {n} { return [[ord::get_db] findMaster sky130_fd_sc_hd__$n] }
proc in_pin {inst} { foreach it [$inst getITerms] { if {[$it isInputSignal]} { return $it } }; return "" }
proc out_pin {inst} { foreach it [$inst getITerms] { if {[$it isOutputSignal]} { return $it } }; return "" }
proc is_diode {inst} { return [expr {[string match ANTENNA* [$inst getName]] || [string match *diode* [[$inst getMaster] getName]]}] }
proc loc {inst} { set b [$inst getBBox]; return [list [expr {([$b xMin]+[$b xMax])/2}] [expr {([$b yMin]+[$b yMax])/2}]] }
proc net_sinks {net} { set r {}; foreach it [$net getITerms] { if {[$it isInputSignal] && ![is_diode [$it getInst]]} { lappend r $it } }; return $r }
proc net_driver {net} { foreach it [$net getITerms] { if {[$it isOutputSignal]} { return $it } }; return "" }
set ::cnt 0
proc add_buf {src_net m sinks x y tag} {
  global block
  incr ::cnt
  set b [odb::dbInst_create $block [master $m] "v9_buf_${tag}_$::cnt"]
  set nn [odb::dbNet_create $block "v9_net_${tag}_$::cnt"]
  $nn setSigType [$src_net getSigType]
  [in_pin $b] connect $src_net
  [out_pin $b] connect $nn
  foreach s $sinks { $s disconnect; $s connect $nn }
  $b setOrigin [expr {int($x - 1000)}] [expr {int($y - 1000)}]
  $b setPlacementStatus PLACED
  return $b
}
# --- 1. diodes on the clk port net
set cn [$block findNet clk]
foreach it [$cn getITerms] {
  if {[is_diode [$it getInst]]} { puts "RM_DIODE [[$it getInst] getName]"; odb::dbInst_destroy [$it getInst] }
}
# --- 2. root repeater half way between the root buffer and clkbuf_0
foreach n [$block getNets] {
  if {[string match v7_net_clkroot_* [$n getName]]} {
    set d [net_driver $n]; set sk [net_sinks $n]
    lassign [loc [$d getInst]] dx dy; lassign [loc [[lindex $sk 0] getInst]] sx sy
    add_buf $n clkbuf_16 $sk [expr {($dx+$sx)/2}] [expr {($dy+$sy)/2}] clkmid
    puts "ROOT_REPEATER on [$n getName]"
  }
}
# --- 3. clone level-2 clock drivers
foreach i {0 1 2 3} {
  set net [$block findNet clknet_2_${i}_0_clk]; if {$net eq "NULL"} continue
  set drv [net_driver $net]; set dinst [$drv getInst]; set parent [[in_pin $dinst] getNet]
  set sinks [net_sinks $net]
  set sorted [lsort -real -index 0 [lmap s $sinks { lassign [loc [$s getInst]] x y; list $x $s $x $y }]]
  set grp [lrange $sorted [expr {[llength $sorted]/2}] end]
  set cx 0; set cy 0
  foreach g $grp { set cx [expr {$cx+[lindex $g 2]}]; set cy [expr {$cy+[lindex $g 3]}] }
  set cx [expr {$cx/[llength $grp]}]; set cy [expr {$cy/[llength $grp]}]
  lassign [loc $dinst] dx dy
  add_buf $parent [string map {sky130_fd_sc_hd__ ""} [[$dinst getMaster] getName]] [lmap g $grp {lindex $g 1}] [expr {($cx+$dx)/2}] [expr {($cy+$dy)/2}] cts2_$i
  puts "CLONE clknet_2_${i}_0_clk: [llength $sinks] -> [expr {[llength $sinks]-[llength $grp]}] + [llength $grp]"
}
# --- 4. data nets
set fh [open $::env(VIOL) r]; gets $fh; set seen {}
while {[gets $fh line] >= 0} {
  set n [lindex [split $line ,] 2]
  if {[string match clknet_* $n] || $n eq "clk" || [string match v7_net_clkroot_* $n] || [string match v9_* $n] || [lsearch -exact $seen $n] >= 0} continue
  lappend seen $n
}
close $fh
foreach n $seen {
  set net [$block findNet $n]; if {$net eq "NULL"} { puts "WARN no net $n"; continue }
  set drv [net_driver $net]; if {$drv eq ""} continue
  set sinks [net_sinks $net]; set ns [llength $sinks]; if {$ns == 0} continue
  lassign [loc [$drv getInst]] dx dy
  if {$ns == 1} {
    lassign [loc [[lindex $sinks 0] getInst]] sx sy
    add_buf $net buf_6 $sinks [expr {($dx+$sx)/2}] [expr {($dy+$sy)/2}] d
    puts "BUF1 $n"; continue
  }
  set ng 2; set gs [expr {int(ceil($ns/2.0))}]
  set xs {}; set ys {}
  foreach s $sinks { lassign [loc [$s getInst]] x y; lappend xs $x; lappend ys $y }
  set xr [expr {[tcl::mathfunc::max {*}$xs]-[tcl::mathfunc::min {*}$xs]}]; set yr [expr {[tcl::mathfunc::max {*}$ys]-[tcl::mathfunc::min {*}$ys]}]
  set axis [expr {$xr >= $yr ? 2 : 3}]
  set sorted [lsort -real -index $axis [lmap s $sinks { lassign [loc [$s getInst]] x y; list 0 $s $x $y }]]
  for {set k 0} {$k < $ng} {incr k} {
    set grp [lrange $sorted [expr {$k*$gs}] [expr {($k+1)*$gs-1}]]
    if {[llength $grp] == 0} continue
    set cx 0; set cy 0
    foreach g $grp { set cx [expr {$cx+[lindex $g 2]}]; set cy [expr {$cy+[lindex $g 3]}] }
    set cx [expr {$cx/[llength $grp]}]; set cy [expr {$cy/[llength $grp]}]
    add_buf $net buf_6 [lmap g $grp {lindex $g 1}] [expr {(0.7*$cx+0.3*$dx)}] [expr {(0.7*$cy+0.3*$dy)}] d
  }
  puts "SPLIT $n: $ns sinks -> $ng groups"
}
add_global_connection -net VDD -inst_pattern .* -pin_pattern {^VPWR$|^VPB$} -power
add_global_connection -net VSS -inst_pattern .* -pin_pattern {^VGND$|^VNB$} -ground
global_connect
detailed_placement -max_displacement {500 100}
check_placement -verbose
vio after_insert
repair_design -verbose -slew_margin $::env(SM) -cap_margin $::env(CM)
vio after_repair_design
repair_timing -hold -hold_margin $::env(HM) -setup_margin 0.0 -max_buffer_percent 30 -verbose
vio after_hold
detailed_placement -max_displacement {500 100}
check_placement -verbose
set block [ord::get_db_block]
foreach net [$block getNets] {
  if {[$net getSigType] eq "SIGNAL" || [$net getSigType] eq "CLOCK"} { set w [$net getWire]; if {$w ne "NULL"} { odb::dbWire_destroy $w } }
}
# renumber diodes contiguously (avoids the repair_antennas name-collision crash seen in V7)
set dio {}
foreach i [$block getInsts] { if {[string match ANTENNA_* [$i getName]]} { lappend dio $i } }
set k 0; foreach i $dio { $i rename TMPDIODE_$k; incr k }
set k 0; foreach i $dio { $i rename ANTENNA_$k; incr k }
puts "DIODES_RENUMBERED $k"
report_cell_usage
write_db $::env(OUT)/omega_fusion_soc_asic.odb
write_def $::env(OUT)/omega_fusion_soc_asic.def
write_verilog $::env(OUT)/omega_fusion_soc_asic.nl.v
write_verilog -include_pwr_gnd $::env(OUT)/omega_fusion_soc_asic.pnl.v
puts "ECO_V9_DONE"
