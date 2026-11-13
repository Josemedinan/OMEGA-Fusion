set lib $::env(PDK)/libs.ref/sky130_fd_sc_hd
read_lef $lib/techlef/sky130_fd_sc_hd__max.tlef
read_lef $lib/lef/sky130_fd_sc_hd.lef
read_db $::env(ODB)
set block [ord::get_db_block]
puts "=== WITH diode"
check_antennas -net net2070 -verbose
puts "ANT_WITH_DONE"
set d [$block findInst ANTENNA_2107]
puts "DIODE at [[$d getBBox] xMin] [[$d getBBox] yMin]"
odb::dbInst_destroy $d
puts "=== WITHOUT diode (wire stub of the diode left in place, so the check is conservative)"
check_antennas -net net2070 -verbose
puts "ANT_WITHOUT_DONE"
