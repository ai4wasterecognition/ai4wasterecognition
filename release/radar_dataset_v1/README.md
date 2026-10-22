# AI4WasteRecognition Radar Dataset v1

Curated 24 GHz FMCW radar dataset of sorted waste materials, collected in the project laboratory experiments (deliverable `D3.3`). The dataset is versioned directly in this repository as `release/radar_dataset_v1`.

Contents:

- `core/` - clean benchmark subset
- `extended/` - atypical or lower-consistency measurements
- `summary.json` - combined release summary
- `checksums.sha256` - file checksums
- `core/data_dictionary.csv` and `extended/data_dictionary.csv` - column reference

Each subset contains `measurement_bins.parquet`, `measurement_tensor.npz`, `measurement_labels.parquet`, `measurement_metadata.parquet`, `measurement_provenance.parquet`, `splits.parquet`, and `summary.json`.

Counts:

- core measurements: 13,650 (train 9,102 / val 2,418 / test 2,130)
- core bin rows: 254,594
- extended measurements: 201
- extended bin rows: 17,495
- core primary material classes: `plastic`, `paper_cardboard`, `water`, `biomass`, `background`, `glass`, `human`, `container_only`, `oil`, `metal`, `unknown`

The dataset has no DOI-backed archive copy yet. Landing page: [docs/datasets/radar_dataset_v1/experimental-data.md](../../docs/datasets/radar_dataset_v1/experimental-data.md).
