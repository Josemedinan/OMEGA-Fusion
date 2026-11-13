# common env for release scripts
export OF=$HOME/omega-fusion-tapeout
export RUNS=$OF/openlane/omega_fusion_soc_v2/runs
export PDKV=8afc8346a57fe1ab7934ba5a6056ea8b43078e71
export PDK=$HOME/.ciel/ciel/sky130/versions/$PDKV/sky130A
export IMG=ghcr.io/librelane/librelane:3.0.11
# run a command inside LibreLane image (openroad/klayout/magic/netgen on PATH); $HOME mounted at same path
lld() { docker run --rm --entrypoint "" -v $HOME:$HOME -w "$PWD" -e HOME=$HOME $IMG "$@"; }
