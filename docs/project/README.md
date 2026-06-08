# Project Overview

This folder contains the project-level public structure derived from the official application.

The goal of the repository is to mirror the project logic from the application:

- work packages define the main output areas
- deliverables define the public-facing output containers
- dataset pages document real data releases, whether they are hosted in this repository or mirrored externally
- `samples/` holds small illustrative files and previews for larger dataset families

Current examples in this repository:

- full public radar release in `release/radar_dataset_v1/`
- public segmentation mini sample in `samples/video_segmentation_dataset_v1/all_classes_mini_coco/`
- local-only full segmentation dataset documented through specs and training templates

## Official Project Context

- Title: `AI4WasteRecognition: AI-assisted recognition of sorted waste cleanliness`
- Short title: `AI4 Waste recognition`
- Project code: `09I05-03-V02-00068`
- Funding line: Recovery and Resilience Plan for Slovakia, call `09I05-03-V02`

## Public Repository Role

This repository should function as:

- the public project landing page
- the deliverables index
- the dataset registry
- the host for approved compact public dataset releases
- the host for public sample packages that document larger local-only datasets
- the publication and dissemination index

It should not function as the main storage for raw internal data, very large archives, or internal consortium documentation.

## Structure

- [work-packages.md](work-packages.md) - normalized WP structure for the repository
- [milestones.md](milestones.md) - milestone map and expected public outputs

## Repository Convention

When a deliverable leads to a dataset:

1. create or update the dataset page in `docs/datasets/`
2. decide whether the curated public release belongs in `release/` or only in an external archive
3. add a small example to `samples/` if useful
4. if an archival mirror exists, link the DOI back into the dataset page

When a deliverable leads to a report or dissemination output:

1. create or update the relevant page in `docs/deliverables/`
2. add a public summary, abstract, or publication link
3. avoid uploading restricted internal files directly
