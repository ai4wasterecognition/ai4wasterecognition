#!/usr/bin/env python3
"""Run inference on raw radar .txt frames using a trained radar (multidetector-measurement) model.

Usage:
    # single file
    python infer.py --model models/radar_dataset_from_multidetektor_measurement/transformer_..._label_category.pt \
                    --input data/multidetektor/meranie_23_04/<folder>/FD/10_*.txt

    # batch (folder, recursive .txt)
    python infer.py --model <model.{pt,joblib}> --input <folder> --out predictions.csv

For sklearn models (.joblib) and torch models (.pt) the loader is auto-detected.
Output JSON to stdout for single files, CSV with --out for batches.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

HEADER_LINE_RE = re.compile(r"^([^:]+):\s*(.*)$")
SEPARATOR_RE = re.compile(r"^=+\s*$")

EXPECTED = {
    "Bin Size [mm]": 320.604,
    "Number of Samples": 17,
    "Ramp Time [ms]": 50,
    "Active Channels": "I1, Q1, I2, Q2",
}


def parse_txt(path: Path) -> tuple[dict, np.ndarray]:
    header: dict[str, str] = {}
    bins: list[list[float]] = []
    state = "header"
    with path.open("r", encoding="ascii", errors="replace") as fh:
        for line in fh:
            line = line.rstrip("\r\n")
            if state == "header":
                if SEPARATOR_RE.match(line):
                    state = "channel_header"
                    continue
                m = HEADER_LINE_RE.match(line)
                if m:
                    header[m.group(1).strip()] = m.group(2).strip()
            elif state == "channel_header":
                if line.strip():
                    state = "data"
            elif state == "data":
                if not line.strip():
                    continue
                parts = [p for p in line.split() if p]
                if len(parts) != 4:
                    raise ValueError(f"Expected 4 floats, got {parts!r} in {path}")
                bins.append([float(p) for p in parts])
    arr = np.array(bins, dtype=np.float32).T  # → (4, 17)
    return header, arr


def validate_header(header: dict, path: Path) -> list[str]:
    warnings = []
    for k, expected in EXPECTED.items():
        if k not in header:
            warnings.append(f"{path.name}: missing header '{k}'")
            continue
        v = header[k]
        try:
            if isinstance(expected, (int, float)):
                if abs(float(v) - float(expected)) > 1e-3:
                    warnings.append(f"{path.name}: {k}={v} (expected {expected})")
            else:
                if str(v).strip() != str(expected).strip():
                    warnings.append(f"{path.name}: {k}={v!r} (expected {expected!r})")
        except ValueError:
            warnings.append(f"{path.name}: {k}={v!r} unparsable")
    return warnings


def load_model(path: Path):
    if path.suffix == ".joblib":
        import joblib
        bundle = joblib.load(path)
        return "sklearn", bundle
    elif path.suffix == ".pt":
        import torch
        ckpt = torch.load(path, map_location="cpu", weights_only=False)
        return "torch", ckpt
    else:
        raise ValueError(f"Unknown model file type: {path.suffix}")


def sklearn_predict(bundle: dict, X: np.ndarray) -> tuple[list[str], list[list[float]]]:
    """X: (N, 4, 17). Return (label list, prob list)."""
    feat = bundle["feat"]
    if feat == "hc":
        from train_classifier import handcrafted_features as hc
        F = hc(X)
    elif feat == "flat":
        F = X.reshape(X.shape[0], -1)
    else:
        from train_classifier import handcrafted_features as hc
        F = np.concatenate([hc(X), X.reshape(X.shape[0], -1)], axis=1)
    model = bundle["model"]
    probs = model.predict_proba(F).tolist()
    labels = model.predict(F).tolist()
    return labels, probs


def torch_predict(ckpt: dict, X: np.ndarray) -> tuple[list[str], list[list[float]]]:
    import torch
    from torch import nn

    cfg = ckpt["config"]
    classes = ckpt["classes"]
    norm = ckpt["normalization"]
    mean = np.array(norm["mean"], dtype=np.float32)
    std = np.array(norm["std"], dtype=np.float32)

    in_ch, n_bins = ckpt["input_shape"]

    class CompactEncoder(nn.Module):
        def __init__(self):
            super().__init__()
            self.embed = nn.Conv1d(in_ch, cfg["d_model"], kernel_size=1)
            self.pos = nn.Parameter(torch.zeros(1, n_bins, cfg["d_model"]))
            enc_layer = nn.TransformerEncoderLayer(
                d_model=cfg["d_model"],
                nhead=cfg["heads"],
                dim_feedforward=cfg["d_model"] * cfg["mlp_ratio"],
                dropout=cfg["dropout"],
                activation="gelu",
                batch_first=True,
                norm_first=True,
            )
            self.encoder = nn.TransformerEncoder(enc_layer, num_layers=cfg["depth"])
            self.norm = nn.LayerNorm(cfg["d_model"])
            self.head = nn.Linear(cfg["d_model"], len(classes))

        def forward(self, x):
            z = self.embed(x).transpose(1, 2) + self.pos
            z = self.encoder(z)
            z = self.norm(z).mean(dim=1)
            return self.head(z)

    model = CompactEncoder()
    model.load_state_dict(ckpt["state_dict"])
    model.eval()

    Xn = (X - mean) / std
    with torch.no_grad():
        logits = model(torch.from_numpy(Xn).float())
        probs = torch.softmax(logits, dim=1).numpy()
        preds = probs.argmax(axis=1)
    return [classes[i] for i in preds], probs.tolist()


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", type=Path, required=True)
    p.add_argument("--input", type=Path, required=True, help="single .txt or folder")
    p.add_argument("--out", type=Path, default=None, help="CSV output (folder mode)")
    p.add_argument("--top-k", type=int, default=3)
    args = p.parse_args()

    # ensure local import works
    sys.path.insert(0, str(Path(__file__).resolve().parent))

    kind, model_obj = load_model(args.model)

    if args.input.is_file():
        files = [args.input]
    else:
        files = sorted(args.input.rglob("*.txt"))
        if not files:
            raise SystemExit(f"No .txt files in {args.input}")

    frames = []
    headers = []
    all_warnings = []
    for f in files:
        header, arr = parse_txt(f)
        warns = validate_header(header, f)
        all_warnings.extend(warns)
        if arr.shape != (4, 17):
            raise ValueError(f"{f.name}: expected (4,17), got {arr.shape}")
        frames.append(arr)
        headers.append(header)
    X = np.stack(frames)  # (N, 4, 17)

    if kind == "sklearn":
        labels, probs = sklearn_predict(model_obj, X)
        classes = model_obj["classes"]
    else:
        labels, probs = torch_predict(model_obj, X)
        classes = model_obj["classes"]

    results = []
    for f, pred, prob, header in zip(files, labels, probs, headers):
        idx = sorted(range(len(prob)), key=lambda i: prob[i], reverse=True)[: args.top_k]
        results.append({
            "filename": f.name,
            "path": str(f),
            "date": header.get("Date"),
            "time": header.get("Time"),
            "predicted_label": pred,
            "confidence": round(float(max(prob)), 6),
            "top_k": [{"label": classes[i], "prob": round(float(prob[i]), 6)} for i in idx],
        })

    if all_warnings:
        for w in all_warnings:
            print(f"[WARN] {w}", file=sys.stderr)

    if args.out:
        import csv
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("w", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["filename", "date", "time", "predicted_label", "confidence"])
            for r in results:
                writer.writerow([r["filename"], r["date"], r["time"], r["predicted_label"], r["confidence"]])
        print(f"[OK] {len(results)} predictions -> {args.out}", file=sys.stderr)
    else:
        for r in results:
            print(json.dumps(r, ensure_ascii=False))


if __name__ == "__main__":
    main()
