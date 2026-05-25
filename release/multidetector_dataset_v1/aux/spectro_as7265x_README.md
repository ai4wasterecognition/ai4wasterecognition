# AS7265x UV-VIS Spectrometer — Auxiliary Data

**Source:** `data/multidetektor/Protokol_AS7265x_s_datami_.docx`

Sensor: AMS AS7265x, 18 wavelength channels (410–940 nm + UV).
LED illumination off; natural daylight only. Sensor 65 mm above sample, 90° viewing angle.

This is a small **parallel** measurement set (10 reps × 18 wavelengths per material).
It is **NOT** strictly 1:1 with the radar frames — each spectro sample maps to one or more radar Nb.

## Schema (`spectro_as7265x.parquet`)

| column | type | description |
|---|---|---|
| sample_label | string | Sample name (Slovak) verbatim from docx (e.g., 'Plast čistý') |
| measurement_idx | int | 1..10 repeat measurement index |
| wavelength_nm | int | Wavelength in nm: 410, 435, 460, 485, 510, 535, 560, 585, 610, 645, 680, 715, 760, 810, 860, 900, 940 (and UV) |
| intensity | float | Raw sensor intensity (uncalibrated, 8-bit resolution) |

## Spectro sample → radar Nb (suggested mapping)

| spectro sample_label | radar nb_of_sample (multidetector_dataset_v1) |
|---|---|
| Pozadie   —   Referenčné meranie | 10 |
| Plast čistý | 20, 40 |
| Papier čistý | 210 |
| Papier2 čistý | 210 |
| Plast + papier | 80 |
| Plast + mokrý papier | 120, 130 |
| Mokrý papier čistý | 220 |
| Kov čistý | 180, 181, 200 |
| Plast + drevo | 50, 70, 71 |
| Plast + sklo | 140, 160 |

## Caveats (from the report)

- 8-bit sensor resolution; many channels show 0 std-dev across 10 reps.
- UV channel (R) is ~0 because UV LED was off.
- Natural daylight illumination is not controlled.
- 'Papier čistý' and 'Papier2 čistý' are nominally the same material but with different sheet thickness/orientation.