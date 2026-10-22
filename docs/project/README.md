# Project Overview

This folder contains the project-level structure of the repository, derived from the official application.

The repository follows the project logic from the application:

- work packages define the main output areas
- deliverables are listed per work package, with their status in this repository
- dataset pages document the published data releases
- `samples/` holds small previews of each dataset

## Official Project Context

- Title: `AI4WasteRecognition: AI-assisted recognition of sorted waste cleanliness`
- Short title: `AI4 Waste recognition`
- Project code: `09I05-03-V02-00068`
- Funding line: Recovery and Resilience Plan for Slovakia, call `09I05-03-V02`

## What the Repository Contains

- the public project landing page ([README.md](../../README.md))
- the deliverables index ([docs/deliverables/](../deliverables/README.md))
- the dataset registry ([docs/datasets/](../datasets/README.md))
- two full radar dataset releases in `release/radar_dataset_v1/` and `release/radar_dataset_from_multidetektor_measurement/`
- a preview sample of the video segmentation dataset in `samples/video_segmentation_dataset_v1/all_classes_mini_coco/`; the full segmentation dataset is not published
- export, training, and inference code in `scripts/` and `training/`
- the publication index ([docs/publications/](../publications/README.md))

The repository does not contain raw internal data, internal reports, or internal consortium documentation. See [docs/PUBLISHING.md](../PUBLISHING.md).

## Structure

- [work-packages.md](work-packages.md) - work-package structure
- [milestones.md](milestones.md) - milestone map and related repository content
