# deliverables/

Small physical deliverables kept in git (gzip). **GDS, SPEF, KLayout GDS and DEF are GitHub Release assets** — see `../docs/RELEASE_ASSETS.md`.

* `lef/`, `netlist/`, `timing/` — **V6 baseline** (`OMEGA_V6_ECO2` + `OMEGA_V6_SIGNOFF5`). `SHA256SUMS.txt` covers the files in git; `SHA256SUMS.original.txt` the uncompressed originals; `SHA256SUMS.release_assets.txt` the release assets.
* `v7/` — **V7 candidate** (`OMEGA_V15_RT`), same structure; netlists: `nl.v`/`pnl.v` (with fill and taps, used for LVS) and `*.nofill.v` (for hierarchical integration/STA). Lineage and consistency: `../docs/results/RELEASE_CANDIDATE.md`.
* Verify: `( cd deliverables && shasum -a 256 -c SHA256SUMS.txt ) && ( cd deliverables/v7 && shasum -a 256 -c SHA256SUMS.txt )`.
