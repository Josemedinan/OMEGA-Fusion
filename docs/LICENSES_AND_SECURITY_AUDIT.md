# Licenses and security audit (2026-11-13)

## 1. License inventory — what is verified and what is not
| Component | Origin | License evidence | Status |
|---|---|---|---|
| `rtl/**`, `tb/**`, `firmware/**`, `scripts/**` (except generated files), `caravel/rtl/omega_wb_bridge.v`, `caravel/rtl/omega_fusion_soc_asic_bb.v`, `physical_design/**` (configs, SDC, ECO/flow scripts, reports), `docs/**`, `charts/**`, `visuals/**` | Written for this project by the repository owner (git author `Josemedinan`), with AI assistance in the engineering sessions | **No license header and no license decision recorded anywhere in the source tree** | **OPEN — owner's choice required.** Apache-2.0 is the natural candidate (see §3) but it has not been chosen. |
| `caravel/rtl/user_project_wrapper.v`, `defines.v`, `user_defines.v`, `uprj_netlists.v` | Efabless `caravel_user_project` template (the first two modified for OMEGA) | SPDX header `Apache-2.0`, "Copyright 2020 Efabless Corporation" in the files | Apache-2.0 **must be kept** for these files (and for our modifications of them) |
| `caravel/openlane/fixed_dont_change/*`, `base_user_project_wrapper.sdc`, `pin_order.cfg` | Same template | `fixed_wrapper_cfgs.tcl` / `default_wrapper_cfgs.tcl` carry the same Efabless Apache-2.0 header; the `.def`, `.cells` and `.sdc` files carry none but come from the same repository | Treated as Apache-2.0 (Efabless); attribution required |
| `LICENSE` | Text of Apache-2.0 copied from the template repository (`caravel_user_project`) | It is the license text of that template; it is **not** evidence that the OMEGA sources are licensed under it | Kept because the template files need it; does not decide the license of our own files |
| SKY130A PDK / `sky130_fd_sc_hd` | SkyWater / Google; fetched by `ciel`, **not** vendored in this repository | Apache-2.0 (upstream) | Not redistributed as files. The released GDS/netlists/LEF contain or instantiate standard cells of that library: keep the attribution (NOTICE below) |
| OpenROAD, Yosys, Magic, KLayout, Netgen, LibreLane, Verilator, Icarus | Used as tools; not redistributed | various open-source licenses | Nothing to redistribute; versions listed in `docs/methodology/tool_versions_container.txt` |
| Python/matplotlib | Used to generate figures | not included | — |
| Images/charts/PDF | Generated from project files by the scripts in this repository | follow the license chosen for the project | OPEN together with the first row |

**I did not assume Apache-2.0 for the original code.** The repository ships the template's `LICENSE` file only because third-party files inside it require it.

## 2. Notice to carry with the physical release
"Layout, netlists and LEF include standard cells from SkyWater SKY130 `sky130_fd_sc_hd` (Apache License 2.0, https://github.com/google/skywater-pdk). Caravel wrapper files are © Efabless Corporation, Apache License 2.0."

## 3. Decision needed from the owner (one item)
Choose the license for the original OMEGA-Fusion sources (RTL, scripts, documentation, figures). Constraints I can state from the evidence: (a) the Efabless template files must stay Apache-2.0; (b) open shuttle programs based on that template (e.g. chipIgnite) have required Apache-2.0-compatible open-source submissions — verify the current program rules before submitting; (c) Apache-2.0 for the rest would make the repository uniform. Until the owner decides, the repository states the situation in `README.md` instead of claiming a license.

## 4. Security and privacy checks performed
| Check | Result |
|---|---|
| Secrets/credentials (regex for private keys, GitHub/AWS tokens, `password`/`api key` strings) in the working tree | none found |
| Same scan over every commit | the repository has a single local commit (nothing published); none found |
| Personal data | absolute home paths replaced by `<HOME>`, e-mail address removed from all text files; git author is the GitHub account name only |
| Proprietary files | none: no EDA vendor tools or libraries, no PDK files, no foundry NDA material |
| Binary/large files | only the gzip'd physical deliverables (≤ 28 MB each) and a PDF; handled as release assets, see `docs/RELEASE_ASSETS.md` |
| `.gitignore` | excludes build output, run databases (`runs/`, `*.odb`, `*.def`, `*.spef`, `*.sdf`, `*.gds`); the template `.def` files under `caravel/openlane/fixed_dont_change/` are explicitly kept |
| GitHub workflow | `.github/workflows/rtl.yml` runs only the RTL regression and checksums; it uses `actions/checkout` and `apt` only; **it has not been executed on GitHub yet** |
