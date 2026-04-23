# Publishing Guide

This guide assumes you want to use:

- GitHub for the public project page, code, docs, and lightweight curated files
- Zenodo for archival release and DOI assignment

## 1. Decide the Repository Name

Because the repository should follow the official application and may later host multiple outputs, use the official project identity rather than a dataset-specific slug.

Recommended repository name:

- `AI4WasteRecognition`

Recommended GitHub slug if you prefer lowercase style:

- `ai4wasterecognition`
- or `ai4waste-recognition`

Recommendation:

- repository name / slug: official project acronym
- repository description: official project title
- datasets: separate subpages, folders, or DOI links inside the same umbrella repository
- radar outputs: one specific output stream, not the whole repository identity

## 2. Prepare the First Public Commit

From the project root:

```bash
git init -b main
git add README.md DATASET_CARD.md CITATION.cff .gitignore docs public_dataset
git commit -m "Initial public repository scaffold"
```

If you later decide to publish selected notebooks or scripts, add them in a second commit after review.

## 3. Create the GitHub Repository via the Web

1. Go to `https://github.com/new`
2. Set the owner
3. Enter the repository name
4. Add a short description
5. Choose `Public`
6. Do not initialize it with a README, `.gitignore`, or license
7. Click `Create repository`

## 4. Connect Local Git to GitHub

Replace the placeholders below:

```bash
git remote add origin https://github.com/<github-user>/<repo-name>.git
git push -u origin main
```

## 5. Fill the GitHub Repository Metadata

On the GitHub repository page:

1. Add the repository description
2. Add topics such as `radar`, `waste`, `dataset`, `fmcw`, `cw`, `open-science`
3. Pin the repository if relevant
4. Check that the `Cite this repository` widget appears from `CITATION.cff`

## 6. Add Curated Public Dataset Files or Dataset Links

If the dataset is small and curated, place release files in `public_dataset/`, for example:

- `public_dataset/measurements.csv`
- `public_dataset/material_conditions.csv`
- `public_dataset/data_dictionary.csv`

If the dataset is large or should be DOI-first:

- keep only dataset cards and download links in GitHub
- publish the actual files in Zenodo or another research repository
- link them from `README.md` and dataset documentation pages

If the repository will host multiple public outputs:

- create one page per dataset in `docs/datasets/`
- add deliverable-linked notes in `docs/deliverables/`
- keep the top-level `README.md` project-wide, not dataset-specific

Then commit and push:

```bash
git add public_dataset
git commit -m "Add curated public dataset v0.1"
git push
```

## 7. Create a GitHub Release

Recommended first tag:

- `v0.1.0` for an initial curated draft
- `v1.0.0` for the first stable DOI-backed public release

GitHub web flow:

1. Open `Releases`
2. Click `Draft a new release`
3. Create the tag
4. Add release notes summarizing the dataset contents
5. Publish the release

## 8. Connect GitHub to Zenodo

Zenodo flow:

1. Create or log into your Zenodo account
2. Connect your GitHub account
3. Enable this repository in Zenodo
4. Create a GitHub release
5. Wait for Zenodo to archive the release and mint a DOI

After Zenodo creates the DOI:

- add the DOI to `README.md`
- add the DOI to `CITATION.cff`
- optionally add a `.zenodo.json` file for richer metadata

## 9. Update `CITATION.cff`

Before the first stable public release, review:

- final title
- final version
- author list or consortium citation style
- DOI

## 10. Optional CLI Flow with `gh`

If you later install and authenticate the GitHub CLI:

```bash
gh repo create <repo-name> --public --source=. --remote=origin --push
```

At the moment this machine does not have `gh` installed, so the web flow is the safe default.

## 11. Recommended Order of Public Release

1. Publish the repository scaffold
2. Publish project-level documentation under the official project name
3. Decide per dataset whether it lives in GitHub or only via external DOI links
4. Publish curated dataset files or dataset links
5. Create the first GitHub release
6. Archive the release in Zenodo if needed
7. Announce the DOI-backed version
