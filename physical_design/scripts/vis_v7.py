# Renders the V7 final layout (LibreLane run OMEGA_V15_RT, "V7 final") with headless KLayout: routed DEF (all layers) and final GDS views.
# Outputs: visuals/v7/*.png  (V6/V4-checkpoint images in visuals/ are untouched).
import sys; import os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from make_visuals import *
F = RUNS+"/OMEGA_V15_RT/final"
DEF = F+"/def/omega_fusion_soc_asic.def"; GDS = F+"/gds/omega_fusion_soc_asic.gds"
OUTD = os.environ.get("V7_VIS_DIR", VIS+"/v7"); os.makedirs(OUTD, exist_ok=True)
R = TMP+"/v7_"
src_def = "runs/OMEGA_V15_RT/final/def/omega_fusion_soc_asic.def (V7 final routed DEF)"
src_gds = "runs/OMEGA_V15_RT/final/gds/omega_fusion_soc_asic.gds (V7 final GDS, Magic stream-out)"
LEG = [("met1","#2d6cdf"),("met2","#e0472b"),("met3","#2da84a"),("met4","#d9a400")]
rv = [{"out": R+"07a.png","layers":["met1","met2","met3","met4"],"box":[0,0,1800,1800],"w":2400,"h":2400}]
klayout(DEF, rv)
annotate(R+"07a.png", OUTD+"/v7_07a_detailed_routing_all_layers.png", [0,0,1800,1800], "V7 07a Detailed routing - full chip, met1-met4 (final routed DEF)", src_def, "met1 blue, met2 red, met3 green, met4 yellow.", LEG)
gv = [{"out": R+"08a.png","layers":["met1.drawing","met2.drawing","met3.drawing","met4.drawing"],"box":[0,0,1800,1800],"w":2400,"h":2400},
      {"out": R+"08b.png","layers":["met1.drawing","met2.drawing","met3.drawing","met4.drawing"],"box":[1180,880,1300,1000],"w":2400,"h":2400},
      {"out": R+"08d.png","layers":["diff.drawing","poly.drawing","licon1.drawing","li1.drawing","mcon.drawing","met1.drawing"],"box":[1240,940,1262,962],"w":2400,"h":2400}]
klayout(GDS, gv)
gs = src_gds
annotate(R+"08a.png", OUTD+"/v7_08a_final_gds_full_chip.png", [0,0,1800,1800], "V7 08a Final GDS - full chip in KLayout (met1-met4)", gs, "Rendered with sky130A.lyp layer colours.")
annotate(R+"08b.png", OUTD+"/v7_08b_final_gds_core_zoom_120um.png", [1180,880,1300,1000], "V7 08b Final GDS - core zoom 120x120 um", gs, "met1-met4 interconnect over standard cells.")
annotate(R+"08d.png", OUTD+"/v7_08d_final_gds_cell_level_22um.png", [1240,940,1262,962], "V7 08d Final GDS - cell level 22x22 um (diff, poly, licon, li1, mcon, met1)", gs, "")

# PDN: pre-routing DEF of the V4 base run contains only the power grid; the grid is generated once and is the same in V4-V7
pdn = RUNS+"/OMEGA_V4_FULL/01-openroad-globalplacement/omega_fusion_soc_asic.def"
pv = [{"out": R+"02a.png","layers":["met1","met4"],"box":[0,0,1800,1800],"w":2400,"h":2400},
      {"out": R+"02b.png","layers":["met1","met4","via","via2","via3"],"box":[1250,880,1290,920],"w":2400,"h":2400}]
klayout(pdn, pv)
psrc = "runs/OMEGA_V4_FULL/01-openroad-globalplacement/omega_fusion_soc_asic.def (PDN only; the grid is generated once and shared by V4-V7)"
annotate(R+"02a.png", OUTD+"/v7_02a_pdn_full_vdd_vss.png", [0,0,1800,1800], "V7 02a Power distribution (unchanged since the PDN stage): met1 rails + met4 straps, VDD/VSS", psrc, "PDN_MULTILAYER=false, PDN_CORE_RING=false. met1 rails every 2.72 um alternate VDD/VSS; met4 straps alternate VDD/VSS.", [("met1 rails","#2d6cdf"),("met4 straps","#d9a400")])
annotate(R+"02b.png", OUTD+"/v7_02b_pdn_zoom_40um.png", [1250,880,1290,920], "V7 02b PDN zoom 40x40 um (via cuts are not drawn by the DEF importer; connectivity is proven by the PSM check)", psrc, "", [("met1","#2d6cdf"),("met4","#d9a400")])
