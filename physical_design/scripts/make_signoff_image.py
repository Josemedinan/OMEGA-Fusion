import json, csv, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os; H=os.environ.get("OMEGA_RELEASE","release")+"/"  # work-tree release dir (see docs/methodology/reproduction.md)
rows={r["tag"]:r for r in csv.DictReader(open(H+"reports/signoff_v6/sta_independent_summary.csv"))}
C=["nom_tt_025C_1v80","nom_ss_100C_1v60","nom_ff_n40C_1v95","min_tt_025C_1v80","min_ss_100C_1v60","min_ff_n40C_1v95","max_tt_025C_1v80","max_ss_100C_1v60","max_ff_n40C_1v95"]
fig=plt.figure(figsize=(14,9.5),dpi=130)
ax=fig.add_axes([.03,.55,.45,.4]); ax.axis("off")
chk=[("Magic DRC (GDS)","0 errors","PASS"),("KLayout DRC (GDS)","0 errors","PASS"),("Route DRC (TritonRoute)","0 violations","PASS"),("LVS Netgen","Circuits match uniquely: 67,494 devices / 66,673 nets","PASS"),
("Antenna (post-DRT)","0 nets / 0 pins","PASS"),("XOR Magic vs KLayout GDS","no differences","PASS"),("Disconnected pins / PDN (PSM)","0 / VDD,VSS connected","PASS"),
("Setup, 9 corners (reg2reg+IO)","WNS +52.0 ns (max_ss)","PASS"),("Hold, 9 corners","WNS +0.017 ns (max_ff)","PASS"),("Recovery / removal rst_n","+89.9 ns / +0.017..+0.64 ns","PASS"),
("Max slew @0.75 ns flow limit","158 pins (max_ss), 16 (nom_tt)","FAIL"),("Max cap @0.2 pF flow limit","18-23 pins/corner (clock-tree nets)","FAIL"),("Max fanout @10 flow limit","83 nets/corner (CTS nodes + mux selects)","FAIL"),
("Liberty-only limits (no SDC override)","3 slew on port net clk (max_ss); cap 0","FAIL (3)"),("Equivalence (EQY)","not run","UNVERIFIED"),("Caravel wrapper DRC/LVS","not run (memory)","UNVERIFIED")]
ax.set_title("Signoff evidence - final layout V6 (all numbers measured)",loc="left",fontweight="bold")
for i,(a,b,c) in enumerate(chk):
    y=1-i/len(chk); col={"PASS":"#2ca02c","FAIL":"#d62728","UNVERIFIED":"#ff7f0e"}.get(c.split()[0],"#d62728")
    ax.text(0,y,a,fontsize=8,va="top"); ax.text(.36,y,b,fontsize=7.5,va="top",family="monospace"); ax.text(.97,y,c,fontsize=8,va="top",ha="right",color=col,fontweight="bold")
a2=fig.add_axes([.56,.58,.4,.34]); S=np.array([[float(rows[c+"_flow"]["setup_ws_ns"]),float(rows[c+"_flow"]["hold_ws_ns"])] for c in C])
im=a2.imshow(S.T,aspect="auto",cmap="RdYlGn",vmin=-1,vmax=1); a2.set_yticks([0,1]); a2.set_yticklabels(["setup WNS [ns]","hold WNS [ns]"]); a2.set_xticks(range(9)); a2.set_xticklabels([c.replace("_025C_1v80","").replace("_100C_1v60","").replace("_n40C_1v95","") for c in C],fontsize=7)
for i in range(9):
    a2.text(i,0,f"{S[i,0]:.1f}",ha="center",va="center",fontsize=7); a2.text(i,1,f"{S[i,1]:.3f}",ha="center",va="center",fontsize=7)
a2.set_title("Independent post-route STA (OpenROAD + extracted SPEF): all slacks >= 0",fontsize=9)
a3=fig.add_axes([.05,.08,.42,.36]); x=np.arange(9); w=.27
for j,(k,l) in enumerate([("slew_vio","slew"),("cap_vio","cap"),("fanout_vio","fanout")]): a3.bar(x+(j-1)*w,[int(rows[c+"_flow"][k]) for c in C],w,label=l)
a3.set_yscale("symlog",linthresh=1); a3.set_xticks(x); a3.set_xticklabels([c.replace("_025C_1v80","").replace("_100C_1v60","").replace("_n40C_1v95","") for c in C],fontsize=7); a3.legend(fontsize=8); a3.set_title("Electrical limit violations vs flow limits (what still fails)",fontsize=9)
a4=fig.add_axes([.56,.08,.4,.36]); a4.axis("off"); a4.set_title("Liberty-only check (SDC without set_max_*): 4 corners",fontsize=9,loc="left")
L=[("max_ff","0","0","0"),("max_tt","0","0","0"),("nom_ss","0","0","0"),("max_ss","3","0","0")]
for i,(c,s,cp,f) in enumerate(L): a4.text(0,.8-i*.17,f"{c}:  slew {s}   cap {cp}   fanout {f}",family="monospace",fontsize=9)
a4.text(0,.1,"The 3 slew items are the clk port net / clock root buffer\n(driving-cell model inv_2 into the CTS root); real Caravel\ndrives wb_clk_i from the wrapper clock tree.",fontsize=8)
fig.text(.01,.005,"Sources: release/reports/signoff_v6/{manufacturability.rpt,lvs,magic_drc,sta_independent_summary.csv}, release/reports/signoff_v6/sta/*.summary.txt",fontsize=7,family="monospace")
fig.savefig(H+"visuals/v4_v6/10_signoff_evidence.png"); print("ok")
