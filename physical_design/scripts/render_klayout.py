#!/usr/bin/env python3
"""Headless KLayout renderer of REAL physical files (DEF+LEF or GDS). Run inside the LibreLane image:
  klayout -zz -r render_klayout.py -rd jobs=<jobs.json>
jobs.json = {"in": "<def|gds>", "lefs": [...], "views": [{"out": png, "layers": [names], "box": [x1,y1,x2,y2] (um) | null,
             "w": 2400, "h": 2400}]}
DEF layer names: li1 met1 met2 met3 met4 met5 via via2 via3 via4 OUTLINE met4.PIN ...; GDS names: sky130A.lyp names."""
import pya, os, json
J = json.load(open(jobs))
pdk = os.environ["PDK"]
inp = J["in"]
COL = {"li1.OBS": "#9a9a9a", "met1.PIN": "#7aa7f0", "li1": "#9a9a9a", "met1": "#2d6cdf", "met2": "#e0472b", "met3": "#2da84a", "met4": "#d9a400", "met5": "#8a3fc0",
       "via": "#222222", "via2": "#222222", "via3": "#222222", "via4": "#222222", "OUTLINE": "#000000",
       "met1.PIN": "#2d6cdf", "met2.PIN": "#e0472b", "met3.PIN": "#2da84a", "met4.PIN": "#d9a400", "met5.PIN": "#8a3fc0"}
lv = pya.LayoutView()
opt = pya.LoadLayoutOptions()
is_def = inp.endswith(".def")
if is_def:
    c = opt.lefdef_config
    c.lef_files = J["lefs"]
    c.read_lef_with_def = False
    c.macro_resolution_mode = 1
    c.produce_via_geometry = True
    c.produce_pins = True
    c.produce_cell_outlines = True
    c.produce_obstructions = False
    c.produce_blockages = False
    c.produce_routing = True
    c.produce_labels = False
lv.load_layout(inp, opt, "", 0)
if not is_def:
    lv.load_layer_props(pdk + "/libs.tech/klayout/tech/sky130A.lyp")
lv.add_missing_layers()
lv.set_config("background-color", "#ffffff")
lv.set_config("grid-visible", "false")
lv.set_config("text-visible", "false")
lv.set_config("cell-box-visible", "false")
lv.set_config("cell-box-text-visible", "false")
lv.set_config("show-cell-boxes", "false") if False else None
lv.max_hier()

def apply(layers):
    it = lv.begin_layers()
    while not it.at_end():
        p = it.current()
        nm = p.name if p.name else p.source_layer_name if hasattr(p, "source_layer_name") else ""
        if is_def:
            nm = p.source.split(" ")[0]
        if not is_def: nm = (p.name or "").split(" ")[0]
        vis = nm in layers
        p.visible = vis
        if is_def and vis:
            col = int(COL.get(nm, "#555555")[1:], 16) | 0xFF000000
            p.fill_color = col; p.frame_color = col
            p.dither_pattern = 0 if nm.startswith("met") or nm.startswith("li") else 1
            p.width = 0
        lv.set_layer_properties(it, p)
        it.next()

for v in J["views"]:
    apply(v["layers"])
    if v.get("box"):
        x1, y1, x2, y2 = v["box"]
        lv.zoom_box(pya.DBox(x1, y1, x2, y2))
    else:
        lv.zoom_fit()
    W, H = v.get("w", 2400), v.get("h", 2400)
    lv.resize(W, H)
    lv.save_image(v["out"], W, H)
    print("saved", v["out"])
