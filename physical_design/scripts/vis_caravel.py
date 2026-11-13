import sys; import os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from make_visuals import *
from matplotlib.patches import Rectangle
W = OF+"/openlane/user_project_wrapper_v6/runs/WRAP_FINAL_PNR"
pdn = OF+"/openlane/user_project_wrapper_v6/runs/WRAP_FINAL_PDN/17-openroad-generatepdn/user_project_wrapper.def"; drt = W+"/24-openroad-detailedrouting/user_project_wrapper.def"
lefs = LEFS+[OF+"/release/lef/omega_fusion_soc_asic.lef"]
import make_visuals; make_visuals.LEFS = lefs
box = [0,0,2920,3520]
klayout(pdn, [{"out":TMP+"/09a.png","layers":["met4","met5"],"box":box,"w":2200,"h":2650},{"out":TMP+"/09c.png","layers":["met1","met4","met5","OUTLINE"],"box":[500,800,800,1100],"w":2400,"h":2400}])
klayout(drt, [{"out":TMP+"/09b.png","layers":["met1","met2","met3","met4","met5"],"box":box,"w":2200,"h":2650}])
def mprj(ax):
    ax.add_patch(Rectangle((560,860),1800,1800,fill=False,ec="red",lw=2.2,label="mprj (omega_fusion_soc_asic) 1800x1800 µm @ (560,860) N"))
    ax.add_patch(Rectangle((0,0),2920,3520,fill=False,ec="black",lw=1.5)); ax.legend(loc="upper right",fontsize=8)
src = "openlane/user_project_wrapper_v6/runs/WRAP_FINAL_PDN|WRAP_FINAL_PNR (wrapper with FINAL macro LEF/GDS/netlist/SPEF)"
annotate(TMP+"/09a.png", VIS+"/09a_caravel_wrapper_pdn_mprj.png", box, "09a Caravel user_project_wrapper (2920 x 3520 µm): PDN grid + macro mprj", src+"; DEF 17-generatepdn", "PSM-0040: all 8 power nets connected (vccd1/2, vdda1/2, vssd1/2, vssa1/2). Wrapper PDN: met4 vertical + met5 horizontal.", [("met4","#d9a400"),("met5","#8a3fc0")], mprj)
annotate(TMP+"/09b.png", VIS+"/09b_caravel_wrapper_routed_overview.png", box, "09b Caravel wrapper after detailed routing: wrapper logic + signal routes to mprj", src+"; DEF 24-openroad-detailedrouting", "Route DRC 0; macro interior is opaque (LEF abstract).", [("met1","#2d6cdf"),("met2","#e0472b"),("met3","#2da84a"),("met4","#d9a400"),("met5","#8a3fc0")], mprj)
def corner(ax): ax.add_patch(Rectangle((560,860),1800,1800,fill=False,ec="red",lw=2))
annotate(TMP+"/09c.png", VIS+"/09c_caravel_macro_corner_power_connection.png", [500,800,800,1100], "09c Macro corner (560,860): wrapper met4/met5 power stripes over the mprj met4 straps", src, "Wrapper met5 stripes (purple) cross the macro's met4 VDD/VSS straps -> via4 stack; red = macro boundary.", [("met4","#d9a400"),("met5","#8a3fc0"),("met1","#2d6cdf")], corner)
