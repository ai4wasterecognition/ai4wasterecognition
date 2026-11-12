# Video Segmentation Samples

This folder contains a small preview of the project image-segmentation dataset. The full dataset is published in [../../release/video_segmentation_dataset_v1/](../../release/video_segmentation_dataset_v1/README.md).

Current sample package:

- `all_classes_mini_coco/`

The sample shows the exact training-ready format of the dataset. It is not a benchmark release.

## all_classes_mini_coco

Contents:

- `train/`, `valid/`, `test/` split folders
- `_annotations.coco.json` in each split
- original sample images
- `label_taxonomy.csv`
- `sample_manifest.csv`

Current sample size:

- `6` images total
- `317` annotated instances total
- examples from both single-material and impurity or mixed scenes

This sample is suitable for:

- inspecting the COCO instance-segmentation layout
- validating training scripts with a dry run
- documenting the dataset structure

This sample is not suitable for:

- meaningful model training
- benchmark reporting
- class-balance analysis

For the full dataset description, see [../../docs/datasets/video_segmentation_dataset_v1/outputs.md](../../docs/datasets/video_segmentation_dataset_v1/outputs.md).
