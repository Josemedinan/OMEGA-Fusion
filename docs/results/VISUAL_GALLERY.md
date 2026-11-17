# Visual gallery

All images are generated from real physical files (ODB/DEF/GDS/guide files) by OpenROAD-extracted geometry plus matplotlib, or by headless KLayout 0.30.7. Nothing is synthetic. Date of the results: 2026-11-12. Image scripts: `physical_design/scripts/`.
Checkpoints refer to LibreLane run tags under the work tree (not stored in git; see `docs/methodology/cleanup_manifest.md`). Missing: no images exist for Caravel wrapper DRC/LVS (not run) and no Magic screenshots (Magic only runs in batch mode).

## V7 images (`visuals/v7/`, current candidate, 2026-11-13)
Each image title names its version. Tools: OpenROAD-extracted geometry (`dump_insts.py`, `dump_maps_def.py`) + matplotlib, or headless KLayout 0.30.7 (`vis_v7.py`). Run: LibreLane `OMEGA_V15_RT` (= V7) unless a row says otherwise.

| Image | Stage | Checkpoint (source) | Tool |
|---|---|---|---|
| `v7_01_floorplan_die_core_pins.png` | Floorplan (shared V4–V7) | `OMEGA_V4_FULL/01-openroad-globalplacement` odb | OpenROAD geometry + matplotlib |
| `v7_02a_pdn_full_vdd_vss.png`, `v7_02b_pdn_zoom_40um.png` | PDN (shared V4–V7) | `OMEGA_V4_FULL/01-…` DEF (power grid only) | KLayout headless |
| `v4_03_global_placement_full.png` | Global placement — **V4 base run, not the V7 final** | `OMEGA_V4_FULL/01-…` odb | OpenROAD + matplotlib |
| `v7_03b_placement_density_heatmap.png`, `v7_04a_detailed_placement_full.png`, `v7_04b_detailed_placement_zoom_100um.png` | Final detailed placement | `OMEGA_V15_RT/06-openroad-detailedrouting` odb | OpenROAD + matplotlib |
| `v7_05a_cts_clock_tree_full.png`, `v7_05b_cts_clock_tree_zoom_250um.png` | Clock network (TritonCTS + 22 ECO buffers) | same odb | OpenROAD + matplotlib |
| `v7_06_global_routing_guides_by_layer.png`, `v7_06b_global_routing_guides_overlay.png` | Global routing guides | `OMEGA_V15_RT/01-openroad-globalrouting/after_grt.guide` | matplotlib |
| `v7_06c_routing_congestion_heatmap_final.png` | Congestion | `OMEGA_V15_RT/final/def` | matplotlib |
| `v7_07a_detailed_routing_all_layers.png` | Detailed routing | `OMEGA_V15_RT/final/def` | KLayout headless |
| `v7_08a_final_gds_full_chip.png`, `v7_08b_final_gds_core_zoom_120um.png`, `v7_08d_final_gds_cell_level_22um.png` | Final GDS (sha256 `275337f0…`) | `OMEGA_V15_RT/final/gds` | KLayout headless |
| `../00_hero_final_gds_klayout.png` | Hero (crop of `v7_08a`, pixels unmodified) | same GDS | KLayout headless |

| | |
|---|---|
| ![](../../visuals/v7/v7_01_floorplan_die_core_pins.png) | ![](../../visuals/v7/v7_02a_pdn_full_vdd_vss.png) |
| ![](../../visuals/v7/v4_03_global_placement_full.png) | ![](../../visuals/v7/v7_04a_detailed_placement_full.png) |
| ![](../../visuals/v7/v7_05a_cts_clock_tree_full.png) | ![](../../visuals/v7/v7_06b_global_routing_guides_overlay.png) |
| ![](../../visuals/v7/v7_06c_routing_congestion_heatmap_final.png) | ![](../../visuals/v7/v7_07a_detailed_routing_all_layers.png) |
| ![](../../visuals/v7/v7_08a_final_gds_full_chip.png) | ![](../../visuals/v7/v7_08b_final_gds_core_zoom_120um.png) |

**Legend note (CTS/placement images):** the class "clkbuf*/clkinv* cells (counted by name…)" counts cells by master name; it includes non-CTS buffers and is not the CTS result (2,168 + 102 per `metrics.json`).

