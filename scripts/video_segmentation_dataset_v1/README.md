# Video Segmentation Dataset v1 Scripts

Scripts in this folder:

- `train_rfdetr.py` - RF-DETR Seg training wrapper for the dataset in COCO instance-segmentation format (Small and Large)
- `build_release.py` - builds [`release/video_segmentation_dataset_v1/`](../../release/video_segmentation_dataset_v1/README.md) from the internal training-ready COCO export: split and metadata tables, data dictionary, anonymization of personal data, checksums

The dataset is published in [`release/video_segmentation_dataset_v1/`](../../release/video_segmentation_dataset_v1/README.md); the internal helper that converts the raw CVAT bundles is not published. The input and export format is documented in [../../docs/datasets/video_segmentation_dataset_v1/input-spec.md](../../docs/datasets/video_segmentation_dataset_v1/input-spec.md). The `all_classes` configs point to the release; a quick dry run is also possible with the preview sample in [../../samples/video_segmentation_dataset_v1/all_classes_mini_coco/](../../samples/video_segmentation_dataset_v1/all_classes_mini_coco/README.md).
