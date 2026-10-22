# Video Segmentation Input Specification

This page describes the raw annotation format used to prepare the video segmentation dataset and the training-ready format that the training scripts read. The raw image bundles and the full dataset are not published.

## Supported Raw Input Pattern

The raw source is a CVAT export with polygon annotations.

Each bundle can be in one of these shapes:

1. Single-task bundle:

```text
<bundle>.zip
  task.json
  annotations.json
  data/
    manifest.jsonl
    <image files>
```

2. Multi-task bundle:

```text
<bundle>.zip
  project.json
  task_0/
    task.json
    annotations.json
    data/
      manifest.jsonl
      <image files>
  task_1/
    ...
```

## Required Raw Files

Each task must contain:

- `task.json`
- `annotations.json`
- `data/manifest.jsonl`
- the referenced image files

## Required Annotation Semantics

Each annotated object provides:

- a polygon
- a class label
- a frame index that maps to an entry in `manifest.jsonl`

The canonical label set of the dataset is:

- `PET`
- `HDPE`
- `LDPE_hrube`
- `LDPE_farebne`
- `PP_tenke`
- `PS`
- `OST_plast`
- `OCC_karton`
- `paper`
- `napojove_kartony`
- `contaminant`

`background` is implicit and is not a training category.

## Naming Convention

Source frame names encode scene and video identity, which enables leakage-safe grouping, for example:

```text
frame_vid3_2.jpg
primesy_hdpe_v_pet_vid4_1.jpg
```

The important fields are:

- scene or mixture prefix
- video id
- frame id

## Training-Ready Output Contract

The training-ready dataset uses the COCO instance-segmentation format, which RF-DETR Seg reads directly.

Layout:

```text
<dataset_root>/
  train/
    _annotations.coco.json
    <images>.jpg
  valid/
    _annotations.coco.json
    <images>.jpg
  test/
    _annotations.coco.json
    <images>.jpg
```

Each COCO annotation includes:

- `image_id`
- `category_id`
- `segmentation`
- `bbox`
- `area`
- `iscrowd`

## Split Policy

Splits are not made randomly by image. They are grouped by source video or source scene so that near-identical frames from the same capture do not leak across `train`, `valid`, and `test`.

Minimum grouping fields:

- `task_name`
- `scene_group`
- `video_id`

## Published in This Repository

- this input specification
- the segmentation dataset landing page: [outputs.md](outputs.md)
- the RF-DETR Seg training script and configs
- a COCO preview sample in [samples/video_segmentation_dataset_v1/all_classes_mini_coco](../../../samples/video_segmentation_dataset_v1/all_classes_mini_coco/README.md)

## Not Published

- raw ZIP exports
- full image data
- internal conversion helpers
