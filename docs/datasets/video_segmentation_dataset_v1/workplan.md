# Video Segmentation Work Plan

This work plan defines how the newly added annotated image data should be prepared as the next public project output under `AI4WasteRecognition`.

## Current Repository State

Already prepared:

- local training-ready segmentation dataset in private/local storage
- three local tracks: `all_classes_v1`, `single_material_v1`, `mixtures_and_impurities_v1`
- public mini COCO sample in `samples/video_segmentation_dataset_v1/all_classes_mini_coco/`
- public RF-DETR Seg training template, configs, and shell launcher

Still pending:

- full public archive outside local storage, if approved
- DOI-backed mirror, if needed
- baseline training run results and benchmark metrics

## Project Mapping

Primary deliverable alignment:

- `D3.3` Experimental Data Collection Dataset
- `D4.2` Report on AI-Driven Video Data Analysis

Secondary downstream alignment:

- `D5.1` Generalisation, comparison and recommendation for future work
- possible future publication outputs under `D5.3`

Interpretation:

- `D3.3` is represented in GitHub by the dataset landing page, input specification, and public mini sample, and would be fully satisfied by the curated public archive itself
- `D4.2` is represented by the segmentation methodology page, benchmark definition, public sample package, and training code

## Working Goal

Prepare a public, training-ready image segmentation dataset for sorted waste materials and impurity scenarios that is:

- annotation-consistent
- exportable to standard training formats
- safe against train or test leakage
- documented well enough for external reuse
- aligned with the GitHub publication model already used for the radar dataset

## Source Data Scope

Current known source bundles:

- `WasteR_01_02_03_Backup.zip`
- `WasteR_04_05_06_Backup.zip`
- `WasteR_07_Backup.zip`
- `WasteR_11_Backup.zip`

Current known material coverage:

- `PET`
- `HDPE`
- `LDPE_hrube`
- `LDPE_farebne`
- `PP_tenke`
- `PS`
- `OST_plast`
- `paper`
- `OCC_karton`
- `napojove_kartony`
- `contaminant`

The dataset naturally separates into two primary public benchmark families plus one combined development track:

1. `single_material_v1`
2. `mixtures_and_impurities_v1`
3. `all_classes_v1`

## Core Decisions

The main benchmark should use:

- original full images
- polygon annotations with class labels
- instance segmentation as the primary task

The main benchmark should not use:

- one-object crops as the primary public dataset
- pre-rendered mask visualizations as the only ground truth

Optional auxiliary data can later include:

- single-object crops with masks
- binary foreground masks
- class-specific subsets for ablation experiments

## Work Phases

Implementation note:

- phases `1` to `6` are already reflected in the current local dataset build and public documentation
- phase `7` is partially complete through the RF-DETR Seg training template
- phase `8` is partially complete through the public mini sample and landing pages

## Phase 1. Ingest and Inventory

Outputs:

- one local inventory table for every ZIP or task
- counts of images, frames, labels, and instances
- source grouping keys such as `bundle`, `task_name`, `video_id`, `frame_id`

Checks:

- identify missing frames
- identify duplicated filenames across bundles
- identify whether all tasks use the same image size and annotation convention

## Phase 2. Freeze Taxonomy

Outputs:

- one canonical label taxonomy file
- mapping from raw CVAT labels to release labels

Current expected canonical labels:

- `PET`
- `HDPE`
- `LDPE_hrube`
- `LDPE_farebne`
- `PP_tenke`
- `PS`
- `OST_plast`
- `paper`
- `OCC_karton`
- `napojove_kartony`
- `contaminant`

Checks:

- unify spelling and case
- decide whether `background` remains implicit or explicit
- decide whether `paper` and `OCC_karton` stay separate in v1
- decide whether impurity labels are universal across bundles or only mixture-specific

## Phase 3. Annotation QA

Outputs:

- one QC report per task or bundle
- one list of frames needing manual review

Checks:

- self-intersecting polygons
- extremely small polygons
- empty or malformed annotations
- labels that do not match task intent
- severe truncation or occlusion cases

