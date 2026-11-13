#!/usr/bin/env bash
# UNTESTED. Formal equivalence RTL vs. synthesized netlist with Yosys EQY through LibreLane (RUN_EQY).
# This checks RTL against the post-SYNTHESIS netlist only; the ECO/PnR edits (buffers, resizing, antenna diodes) are not covered by it.
# For post-route vs post-synthesis use a netlist-level equivalence (e.g. Yosys `equiv_*` or Conformal/Formality) — not provided.
set -euo pipefail
: "${PDK_ROOT:?}"; REPO=$(cd "$(dirname "$0")/../.." && pwd); mkdir -p pending_results; cd "$REPO/physical_design/config"
librelane --dockerized -m "$REPO" --pdk-root "$PDK_ROOT" --pdk sky130A --run-tag EQY_V7 --to Yosys.EQY --condensed config_v5.json -c RUN_EQY=true 2>&1 | tee "$OLDPWD/pending_results/eqy.log"
