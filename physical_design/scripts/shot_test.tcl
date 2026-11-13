read_db $::env(ODB)
gui::set_display_controls "Instances/*" visible true
gui::fit
save_image -width 1600 $::env(OUT)
exit
