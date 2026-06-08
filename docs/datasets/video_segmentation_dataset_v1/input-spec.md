# Video Segmentation Input Specification

This note describes the expected local inputs for preparing a segmentation training dataset. It is intended for private/local dataset preparation, not as a public release artifact containing the raw image data itself.

## Goal

The public repository should document:

- the expected raw annotation format
- the expected training-ready dataset format
- the sample training script

The public repository should not require publishing:

- the raw image ZIP bundles
- the full private image archive
- private local conversion helpers tied to one workstation

## Supported Raw Input Pattern

The local raw source is expected to be a CVAT-style export with polygon annotations.

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

Each annotated object should provide:

- a polygon
- a class label
- a frame index that maps to an entry in `manifest.jsonl`

The raw label set can be project-specific, but for `WasteR` the current canonical label family is:

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

`background` can remain implicit and does not need to become a foreground training category.

## Recommended Naming Convention

To enable leakage-safe grouping, the source frame names should encode scene/video identity, for example:

```text
frame_vid3_2.jpg
primesy_hdpe_v_pet_vid4_1.jpg
```

The important fields are:

- scene or mixture prefix
- video id
- frame id

## Training-Ready Output Contract

The training-ready local dataset should be prepared in COCO instance-segmentation format because this works cleanly with RF-DETR Seg.

Expected layout:

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

Each COCO annotation should include:

- `image_id`
- `category_id`
- `segmentation`
- `bbox`
- `area`
- `iscrowd`

## Split Policy

Do not split randomly by image.

Use grouping by source video or source scene so that near-identical frames from the same capture do not leak across `train`, `valid`, and `test`.

Minimum grouping fields:

- `task_name`
- `scene_group`
- `video_id`

## What The Public Repo Should Include

- this input specification
- the segmentation dataset landing page
- a sample RF-DETR Seg training script
- sample configs
- a tiny but real COCO preview package in `samples/video_segmentation_dataset_v1/all_classes_mini_coco/`

## What Stays Local

- raw ZIP exports
- full image data
- workstation-specific conversion helpers
- local build outputs
