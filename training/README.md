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

### multidetector_dataset_v1

Compact transformer and sklearn baseline for the fixed-geometry radar lab session (D4.3).

Configs:

- `configs/multidetector_dataset_v1/baseline.yaml`
- `configs/multidetector_dataset_v1/transformer_label_category.yaml` (primary)
- `configs/multidetector_dataset_v1/transformer_label_name.yaml` (17-class fine-grained)
- `configs/multidetector_dataset_v1/transformer_label_contamination.yaml` (binary)

Scripts (under `scripts/multidetector_dataset_v1/`):

- `ingest_raw_txt.py`, `build_sample_mapping.py`, `export_dataset.py` — build the release
- `extract_as7265x.py`, `build_foto_manifest.py` — auxiliary modalities
- `build_samples.py` — GitHub-safe previews
- `train_classifier.py` — baseline + transformer
- `infer.py` — CLI inference on raw `.txt` frames

Workflow:

```bash
# End-to-end build
python scripts/multidetector_dataset_v1/ingest_raw_txt.py
python scripts/multidetector_dataset_v1/build_sample_mapping.py
python scripts/multidetector_dataset_v1/export_dataset.py
python scripts/multidetector_dataset_v1/extract_as7265x.py
python scripts/multidetector_dataset_v1/build_foto_manifest.py
python scripts/multidetector_dataset_v1/build_samples.py

# Train + infer
python scripts/multidetector_dataset_v1/train_classifier.py \
    --model transformer --target label_category --epochs 30
python scripts/multidetector_dataset_v1/infer.py \
    --model models/multidetector_dataset_v1/transformer_label_category.pt \
    --input data/multidetektor/meranie_23_04/2026-04-23_13-14-01.859/FD/
```

## Model Choice

The default model across radar datasets is a compact encoder-only transformer with optional patch embedding. Multidetector also ships a scikit-learn baseline (LogReg / RandomForest on handcrafted + flattened features) for quick sanity checks without PyTorch.

This is a deliberate compromise:

- closer to the multivariate time-series transformer literature than hand-crafted feature models alone
- simpler and more appropriate for short radar sequences than a large long-horizon forecasting architecture
- easy to reproduce and deploy

## Runtime Notes

- `scripts/*/train_*.py` and `scripts/multidetector_dataset_v1/infer.py` require PyTorch. The baseline path (`--model baseline`) requires only scikit-learn + joblib.
- The exporter scripts do not require PyTorch.

## Suggested Install

```bash
# PyTorch from the official selector (CPU / CUDA):
#   https://pytorch.org/get-started/locally/

pip install -r requirements-train.txt
```
