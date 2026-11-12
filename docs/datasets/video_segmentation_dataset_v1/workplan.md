# Video Segmentation Dataset Preparation

This page describes how the project video segmentation dataset was prepared: source data, label taxonomy, quality checks, export format, split protocol, benchmark tracks, and the baseline model. The training-ready dataset is published in [release/video_segmentation_dataset_v1](../../../release/video_segmentation_dataset_v1/README.md) together with the training code.

## Project Mapping

- `D3.3` Experimental Data Collection Dataset
- `D4.2` Report on AI-Driven Video Data Analysis
- `D5.1` Generalisation, comparison and recommendation for future work

## Repository Content

- landing page: [outputs.md](outputs.md)
- input and export format: [input-spec.md](input-spec.md)
- dataset release: [release/video_segmentation_dataset_v1](../../../release/video_segmentation_dataset_v1/README.md)
- preview sample: [samples/video_segmentation_dataset_v1/all_classes_mini_coco](../../../samples/video_segmentation_dataset_v1/all_classes_mini_coco/README.md)
- RF-DETR Seg training script, configs, and shell launcher: [scripts/video_segmentation_dataset_v1](../../../scripts/video_segmentation_dataset_v1/README.md), [training/configs/video_segmentation_dataset_v1](../../../training/configs/video_segmentation_dataset_v1/), [training/run_rfdetr_seg.sh](../../../training/run_rfdetr_seg.sh)

## Source Data

Source bundles (CVAT exports, not published):

- `WasteR_01_02_03_Backup.zip`
- `WasteR_04_05_06_Backup.zip`
- `WasteR_07_Backup.zip`
- `WasteR_08_Backup.zip`
- `WasteR_09_Backup.zip`
- `WasteR_10_Backup.zip`
- `WasteR_11_Backup.zip`

Material coverage: `PET`, `HDPE`, `LDPE_hrube`, `LDPE_farebne`, `PP_tenke`, `PS`, `OST_plast`, `paper`, `OCC_karton`, `napojove_kartony`, `contaminant`.

Inventory per bundle is listed in [outputs.md](outputs.md#dataset-inventory).

## Label Taxonomy

The dataset uses the 11 canonical labels listed above. Raw CVAT labels are mapped to these labels; `background` is implicit and is not a training category. The taxonomy is in [label_taxonomy.csv](../../../release/video_segmentation_dataset_v1/label_taxonomy.csv).

## Annotation Quality Checks

Each task is checked for:

- self-intersecting polygons
- extremely small polygons
- empty or malformed annotations
- labels that do not match the task
- severe truncation or occlusion

Usable frames with issues are kept with a QC flag; broken frames are excluded from the benchmark.

## Export Format

- full original images as inputs
- polygon annotations with class labels
- `COCO instance segmentation` format, with `_annotations.coco.json` in each of `train/`, `valid/`, and `test/`

COCO instance segmentation is supported by RF-DETR, Detectron2, MMDetection, and TorchVision, and keeps polygons, classes, areas, and boxes in one file. Layout details are in [input-spec.md](input-spec.md#training-ready-output-contract).

## Split Protocol

Splits are grouped by source video, not made randomly by image, so near-identical frames from the same capture do not leak across `train`, `valid`, and `test`. Grouping fields: `task_name`, `scene_group`, `video_id`.

## Benchmark Tracks

| Track | Content |
| --- | --- |
| `single_material_v1` | single-material instance segmentation of plastics |
| `mixtures_and_impurities_v1` | mixed-material and impurity scenes |
| `all_classes_v1` | combined development track over the full label set; published as `release/video_segmentation_dataset_v1` |

Evaluation metrics: `mAP@[.50:.95]`, `AP50`, per-class AP, and object-count summary. Only the `all_classes_v1` track is published; results of the models trained on it are reported in `D4.2`.

## Baseline Model

The baseline is `RF-DETR Seg Small` (`RFDETRSegSmall`); the best model in `D4.2` is `RF-DETR Seg Large` (`RFDETRSegLarge`, config `rfdetr_seg_all_classes_large.yaml`). Both read the COCO instance-segmentation layout directly and provides a transformer-based segmentation baseline with a reproducible configuration flow. Training instructions are in [training/README.md](../../../training/README.md#video_segmentation_dataset_v1).
