# Sourced by the run_*.sh scripts. Defines file lists relative to the repo root.
cd "$(dirname "${BASH_SOURCE[0]}")/.."
ACC=(rtl/accelerators/omega_fusion_mac.sv rtl/accelerators/omega_fusion_mac_folded.sv rtl/accelerators/omega_fusion.sv)
CPU=(rtl/cpu/omega_rv32_controller.sv)
SOC_DEMO=(rtl/soc/omega_fusion_soc_demo.sv)
SOC_ASIC=(rtl/soc/omega_fusion_soc_asic.sv)
BUILD=${BUILD:-build}; mkdir -p "$BUILD"
need() { command -v "$1" >/dev/null || { echo "ERROR: $1 not found"; exit 1; }; }
