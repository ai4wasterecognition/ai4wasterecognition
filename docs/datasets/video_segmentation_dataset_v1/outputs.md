# Video Segmentation Dataset v1

## Status

- preview sample published in `samples/video_segmentation_dataset_v1/all_classes_mini_coco/`
- the full dataset is not published; it is kept in project-internal storage

## Related Deliverables

- `D3.3` Experimental Data Collection Dataset
- `D4.2` Report on AI-Driven Video Data Analysis
- `D5.1` Generalisation, comparison and recommendation for future work

## Purpose

This page describes the image-segmentation dataset built from annotated video frames and still images collected in the project. The dataset covers instance segmentation of sorted-waste materials and selected impurity scenarios.

This repository publishes a preview sample of the dataset in the exact training-ready format, together with the input specification and baseline training code. The full dataset is not published.

For the dataset preparation plan, see [workplan.md](workplan.md).
For the input and export format, see [input-spec.md](input-spec.md).
For the preview sample, see [../../../samples/video_segmentation_dataset_v1/all_classes_mini_coco/README.md](../../../samples/video_segmentation_dataset_v1/all_classes_mini_coco/README.md).
For the training workflow, see [../../../training/README.md](../../../training/README.md).

## Dataset Inventory

The full (non-public) dataset consists of:

- `WasteR_01_02_03_Backup.zip`
  - tasks `01_PET`, `02_HDPE`, `03_LDPE_HRUBE`
  - `89` images total
  - annotated instances: `PET=542`, `HDPE=810`, `LDPE_hrube=222`
- `WasteR_04_05_06_Backup.zip`
  - tasks `04_LDPE_FAREBNE`, `05_PP_TENKE`, `06_PS`
  - `44` images total
  - annotated instances: `LDPE_farebne=112`, `PP_tenke=413`, `PS=231`
- `WasteR_07_Backup.zip`
  - task `07_OST_PLAST`
  - `15` images total
  - annotated instances: `OST_plast=449`
- `WasteR_11_Backup.zip`
  - task `11_PRIMESY`
  - `84` images total
  - annotated instances: `PET=499`, `paper=753`, `OCC_karton=275`, `napojove_kartony=235`, `contaminant=437`

Totals:

- `232` annotated images
- `4,978` polygon instances
- single-material tasks for plastics
- mixed-material and impurity scenarios for downstream robustness evaluation

Prepared training tracks (non-public):

- `all_classes_v1`
- `single_material_v1`
- `mixtures_and_impurities_v1`

Published preview sample:

- `samples/video_segmentation_dataset_v1/all_classes_mini_coco/`
- `6` images total
- `317` annotated instances total
- `train/valid/test` layout with `_annotations.coco.json` in each split

## What This Repository Contains

- dataset description and inventory summary (this page)
- preview sample in [`samples/video_segmentation_dataset_v1/all_classes_mini_coco/`](../../../samples/video_segmentation_dataset_v1/all_classes_mini_coco/README.md): images, `COCO instance segmentation` annotations per split, `label_taxonomy.csv`, and `sample_manifest.csv`
- input and export format of the dataset: [input-spec.md](input-spec.md)
- dataset preparation plan: [workplan.md](workplan.md)
- RF-DETR Seg training script and configurations: [`scripts/video_segmentation_dataset_v1/`](../../../scripts/video_segmentation_dataset_v1/README.md), [`training/configs/video_segmentation_dataset_v1/`](../../../training/configs/video_segmentation_dataset_v1/)

## What This Repository Does Not Contain

- the full annotated image dataset (232 images, 4,978 polygon instances)
- raw video recordings and the source annotation ZIP bundles
- internal conversion helpers that depend on the non-public ZIP bundles

## Relation to the Radar Dataset

- The project publishes [`radar_dataset_from_multidetektor_measurement`](../radar_dataset_from_multidetektor_measurement/outputs.md), a 24 GHz radar dataset with numbered sample photographs.
- The segmentation dataset was used to train the image-recognition model whose results are compared with radar-based classification on the same samples.
