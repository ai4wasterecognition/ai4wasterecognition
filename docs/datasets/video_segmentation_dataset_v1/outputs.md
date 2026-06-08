# Video Segmentation Dataset v1

## Status

- local training-ready dataset prepared in private/local storage
- public GitHub mini-sample published in `samples/video_segmentation_dataset_v1/all_classes_mini_coco/`
- full public archive and DOI still pending

## Related Deliverables

- `D3.3` Experimental Data Collection Dataset
- `D4.2` Report on AI-Driven Video Data Analysis
- `D5.1` Generalisation, comparison and recommendation for future work

## Purpose

This page covers the public image-segmentation dataset family derived from annotated video frames and still images collected in the project.

The primary goal is to publish a curated instance-segmentation benchmark for sorted-waste materials and selected impurity scenarios, together with training-ready annotations, split definitions, and baseline training code.

For the detailed work plan, see [workplan.md](workplan.md).
For the required private/local input format, see [input-spec.md](input-spec.md).
For the current sample package, see [../../../samples/video_segmentation_dataset_v1/all_classes_mini_coco/README.md](../../../samples/video_segmentation_dataset_v1/all_classes_mini_coco/README.md).
For the public training scaffold, see [../../../training/README.md](../../../training/README.md).

## Current Source Inventory

The current private/local source inventory includes:

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

Current working totals:

- `232` annotated images
- `4,978` polygon instances
- single-material tasks for plastics
- mixed-material and impurity scenarios for downstream robustness evaluation

Current local prepared tracks:

- `all_classes_v1`
- `single_material_v1`
- `mixtures_and_impurities_v1`

Current public repository sample:

- `samples/video_segmentation_dataset_v1/all_classes_mini_coco/`
- `6` images total
- `317` annotated instances total
- `train/valid/test` layout with `_annotations.coco.json` in each split

## Recommended Public Dataset Shape

The main public release should use:

- original full images as inputs
- polygon-based annotations converted to `COCO instance segmentation`
- one benchmark for single-material instance segmentation
- one benchmark for mixed or impurity segmentation
- one optional combined `all_classes_v1` track for development, smoke tests, and unified training
- split definitions grouped by source video, not random image-level splits

The repository may also later include:

- a crop-based auxiliary dataset derived from single object instances
- additional preview packages in `samples/`
- additional training and evaluation scripts linked from `training/` or `scripts/`

## What This Repository Should Contain

- dataset description and inventory summary
- label taxonomy summary
- annotation format notes and export rules
- split protocol grouped by source video or source capture
- sample assets in `samples/video_segmentation_dataset_v1/all_classes_mini_coco/`
- compact repository release in `release/` if approved and practical
- external archive link once released, if needed
- baseline training scripts and benchmark notes
- input specification for private/local dataset preparation

## Relation to the Radar Dataset

- The project also publishes [`radar_dataset_from_multidetektor_measurement`](../radar_dataset_from_multidetektor_measurement/outputs.md), a 24 GHz radar dataset with numbered sample photographs.
- The segmentation dataset provides the image-recognition counterpart for project benchmarking and later radar-vs-video comparison studies.

## What Should Not Be The Primary Public Release

- raw video dumps if they exist outside the current frame exports
- duplicated crop-only datasets as the main benchmark
- random image-level train or test splits that leak near-identical scenes
- unreviewed label variants or temporary class names
- restricted internal annotation exports
- private workstation-specific conversion helpers that depend on non-public ZIP bundles

## DOI and Archive

- DOI: `TBD`
- URL: `TBD`
- version: `TBD`
