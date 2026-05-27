# radar_dataset_from_multidetektor_measurement — Samples

Small GitHub-friendly previews of the [`release/radar_dataset_from_multidetektor_measurement/`](../../release/radar_dataset_from_multidetektor_measurement/) package.

| File | Description |
|---|---|
| `sample_frame.txt` | One raw radar .txt frame (Nb=10, Empty container, 17 bins × 4 channels) — verbatim copy from the original radar export |
| `sample_labels_head25.csv` | First 25 rows of `measurement_labels.parquet` |
| `sample_metadata_head25.csv` | First 25 rows of `measurement_metadata.parquet` |
| `sample_bins_first_measurement.csv` | All 17 bin rows for the first measurement (`2026-04-23_13-14-01.859/FD/10_2026-04-23_13-14-01.859.txt`) |

The full dataset (2950 frames × 17 bins × 4 channels, parquet + npz + splits) plus the
43 sample photographs and their catalog live in the release package:
see [`release/radar_dataset_from_multidetektor_measurement/README.md`](../../release/radar_dataset_from_multidetektor_measurement/README.md).
