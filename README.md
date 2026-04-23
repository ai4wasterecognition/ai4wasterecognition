# AI4WasteRecognition

This repository is the public-facing project scaffold for the local `WasteR` analysis workspace. It is intended to host project documentation, reproducible analysis artifacts, and links to one or more curated public datasets derived from radar-based waste recognition experiments.

## Overview

AI4WasteRecognition explores whether 24 GHz radar sensing, combined with downstream analytics and AI methods, can support recognition of waste composition and waste cleanliness under controlled and semi-realistic measurement conditions.

The current local workspace contains:

- exploratory and analytical notebooks for CW vs FMCW comparison
- environment and background-effect analyses
- object/material detectability analysis
- processed run-level tables derived from radar measurements

This public repository is intentionally narrower than the full local workspace. Raw measurement logs, large intermediate files, internal office documents, and unpublished working exports are excluded by default.

## Project Context

- Official project title: `AI4WasteRecognition: AI-assisted recognition of sorted waste cleanliness`
- Short title / acronym: `AI4 Waste recognition`
- Project code: `09I05-03-V02-00068`
- Funding: EU NextGenerationEU through the Recovery and Resilience Plan for Slovakia
- Call: 09I05-03-V02, research projects focused on digitalization of the economy in TRL 1-3
- Consortium: Slovak University of Technology in Bratislava, Optima Ideas s.r.o., Sensoneo j. s. a., Asseco Central Europe, a. s., and the City of Michalovce

## What Will Be Published Here

This repository is designed to contain:

- official project overview and publication-ready documentation
- one or more dataset cards describing public releases
- citation metadata for the repository
- instructions for GitHub and Zenodo publication
- curated public dataset files and/or links to externally archived datasets

Recommended project-level structure:

- `public_dataset/`
  - small curated files that fit naturally in GitHub
- `docs/datasets/`
  - one markdown card per published dataset
- `docs/links/`
  - DOI and landing-page links for datasets stored in Zenodo or elsewhere

## Current Status

Status: public release scaffold under preparation.

Important notes before the first public release:

- do not publish raw radar logs unless the consortium explicitly approves it
- do not publish personal data or anything that can identify a person
- do not publish files that may weaken future IP protection or commercialization plans
- prefer DOI-backed dataset archives over pushing large working files directly to GitHub
- use this repository as the umbrella project repository even if some datasets live elsewhere

## Local Workspace vs Public Release

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

## Repository Structure

- `README.md` - project overview
- `DATASET_CARD.md` - initial dataset-release template
- `CITATION.cff` - citation metadata for GitHub
- `public_dataset/` - optional location for small curated release files
- `docs/PUBLISHING.md` - step-by-step GitHub and Zenodo publication guide
- `docs/LICENSING.md` - license decision guidance for code, data, and documentation

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
