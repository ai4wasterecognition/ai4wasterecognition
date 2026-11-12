# AI4WasteRecognition Video Segmentation Dataset v1

Instance-segmentation dataset of sorted plastic and paper waste and admixture scenes, built from annotated frames of videos recorded on the waste-sorting line in Michalovce. This is the training-ready dataset on which the RF-DETR Seg models in deliverable `D4.2` were trained.

- format: `COCO instance segmentation` (RF-DETR, Detectron2, MMDetection, TorchVision)
- 322 images, 7,124 polygon instances, 11 classes
- split: train 226 / valid 48 / test 48 images, grouped by source video (no leakage)
- license: CC BY 4.0, see [LICENSE-DATA](../../LICENSE-DATA)
- landing page: [docs/datasets/video_segmentation_dataset_v1/outputs.md](../../docs/datasets/video_segmentation_dataset_v1/outputs.md)
- dataset card: [DATASET_CARD.md](DATASET_CARD.md)

## Files

| File | Content |
| --- | --- |
| `train/`, `valid/`, `test/` | images and `_annotations.coco.json` per split |
| `splits.csv` | split of every image with its grouping keys |
| `metadata.csv` | per-image metadata and image checksum |
| `label_taxonomy.csv` | category ids, labels, and descriptions |
| `data_dictionary.csv` | description of all CSV columns and COCO fields |
| `anonymization_regions.csv` | regions blurred to remove personal data |
| `summary.json` | counts per split, class, and source task |
| `checksums.sha256` | SHA-256 of every file (`sha256sum -c checksums.sha256`) |

## Quick Start

```bash
pip install "rfdetr[train,loggers]"
python scripts/video_segmentation_dataset_v1/train_rfdetr.py \
  --config training/configs/video_segmentation_dataset_v1/rfdetr_seg_all_classes_large.yaml
```

```python
import json
coco = json.load(open("release/video_segmentation_dataset_v1/train/_annotations.coco.json"))
print(len(coco["images"]), len(coco["annotations"]), [c["name"] for c in coco["categories"]])
```

## How It Was Built

The release is generated from the internal training-ready COCO export by [`scripts/video_segmentation_dataset_v1/build_release.py`](../../scripts/video_segmentation_dataset_v1/build_release.py). Images and annotation files are copied unchanged, except for regions with personal data, which are blurred (see `anonymization_regions.csv`).

## Citation

Cite using [CITATION.cff](../../CITATION.cff) and name the release `release/video_segmentation_dataset_v1`. The GitHub repository is the reference location of this release.
