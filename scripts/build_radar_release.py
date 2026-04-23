#!/usr/bin/env python3
"""Build a local radar dataset release package and GitHub-safe samples."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

from export_radar_dataset import (
    DEFAULT_MAPPING,
    DEFAULT_MAPPING_OVERRIDES,
    DEFAULT_XLSX,
    export_dataset,
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_checksums(root: Path) -> None:
    lines = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if rel.name == "checksums.sha256":
            continue
        lines.append(f"{sha256_file(path)}  {rel.as_posix()}")
    (root / "checksums.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_release_readme(root: Path, summary: dict[str, object]) -> None:
    text = f"""# AI4WasteRecognition Radar Dataset Release

This local release package was generated from the `WasteR` workspace.

Contents:

- `core/` clean benchmark-oriented subset
- `extended/` atypical or lower-consistency subset
- `summary.json` combined release summary
- `checksums.sha256` file checksums

Counts:

- core measurements: {summary['core']['measurement_count']}
- core bin rows: {summary['core']['bin_row_count']}
- extended measurements: {summary['extended']['measurement_count']}
- extended bin rows: {summary['extended']['bin_row_count']}

This package is intended for local review before any public archival release.
"""
    (root / "README.md").write_text(text, encoding="utf-8")


def write_samples(release_root: Path, samples_dir: Path) -> None:
    samples_dir.mkdir(parents=True, exist_ok=True)

    labels = pd.read_parquet(release_root / "core" / "measurement_labels.parquet")
    metadata = pd.read_parquet(release_root / "core" / "measurement_metadata.parquet")
    bins = pd.read_parquet(release_root / "core" / "measurement_bins.parquet")

    labels.head(25).to_csv(samples_dir / "radar_core_measurement_labels_sample.csv", index=False)
    metadata.head(25).to_csv(samples_dir / "radar_core_measurement_metadata_sample.csv", index=False)

    first_measurement_id = bins["measurement_id"].iloc[0]
    bins[bins["measurement_id"] == first_measurement_id].head(40).to_csv(
        samples_dir / "radar_core_measurement_bins_sample.csv",
        index=False,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xlsx", type=Path, default=DEFAULT_XLSX)
    parser.add_argument("--mapping-csv", type=Path, default=DEFAULT_MAPPING)
    parser.add_argument("--mapping-overrides-csv", type=Path, default=DEFAULT_MAPPING_OVERRIDES)
    parser.add_argument("--release-dir", type=Path, default=Path("release/radar_dataset_v1"))
    parser.add_argument("--samples-dir", type=Path, default=Path("samples"))
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    release_dir = args.release_dir
    core_dir = release_dir / "core"
    extended_dir = release_dir / "extended"
    release_dir.mkdir(parents=True, exist_ok=True)

    export_dataset(
        xlsx_path=args.xlsx,
        mapping_path=args.mapping_csv,
        mapping_overrides_path=args.mapping_overrides_csv,
        output_dir=core_dir,
        subset="core",
        seed=args.seed,
    )
    export_dataset(
        xlsx_path=args.xlsx,
        mapping_path=args.mapping_csv,
        mapping_overrides_path=args.mapping_overrides_csv,
        output_dir=extended_dir,
        subset="extended",
        seed=args.seed,
    )

    combined_summary = {
        "core": json.loads((core_dir / "summary.json").read_text(encoding="utf-8")),
        "extended": json.loads((extended_dir / "summary.json").read_text(encoding="utf-8")),
    }
    (release_dir / "summary.json").write_text(json.dumps(combined_summary, indent=2), encoding="utf-8")
    write_release_readme(release_dir, combined_summary)
    write_checksums(release_dir)
    write_samples(release_dir, args.samples_dir)


if __name__ == "__main__":
    main()
