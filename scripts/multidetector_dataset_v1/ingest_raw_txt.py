#!/usr/bin/env python3
"""Ingest raw .txt radar frames from multidetector experiment (2026-04-23).

Walks data/multidetektor/meranie_23_04/<folder_ts>/FD/<Nb>_<ts>.txt, parses each
file into bin-level rows, and produces a single long-format parquet at
processed/multidetector_dataset_v1/df_bins.parquet.

Output schema (one row per (measurement_id, bin_idx)):
    measurement_id      str   relative path "<folder_ts>/FD/<filename>"
    source_txt          str   filename only
    folder_ts           str   parent folder timestamp
    nb_of_sample        int   from filename prefix
    bin_idx             int   1..17
    mag_i1_dbm          float
    mag_q1_dbm          float
    mag_i2_dbm          float
    mag_q2_dbm          float
    date                str   YYYY-MM-DD from header
    time                str   HH:MM:SS.mmm from header
    radar_no            str
    interface           str
    start_freq_mhz      int
    stop_freq_mhz       int
    ramp_time_ms        int
    attenuation_db      float
    bin_size_mm         float
    number_of_samples   int
    bin_size_hz         int
    zero_pad_factor     int
    normalization       int
    active_channels     str
    magnitude_unit      str

Sidecar ingest_log.json with counts and any parse errors.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Iterator

import pandas as pd

DEFAULT_RAW = Path("data/multidetektor/meranie_23_04")
DEFAULT_OUT = Path("processed/multidetector_dataset_v1/df_bins.parquet")
DEFAULT_LOG = Path("processed/multidetector_dataset_v1/ingest_log.json")

EXCLUDE_NB = {90}  # per finalized plan

SEPARATOR_RE = re.compile(r"^=+\s*$")
HEADER_LINE_RE = re.compile(r"^([^:]+):\s*(.*)$")

EXPECTED_HEADERS = {
    "Date", "Time", "Radar No.", "Interface",
    "Start-Frequency [MHz]", "Stop-Frequency [MHz]",
    "Ramp Time [ms]", "Attenuation [dB]",
    "Bin Size [mm]", "Number of Samples", "Bin Size [Hz]",
    "Zero Pad Factor", "Normalization", "Active Channels",
}


def parse_one_file(path: Path) -> tuple[dict, list[list[float]]]:
    """Return (header_dict, bin_rows) for one .txt frame file."""
    header: dict[str, str] = {}
    bin_rows: list[list[float]] = []
    state = "header"

    with path.open("r", encoding="ascii", errors="replace") as fh:
        for raw_line in fh:
            line = raw_line.rstrip("\r\n")
            if state == "header":
                if SEPARATOR_RE.match(line):
                    state = "channel_header"
                    continue
                m = HEADER_LINE_RE.match(line)
                if not m:
                    continue
                key = m.group(1).strip()
                val = m.group(2).strip()
                # Magnitude Unit line embeds a second key after a comma + tab:
                #   "[dBm], Phase/Obj. Angle Unit:\t[degrees]"
                # We only need the first value; keep verbatim.
                header[key] = val
            elif state == "channel_header":
                if not line.strip():
                    continue
                # Expect "<Mag. I1>\t<Mag. Q1>\t<Mag. I2>\t<Mag. Q2>"
                if "<Mag." not in line:
                    raise ValueError(f"Unexpected channel header in {path}: {line!r}")
                state = "data"
            elif state == "data":
                if not line.strip():
                    continue
                parts = [p for p in line.split() if p]
                if len(parts) != 4:
                    raise ValueError(
                        f"Expected 4 float columns at {path}:{len(bin_rows)+1}, got {len(parts)}: {line!r}"
                    )
                bin_rows.append([float(p) for p in parts])

    return header, bin_rows


def iter_txt_files(root: Path) -> Iterator[Path]:
    for folder in sorted(root.iterdir()):
        if not folder.is_dir():
            continue
        fd = folder / "FD"
        if not fd.is_dir():
            continue
        for txt in sorted(fd.glob("*.txt")):
            yield txt


def header_to_row_meta(header: dict, path: Path, raw_root: Path) -> dict:
    fname = path.name
    folder_ts = path.parent.parent.name
    measurement_id = str(path.relative_to(raw_root))
    nb_str = fname.split("_", 1)[0]
    nb = int(nb_str)

    def gi(key: str) -> int:
        return int(header[key])

    def gf(key: str) -> float:
        return float(header[key])

    meta = {
        "measurement_id": measurement_id,
        "source_txt": fname,
        "folder_ts": folder_ts,
        "nb_of_sample": nb,
        "date": header["Date"],
        "time": header["Time"],
        "radar_no": header["Radar No."],
        "interface": header["Interface"],
        "start_freq_mhz": gi("Start-Frequency [MHz]"),
        "stop_freq_mhz": gi("Stop-Frequency [MHz]"),
        "ramp_time_ms": gi("Ramp Time [ms]"),
        "attenuation_db": gf("Attenuation [dB]"),
        "bin_size_mm": gf("Bin Size [mm]"),
        "number_of_samples": gi("Number of Samples"),
        "bin_size_hz": gi("Bin Size [Hz]"),
        "zero_pad_factor": gi("Zero Pad Factor"),
        "normalization": gi("Normalization"),
        "active_channels": header["Active Channels"],
        "magnitude_unit": header.get("Magnitude Unit", ""),
    }
    return meta


def ingest(
    raw_root: Path,
    out_parquet: Path,
    log_path: Path,
    exclude_nb: set[int],
) -> dict:
    rows: list[dict] = []
    parse_errors: list[dict] = []
    nb_counter: Counter[int] = Counter()
    excluded_counter: Counter[int] = Counter()
    measurement_ids: set[str] = set()
    files_seen = 0

    for txt in iter_txt_files(raw_root):
        files_seen += 1
        try:
            header, bin_rows = parse_one_file(txt)
        except Exception as exc:
            parse_errors.append({"path": str(txt), "error": repr(exc)})
            continue

        try:
            meta = header_to_row_meta(header, txt, raw_root)
        except Exception as exc:
            parse_errors.append({"path": str(txt), "error": f"meta: {exc!r}"})
            continue

        nb = meta["nb_of_sample"]
        if nb in exclude_nb:
            excluded_counter[nb] += 1
            continue

        n_samples = meta["number_of_samples"]
        if len(bin_rows) != n_samples:
            parse_errors.append({
                "path": str(txt),
                "error": f"bin count mismatch: header={n_samples} parsed={len(bin_rows)}",
            })
            continue

        nb_counter[nb] += 1
        measurement_ids.add(meta["measurement_id"])

        for bin_idx, (i1, q1, i2, q2) in enumerate(bin_rows, start=1):
            row = dict(meta)
            row["bin_idx"] = bin_idx
            row["mag_i1_dbm"] = i1
            row["mag_q1_dbm"] = q1
            row["mag_i2_dbm"] = i2
            row["mag_q2_dbm"] = q2
            rows.append(row)

    df = pd.DataFrame(rows)
    column_order = [
        "measurement_id", "source_txt", "folder_ts", "nb_of_sample",
        "bin_idx", "mag_i1_dbm", "mag_q1_dbm", "mag_i2_dbm", "mag_q2_dbm",
        "date", "time",
        "radar_no", "interface",
        "start_freq_mhz", "stop_freq_mhz", "ramp_time_ms", "attenuation_db",
        "bin_size_mm", "number_of_samples", "bin_size_hz", "zero_pad_factor",
        "normalization", "active_channels", "magnitude_unit",
    ]
    df = df[column_order]

    out_parquet.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_parquet, index=False)

    summary = {
        "raw_root": str(raw_root),
        "out_parquet": str(out_parquet),
        "files_seen": files_seen,
        "files_included": len(measurement_ids),
        "files_excluded_by_nb": dict(sorted(excluded_counter.items())),
        "excluded_nb_rule": sorted(exclude_nb),
        "parse_errors": parse_errors,
        "rows_total": len(df),
        "rows_per_measurement_unique": int(df.groupby("measurement_id").size().nunique()),
        "rows_per_measurement_value_counts": df.groupby("measurement_id").size().value_counts().to_dict(),
        "frames_per_nb": dict(sorted(nb_counter.items())),
        "bin_idx_range": [int(df["bin_idx"].min()), int(df["bin_idx"].max())],
        "channel_dbm_range": {
            "i1": [float(df["mag_i1_dbm"].min()), float(df["mag_i1_dbm"].max())],
            "q1": [float(df["mag_q1_dbm"].min()), float(df["mag_q1_dbm"].max())],
            "i2": [float(df["mag_i2_dbm"].min()), float(df["mag_i2_dbm"].max())],
            "q2": [float(df["mag_q2_dbm"].min()), float(df["mag_q2_dbm"].max())],
        },
        "unique_categorical": {
            "bin_size_mm": sorted(df["bin_size_mm"].unique().tolist()),
            "ramp_time_ms": sorted(df["ramp_time_ms"].unique().tolist()),
            "number_of_samples": sorted(df["number_of_samples"].unique().tolist()),
            "active_channels": sorted(df["active_channels"].unique().tolist()),
            "radar_no": sorted(df["radar_no"].unique().tolist()),
        },
        "date_range": [df["date"].min(), df["date"].max()],
    }

    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--raw", type=Path, default=DEFAULT_RAW)
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument("--log", type=Path, default=DEFAULT_LOG)
    p.add_argument("--include-nb-90", action="store_true",
                   help="Include Nb=90 (default: excluded per plan)")
    args = p.parse_args()

    exclude = set() if args.include_nb_90 else EXCLUDE_NB
    summary = ingest(args.raw, args.out, args.log, exclude_nb=exclude)

    print(f"[OK] wrote {summary['rows_total']} rows × {len(summary['unique_categorical'])} cat dims")
    print(f"[OK] {summary['files_included']} measurements, {len(summary['frames_per_nb'])} unique Nb")
    print(f"[OK] parquet: {args.out}")
    print(f"[OK] log:     {args.log}")
    if summary["parse_errors"]:
        print(f"[WARN] {len(summary['parse_errors'])} parse errors — see log")
        sys.exit(1)


if __name__ == "__main__":
    main()
