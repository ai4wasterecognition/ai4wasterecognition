# Dataset Card

## Dataset Name

AI4WasteRecognition Radar Waste Detectability Dataset

## Status

Planned public release. This card describes the intended public dataset derived from the local `WasteR` analysis workspace.

## Summary

This dataset is intended to support research on radar-based recognition of waste materials and waste cleanliness. The source experiments were performed with a 24 GHz IMST Sentire radar in CW and FMCW modes across different environments, orientations, and reflector/deflector configurations.

The public release should focus on curated tabular data suitable for:

- descriptive analysis
- reproducible reporting
- classical statistical modeling
- downstream AI/ML prototyping on aggregated records

## Motivation

The project investigates whether radar sensing can help identify waste composition and contamination in conditions where optical sensing may be unreliable due to lighting, dust, occlusion, or material packaging.

## Intended Public Files

The recommended public release is:

- `public_dataset/measurements.csv`
  - curated measurement-level or run-level table
- `public_dataset/material_conditions.csv`
  - aggregated material-condition detectability summary
- `public_dataset/data_dictionary.csv`
  - variable descriptions and units

Optional:

- `public_dataset/collection_protocol.pdf`
- `public_dataset/figures/`
- `public_dataset/notebooks/`

## Unit of Observation

Recommended primary unit:

- one row per radar measurement after target/background aggregation

Recommended secondary unit:

- one row per material-condition aggregate

## Source Data

The local workspace currently contains:

- raw radar text logs
- Excel-based experimental catalogs
- processed run-level exports
- material-mapped detectability outputs

The public release should be derived from curated processed tables rather than from raw device logs unless consortium approval explicitly allows raw publication.

## Collection Context

The experiments vary across:

- radar mode: CW, FMCW
- environment: laboratory, corridor, outdoor
- reflector/deflector setup
- orientation relative to surroundings
- attenuation and ramp-time settings
- measured materials and packaging conditions

## Processing Pipeline

High-level processing flow:

1. Raw radar logs are converted into tabular bin-level data.
2. Target and background bins are labeled.
3. Bin-level values are aggregated into measurement-level records.
4. Material labels are merged from experiment catalogs and fallback mapping rules.
5. Detectability metrics are computed and summarized.

## Likely Variables in the Public Measurement Table

Suggested variables to keep if validated:

- `cw_fmcw`
- `attenuation_db`
- `ramp_time_ms`
- `bin_size_mm`
- `start_freq_mhz`
- `stop_freq_mhz`
- `number_of_samples`
- `measurement_distance_m`
- `place`
- `orientation`
- `refl_defl_ni`
- `material_name_auto`
- `material_primary`
- `material_secondary`
- `obal`
- `delta_dbm_mean_channels_w2`
- `delta_dbm_mean_channels_w3`
- `ratio_lin_target_bg_w2`
- `ratio_lin_target_bg_w3`

## Recommended Exclusions

Before public release, review and likely exclude:

- raw device log files
- office documents and internal reports
- local-only working artifacts
- fields with unresolved semantic ambiguity
- fields that may expose unnecessary operational details
- fields that may create privacy or IP risk

## Known Limitations

Current known issues in the local workspace:

- measurement metadata are not yet fully normalized across all analysis paths
- some material mappings were reconstructed using fallback rules
- `measurement_distance_m` appears to require validation before publication as a physical distance field
- some notebooks depend on in-memory state and are not yet a fully clean release pipeline

## Ethics, Privacy, and Legal Review

Release checklist before publication:

- confirm that no personal data are included
- confirm that no confidential partner information is included
- confirm that publication does not interfere with planned IP protection
- confirm consortium approval for the final release scope

## Licensing Guidance

Do not pick a final public license until the consortium agrees.

Recommended default direction:

- documentation: CC-BY-4.0
- curated dataset: CC-BY-4.0 or CC0 only after approval
- code/scripts: MIT or Apache-2.0

See [docs/LICENSING.md](docs/LICENSING.md).

## Versioning

Recommended scheme:

- `v0.x` for internal/public draft releases
- `v1.0.0` for the first DOI-backed public dataset release

Each public release should be archived in Zenodo to obtain a DOI.

## Citation

Use the repository `CITATION.cff` and the Zenodo DOI once available.
