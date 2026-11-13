# V7 ECO pass 2: remove every remaining max-fanout violation (fanout is topological, so it can be fixed before re-routing).
# Input: output DB of eco_v7.tcl. Classes (detected from the DB, not from a list):
#   * clock leaf buffers (clkbuf_leaf_*) with fanout > 10: move the sink closest to a leaf buffer that still has room (<=9 sinks)
#     to that buffer (no new clock level, parent fanouts unchanged).
#   * other clock-tree buffers with fanout > 10: clone the driver and give the clone half of the sinks (as in eco_v7.tcl).
#   * data nets with fanout > 10: split in groups of <=5 sinks behind buf_6 (antenna diodes are never moved).
# env: ODB OUT
set lib $::env(PDK)/libs.ref/sky130_fd_sc_hd
read_lef $lib/techlef/sky130_fd_sc_hd__max.tlef
read_lef $lib/lef/sky130_fd_sc_hd.lef
read_db $::env(ODB)
set block [ord::get_db_block]
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
  set b [odb::dbInst_create $block [master $m] "v7b_buf_${tag}_$::cnt"]
  set nn [odb::dbNet_create $block "v7b_net_${tag}_$::cnt"]
  $nn setSigType [$src_net getSigType]
  [in_pin $b] connect $src_net
  [out_pin $b] connect $nn
  foreach s $sinks { $s disconnect; $s connect $nn }
  $b setOrigin [expr {int($x - 1000)}] [expr {int($y - 1000)}]
  $b setPlacementStatus PLACED
  return $b
}
# collect violators
set leaf {}; set clk {}; set data {}
foreach net [$block getNets] {
  if {[$net getSigType] eq "POWER" || [$net getSigType] eq "GROUND"} continue
  set n [llength [net_sinks $net]]
  if {$n <= 10} continue
  set d [net_driver $net]; if {$d eq ""} continue
  set dn [[$d getInst] getName]
  if {[string match clkbuf_leaf_* $dn]} { lappend leaf $net } elseif {[string match clkbuf_* $dn] || [string match v7_buf_cts* $dn]} { lappend clk $net } else { lappend data $net }
}
puts "FANOUT>10: leaf=[llength $leaf] clocktree=[llength $clk] data=[llength $data]"
# leaf buffers with room
array set room {}
foreach inst [$block getInsts] {
  if {[string match clkbuf_leaf_* [$inst getName]]} {
    set on [[out_pin $inst] getNet]; set room([$inst getName]) [llength [net_sinks $on]]
  }
}
foreach net $leaf {
  set d [net_driver $net]; set L [$d getInst]
  while {[llength [net_sinks $net]] > 10} {
    set best ""; set bd 1e18
    foreach s [net_sinks $net] {
      lassign [loc [$s getInst]] sx sy
      foreach mn [array names room] {
        if {$room($mn) > 9 || $mn eq [$L getName]} continue
        set mi [$block findInst $mn]; lassign [loc $mi] mx my
        set dist [expr {abs($sx-$mx)+abs($sy-$my)}]
        if {$dist < $bd} { set bd $dist; set best [list $s $mn] }
      }
    }
    if {$best eq ""} { puts "WARN leaf [$net getName] no room"; break }
    lassign $best s mn
    set mi [$block findInst $mn]
    $s disconnect; $s connect [[out_pin $mi] getNet]
    incr room($mn)
    puts "MOVE [[$s getInst] getName] [$net getName] -> $mn dist=[expr {$bd/1000.0}]um"
  }
}
foreach net $clk {
  set drv [net_driver $net]; set dinst [$drv getInst]; set parent [[in_pin $dinst] getNet]
  set sinks [net_sinks $net]
  set sorted [lsort -real -index 0 [lmap s $sinks { lassign [loc [$s getInst]] x y; list $x $s $x $y }]]
  set grp [lrange $sorted [expr {[llength $sorted]/2}] end]
  set cx 0; set cy 0
  foreach g $grp { set cx [expr {$cx+[lindex $g 2]}]; set cy [expr {$cy+[lindex $g 3]}] }
  set cx [expr {$cx/[llength $grp]}]; set cy [expr {$cy/[llength $grp]}]
  lassign [loc $dinst] dx dy
  add_buf $parent [string map {sky130_fd_sc_hd__ ""} [[$dinst getMaster] getName]] [lmap g $grp {lindex $g 1}] [expr {($cx+$dx)/2}] [expr {($cy+$dy)/2}] clk
  puts "CLONE [$net getName]: [llength $sinks] -> [expr {[llength $sinks]-[llength $grp]}] + [llength $grp]"
}
foreach net $data {
  set drv [net_driver $net]; lassign [loc [$drv getInst]] dx dy
  set sinks [net_sinks $net]; set ns [llength $sinks]
  set ng [expr {int(ceil($ns/5.0))}]; set gs [expr {int(ceil(double($ns)/$ng))}]
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
  puts "SPLIT [$net getName]: $ns sinks -> $ng groups"
}
add_global_connection -net VDD -inst_pattern .* -pin_pattern {^VPWR$|^VPB$} -power
add_global_connection -net VSS -inst_pattern .* -pin_pattern {^VGND$|^VNB$} -ground
global_connect
detailed_placement -max_displacement {500 100}
check_placement -verbose
# recount
set rem 0
foreach net [$block getNets] {
  if {[$net getSigType] eq "POWER" || [$net getSigType] eq "GROUND"} continue
  if {[llength [net_sinks $net]] > 10 && [net_driver $net] ne ""} { incr rem; puts "REMAINING fanout>10: [$net getName] [llength [net_sinks $net]]" }
}
puts "FANOUT_REMAINING=$rem"
foreach net [$block getNets] {
  if {[$net getSigType] eq "SIGNAL" || [$net getSigType] eq "CLOCK"} { set w [$net getWire]; if {$w ne "NULL"} { odb::dbWire_destroy $w } }
}
write_db $::env(OUT)/omega_fusion_soc_asic.odb
write_def $::env(OUT)/omega_fusion_soc_asic.def
write_verilog $::env(OUT)/omega_fusion_soc_asic.nl.v
write_verilog -include_pwr_gnd $::env(OUT)/omega_fusion_soc_asic.pnl.v
puts "ECO_V7B_DONE"