Decision rule:

- if a frame is still usable, keep it with a QC flag
- if a frame is broken, exclude it from the public benchmark and record the reason

## Phase 4. Canonical Export

Outputs:

- `images/`
- `annotations/instances_*.json` in COCO format
- optional `masks/` only if needed for a secondary export
- `metadata.csv`
- `data_dictionary.csv`
- `label_taxonomy.csv`

Recommended canonical public format:

- `COCO instance segmentation`

Reason:

- widely supported by Detectron2, MMDetection, TorchVision, and many segmentation workflows
- preserves polygons, classes, areas, and boxes in one standard release

## Phase 5. Leakage-Safe Split Protocol

Outputs:

- `splits.csv`
- documented split policy

Required rule:

- split by source video group, not randomly by image

Minimum grouping fields:

- `bundle_id`
- `task_name`
- `video_id`

Recommended release splits:

- `train`
- `val`
- `test`

Optional robustness splits:

- leave-one-material-family-out
- train on single-material scenes, test on mixture scenes
- train on clean scenes, test on impurity scenes

## Phase 6. Benchmark Definition

Public benchmark tracks should be:

1. `single_material_instance_segmentation`
2. `mixtures_and_impurities_instance_segmentation`

Convenience development track:

- `all_classes_v1` for unified end-to-end training and smoke tests across the full label set

Optional secondary tasks:

- semantic segmentation
- binary contaminant detection
- object counting by class

Metrics:

- `mAP@[.50:.95]`
- `AP50`
- per-class AP
- object-count summary

## Phase 7. Baseline Training Package

Outputs:

- training config
- training script
- shell launcher
- environment notes
- optional evaluation script
- baseline results summary when runtime execution is completed

Current public baseline choice:

- `RF-DETR Seg Small`

Reason:

- direct compatibility with the current COCO export contract
- modern transformer-based segmentation baseline
- clean public training API and reproducible configuration flow

Optional later comparisons:

- `RF-DETR Seg Nano` for lighter runs
- a second baseline such as `Mask2Former` if a comparative study is needed

The current repository already includes the training template. The missing part is the executed benchmark run and its metrics.

## Phase 8. Public Release Packaging

Outputs:

- `docs/datasets/video_segmentation_dataset_v1/outputs.md`
- `samples/video_segmentation_dataset_v1/all_classes_mini_coco/`
- `release/video_segmentation_dataset_v1/` only if the full package later becomes small enough for GitHub
- `README.md`
- `DATASET_CARD.md` or dataset-specific card
- `checksums.sha256`
- `CITATION.cff` update if needed

Release decision:

- GitHub already keeps docs, training scaffolding, and the mini sample
- if the curated full dataset remains compact, it can later live directly in `release/`
- if it becomes too large, GitHub should keep docs and samples while the full archive moves to Zenodo or another research repository

## Recommended Immediate Sequence

1. Review the local `v1` export and confirm the final public archive scope.
2. Run any final annotation QA checks before external publication.
3. Decide whether the full dataset will live in GitHub `release/` or in an external archive.
4. Prepare dataset-specific release notes, checksums, and citation metadata for the full archive.
5. Install the RF-DETR runtime and execute the first baseline training run.
6. Publish the first baseline metrics under `D4.2`.

## Recommended Repository Deliverables

Minimum repository artifacts for this output:

- one dataset landing page
- one work plan page
- one input specification page
- one public sample package
- one training baseline script
- one release folder or external archive link for the full dataset when approved

## Acceptance Criteria For v1

Repository-side readiness is already achieved when:

- the landing page is published
- the input specification is published
- the public mini COCO sample is published
- the RF-DETR Seg training template is published
- the GitHub documentation is aligned with the current repository state

The full segmentation archive is ready when:

- all source bundles are inventoried
- the taxonomy is frozen
- the COCO export passes validation
- the split protocol is fixed and documented
- at least one baseline model run is executed on the release
- the final release location and citation metadata are fixed
