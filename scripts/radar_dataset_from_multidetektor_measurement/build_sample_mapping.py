#!/usr/bin/env python3
"""Build sample_mapping.csv from VysledkyPreStatistiku.xlsx.

Derives canonical (Nb -> label_name, label_category) per measurement from the
manually maintained xlsx. Drops excluded Nb (default: 90). Also derives
label_contamination_present as (label_category != 'Reference measurement').

Output: processed/radar_dataset_from_multidetektor_measurement/sample_mapping.csv
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

import openpyxl
import pandas as pd

DEFAULT_XLSX = Path("data/multidetektor/VysledkyPreStatistiku.xlsx")
DEFAULT_OUT = Path("processed/radar_dataset_from_multidetektor_measurement/sample_mapping.csv")
EXCLUDE_NB = {90}


def load_mapping_from_xlsx(xlsx_path: Path) -> pd.DataFrame:
    wb = openpyxl.load_workbook(xlsx_path, data_only=True, read_only=True)
    ws = wb["data"]

    nb_to_names: dict[int, set] = defaultdict(set)
    nb_to_categories: dict[int, set] = defaultdict(set)

    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i == 0:
            continue
        nb = row[20]
        name = row[21]
        category = row[22]
        if nb is None:
            continue
        nb_to_names[int(nb)].add(str(name).strip() if name is not None else None)
        nb_to_categories[int(nb)].add(str(category).strip() if category is not None else None)

    rows = []
    for nb in sorted(nb_to_names):
        names = {n for n in nb_to_names[nb] if n is not None}
        cats = {c for c in nb_to_categories[nb] if c is not None}
        if len(names) != 1:
            raise ValueError(f"Nb={nb} has multiple Name o sample values: {names}")
        if len(cats) != 1:
            raise ValueError(f"Nb={nb} has multiple Category values: {cats}")
        label_name = names.pop()
        label_category = cats.pop()
        rows.append({
            "nb_of_sample": nb,
            "label_name": label_name,
            "label_category": label_category,
            "label_contamination_present": label_category != "Reference measurement",
        })
    return pd.DataFrame(rows)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--xlsx", type=Path, default=DEFAULT_XLSX)
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument("--include-excluded", action="store_true",
                   help="Include Nb in EXCLUDE_NB (default: drop)")
    args = p.parse_args()

    df = load_mapping_from_xlsx(args.xlsx)
    if not args.include_excluded:
        df = df[~df["nb_of_sample"].isin(EXCLUDE_NB)].reset_index(drop=True)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)

    print(f"[OK] wrote {len(df)} rows -> {args.out}")
    print(df.to_string(index=False))
    print()
    print("Category distribution:")
    print(df["label_category"].value_counts().to_string())


if __name__ == "__main__":
    main()
