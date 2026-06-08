#!/usr/bin/env python3
"""Sample RF-DETR Seg fine-tuning script for local WasteR segmentation datasets."""

from __future__ import annotations

import argparse
import importlib
import json
import random
from pathlib import Path
from typing import Any

import numpy as np
import yaml


MODEL_CLASS_NAMES = {
    "nano": "RFDETRSegNano",
    "small": "RFDETRSegSmall",
    "medium": "RFDETRSegMedium",
    "large": "RFDETRSegLarge",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True, help="YAML config for RF-DETR Seg fine-tuning.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate the config and dataset layout without launching training.",
    )
    return parser.parse_args()


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def ensure_dataset_layout(dataset_dir: Path) -> None:
    placeholder_text = str(dataset_dir)
    if "<" in placeholder_text or placeholder_text.startswith("/path/to/"):
        raise SystemExit(
            "The config still contains a placeholder dataset_dir. Replace it with the path to your local "
            "COCO segmentation dataset before running RF-DETR training."
        )
    missing = []
    for split in ("train", "valid", "test"):
        split_dir = dataset_dir / split
        if not split_dir.exists():
            missing.append(str(split_dir))
            continue
        annotation_file = split_dir / "_annotations.coco.json"
        if not annotation_file.exists():
            missing.append(str(annotation_file))
    if missing:
        raise SystemExit(
            "Dataset layout is incomplete. RF-DETR expects train/valid/test directories with "
            f"_annotations.coco.json files. Missing: {missing}"
        )


def ensure_rfdetr():
    try:
        return importlib.import_module("rfdetr")
    except ImportError as exc:
        raise SystemExit(
            "RF-DETR is not installed in this environment. Install the package with "
            '`pip install "rfdetr[train,loggers]"` and rerun the script.'
        ) from exc


def resolve_model(rfdetr_module: Any, model_size: str) -> Any:
    if model_size not in MODEL_CLASS_NAMES:
        raise SystemExit(
            f"Unsupported model size '{model_size}'. Choose one of: {sorted(MODEL_CLASS_NAMES)}."
        )
    class_name = MODEL_CLASS_NAMES[model_size]
    try:
        model_cls = getattr(rfdetr_module, class_name)
    except AttributeError as exc:
        raise SystemExit(
            f"The installed rfdetr package does not expose {class_name}. "
            "Upgrade the package or switch to a supported segmentation model size."
        ) from exc
    return model_cls()


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
    except ImportError:
        return
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def build_train_kwargs(config: dict[str, Any]) -> dict[str, Any]:
    train_kwargs = {
        "dataset_dir": str(Path(config["dataset_dir"])),
        "output_dir": str(Path(config["output_dir"])),
        "epochs": int(config.get("epochs", 100)),
        "batch_size": int(config.get("batch_size", 4)),
        "grad_accum_steps": int(config.get("grad_accum_steps", 4)),
        "lr": float(config.get("lr", 1e-4)),
        "lr_encoder": float(config.get("lr_encoder", 1.5e-4)),
        "resolution": int(config.get("resolution", 384)),
        "weight_decay": float(config.get("weight_decay", 1e-4)),
        "device": str(config.get("device", "cuda")),
        "notes": config.get("notes", "WasteR segmentation sample training run"),
    }
    optional_keys = (
        "num_workers",
        "early_stopping",
        "patience",
        "checkpoint_interval",
        "loggers",
    )
    for key in optional_keys:
        if key in config and config[key] is not None:
            train_kwargs[key] = config[key]
    return train_kwargs


def main() -> None:
    args = parse_args()
    config = load_config(args.config)

    dataset_dir = Path(config["dataset_dir"])
    ensure_dataset_layout(dataset_dir)

    seed = int(config.get("seed", 42))
    set_seed(seed)

    resolved = {
        "model_size": config.get("model_size", "small"),
        "dataset_dir": str(dataset_dir),
        "output_dir": str(Path(config.get("output_dir", "runs/rfdetr_seg"))),
        "seed": seed,
        "dry_run": bool(args.dry_run),
    }
    print(json.dumps(resolved, indent=2))

    if args.dry_run or bool(config.get("dry_run", False)):
        print("Dry run completed. Dataset layout and training config look valid.")
        return

    rfdetr_module = ensure_rfdetr()
    model = resolve_model(rfdetr_module, str(config.get("model_size", "small")).lower())
    train_kwargs = build_train_kwargs(config)
    model.train(**train_kwargs)


if __name__ == "__main__":
    main()
