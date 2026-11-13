# V7 ECO: surgical fix of the residual max-slew / max-cap / max-fanout violators of V6 (viol_max_ss).
# Runs on the routed V6 database with REAL SPEF (SS/max for limits, FF/min for hold). V6 files are only read.
# env: PDK ODB RCX SDC OUT VIOL(csv of violators) SM CM HM
#  1. CTS level-4 nodes (clknet_4_*_0_clk, fanout 16-17, 0.21-0.26 pF): clone the driving clkbuf, move half of the sinks
#     to the clone (same parent net, same cell => no extra clock level, latency ~unchanged).
#  2. clk root net (port driver model inv_2 -> long wire -> clkbuf_0): insert clkbuf_16 near the port in front of clkbuf_0.
#  3. data nets (36): single-fanout long wires get a buffer at the midpoint; multi-fanout nets are split in groups of <=5 sinks,
#     each group behind a buffer. Antenna diodes are never moved.
#  4. repair_design (margins SM/CM) and repair_timing -hold (SPEF-based), legalize, strip routes, write DB.
# No SDC change, no limit change. Instances/nets created here are prefixed "v7_".
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
set db [ord::get_db]
proc vio {tag} {
  puts "VIO $tag slew=[sta::max_slew_violation_count] cap=[sta::max_capacitance_violation_count] fanout=[sta::max_fanout_violation_count] hold_ws_ss=[sta::worst_slack_cmd min]"
}
vio before

proc master {n} { return [[ord::get_db] findMaster sky130_fd_sc_hd__$n] }
proc in_pin {inst} { foreach it [$inst getITerms] { if {[$it isInputSignal]} { return $it } }; return ""}
proc out_pin {inst} { foreach it [$inst getITerms] { if {[$it isOutputSignal]} { return $it } }; return ""}
proc is_diode {inst} { return [expr {[string match ANTENNA* [$inst getName]] || [string match *diode* [[$inst getMaster] getName]]}] }
proc loc {inst} { set b [$inst getBBox]; return [list [expr {([$b xMin]+[$b xMax])/2}] [expr {([$b yMin]+[$b yMax])/2}]] }
set ::cnt 0

# add a buffer (master $m) whose input is on $src_net and output on a new net; moves $sinks (iterm list) to the new net; place at ($x,$y)
proc add_buf {src_net m sinks x y tag} {
  global block
  incr ::cnt
  set b [odb::dbInst_create $block [master $m] "v7_buf_${tag}_$::cnt"]
  set nn [odb::dbNet_create $block "v7_net_${tag}_$::cnt"]
  $nn setSigType [$src_net getSigType]
  [in_pin $b] connect $src_net
  [out_pin $b] connect $nn
  foreach s $sinks { $s disconnect; $s connect $nn }
  $b setOrigin [expr {int($x - 1000)}] [expr {int($y - 1000)}]
  $b setPlacementStatus PLACED
  return $b
}
proc net_sinks {net} {
  set r {}
  foreach it [$net getITerms] { if {[$it isInputSignal] && ![is_diode [$it getInst]]} { lappend r $it } }
  return $r
}
proc net_driver {net} { foreach it [$net getITerms] { if {[$it isOutputSignal]} { return $it } }; return "" }

# --- 1. clone CTS level-4 drivers
foreach i {0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15} {
  set nn clknet_4_${i}_0_clk
  set net [$block findNet $nn]; if {$net eq "NULL"} { puts "WARN no net $nn"; continue }
  set drv [net_driver $net]; set dinst [$drv getInst]
  set parent [[in_pin $dinst] getNet]
  set sinks [net_sinks $net]
  set xs {}; set ys {}
  foreach s $sinks { lassign [loc [$s getInst]] x y; lappend xs $x; lappend ys $y }
  set xr [expr {[tcl::mathfunc::max {*}$xs]-[tcl::mathfunc::min {*}$xs]}]; set yr [expr {[tcl::mathfunc::max {*}$ys]-[tcl::mathfunc::min {*}$ys]}]
  set axis [expr {$xr >= $yr ? 0 : 1}]
  set sorted [lsort -real -index 0 [lmap s $sinks { lassign [loc [$s getInst]] x y; list [expr {$axis==0?$x:$y}] $s $x $y }]]
  set half [expr {[llength $sorted]/2}]
  set grp [lrange $sorted $half end]
  set cx 0; set cy 0
  foreach g $grp { set cx [expr {$cx+[lindex $g 2]}]; set cy [expr {$cy+[lindex $g 3]}] }
  set cx [expr {$cx/[llength $grp]}]; set cy [expr {$cy/[llength $grp]}]
  lassign [loc $dinst] dx dy
  set b [add_buf $parent [string map {sky130_fd_sc_hd__ ""} [[$dinst getMaster] getName]] [lmap g $grp {lindex $g 1}] [expr {($cx+$dx)/2}] [expr {($cy+$dy)/2}] cts$i]
  puts "CLONE $nn: [llength $sinks] sinks -> [expr {[llength $sinks]-[llength $grp]}] + [llength $grp]"
}

# --- 2. clk root: buffer in front of clkbuf_0_clk
set cn [$block findNet clk]
foreach it [$cn getITerms] {
  if {[string match clkbuf_0_clk [[$it getInst] getName]]} {
    set bt [lindex [$block getBTerms] 0]
    foreach t [$block getBTerms] { if {[$t getName] eq "clk"} { set bt $t } }
    set bb [$bt getBBox]
    set px [expr {([$bb xMin]+[$bb xMax])/2}]; set py [expr {([$bb yMin]+[$bb yMax])/2}]
    # place 15 um inside the die from the pin
    set die [$block getDieArea]
    set ix $px; set iy $py
    if {$px < [$die xMin] + 1000} { set ix [expr {$px+15000}] } elseif {$px > [$die xMax] - 1000} { set ix [expr {$px-15000}] }
    if {$py < [$die yMin] + 1000} { set iy [expr {$py+15000}] } elseif {$py > [$die yMax] - 1000} { set iy [expr {$py-15000}] }
    add_buf $cn clkbuf_16 [list $it] $ix $iy clkroot
    puts "ROOT buffer near pin ($px,$py)"
    break
  }
}

# --- 3. data nets
set fh [open $::env(VIOL) r]; set seen {}
gets $fh
while {[gets $fh line] >= 0} {
  set f [split $line ,]; set n [lindex $f 2]
  if {[string match clknet_* $n] || $n eq "clk" || [lsearch -exact $seen $n] >= 0} continue
  lappend seen $n
}
close $fh
foreach n $seen {
  set net [$block findNet $n]; if {$net eq "NULL"} { puts "WARN no net $n"; continue }
  set drv [net_driver $net]; if {$drv eq ""} { puts "WARN no driver $n"; continue }
  set sinks [net_sinks $net]; set ns [llength $sinks]
  lassign [loc [$drv getInst]] dx dy
  if {$ns == 0} continue
  if {$ns == 1} {
    lassign [loc [[lindex $sinks 0] getInst]] sx sy
    add_buf $net buf_4 $sinks [expr {($dx+$sx)/2}] [expr {($dy+$sy)/2}] d
    puts "BUF1 $n"
    continue
  }
  set ng [expr {max(2, int(ceil($ns/5.0)))}]
  set gs [expr {int(ceil(double($ns)/$ng))}]
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
    add_buf $net buf_6 [lmap g $grp {lindex $g 1}] [expr {($cx+$dx)/2}] [expr {($cy+$dy)/2}] d
  }
  puts "SPLIT $n: $ns sinks -> $ng groups"
}

# power/ground pins of the new instances
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
puts "ECO_V7_DONE"
