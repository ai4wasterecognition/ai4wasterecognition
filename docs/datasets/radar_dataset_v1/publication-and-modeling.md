# Radar Dataset v1: Release Structure and Modeling

This page describes the structure of the published radar dataset [release/radar_dataset_v1](../../../release/radar_dataset_v1/README.md), its labels and split protocol, and the baseline transformer model.

## Design Goals

The release is structured so that:

- the data are usable for machine learning from raw radar measurements
- the published files are interpretable and reproducible
- canonical signal data are separated from derived model inputs
- the data are documented well enough for external reuse

This follows the FAIR principles (findability, accessibility, interoperability, reusability), which highlight rich metadata, provenance, licensing, and domain standards for data and the workflows that produced them.

## Release Layers

The release has three layers, each present in both the `core/` and `extended/` subsets.

### Canonical Signal Layer

`measurement_bins.parquet` is the minimum-processed representation of each radar measurement, with one row per `(measurement_id, bin_idx)`:

- `measurement_id`
- `bin_idx`
- `bin_range_m`
- `i1_dbm`
- `q1_dbm`
- `i2_dbm`
- `q2_dbm`
- `is_target_bin_w2`
- `is_target_bin_w3`
- `is_background_bin`

This is the audit layer: the model input tensor can be rebuilt from this file.

### Model-Ready Tensor Layer

`measurement_tensor.npz` contains exactly what the model receives at train and inference time. It is generated from the canonical signal layer.

Arrays:

- `measurement_id`
- `signal` with shape `[N, L, C]`
- `valid_mask` with shape `[N, L]`
- `seq_len`
- `bin_indices`
- `channel_names`, fixed as `["i1_dbm", "q1_dbm", "i2_dbm", "q2_dbm"]`

All arrays use plain numeric or string dtypes, so `np.load(path)` works without `allow_pickle`.

### Metadata, Labels, and Splits

- `measurement_metadata.parquet` - acquisition settings (mode, attenuation, ramp time, bin size, frequency range, channels), place, orientation, and QC flags
- `measurement_labels.parquet` - curated labels
- `measurement_provenance.parquet` - source file and label source of each measurement
- `splits.parquet` - leakage-safe split assignments
- `data_dictionary.csv` - column reference

## Excluded Data

The release does not contain:

- private office documents or internal working notebooks
- ambiguous distance fields
- internal file paths as primary IDs
- partner-specific notes

In particular, `measurement_distance_m` in the raw workbook is a bin-range field, not an object distance, and `distance_m` is not reliable enough to be a benchmark feature. Neither is included.

## File Formats

- `Parquet` for tabular signal data and metadata
- `NPZ` for model-ready dense tensors
- `CSV` for dictionaries
- `JSON` for summaries

## Core and Extended Subsets

### Core

The benchmark subset (13,650 measurements):

- 4-channel measurements only
- valid `bin_size_mm > 0`
- `number_of_samples` in `{17, 32, 33}`
- no partial-channel captures

### Extended

Atypical measurements kept for completeness (201 measurements):

- 161-bin special measurements
- partial-channel or atypical captures

`extended` is not the default benchmark.

## Labels

The release carries three label granularities:

- `material_name_auto` - fine-grained label (68 classes in `core`)
- `material_primary` - coarse primary class (11 classes)
- `has_biomass` - binary biomass label

Label source chain:

1. catalog join from `Ciselnik Merani`
2. curated mapping from `material_name_auto_mapping.csv`
3. tracked overrides from [material_mapping_overrides.csv](material_mapping_overrides.csv)
4. the `label_source` field records the origin of each label (`catalog+mapping` for all `core` measurements)

Ambiguous records are labelled `unknown` and are not forced into benchmark classes. The training script excludes `unknown` from supervised material classification and biomass detection.

In `core`, `has_biomass` is stored as the strings `"True"`/`"False"` (missing for `unknown`); in `extended` it is a boolean column. Convert it explicitly, for example `labels["has_biomass"].map({"True": True, "False": False, True: True, False: False})`.

## Split Protocol

Splits are made at group level, not randomly by individual measurement. The data contain repeated captures of the same scenarios, so random row-level splitting would leak near-duplicate conditions across train and test.

Each measurement has a deterministic `capture_group_id` (448 groups in `core`) derived from series prefix, sample type, mode, attenuation, ramp time, bin size, number of samples, place, orientation, and background setup. Whole groups are assigned to `train`, `val`, or `test` (split scheme `group_hash_v1`): 9,102 / 2,418 / 2,130 measurements in `core`.

## Documentation

The release is accompanied by:

- a landing page: [experimental-data.md](experimental-data.md)
- a release README, summary, and checksums: [release/radar_dataset_v1](../../../release/radar_dataset_v1/README.md)
- data dictionaries per subset
- this description of structure, labels, and splits
- citation metadata: [CITATION.cff](../../../CITATION.cff)

This structure follows Datasheets for Datasets and Data Cards, which document motivation, composition, collection process, and recommended uses across the dataset lifecycle.

## Baseline Model

The data are short multivariate signal sequences with moderate dataset size and a strong risk of scenario leakage, so the baseline is a compact model rather than a large forecasting architecture:

- compact encoder-only multivariate time-series transformer classifier
- raw bin sequence as input
- optional temporal patch embedding
- supervised training on `measurement_tensor.npz` with the group-level split
- two tasks: binary biomass detection and coarse material classification

Rationale:

- Zerveas et al. present a transformer framework for multivariate time series with strong classification results, including settings with limited training samples.
- PatchTST shows that patching improves efficiency and representation learning. Its main formulation targets long-term forecasting, so only the patching idea is used here, as an optional front-end.

## Code

- [scripts/radar_dataset_v1/export_dataset.py](../../../scripts/radar_dataset_v1/export_dataset.py) - builds one subset from the internal source data
- [scripts/radar_dataset_v1/build_release.py](../../../scripts/radar_dataset_v1/build_release.py) - builds the full release, README, checksums, and samples
- [scripts/radar_dataset_v1/train_transformer.py](../../../scripts/radar_dataset_v1/train_transformer.py) - trains the baseline transformer on the release
- [training/configs/radar_dataset_v1/](../../../training/configs/radar_dataset_v1/) - training configurations
- [training/README.md](../../../training/README.md) - training workflow

## Sources

- FAIR principles: https://www.nature.com/articles/sdata201618
- DataCite Metadata Schema 4.7: https://schema.datacite.org/
- Datasheets for Datasets: https://arxiv.org/abs/1803.09010
- Data Cards: https://arxiv.org/abs/2204.01075
- Transformer framework for multivariate time series: https://openreview.net/forum?id=lE1AB4stmX
- PatchTST: https://openreview.net/pdf?id=Jbdc0vTOcol
