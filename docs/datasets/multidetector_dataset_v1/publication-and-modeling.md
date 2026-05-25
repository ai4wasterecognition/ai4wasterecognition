# Multidetector — Publication & Modelling Notes

Companion document to [`outputs.md`](outputs.md) and the release at [`release/multidetector_dataset_v1/`](../../../release/multidetector_dataset_v1/).

## Publishing Layout

Three layers, mirroring the FAIR pattern used by `radar_dataset_v1`:

1. **Canonical signal layer** — `measurement_bins.parquet` long-format, every range bin × every channel preserved verbatim from the raw `.txt` exports. No filtering or normalisation.
2. **Model-ready tensor layer** — `measurement_tensor.npz` with `X: (N, 4, 17) float32` (channel order `I1, Q1, I2, Q2`) and `measurement_ids: (N,)`.
3. **Labels, metadata, provenance, splits** — kept as separate small parquet tables to allow recomputing splits / regrouping labels without re-exporting the bin matrix.

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

## Splits

`folder_time_ordered_60_20_20`: per `nb_of_sample`, sort frames by acquisition timestamp; take first 60% → train, next 20% → val, last 20% → test.

**Limitation:** within one Nb the recording session is continuous (~30–50 s, ~80 ms between frames in a stationary scene). The split prevents identical adjacent-frame copies from crossing splits but does **not** measure generalisation across recording sessions, days, or container configurations. **Treat the v1 metrics as a sanity check on the pipeline, not as deployment-quality numbers.**

For deployment-quality estimates, a second recording session per Nb (different day, different operator) is required. This is intentionally out of scope for v1.

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
- [`training/configs/multidetector_dataset_v1/transformer_label_category.yaml`](../../../training/configs/multidetector_dataset_v1/transformer_label_category.yaml) — primary
- [`training/configs/multidetector_dataset_v1/transformer_label_name.yaml`](../../../training/configs/multidetector_dataset_v1/transformer_label_name.yaml) — fine-grained
- [`training/configs/multidetector_dataset_v1/transformer_label_contamination.yaml`](../../../training/configs/multidetector_dataset_v1/transformer_label_contamination.yaml) — binary

A scikit-learn baseline (LogReg / RandomForest on handcrafted + flattened features) is also shipped via [`training/configs/multidetector_dataset_v1/baseline.yaml`](../../../training/configs/multidetector_dataset_v1/baseline.yaml) and the same `train_classifier.py` script.

## Inference

[`scripts/multidetector_dataset_v1/infer.py`](../../../scripts/multidetector_dataset_v1/infer.py) is the deployable CLI:

```bash
python scripts/multidetector_dataset_v1/infer.py \
    --model models/multidetector_dataset_v1/transformer_label_category.pt \
    --input <single.txt or folder>
```

The script validates that the input `.txt` matches the v1 setup (17 bins, bin_size=320.604 mm, ramp=50 ms, channels=I1,Q1,I2,Q2). If your radar exports differ (different distance, different bin count), this v1 model is **not** transferable without retraining.

## Archival Workflow

GitHub repository serves as the canonical hub. Zenodo mirroring with DOI may be added once v1 is validated by a second-session evaluation. The current `release/` directory is small enough (~1.7 MB total) to live directly in the repo without LFS.
