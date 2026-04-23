# Radar Experimental Data

## Status

Public release available.

## Related Deliverables

- `D3.3` Experimental Data Collection Dataset
- `D3.1` Laboratory Setup and Calibration Report

## Purpose

This page describes the public radar measurement dataset produced during laboratory data collection and prepared for model training from raw bin-level measurements.

For the concrete publication and modeling strategy, see [radar-publication-and-modeling.md](radar-publication-and-modeling.md).

## Current Public Release

- release path: [release/radar_dataset_v1](../../release/radar_dataset_v1/README.md)
- combined summary: [release/radar_dataset_v1/summary.json](../../release/radar_dataset_v1/summary.json)
- core subset:
  - [measurement_bins.parquet](../../release/radar_dataset_v1/core/measurement_bins.parquet)
  - [measurement_tensor.npz](../../release/radar_dataset_v1/core/measurement_tensor.npz)
  - [measurement_labels.parquet](../../release/radar_dataset_v1/core/measurement_labels.parquet)
  - [measurement_metadata.parquet](../../release/radar_dataset_v1/core/measurement_metadata.parquet)
  - [splits.parquet](../../release/radar_dataset_v1/core/splits.parquet)
- extended subset:
  - [measurement_bins.parquet](../../release/radar_dataset_v1/extended/measurement_bins.parquet)
  - [measurement_tensor.npz](../../release/radar_dataset_v1/extended/measurement_tensor.npz)
  - [measurement_labels.parquet](../../release/radar_dataset_v1/extended/measurement_labels.parquet)
  - [measurement_metadata.parquet](../../release/radar_dataset_v1/extended/measurement_metadata.parquet)
  - [splits.parquet](../../release/radar_dataset_v1/extended/splits.parquet)
- exporter and training code:
  - [scripts/export_radar_dataset.py](../../scripts/export_radar_dataset.py)
  - [scripts/build_radar_release.py](../../scripts/build_radar_release.py)
  - [scripts/train_radar_transformer.py](../../scripts/train_radar_transformer.py)
  - [training/README.md](../../training/README.md)

## Release Summary

- `core`: 13,650 measurements, 254,594 bin rows, 4 channels, maximum sequence length 33
- `extended`: 201 measurements, 17,495 bin rows, 4 channels, maximum sequence length 161
- `core` primary labels include `plastic`, `paper_cardboard`, `water`, `biomass`, `background`, `glass`, `human`, `container_only`, `oil`, `metal`, and `unknown`

## What This Repository Contains

- full curated release package in `release/radar_dataset_v1/`
- dataset description and release summary
- schema notes and data dictionaries inside the release folders
- small illustrative CSV samples in `samples/`
- exporter and training scripts linked from the repository

## What Should Stay Outside The Public Release

- raw logs
- internal working notebooks that were not cleaned for publication
- large binary captures
- restricted or unapproved consortium material

## DOI and Archival Mirror

- current repository release: `release/radar_dataset_v1`
- DOI: `TBD`
- archival mirror URL: `TBD`
- version: `v1`
