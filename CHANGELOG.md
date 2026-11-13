# Changelog

## Unreleased — publication preparation (2026-11-13)
* Open `net2070` (V7) analysed: SDC rule, 33 % of cap limit, 38 % of slew limit, +76 ns setup / +5 ns hold slack through it; not changed (`docs/results/NET2070_ANALYSIS.md`).
* Release candidate selection and file lineage (`docs/results/RELEASE_CANDIDATE.md`); V7 images for every phase with version in the title (`visuals/v7/`); V6-vs-V7 charts 19/20; 18-slide V7 presentation; wrapper PDN stage re-run with the V7 macro (PASS, 8/8 nets).
* New: `docs/INDUSTRIAL_APPLICATIONS.md`, `docs/LICENSES_AND_SECURITY_AUDIT.md`, `docs/RELEASE_ASSETS.md`, `docs/results/PENDING_VERIFICATION.md`, `scripts/pending/`.
* Moved: GDS `.gz` out of git (release assets); legacy images to `visuals/v4_v6/`; V6 deck to `docs/results/archive_v6/`.
* Git history recreated before the first publication (the first local commit contained the GDS blobs); the old commit is kept as a bundle in the engineering archive.

## V7 candidate (2026-11-13)
* V7 = V6 + 9 ECO/re-route iterations (`docs/results/V7_ECO_REPORT.md`): slew 158 → 0, cap 23 → 0, fanout 83 → 1 net, hold +0.017 → +0.102 ns, setup +52.0 → +54.7 ns; DRC (Magic/KLayout/route), LVS, XOR, antenna all clean; gate-level simulation PASS. One net still above the fanout limit. TAPEOUT_READY remains NO.
* New: `deliverables/v7/`, `physical_design/reports/{v7,iterations}/`, `charts/18_eco_iterations_v6_to_v7.*`, `visuals/v7/`, ECO scripts `eco_v7*.tcl` … `eco_v15.tcl`.
* V6 deliverables and reports are unchanged.

## GitHub-ready layout (2026-11-12)
* RTL reorganized into `rtl/{cpu,accelerators,soc}`; scripts and configs updated; RTL regression and zero-delay gate-level simulation re-run: PASS.
* Added compressed deliverables with SHA-256 manifests, cleanup manifest, reproduction guide, architecture diagram, visual gallery with errata, fixed chart title overlap (10_11).
* Corrected `FINAL_STATUS.json`: reproducibility is PARTIAL (physical flow not re-run from the new layout).

## V6 physical baseline (2026-11-12)
* ECO rounds with real SPEF (resizing + hold repair); setup/hold ≥ 0 in 9 corners; DRC/LVS/antenna clean on the macro; slew 12,908 → 158. TAPEOUT_READY = NO (slew/cap/fanout, wrapper DRC/LVS/antenna, EQY, SDF, pre-check).

## V4 / V3
* SDC v4 (limits, driving cell, load, uncertainty, derate, `rst_n` constrained); V3: reset-tree antenna fix; see `docs/physical_design/PHYSICAL_DESIGN_REPORT.md`.

## V2 series
* Synthesis → floorplan → PDN → GPL → CTS → GRT checkpoints (kept untouched).

## v0.2 / v0.3
* Accelerator with folded/parallel MAC, MMIO, DMA loader, RV32I-subset demo SoC; programmable-IMEM ASIC top.
