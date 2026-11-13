# Release assets (physical release)

Large physical files are **not** stored in git. They are distributed as GitHub Release assets (all files below are gzip-compressed; the SHA-256 is of the `.gz` file as uploaded). **Status: prepared locally on 2026-11-13; they are not published until the release exists on GitHub** — this file will not claim otherwise.

Local archive of the assets: `~/omega-fusion-tapeout/github_release_assets/` (engineering archive, outside the repository).

| Asset | Size | SHA-256 (gz) | Content |
|---|---:|---|---|
| `omega_fusion_soc_asic_V6.gds.gz` | 27.5 MB | `e6a7839ba3107e80b0700732b9732ad837f75cd688d12d04f39f72830abb6914` | V6 baseline GDSII |
| `omega_fusion_soc_asic_V6.max.spef.gz` | 23.2 MB | `61b2013dd3d5b36420cc7f0f76f6a61987453645da04e441134f579c3277e224` | SPEF max corner, V6 layout |
| `omega_fusion_soc_asic_V6.min.spef.gz` | 21.2 MB | `4f7ed7916fdbcac6d167638626507e9b4b23c8bbb984c617a78e56903863bb8f` | SPEF min corner, V6 layout |
| `omega_fusion_soc_asic_V6.nom.spef.gz` | 21.6 MB | `9e2ef60bc67ba6cb5b39811196d5a39b5e004d723b04ec07ca51cb7f17066e39` | SPEF nom corner, V6 layout |
| `omega_fusion_soc_asic_V7.def.gz` | 11.7 MB | `091515f21b99b8f3c025f17094103f016973646699918bbb7ba38ea1f1c7bcab` | V7 final routed DEF |
| `omega_fusion_soc_asic_V7.gds.gz` | 27.7 MB | `eb1555e44647a201c196b5369b36937d294f938f130b0f842ecbe8f19347b76d` | V7 final GDSII (Magic stream-out; sha256 of the decompressed GDS: 275337f0…) |
| `omega_fusion_soc_asic_V7.klayout.gds.gz` | 9.4 MB | `dda3936fc7b95b78cc6a2cbcee30715a9f2e2fc3a870f46575639f96990c9049` | V7 KLayout stream-out (XOR-clean vs the Magic GDS) |
| `omega_fusion_soc_asic_V7.max.spef.gz` | 23.3 MB | `e0c03c475d4534d130460fd589ce01510800a900018aae6ba13e2b918764a650` | SPEF max corner, V7 layout |
| `omega_fusion_soc_asic_V7.min.spef.gz` | 21.2 MB | `93efada504a3135c4fd95db9e9f1cb4a77b54e75e12b7f4cceabda5aa23777d0` | SPEF min corner, V7 layout |
| `omega_fusion_soc_asic_V7.nom.spef.gz` | 21.7 MB | `63fa4e7dc2a9d2dd7f847525173988e235c08cce25d1a5d6f616a1d93692589d` | SPEF nom corner, V7 layout |

## Verify

```bash
shasum -a 256 -c SHA256SUMS.txt   # in the directory with the downloaded assets (SHA256SUMS.txt is attached to the release)
```

## What stays in git
`deliverables/lef/*.gz`, `deliverables/netlist/*.gz`, `deliverables/timing/*.sdc` (V6) and `deliverables/v7/{lef,netlist,timing}` (V7), with `SHA256SUMS.txt` (files in git) and `SHA256SUMS.original.txt` (hashes of the uncompressed originals in the engineering archive).

## Notice
The layouts include standard cells of SkyWater SKY130 `sky130_fd_sc_hd` (Apache-2.0); see `docs/LICENSES_AND_SECURITY_AUDIT.md`. The license of the original OMEGA-Fusion sources is pending the owner’s decision.
