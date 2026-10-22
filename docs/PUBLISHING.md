# Publishing Rules

This page describes what the repository publishes, what it does not publish, and how a new dataset release is added.

## What Is Published

- project overview pages, work-package and deliverable indexes
- dataset landing pages in `docs/datasets/<name>/`
- curated, consortium-approved dataset releases in `release/<name>/`
- small previews in `samples/<name>/`
- export, training, and inference code in `scripts/<name>/` and `training/`
- publication index in `docs/publications/`

Current dataset releases:

- [release/radar_dataset_v1](../release/radar_dataset_v1/README.md)
- [release/radar_dataset_from_multidetektor_measurement](../release/radar_dataset_from_multidetektor_measurement/README.md)

The video segmentation dataset is represented only by a preview sample in [samples/video_segmentation_dataset_v1](../samples/video_segmentation_dataset_v1/README.md). The full segmentation dataset is not published.

## What Is Not Published

- raw measurement logs and device dumps
- full datasets that the consortium has not approved for release, including the full video segmentation dataset
- personal data or anything that could identify a person
- restricted consortium documents and internal reports
- material whose disclosure could weaken IP protection or commercialization

## Folder Convention

Each dataset family uses the same subfolder name across the repository:

- `release/<name>/` - dataset files
- `samples/<name>/` - previews
- `scripts/<name>/` - export and training code
- `training/configs/<name>/` - training configurations
- `docs/datasets/<name>/` - landing page and documentation

## Adding a Dataset Release

1. Create or update the landing page in `docs/datasets/<name>/` and link it to the related deliverable(s).
2. Confirm consortium approval and the privacy and IP checks listed in [docs/datasets/DATASET_CARD_TEMPLATE.md](datasets/DATASET_CARD_TEMPLATE.md).
3. Add the release files, data dictionary, `summary.json`, and `checksums.sha256` to `release/<name>/`, and whitelist the folder in `.gitignore`.
4. Add a small preview to `samples/<name>/`.
5. If a DOI-backed archive copy is created (for example in Zenodo), add the DOI to the landing page and to `CITATION.cff`.

## Zenodo Archiving

No release is archived in Zenodo yet. To archive a GitHub release:

1. connect the GitHub repository in Zenodo and enable it
2. create a GitHub release
3. Zenodo archives the release and mints a DOI
4. add the DOI to the dataset landing page, `CITATION.cff`, and the README
