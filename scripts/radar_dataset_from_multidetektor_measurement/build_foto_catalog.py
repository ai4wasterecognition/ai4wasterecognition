#!/usr/bin/env python3
"""Build the sample-photo catalog and copy photos into the release.

Reads numbered/named sample photos from data/Foto/ (naming convention
`Nb.<num>_<english description>_<view>.jpg`) and produces:

    release/radar_dataset_from_multidetektor_measurement/photos/         (copied images)
    release/radar_dataset_from_multidetektor_measurement/aux/foto_catalog.csv

Each photo carries the same sample number (Nb) as the radar measurements,
so radar frames and photos can be cross-referenced 1:1 by nb_of_sample.

foto_catalog.csv columns:
    filename            photo file name (under photos/)
    nb_of_sample        integer sample number, or empty for setup slides
    description         English description parsed from the file name
    view                slide/view label (a, b, c, A, B) when present
    is_setup            true for the measurement-setup slides
    has_radar_match     true if nb_of_sample exists in the radar release
"""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

import pandas as pd

DEFAULT_FOTO_DIR = Path("data/Foto")
DEFAULT_RELEASE = Path("release/radar_dataset_from_multidetektor_measurement")

NB_RE = re.compile(r"Nb\.?\s*0*(\d+)", re.IGNORECASE)
VIEW_RE = re.compile(r"(?:[._\s]sl[._\s]*|view)([abcABC])\b", re.IGNORECASE)
IMAGE_EXTS = {".jpg", ".jpeg", ".png"}


def radar_nb_set(release: Path) -> set[int]:
    labels = pd.read_parquet(release / "measurement_labels.parquet")
    return set(int(x) for x in labels["nb_of_sample"].unique())


def parse_photo(name: str) -> dict:
    stem = Path(name).stem
    is_setup = bool(re.match(r"^measurement[ _]?setup", stem, re.IGNORECASE))

    nb = None
    if not is_setup:
        m = NB_RE.search(stem)
        if m:
            nb = int(m.group(1))

    view = ""
    vm = VIEW_RE.search(stem)
    if vm:
        view = vm.group(1).lower()

    # description: drop the leading Nb.<n>_ and the trailing view marker
    desc = stem
    desc = NB_RE.sub("", desc, count=1)
    desc = VIEW_RE.sub("", desc)
    desc = desc.replace("_", " ").replace(".", " ")
    desc = re.sub(r"\s+", " ", desc).strip(" -")
    if is_setup:
        desc = re.sub(r"(?i)measurement[ _]?setup", "Measurement setup", desc).strip()

    return {
        "nb_of_sample": nb,
        "description": desc,
        "view": view,
        "is_setup": is_setup,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--foto-dir", type=Path, default=DEFAULT_FOTO_DIR)
    p.add_argument("--release", type=Path, default=DEFAULT_RELEASE)
    p.add_argument("--no-copy", action="store_true", help="Only build the catalog, do not copy images")
    args = p.parse_args()

    photos = sorted(
        f for f in args.foto_dir.iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTS
    )
    if not photos:
        raise SystemExit(f"No images in {args.foto_dir}")

    radar_nb = radar_nb_set(args.release)

    photos_out = args.release / "photos"
    if not args.no_copy:
        photos_out.mkdir(parents=True, exist_ok=True)

    rows = []
    for src in photos:
        info = parse_photo(src.name)
        nb = info["nb_of_sample"]
        rows.append({
            "filename": src.name,
            "nb_of_sample": "" if nb is None else nb,
            "description": info["description"],
            "view": info["view"],
            "is_setup": info["is_setup"],
            "has_radar_match": (nb in radar_nb) if nb is not None else False,
        })
        if not args.no_copy:
            shutil.copy2(src, photos_out / src.name)

    df = pd.DataFrame(rows).sort_values(
        ["is_setup", "nb_of_sample", "view"], key=lambda s: s if s.name != "nb_of_sample" else pd.to_numeric(s, errors="coerce")
    )
    catalog_path = args.release / "aux" / "foto_catalog.csv"
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(catalog_path, index=False)

    n_setup = int(df["is_setup"].sum())
    n_sample = len(df) - n_setup
    n_match = int(df["has_radar_match"].sum())
    nbs_with_photos = sorted(int(x) for x in df["nb_of_sample"] if x != "")
    nbs_no_radar = sorted(set(nbs_with_photos) - radar_nb)

    print(f"[OK] catalog: {catalog_path}  ({len(df)} photos: {n_sample} samples + {n_setup} setup)")
    if not args.no_copy:
        print(f"[OK] copied {len(df)} images -> {photos_out}")
    print(f"     photos with radar match: {n_match}")
    print(f"     sample Nb with photos:   {sorted(set(nbs_with_photos))}")
    print(f"     photo-only Nb (no radar): {nbs_no_radar}")


if __name__ == "__main__":
    main()
