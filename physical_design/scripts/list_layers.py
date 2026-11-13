import pya,os
pdk=os.environ["PDK"]
opt=pya.LoadLayoutOptions(); c=opt.lefdef_config
c.lef_files=[pdk+"/libs.ref/sky130_fd_sc_hd/techlef/sky130_fd_sc_hd__nom.tlef",pdk+"/libs.ref/sky130_fd_sc_hd/lef/sky130_fd_sc_hd.lef"]
c.read_lef_with_def=False; c.produce_via_geometry=True; c.produce_pins=True; c.produce_cell_outlines=True; c.produce_routing=True; c.produce_obstructions=False
m=pdk+"/libs.tech/klayout/tech/sky130A.map"
ly=pya.Layout(); ly.read(inp,opt)
top=ly.top_cell(); print("top",top.name, top.bbox())
for li in ly.layer_indexes():
    info=ly.get_info(li); n=top.begin_shapes_rec(li); cnt=0
    while not n.at_end() and cnt<1: cnt+=1; n.next()
    print(info, top.bbox_per_layer(li))
