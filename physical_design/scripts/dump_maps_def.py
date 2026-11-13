#!/usr/bin/env python3
"""Routed wire length per bin & layer straight from a routed DEF (real data). usage: dump_maps_def.py <def> <out.json> [bin_um]"""
import sys, re, json
d, out = sys.argv[1], sys.argv[2]; B = float(sys.argv[3]) if len(sys.argv) > 3 else 30.0
N = int(1800 // B) + 1; wl = {}; U = 1000.0; innets = False; layer = None; prev = None
tok = re.compile(r"\(\s*(\*|-?\d+)\s+(\*|-?\d+)\s*(?:\d+\s*)?\)|(\bNEW\b)\s+(\w+)|\+\s+ROUTED\s+(\w+)")
for ln in open(d):
    if ln.startswith("NETS "): innets = True; continue
    if ln.startswith("END NETS"): break
    if not innets: continue
    if "+ ROUTED" in ln or " NEW " in ln or ln.lstrip().startswith("NEW "): prev = None
    m = re.search(r"(?:ROUTED|NEW)\s+(\w+)", ln)
    if m: layer = m.group(1); prev = None
    if layer is None or not layer.startswith("met"): continue
    for g in re.finditer(r"\(\s*(\*|-?\d+)\s+(\*|-?\d+)\s*(?:\d+\s*)?\)", ln):
        x, y = g.group(1), g.group(2)
        x = prev[0] if x == "*" else int(x); y = prev[1] if y == "*" else int(y)
        if prev is not None and (x != prev[0] or y != prev[1]):
            g_ = wl.setdefault(layer, [[0.0] * N for _ in range(N)])
            x0, y0 = prev[0] / U, prev[1] / U; x1, y1 = x / U, y / U
            if abs(x1 - x0) >= abs(y1 - y0):   # horizontal: split across x bins
                a, b = sorted((x0, x1)); j = min(int(y0 // B), N - 1); i = int(a // B)
                while a < b and i < N:
                    e = min(b, (i + 1) * B); g_[j][i] += e - a; a = e; i += 1
            else:
                a, b = sorted((y0, y1)); i = min(int(x0 // B), N - 1); j = int(a // B)
                while a < b and j < N:
                    e = min(b, (j + 1) * B); g_[j][i] += e - a; a = e; j += 1
        prev = (x, y)
json.dump({"bin": B, "n": N, "wire_len": wl, "source": d.split("omega-fusion-tapeout/")[-1]}, open(out, "w"))
print({k: round(sum(map(sum, v))) for k, v in wl.items()})
