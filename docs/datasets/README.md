# Dataset Registry

This folder is the dataset registry for the AI4WasteRecognition project.

The intended publication model is:

- real datasets live in an external archive such as Zenodo
- GitHub stores the dataset page, metadata, schema notes, and a small sample if needed
- each dataset page links back to the relevant deliverable(s)

## What Belongs Here

- one markdown landing page per dataset family
- version and DOI links
- owners and related deliverables
- schema summaries or data-dictionary references
- sample references in `samples/`

## What Does Not Belong Here

- full operational datasets
- raw measurement dumps
- large image or video collections
- restricted consortium material

## Deliverable-Backed Dataset Families

- [radar-publication-and-modeling.md](radar-publication-and-modeling.md) - release structure, metadata policy, and baseline transformer plan
- [radar-experimental-data.md](radar-experimental-data.md) - linked mainly to `D3.3`
- [radar-analysis-outputs.md](radar-analysis-outputs.md) - linked mainly to `D4.1`
- [video-segmentation-outputs.md](video-segmentation-outputs.md) - linked mainly to `D4.2`
- [multidetector-outputs.md](multidetector-outputs.md) - linked mainly to `D4.3`
- [TEMPLATE.md](TEMPLATE.md) - template for future dataset pages

## Future Project-Level Dataset Families

Additional dataset pages can be added later for:

- waste-management structured datasets
- benchmark splits
- annotation resources
- derived evaluation tables
