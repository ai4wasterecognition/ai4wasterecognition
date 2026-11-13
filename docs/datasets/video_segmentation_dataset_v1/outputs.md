# Video Segmentation Dataset v1

## Status

- full training-ready release published in [`release/video_segmentation_dataset_v1/`](../../../release/video_segmentation_dataset_v1/README.md)
- this is the dataset on which the RF-DETR Seg models reported in `D4.2` were trained
- personal data visible in some photos (handwriting, letters, invoices, address labels) were blurred before publication, see [Anonymization](#anonymization)
- DOI: [10.5281/zenodo.24187950](https://doi.org/10.5281/zenodo.24187950) (Zenodo archive of all project datasets, file `video_segmentation_dataset_v1.zip`)

## Related Deliverables

- `D3.3` Experimental Data Collection Dataset
- `D4.2` Report on AI-Driven Video Data Analysis
- `D5.1` Generalisation, comparison and recommendation for future work

## Purpose

This page describes the image-segmentation dataset built from annotated frames of videos recorded on the waste-sorting line in Michalovce. The dataset covers instance segmentation of sorted plastic and paper fractions and selected admixture (impurity) scenarios.

The repository publishes the full training-ready dataset in `COCO instance segmentation` format with the exact `train/valid/test` split used in `D4.2`, together with split and metadata tables, a data dictionary, checksums, and the RF-DETR Seg training code and configurations.

For the dataset preparation plan, see [workplan.md](workplan.md).
For the input and export format, see [input-spec.md](input-spec.md).
For the training workflow, see [../../../training/README.md](../../../training/README.md).

## Release Content

[`release/video_segmentation_dataset_v1/`](../../../release/video_segmentation_dataset_v1/README.md):

| File | Content |
| --- | --- |
| `train/`, `valid/`, `test/` | images and `_annotations.coco.json` per split |
| `splits.csv` | split assignment of every image with its grouping keys (task, scene group, video) |
| `metadata.csv` | per-image metadata: size, task, source video and frame, annotation count, labels, checksum |
| `label_taxonomy.csv` | 11 category ids and labels with descriptions |
| `data_dictionary.csv` | description of every CSV column and COCO field |
| `anonymization_regions.csv` | image regions blurred to remove personal data |
| `summary.json` | counts per split, category, and source task |
| `DATASET_CARD.md`, `README.md` | dataset card and release notes |
| `checksums.sha256` | SHA-256 of every file in the release |

## Dataset Inventory

Totals:

- `322` annotated images (video frames; 316 portrait 406 × 720 px, 6 landscape 1280 × 720 px)
- `7,124` polygon instances
- `11` classes: `PET`, `HDPE`, `LDPE_hrube`, `LDPE_farebne`, `PP_tenke`, `PS`, `OST_plast`, `OCC_karton`, `paper`, `napojove_kartony`, `contaminant`

Splits (grouped by source video, no leakage between splits):

| Split | Images | Instances | Video groups |
| --- | ---: | ---: | ---: |
| train | 226 | 5,054 | 76 |
| valid | 48 | 952 | 16 |
| test | 48 | 1,118 | 16 |
| **total** | **322** | **7,124** | **108** |

Source annotation tasks (CVAT bundles, not published):

| Task | Source bundle | Images | Instances |
| --- | --- | ---: | ---: |
| `01_pet` | `WasteR_01_02_03_Backup.zip` | 30 | 542 |
| `02_hdpe` | `WasteR_01_02_03_Backup.zip` | 30 | 810 |
| `03_ldpe_hrube` | `WasteR_01_02_03_Backup.zip` | 29 | 222 |
| `04_ldpe_farebne` | `WasteR_04_05_06_Backup.zip` | 15 | 112 |
| `05_pp_tenke` | `WasteR_04_05_06_Backup.zip` | 14 | 413 |
| `06_ps` | `WasteR_04_05_06_Backup.zip` | 15 | 231 |
| `07_ost_plast` | `WasteR_07_Backup.zip` | 15 | 449 |
| `08_occ_karton` | `WasteR_08_Backup.zip` | 30 | 334 |
| `09_paper` | `WasteR_09_Backup.zip` | 30 | 861 |
| `10_napojove_kartony` | `WasteR_10_Backup.zip` | 30 | 951 |
| `11_primesy` (admixtures) | `WasteR_11_Backup.zip` | 84 | 2,199 |
| **total** | 7 bundles | **322** | **7,124** |

Instances per class are listed in `summary.json` in the release.

## Note on the Figures in Report D4.2

Report `D4.2` quotes three different dataset sizes. The valid figure is **322 images / 7,124 polygon instances**, which is the size of this release.

| Place in D4.2 | Figure in D4.2 | Status | Explanation |
| --- | --- | --- | --- |
| Table of training data | 322 images / 7,124 instances | valid | Identical to this release (train 226 / valid 48 / test 48). The RF-DETR Seg and YOLO models in `D4.2` were trained and evaluated on exactly these images, annotations, and split. |
| Chapter 6, dataset inventory | 232 images / 4,978 instances | preliminary | Working inventory compiled before the annotation bundles of tasks `08_occ_karton`, `09_paper`, and `10_napojove_kartony` were added. These tasks are therefore missing from the inventory, although they are part of the training data. |
| Conclusion | 464 manually annotated frames | before final review | Number of frames annotated in CVAT before the final review of the dataset. In that review, 142 annotated frames were excluded to avoid near-duplicate frames and frames with uncertain labels. The remaining 322 frames form the training data and this release. |

Difference between the chapter 6 inventory and the training data:

| Task | Images | Instances |
| --- | ---: | ---: |
| `08_occ_karton` | 30 | 334 |
| `09_paper` | 30 | 861 |
| `10_napojove_kartony` | 30 | 951 |
| **added after the inventory** | **90** | **2,146** |
| inventory in chapter 6 | 232 | 4,978 |
| **training data = this release** | **322** | **7,124** |

Overview of the frame counts:

- about 4,000 frames extracted from the videos (every 30th frame, blurred and dark frames filtered out)
- 464 frames manually annotated in CVAT
- 142 annotated frames excluded in the final review (near-duplicates, uncertain labels)
- **322 frames with 7,124 manually drawn polygons** in the final dataset = training data of `D4.2` = this release

## Anonymization

The photos show sorted waste. Some frames, mainly of the `09_paper`, `08_occ_karton`, and `11_primesy` tasks, contained readable personal data: handwritten letters and notes, invoices and letters with an addressee block, postal forms, and parcel address labels. Before publication these regions were blurred (pixelated and Gaussian-blurred) so that the text cannot be read.

- the blurred boxes are listed in `anonymization_regions.csv` (file name, box, type of data removed)
- `metadata.csv` gives the number of blurred regions per image (`anonymized_regions`)
- annotations were not changed; blurring only affects pixels inside the listed boxes
- models in `D4.2` were trained on the original frames; the difference concerns only small paper regions and does not change the annotation set

## What This Repository Contains

- the full training-ready dataset: [`release/video_segmentation_dataset_v1/`](../../../release/video_segmentation_dataset_v1/README.md)
- a small preview sample: [`samples/video_segmentation_dataset_v1/all_classes_mini_coco/`](../../../samples/video_segmentation_dataset_v1/all_classes_mini_coco/README.md)
- input and export format: [input-spec.md](input-spec.md)
- dataset preparation plan: [workplan.md](workplan.md)
- release build script: [`scripts/video_segmentation_dataset_v1/build_release.py`](../../../scripts/video_segmentation_dataset_v1/build_release.py)
- RF-DETR Seg training script and configurations, including RF-DETR Seg Large used in `D4.2`: [`scripts/video_segmentation_dataset_v1/`](../../../scripts/video_segmentation_dataset_v1/README.md), [`training/configs/video_segmentation_dataset_v1/`](../../../training/configs/video_segmentation_dataset_v1/)

## What This Repository Does Not Contain

- raw video recordings and the source CVAT annotation ZIP bundles
- internal conversion helpers that read the non-public ZIP bundles
- trained model weights

## License and Citation

The dataset is licensed under CC BY 4.0, see [LICENSE-DATA](../../../LICENSE-DATA) and [docs/LICENSING.md](../../LICENSING.md). Cite it using [CITATION.cff](../../../CITATION.cff) and name the release `release/video_segmentation_dataset_v1`.

## Relation to the Radar Dataset

- The project publishes [`radar_dataset_from_multidetektor_measurement`](../radar_dataset_from_multidetektor_measurement/outputs.md), a 24 GHz radar dataset with numbered sample photographs.
- The segmentation dataset was used to train the image-recognition model whose results are compared with radar-based classification on the same samples.
