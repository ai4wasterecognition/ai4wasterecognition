# Radar Publication and Modeling Plan

This note translates the current `WasteR` workspace into a publication and modeling strategy that is both research-grade and practical for downstream training.

## Why This Structure

The publication strategy should satisfy four constraints at once:

- the released dataset must be usable for machine learning from raw radar measurements
- the published files must remain interpretable and reproducible
- the public archive must separate canonical signal data from derived analytical features
- the repository must document the data well enough for external reuse

This direction is consistent with the FAIR principles, which emphasize findability, accessibility, interoperability, and reusability for data and also for the workflows that produced them. The FAIR paper also explicitly highlights persistent identifiers, rich metadata, provenance, licensing, and domain standards as core requirements.

## What To Publish

The recommended public radar release has three layers:

1. Canonical signal layer
2. Model-ready tensor layer
3. Metadata, labels, and split layer

### Canonical Signal Layer

This is the minimum-processed representation of each radar measurement.

Recommended files:

- `measurement_bins.parquet`
- `measurement_metadata.parquet`
- `measurement_labels.parquet`
- `measurement_provenance.parquet`

`measurement_bins.parquet` should keep one row per `(measurement_id, bin_idx)` with:

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

This is the audit layer. Anyone should be able to rebuild a model input tensor from this file.

### Model-Ready Tensor Layer

This is the training layer. It should represent exactly what the model receives at train and inference time.

Recommended file:

- `measurement_tensor.npz`

Recommended arrays:

- `measurement_id`
- `signal`
- `valid_mask`
- `bin_indices`
- `channel_names`

Where:

- `signal` has shape `[N, L, C]`
- `valid_mask` has shape `[N, L]`
- `channel_names` is fixed as `["i1_dbm", "q1_dbm", "i2_dbm", "q2_dbm"]`

This layer should be generated from the canonical signal layer, not maintained manually.

### Metadata, Labels, and Splits

Recommended files:

- `measurement_metadata.parquet`
- `measurement_labels.parquet`
- `measurement_provenance.parquet`
- `splits.parquet`
- `data_dictionary.csv`

This layer should include:

- acquisition settings
- environment and orientation fields
- curated labels
- task-ready labels such as biomass binary detection
- leakage-safe split assignments

## What Not To Publish Directly

The first public release should avoid publishing:

- private office documents
- raw internal working notebooks without cleanup
- ambiguous distance fields
- unreviewed operational file paths as primary public IDs
- hidden partner-specific notes

In particular:

- `measurement_distance_m` in the current raw workbook is actually a bin-range field, not an object-distance field
- `distance_m` is not currently reliable enough to expose as a benchmark feature without additional validation

## File Formats

Recommended public formats:

- `Parquet` for tabular canonical data and metadata
- `NPZ` for model-ready dense tensors
- `CSV` for dictionaries and taxonomies
- `JSON` for summaries, manifests, and training metrics

This split is deliberate:

- Parquet is efficient and interoperable for columnar research data
- NPZ is convenient for direct array loading in training code

## Release Layout

Recommended archive layout:

- `README.md`
- `DATASET_CARD.md`
- `CITATION.cff`
- `checksums.sha256`
- `core/measurement_bins.parquet`
- `core/measurement_metadata.parquet`
- `core/measurement_labels.parquet`
- `core/measurement_tensor.npz`
- `core/splits.parquet`
- `core/data_dictionary.csv`
- `extended/` with the same pattern for atypical or lower-confidence subsets
- `code/` or a linked GitHub release for exporters and training scripts

## Core vs Extended Subsets

For this project, a split into `core` and `extended` is justified.

### Core

Recommended first benchmark subset:

- 4-channel measurements only
- valid `bin_size_mm > 0`
- `number_of_samples` in `{17, 32, 33}`
- no partial-channel captures

This currently corresponds to the cleanest and most immediately trainable portion of the data.

### Extended

Recommended second subset:

- 161-bin special measurements
- partial-channel or atypical captures
- records retained mainly for completeness or follow-up work

The `extended` subset should be documented but should not be the default benchmark.

## Labeling Strategy

