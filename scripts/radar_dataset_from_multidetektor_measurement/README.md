# radar_dataset_from_multidetektor_measurement scripts

Scripts for building and consuming [`release/radar_dataset_from_multidetektor_measurement/`](../../release/radar_dataset_from_multidetektor_measurement/). All paths below are repo-relative; run them from the repository root.

## Pipeline

```
data/multidetektor/meranie_23_04/        VysledkyPreStatistiku.xlsx        data/Foto/
                │                                  │                            │
                ▼                                  ▼                            │
        ingest_raw_txt.py              build_sample_mapping.py                  │
                │                                  │                            │
                └──────────► export_dataset.py ◄───┘                            │
                                  │                                             │
                                  ▼                                             ▼
              release/radar_dataset_from_multidetektor_measurement/  ◄─  build_foto_catalog.py
                  (parquet, npz, splits, summary, checksums)            (photos/ + aux/foto_catalog.csv)
```

| Script | Purpose |
|---|---|
| `ingest_raw_txt.py` | Parse 2950 raw `.txt` frames → `processed/radar_dataset_from_multidetektor_measurement/df_bins.parquet` (+ `ingest_log.json`). Excludes `Nb=90` by default. |
| `build_sample_mapping.py` | Build canonical `Nb → label_name + label_category + label_contamination_present` from xlsx. |
| `export_dataset.py` | Materialise the publishable release (parquet tables, npz tensor, splits, data_dictionary, summary, checksums). |
| `build_foto_catalog.py` | Catalogue the sample photographs from `data/Foto/` and copy them into `photos/`; writes `aux/foto_catalog.csv` keyed by `nb_of_sample`. |
| `build_samples.py` | Generate GitHub-safe previews under `samples/radar_dataset_from_multidetektor_measurement/`. |
| `train_classifier.py` | Train baseline (sklearn) or compact transformer (torch) on any of the 3 label targets. |
| `infer.py` | CLI inference: raw `.txt` (single file or folder) → predicted label JSON / CSV. |

## End-to-end

```bash
NAME=radar_dataset_from_multidetektor_measurement
python scripts/$NAME/ingest_raw_txt.py
python scripts/$NAME/build_sample_mapping.py
python scripts/$NAME/export_dataset.py
python scripts/$NAME/build_foto_catalog.py
python scripts/$NAME/build_samples.py

# train (via a YAML config — recommended; CLI flags override config values)
python scripts/$NAME/train_classifier.py \
    --config training/configs/$NAME/transformer_label_category.yaml
# or purely via CLI
python scripts/$NAME/train_classifier.py \
    --model transformer --target label_category --epochs 30

# infer
python scripts/$NAME/infer.py \
    --model models/$NAME/transformer_label_category.pt \
    --input data/multidetektor/meranie_23_04/2026-04-23_13-14-01.859/FD/
```

`train_classifier.py` resolves every setting as **explicit CLI flag > `--config` YAML > built-in default**, so the configs in `training/configs/$NAME/` fully drive a run (model family, target, transformer architecture, augmentation, seed).

## Conventions

- All paths default to repository-relative locations (configurable via CLI flags); run from the repo root.
- All scripts are idempotent — re-running overwrites outputs deterministically.
- This folder is one dataset family. Sister folders for other datasets:
  - `scripts/radar_dataset_v1/` — radar training set (D3.3)
  - `scripts/video_segmentation_dataset_v1/` — planned open video dataset (D4.2)
