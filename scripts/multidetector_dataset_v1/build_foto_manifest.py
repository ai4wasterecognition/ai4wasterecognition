#!/usr/bin/env python3
"""Build EXIF-based photo manifest for the multidetector lab session photos.

For each .jpg in the photo folder, extract DateTime from EXIF (or from filename),
then map it to the nearest measurement_id (by acquisition time within ±tolerance).

Writes:
    release/multidetector_dataset_v1/aux/foto_manifest.csv
"""

from __future__ import annotations

import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from PIL import Image
from PIL.ExifTags import TAGS

DEFAULT_FOTO_DIR = Path("data/multidetektor/Lab Experimenty Video a 24GHz radar/Foto")
DEFAULT_META = Path("release/multidetector_dataset_v1/measurement_metadata.parquet")
DEFAULT_LABELS = Path("release/multidetector_dataset_v1/measurement_labels.parquet")
DEFAULT_OUT = Path("release/multidetector_dataset_v1/aux/foto_manifest.csv")

FILENAME_RE = re.compile(r"^(\d{8})_(\d{6})\.jpg$", re.IGNORECASE)
DEFAULT_TOLERANCE_SEC = 120


def parse_jpg_timestamp(path: Path) -> datetime | None:
    """Try EXIF DateTimeOriginal → EXIF DateTime → filename pattern."""
    try:
        img = Image.open(path)
        exif = img.getexif()
        info = {TAGS.get(k, k): v for k, v in exif.items()}
        for key in ("DateTimeOriginal", "DateTime"):
            raw = info.get(key)
            if raw:
                try:
                    return datetime.strptime(str(raw), "%Y:%m:%d %H:%M:%S")
                except ValueError:
                    pass
    except Exception:
        pass

    m = FILENAME_RE.match(path.name)
    if m:
        try:
            return datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S")
        except ValueError:
            return None
    return None


def parse_measurement_dt(date_str: str, time_str: str) -> datetime:
    return datetime.strptime(f"{date_str} {time_str[:8]}", "%Y-%m-%d %H:%M:%S")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--foto-dir", type=Path, default=DEFAULT_FOTO_DIR)
    p.add_argument("--metadata", type=Path, default=DEFAULT_META)
    p.add_argument("--labels", type=Path, default=DEFAULT_LABELS)
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument("--tolerance-sec", type=int, default=DEFAULT_TOLERANCE_SEC)
    args = p.parse_args()

    meta = pd.read_parquet(args.metadata)[["measurement_id", "nb_of_sample", "date", "time"]]
    labels = pd.read_parquet(args.labels)[["measurement_id", "label_category", "label_name"]]
    df_meta = meta.merge(labels, on="measurement_id")
    df_meta["dt"] = [parse_measurement_dt(d, t) for d, t in zip(df_meta["date"], df_meta["time"])]
    df_meta = df_meta.sort_values("dt").reset_index(drop=True)
    meta_dts = df_meta["dt"].tolist()

    jpgs = sorted(args.foto_dir.glob("*.jpg"))
    if not jpgs:
        raise SystemExit(f"No .jpg files in {args.foto_dir}")

    rows = []
    tol = timedelta(seconds=args.tolerance_sec)
    for jpg in jpgs:
        ts = parse_jpg_timestamp(jpg)
        nearest = None
        diff = None
        nb = None
        cat = None
        name = None
        if ts is not None:
            # find the row with the smallest abs time difference
            diffs = [(abs((m - ts).total_seconds()), i) for i, m in enumerate(meta_dts)]
            diffs.sort()
            best_sec, best_idx = diffs[0]
            if best_sec <= args.tolerance_sec:
                row = df_meta.iloc[best_idx]
                nearest = row["measurement_id"]
                nb = int(row["nb_of_sample"])
                cat = row["label_category"]
                name = row["label_name"]
                diff = round(best_sec, 3)
            else:
                # outside tolerance — still record the nearest as hint
                row = df_meta.iloc[best_idx]
                nearest = row["measurement_id"]
                nb = int(row["nb_of_sample"])
                cat = row["label_category"]
                name = row["label_name"]
                diff = round(best_sec, 3)
        rows.append({
            "filename": jpg.name,
            "exif_dt": ts.isoformat() if ts else "",
            "nearest_measurement_id": nearest or "",
            "nearest_nb_of_sample": nb if nb is not None else "",
            "nearest_label_category": cat or "",
            "nearest_label_name": name or "",
            "time_diff_sec": diff if diff is not None else "",
            "within_tolerance": (diff is not None and diff <= args.tolerance_sec),
        })

    df = pd.DataFrame(rows)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)

    print(f"[OK] {len(df)} photos -> {args.out}")
    within = df["within_tolerance"].sum()
    print(f"     within ±{args.tolerance_sec}s tolerance: {within}/{len(df)}")
    print()
    print("Per-Nb counts (within tolerance only):")
    in_tol = df[df["within_tolerance"]]
    print(in_tol.groupby("nearest_nb_of_sample").size().to_string())


if __name__ == "__main__":
    main()
