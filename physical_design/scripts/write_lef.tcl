# env: PDK ODB OUT ; abstract LEF from final ODB (Magic WriteLEF produced an empty file on this design)
set lib $::env(PDK)/libs.ref/sky130_fd_sc_hd
read_lef $lib/techlef/sky130_fd_sc_hd__nom.tlef
read_lef $lib/lef/sky130_fd_sc_hd.lef
read_db $::env(ODB)
write_abstract_lef -bloat_factor 3 $::env(OUT)