The public release should carry at least three label granularities:

- `material_name_auto` as fine-grained label
- `material_primary` as coarse primary class
- `has_biomass` as binary task label

This supports:

- fine-grained classification
- coarse material classification
- biomass detection

The recommended public label source chain is:

1. catalog join from `Ciselnik Merani`
2. curated mapping from `material_name_auto_mapping.csv`
3. tracked overrides from `radar_material_mapping_overrides.csv`
4. explicit provenance fields that record whether a label came from catalog only or from catalog plus curated mapping

Known ambiguous records should not be forced into benchmark classes. In this repository, unresolved labels can be marked as `unknown`, and the default material-classification training script excludes `unknown` from the supervised benchmark.

## Split Policy

Do not split randomly by individual measurements.

The current data contains repeated captures from the same scenarios. Random row-level splitting would leak near-duplicate conditions across train and test.

Use group-level splitting with a deterministic `capture_group_id`, for example derived from:

- series prefix
- sample type
- mode
- attenuation
- ramp time
- bin size
- number of samples
- place
- orientation
- background setup

The default public split should be deterministic and documented.

## Documentation Requirements

Each public radar release should be accompanied by:

- a dataset card
- a datasheet-style description of composition and collection
- a labeling and preprocessing note
- a split protocol
- a citation entry

This aligns well with:

- Datasheets for Datasets, which recommends documenting motivation, composition, collection process, and recommended uses
- Data Cards, which emphasizes structured dataset documentation across the dataset lifecycle

## Repository and DOI Workflow

Recommended workflow:

1. Keep the GitHub repository as the public project hub.
2. Publish the real dataset in Zenodo as a dataset record.
3. Link the GitHub repository to Zenodo for code releases.
4. Reserve the DOI before the final upload if you want the DOI included inside files.
5. Use DataCite-compliant metadata fields when describing the record.

Zenodo states that a record consists of metadata, files, and a persistent identifier, and that metadata is critical for discoverability. Zenodo also supports automatic ingestion of GitHub releases once the repository is enabled.

## Model Recommendation

For v1, the most suitable transformer is not a large forecasting-oriented architecture. The data here are short multivariate signal sequences with moderate dataset size and strong risk of scenario leakage.

Recommended baseline:

- a compact encoder-only multivariate time series transformer classifier
- optional temporal patch embedding
- leakage-safe supervised training on `measurement_tensor.npz`

Reasoning from primary sources:

- Zerveas et al. present a transformer framework for multivariate time series and report strong results on regression and classification, including settings with limited training samples.
- PatchTST shows that patching can improve efficiency and representation learning, but its main formulation targets long-term forecasting. Its patching idea is still useful here as an optional front-end, but the full forecasting-oriented design is not necessary for short radar sequences.

Therefore, the best v1 choice is:

- compact encoder-only transformer backbone
- raw bin sequence as input
- optional small patch embedding
- binary biomass and coarse-material tasks first

## What This Repository Now Includes

The repository contains a first reproducibility scaffold for this plan:

- `scripts/export_radar_dataset.py`
- `scripts/build_radar_release.py`
- `scripts/train_radar_transformer.py`
- `docs/datasets/radar_material_mapping_overrides.csv`
- `training/configs/`
- `training/README.md`

These scripts are meant to create and consume the dataset structure described above.

## Sources

- FAIR principles: https://www.nature.com/articles/sdata201618
- DataCite Metadata Schema 4.7: https://schema.datacite.org/
- Zenodo records and DOI docs: https://help.zenodo.org/docs/deposit/about-records/ and https://help.zenodo.org/docs/deposit/describe-records/reserve-doi/
- Zenodo GitHub integration: https://help.zenodo.org/docs/github/ and https://help.zenodo.org/docs/github/enable-repository/
- Datasheets for Datasets: https://arxiv.org/abs/1803.09010
- Data Cards: https://arxiv.org/abs/2204.01075
- Transformer framework for multivariate time series: https://openreview.net/forum?id=lE1AB4stmX
- PatchTST: https://openreview.net/pdf?id=Jbdc0vTOcol
