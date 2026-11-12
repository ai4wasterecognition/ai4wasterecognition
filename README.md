# AI4WasteRecognition

[Slovenská verzia](README.sk.md)

Public repository of the project `AI4WasteRecognition: AI-assisted recognition of sorted waste cleanliness`. It publishes the radar datasets collected in the project laboratory experiments and the video segmentation dataset of sorted waste, together with dataset documentation, preview samples, export and training code, and the public mapping of project work packages and deliverables.

## Published Data

The repository contains two full radar datasets and the full video segmentation dataset. All files are in the `main` branch and can be downloaded directly from GitHub (`Code → Download ZIP` or `git clone`).

| Dataset | Content | Size | Location |
| --- | --- | --- | --- |
| Radar dataset v1 | 24 GHz FMCW radar measurements of sorted waste materials, 11 primary material classes, `train`/`val`/`test` splits | 13,650 measurements (`core`) + 201 measurements (`extended`) | [release/radar_dataset_v1](release/radar_dataset_v1/README.md) |
| Radar dataset from multidetector measurement | 24 GHz FMCW radar measurements of plastic waste with controlled contaminations (wood, paper, glass, Al blinds), fixed lab geometry, paired with sample photographs | 2,950 measurements, 17 sample types, 43 photographs | [release/radar_dataset_from_multidetektor_measurement](release/radar_dataset_from_multidetektor_measurement/README.md) |
| Video segmentation dataset v1 | COCO instance segmentation of sorted plastic and paper waste and admixtures, 11 classes, `train`/`valid`/`test` splits; the training data of the models in `D4.2` | 322 images, 7,124 annotated instances | [release/video_segmentation_dataset_v1](release/video_segmentation_dataset_v1/README.md) |

Each radar release contains:

- `measurement_bins.parquet` - bin-level radar signal, one row per measurement and range bin
- `measurement_tensor.npz` - model-ready arrays built from the bin-level data
- `measurement_labels.parquet` - labels per measurement
- `measurement_metadata.parquet` - acquisition metadata
- `measurement_provenance.parquet` - mapping of each measurement to its raw source file
- `splits.parquet` - deterministic `train`/`val`/`test` split
- `data_dictionary.csv` - column reference
- `summary.json` and `checksums.sha256` - counts and file checksums

Parquet and NPZ files cannot be previewed in the GitHub web interface. Download them and open them with Python, for example:

```python
import numpy as np
import pandas as pd

base = "release/radar_dataset_v1/core"
labels = pd.read_parquet(f"{base}/measurement_labels.parquet")
splits = pd.read_parquet(f"{base}/splits.parquet")
print(labels.merge(splits[["measurement_id", "split"]], on="measurement_id")
            .groupby(["split", "material_primary"]).size().unstack(fill_value=0))

npz = np.load(f"{base}/measurement_tensor.npz")
X = npz["signal"]  # (13650, 33, 4): measurements x range bins x channels
```

Small CSV previews of every radar release are available in [samples/](samples/README.md) and can be viewed directly in the browser.

## Project Identity

- Official project title: `AI4WasteRecognition: AI-assisted recognition of sorted waste cleanliness`
- Short title: `AI4 Waste recognition`
- Project code: `09I05-03-V02-00068`
- Funding: EU NextGenerationEU through the Recovery and Resilience Plan for Slovakia
- Call: `09I05-03-V02`
- Consortium: Slovak University of Technology in Bratislava, Optima Ideas s.r.o., Sensoneo j. s. a., Asseco Central Europe, a. s., and the City of Michalovce

## Repository Contents

| Folder | Content |
| --- | --- |
| [release/](release/) | full public radar dataset releases |
| [samples/](samples/README.md) | small CSV, raw-frame, and image previews of each dataset |
| [docs/datasets/](docs/datasets/README.md) | dataset landing pages, schema notes, and release documentation |
| [scripts/](scripts/) | dataset export, release-building, training, and inference scripts |
| [training/](training/README.md) | training configurations and run scripts for radar and segmentation models |
| [docs/project/](docs/project/README.md) | project overview, work packages, and milestones |
| [docs/deliverables/](docs/deliverables/README.md) | deliverables index and their status in this repository |
| [docs/publications/](docs/publications/README.md) | publication index |

Key pages:

- [docs/datasets/radar_dataset_v1/experimental-data.md](docs/datasets/radar_dataset_v1/experimental-data.md) - radar dataset v1 landing page
- [docs/datasets/radar_dataset_v1/publication-and-modeling.md](docs/datasets/radar_dataset_v1/publication-and-modeling.md) - release structure and transformer baseline
- [docs/datasets/radar_dataset_from_multidetektor_measurement/outputs.md](docs/datasets/radar_dataset_from_multidetektor_measurement/outputs.md) - multidetector radar dataset landing page
- [docs/datasets/video_segmentation_dataset_v1/outputs.md](docs/datasets/video_segmentation_dataset_v1/outputs.md) - segmentation dataset page
- [docs/deliverables/README.md](docs/deliverables/README.md) - deliverables index
- [docs/PUBLISHING.md](docs/PUBLISHING.md) - publication rules and workflow
- [docs/LICENSING.md](docs/LICENSING.md) - licensing notes

## Deliverable-Oriented Structure

The repository follows the five work packages defined in the project application:

- `KPB1` Project Management
- `KPB2` Tech and AI Research
- `KPB3` Laboratory Experiment
- `KPB4` Data analysis
- `KPB5` Evaluation

Each work package has a page in [docs/deliverables/](docs/deliverables/README.md) listing its deliverables and what this repository contains for each of them. The published radar datasets belong to `D3.3` (Experimental Data Collection Dataset) and `D4.3` (Report on AI-Driven multidetector Data Analysis).

## Publication Rules

The rules for what is and is not published in this repository are described in [docs/PUBLISHING.md](docs/PUBLISHING.md).

## License and Citation

Source code is released under the [MIT License](LICENSE). Datasets and documentation are released under [CC BY 4.0](LICENSE-DATA). Details are in [docs/LICENSING.md](docs/LICENSING.md).

If you use this repository or one of its datasets, cite it using the metadata in [CITATION.cff](CITATION.cff).
