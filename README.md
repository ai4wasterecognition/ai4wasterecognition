# AI4WasteRecognition

This repository is the public umbrella repository for the project `AI4WasteRecognition: AI-assisted recognition of sorted waste cleanliness`.

It is structured from the official project application and its deliverables, not from one internal analysis workspace. Radar measurements are only one output stream. The repository is meant to aggregate project information, deliverable-linked public outputs, dataset landing pages, directly hosted public dataset releases when practical, sample files, and links to externally archived datasets.

## Project Identity

- Official project title: `AI4WasteRecognition: AI-assisted recognition of sorted waste cleanliness`
- Short title: `AI4 Waste recognition`
- Project code: `09I05-03-V02-00068`
- Funding: EU NextGenerationEU through the Recovery and Resilience Plan for Slovakia
- Call: `09I05-03-V02`
- Consortium: Slovak University of Technology in Bratislava, Optima Ideas s.r.o., Sensoneo j. s. a., Asseco Central Europe, a. s., and the City of Michalovce

## Public Output Model

This GitHub repository is intended to publish:

- project overview pages derived from the application
- work-package and deliverable indexes
- public summaries of reports, methods, and outputs
- dataset cards and dataset landing pages
- versioned public dataset releases when they are small enough, non-sensitive, and consortium-approved
- `samples/` for lightweight previews and for future larger datasets
- links to DOI-backed archives where external archival release is preferred
- publication and dissemination links

This GitHub repository can host curated benchmark-ready datasets directly when size and sensitivity allow it. For long-term archival, DOI minting, or larger future datasets, Zenodo or another research repository remains the recommended companion archive.

## Repository Layout

- [docs/project/README.md](docs/project/README.md) - project overview and repository model
- [docs/project/work-packages.md](docs/project/work-packages.md) - work-package structure derived from the application
- [docs/project/milestones.md](docs/project/milestones.md) - milestone map for public outputs
- [docs/deliverables/README.md](docs/deliverables/README.md) - full deliverables index
- [docs/deliverables/KPB1.md](docs/deliverables/KPB1.md) - project management outputs
- [docs/deliverables/KPB2.md](docs/deliverables/KPB2.md) - research and review outputs
- [docs/deliverables/KPB3.md](docs/deliverables/KPB3.md) - laboratory and data collection outputs
- [docs/deliverables/KPB4.md](docs/deliverables/KPB4.md) - analysis outputs
- [docs/deliverables/KPB5.md](docs/deliverables/KPB5.md) - evaluation and publication outputs
- [docs/datasets/README.md](docs/datasets/README.md) - dataset registry and publication rules
- [docs/datasets/radar-publication-and-modeling.md](docs/datasets/radar-publication-and-modeling.md) - concrete radar publication and transformer baseline plan
- [docs/publications/README.md](docs/publications/README.md) - publication index placeholder
- [samples/README.md](samples/README.md) - policy for repository-hosted samples
- [training/README.md](training/README.md) - export and training workflow for radar data
- [DATASET_CARD.md](DATASET_CARD.md) - generic dataset-card template
- [docs/PUBLISHING.md](docs/PUBLISHING.md) - GitHub and Zenodo publication workflow
- [docs/LICENSING.md](docs/LICENSING.md) - licensing guidance for code, docs, and data

## Deliverable-Oriented Structure

The application defines five work packages:

- `KPB1` Project Management
- `KPB2` Tech and AI Research
- `KPB3` Laboratory Experiment
- `KPB4` Data analysis
- `KPB5` Evaluation

This repository follows that same structure. Each work package has its own deliverable page and expected public representation. That keeps the repository aligned with the official project plan even if future outputs include radar, waste-management, segmentation, or multidetector resources.

## Dataset Policy

The current publication policy for this repository is:

- public datasets may be versioned directly in GitHub when they are compact, curated, and approved for release
- the current radar training release is published in [release/radar_dataset_v1](release/radar_dataset_v1/README.md)
- `samples/` remains for lightweight previews and for dataset families that are not fully hosted in the repository
- one landing page per dataset family in `docs/datasets/`
- one repository path and, when available, one archival DOI or external mirror per real dataset release
- clear linkage between each dataset and the relevant deliverable(s)

## Important Publication Constraints

- Do not publish raw logs, sensitive measurements, or private consortium material without approval.
- Do not publish personal data or anything that could identify a person.
- Do not publish assets that may weaken future IP protection or commercialization.
- Use repository-hosted releases only for curated public datasets. Larger, citation-critical, or long-term archival copies should also be mirrored in Zenodo or another research archive.

## Citation

If you use this repository or a dataset released from it, cite the repository metadata in `CITATION.cff` and the archival DOI when one is added.
