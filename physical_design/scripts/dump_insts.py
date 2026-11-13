# openroad -python dump_insts.py <odb> <out.json>  : real instance geometry + clock-tree edges from an ODB
import sys, odb, json
db = odb.dbDatabase.create(); odb.read_db(db, sys.argv[1])
blk = db.getChip().getBlock(); u = blk.getDbUnitsPerMicron()
def cls(n):
    if "tapvpwrvgnd" in n or "__tap" in n: return "tap"
    if "fill" in n or "decap" in n: return "fill"
    if "diode" in n: return "antenna"
    if n.startswith("sky130_fd_sc_hd__df") or "dlxt" in n or "dlxb" in n: return "seq"
    if "clkbuf" in n or "clkinv" in n: return "clk"
    if "dlygate" in n or "clkdlybuf" in n or "dlymetal" in n: return "delay"
    if "__buf_" in n or "__inv_" in n: return "buf"
    return "comb"
rows = []
for i in blk.getInsts():
    b = i.getBBox(); m = i.getMaster().getName()
    rows.append([i.getName(), m, cls(m), b.xMin()/u, b.yMin()/u, b.xMax()/u, b.yMax()/u, 1 if i.isPlaced() else 0])
edges = []
for n in blk.getNets():
    nm = n.getName()
    if not (nm.startswith("clknet") or nm == "clk"): continue
    drv = None; loads = []
    for it in n.getITerms():
        if it.isOutputSignal(): drv = it.getInst().getName()
        elif it.isInputSignal(): loads.append(it.getInst().getName())
    bt = [bt for bt in n.getBTerms()]
    if bt and drv is None: drv = "PORT_clk"
    edges.append([nm, drv, loads])
pins = []
for bt in blk.getBTerms():
    bb = bt.getBBox()
    pins.append([bt.getName(), bb.xMin()/u, bb.yMin()/u, bb.xMax()/u, bb.yMax()/u, bt.getSigType()])
die = blk.getDieArea(); core = blk.getCoreArea()
json.dump({"die": [die.xMin()/u, die.yMin()/u, die.xMax()/u, die.yMax()/u], "core": [core.xMin()/u, core.yMin()/u, core.xMax()/u, core.yMax()/u],
           "insts": rows, "clk_edges": edges, "pins": pins}, open(sys.argv[2], "w"))
print("insts", len(rows), "clk nets", len(edges), "pins", len(pins))
