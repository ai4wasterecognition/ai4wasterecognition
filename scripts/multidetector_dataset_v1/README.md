# multidetector_dataset_v1 scripts

Scripts for building and consuming [`release/multidetector_dataset_v1/`](../../release/multidetector_dataset_v1/). All paths below are repo-relative.

## Pipeline

```
data/multidetektor/meranie_23_04/             VysledkyPreStatistiku.xlsx
                │                                       │
                ▼                                       ▼
        ingest_raw_txt.py                    build_sample_mapping.py
                │                                       │
                └────────► export_dataset.py ◄──────────┘
                                  │
                                  ▼
                     release/multidetector_dataset_v1/
                                  ▲
            ┌─────────────────────┼────────────────────┐
            │                                          │
   extract_as7265x.py                       build_foto_manifest.py
   (docx → aux/spectro_as7265x.parquet)     (EXIF → aux/foto_manifest.csv)
```

| Script | Purpose |
|---|---|
| `ingest_raw_txt.py` | Parse 2950 raw `.txt` frames → `processed/multidetector_dataset_v1/df_bins.parquet` (+ `ingest_log.json`). Excludes `Nb=90` by default. |
| `build_sample_mapping.py` | Build canonical `Nb → label_name + label_category + label_contamination_present` from xlsx. |
| `export_dataset.py` | Materialise the publishable release (parquet tables, npz tensor, splits, data_dictionary, summary, checksums). |
| `extract_as7265x.py` | Parse AS7265x UV-VIS spectrometer tables from the Word protocol into `aux/spectro_as7265x.parquet`. |
| `build_foto_manifest.py` | EXIF-based mapping of 44 lab photos → nearest radar measurement. |
| `build_samples.py` | Generate GitHub-safe previews under `samples/multidetector_dataset_v1/`. |
| `train_classifier.py` | Train baseline (sklearn) or compact transformer (torch) on any of the 3 label targets. |
| `infer.py` | CLI inference: raw `.txt` (single file or folder) → predicted label JSON / CSV. |

## End-to-end

```bash
python scripts/multidetector_dataset_v1/ingest_raw_txt.py
python scripts/multidetector_dataset_v1/build_sample_mapping.py
python scripts/multidetector_dataset_v1/export_dataset.py
python scripts/multidetector_dataset_v1/extract_as7265x.py
python scripts/multidetector_dataset_v1/build_foto_manifest.py
python scripts/multidetector_dataset_v1/build_samples.py

# train + infer
python scripts/multidetector_dataset_v1/train_classifier.py \
    --model transformer --target label_category --epochs 30
python scripts/multidetector_dataset_v1/infer.py \
    --model models/multidetector_dataset_v1/transformer_label_category.pt \
    --input data/multidetektor/meranie_23_04/2026-04-23_13-14-01.859/FD/
```

## Conventions

- All paths default to repository-absolute locations (configurable via CLI flags).
- All scripts are idempotent — re-running overwrites outputs deterministically.
- This folder is one dataset family. Sister folders for other datasets:
  - `scripts/radar_dataset_v1/` — radar training set (D3.3)
  - `scripts/video_segmentation_dataset_v1/` — planned (D4.2)
