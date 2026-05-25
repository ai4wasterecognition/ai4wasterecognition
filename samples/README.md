# Samples

This folder is reserved for small, non-sensitive examples that complement public datasets and larger future archives. Files are organised one subfolder per dataset (`samples/<name>_v<n>/`) to match the convention used by `release/`, `scripts/`, `training/configs/`, and `docs/datasets/`.

Recommended contents per subfolder:

- tiny CSV samples
- schema previews
- one or two raw frame examples
- preview figures or thumbnails

## Current dataset previews

- [`radar_dataset_v1/`](radar_dataset_v1/) — core measurement bin / label / metadata samples; full release: [release/radar_dataset_v1](../release/radar_dataset_v1/README.md)
- [`multidetector_dataset_v1/`](multidetector_dataset_v1/) — raw frame .txt, label/metadata head, bin sample; full release: [release/multidetector_dataset_v1](../release/multidetector_dataset_v1/README.md)

Do not place versioned dataset releases here. Use `release/<name>_v<n>/` for repository-hosted public datasets, or document external archives from `docs/datasets/<name>_v<n>/`.