# Legacy images: V4 base run and V6 (`visuals/v4_v6/`)
These are **not** the final layout; they are kept for the baseline record. Their on-image titles do not carry a version tag, so this section is the authority: `01`–`05` come from the V4 base run, `06*` from V6 guides, `07*`/`08*` from the V6 routed DEF/GDS.

## Errata (read before quoting numbers from images)

* **`05a` / `05b` (CTS):** the legend counts "clock buffers/inv (4267)" are a *cell-name pattern* count (`clkbuf*`/`clkinv*`) on the V4 CTS checkpoint and include repair buffers that use clock-buffer masters. The authoritative TritonCTS result in `metrics.json` is **2,168 clock buffers + 102 clock inverters**. The title's "H-tree" is descriptive; topology was not analysed. The picture is the V4 checkpoint (before the two ECO rounds that resized drivers).
* **`01`–`05`:** taken from the V4 base run (`OMEGA_V4_FULL`), not from the final V6 database; cell sizes/buffers differ slightly after the ECO rounds. `06*` use the V6 global-routing guides; `07*`/`08*` use the final V6 routed DEF/GDS.
* **`02b`:** via cuts are not drawn by the DEF importer; PDN connectivity is proven by the PSM check, not by this image.
* **`00_hero`:** crop (axes frame only, pixels unmodified) of the **V7** GDS render `v7/v7_08a_final_gds_full_chip.png`; the V6 hero is `00_hero_v6_gds_klayout.png`.
* **`v7/*`:** rendered from the V7 final DEF/GDS (LibreLane run `OMEGA_V15_RT`, 2026-11-13) with the same scripts (`physical_design/scripts/vis_v7.py`); all other images are V4/V6 as stated per image.
* **`05a`, `06`, `06b`:** straight lines are connectivity / guides, not routed wires.

## 00_hero_final_gds_klayout.png (V7)
![00_hero](../../visuals/00_hero_final_gds_klayout.png)

Final GDS, full chip, met1–met4 (crop of v7_08a). *Source:* release asset `omega_fusion_soc_asic_V7.gds.gz` (`docs/RELEASE_ASSETS.md`) (Magic stream-out, XOR-clean vs KLayout stream-out). *Tool:* KLayout 0.30.7 headless, `sky130A.lyp` colours.

## V7 images (`visuals/v7/`)
| | |
|---|---|
| ![](../../visuals/v7/v7_07a_detailed_routing_all_layers.png)<br>Detailed routing, all layers (V7 routed DEF) | ![](../../visuals/v7/v7_08a_final_gds_full_chip.png)<br>Final GDS, full chip |
| ![](../../visuals/v7/v7_08b_final_gds_core_zoom_120um.png)<br>Final GDS, core zoom 120×120 µm | ![](../../visuals/v7/v7_08d_final_gds_cell_level_22um.png)<br>Final GDS, cell level 22×22 µm |

*Source:* `runs/OMEGA_V15_RT/final/{def,gds}` — *Tool:* KLayout 0.30.7 headless.

In the V7 layout the numbers are not shown on the pictures; see `docs/results/V7_ECO_REPORT.md`.

## 01_floorplan_die_core_pins.png
![01_floorplan_die_core_pins.png](../../visuals/v4_v6/01_floorplan_die_core_pins.png)

Floorplan: die 1800x1800 µm, core 1749.4x1746.2 µm (3.055 mm²), 179 IO pins by side, 43,470 tap cells (grey lines). Dimension arrows in µm.

*Source:* `ODB OMEGA_V4_FULL/01 (floorplan/IO/tap content)`

## 02a_pdn_full_vdd_vss.png
![02a_pdn_full_vdd_vss.png](../../visuals/v4_v6/02a_pdn_full_vdd_vss.png)

Power grid: met1 rails + met4 straps, VDD/VSS alternating (full die).

*Source:* `DEF with PDN only (V4/01), same grid as final`

## 02b_pdn_zoom_40um_straps_rails.png
![02b_pdn_zoom_40um_straps_rails.png](../../visuals/v4_v6/02b_pdn_zoom_40um_straps_rails.png)

PDN zoom: rails crossing two met4 straps. Via cuts are not drawn by the DEF importer; connectivity proven by PSM, not by this image.

