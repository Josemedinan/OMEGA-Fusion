# V14 ECO (on the routed V13 database): V13 is clean on slew/cap/hold; 3 nets sit at 11 loads (diodes re-inserted by the antenna repair of the re-route). Cluster rule now triggers from 9 loads to leave margin.
# (V13 header follows) V13 ECO (on the routed V12 database with REAL SPEF): V12 left 1 slew net (net20940, 0.757 ns vs 0.75, weak clkdlybuf4s15_1 with 10 loads) and 1 fanout net.
# Combines: V10 split with buffers next to the driver, V11 re-homing of stranded diodes, V12 sink+diode cluster rule, plus a plain split for nets with >10 non-diode loads.
# (V10 text follows) V9 closed hold (+0.104 ns), fanout (0) and the clock-tree/root violations; what is left are 15 data nets with max-slew > 0.75 ns and 3 nets above 0.2 pF.
# Cause seen in V8/V9: buffers inserted half way along the wire left the weak driver (nor4_4, o31ai_4, clkdlybuf4s15_1, ...) with a long wire. Here every inserted buffer sits right next to the driver so the gate only sees a buffer input, and the long wire is driven by buf_6; capacitance violators are split in 3 groups.
# (history of V9 targets follows)
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
  set b [odb::dbInst_create $block [master $m] "v14_buf_${tag}_$::cnt"]
  set nn [odb::dbNet_create $block "v14_net_${tag}_$::cnt"]
  $nn setSigType [$src_net getSigType]
  [in_pin $b] connect $src_net
  [out_pin $b] connect $nn
  foreach s $sinks { $s disconnect; $s connect $nn }
  $b setOrigin [expr {int($x - 1000)}] [expr {int($y - 1000)}]
  $b setPlacementStatus PLACED
  return $b
}
# --- data nets (violators of the V9 route), buffers adjacent to the driver
set capnets {}
set fh [open $::env(VIOL) r]; gets $fh; set seen {}
while {[gets $fh line] >= 0} {
  set n [lindex [split $line ,] 2]
  if {[string match clknet_* $n] || $n eq "clk" || [lsearch -exact $seen $n] >= 0} continue
  lappend seen $n
}
close $fh
foreach n $seen {
  set net [$block findNet $n]; if {$net eq "NULL"} { puts "WARN no net $n"; continue }
  set drv [net_driver $net]; if {$drv eq ""} continue
  set sinks [net_sinks $net]; set ns [llength $sinks]; if {$ns == 0} continue
  lassign [loc [$drv getInst]] dx dy
  if {$ns == 1} {
    add_buf $net buf_6 $sinks [expr {$dx+3000}] $dy d
    puts "BUF1 $n"; continue
  }
  set ng [expr {[lsearch -exact $capnets $n] >= 0 ? 3 : 2}]
  if {$ng > $ns} { set ng $ns }
  set gs [expr {int(ceil(double($ns)/$ng))}]
  set xs {}; set ys {}
  foreach s $sinks { lassign [loc [$s getInst]] x y; lappend xs $x; lappend ys $y }
  set xr [expr {[tcl::mathfunc::max {*}$xs]-[tcl::mathfunc::min {*}$xs]}]; set yr [expr {[tcl::mathfunc::max {*}$ys]-[tcl::mathfunc::min {*}$ys]}]
  set axis [expr {$xr >= $yr ? 2 : 3}]
  set sorted [lsort -real -index $axis [lmap s $sinks { lassign [loc [$s getInst]] x y; list 0 $s $x $y }]]
  for {set k 0} {$k < $ng} {incr k} {
    set grp [lrange $sorted [expr {$k*$gs}] [expr {($k+1)*$gs-1}]]
    if {[llength $grp] == 0} continue
    add_buf $net buf_6 [lmap g $grp {lindex $g 1}] [expr {$dx+3000+$k*2800}] $dy d
  }
  puts "SPLIT $n: $ns sinks -> $ng groups"
}
# --- A. re-home stranded diodes
proc dist {a b} { lassign [loc $a] x1 y1; lassign [loc $b] x2 y2; return [expr {abs($x1-$x2)+abs($y1-$y2)}] }
set moved 0
foreach net [$block getNets] {
  if {[$net getSigType] eq "POWER" || [$net getSigType] eq "GROUND"} continue
  set bufs {}; set dios {}
  foreach it [$net getITerms] {
    if {![$it isInputSignal]} continue
    set inst [$it getInst]; set nm [$inst getName]
    if {[string match v7_buf_d_* $nm] || [string match v7b_buf_* $nm] || [string match v9_buf_d_* $nm] || [string match v10_buf_d_* $nm] || [string match v14_buf_d_* $nm]} { lappend bufs $inst }
    if {[is_diode $inst]} { lappend dios $it }
  }
  if {[llength $bufs] == 0 || [llength $dios] == 0} continue
  foreach dit $dios {
    set best ""; set bd 1e18
    foreach b $bufs {
      set on [[out_pin $b] getNet]
      foreach s [net_sinks $on] { set d [dist [$dit getInst] [$s getInst]]; if {$d < $bd} { set bd $d; set best $on } }
    }
    if {$best ne ""} { $dit disconnect; $dit connect $best; incr moved }
  }
  puts "REHOME [$net getName]: [llength $dios] diodes onto [llength $bufs] buffer nets"
}
puts "DIODES_REHOMED=$moved"
foreach net [$block getNets] {
  if {[$net getSigType] eq "POWER" || [$net getSigType] eq "GROUND"} continue
  set loads {}; set dios {}; set sinks {}
  foreach it [$net getITerms] {
    if {![$it isInputSignal]} continue
    lappend loads $it
    if {[is_diode [$it getInst]]} { lappend dios $it } else { lappend sinks $it }
  }
  if {[llength $loads] <= 8 || [llength $dios] == 0 || [llength $sinks] == 0} continue
  # assign each diode to its nearest non-diode sink; pick the sink with most diodes
  array unset dcnt; array unset dmem
  foreach s $sinks { set dcnt([$s getName]) 0; set dmem([$s getName]) {} }
  foreach d $dios {
    set best ""; set bd 1e18
    foreach s $sinks { set x [dist [$d getInst] [$s getInst]]; if {$x < $bd} { set bd $x; set best $s } }
    incr dcnt([$best getName]); lappend dmem([$best getName]) $d
  }
  set top ""; set tc -1
  foreach s $sinks { if {$dcnt([$s getName]) > $tc} { set tc $dcnt([$s getName]); set top $s } }
  set grp [concat [list $top] $dmem([$top getName])]
  lassign [loc [$top getInst]] sx sy
  add_buf $net buf_6 $grp [expr {$sx-3000}] $sy dio
  puts "DIODE_CLUSTER [$net getName]: loads=[llength $loads] -> sink [[$top getInst] getName] + [llength $dmem([$top getName])] diodes behind a buffer"
}
# --- plain split for nets with more than 10 non-diode loads (diodes re-homed afterwards by the same rule)
foreach net [$block getNets] {
  if {[$net getSigType] eq "POWER" || [$net getSigType] eq "GROUND"} continue
  set sinks [net_sinks $net]; set ns [llength $sinks]
  if {$ns <= 10 || [net_driver $net] eq ""} continue
  lassign [loc [[net_driver $net] getInst]] dx dy
  set ng [expr {int(ceil($ns/6.0))}]; set gs [expr {int(ceil(double($ns)/$ng))}]
  set sorted [lsort -real -index 2 [lmap s $sinks { lassign [loc [$s getInst]] x y; list 0 $s $x $y }]]
  for {set k 0} {$k < $ng} {incr k} {
    set grp [lrange $sorted [expr {$k*$gs}] [expr {($k+1)*$gs-1}]]
    if {[llength $grp] == 0} continue
    add_buf $net buf_6 [lmap g $grp {lindex $g 1}] [expr {$dx+3000+$k*2800}] $dy d
  }
  puts "PLAIN_SPLIT [$net getName]: $ns sinks -> $ng groups"
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
