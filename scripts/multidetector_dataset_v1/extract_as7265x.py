#!/usr/bin/env python3
"""Extract AS7265x UV-VIS spectrometer measurements from the Word protocol.

Reads:
    data/multidetektor/Protokol_AS7265x_s_datami_.docx

Writes:
    release/multidetector_dataset_v1/aux/spectro_as7265x.parquet
    release/multidetector_dataset_v1/aux/spectro_as7265x_README.md

Structure:
    - Sensor: AS7265x, 18 channels 410..940 nm + UV (R channel ≈ 0 throughout)
    - 10 samples (Pozadie + 9 materials)
    - Each sample = 10 measurement repeats × 18 wavelengths
    - Output long-format: (sample_label, measurement_idx, wavelength_nm, intensity)
"""

from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import pandas as pd

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

DEFAULT_DOCX = Path("data/multidetektor/Protokol_AS7265x_s_datami_.docx")
DEFAULT_OUT = Path("release/multidetector_dataset_v1/aux/spectro_as7265x.parquet")
DEFAULT_README = DEFAULT_OUT.with_name("spectro_as7265x_README.md")

WAVELENGTH_RE = re.compile(r"^[A-Z]\s+(\d+)nm$")
UV_LABEL_RE = re.compile(r"^[A-Z]\s+UV$")
STATS_LABELS = {"Priemer", "Std. odch."}


def cell_text(tc: ET.Element) -> str:
    return "".join(t.text or "" for t in tc.iter(f"{W}t")).strip()


def read_tables(docx_path: Path) -> list[list[list[str]]]:
    with zipfile.ZipFile(docx_path) as z, z.open("word/document.xml") as fh:
        root = ET.parse(fh).getroot()
    body = root.find(f"{W}body")
    out: list[list[list[str]]] = []
    blocks: list[tuple[str, list[list[str]] | None]] = []
    for child in body:
        tag = child.tag.replace(W, "")
        if tag == "tbl":
            rows = []
            for tr in child.iter(f"{W}tr"):
                cells = [cell_text(tc) for tc in tr.findall(f"{W}tc")]
                rows.append(cells)
            out.append(rows)
    return out


def is_wavelength_header(row: list[str]) -> tuple[bool, list[int | None]]:
    """Returns (True, [wavelengths]) — UV column encoded as None and dropped later."""
    if not row or row[0] != "Mer.":
        return False, []
    wls: list[int | None] = []
    for cell in row[1:]:
        m = WAVELENGTH_RE.match(cell)
        if m:
            wls.append(int(m.group(1)))
            continue
        if UV_LABEL_RE.match(cell):
            wls.append(None)  # UV column, will be skipped
            continue
        return False, []
    return True, wls


def extract_data_rows(
    table: list[list[str]], wavelengths: list[int | None]
) -> list[tuple[int, dict[int, float]]]:
    """Return list of (measurement_idx, {wavelength: intensity}). UV column (wl=None) is skipped."""
    out: list[tuple[int, dict[int, float]]] = []
    for row in table[1:]:
        if not row or not row[0]:
            continue
        if row[0] in STATS_LABELS:
            continue
        try:
            mer_idx = int(row[0])
        except ValueError:
            continue
        vals = {}
        for wl, cell in zip(wavelengths, row[1:]):
            if wl is None:
                continue  # drop UV column
            try:
                vals[wl] = float(cell.replace(",", "."))
            except ValueError:
                vals[wl] = float("nan")
        out.append((mer_idx, vals))
    return out


