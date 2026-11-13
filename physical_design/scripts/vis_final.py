import sys; import os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from make_visuals import *
DEF = OF+"/release/gds/omega_fusion_soc_asic.def"; GDS = OF+"/release/gds/omega_fusion_soc_asic.gds"
pdn = RUNS+"/OMEGA_V4_FULL/01-openroad-globalplacement/omega_fusion_soc_asic.def"
R = TMP+"/"
src_def = "release/gds/omega_fusion_soc_asic.def (final routed DEF, run OMEGA_V6_SIGNOFF5)"
cap = {"07a": ("07a Detailed routing - full chip, met1-met4 (final routed DEF)", [0,0,1800,1800], ["met1","met2","met3","met4"]),
       "07b": ("07b Detailed routing - met1 only", [0,0,1800,1800], ["met1"]),
       "07c": ("07c Detailed routing - met2 only", [0,0,1800,1800], ["met2"]),
       "07d": ("07d Detailed routing - met3 only", [0,0,1800,1800], ["met3"]),
       "07e": ("07e Detailed routing - met4 only", [0,0,1800,1800], ["met4"]),
       "07f": ("07f Detailed routing - zoom 60x60 µm, all layers + vias", [1200,900,1260,960], ["met1","met2","met3","met4","via","via2","via3"])}
views = [{"out": R+k+".png", "layers": v[2], "box": v[1], "w": 2400, "h": 2400} for k, v in cap.items()]
klayout(DEF, views)
LEG = [("met1","#2d6cdf"),("met2","#e0472b"),("met3","#2da84a"),("met4","#d9a400")]
for k, (t, box, ly) in cap.items():
    annotate(R+k+".png", f"{VIS}/{k}_detailed_routing_{'_'.join(ly[:1]) if len(ly)==1 else ('zoom_60um' if k=='07f' else 'all_layers')}.png", box, t, src_def,
             "KLayout headless render of the routed DEF; colours: met1 blue, met2 red, met3 green, met4 yellow (met4 vertical = PDN straps + routes).", [(l,c) for l,c in LEG if l in ly])
# PDN (pre-routing DEF has only the power grid)
pv = [{"out": R+"02a.png","layers":["met1","met4"],"box":[0,0,1800,1800],"w":2400,"h":2400},
      {"out": R+"02b.png","layers":["met1","met4","via","via2","via3"],"box":[1250,880,1290,920],"w":2400,"h":2400}]
klayout(pdn, pv)
psrc = "openlane/omega_fusion_soc_v2/runs/OMEGA_V4_FULL/01-openroad-globalplacement/omega_fusion_soc_asic.def (PDN only, same grid as final)"
annotate(R+"02a.png", VIS+"/02a_pdn_full_vdd_vss.png", [0,0,1800,1800], "02a Power distribution: met1 rails (horizontal) + met4 straps (vertical), VDD/VSS", psrc, "PDN_MULTILAYER=false, PDN_CORE_RING=false. met1 rails every 2.72 µm alternate VDD/VSS; met4 straps alternate VDD/VSS.", [("met1 rails","#2d6cdf"),("met4 straps","#d9a400")])
annotate(R+"02b.png", VIS+"/02b_pdn_zoom_40um_vias.png", [1250,880,1290,920], "02b PDN zoom 40x40 µm: rails, straps and via stack (met1-via-met2-via2-met3-via3-met4)", psrc, "Vias at rail/strap crossings connect met1 to met4 through the via stack.", [("met1","#2d6cdf"),("met4","#d9a400")])
# final GDS
gv = [{"out": R+"08a.png","layers":["met1.drawing","met2.drawing","met3.drawing","met4.drawing"],"box":[0,0,1800,1800],"w":2400,"h":2400},
      {"out": R+"08b.png","layers":["met1.drawing","met2.drawing","met3.drawing","met4.drawing"],"box":[1180,880,1300,1000],"w":2400,"h":2400},
      {"out": R+"08c.png","layers":["li1.drawing","mcon.drawing","met1.drawing","via.drawing","met2.drawing","via2.drawing","met3.drawing"],"box":[1240,940,1270,970],"w":2400,"h":2400},
      {"out": R+"08d.png","layers":["diff.drawing","poly.drawing","licon1.drawing","li1.drawing","mcon.drawing","met1.drawing"],"box":[1240,940,1262,962],"w":2400,"h":2400}]
klayout(GDS, gv, lefs=False)
gs = "release/gds/omega_fusion_soc_asic.gds (Magic stream-out, XOR-clean vs KLayout stream-out)"
annotate(R+"08a.png", VIS+"/08a_final_gds_full_chip.png", [0,0,1800,1800], "08a Final GDS - full chip in KLayout (met1-met4)", gs, "Rendered with sky130A.lyp layer colours.")
annotate(R+"08b.png", VIS+"/08b_final_gds_core_zoom_120um.png", [1180,880,1300,1000], "08b Final GDS - core zoom 120x120 µm", gs, "met1-met4 interconnect over standard cells.")
annotate(R+"08c.png", VIS+"/08c_final_gds_interconnect_30um.png", [1240,940,1270,970], "08c Final GDS - interconnect detail 30x30 µm (li1, mcon, met1, via, met2, via2, met3)", gs, "")
annotate(R+"08d.png", VIS+"/08d_final_gds_cell_level_22um.png", [1240,940,1262,962], "08d Final GDS - cell level 22x22 µm (diff, poly, licon, li1, mcon, met1)", gs, "")
