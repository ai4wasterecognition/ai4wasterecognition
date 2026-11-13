# Dataset Card: Video Segmentation Dataset v1

## Dataset Name

`AI4WasteRecognition Video Segmentation Dataset v1` (`video_segmentation_dataset_v1`)

## Status

Public release available.

## Related Deliverables

- `D3.3` Experimental Data Collection Dataset
- `D4.2` Report on AI-Driven Video Data Analysis
- `D5.1` Generalisation, comparison and recommendation for future work

## Summary

Instance-segmentation dataset of sorted waste on a sorting line. It supports the AI-driven video analysis in `D4.2`: detection and segmentation of sorted plastic and paper fractions and of admixtures (impurities) in them. It is the exact dataset (images, annotations, and split) on which the RF-DETR Seg Small and Large and the YOLO segmentation models in `D4.2` were trained and evaluated.

## Repository Release or External Archive

- repository release path: `release/video_segmentation_dataset_v1/`
- DOI: [10.5281/zenodo.24187950](https://doi.org/10.5281/zenodo.24187950) (Zenodo archive of all project datasets, file `video_segmentation_dataset_v1.zip`)
- landing page: [docs/datasets/video_segmentation_dataset_v1/outputs.md](../../docs/datasets/video_segmentation_dataset_v1/outputs.md)
- version: `v1`

## Unit of Observation

One video frame (JPEG image) with polygon instance annotations.

## Files

- `train/`, `valid/`, `test/` with images and `_annotations.coco.json`
- `splits.csv`, `metadata.csv`, `label_taxonomy.csv`, `data_dictionary.csv`, `anonymization_regions.csv`
- `summary.json`, `checksums.sha256`, `README.md`, this card

## Size

| Split | Images | Instances |
| --- | ---: | ---: |
| train | 226 | 5,054 |
| valid | 48 | 952 |
| test | 48 | 1,118 |
| total | 322 | 7,124 |

Images are 406 × 720 px (316 portrait frames) or 1280 × 720 px (6 landscape frames).

## Classes

| id | label | description |
| ---: | --- | --- |
| 1 | `PET` | PET bottles, clear and colored |
| 2 | `HDPE` | HDPE containers, white and colored |
| 3 | `LDPE_hrube` | thick LDPE films |
| 4 | `LDPE_farebne` | colored LDPE films |
| 5 | `PP_tenke` | thin PP films |
| 6 | `PS` | polystyrene |
| 7 | `OST_plast` | other rigid plastics |
| 8 | `OCC_karton` | corrugated cardboard (OCC) |
| 9 | `paper` | mixed paper |
| 10 | `napojove_kartony` | beverage cartons |
| 11 | `contaminant` | admixture / foreign object in a sorted fraction |

`background` is implicit and is not a category.

## Source and Collection Context

About 70 videos of sorted waste fractions were recorded on the waste-sorting line in Michalovce with a handheld camera above the material. Separate series show single fractions (tasks `01`-`10`) and fractions with deliberately added admixtures (task `11_primesy`, e.g. paper in PET, PET in cardboard, HDPE in PET). Frames were extracted from the videos and selected frames were annotated with polygons in CVAT. Seven CVAT bundles (`WasteR_01_02_03`, `04_05_06`, `07`, `08`, `09`, `10`, `11`) form the dataset.

## Processing Summary

1. Frame extraction from the videos and selection of sharp frames.
2. Manual polygon annotation in CVAT according to the 11-class taxonomy (464 frames).
3. Quality checks: self-intersecting or tiny polygons, empty or malformed annotations, labels not matching the task.
4. Final review: 142 annotated frames excluded to avoid near-duplicate frames and frames with uncertain labels; 322 frames remain.
5. Conversion to COCO instance segmentation; bounding boxes and areas computed from the polygons.
6. Split by source video group (`task`, `scene_group`, `video_id`) with a fixed seed (70/15/15 % of groups), so near-identical frames of one video never appear in two splits.
7. Anonymization: regions with readable personal data blurred (see below).
8. Release packaging with metadata tables and checksums (`scripts/video_segmentation_dataset_v1/build_release.py`).

## Core Variables or Assets

- images (JPEG)
- per instance: polygon (`segmentation`), `bbox`, `area`, `category_id`, `iscrowd = 0`
- per image: split, task, scene group, source video and frame, annotation count, labels present

## Recommended Use and Limitations

- instance segmentation and detection of sorted-waste materials and admixtures
- small dataset (322 images); class balance differs between splits, see `summary.json`
- frames come from one site and one camera setup; generalisation to other lines is not guaranteed
- several frames of the same video are near-duplicates; always respect the provided split

## Recommended Exclusions

Not published: raw video recordings, source CVAT bundles, internal conversion helpers, trained model weights.

## Ethics, Privacy, and IP Review

- personal data: the frames show waste, no persons. Readable personal data on discarded documents (handwritten letters and notes, invoices and letters with an addressee block, postal forms, parcel address labels) were blurred before publication; the boxes are listed in `anonymization_regions.csv`. Printed commercial content (packaging, brands, supermarket flyers, newspapers) was not blurred.
- annotations were not changed by the anonymization; the D4.2 models were trained on the original frames
- no confidential partner information is included
- release approved by the consortium for publication under CC BY 4.0

## Licensing

CC BY 4.0, see [LICENSE-DATA](../../LICENSE-DATA) and [docs/LICENSING.md](../../docs/LICENSING.md). Code: MIT.

## Citation

Use [CITATION.cff](../../CITATION.cff) and name the release `release/video_segmentation_dataset_v1`, DOI [10.5281/zenodo.24187950](https://doi.org/10.5281/zenodo.24187950).