def harvest_sample_label_from_small_table(table: list[list[str]]) -> str | None:
    """Some headers are tucked inside the 'Graf/Fotografia' cosmetic tables."""
    # Pattern A: single cell single row
    if len(table) == 1 and len(table[0]) == 1 and table[0][0]:
        return table[0][0]
    # Pattern B: 2-3 row cosmetic table containing a stray sample label
    if len(table) <= 3 and all(len(r) <= 2 for r in table):
        for r in table:
            for cell in r:
                if cell and "Graf" not in cell and "Fotografia" not in cell:
                    if not is_wavelength_header(r)[0]:
                        # exclude wavelength rows; standalone strings only
                        if "<Mag" not in cell and len(cell) < 80:
                            return cell
    return None


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--docx", type=Path, default=DEFAULT_DOCX)
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument("--readme", type=Path, default=DEFAULT_README)
    args = p.parse_args()

    tables = read_tables(args.docx)

    # Pass over tables in order, tracking current sample label, then pairing
    # consecutive wavelength data tables to a single sample.
    current_label: str | None = None
    pending_visible: list[tuple[list[int], list[list[str]]]] = []
    samples: dict[str, dict[int, dict[int, float]]] = {}

    def flush_pending():
        nonlocal pending_visible, current_label
        if not pending_visible or current_label is None:
            pending_visible = []
            return
        per_mer: dict[int, dict[int, float]] = {}
        for wl, tbl in pending_visible:
            rows = extract_data_rows(tbl, wl)
            for mer, mapping in rows:
                per_mer.setdefault(mer, {}).update(mapping)
        samples.setdefault(current_label, {})
        for mer, mapping in per_mer.items():
            samples[current_label].setdefault(mer, {}).update(mapping)
        pending_visible = []

    for tbl in tables:
        # Skip the source-code embedded table by content size
        if tbl and len(tbl[0]) == 1 and "import serial" in tbl[0][0]:
            continue

        if not tbl:
            continue

        is_wl, wls = is_wavelength_header(tbl[0])
        if is_wl:
            pending_visible.append((wls, tbl))
            continue

        # Possibly a sample label table
        label = harvest_sample_label_from_small_table(tbl)
        if label:
            # New sample starts: flush previous before assigning new label
            flush_pending()
            current_label = label
            continue

        # other tables (summary etc) — flush if data was pending
        flush_pending()

    flush_pending()

    # Build long-format dataframe
    rows = []
    for label, per_mer in samples.items():
        for mer, wl_to_val in sorted(per_mer.items()):
            for wl, val in sorted(wl_to_val.items()):
                rows.append({
                    "sample_label": label,
                    "measurement_idx": mer,
                    "wavelength_nm": wl,
                    "intensity": val,
                })
    df = pd.DataFrame(rows)
    if df.empty:
        raise RuntimeError("No spectro data parsed — check docx structure")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(args.out, index=False)

    # Stats / sanity report
    print(f"[OK] {len(df)} rows -> {args.out}")
    summary = df.groupby("sample_label").agg(
        n_measurements=("measurement_idx", "nunique"),
        n_wavelengths=("wavelength_nm", "nunique"),
        n_rows=("intensity", "size"),
    )
    print(summary.to_string())

    # Approximate mapping spectro sample → radar Nb (for cross-modal use)
    nb_hint = {
        "Pozadie   —   Referenčné meranie": [10],
        "Plast čistý": [20, 40],
        "Papier čistý": [210],
        "Papier2 čistý": [210],
        "Plast + papier": [80],
        "Plast + mokrý papier": [120, 130],
        "Mokrý papier čistý": [220],
        "Kov čistý": [180, 181, 200],
        "Plast + drevo": [50, 70, 71],
        "Plast + sklo": [140, 160],
    }
    readme = []
    readme.append("# AS7265x UV-VIS Spectrometer — Auxiliary Data")
    readme.append("")
    readme.append("**Source:** `data/multidetektor/Protokol_AS7265x_s_datami_.docx`")
    readme.append("")
    readme.append("Sensor: AMS AS7265x, 18 wavelength channels (410–940 nm + UV).")
    readme.append("LED illumination off; natural daylight only. Sensor 65 mm above sample, 90° viewing angle.")
    readme.append("")
    readme.append("This is a small **parallel** measurement set (10 reps × 18 wavelengths per material).")
    readme.append("It is **NOT** strictly 1:1 with the radar frames — each spectro sample maps to one or more radar Nb.")
    readme.append("")
    readme.append("## Schema (`spectro_as7265x.parquet`)")
    readme.append("")
    readme.append("| column | type | description |")
    readme.append("|---|---|---|")
    readme.append("| sample_label | string | Sample name (Slovak) verbatim from docx (e.g., 'Plast čistý') |")
    readme.append("| measurement_idx | int | 1..10 repeat measurement index |")
    readme.append("| wavelength_nm | int | Wavelength in nm: 410, 435, 460, 485, 510, 535, 560, 585, 610, 645, 680, 715, 760, 810, 860, 900, 940 (and UV) |")
    readme.append("| intensity | float | Raw sensor intensity (uncalibrated, 8-bit resolution) |")
    readme.append("")
    readme.append("## Spectro sample → radar Nb (suggested mapping)")
    readme.append("")
    readme.append("| spectro sample_label | radar nb_of_sample (multidetector_dataset_v1) |")
    readme.append("|---|---|")
    for k, v in nb_hint.items():
        readme.append(f"| {k} | {', '.join(str(x) for x in v)} |")
    readme.append("")
    readme.append("## Caveats (from the report)")
    readme.append("")
    readme.append("- 8-bit sensor resolution; many channels show 0 std-dev across 10 reps.")
    readme.append("- UV channel (R) is ~0 because UV LED was off.")
    readme.append("- Natural daylight illumination is not controlled.")
    readme.append("- 'Papier čistý' and 'Papier2 čistý' are nominally the same material but with different sheet thickness/orientation.")
    args.readme.write_text("\n".join(readme))
    print(f"[OK] README -> {args.readme}")


if __name__ == "__main__":
    main()
