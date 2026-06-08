# Training

Per-dataset training scaffolding lives under `training/configs/<name>_v<n>/`, matching the per-dataset layout used elsewhere in the repository.

## Available datasets

### radar_dataset_v1

Compact encoder-only transformer for the radar training set (D3.3 / D3.1).

Configs:

- `configs/radar_dataset_v1/transformer_biomass.yaml`
- `configs/radar_dataset_v1/transformer_material_primary.yaml`

Scripts (under `scripts/radar_dataset_v1/`):

- `export_dataset.py`
- `build_release.py`
- `train_transformer.py`

Optional shell launcher:

- `run_radar_transformer.sh`

Workflow:

```bash
# Export a clean subset
python scripts/radar_dataset_v1/export_dataset.py --subset core --output-dir build/radar_core_v1

# Or build the full local release package
python scripts/radar_dataset_v1/build_release.py

# Train the biomass detector
python scripts/radar_dataset_v1/train_transformer.py \
    --config training/configs/radar_dataset_v1/transformer_biomass.yaml

# Train the coarse material classifier
python scripts/radar_dataset_v1/train_transformer.py \
    --config training/configs/radar_dataset_v1/transformer_material_primary.yaml
```

Or use the shell launcher:

```bash
training/run_radar_transformer.sh biomass
training/run_radar_transformer.sh material
training/run_radar_transformer.sh both
```

### radar_dataset_from_multidetektor_measurement

Compact transformer and sklearn baseline for the fixed-geometry radar lab session (D4.3), paired with numbered sample photographs.

Configs:

- `configs/radar_dataset_from_multidetektor_measurement/baseline.yaml`
- `configs/radar_dataset_from_multidetektor_measurement/transformer_label_category.yaml` (primary)
- `configs/radar_dataset_from_multidetektor_measurement/transformer_label_name.yaml` (17-class fine-grained)
- `configs/radar_dataset_from_multidetektor_measurement/transformer_label_contamination.yaml` (binary)

Scripts (under `scripts/radar_dataset_from_multidetektor_measurement/`):

- `ingest_raw_txt.py`, `build_sample_mapping.py`, `export_dataset.py` - build the release
- `build_foto_catalog.py` - catalogue sample photographs into `photos/` plus `aux/foto_catalog.csv`
- `build_samples.py` - GitHub-safe previews
- `train_classifier.py` - baseline plus transformer
- `infer.py` - CLI inference on raw `.txt` frames

Workflow:

```bash
NAME=radar_dataset_from_multidetektor_measurement

# End-to-end build
python scripts/$NAME/ingest_raw_txt.py
python scripts/$NAME/build_sample_mapping.py
python scripts/$NAME/export_dataset.py
python scripts/$NAME/build_foto_catalog.py
python scripts/$NAME/build_samples.py

# Train via a config (recommended) — CLI flags override config values
python scripts/$NAME/train_classifier.py \
    --config training/configs/$NAME/transformer_label_category.yaml

# Infer
python scripts/$NAME/infer.py \
    --model models/$NAME/transformer_label_category.pt \
    --input data/multidetektor/meranie_23_04/2026-04-23_13-14-01.859/FD/
```

`train_classifier.py` reads the YAML config and resolves settings as `CLI flag > config value > built-in default`, so the configs in `configs/$NAME/` drive the model family, target, transformer architecture, and augmentation.

### video_segmentation_dataset_v1

RF-DETR Seg training template for the local full image-segmentation dataset prepared from private CVAT exports.

Configs:

- `configs/video_segmentation_dataset_v1/rfdetr_seg_all_classes.yaml`
- `configs/video_segmentation_dataset_v1/rfdetr_seg_single_material.yaml`

Scripts:

- `../scripts/video_segmentation_dataset_v1/train_rfdetr.py`
- `run_rfdetr_seg.sh`

Recommended workflow:

1. Prepare a local COCO dataset that matches the input contract in [../docs/datasets/video_segmentation_dataset_v1/input-spec.md](../docs/datasets/video_segmentation_dataset_v1/input-spec.md).

Expected layout:

```bash
<dataset_root>/
  train/
    _annotations.coco.json
    *.jpg
  valid/
    _annotations.coco.json
    *.jpg
  test/
    _annotations.coco.json
    *.jpg
```

2. Update the config so `dataset_dir` points to your local COCO dataset.

3. Validate the RF-DETR Seg config without starting training:

```bash
python scripts/video_segmentation_dataset_v1/train_rfdetr.py \
  --config training/configs/video_segmentation_dataset_v1/rfdetr_seg_all_classes.yaml \
  --dry-run
```

4. Fine-tune RF-DETR Seg once the runtime is prepared:

```bash
pip install "rfdetr[train,loggers]"
python scripts/video_segmentation_dataset_v1/train_rfdetr.py \
  --config training/configs/video_segmentation_dataset_v1/rfdetr_seg_all_classes.yaml
```

Or use the shell launcher:

```bash
training/run_rfdetr_seg.sh all --dry-run
training/run_rfdetr_seg.sh single
```

## Model Choice

The default model across radar datasets is a compact encoder-only transformer with optional patch embedding. Multidetector also ships a scikit-learn baseline (LogReg / RandomForest on handcrafted plus flattened features) for quick sanity checks without PyTorch.

For image segmentation, the public template uses `RFDETRSegSmall` by default because it accepts the COCO instance-segmentation layout directly and provides a modern transformer-based baseline.

This is a deliberate compromise:

- closer to the multivariate time-series transformer literature than hand-crafted feature models alone
- simpler and more appropriate for short radar sequences than a large long-horizon forecasting architecture
- easy to reproduce and deploy

## Runtime Notes

- `scripts/*/train_*.py` and `scripts/radar_dataset_from_multidetektor_measurement/infer.py` require PyTorch. The baseline path (`--model baseline`) requires only scikit-learn plus joblib.
- The exporter scripts do not require PyTorch.
- RF-DETR Seg requires `rfdetr[train,loggers]` in addition to the base training environment.

## Suggested Install

```bash
# PyTorch from the official selector (CPU / CUDA):
#   https://pytorch.org/get-started/locally/

pip install -r requirements-train.txt
pip install "rfdetr[train,loggers]"
```

## Segmentation Notes

- The raw image ZIP bundles and the full local dataset are not intended for GitHub publication.
- A tiny public COCO preview is available in `../samples/video_segmentation_dataset_v1/all_classes_mini_coco/` for schema inspection and dry runs only.
- RF-DETR accepts COCO layout directly, so the only required public contract is the `train/valid/test` COCO structure.
