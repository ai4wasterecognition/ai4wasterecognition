# Radar Dataset from Multidetector Measurement — Landing Page

24 GHz FMCW radar dataset of plastic-waste samples with controlled contaminations, collected in a single fixed-geometry lab setup, paired with numbered/named sample photographs. The radar measurements are the core; the photos make the set multi-input ready and allow a comparison between radar sensing and image-based recognition.

## Dataset Name

`radar_dataset_from_multidetektor_measurement`

## Status

- [x] Public release available — `release/radar_dataset_from_multidetektor_measurement/`

## Related Deliverable

- `D4.31` — *Správa o multidetektorovej analýze údajov riadenej AI*

## Purpose

Provide a reproducible training set for radar-based detection of plastic-waste contamination at a fixed sorting geometry, together with photographs of the same samples (same Nb numbering) so radar results can be compared with video/image recognition.

## What This Repository Contains

| Asset | Path |
|---|---|
| Dataset card | [`release/radar_dataset_from_multidetektor_measurement/DATASET_CARD.md`](../../../release/radar_dataset_from_multidetektor_measurement/DATASET_CARD.md) |
| Dataset README | [`release/radar_dataset_from_multidetektor_measurement/README.md`](../../../release/radar_dataset_from_multidetektor_measurement/README.md) |
| Modelling notes | [`docs/datasets/radar_dataset_from_multidetektor_measurement/publication-and-modeling.md`](publication-and-modeling.md) |
| Sample mapping (Nb → label) | [`docs/datasets/radar_dataset_from_multidetektor_measurement/sample_mapping.csv`](sample_mapping.csv) |
| Lightweight previews | [`samples/radar_dataset_from_multidetektor_measurement/`](../../../samples/radar_dataset_from_multidetektor_measurement/) |
| Training scaffolding | [`scripts/radar_dataset_from_multidetektor_measurement/`](../../../scripts/radar_dataset_from_multidetektor_measurement/), [`training/configs/radar_dataset_from_multidetektor_measurement/`](../../../training/configs/radar_dataset_from_multidetektor_measurement/) |

## Dataset Snapshot

- 2950 measurement frames (one frame = one `.txt` radar export)
- 17 sample types, 6 categories
- 17 range bins × 4 channels (`I1`, `Q1`, `I2`, `Q2`) per frame
- Fixed geometry: container at 2.12 m, back wall at 4.0 m
- Acquisition date: 2026-04-23, Lab Optima
- Splits: 1770 train / 591 val / 589 test (`folder_time_ordered_60_20_20`)
- 43 sample photographs under `release/.../photos/`, catalogued in `aux/foto_catalog.csv`

## Sample Photographs

There are photographs of the measured samples that share the same sample number (Nb) as the radar measurements:

- each radar sample number maps to one or more photos via `nb_of_sample`;
- the photos show the **detailed composition of the waste** and the **top-down view of the sample poured into the waste container** — the same scene the radar observes;
- this enables a direct **comparison between radar sensing and video/image technology** on identical samples.

The photographs are included under `release/.../photos/` and are also available as a zip archive: **xxx** (link TBD).

## Relation to the Planned Open Video Dataset

The repository will additionally host a separate **open video dataset** focused on recognising plastic and paper waste and their individual categories. It is built over an extensive collection of images of these separated waste fractions. During the project it was used to train a neural network, which was then applied to recognise photographs from that dataset; those recognition results can be compared with the radar-based classification provided here. See [`video_segmentation_dataset_v1/outputs.md`](../video_segmentation_dataset_v1/outputs.md).

## DOI and Archive

- DOI: TBD
- URL: this repository at `release/radar_dataset_from_multidetektor_measurement/`
- Version: `1.0.0`

## Notes

- This dataset is **separate** from [`radar_dataset_v1`](../radar_dataset_v1/experimental-data.md). The two datasets share no overlapping measurements; they use the same 24 GHz radar but were acquired in different sessions and follow different label conventions.
- Classification metrics reflect memorisation of within-session bin profiles, not true generalisation. A second recording session is required to evaluate transferable performance.
