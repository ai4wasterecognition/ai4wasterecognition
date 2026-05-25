#!/usr/bin/env python3
"""Export a public-ready radar dataset from the current WasteR workspace."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd


DEFAULT_XLSX = Path("data/16012026/Dec_Jan_v5.xlsx")
DEFAULT_MAPPING = Path("outputs/object_detectability/material_name_auto_mapping.csv")
DEFAULT_MAPPING_OVERRIDES = Path("docs/datasets/radar_dataset_v1/material_mapping_overrides.csv")


def normalize_text(value: object) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = unicodedata.normalize("NFKC", str(value)).replace("\xa0", " ").strip()
    if not text:
        return None
    text = re.sub(r"\s+", " ", text)
    return text


def normalize_key(value: object) -> str | None:
    text = normalize_text(value)
    if text is None:
        return None
    text = text.lower()
    if re.fullmatch(r"-?\d+\.0+", text):
        return str(int(float(text)))
    return text


def make_public_measurement_id(source_file: str) -> str:
    digest = hashlib.sha1(source_file.encode("utf-8")).hexdigest()
    return f"m_{digest[:16]}"


def first_non_null(series: pd.Series) -> object:
    non_null = series.dropna()
    if non_null.empty:
        return np.nan
    return non_null.iloc[0]


def detect_header_row(raw: pd.DataFrame) -> int:
    marker_rows = raw[raw.eq("p.č.").any(axis=1)].index.tolist()
    if marker_rows:
        return marker_rows[0]
    marker_rows = raw[raw.eq("I1>").any(axis=1)].index.tolist()
    if marker_rows:
        return marker_rows[0]
    raise ValueError('Unable to detect data-sheet header row using "p.č." or "I1>" marker.')


def normalize_header_row(header_row: pd.Series) -> list[str]:
    names: list[str] = []
    for idx, value in enumerate(header_row):
        if pd.isna(value):
            names.append(f"col_{idx:02d}")
            continue
        name = str(value).strip().rstrip(">")
        name = re.sub(r"[\s/]+", "_", name)
        name = re.sub(r"[^0-9A-Za-z_]+", "_", name)
        name = re.sub(r"_+", "_", name).strip("_").lower()
        names.append(name or f"col_{idx:02d}")
    return names


def load_raw_bins(xlsx_path: Path) -> pd.DataFrame:
    raw = pd.read_excel(xlsx_path, sheet_name="data", header=None)
    header_idx = detect_header_row(raw)
    header_row = raw.loc[header_idx]
    normed = normalize_header_row(header_row)

    mag_indices = [
        idx
        for idx, value in enumerate(header_row)
        if isinstance(value, str) and value.startswith("<Mag")
    ]
    keep_mask = [idx not in mag_indices for idx in range(len(normed))]
    columns = [name for idx, name in enumerate(normed) if keep_mask[idx]]

    df = raw.iloc[header_idx + 1 :, keep_mask].copy()
    df.columns = columns

    rename_map = {
        "i1": "i1_dbm",
        "q1": "q1_dbm",
        "i2": "i2_dbm",
        "q2": "q2_dbm",
        "p": "bin_idx",
        "p_c": "bin_idx",
        "p_c_": "bin_idx",
        "measurement_distance_m": "bin_range_m",
        "material": "type_of_material_number",
        "meranie": "measure_title_raw",
        "measured_object": "measured_object_raw",
        "measure_number": "sample_type_raw",
    }
    for old_name, new_name in rename_map.items():
        if old_name in df.columns:
            df = df.rename(columns={old_name: new_name})

    numeric_cols = [
        "i1_dbm",
        "q1_dbm",
        "i2_dbm",
        "q2_dbm",
        "bin_idx",
        "bin_range_m",
        "start_frequency_mhz",
        "stop_frequency_mhz",
        "ramp_time_ms",
        "attenuation_db",
        "bin_size_mm",
        "bin_size_hz",
        "number_of_samples",
        "zero_pad_factor",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df[df["source_file"].notna()].copy()
    df["source_file"] = df["source_file"].map(normalize_text)
    df = df[df["source_file"].notna()].copy()

    df = df[df["bin_idx"].notna()].copy()
    df["bin_idx"] = df["bin_idx"].astype(int)
    df["measurement_id"] = df["source_file"].map(make_public_measurement_id)
    df["series_prefix"] = df["source_file"].str.split("_").str[0]
    df["series_prefix_norm"] = df["series_prefix"].map(normalize_key)
    df["sample_type_norm"] = df["type_of_material_number"].map(normalize_key)

    # Notebook-compatible target/background labeling.
    df["is_target_bin_w2"] = df["bin_idx"].isin([2, 3])
    df["is_target_bin_w3"] = df["bin_idx"].isin([2, 3, 4])

    ns = pd.to_numeric(df["number_of_samples"], errors="coerce")
    bg_mask = ((df["bin_idx"] == 1) | (df["bin_idx"] >= (ns - 1))) & ns.notna()
    df["is_background_bin"] = bg_mask & ~(df["is_target_bin_w2"] | df["is_target_bin_w3"])

    if "cw_fmcw" in df.columns:
        df["cw_fmcw"] = df["cw_fmcw"].map(normalize_text)

    return df


def pick_catalog_col(df: pd.DataFrame, candidates: list[str]) -> str:
    for col in candidates:
        if col in df.columns:
            return col
    raise KeyError(f"Expected one of {candidates}, found columns: {list(df.columns)}")


def load_catalog(xlsx_path: Path) -> pd.DataFrame:
    df = pd.read_excel(xlsx_path, sheet_name="Ciselnik Merani", header=2)

    measure_title_col = pick_catalog_col(df, ["Unnamed: 1", "Measure title"])
    sample_type_col = pick_catalog_col(df, ["Číslo typu vzorku", "číslo typu vzorku"])
    measured_object_col = pick_catalog_col(df, ["Measured object"])

    keep_cols = {
        "measure_title_key": measure_title_col,
        "sample_type_key": sample_type_col,
        "measured_object_label": measured_object_col,
    }
    optional = {
        "place_label": "Place",
        "refl_defl_ni_label": "Refl / Defl / nič",
        "orientation_label": "orientation",
        "cw_fmcw_label": "FMCW/CW",
        "vzd_refl_stena_label": "Vzd. (refl - stena)",
        "vzd_radar_stena_label": "Vzd. (radar - stena",
    }
    for public_name, source_name in optional.items():
        if source_name in df.columns:
            keep_cols[public_name] = source_name

    catalog = df[list(keep_cols.values())].rename(columns={v: k for k, v in keep_cols.items()})
    catalog["measure_title_norm"] = catalog["measure_title_key"].map(normalize_key)
    catalog["sample_type_norm"] = catalog["sample_type_key"].map(normalize_key)
    catalog["measured_object_label"] = catalog["measured_object_label"].map(normalize_text)

    duplicate_mask = catalog.duplicated(subset=["measure_title_norm", "sample_type_norm"], keep=False)
    if duplicate_mask.any():
        catalog = catalog.drop_duplicates(subset=["measure_title_norm", "sample_type_norm"], keep="first")

    return catalog


def load_material_mapping(mapping_path: Path, overrides_path: Path | None = None) -> pd.DataFrame:
    mapping = pd.read_csv(mapping_path)
    if overrides_path is not None and overrides_path.exists():
        overrides = pd.read_csv(overrides_path)
        mapping = pd.concat([mapping, overrides], ignore_index=True)
    mapping["material_name_norm"] = mapping["material_name_auto"].map(normalize_key)
    mapping = mapping.drop_duplicates(subset=["material_name_norm"], keep="last")
    return mapping


def attach_labels(raw_bins: pd.DataFrame, catalog: pd.DataFrame, mapping: pd.DataFrame) -> pd.DataFrame:
    mapped = raw_bins.merge(
        catalog,
        left_on=["series_prefix_norm", "sample_type_norm"],
        right_on=["measure_title_norm", "sample_type_norm"],
        how="left",
    )

    if "measured_object_raw" in mapped.columns:
        mapped["measured_object_label"] = mapped["measured_object_label"].fillna(
            mapped["measured_object_raw"].map(normalize_text)
        )
    if "place" in mapped.columns and "place_label" in mapped.columns:
        mapped["place_label"] = mapped["place_label"].fillna(mapped["place"].map(normalize_text))
    if "refl_defl_ni" in mapped.columns and "refl_defl_ni_label" in mapped.columns:
        mapped["refl_defl_ni_label"] = mapped["refl_defl_ni_label"].fillna(
            mapped["refl_defl_ni"].map(normalize_text)
        )
    if "orientation" in mapped.columns and "orientation_label" in mapped.columns:
        mapped["orientation_label"] = mapped["orientation_label"].fillna(
            mapped["orientation"].map(normalize_text)
        )
    if "cw_fmcw" in mapped.columns and "cw_fmcw_label" in mapped.columns:
        mapped["cw_fmcw_label"] = mapped["cw_fmcw_label"].fillna(mapped["cw_fmcw"].map(normalize_text))

    mapped["material_name_auto"] = mapped["measured_object_label"].map(normalize_text)
    mapped["material_name_norm"] = mapped["material_name_auto"].map(normalize_key)
    mapped = mapped.merge(
        mapping[["material_name_norm", "material_name_auto", "material_primary", "material_secondary", "obal"]],
        on="material_name_norm",
        how="left",
        suffixes=("", "_mapped"),
    )
    mapped["material_name_auto"] = mapped["material_name_auto"].fillna(mapped["material_name_auto_mapped"])
    mapped["has_biomass"] = np.where(
        mapped["material_primary"].eq("unknown"),
        pd.NA,
        mapped["material_primary"].eq("biomass") | mapped["material_secondary"].eq("biomass"),
    )
    mapped["is_background"] = mapped["material_primary"].eq("background")

    conditions = [
        mapped["material_primary"].notna(),
        mapped["measured_object_label"].notna(),
    ]
    choices = ["catalog+mapping", "catalog_only"]
    mapped["label_source"] = np.select(conditions, choices, default="unmatched")

    qc_flags = []
    qc_flags.append(np.where(mapped["measured_object_label"].isna(), "missing_catalog_label", ""))
    qc_flags.append(np.where(mapped["material_primary"].isna(), "missing_material_mapping", ""))
    qc_flags.append(np.where(mapped["bin_size_mm"].fillna(0) <= 0, "invalid_bin_size", ""))
    qc_flags.append(
        np.where(
            mapped["active_channels"].astype(str).ne("I1, Q1, I2, Q2"),
            "partial_channels",
            "",
        )
    )
    qc_flags.append(
        np.where(
            ~mapped["number_of_samples"].isin([17, 32, 33]),
            "nonstandard_sequence_length",
            "",
        )
    )

    flag_frame = pd.DataFrame(qc_flags).T
    mapped["qc_flags"] = flag_frame.apply(
        lambda row: "|".join(flag for flag in row if flag),
        axis=1,
    )

    return mapped


def apply_subset_filter(df: pd.DataFrame, subset: str) -> pd.DataFrame:
    if subset == "all":
        return df.copy()
    if subset == "core":
        mask = (
            df["bin_size_mm"].fillna(0) > 0
        ) & df["number_of_samples"].isin([17, 32, 33]) & df["active_channels"].eq("I1, Q1, I2, Q2")
        return df[mask].copy()
    if subset == "extended":
        mask = (
            (df["bin_size_mm"].fillna(0) <= 0)
            | ~df["number_of_samples"].isin([17, 32, 33])
            | df["active_channels"].ne("I1, Q1, I2, Q2")
        )
        return df[mask].copy()
    raise ValueError(f"Unsupported subset: {subset}")


def build_measurement_tables(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    metadata_cols = [
        "series_prefix",
        "type_of_material_number",
        "sample_type_norm",
        "cw_fmcw",
        "attenuation_db",
        "ramp_time_ms",
        "bin_size_mm",
        "bin_size_hz",
        "number_of_samples",
        "start_frequency_mhz",
        "stop_frequency_mhz",
        "zero_pad_factor",
        "active_channels",
        "radar_no",
        "interface",
        "magnitude_unit",
        "place_label",
        "refl_defl_ni_label",
        "orientation_label",
        "vzd_refl_stena_label",
        "vzd_radar_stena_label",
        "qc_flags",
    ]
    metadata_cols = [col for col in metadata_cols if col in df.columns]
    measurement_metadata = df.groupby("measurement_id")[metadata_cols].agg(first_non_null).reset_index()

    label_cols = [
        "material_name_auto",
        "material_primary",
        "material_secondary",
        "obal",
        "has_biomass",
        "is_background",
        "label_source",
    ]
    label_cols = [col for col in label_cols if col in df.columns]
    measurement_labels = df.groupby("measurement_id")[label_cols].agg(first_non_null).reset_index()

    provenance_cols = [
        "source_file",
        "series_prefix",
        "type_of_material_number",
        "sample_type_norm",
        "label_source",
        "qc_flags",
    ]
    provenance_cols = [col for col in provenance_cols if col in df.columns]
    measurement_provenance = df.groupby("measurement_id")[provenance_cols].agg(first_non_null).reset_index()

    measurement_bins = df[
        [
            "measurement_id",
            "bin_idx",
            "bin_range_m",
            "i1_dbm",
            "q1_dbm",
            "i2_dbm",
            "q2_dbm",
            "is_target_bin_w2",
            "is_target_bin_w3",
            "is_background_bin",
        ]
    ].copy()
    measurement_bins = measurement_bins.sort_values(["measurement_id", "bin_idx"]).reset_index(drop=True)

    return measurement_bins, measurement_metadata, measurement_labels, measurement_provenance


def build_group_split(metadata: pd.DataFrame, seed: int) -> pd.DataFrame:
    fields = [
        "series_prefix",
        "type_of_material_number",
        "cw_fmcw",
        "attenuation_db",
        "ramp_time_ms",
        "bin_size_mm",
        "number_of_samples",
        "place_label",
        "orientation_label",
        "refl_defl_ni_label",
    ]
    fields = [col for col in fields if col in metadata.columns]

    def make_group_id(row: pd.Series) -> str:
        parts = [normalize_text(row.get(col, "")) or "" for col in fields]
        key = "|".join(parts)
        digest = hashlib.sha1(key.encode("utf-8")).hexdigest()
        return f"g_{digest[:16]}"

    split_df = metadata[["measurement_id"] + fields].copy()
    split_df["capture_group_id"] = split_df.apply(make_group_id, axis=1)

    unique_groups = split_df["capture_group_id"].drop_duplicates().sort_values().tolist()
    split_map: dict[str, str] = {}
    for group_id in unique_groups:
        digest = hashlib.sha1(f"{seed}:{group_id}".encode("utf-8")).hexdigest()
        bucket = int(digest[:8], 16) % 100
        if bucket < 70:
            split_map[group_id] = "train"
        elif bucket < 85:
            split_map[group_id] = "val"
        else:
            split_map[group_id] = "test"

    split_df["split"] = split_df["capture_group_id"].map(split_map)
    split_df["split_scheme"] = "group_hash_v1"
    return split_df


def build_tensor_export(measurement_bins: pd.DataFrame, output_path: Path) -> dict[str, object]:
    channels = ["i1_dbm", "q1_dbm", "i2_dbm", "q2_dbm"]
    measurement_ids = measurement_bins["measurement_id"].drop_duplicates().tolist()
    max_len = int(measurement_bins["bin_idx"].max())

    signal = np.full((len(measurement_ids), max_len, len(channels)), np.nan, dtype=np.float32)
    valid_mask = np.zeros((len(measurement_ids), max_len), dtype=bool)
    seq_len = np.zeros((len(measurement_ids),), dtype=np.int32)

    measurement_index = {mid: idx for idx, mid in enumerate(measurement_ids)}
    for measurement_id, group in measurement_bins.groupby("measurement_id"):
        row_idx = measurement_index[measurement_id]
        positions = group["bin_idx"].to_numpy(dtype=int) - 1
        valid_mask[row_idx, positions] = True
        seq_len[row_idx] = len(group)
        for channel_idx, channel in enumerate(channels):
            signal[row_idx, positions, channel_idx] = group[channel].to_numpy(dtype=np.float32)

    np.savez_compressed(
        output_path,
        measurement_id=np.array(measurement_ids, dtype="U32"),
        signal=signal,
        valid_mask=valid_mask,
        seq_len=seq_len,
        bin_indices=np.arange(1, max_len + 1, dtype=np.int32),
        channel_names=np.array(channels, dtype="U16"),
    )

    return {
        "measurement_count": len(measurement_ids),
        "max_seq_len": max_len,
        "channel_count": len(channels),
    }


def write_data_dictionary(output_path: Path) -> None:
    rows = [
        ("measurement_id", "public stable identifier for a single radar capture", "string"),
        ("bin_idx", "1-based radar bin index inside a single capture", "integer"),
        ("bin_range_m", "distance represented by the radar bin, not object distance", "float"),
        ("i1_dbm", "I1 channel magnitude in dBm", "float"),
        ("q1_dbm", "Q1 channel magnitude in dBm", "float"),
        ("i2_dbm", "I2 channel magnitude in dBm", "float"),
        ("q2_dbm", "Q2 channel magnitude in dBm", "float"),
        ("is_target_bin_w2", "target-window flag using bins {2,3}", "boolean"),
        ("is_target_bin_w3", "target-window flag using bins {2,3,4}", "boolean"),
        ("is_background_bin", "background-bin flag using bin 1 and the trailing bins", "boolean"),
        ("material_name_auto", "curated fine-grained object or material label", "string"),
        ("material_primary", "curated coarse material class", "string"),
        ("material_secondary", "optional secondary material class", "string"),
        ("obal", "optional packaging or container context", "string"),
        ("has_biomass", "binary flag for biomass presence", "boolean"),
        ("capture_group_id", "group identifier used for leakage-safe data splitting", "string"),
        ("split", "recommended split assignment", "string"),
    ]
    df = pd.DataFrame(rows, columns=["column_name", "description", "dtype"])
    df.to_csv(output_path, index=False)


def build_summary(
    measurement_bins: pd.DataFrame,
    measurement_labels: pd.DataFrame,
    measurement_metadata: pd.DataFrame,
    split_df: pd.DataFrame,
    subset: str,
    tensor_meta: dict[str, object],
) -> dict[str, object]:
    material_counts = measurement_labels["material_primary"].fillna("NA").value_counts(dropna=False)
    split_counts = split_df["split"].fillna("NA").value_counts(dropna=False)
    summary = {
        "subset": subset,
        "measurement_count": int(measurement_metadata["measurement_id"].nunique()),
        "bin_row_count": int(len(measurement_bins)),
        "material_primary_counts": {str(k): int(v) for k, v in material_counts.items()},
        "split_counts": {str(k): int(v) for k, v in split_counts.items()},
    }
    summary.update(tensor_meta)
    return summary


def normalize_for_parquet(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        if out[col].dtype == object:
            out[col] = out[col].astype("string")
    return out


def export_dataset(
    xlsx_path: Path,
    mapping_path: Path,
    output_dir: Path,
    subset: str,
    seed: int,
    mapping_overrides_path: Path | None = None,
) -> None:
    raw_bins = load_raw_bins(xlsx_path)
    catalog = load_catalog(xlsx_path)
    mapping = load_material_mapping(mapping_path, overrides_path=mapping_overrides_path)
    labeled_bins = attach_labels(raw_bins, catalog, mapping)
    subset_bins = apply_subset_filter(labeled_bins, subset)

    if subset_bins.empty:
        raise ValueError(f"No rows left after applying subset filter: {subset}")

    (
        measurement_bins,
        measurement_metadata,
        measurement_labels,
        measurement_provenance,
    ) = build_measurement_tables(subset_bins)
    split_df = build_group_split(measurement_metadata, seed=seed)

    output_dir.mkdir(parents=True, exist_ok=True)
    normalize_for_parquet(measurement_bins).to_parquet(output_dir / "measurement_bins.parquet", index=False)
    normalize_for_parquet(measurement_metadata).to_parquet(output_dir / "measurement_metadata.parquet", index=False)
    normalize_for_parquet(measurement_labels).to_parquet(output_dir / "measurement_labels.parquet", index=False)
    normalize_for_parquet(measurement_provenance).to_parquet(output_dir / "measurement_provenance.parquet", index=False)
    normalize_for_parquet(split_df).to_parquet(output_dir / "splits.parquet", index=False)
    write_data_dictionary(output_dir / "data_dictionary.csv")

    tensor_meta = build_tensor_export(measurement_bins, output_dir / "measurement_tensor.npz")
    summary = build_summary(
        measurement_bins=measurement_bins,
        measurement_labels=measurement_labels,
        measurement_metadata=measurement_metadata,
        split_df=split_df,
        subset=subset,
        tensor_meta=tensor_meta,
    )
    with (output_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xlsx", type=Path, default=DEFAULT_XLSX)
    parser.add_argument("--mapping-csv", type=Path, default=DEFAULT_MAPPING)
    parser.add_argument("--mapping-overrides-csv", type=Path, default=DEFAULT_MAPPING_OVERRIDES)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--subset", choices=["core", "extended", "all"], default="core")
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    export_dataset(
        xlsx_path=args.xlsx,
        mapping_path=args.mapping_csv,
        output_dir=args.output_dir,
        subset=args.subset,
        seed=args.seed,
        mapping_overrides_path=args.mapping_overrides_csv,
    )


if __name__ == "__main__":
    main()
