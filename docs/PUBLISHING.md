# Publishing Guide

This repository should be published as a project hub, not as a full dataset dump.

Recommended split:

- GitHub for project pages, deliverable mapping, dataset cards, dataset links, and small `samples/`
- Zenodo or another research repository for full archived dataset releases and DOI assignment

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

## 3. Keep GitHub Focused on Public Documentation

The default public contents should be:

- project overview pages
- work-package and deliverable indexes
- dataset landing pages in `docs/datasets/`
- publication indexes
- small examples in `samples/`

The default non-GitHub contents should be:

- full dataset packages
- raw measurement exports
- large media collections
- restricted consortium documents

## 4. Publish Dataset Families via Landing Pages

For each real dataset release:

1. create or update one dataset page in `docs/datasets/`
2. add a short sample or schema preview in `samples/` if needed
3. publish the real dataset in Zenodo or another archive
4. add the DOI and download link back into the dataset page

## 5. GitHub Metadata

On GitHub, fill in:

- repository description
- topics such as `waste`, `open-science`, `dataset-registry`, `radar-sensing`, `computer-vision`, `segmentation`
- the citation widget from `CITATION.cff`

## 6. Release Strategy

Recommended release order:

1. project scaffold and deliverable structure
2. first public documentation release
3. first dataset landing page plus sample files
4. first external DOI-backed dataset archive
5. project release notes pointing to the archive

## 7. Zenodo Flow

1. create or log into Zenodo
2. connect the GitHub repository
3. enable the repository
4. create a GitHub release
5. let Zenodo archive the release and mint a DOI

After the DOI is available:

- add it to the relevant dataset page
- update `CITATION.cff` if needed
- include it in release notes and README links
