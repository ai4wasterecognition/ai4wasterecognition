#!/usr/bin/env python3
"""Build the radar_dataset_from_multidetektor_measurement publishable release.

Reads:
    processed/radar_dataset_from_multidetektor_measurement/df_bins.parquet           (Krok 1 output)
    processed/radar_dataset_from_multidetektor_measurement/sample_mapping.csv        (Krok 2 output)

Writes into <release_dir> (default release/radar_dataset_from_multidetektor_measurement/):
    measurement_bins.parquet
    measurement_labels.parquet
    measurement_metadata.parquet
    measurement_provenance.parquet
    measurement_tensor.npz                  (X: (N, 4, 17) float32, ids: (N,))
    splits.parquet                          (folder_time_ordered_60_20_20)
    data_dictionary.csv
    summary.json

Constants (per D4.31 report):
    measurement_distance_m = 2.12
    back_wall_distance_m = 4.0
    place = "Lab Optima"
    recommended_target_bins = [7, 8]
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

DEFAULT_BINS = Path("processed/radar_dataset_from_multidetektor_measurement/df_bins.parquet")
DEFAULT_MAPPING = Path("processed/radar_dataset_from_multidetektor_measurement/sample_mapping.csv")
DEFAULT_RELEASE = Path("release/radar_dataset_from_multidetektor_measurement")

MEASUREMENT_DISTANCE_M = 2.12
BACK_WALL_DISTANCE_M = 4.0
PLACE = "Lab Optima"
RECOMMENDED_TARGET_BINS = [7, 8]
SPLIT_STRATEGY = "folder_time_ordered_60_20_20"
SPLIT_SEED = 42
DATASET_VERSION = "radar_dataset_from_multidetektor_measurement_1.0.0"


def build_bins_table(df_bins: pd.DataFrame, bin_size_m: float) -> pd.DataFrame:
    bins = df_bins[[
        "measurement_id", "bin_idx",
        "mag_i1_dbm", "mag_q1_dbm", "mag_i2_dbm", "mag_q2_dbm",
    ]].copy()
    bins["range_m"] = (bins["bin_idx"] - 1) * bin_size_m
    bins = bins[[
        "measurement_id", "bin_idx", "range_m",
        "mag_i1_dbm", "mag_q1_dbm", "mag_i2_dbm", "mag_q2_dbm",
    ]]
    return bins.sort_values(["measurement_id", "bin_idx"]).reset_index(drop=True)


def build_labels_table(meta_df: pd.DataFrame, mapping: pd.DataFrame) -> pd.DataFrame:
    labels = meta_df[["measurement_id", "nb_of_sample"]].merge(
        mapping, on="nb_of_sample", how="left", validate="m:1"
    )
    missing = labels[labels["label_name"].isna()]
    if len(missing):
        raise ValueError(f"{len(missing)} measurements lack mapping (Nb not in sample_mapping.csv)")
    return labels[[
        "measurement_id", "nb_of_sample",
        "label_name", "label_category", "label_contamination_present",
    ]]


def build_metadata_table(df_bins: pd.DataFrame) -> pd.DataFrame:
    meta_cols = [
        "measurement_id", "nb_of_sample", "date", "time",
        "radar_no", "interface",
        "start_freq_mhz", "stop_freq_mhz",
        "ramp_time_ms", "attenuation_db",
        "bin_size_mm", "number_of_samples", "bin_size_hz", "zero_pad_factor",
        "normalization", "active_channels", "magnitude_unit",
    ]
    meta = df_bins[meta_cols].drop_duplicates("measurement_id").reset_index(drop=True)
    meta["measurement_distance_m"] = MEASUREMENT_DISTANCE_M
    meta["back_wall_distance_m"] = BACK_WALL_DISTANCE_M
    meta["place"] = PLACE
    return meta


def build_provenance_table(df_bins: pd.DataFrame, raw_root: str) -> pd.DataFrame:
    prov = df_bins[["measurement_id", "source_txt", "folder_ts"]].drop_duplicates("measurement_id").copy()
    prov["source_txt_relpath"] = prov["measurement_id"]
    prov["raw_root_hint"] = raw_root
    prov["ingest_timestamp_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return prov[[
        "measurement_id", "source_txt", "folder_ts",
        "source_txt_relpath", "raw_root_hint", "ingest_timestamp_utc",
    ]].reset_index(drop=True)


def build_tensor(df_bins: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Return X: (N, 4, 17) float32 and measurement_ids: (N,)."""
    df = df_bins.sort_values(["measurement_id", "bin_idx"])
    ids = df["measurement_id"].drop_duplicates().tolist()
    id_to_idx = {mid: i for i, mid in enumerate(ids)}

    n_samples = int(df["number_of_samples"].iloc[0])
    X = np.full((len(ids), 4, n_samples), np.nan, dtype=np.float32)

    for mid, g in df.groupby("measurement_id"):
        i = id_to_idx[mid]
        # bin_idx 1..17 → tensor index 0..16
        bi = (g["bin_idx"].to_numpy() - 1)
        X[i, 0, bi] = g["mag_i1_dbm"].to_numpy(dtype=np.float32)
        X[i, 1, bi] = g["mag_q1_dbm"].to_numpy(dtype=np.float32)
        X[i, 2, bi] = g["mag_i2_dbm"].to_numpy(dtype=np.float32)
        X[i, 3, bi] = g["mag_q2_dbm"].to_numpy(dtype=np.float32)

    if np.isnan(X).any():
        n_nan = int(np.isnan(X).sum())
        raise ValueError(f"Tensor has {n_nan} NaN values — bin coverage incomplete")

    return X, np.array(ids, dtype=object)


