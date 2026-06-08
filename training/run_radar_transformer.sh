#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DEFAULT_BIOMASS_CONFIG="${REPO_ROOT}/training/configs/radar_dataset_v1/transformer_biomass.yaml"
DEFAULT_MATERIAL_CONFIG="${REPO_ROOT}/training/configs/radar_dataset_v1/transformer_material_primary.yaml"
TRAIN_SCRIPT="${REPO_ROOT}/scripts/radar_dataset_v1/train_transformer.py"

usage() {
  cat <<'EOF'
Usage:
  training/run_radar_transformer.sh biomass
  training/run_radar_transformer.sh material
  training/run_radar_transformer.sh both
  training/run_radar_transformer.sh --config /path/to/config.yaml

Modes:
  biomass   Use training/configs/radar_dataset_v1/transformer_biomass.yaml
  material  Use training/configs/radar_dataset_v1/transformer_material_primary.yaml
  both      Run biomass first, then material

Examples:
  training/run_radar_transformer.sh biomass
  training/run_radar_transformer.sh material
  training/run_radar_transformer.sh both
  training/run_radar_transformer.sh --config /data/custom_radar_config.yaml

Notes:
  - Export the radar dataset first, or update dataset_dir in the YAML config.
  - Training requires PyTorch in the current environment.
EOF
}

run_config() {
  local config_path="$1"
  if [[ ! -f "${config_path}" ]]; then
    echo "Config file not found: ${config_path}" >&2
    exit 1
  fi
  echo "Running radar training with config: ${config_path}"
  python "${TRAIN_SCRIPT}" --config "${config_path}"
}

if [[ $# -eq 0 ]]; then
  usage
  exit 1
fi

MODE=""
CONFIG_PATH=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    biomass)
      MODE="biomass"
      shift
      ;;
    material)
      MODE="material"
      shift
      ;;
    both)
      MODE="both"
      shift
      ;;
    --config)
      if [[ $# -lt 2 ]]; then
        echo "Missing value for --config" >&2
        exit 1
      fi
      CONFIG_PATH="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

cd "${REPO_ROOT}"

if [[ -n "${CONFIG_PATH}" ]]; then
  run_config "${CONFIG_PATH}"
  exit 0
fi

case "${MODE}" in
  biomass)
    run_config "${DEFAULT_BIOMASS_CONFIG}"
    ;;
  material)
    run_config "${DEFAULT_MATERIAL_CONFIG}"
    ;;
  both)
    run_config "${DEFAULT_BIOMASS_CONFIG}"
    run_config "${DEFAULT_MATERIAL_CONFIG}"
    ;;
  *)
    echo "Choose 'biomass', 'material', 'both', or provide --config." >&2
    usage
    exit 1
    ;;
esac
