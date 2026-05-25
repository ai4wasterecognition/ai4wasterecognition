# multidetector_dataset_v1

24 GHz FMCW radar dataset of plastic waste samples in a fixed lab geometry, with optional auxiliary UV-VIS spectrometer (AS7265x) and lab photos.

**Version:** `multidetector_dataset_v1.0.0`
**Acquisition date:** 2026-04-23
**Location:** Lab Optima
**Project:** AI4WasteRecognition — `09I05-03-V02-00068`
**Related deliverable:** D4.31 — *Správa o multidetektorovej analýze údajov riadenej AI*

## Overview

- **Sensor:** SENTIRE 24 GHz FMCW radar, 4 channels (`I1`, `Q1`, `I2`, `Q2`)
- **Fixed geometry:** radar → waste container = **2.12 m**, radar → back wall = 4 m
- **Frame:** 17 range bins × 4 channels, magnitude in dBm
- **Recommended target window:** bins **7 and 8** (container at ≈ 1.92–2.24 m)
- **17 sample types** organised into 6 categories (Reference, +wood, +paper, +glass, +Al blinds, only paper)
- **2950 measurement frames** (each frame = one .txt export from the radar)

## Files

| File | Rows | Description |
|---|---:|---|
| `measurement_bins.parquet` | 50,150 | Long-format bin-level data (one row per (measurement_id, bin_idx)) |
| `measurement_labels.parquet` | 2,950 | Per-measurement labels: `label_name` (17 classes), `label_category` (6 classes), `label_contamination_present` (binary) |
| `measurement_metadata.parquet` | 2,950 | Per-measurement acquisition metadata + geometry constants |
| `measurement_provenance.parquet` | 2,950 | Mapping back to raw `.txt` file paths and ingest timestamps |
| `measurement_tensor.npz` | – | Model-ready arrays: `X: (2950, 4, 17) float32`, `measurement_ids: (2950,)` |
| `splits.parquet` | 2,950 | `train`/`val`/`test` split (`folder_time_ordered_60_20_20` per Nb) |
| `data_dictionary.csv` | – | Full column reference for every file |
| `summary.json` | – | Counts, splits, label classes, source documents |
| `checksums.sha256` | – | SHA-256 of every data file |
| `aux/spectro_as7265x.parquet` | 1,700 | Optional UV-VIS spectrometer (10 samples × 10 reps × 17 wavelengths) |
| `aux/foto_manifest.csv` | 44 | Lab photos with EXIF timestamps mapped to the nearest radar frame |

## Quick start (Python)

```python
import numpy as np
import pandas as pd

base = "release/multidetector_dataset_v1"

# Tabular access
labels = pd.read_parquet(f"{base}/measurement_labels.parquet")
splits = pd.read_parquet(f"{base}/splits.parquet")
df = labels.merge(splits, on="measurement_id")
print(df.groupby(["split", "label_category"]).size().unstack(fill_value=0))

# Tensor access
npz = np.load(f"{base}/measurement_tensor.npz", allow_pickle=True)
X = npz["X"]                       # (2950, 4, 17) float32
ids = npz["measurement_ids"]       # (2950,) object
print(X.shape, X.dtype)
```

## Splits

`folder_time_ordered_60_20_20`: within each `nb_of_sample`, frames are sorted by acquisition timestamp; first 60% → train, next 20% → val, last 20% → test.

This guards against trivial duplicate-frame leakage (adjacent radar frames are ~80 ms apart and nearly identical) without forcing leave-one-sample-out, which is not possible here (each Nb was recorded in a single continuous session).

| split | n |
|---|---:|
| train | 1770 |
| val | 591 |
| test | 589 |

## Label schema

| target | classes | source |
|---|---:|---|
| `label_name` | 17 | verbatim `Name o sample` from `VysledkyPreStatistiku.xlsx` (trimmed) |
| `label_category` | 6 | verbatim `Category` from `VysledkyPreStatistiku.xlsx` |
| `label_contamination_present` | 2 | derived: `Category != "Reference measurement"` |

The 6 categories are: `Reference measurement`, `Plastic + wooden objects`, `Plastic + paper waste`, `Plastic + glass waste`, `Plastic + Al blinds`, `Only paper waste`.

**Reference measurement** includes Empty container (Nb=10), 1/3 plastic (Nb=20), Full plastic (Nb=40) — i.e., "no contamination present". The binary `label_contamination_present` collapses these three Nb's to `False` and everything else to `True`.

## Excluded data

| Nb | reason |
|---:|---|
| 90 | Operator excluded — no matching label in the source `Name o sample` catalogue (178 frames dropped from raw). Listed in `summary.json["excluded_nb"]`. |

One additional Empty frame (`10_2026-04-23_13-13-39.926`) appears in the source xlsx but not in the raw `.txt` dump (likely a warm-up record). Excluded for raw/release consistency.

## Source-data lineage

```
data/multidetektor/meranie_23_04/<folder_ts>/FD/<Nb>_<ts>.txt   ← canonical raw
        │
        ├── ingest_raw_txt.py  (parse header + 17 bin rows × 4 channels)
        │       │
        │       └── processed/multidetector_dataset_v1/df_bins.parquet
        │
        └── (geometry constants from D4.31 report)

data/multidetektor/VysledkyPreStatistiku.xlsx                   ← label source
        │   (column: Name o sample, Category)
        │
        └── build_sample_mapping.py → processed/multidetector_dataset_v1/sample_mapping.csv

both → export_dataset.py → release/multidetector_dataset_v1/{parquet,npz,splits,...}
```

## Caveats

- **Single recording session per Nb.** Frames within one Nb are ~80 ms apart in a stationary scene → very high frame-to-frame correlation. Within-Nb time-ordered splits do not eliminate this. **Reported classification metrics on this v1 reflect memorisation of stable per-sample bin profiles, not true generalisation.** For honest generalisation estimates, collect a second recording session per Nb.
- **`measurement_distance_m`** (2.12 m) is a session-level constant, not a per-frame measurement.
- **`Category` typo fix.** The source xlsx originally contained `Plastic + Ai blinds`; the maintainer corrected this to `Plastic + Al blinds` directly in the xlsx before the v1 export.

## Training & inference

Scripts (in [`scripts/multidetector_dataset_v1/`](../../scripts/multidetector_dataset_v1/)):

- `train_classifier.py` — baseline (LogReg/RandomForest) and a compact encoder-only transformer
- `infer.py` — CLI that reads raw `.txt` frames and outputs predicted labels

YAML configs in [`training/configs/multidetector_dataset_v1/`](../../training/configs/multidetector_dataset_v1/):

- `baseline.yaml`
- `transformer_label_category.yaml`   (primary; 6 classes)
- `transformer_label_name.yaml`       (fine-grained; 17 classes)
- `transformer_label_contamination.yaml` (binary)

## Citation

If you use this dataset, please cite the project's `CITATION.cff` and reference the D4.31 deliverable for the methodology.

## License

See repository [`LICENSE`](../../LICENSE) for license terms.
