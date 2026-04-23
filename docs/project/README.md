# Project Overview

This folder contains the project-level public structure derived from the official application.

The goal of the repository is to mirror the project logic from the application:

- work packages define the main output areas
- deliverables define the public-facing output containers
- dataset pages document real data releases without storing the full data in GitHub
- `samples/` holds only small, non-sensitive illustrative files

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
- the publication and dissemination index

It should not function as the main storage for full research datasets or internal consortium documentation.

## Structure

- [work-packages.md](work-packages.md) - normalized WP structure for the repository
- [milestones.md](milestones.md) - milestone map and expected public outputs

## Repository Convention

When a deliverable leads to a dataset:

1. create or update the dataset page in `docs/datasets/`
2. add a small example to `samples/` if useful
3. publish the real dataset externally
4. link the DOI and archive back into the dataset page

When a deliverable leads to a report or dissemination output:

1. create or update the relevant page in `docs/deliverables/`
2. add a public summary, abstract, or publication link
3. avoid uploading restricted internal files directly
