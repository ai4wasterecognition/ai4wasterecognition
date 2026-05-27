# Radar Dataset from Multidetector Measurement — Publication & Modelling Notes

Companion document to [`outputs.md`](outputs.md) and the release at [`release/radar_dataset_from_multidetektor_measurement/`](../../../release/radar_dataset_from_multidetektor_measurement/).

## Publishing Layout

Three layers, mirroring the FAIR pattern used by `radar_dataset_v1`:

1. **Canonical signal layer** — `measurement_bins.parquet` long-format, every range bin × every channel preserved verbatim from the raw `.txt` exports. No filtering or normalisation.
2. **Model-ready tensor layer** — `measurement_tensor.npz` with `X: (N, 4, 17) float32` (channel order `I1, Q1, I2, Q2`) and `measurement_ids: (N,)`.
3. **Labels, metadata, provenance, splits** — kept as separate small parquet tables to allow recomputing splits / regrouping labels without re-exporting the bin matrix.

A fourth, image layer accompanies the radar data: sample photographs under `photos/`, catalogued in `aux/foto_catalog.csv` and keyed by the same `nb_of_sample` as the radar tables.

## What is NOT Published

- Raw .txt frames themselves (provenance recorded; the canonical bin parquet is byte-equivalent).
- Source xlsx (`VysledkyPreStatistiku.xlsx`) — internal project workbook.
- D4.31 report (consortium-internal).
- Working notebooks / one-off analyses.
- Per-frame radar-distance field (geometry is a session-level constant 2.12 m, not a per-frame measurement; do not treat it as a regression target).

## Labels

Three label columns are shipped:

- `label_name` (17) — verbatim `Name o sample` from xlsx (operator-supplied).
- `label_category` (6) — verbatim `Category` from xlsx (after typo `Ai → Al` correction).
- `label_contamination_present` (binary) — derived: `Category != "Reference measurement"`.

`label_category` is the **primary inference target** for this release. `label_name` is provided for finer-grained experiments (e.g., distinguishing panel orientation in `plastic + wood`). `label_contamination_present` is a clean baseline for the operational "is there any anomaly?" use case.

## Sample Photographs and Radar-vs-Video Comparison

Each radar sample number (Nb) is paired with photograph(s) of the same physical sample. The photos capture the detailed waste composition and the top-down view of the sample in the container. Because the photos and radar frames share `nb_of_sample`, the dataset supports a direct comparison between radar-based classification and image-based recognition, and is a starting point for multi-input (radar + image) models.

A separate **open video dataset** (built over a large collection of separated plastic/paper waste images, used during the project to train an image-recognition neural network) will be published in the repository and can serve as the image-recognition counterpart for this comparison.

## Splits

`folder_time_ordered_60_20_20`: per `nb_of_sample`, sort frames by acquisition timestamp; take first 60% → train, next 20% → val, last 20% → test.

**Limitation:** within one Nb the recording session is continuous (~30–50 s, ~80 ms between frames in a stationary scene). The split prevents identical adjacent-frame copies from crossing splits but does **not** measure generalisation across recording sessions, days, or container configurations. **Treat these metrics as a sanity check on the pipeline, not as deployment-quality numbers.**

For deployment-quality estimates, a second recording session per Nb (different day, different operator) is required. This is intentionally out of scope here.

## Modelling

A compact encoder-only transformer is provided as the reference architecture:

- Input: `(B, 4, 17)` standardised per channel
- `Conv1d(4 → d_model, kernel_size=1)` patch embed + learnable 17-token positional encoding
- 4 transformer encoder layers (`norm_first=True`), 4 heads, mlp_ratio=2, dropout=0.1
- Mean-pool over bins → linear classifier
- AdamW (lr=3e-4, weight_decay=1e-4) + cosine schedule
- Class-balanced cross-entropy loss
- Augmentation: per-channel gaussian noise σ ≈ 0.5 dB, random whole-channel masking p=0.2

Three YAML configs:
- [`training/configs/radar_dataset_from_multidetektor_measurement/transformer_label_category.yaml`](../../../training/configs/radar_dataset_from_multidetektor_measurement/transformer_label_category.yaml) — primary
- [`training/configs/radar_dataset_from_multidetektor_measurement/transformer_label_name.yaml`](../../../training/configs/radar_dataset_from_multidetektor_measurement/transformer_label_name.yaml) — fine-grained
- [`training/configs/radar_dataset_from_multidetektor_measurement/transformer_label_contamination.yaml`](../../../training/configs/radar_dataset_from_multidetektor_measurement/transformer_label_contamination.yaml) — binary

A scikit-learn baseline (LogReg / RandomForest on handcrafted + flattened features) is also shipped via [`training/configs/radar_dataset_from_multidetektor_measurement/baseline.yaml`](../../../training/configs/radar_dataset_from_multidetektor_measurement/baseline.yaml) and the same `train_classifier.py` script.

## Inference

[`scripts/radar_dataset_from_multidetektor_measurement/infer.py`](../../../scripts/radar_dataset_from_multidetektor_measurement/infer.py) is the deployable CLI:

```bash
python scripts/radar_dataset_from_multidetektor_measurement/infer.py \
    --model models/radar_dataset_from_multidetektor_measurement/transformer_label_category.pt \
    --input <single.txt or folder>
```

The script validates that the input `.txt` matches the setup (17 bins, bin_size=320.604 mm, ramp=50 ms, channels=I1,Q1,I2,Q2). If your radar exports differ (different distance, different bin count), this model is **not** transferable without retraining.

## Archival Workflow

The GitHub repository serves as the canonical hub. Zenodo mirroring with DOI may be added once the release is validated by a second-session evaluation. The radar tables are compact (~1.7 MB); the sample photographs add ~150 MB, and are also offered as a downloadable zip archive (link TBD).
