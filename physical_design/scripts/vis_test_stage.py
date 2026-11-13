import sys; import os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from make_visuals import *
d=RUNS+"/OMEGA_V4_FULL/07-openroad-detailedplacement/omega_fusion_soc_asic.def"
klayout(d,[{"out":TMP+"/t_dpl_full.png","layers":["OUTLINE"],"box":[0,0,1800,1800],"w":2000,"h":2000},
           {"out":TMP+"/t_dpl_zoom.png","layers":["OUTLINE","li1.OBS","met1.PIN","met1"],"box":[900,900,1020,1020],"w":2000,"h":2000}])
