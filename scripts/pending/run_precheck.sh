#!/usr/bin/env bash
# UNTESTED. Efabless/ChipIgnite shuttle pre-check on a full Caravel user project (needs the final wrapper GDS, so it can only follow run_wrapper_signoff.sh).
# Follow the CURRENT instructions of https://github.com/efabless/mpw_precheck : it runs in Docker against a `caravel_user_project` checkout whose gds/user_project_wrapper.gds is the signed-off wrapper.
echo "Not automated here: clone efabless/caravel_user_project, copy the wrapper GDS/LEF/netlists, then run make precheck per the program's current documentation."
exit 1
