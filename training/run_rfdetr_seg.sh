#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DEFAULT_ALL_CONFIG="${REPO_ROOT}/training/configs/video_segmentation_dataset_v1/rfdetr_seg_all_classes.yaml"
DEFAULT_SINGLE_CONFIG="${REPO_ROOT}/training/configs/video_segmentation_dataset_v1/rfdetr_seg_single_material.yaml"
TRAIN_SCRIPT="${REPO_ROOT}/scripts/video_segmentation_dataset_v1/train_rfdetr.py"

usage() {
  cat <<'EOF'
Usage:
  training/run_rfdetr_seg.sh all [--dry-run]
  training/run_rfdetr_seg.sh single [--dry-run]
  training/run_rfdetr_seg.sh --config /path/to/config.yaml [--dry-run]

Modes:
  all       Use training/configs/video_segmentation_dataset_v1/rfdetr_seg_all_classes.yaml
  single    Use training/configs/video_segmentation_dataset_v1/rfdetr_seg_single_material.yaml

Examples:
  training/run_rfdetr_seg.sh all --dry-run
  training/run_rfdetr_seg.sh single
  training/run_rfdetr_seg.sh --config /data/my_seg_config.yaml --dry-run

Notes:
  - Update dataset_dir inside the YAML config before running.
  - RF-DETR training dependencies are installed with:
      pip install "rfdetr[train,loggers]"
EOF
}

if [[ $# -eq 0 ]]; then
  usage
  exit 1
fi

CONFIG_PATH=""
DRY_RUN_ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    all)
      CONFIG_PATH="${DEFAULT_ALL_CONFIG}"
      shift
      ;;
    single)
      CONFIG_PATH="${DEFAULT_SINGLE_CONFIG}"
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
    --dry-run)
      DRY_RUN_ARGS+=(--dry-run)
      shift
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

if [[ -z "${CONFIG_PATH}" ]]; then
  echo "Choose 'all', 'single', or provide --config." >&2
  usage
  exit 1
fi

if [[ ! -f "${CONFIG_PATH}" ]]; then
  echo "Config file not found: ${CONFIG_PATH}" >&2
  exit 1
fi

cd "${REPO_ROOT}"
python "${TRAIN_SCRIPT}" --config "${CONFIG_PATH}" "${DRY_RUN_ARGS[@]}"