*Source:* `same`

## 03_global_placement_full.png
![03_global_placement_full.png](../../visuals/v4_v6/03_global_placement_full.png)

Global placement: flip-flop arrays (red) left/bottom, datapath logic (blue) right/top; the die is ~28 % used.

*Source:* `ODB V4/01`

## 03b_placement_density_heatmap.png
![03b_placement_density_heatmap.png](../../visuals/v4_v6/03b_placement_density_heatmap.png)

Placement density heatmap (functional cell area / bin area, 30 µm bins).

*Source:* `ODB V4/07 (after detailed placement)`

## 04a_detailed_placement_full.png
![04a_detailed_placement_full.png](../../visuals/v4_v6/04a_detailed_placement_full.png)

Legalized placement, full chip, cells coloured by class (comb, flop, clock, delay/IO, repair buffers).

*Source:* `ODB V4/07`

## 04b_detailed_placement_zoom_100um.png
![04b_detailed_placement_zoom_100um.png](../../visuals/v4_v6/04b_detailed_placement_zoom_100um.png)

Legalized standard cells, 100x100 µm zoom (tap cells = grey dashes).

*Source:* `ODB V4/07`

## 05a_cts_clock_tree_full.png
![05a_cts_clock_tree_full.png](../../visuals/v4_v6/05a_cts_clock_tree_full.png)

Clock tree: 4,267 clock buffers/inverters, upper-level (black) and leaf (green) driver→load connectivity. Straight lines are connectivity, not routed wires.

*Source:* `ODB V4/08`

## 05b_cts_clock_tree_zoom_250um.png
![05b_cts_clock_tree_zoom_250um.png](../../visuals/v4_v6/05b_cts_clock_tree_zoom_250um.png)

Clock tree zoom 250x250 µm.

*Source:* `ODB V4/08`

## 06_global_routing_guides_by_layer.png
![06_global_routing_guides_by_layer.png](../../visuals/v4_v6/06_global_routing_guides_by_layer.png)

Global-routing guide coverage per layer met1–met4 (guides saturate met1/met2 bins; overflow was 0). Not final wires.

*Source:* `after_grt.guide V6/01`

## 06b_global_routing_guides_overlay.png
![06b_global_routing_guides_overlay.png](../../visuals/v4_v6/06b_global_routing_guides_overlay.png)

All global-routing guides overlaid, colour per layer.

*Source:* `after_grt.guide V6/01`

## 06c_routing_congestion_heatmap_final.png
![06c_routing_congestion_heatmap_final.png](../../visuals/v4_v6/06c_routing_congestion_heatmap_final.png)

Congestion: final routed wire length / track capacity per 30 µm bin and layer (max 0.42/0.65/0.67/0.47 for met1–met4).

*Source:* `routed DEF (final)`

## 07a_detailed_routing_all_layers.png
![07a_detailed_routing_all_layers.png](../../visuals/v4_v6/07a_detailed_routing_all_layers.png)

Final detailed routing, all layers (met1 blue, met2 red, met3 green, met4 yellow).

*Source:* `final routed DEF`

## 07b_detailed_routing_met1.png
![07b_detailed_routing_met1.png](../../visuals/v4_v6/07b_detailed_routing_met1.png)

Detailed routing, met1 only (incl. power rails).

*Source:* `final routed DEF`

## 07c_detailed_routing_met2.png
![07c_detailed_routing_met2.png](../../visuals/v4_v6/07c_detailed_routing_met2.png)

Detailed routing, met2 only (vertical).

*Source:* `final routed DEF`

## 07d_detailed_routing_met3.png
![07d_detailed_routing_met3.png](../../visuals/v4_v6/07d_detailed_routing_met3.png)

Detailed routing, met3 only (horizontal).

*Source:* `final routed DEF`

## 07e_detailed_routing_met4.png
![07e_detailed_routing_met4.png](../../visuals/v4_v6/07e_detailed_routing_met4.png)

Detailed routing, met4 only (vertical, straps + routes).

*Source:* `final routed DEF`

## 07f_detailed_routing_zoom_60um.png
![07f_detailed_routing_zoom_60um.png](../../visuals/v4_v6/07f_detailed_routing_zoom_60um.png)

