# Training

This folder contains the first public modeling scaffold for radar-based waste recognition.

The goal is not to publish a final benchmark yet, but to make the release reproducible:

- export public-ready radar tensors from the current raw workbook and curated mappings
- train a compact transformer baseline on the exported data
- save enough metadata to rerun the experiment later

## Files

- `configs/radar_transformer_biomass.yaml`
- `configs/radar_transformer_material_primary.yaml`
- `../scripts/export_radar_dataset.py`
- `../scripts/build_radar_release.py`
- `../scripts/train_radar_transformer.py`

## Recommended Workflow

1. Export a clean subset:

```bash
python scripts/export_radar_dataset.py \
  --subset core \
  --output-dir build/radar_core_v1
```

Or build the full local release package:

```bash
python scripts/build_radar_release.py
```

2. Train the biomass detector:

```bash
python scripts/train_radar_transformer.py \
  --config training/configs/radar_transformer_biomass.yaml
```

3. Train the coarse material classifier:

```bash
python scripts/train_radar_transformer.py \
  --config training/configs/radar_transformer_material_primary.yaml
```

## Model Choice

The default model is a compact encoder-only transformer with optional patch embedding.

This is a deliberate compromise:

- closer to the multivariate time series transformer literature than hand-crafted feature models
- simpler and more appropriate for short radar sequences than a large long-horizon forecasting architecture
- easy to reproduce and deploy

## Runtime Notes

- The current environment in this workspace does not have `torch` installed, so training was not executed here.
- The scripts are written to be reproducible once PyTorch is installed.
- The exporter script does not require PyTorch.

## Suggested Install

Install PyTorch from the official selector for your CPU or CUDA environment:

- https://pytorch.org/get-started/locally/

Then install the remaining Python dependencies:

```bash
pip install -r requirements-train.txt
```
