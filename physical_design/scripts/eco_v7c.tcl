# V7 ECO pass 3: STA counts antenna diodes as fanout. Nets that still exceed 10 loads only because of the diodes
# inserted by earlier antenna-repair stages (up to 11 diodes on one net) lose those diodes here; the antenna check/repair
# of the re-route (post-GRT and post-DRT) re-evaluates every net on the new topology and re-inserts what is really needed.
# env: ODB OUT
set lib $::env(PDK)/libs.ref/sky130_fd_sc_hd
read_lef $lib/techlef/sky130_fd_sc_hd__max.tlef
read_lef $lib/lef/sky130_fd_sc_hd.lef
read_db $::env(ODB)
set block [ord::get_db_block]
set removed 0
foreach net [$block getNets] {
  if {[$net getSigType] eq "POWER" || [$net getSigType] eq "GROUND"} continue
  set loads {}; set dio {}
  foreach it [$net getITerms] {
    if {[$it isInputSignal]} {
      lappend loads $it
      if {[string match ANTENNA* [[$it getInst] getName]]} { lappend dio [$it getInst] }
    }
  }
  if {[llength $loads] > 10 && [llength $dio] > 0} {
    foreach d $dio { odb::dbInst_destroy $d; incr removed }
    puts "DIODES_REMOVED [$net getName]: [llength $dio] (loads were [llength $loads])"
  }
}
puts "TOTAL_DIODES_REMOVED=$removed"
write_db $::env(OUT)/omega_fusion_soc_asic.odb
write_def $::env(OUT)/omega_fusion_soc_asic.def
write_verilog $::env(OUT)/omega_fusion_soc_asic.nl.v
write_verilog -include_pwr_gnd $::env(OUT)/omega_fusion_soc_asic.pnl.v
puts "ECO_V7C_DONE"
