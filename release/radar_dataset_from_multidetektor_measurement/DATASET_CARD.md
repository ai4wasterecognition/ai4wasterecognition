# Dataset Card — radar_dataset_from_multidetektor_measurement

## Dataset Name

`radar_dataset_from_multidetektor_measurement`

## Status

- [x] Public release available

## Related Deliverables

- `D4.31` — *Správa o multidetektorovej analýze údajov riadenej AI*

## Purpose

24 GHz FMCW radar measurements of plastic waste with controlled contaminations (wood, dry/wet paper, glass, Al blinds) collected in a single fixed-geometry lab setup. Intended for training and benchmarking radar-based waste-content classifiers under the AI4WasteRecognition project. The radar data is paired with numbered/named sample photographs (same Nb numbering), making the set multi-input ready and enabling a comparison between radar sensing and image-based recognition.

## What This Repository Contains

- landing page: [`docs/datasets/radar_dataset_from_multidetektor_measurement/outputs.md`](../../docs/datasets/radar_dataset_from_multidetektor_measurement/outputs.md)
- modelling notes: [`docs/datasets/radar_dataset_from_multidetektor_measurement/publication-and-modeling.md`](../../docs/datasets/radar_dataset_from_multidetektor_measurement/publication-and-modeling.md)
- repository-hosted release: [`release/radar_dataset_from_multidetektor_measurement/`](.) (this directory)
- sample preview files: [`samples/radar_dataset_from_multidetektor_measurement/`](../../samples/radar_dataset_from_multidetektor_measurement/)
- training scaffolding: [`scripts/radar_dataset_from_multidetektor_measurement/`](../../scripts/radar_dataset_from_multidetektor_measurement/), [`training/configs/radar_dataset_from_multidetektor_measurement/`](../../training/configs/radar_dataset_from_multidetektor_measurement/)

## DOI and Archive

- DOI: TBD (Zenodo mirror may be added)
- URL: GitHub-hosted at `release/radar_dataset_from_multidetektor_measurement/` of this repository
- version: `1.0.0`

## Public Files

| File | Type | Notes |
|---|---|---|
| `measurement_bins.parquet` | parquet | bin-level radar data (50,150 rows) |
| `measurement_labels.parquet` | parquet | per-measurement labels (2,950) |
| `measurement_metadata.parquet` | parquet | acquisition metadata + geometry (2,950) |
| `measurement_provenance.parquet` | parquet | raw .txt provenance (2,950) |
| `measurement_tensor.npz` | numpy npz | `X (2950, 4, 17) float32` + ids |
| `splits.parquet` | parquet | train/val/test |
| `data_dictionary.csv` | csv | column reference for every file |
| `summary.json` | json | counts, splits, labels, sources, photos |
| `checksums.sha256` | text | SHA-256 of the core data files |
| `photos/` | jpg | 43 sample photographs |
| `aux/foto_catalog.csv` | csv | photo catalog keyed by nb_of_sample |

## Variables and units

- 4 radar channels (`I1`, `Q1`, `I2`, `Q2`) magnitude in dBm
- 17 range bins, bin size ≈ 320.604 mm → max range ≈ 5.45 m
- Frequency 24 008 – 24 242 MHz (FMCW)
- Distance constants: container 2.12 m, back wall 4.0 m
- 17 sample types (column `label_name`), 6 categories (column `label_category`), 1 binary contamination flag
- Sample photographs keyed by `nb_of_sample` in `aux/foto_catalog.csv`

See `data_dictionary.csv` for the full column reference per file.

## Collection Context

- **Geometry:** radar mounted at a fixed distance of 2.12 m from a waste container; back wall at 4.0 m.
- **Acquisition:** SENTIRE 24 GHz radar; one continuous capture session per sample (≈ 150–220 frames per Nb at 50 ms ramp time).
- **Samples:** prepared by operator from real plastic waste with controlled additions (wood objects, dry/wet paper, glass shards, Al blinds rolled or unrolled).
- **Photos:** photographs of each sample showing the detailed waste composition and the top-down view of the sample poured into the container; numbered with the same Nb as the radar samples.

## Processing Steps

1. Raw .txt frames parsed from `data/multidetektor/meranie_23_04/<folder_ts>/FD/`.
2. Per-frame validation: header consistency, 17 bins × 4 channels.
3. Labels merged from `VysledkyPreStatistiku.xlsx` columns `Name o sample` and `Category`.
4. Geometry constants stamped from the D4.31 report.
5. Time-ordered 60/20/20 split within each Nb (`folder_time_ordered_60_20_20`).
6. Long-format parquet + (N, 4, 17) float32 tensor + splits + checksums.
7. Sample photos catalogued by Nb and copied into `photos/`.

## Privacy / Ethics / IP

- No personal data, no identifiable subjects.
- Source materials are project-internal documents (Optima Ideas s.r.o., Asseco Central Europe a.s., STU Bratislava, Sensoneo j.s.a., Mesto Michalovce).
- IP cleared by maintainer for public release at the bin-level + label + photo granularity.

## Licensing

See repository [`LICENSE`](../../LICENSE) and [`docs/LICENSING.md`](../../docs/LICENSING.md).

## Notes

- `Plastic + Ai blinds` → `Plastic + Al blinds` typo correction was applied in the source xlsx before export.
- Sample `Nb=90` (178 frames) excluded — no matching `Name o sample` entry in the source catalogue.
- One stray Empty frame in the xlsx but not in the raw `.txt` dump is excluded.
- Photos are also available as a zip archive: **xxx** (link TBD).
