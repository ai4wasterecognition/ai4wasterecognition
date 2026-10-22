# Samples

This folder contains small, non-sensitive previews of the project datasets that can be viewed directly in the browser. Files are organised one subfolder per dataset (`samples/<name>/`), matching the convention used by `release/`, `scripts/`, `training/configs/`, and `docs/datasets/`.

## Dataset Previews

| Folder | Content | Full dataset |
| --- | --- | --- |
| [radar_dataset_v1/](radar_dataset_v1/) | CSV samples of measurement bins, labels, and metadata from the `core` subset | [release/radar_dataset_v1](../release/radar_dataset_v1/README.md) |
| [radar_dataset_from_multidetektor_measurement/](radar_dataset_from_multidetektor_measurement/README.md) | one raw radar `.txt` frame, first 25 label and metadata rows, all bin rows of one measurement | [release/radar_dataset_from_multidetektor_measurement](../release/radar_dataset_from_multidetektor_measurement/README.md) |
| [video_segmentation_dataset_v1/](video_segmentation_dataset_v1/README.md) | mini COCO instance-segmentation sample: 6 images, 317 annotated instances | not published |

Full dataset releases are in `release/<name>/`, not in this folder.