Detailed routing zoom 60x60 µm, all layers.

*Source:* `final routed DEF`

## 08a_final_gds_full_chip.png
![08a_final_gds_full_chip.png](../../visuals/v4_v6/08a_final_gds_full_chip.png)

Final GDS, full chip in KLayout (met1–met4 with sky130A layer colours).

*Source:* `release/gds/omega_fusion_soc_asic.gds`

## 08b_final_gds_core_zoom_120um.png
![08b_final_gds_core_zoom_120um.png](../../visuals/v4_v6/08b_final_gds_core_zoom_120um.png)

Final GDS core zoom 120x120 µm.

*Source:* `same`

## 08c_final_gds_interconnect_30um.png
![08c_final_gds_interconnect_30um.png](../../visuals/v4_v6/08c_final_gds_interconnect_30um.png)

Final GDS interconnect detail 30x30 µm (li1, mcon, met1, via, met2, via2, met3).

*Source:* `same`

## 08d_final_gds_cell_level_22um.png
![08d_final_gds_cell_level_22um.png](../../visuals/v4_v6/08d_final_gds_cell_level_22um.png)

Final GDS cell level 22x22 µm (diff, poly, licon, li1, mcon, met1).

*Source:* `same`

## 09a_caravel_wrapper_pdn_mprj.png
![09a_caravel_wrapper_pdn_mprj.png](../../visuals/v4_v6/09a_caravel_wrapper_pdn_mprj.png)

Caravel wrapper 2920x3520 µm with macro mprj outlined (560,860); wrapper met4/met5 power grid; PSM: all 8 nets connected.

*Source:* `wrapper run WRAP_FINAL_PDN`

## 09b_caravel_wrapper_routed_overview.png
![09b_caravel_wrapper_routed_overview.png](../../visuals/v4_v6/09b_caravel_wrapper_routed_overview.png)

Wrapper after detailed routing (route DRC 0).

*Source:* `wrapper run WRAP_FINAL_PNR`

## 09c_caravel_macro_corner_power_connection.png
![09c_caravel_macro_corner_power_connection.png](../../visuals/v4_v6/09c_caravel_macro_corner_power_connection.png)

Macro corner: wrapper power stripes crossing the macro boundary.

*Source:* `wrapper run WRAP_FINAL_PDN`

## 10_signoff_evidence.png
![10_signoff_evidence.png](../../visuals/v4_v6/10_signoff_evidence.png)

Signoff evidence: PASS/FAIL/UNVERIFIED table, post-route STA slack map (9 corners), violations still failing, Liberty-only check.

*Source:* `reports/signoff_v6/*`


# Charts (`charts/`, data in `charts/data/`)

* `charts/01_area_by_stage.png` (+ SVG)

* `charts/02_instances_by_stage.png` (+ SVG)

* `charts/03_setup_slack_by_corner.png` (+ SVG)

* `charts/04_hold_slack_by_corner.png` (+ SVG)

* `charts/04b_hold_violations.png` (+ SVG)

* `charts/05_slew_violations.png` (+ SVG)

* `charts/06_cap_violations.png` (+ SVG)

* `charts/07_fanout_violations_final.png` (+ SVG)

* `charts/08_clock_skew_by_corner.png` (+ SVG)

* `charts/09_buffers_by_stage.png` (+ SVG)

* `charts/10_11_routing_resources_congestion.png` (+ SVG)

* `charts/12_antenna_evolution.png` (+ SVG)

* `charts/13_antenna_variants_11_vs_12.png` (+ SVG)

* `charts/14_wirelength.png` (+ SVG)

* `charts/15_drc_lvs_antenna_final.png` (+ SVG)

* `charts/16_power_irdrop.png` (+ SVG)

* `charts/17_ppa_summary.png` (+ SVG)

## Caravel wrapper with the V7 macro (`visuals/v8_wrapper/`, 2026-11-16)
Rendered by `physical_design/scripts/vis_wrapper_v8.py` from LibreLane run `W8_A` (macro `FS` at (560, 860)): `w8_01` floorplan and pin placement (pins parsed from DEF), `w8_02` PDN (KLayout), `w8_03` placement, `w8_04` signal routing (special nets hidden). Charts `final_*` come from `physical_design/scripts/plot_portfolio.py`.
