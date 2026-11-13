#!/usr/bin/env bash
# Independent post-route STA of the final ODB, 9 PVT/RC corners, flow limits + Liberty-only limits.
# usage: run_sta_all.sh <final.odb> <rcx_dir> <outdir>
set -u; source "$(dirname "$0")/env.sh"
ODB=$1; RCX=$2; OUT=$3; mkdir -p "$OUT"
SDC=$OF/openlane/omega_fusion_soc_v2/soc_constraint_omega_v4.sdc
SDCL=$OF/openlane/omega_fusion_soc_v2/soc_constraint_omega_v4_liberty_only.sdc
for rc in nom min max; do for pvt in tt_025C_1v80 ss_100C_1v60 ff_n40C_1v95; do
  tag=${rc}_${pvt}
  for variant in flow libonly; do
    case $tag in max_*|nom_ss*) ;; *) [ $variant = libonly ] && continue;; esac
    [ -f "$OUT/${tag}_${variant}.summary.txt" ] && continue
    s=$SDC; [ $variant = libonly ] && s=$SDCL
    lld sh -c "PDK=$PDK ODB=$ODB SDC=$s SPEF=$RCX/$rc/omega_fusion_soc_asic.$rc.spef LIBC=$pvt TLEF=$rc OUT=$OUT TAG=${tag}_${variant} openroad -exit $OF/release/scripts/sta_final.tcl" > "$OUT/${tag}_${variant}.log" 2>&1
  done
done; done
echo ALLDONE > "$OUT/ALLDONE"
