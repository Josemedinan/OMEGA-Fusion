# openroad -python dump_maps.py <odb> <outprefix> [binum=30]
# Real data from the ODB: cell-area density per bin and routed wire length per bin per layer.
import sys, odb, json
db = odb.dbDatabase.create(); odb.read_db(db, sys.argv[1]); out = sys.argv[2]
BIN = float(sys.argv[3]) if len(sys.argv) > 3 else 30.0
blk = db.getChip().getBlock(); dbu = blk.getDbUnitsPerMicron()
die = blk.getDieArea(); W = die.xMax()/dbu; H = die.yMax()/dbu
nx, ny = int(W//BIN)+1, int(H//BIN)+1
dens = [[0.0]*nx for _ in range(ny)]; std = [[0.0]*nx for _ in range(ny)]
cnt = {"tap":0,"fill":0,"logic":0}
for inst in blk.getInsts():
    m = inst.getMaster(); bb = inst.getBBox(); cx=(bb.xMin()+bb.xMax())/2/dbu; cy=(bb.yMin()+bb.yMax())/2/dbu
    a = (bb.xMax()-bb.xMin())*(bb.yMax()-bb.yMin())/dbu/dbu
    nm = m.getName()
    if "tap" in nm or "fill" in nm or "decap" in nm: continue   # density of functional cells only
    i=min(int(cx//BIN),nx-1); j=min(int(cy//BIN),ny-1); dens[j][i]+=a
wl = {}
for net in blk.getNets():
    if net.getSigType() not in ("SIGNAL","CLOCK"): continue
    w = net.getWire()
    if w is None: continue
    # second pass using wire shapes
    sh = odb.dbWireShapeItr(); sh.begin(w); s = odb.dbShape()
    while sh.next(s):
        if s.isVia(): continue
        l = s.getTechLayer().getName()
        r = s.getBox(); L = max(r.xMax()-r.xMin(), r.yMax()-r.yMin())/dbu
        cx=(r.xMin()+r.xMax())/2/dbu; cy=(r.yMin()+r.yMax())/2/dbu
        g = wl.setdefault(l, [[0.0]*nx for _ in range(ny)])
        g[min(int(cy//BIN),ny-1)][min(int(cx//BIN),nx-1)] += L
json.dump({"bin":BIN,"nx":nx,"ny":ny,"die":[W,H],"cell_area":dens,"wire_len":wl}, open(out+"_maps.json","w"))
print("done", out, {k:round(sum(map(sum,v))) for k,v in wl.items()})
