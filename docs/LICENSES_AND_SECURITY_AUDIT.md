# Licenses and security audit (2026-11-13)

## 1. License inventory — what is verified and what is not
| Component | Origin | License evidence | Status |
|---|---|---|---|
| `rtl/**`, `tb/**`, `firmware/**`, `scripts/**` (except generated files), `caravel/rtl/omega_wb_bridge.v`, `caravel/rtl/omega_fusion_soc_asic_bb.v`, `physical_design/**` (configs, SDC, ECO/flow scripts, reports), `docs/**`, `charts/**`, `visuals/**` | Written for this project by the repository owner (git author `Josemedinan`), with AI assistance in the engineering sessions | No per-file license headers; the project license is declared by `LICENSE` + `NOTICE` + `README.md` | **Apache-2.0, chosen by the repository owner on 2026-11-13** (rights to license the original code rest with the owner; AI assistance was used in writing it) |
| `caravel/rtl/user_project_wrapper.v`, `defines.v`, `user_defines.v`, `uprj_netlists.v` | Efabless `caravel_user_project` template (the first two modified for OMEGA) | SPDX header `Apache-2.0`, "Copyright 2020 Efabless Corporation" in the files | Apache-2.0 **must be kept** for these files (and for our modifications of them) |
| `caravel/openlane/fixed_dont_change/*`, `base_user_project_wrapper.sdc`, `pin_order.cfg` | Same template | `fixed_wrapper_cfgs.tcl` / `default_wrapper_cfgs.tcl` carry the same Efabless Apache-2.0 header; the `.def`, `.cells` and `.sdc` files carry none but come from the same repository | Treated as Apache-2.0 (Efabless); attribution required |
| `LICENSE` | Apache-2.0 text (first copied from the Efabless template repository) | Now also the declared license of the original OMEGA-Fusion sources (owner's decision) | Apache-2.0 |
| SKY130A PDK / `sky130_fd_sc_hd` | SkyWater / Google; fetched by `ciel`, **not** vendored in this repository | Apache-2.0 (upstream) | Not redistributed as files. The released GDS/netlists/LEF contain or instantiate standard cells of that library: keep the attribution (NOTICE below) |
| OpenROAD, Yosys, Magic, KLayout, Netgen, LibreLane, Verilator, Icarus | Used as tools; not redistributed | various open-source licenses | Nothing to redistribute; versions listed in `docs/methodology/tool_versions_container.txt` |
| Python/matplotlib | Used to generate figures | not included | — |
| Images/charts/PDF | Generated from project files by the scripts in this repository | Apache-2.0 with the rest of the original material | Apache-2.0 |

**The owner chose Apache-2.0 for the original code on 2026-11-13**; I did not assume it before that.

## 2. Notice to carry with the physical release
"Layout, netlists and LEF include standard cells from SkyWater SKY130 `sky130_fd_sc_hd` (Apache License 2.0, https://github.com/google/skywater-pdk). Caravel wrapper files are © Efabless Corporation, Apache License 2.0."

## 3. Decision (closed)
Apache-2.0 for the original OMEGA-Fusion sources. It is consistent with the Efabless template files, which must stay Apache-2.0. Open shuttle programs based on that template have required Apache-2.0-compatible open-source submissions — verify the current program rules before submitting.

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