def build_splits(meta_df: pd.DataFrame, labels_df: pd.DataFrame) -> pd.DataFrame:
    """folder_time_ordered_60_20_20 per Nb.

    Within each nb_of_sample, sort measurements chronologically by (date, time),
    take first 60% → train, next 20% → val, last 20% → test.
    """
    df = meta_df[["measurement_id", "nb_of_sample", "date", "time"]].merge(
        labels_df[["measurement_id", "label_category"]], on="measurement_id"
    )
    df["sort_key"] = df["date"] + " " + df["time"]
    df = df.sort_values(["nb_of_sample", "sort_key"]).reset_index(drop=True)

    out_rows = []
    for nb, g in df.groupby("nb_of_sample", sort=True):
        n = len(g)
        n_train = int(round(n * 0.60))
        n_val = int(round(n * 0.20))
        n_test = n - n_train - n_val
        labels = ["train"] * n_train + ["val"] * n_val + ["test"] * n_test
        for (mid, _), split in zip(g[["measurement_id", "sort_key"]].itertuples(index=False), labels):
            out_rows.append({
                "measurement_id": mid,
                "split": split,
                "split_seed": SPLIT_SEED,
                "split_strategy": SPLIT_STRATEGY,
            })
    return pd.DataFrame(out_rows)


