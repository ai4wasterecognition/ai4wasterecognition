# Dataset Card — multidetector_dataset_v1

## Dataset Name

`multidetector_dataset_v1`

## Status

- [x] Public release available

## Related Deliverables

- `D4.31` — *Správa o multidetektorovej analýze údajov riadenej AI*

## Purpose

24 GHz FMCW radar measurements of plastic waste with controlled contaminations (wood, dry/wet paper, glass, Al blinds) collected in a single fixed-geometry lab setup. Intended for training and benchmarking radar-based waste-content classifiers under the AI4WasteRecognition project. Auxiliary UV-VIS spectrometer data (AS7265x) and lab photos document the same physical samples through complementary modalities.

## What This Repository Contains

- landing page: [`docs/datasets/multidetector_dataset_v1/outputs.md`](../../docs/datasets/multidetector_dataset_v1/outputs.md)
- modelling notes: [`docs/datasets/multidetector_dataset_v1/publication-and-modeling.md`](../../docs/datasets/multidetector_dataset_v1/publication-and-modeling.md)
- repository-hosted release: [`release/multidetector_dataset_v1/`](.) (this directory)
- sample preview files: [`samples/multidetector_dataset_v1/`](../../samples/multidetector_dataset_v1/)
- training scaffolding: [`scripts/multidetector_dataset_v1/`](../../scripts/multidetector_dataset_v1/), [`training/configs/multidetector_dataset_v1/`](../../training/configs/multidetector_dataset_v1/)

## DOI and Archive

- DOI: TBD (Zenodo mirror may be added)
- URL: GitHub-hosted at `release/multidetector_dataset_v1/` of this repository
- version: `1.0.0`

## Public Files

| File | Type | Bytes (approx) |
|---|---|---:|
| `measurement_bins.parquet` | parquet | 855 KB |
| `measurement_labels.parquet` | parquet | 30 KB |
| `measurement_metadata.parquet` | parquet | 60 KB |
| `measurement_provenance.parquet` | parquet | 82 KB |
| `measurement_tensor.npz` | numpy npz | 575 KB |
| `splits.parquet` | parquet | 29 KB |
| `data_dictionary.csv` | csv | 4 KB |
| `summary.json` | json | 3 KB |
| `checksums.sha256` | text | 1 KB |
| `aux/spectro_as7265x.parquet` | parquet | ~25 KB |
| `aux/foto_manifest.csv` | csv | ~10 KB |

## Variables and units

- 4 radar channels (`I1`, `Q1`, `I2`, `Q2`) magnitude in dBm
- 17 range bins, bin size ≈ 320.604 mm → max range ≈ 5.45 m
- Frequency 24 008 – 24 242 MHz (FMCW)
- Distance constants: container 2.12 m, back wall 4.0 m
- 17 sample types (column `label_name`), 6 categories (column `label_category`), 1 binary contamination flag

See `data_dictionary.csv` for the full column reference per file.

## Collection Context

- **Geometry:** sensor mounted at fixed distance 2.12 m from a waste container; back wall at 4.0 m.
- **Acquisition:** SENTIRE 24 GHz radar; one continuous capture session per sample (≈ 150–220 frames per Nb at 50 ms ramp time).
- **Samples:** prepared by operator from real plastic waste with controlled additions (wood objects, dry/wet paper, glass shards, Al blinds rolled or unrolled).
- **Photos:** smartphone images taken during the experiment as visual provenance.
- **Spectro:** AMS AS7265x sensor 65 mm above sample, ambient daylight only (no LED).

## Processing Steps

1. Raw .txt frames parsed from `data/multidetektor/meranie_23_04/<folder_ts>/FD/`.
2. Per-frame validation: header consistency, 17 bins × 4 channels.
3. Labels merged from `VysledkyPreStatistiku.xlsx` columns `Name o sample` and `Category`.
4. Geometry constants stamped from D4.31 report.
5. Time-ordered 60/20/20 split within each Nb (`folder_time_ordered_60_20_20`).
6. Long-format parquet + (N, 4, 17) float32 tensor + splits + checksums.

## Privacy / Ethics / IP

- No personal data, no identifiable subjects.
- Source materials are project-internal documents (Optima Ideas s.r.o., Asseco Central Europe a.s., STU Bratislava, Sensoneo j.s.a., Mesto Michalovce).
- IP cleared by maintainer for public release at the bin-level + label granularity.

## Licensing

See repository [`LICENSE`](../../LICENSE) and [`docs/LICENSING.md`](../../docs/LICENSING.md).

## Notes

- `Plastic + Ai blinds` → `Plastic + Al blinds` typo correction was applied in the source xlsx before export.
- Sample `Nb=90` (178 frames) excluded from v1 — no matching `Name o sample` entry in the source catalogue.
- One stray Empty frame in the xlsx but not in the raw `.txt` dump is excluded.
