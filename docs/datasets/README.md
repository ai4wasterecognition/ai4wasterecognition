# Dataset Registry

This folder documents every dataset family of the AI4WasteRecognition project. Each family has one landing page that describes its content, links to its files in this repository, and names the related deliverable(s).

## Datasets in This Repository

| Dataset | Status | Deliverable | Files | Landing page |
| --- | --- | --- | --- | --- |
| Radar dataset v1 | full release published | `D3.3` | [release/radar_dataset_v1](../../release/radar_dataset_v1/README.md) | [radar_dataset_v1/experimental-data.md](radar_dataset_v1/experimental-data.md) |
| Radar dataset from multidetector measurement | full release published | `D4.3` | [release/radar_dataset_from_multidetektor_measurement](../../release/radar_dataset_from_multidetektor_measurement/README.md) | [radar_dataset_from_multidetektor_measurement/outputs.md](radar_dataset_from_multidetektor_measurement/outputs.md) |
| Video segmentation dataset v1 | full release published | `D4.2` | [release/video_segmentation_dataset_v1](../../release/video_segmentation_dataset_v1/README.md) | [video_segmentation_dataset_v1/outputs.md](video_segmentation_dataset_v1/outputs.md) |

None of the datasets has a DOI-backed archive copy yet. The GitHub repository is the reference location.

## Pages per Dataset

- [radar_dataset_v1/experimental-data.md](radar_dataset_v1/experimental-data.md) - radar dataset v1 landing page, file list, and release summary
- [radar_dataset_v1/publication-and-modeling.md](radar_dataset_v1/publication-and-modeling.md) - release structure, metadata, and transformer baseline
- [radar_dataset_v1/analysis-outputs.md](radar_dataset_v1/analysis-outputs.md) - radar analysis outputs related to `D4.1`
- [radar_dataset_from_multidetektor_measurement/outputs.md](radar_dataset_from_multidetektor_measurement/outputs.md) - multidetector radar dataset landing page
- [radar_dataset_from_multidetektor_measurement/publication-and-modeling.md](radar_dataset_from_multidetektor_measurement/publication-and-modeling.md) - modelling notes
- [video_segmentation_dataset_v1/outputs.md](video_segmentation_dataset_v1/outputs.md) - segmentation dataset landing page, inventory, and note on the figures in `D4.2`
- [video_segmentation_dataset_v1/input-spec.md](video_segmentation_dataset_v1/input-spec.md) - input and export format for the segmentation dataset
- [video_segmentation_dataset_v1/workplan.md](video_segmentation_dataset_v1/workplan.md) - preparation plan for the segmentation dataset

## Templates

- [TEMPLATE.md](TEMPLATE.md) - landing page template
- [DATASET_CARD_TEMPLATE.md](DATASET_CARD_TEMPLATE.md) - dataset card template

## Folder Convention

Every dataset family uses its own subfolder, mirrored in `release/`, `scripts/`, `samples/`, and `training/configs/`:

```text
docs/datasets/
├── README.md
├── TEMPLATE.md
├── DATASET_CARD_TEMPLATE.md
├── radar_dataset_v1/
│   ├── experimental-data.md
│   ├── publication-and-modeling.md
│   ├── analysis-outputs.md
│   └── material_mapping_overrides.csv
├── radar_dataset_from_multidetektor_measurement/
│   ├── outputs.md
│   ├── publication-and-modeling.md
│   └── sample_mapping.csv
└── video_segmentation_dataset_v1/
    ├── outputs.md
    ├── input-spec.md
    ├── workplan.md
    └── anonymization_regions.csv
```

What is and is not published is described in [docs/PUBLISHING.md](../PUBLISHING.md).
