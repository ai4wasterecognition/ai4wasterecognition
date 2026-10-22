# WasteR Segmentation Mini Sample

This is the public mini sample of the WasteR image-segmentation dataset. The full dataset is not published.

It mirrors the same `COCO instance segmentation` layout expected by the RF-DETR Seg training template, but contains only a tiny subset for inspection and dry-run validation.

## Contents

- `train/`, `valid/`, `test/`
- `_annotations.coco.json` in each split
- original sample images
- `label_taxonomy.csv`
- `sample_manifest.csv`

## Current Size

- `6` images
- `317` annotated instances

## Intended Use

- inspect the public sample format
- verify loaders and training wrappers
- show the structure of the full dataset

## Not Intended For

- full training
- benchmark reporting
- model comparison

For the dataset description and format notes, see:

- [../../../docs/datasets/video_segmentation_dataset_v1/outputs.md](../../../docs/datasets/video_segmentation_dataset_v1/outputs.md)
- [../../../docs/datasets/video_segmentation_dataset_v1/input-spec.md](../../../docs/datasets/video_segmentation_dataset_v1/input-spec.md)