def build_data_dictionary() -> pd.DataFrame:
    rows = [
        # measurement_bins
        ("measurement_bins.parquet", "measurement_id", "string", "Unique frame identifier (relative path under raw_root)"),
        ("measurement_bins.parquet", "bin_idx", "int64", "1-based range bin index, 1..17"),
        ("measurement_bins.parquet", "range_m", "float64", "Approximate range = (bin_idx-1) * bin_size_m, where bin_size_m≈0.320604"),
        ("measurement_bins.parquet", "mag_i1_dbm", "float64", "Magnitude of I channel, antenna pair 1, in dBm"),
        ("measurement_bins.parquet", "mag_q1_dbm", "float64", "Magnitude of Q channel, antenna pair 1, in dBm"),
        ("measurement_bins.parquet", "mag_i2_dbm", "float64", "Magnitude of I channel, antenna pair 2, in dBm"),
        ("measurement_bins.parquet", "mag_q2_dbm", "float64", "Magnitude of Q channel, antenna pair 2, in dBm"),
        # measurement_labels
        ("measurement_labels.parquet", "measurement_id", "string", "Unique frame identifier"),
        ("measurement_labels.parquet", "nb_of_sample", "int64", "Sample number from operator catalogue (10,20,40,50,70,71,80,120,130,140,160,180,181,200,210,220,230)"),
        ("measurement_labels.parquet", "label_name", "string", "Verbatim 'Name o sample' from VysledkyPreStatistiku.xlsx (17 classes; trimmed)"),
        ("measurement_labels.parquet", "label_category", "string", "Verbatim 'Category' from VysledkyPreStatistiku.xlsx (6 classes). Note: 'Plastic + Ai blinds' was corrected to 'Plastic + Al blinds' in the source xlsx by the maintainer."),
        ("measurement_labels.parquet", "label_contamination_present", "bool", "Derived: label_category != 'Reference measurement'"),
        # measurement_metadata
        ("measurement_metadata.parquet", "measurement_id", "string", "Unique frame identifier"),
        ("measurement_metadata.parquet", "nb_of_sample", "int64", "Sample number"),
        ("measurement_metadata.parquet", "date", "string", "YYYY-MM-DD acquisition date (all frames: 2026-04-23)"),
        ("measurement_metadata.parquet", "time", "string", "HH:MM:SS.mmm acquisition time within the day"),
        ("measurement_metadata.parquet", "radar_no", "string", "Serial of the SENTIRE 24 GHz radar unit"),
        ("measurement_metadata.parquet", "interface", "string", "Data interface (Ethernet)"),
        ("measurement_metadata.parquet", "start_freq_mhz", "int64", "FMCW start frequency in MHz (24008)"),
        ("measurement_metadata.parquet", "stop_freq_mhz", "int64", "FMCW stop frequency in MHz (24242)"),
        ("measurement_metadata.parquet", "ramp_time_ms", "int64", "FMCW ramp duration in ms (50)"),
        ("measurement_metadata.parquet", "attenuation_db", "float64", "Attenuation in dB (0.0)"),
        ("measurement_metadata.parquet", "bin_size_mm", "float64", "Range bin size in mm (320.604)"),
        ("measurement_metadata.parquet", "number_of_samples", "int64", "Number of range bins per frame (17)"),
        ("measurement_metadata.parquet", "bin_size_hz", "int64", "Frequency bin size after FFT in Hz"),
        ("measurement_metadata.parquet", "zero_pad_factor", "int64", "FFT zero-padding factor"),
        ("measurement_metadata.parquet", "normalization", "int64", "Radar internal normalization flag (0 = OFF)"),
        ("measurement_metadata.parquet", "active_channels", "string", "Comma-separated active channels (I1, Q1, I2, Q2)"),
        ("measurement_metadata.parquet", "magnitude_unit", "string", "Magnitude unit string from radar header (dBm)"),
        ("measurement_metadata.parquet", "measurement_distance_m", "float64", "Constant: distance radar → waste container = 2.12 m (per D4.31 report)"),
        ("measurement_metadata.parquet", "back_wall_distance_m", "float64", "Constant: distance radar → far wall behind container = 4.0 m"),
        ("measurement_metadata.parquet", "place", "string", "Acquisition site (Lab Optima)"),
        # measurement_provenance
        ("measurement_provenance.parquet", "measurement_id", "string", "Unique frame identifier"),
        ("measurement_provenance.parquet", "source_txt", "string", "Filename of the source .txt frame export"),
        ("measurement_provenance.parquet", "folder_ts", "string", "Parent folder timestamp grouping frames from one capture session"),
        ("measurement_provenance.parquet", "source_txt_relpath", "string", "Relative path inside meranie_23_04/ raw dump"),
        ("measurement_provenance.parquet", "raw_root_hint", "string", "Original raw_root path on the maintainer's machine"),
        ("measurement_provenance.parquet", "ingest_timestamp_utc", "string", "ISO-8601 UTC timestamp of the ingest run"),
        # measurement_tensor.npz
        ("measurement_tensor.npz", "X", "float32[N,4,17]", "Channel-stacked dBm magnitudes; channel order = [I1, Q1, I2, Q2]; bin axis = 0..16 → bin_idx 1..17"),
        ("measurement_tensor.npz", "measurement_ids", "object[N]", "measurement_id strings in the same order as X[i]"),
        # splits
        ("splits.parquet", "measurement_id", "string", "Unique frame identifier"),
        ("splits.parquet", "split", "string", "One of {train, val, test}"),
        ("splits.parquet", "split_seed", "int64", "Seed used for the split (42)"),
        ("splits.parquet", "split_strategy", "string", "Strategy label: folder_time_ordered_60_20_20"),
        # aux/foto_catalog.csv (sample photos under photos/)
        ("aux/foto_catalog.csv", "filename", "string", "Photo file name under photos/"),
        ("aux/foto_catalog.csv", "nb_of_sample", "int64", "Sample number; matches nb_of_sample in the radar tables. Empty for measurement-setup slides"),
        ("aux/foto_catalog.csv", "description", "string", "English description parsed from the photo file name"),
        ("aux/foto_catalog.csv", "view", "string", "Slide/view label (a, b, c) when a sample has multiple photos"),
        ("aux/foto_catalog.csv", "is_setup", "bool", "True for the general measurement-setup slides (no sample number)"),
        ("aux/foto_catalog.csv", "has_radar_match", "bool", "True if nb_of_sample exists in the radar measurement tables"),
    ]
    return pd.DataFrame(rows, columns=["file", "column", "dtype", "description"])


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            buf = fh.read(chunk)
            if not buf:
                break
            h.update(buf)
    return h.hexdigest()


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--bins", type=Path, default=DEFAULT_BINS)
    p.add_argument("--mapping", type=Path, default=DEFAULT_MAPPING)
    p.add_argument("--release", type=Path, default=DEFAULT_RELEASE)
    p.add_argument("--raw-root-hint", type=str,
                   default="data/multidetektor/meranie_23_04")
    args = p.parse_args()

    args.release.mkdir(parents=True, exist_ok=True)

    df_bins = pd.read_parquet(args.bins)
    mapping = pd.read_csv(args.mapping)
    bin_size_m = float(df_bins["bin_size_mm"].iloc[0]) / 1000.0

    # 1. build all tables
    meta = build_metadata_table(df_bins)
    labels = build_labels_table(meta, mapping)
    bins = build_bins_table(df_bins, bin_size_m)
    prov = build_provenance_table(df_bins, args.raw_root_hint)
    splits = build_splits(meta, labels)
    X, ids = build_tensor(df_bins)
    data_dict = build_data_dictionary()

    # 2. write outputs
    bins.to_parquet(args.release / "measurement_bins.parquet", index=False)
    labels.to_parquet(args.release / "measurement_labels.parquet", index=False)
    meta.to_parquet(args.release / "measurement_metadata.parquet", index=False)
    prov.to_parquet(args.release / "measurement_provenance.parquet", index=False)
    splits.to_parquet(args.release / "splits.parquet", index=False)
    data_dict.to_csv(args.release / "data_dictionary.csv", index=False)
    np.savez_compressed(args.release / "measurement_tensor.npz", X=X, measurement_ids=ids)

    # 3. summary.json
    summary = {
        "dataset_version": DATASET_VERSION,
        "n_measurements": int(len(meta)),
        "n_bin_rows": int(len(bins)),
        "n_channels": 4,
        "channel_order": ["I1", "Q1", "I2", "Q2"],
        "n_bins_per_frame": int(meta["number_of_samples"].iloc[0]),
        "bin_size_m": bin_size_m,
        "frequency_band_mhz": [int(meta["start_freq_mhz"].iloc[0]), int(meta["stop_freq_mhz"].iloc[0])],
        "modulation": "FMCW",
        "ramp_time_ms": int(meta["ramp_time_ms"].iloc[0]),
        "measurement_distance_m": MEASUREMENT_DISTANCE_M,
        "back_wall_distance_m": BACK_WALL_DISTANCE_M,
        "place": PLACE,
        "recommended_target_bins": RECOMMENDED_TARGET_BINS,
        "acquisition_date": meta["date"].iloc[0],
        "label_classes": {
            "label_name": sorted(labels["label_name"].unique().tolist()),
            "label_category": sorted(labels["label_category"].unique().tolist()),
            "label_contamination_present": [False, True],
        },
        "samples_per_nb": labels.groupby("nb_of_sample").size().to_dict(),
        "samples_per_category": labels["label_category"].value_counts().to_dict(),
        "splits": splits.groupby("split").size().to_dict(),
        "splits_strategy": SPLIT_STRATEGY,
        "split_seed": SPLIT_SEED,
        "tensor_shape": list(X.shape),
        "excluded_nb": [90],
        "excluded_reason": "Operator excluded (no matching label in source catalogue)",
        "source_documents": {
            "raw_radar_frames": args.raw_root_hint,
            "label_xlsx": "data/multidetektor/VysledkyPreStatistiku.xlsx (column Name o sample, Category)",
            "geometry_report": "data/multidetektor/D 4.31_Správa o multidetektorovej analýze údajov riadenej AI.docx",
            "sample_overview": "data/multidetektor/Príloha c. 1 Prehlad_vzorkov a snímkov.docx",
        },
        "sample_photos": {
            "location": "photos/",
            "catalog": "aux/foto_catalog.csv",
            "naming_convention": "Nb.<sample_number>_<english description>_<view>.jpg",
            "description": (
                "Each photographed sample shares its sample number (Nb) with the "
                "radar measurements, so radar frames and photos can be cross-referenced "
                "1:1. Photos show the detailed waste composition and the top-down view "
                "of the sample poured into the waste container, enabling a comparison "
                "between radar sensing and video/image recognition."
            ),
            "built_by": "scripts/radar_dataset_from_multidetektor_measurement/build_foto_catalog.py",
        },
    }
    (args.release / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))

    # 4. checksums
    files_for_hash = [
        "measurement_bins.parquet",
        "measurement_labels.parquet",
        "measurement_metadata.parquet",
        "measurement_provenance.parquet",
        "measurement_tensor.npz",
        "splits.parquet",
        "data_dictionary.csv",
        "summary.json",
    ]
    lines = []
    for f in files_for_hash:
        fp = args.release / f
        if fp.exists():
            lines.append(f"{sha256_file(fp)}  {f}")
    (args.release / "checksums.sha256").write_text("\n".join(lines) + "\n")

    # 5. report
    print(f"[OK] release at: {args.release}")
    print(f"     measurements:  {summary['n_measurements']}")
    print(f"     bin rows:      {summary['n_bin_rows']}")
    print(f"     tensor shape:  {tuple(summary['tensor_shape'])}")
    print(f"     splits:        {summary['splits']}")
    print(f"     categories:    {summary['samples_per_category']}")


if __name__ == "__main__":
    main()
