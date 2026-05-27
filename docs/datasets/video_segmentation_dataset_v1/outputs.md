# Open Video / Image Waste-Recognition Dataset — Landing Page

## Status

Planned — open dataset, in preparation.

## Related Deliverables

- `D4.2` Report on AI-Driven Video Data Analysis

## Purpose

A separate **open dataset** focused on recognising plastic and paper waste and their individual categories. It is built over an extensive collection of images of these separated waste fractions.

During the project measurement this dataset was used to train a neural network, which was then applied to recognise photographs of waste samples. The recognition results from this image model can be compared against the radar-based classification in [`radar_dataset_from_multidetektor_measurement`](../radar_dataset_from_multidetektor_measurement/outputs.md), because the photographed samples there share the same sample numbering (Nb) as the radar measurements.

## What This Repository Should Contain

- dataset description and fraction/category taxonomy (plastic, paper, and their sub-categories)
- annotation / label format notes
- sample assets or thumbnails in `samples/`
- a compact repository release in `release/video_segmentation_dataset_v1/` if approved and practical, or a link to an external archive / zip for the full image collection
- a summary of the neural-network recognition results obtained during the project

## Relation to the Radar Dataset

- Radar dataset: [`radar_dataset_from_multidetektor_measurement`](../radar_dataset_from_multidetektor_measurement/outputs.md) — 24 GHz radar frames of waste samples, with photographs of the same samples.
- This video/image dataset provides the image-recognition counterpart, enabling a radar-vs-video comparison on waste-fraction recognition.

## DOI and Archive

- DOI: `TBD`
- URL: `TBD`
- version: `TBD`
- Full image collection: delivered as a zip archive at **xxx** (link TBD)
