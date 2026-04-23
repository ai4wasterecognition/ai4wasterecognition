# Publishing Guide

This repository should be published as a project hub with a hybrid dataset model.

Recommended split:

- GitHub for project pages, deliverable mapping, dataset cards, training code, and compact public dataset releases that are suitable for normal Git versioning
- Zenodo or another research repository for DOI-backed archival copies, larger future datasets, or releases that are not practical to keep directly in GitHub

## 1. Repository Identity

Use the official project identity rather than a dataset-specific name.

- repository name: `AI4WasteRecognition`
- description: `AI4WasteRecognition: AI-assisted recognition of sorted waste cleanliness`

## 2. First Public Commit

From the project root:

```bash
git add README.md DATASET_CARD.md CITATION.cff .gitignore docs samples
git commit -m "Restructure repository around project deliverables"
```

## 3. Keep GitHub Focused on Public Documentation and Compact Releases

The default public contents should be:

- project overview pages
- work-package and deliverable indexes
- dataset landing pages in `docs/datasets/`
- publication indexes
- small examples in `samples/`
- versioned dataset releases in `release/` when they are approved, compact, and benchmark-ready

The default non-GitHub contents should be:

- raw measurement exports
- large media collections
- restricted consortium documents
- dataset packages that are too large or too dynamic for normal Git history

## 4. Publish Dataset Families via Landing Pages

For each real dataset release:

1. create or update one dataset page in `docs/datasets/`
2. decide whether the dataset should live directly in `release/<dataset-version>/` or only in an external archive
3. add a short sample or schema preview in `samples/` if needed
4. if you archive externally, add the DOI and download link back into the dataset page
5. if the dataset is hosted in GitHub, document the release path and file layout in the dataset page

## 5. GitHub Metadata

On GitHub, fill in:

- repository description
- topics such as `waste`, `open-science`, `dataset-registry`, `radar-sensing`, `computer-vision`, `segmentation`
- the citation widget from `CITATION.cff`

## 6. Release Strategy

Recommended release order:

1. project scaffold and deliverable structure
2. first public documentation release
3. first dataset landing page
4. first repository-hosted or external dataset release
5. optional DOI-backed archival mirror
6. project release notes pointing to the release location

## 7. Optional Zenodo Flow

1. create or log into Zenodo
2. connect the GitHub repository
3. enable the repository
4. create a GitHub release
5. let Zenodo archive the release and mint a DOI

After the DOI is available:

- add it to the relevant dataset page
- update `CITATION.cff` if needed
- include it in release notes and README links
