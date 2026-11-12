# AI4WasteRecognition

[English version](README.md)

Verejný repozitár projektu `AI4WasteRecognition: AI-assisted recognition of sorted waste cleanliness` (Rozpoznávanie čistoty vytriedeného odpadu s podporou umelej inteligencie). Zverejňuje radarové datasety zozbierané v laboratórnych experimentoch projektu a video segmentačný dataset vytriedeného odpadu spolu s dokumentáciou datasetov, ukážkovými súbormi, kódom na export a tréning modelov a verejným prehľadom pracovných balíkov a výstupov projektu.

Hlavnou verziou dokumentácie je anglická verzia [README.md](README.md). Ostatná dokumentácia v repozitári je v angličtine.

## Zverejnené dáta

Repozitár obsahuje dva kompletné radarové datasety a kompletný video segmentačný dataset. Všetky súbory sú vo vetve `main` a dajú sa stiahnuť priamo z GitHubu (`Code → Download ZIP` alebo `git clone`).

| Dataset | Obsah | Rozsah | Umiestnenie |
| --- | --- | --- | --- |
| Radarový dataset v1 | merania 24 GHz FMCW radarom na vytriedených odpadových materiáloch, 11 hlavných materiálových tried, rozdelenie `train`/`val`/`test` | 13 650 meraní (`core`) + 201 meraní (`extended`) | [release/radar_dataset_v1](release/radar_dataset_v1/README.md) |
| Radarový dataset z multidetektorového merania | merania 24 GHz FMCW radarom na plastovom odpade s kontrolovanými prímesami (drevo, papier, sklo, hliníkové žalúzie), pevná laboratórna geometria, doplnené fotografiami vzoriek | 2 950 meraní, 17 typov vzoriek, 43 fotografií | [release/radar_dataset_from_multidetektor_measurement](release/radar_dataset_from_multidetektor_measurement/README.md) |
| Video segmentačný dataset v1 | anotácie COCO instance segmentation vytriedeného plastového a papierového odpadu a prímesí, 11 tried, rozdelenie `train`/`valid`/`test`; tréningové dáta modelov z `D4.2` | 322 obrázkov, 7 124 anotovaných objektov | [release/video_segmentation_dataset_v1](release/video_segmentation_dataset_v1/README.md) |

Každý radarový dataset obsahuje:

- `measurement_bins.parquet` - radarový signál po vzdialenostných binoch, jeden riadok na meranie a bin
- `measurement_tensor.npz` - polia pripravené na tréning modelov
- `measurement_labels.parquet` - označenia (labely) jednotlivých meraní
- `measurement_metadata.parquet` - metadáta merania
- `measurement_provenance.parquet` - väzba každého merania na pôvodný zdrojový súbor
- `splits.parquet` - deterministické rozdelenie na `train`/`val`/`test`
- `data_dictionary.csv` - popis stĺpcov
- `summary.json` a `checksums.sha256` - súhrnné počty a kontrolné súčty súborov

Súbory Parquet a NPZ sa vo webovom rozhraní GitHubu nezobrazia. Treba ich stiahnuť a otvoriť napríklad v Pythone:

```python
import numpy as np
import pandas as pd

base = "release/radar_dataset_v1/core"
labels = pd.read_parquet(f"{base}/measurement_labels.parquet")
splits = pd.read_parquet(f"{base}/splits.parquet")
print(labels.merge(splits[["measurement_id", "split"]], on="measurement_id")
            .groupby(["split", "material_primary"]).size().unstack(fill_value=0))

npz = np.load(f"{base}/measurement_tensor.npz")
X = npz["signal"]  # (13650, 33, 4): merania x biny x kanály
```

Malé CSV ukážky každého radarového datasetu sú v priečinku [samples/](samples/README.md) a dajú sa prezerať priamo v prehliadači.

## Identifikácia projektu

- Oficiálny názov: `AI4WasteRecognition: AI-assisted recognition of sorted waste cleanliness`
- Skrátený názov: `AI4 Waste recognition`
- Kód projektu: `09I05-03-V02-00068`
- Financovanie: EÚ NextGenerationEU prostredníctvom Plánu obnovy a odolnosti SR
- Výzva: `09I05-03-V02`
- Konzorcium: Slovenská technická univerzita v Bratislave, Optima Ideas s.r.o., Sensoneo j. s. a., Asseco Central Europe, a. s., a mesto Michalovce

## Obsah repozitára

| Priečinok | Obsah |
| --- | --- |
| [release/](release/) | kompletné verejné radarové datasety |
| [samples/](samples/README.md) | malé ukážky každého datasetu (CSV, surový rámec, obrázky) |
| [docs/datasets/](docs/datasets/README.md) | stránky datasetov, popis schémy a dokumentácia vydaní |
| [scripts/](scripts/) | skripty na export datasetov, zostavenie vydaní, tréning a inferenciu |
| [training/](training/README.md) | tréningové konfigurácie a spúšťacie skripty pre radarové a segmentačné modely |
| [docs/project/](docs/project/README.md) | prehľad projektu, pracovné balíky a míľniky |
| [docs/deliverables/](docs/deliverables/README.md) | zoznam výstupov projektu a ich stav v tomto repozitári |
| [docs/publications/](docs/publications/README.md) | zoznam publikácií |

## Štruktúra podľa pracovných balíkov

Repozitár kopíruje päť pracovných balíkov zo žiadosti o projekt:

- `KPB1` Riadenie projektu
- `KPB2` Technologický a AI výskum
- `KPB3` Laboratórny experiment
- `KPB4` Analýza dát
- `KPB5` Vyhodnotenie

Každý pracovný balík má stránku v [docs/deliverables/](docs/deliverables/README.md) so zoznamom výstupov a s tým, čo repozitár ku každému z nich obsahuje. Zverejnené radarové datasety patria k výstupom `D3.3` (Dataset zo zberu experimentálnych dát) a `D4.3` (Správa o multidetektorovej analýze údajov riadenej AI).

## Pravidlá zverejňovania

Čo sa v repozitári zverejňuje a čo nie, popisuje [docs/PUBLISHING.md](docs/PUBLISHING.md).

## Licencia a citovanie

Zdrojový kód je zverejnený pod licenciou [MIT](LICENSE). Datasety a dokumentácia sú zverejnené pod licenciou [CC BY 4.0](LICENSE-DATA). Podrobnosti sú v [docs/LICENSING.md](docs/LICENSING.md).

Pri použití repozitára alebo niektorého z datasetov citujte metadáta zo súboru [CITATION.cff](CITATION.cff).
