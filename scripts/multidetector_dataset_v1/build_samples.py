#!/usr/bin/env python3
"""Generate small GitHub-safe preview files for the multidetector dataset.

Writes:
    samples/multidetector_dataset_v1/sample_frame.txt              (1 raw frame, verbatim)
    samples/multidetector_dataset_v1/sample_labels_head25.csv
    samples/multidetector_dataset_v1/sample_metadata_head25.csv
    samples/multidetector_dataset_v1/sample_bins_first_measurement.csv
    samples/multidetector_dataset_v1/README.md
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import pandas as pd

RAW_ROOT = Path("data/multidetektor/meranie_23_04")
RELEASE = Path("release/multidetector_dataset_v1")
OUT = Path("samples/multidetector_dataset_v1")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--raw-root", type=Path, default=RAW_ROOT)
    p.add_argument("--release", type=Path, default=RELEASE)
    p.add_argument("--out", type=Path, default=OUT)
    args = p.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)

    # 1) one verbatim raw .txt frame (Nb=10, very first frame)
    candidates = sorted(args.raw_root.glob("2026-04-23_13-14-01.859/FD/*.txt"))
    if not candidates:
        raise SystemExit("No example .txt found")
    src = candidates[0]
    shutil.copy(src, args.out / "sample_frame.txt")

    # 2) head25 of labels
    labels = pd.read_parquet(args.release / "measurement_labels.parquet")
    labels.head(25).to_csv(args.out / "sample_labels_head25.csv", index=False)

    # 3) head25 of metadata
    meta = pd.read_parquet(args.release / "measurement_metadata.parquet")
    meta.head(25).to_csv(args.out / "sample_metadata_head25.csv", index=False)

    # 4) bins for the first measurement_id (17 bins)
    bins = pd.read_parquet(args.release / "measurement_bins.parquet")
    first_mid = bins["measurement_id"].iloc[0]
    bins[bins["measurement_id"] == first_mid].to_csv(
        args.out / "sample_bins_first_measurement.csv", index=False
    )

    # 5) README
    readme = f"""# multidetector_dataset_v1 — Samples

Small GitHub-friendly previews of the [`release/multidetector_dataset_v1/`](../../release/multidetector_dataset_v1/) package.

| File | Description |
|---|---|
| `sample_frame.txt` | One raw radar .txt frame (Nb=10, Empty container, 17 bins × 4 channels) — verbatim copy from the original radar export |
| `sample_labels_head25.csv` | First 25 rows of `measurement_labels.parquet` |
| `sample_metadata_head25.csv` | First 25 rows of `measurement_metadata.parquet` |
| `sample_bins_first_measurement.csv` | All 17 bin rows for the first measurement (`{first_mid}`) |

For the full dataset (2950 frames × 17 bins × 4 channels, parquet + npz + splits),
see [`release/multidetector_dataset_v1/README.md`](../../release/multidetector_dataset_v1/README.md).
"""
    (args.out / "README.md").write_text(readme)

    print(f"[OK] wrote previews to {args.out}")
    for f in sorted(args.out.iterdir()):
        size = f.stat().st_size
        print(f"     {f.name}  ({size} B)")


if __name__ == "__main__":
    main()
