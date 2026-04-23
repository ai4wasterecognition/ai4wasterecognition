# Dataset Registry

This folder is the dataset registry for the AI4WasteRecognition project.

The intended publication model is:

- compact, approved public datasets may be hosted directly in this repository under `release/`
- larger or citation-critical datasets may also be mirrored in an external archive such as Zenodo
- GitHub always stores the dataset page, metadata, schema notes, and training or export code when available
- each dataset page links back to the relevant deliverable(s)

## What Belongs Here

- one markdown landing page per dataset family
- version and DOI links, or repository release paths
- owners and related deliverables
- schema summaries or data-dictionary references
- sample references in `samples/` when useful
- links to repository-hosted release folders when available

## What Does Not Belong Here

- raw measurement dumps
- large image or video collections
- restricted consortium material
- dataset packages that should live only in an external archive because of size, sensitivity, or licensing

## Deliverable-Backed Dataset Families

- [radar-publication-and-modeling.md](radar-publication-and-modeling.md) - release structure, metadata policy, and baseline transformer plan
- [radar-experimental-data.md](radar-experimental-data.md) - linked mainly to `D3.3`, with a public repository release already available
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
