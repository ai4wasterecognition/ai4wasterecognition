# AI4WasteRecognition

This repository is the public-facing umbrella repository for the project `AI4WasteRecognition: AI-assisted recognition of sorted waste cleanliness`. It is intended to host project documentation, deliverable-linked outputs, dataset metadata, curated public releases, and links to externally archived datasets.

## Project Overview

AI4WasteRecognition explores innovative methods for recognition of different types of waste using AI-assisted sensing and data-driven analysis. The project is positioned in TRL 1-3 and focuses on early-stage research, concept validation, experimental proof-of-concept, and preparation of reusable research outputs for follow-up work.

The broader project is not limited to one sensing modality or one dataset. It is intended to support multiple research outputs related to waste recognition, waste cleanliness assessment, and AI-ready data resources.

The current local `WasteR` workspace is only one internal analysis environment behind this repository. It currently contains:

- exploratory and analytical notebooks for CW vs FMCW comparison
- environment and background-effect analyses
- object/material detectability analysis
- processed run-level tables derived from radar measurements

This public repository is intentionally broader in scope than the radar-only workspace, but narrower than the full private project storage. Raw measurement logs, large intermediate files, internal office documents, and unpublished working exports are excluded by default.

## Project Context

- Official project title: `AI4WasteRecognition: AI-assisted recognition of sorted waste cleanliness`
- Short title / acronym: `AI4 Waste recognition`
- Project code: `09I05-03-V02-00068`
- Funding: EU NextGenerationEU through the Recovery and Resilience Plan for Slovakia
- Call: `09I05-03-V02`, research projects focused on digitalization of the economy in TRL 1-3
- Consortium: Slovak University of Technology in Bratislava, Optima Ideas s.r.o., Sensoneo j. s. a., Asseco Central Europe, a. s., and the City of Michalovce

## Scope of This Repository

This repository is designed to contain:

- official project-level overview and publication-ready documentation
- descriptions of project outputs and deliverables
- one or more dataset cards describing public releases
- citation metadata for the repository
- instructions for GitHub and Zenodo publication
- curated public dataset files and/or links to externally archived datasets
- links to outputs published from different work packages or deliverables

This means the repository can later include, for example:

- radar-based research outputs and derived detectability datasets
- waste-management datasets prepared for downstream modeling
- segmentation datasets or annotation resources
- supporting documentation for deliverables, publications, and public releases

Radar measurements are therefore only one specific output stream of the project, not the definition of the whole repository.

## Research Themes

Based on the project description, the repository may eventually expose outputs related to:

- radar-based waste recognition experiments
- AI-ready datasets for waste classification and cleanliness analysis
- segmentation or annotation datasets
- benchmarking resources for comparing recognition approaches
- public documentation tied to project deliverables, publications, or dissemination outputs

## Recommended Structure

- `README.md`
  - project-level overview
- `docs/datasets/`
  - one markdown card per public dataset
- `docs/deliverables/`
  - public-facing notes or indexes for deliverable-related outputs
- `docs/PUBLISHING.md`
  - publication workflow for GitHub and Zenodo
- `public_dataset/`
  - optional location for smaller curated files that fit naturally in GitHub
- external DOI links
  - for larger or separately archived datasets

## Current Status

Status: public project repository scaffold under preparation.

Important notes before the first public release:

- do not publish raw radar logs unless the consortium explicitly approves it
- do not publish personal data or anything that can identify a person
- do not publish files that may weaken future IP protection or commercialization plans
- prefer DOI-backed dataset archives over pushing large working files directly to GitHub
- use this repository as the umbrella project repository even if some datasets live elsewhere

## Local Workspace vs Public Project Repository

The local workspace currently includes analysis notebooks and intermediate artifacts such as:

- `vystupy_analysis_dec_jan_v5.ipynb`
- `analysis_01_cw_vs_fmcw.ipynb`
- `analysis_02_environment_effect.ipynb`
- `analysis_03_object_detectability.ipynb`
- `processed/df_runs.parquet`
- `outputs/object_detectability/df_unique.parquet`

These files are useful internally, but the public project repository should expose only curated subsets with:

- stable column names
- a documented schema
- explicit versioning
- a clear license
- a DOI-backed archival copy

Not every internal analysis artifact should be published directly. In many cases, the correct public object will be:

- a derived dataset
- a dataset card plus DOI link
- a cleaned benchmark split
- or a deliverable-linked summary page

## Repository Structure

- `README.md` - project overview
- `DATASET_CARD.md` - initial generic dataset-release template
- `CITATION.cff` - citation metadata for GitHub
- `public_dataset/` - optional location for small curated release files
- `docs/datasets/` - dataset-specific public pages
- `docs/deliverables/` - deliverable/output placeholders
- `docs/PUBLISHING.md` - step-by-step GitHub and Zenodo publication guide
- `docs/LICENSING.md` - license decision guidance for code, data, and documentation

## Licensing

This repository currently contains an MIT `LICENSE` file for code and documentation scaffolding already created in GitHub.

Dataset licensing is not finalized here and should be decided separately for each public dataset release.

## Citation

If you use this repository or a dataset released from it, cite the repository metadata in `CITATION.cff` and the DOI-backed archive once available.

## Funding Acknowledgement

Funded by the EU NextGenerationEU through the Recovery and Resilience Plan for Slovakia.

## Release Workflow

1. Create the public GitHub repository under the official project name.
2. Publish the project scaffold and official project metadata.
3. Decide which datasets belong directly in GitHub and which should only be linked externally.
4. Finalize dataset card(s), `CITATION.cff`, and license choice.
5. Connect the repository to Zenodo if you want DOI-backed archived releases.
6. Create public releases for code, documents, and/or dataset packages as needed.

Detailed instructions are in [docs/PUBLISHING.md](docs/PUBLISHING.md).
