# Samples

This folder is reserved for small, non-sensitive examples that complement public datasets and larger future archives. Files are organised one subfolder per dataset (`samples/<name>_v<n>/`) to match the convention used by `release/`, `scripts/`, `training/configs/`, and `docs/datasets/`.

Recommended contents per subfolder:

- tiny CSV samples
- schema previews
- one or two raw frame examples
- preview figures or thumbnails

## Current dataset previews

- [`radar_dataset_v1/`](radar_dataset_v1/) - core measurement bin, label, and metadata samples; full release: [release/radar_dataset_v1](../release/radar_dataset_v1/README.md)
- [`radar_dataset_from_multidetektor_measurement/`](radar_dataset_from_multidetektor_measurement/) - raw frame `.txt`, label and metadata head, and bin sample; full release: [release/radar_dataset_from_multidetektor_measurement](../release/radar_dataset_from_multidetektor_measurement/README.md)
- [`video_segmentation_dataset_v1/`](video_segmentation_dataset_v1/) - mini COCO instance-segmentation sample with images and annotations; the full dataset stays local or moves to an external archive later

Do not place versioned dataset releases here. Use `release/<name>_v<n>/` for repository-hosted public datasets, or document external archives from `docs/datasets/<name>_v<n>/`.
