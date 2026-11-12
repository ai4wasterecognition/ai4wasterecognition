# KPB4 - Data analysis

This page lists analytical deliverables and what this repository contains for each of them.

| Code | Deliverable | Delivery | Access | Content in this repository |
| --- | --- | --- | --- | --- |
| D4.1 | Report on AI-Driven Radar Data Analysis | M24 | N | radar dataset, transformer training code and configs ([analysis-outputs.md](../datasets/radar_dataset_v1/analysis-outputs.md)); report not published (internal) |
| D4.2 | Report on AI-Driven Video Data Analysis | M24 | V | video segmentation dataset [release/video_segmentation_dataset_v1](../../release/video_segmentation_dataset_v1/README.md) (training data of the models in `D4.2`), input specification, RF-DETR Seg Small and Large training code and configs ([outputs.md](../datasets/video_segmentation_dataset_v1/outputs.md)); report not published |
| D4.3 | Report on AI-Driven multidetector Data Analysis | M24 | V | published radar dataset with sample photos [release/radar_dataset_from_multidetektor_measurement](../../release/radar_dataset_from_multidetektor_measurement/README.md), landing page [outputs.md](../datasets/radar_dataset_from_multidetektor_measurement/outputs.md), training and inference code |
| D4.4 | Interim report on the implementation and achievements of the project | M24 | V | not published in this repository |

## What This Repository Contains

- radar dataset from multidetector measurement (`D4.3`): [release/radar_dataset_from_multidetektor_measurement](../../release/radar_dataset_from_multidetektor_measurement/README.md), landing page [outputs.md](../datasets/radar_dataset_from_multidetektor_measurement/outputs.md)
- radar training and inference code for both radar datasets: [scripts/](../../scripts/), [training/](../../training/README.md)
- video segmentation dataset and training code (`D4.2`): [release/video_segmentation_dataset_v1](../../release/video_segmentation_dataset_v1/README.md), landing page [outputs.md](../datasets/video_segmentation_dataset_v1/outputs.md)

## Not Published

- raw video recordings and source annotation bundles of the video segmentation dataset
- the analysis reports `D4.1`-`D4.4`
