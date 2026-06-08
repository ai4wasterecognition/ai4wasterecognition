# Dataset Registry

This folder is the dataset registry for the AI4WasteRecognition project.

The intended publication model is:

- compact, approved public datasets may be hosted directly in this repository under `release/`
- larger or citation-critical datasets may also be mirrored in an external archive such as Zenodo
- GitHub always stores the dataset page, metadata, schema notes, and training or export code when available
- GitHub may also store mini sample packages in `samples/` when the full dataset stays local or moves to an external archive
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

## Folder Convention

Every dataset family lives in its own per-version subfolder (`<name>_v<n>/`) so that the registry, sources, configs, and releases never collide between datasets.

```text
docs/datasets/
├── README.md
├── TEMPLATE.md
├── radar_dataset_v1/
│   ├── experimental-data.md
│   ├── publication-and-modeling.md
│   ├── analysis-outputs.md
│   └── material_mapping_overrides.csv
├── radar_dataset_from_multidetektor_measurement/
│   ├── outputs.md
│   ├── publication-and-modeling.md
│   └── sample_mapping.csv
└── video_segmentation_dataset_v1/
    ├── outputs.md
    ├── input-spec.md
    └── workplan.md
```

The same convention is mirrored in `release/`, `scripts/`, `samples/`, and `training/configs/`.

## Deliverable-Backed Dataset Families

- [radar_dataset_v1/experimental-data.md](radar_dataset_v1/experimental-data.md) - linked mainly to `D3.3`, public repository release available
- [radar_dataset_v1/publication-and-modeling.md](radar_dataset_v1/publication-and-modeling.md) - release structure, metadata policy, and baseline transformer plan
- [radar_dataset_v1/analysis-outputs.md](radar_dataset_v1/analysis-outputs.md) - linked mainly to `D4.1`
- [radar_dataset_from_multidetektor_measurement/outputs.md](radar_dataset_from_multidetektor_measurement/outputs.md) - linked mainly to `D4.3`; 24 GHz radar plus numbered sample photos
- [video_segmentation_dataset_v1/outputs.md](video_segmentation_dataset_v1/outputs.md) - linked mainly to `D4.2`; public COCO mini-sample and local full-dataset specification
- [video_segmentation_dataset_v1/input-spec.md](video_segmentation_dataset_v1/input-spec.md) - required local input and output format for segmentation dataset preparation
- [video_segmentation_dataset_v1/workplan.md](video_segmentation_dataset_v1/workplan.md) - execution plan for the segmentation dataset release
- [TEMPLATE.md](TEMPLATE.md) - template for future dataset pages

## Future Project-Level Dataset Families

Additional dataset pages can be added later for:

- waste-management structured datasets
- benchmark splits
- annotation resources
- derived evaluation tables
