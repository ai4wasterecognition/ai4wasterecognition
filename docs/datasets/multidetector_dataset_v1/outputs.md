# Multidetector Outputs — Landing Page

24 GHz FMCW radar + UV-VIS spectrometer + lab photo dataset of plastic waste samples with controlled contaminations, collected in a single fixed-geometry lab setup.

## Dataset Name

`multidetector_dataset_v1`

## Status

- [x] Public release available — `release/multidetector_dataset_v1/`

## Related Deliverable

- `D4.31` — *Správa o multidetektorovej analýze údajov riadenej AI*

## Purpose

Provide a reproducible training set for radar-based detection of plastic-waste contamination at a fixed sorting geometry. Complemented by parallel UV-VIS spectrometer measurements (AS7265x) and lab photos for cross-modal experimentation.

## What This Repository Contains

| Asset | Path |
|---|---|
| Dataset card | [`release/multidetector_dataset_v1/DATASET_CARD.md`](../../../release/multidetector_dataset_v1/DATASET_CARD.md) |
| Dataset README | [`release/multidetector_dataset_v1/README.md`](../../../release/multidetector_dataset_v1/README.md) |
| Modelling notes | [`docs/datasets/multidetector_dataset_v1/publication-and-modeling.md`](publication-and-modeling.md) |
| Sample mapping (Nb → label) | [`docs/datasets/multidetector_dataset_v1/sample_mapping.csv`](sample_mapping.csv) |
| Lightweight previews | [`samples/multidetector_dataset_v1/`](../../../samples/multidetector_dataset_v1/) |
| Training scaffolding | [`scripts/multidetector_dataset_v1/`](../../../scripts/multidetector_dataset_v1/), [`training/configs/multidetector_dataset_v1/`](../../../training/configs/multidetector_dataset_v1/) |

## Dataset Snapshot

- 2950 measurement frames (one frame = one `.txt` radar export)
- 17 sample types, 6 categories
- 17 range bins × 4 channels (`I1`, `Q1`, `I2`, `Q2`) per frame
- Fixed geometry: container at 2.12 m, back wall at 4.0 m
- Acquisition date: 2026-04-23, Lab Optima
- Splits: 1770 train / 591 val / 589 test (`folder_time_ordered_60_20_20`)

## DOI and Archive

- DOI: TBD
- URL: this repository at `release/multidetector_dataset_v1/`
- Version: `1.0.0`

## Notes

- This dataset is **separate** from [`radar_dataset_v1`](../radar_dataset_v1/experimental-data.md). The two datasets share no overlapping measurements; they use the same 24 GHz radar but were acquired in different sessions and follow different label conventions.
- A future planned dataset will cover **video segmentation** of waste containers and will live under `release/video_segmentation_dataset_v1/` with parallel scaffolding under `scripts/video_segmentation_dataset_v1/` and `training/configs/video_segmentation_dataset_v1/`.
- Classification metrics produced in v1 reflect memorisation of within-session bin profiles, not true generalisation. A second recording session is required to evaluate transferable performance.
