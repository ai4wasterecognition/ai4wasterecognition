#!/usr/bin/env python3
"""Train a classifier on multidetector_dataset_v1.

Two model families:
  --model baseline      logistic-regression / random-forest on handcrafted +
                        flattened features (sklearn)
  --model transformer   compact encoder-only transformer on (4, 17) tensors (torch)

Three target labels:
  --target label_category              (6 classes, default)
  --target label_name                  (17 classes)
  --target label_contamination_present (binary)

Reads release/multidetector_dataset_v1/.
Writes models to models/multidetector_dataset_v1/<run_name>.{joblib|pt} and a metrics JSON.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

RELEASE = Path("release/multidetector_dataset_v1")
MODELS_DIR = Path("models/multidetector_dataset_v1")


@dataclass
class Dataset:
    X: np.ndarray              # (N, 4, 17) float32
    y_str: np.ndarray          # (N,) target labels as strings
    measurement_ids: np.ndarray
    splits: np.ndarray         # (N,) "train"/"val"/"test"
    target_name: str
    classes: list[str]


def load_dataset(release_dir: Path, target: str) -> Dataset:
    npz = np.load(release_dir / "measurement_tensor.npz", allow_pickle=True)
    X = npz["X"]
    ids = np.array([str(s) for s in npz["measurement_ids"]])

    labels = pd.read_parquet(release_dir / "measurement_labels.parquet")
    splits = pd.read_parquet(release_dir / "splits.parquet")[["measurement_id", "split"]]
    if target not in labels.columns:
        raise ValueError(f"Unknown target {target!r}; available: {[c for c in labels.columns if c.startswith('label_')]}")

    df = pd.DataFrame({"measurement_id": ids}).merge(labels, on="measurement_id").merge(splits, on="measurement_id")
    # Reorder X according to df row order (df is already in ids order since labels is sorted by id)
    id_to_idx = {mid: i for i, mid in enumerate(ids)}
    order = df["measurement_id"].map(id_to_idx).to_numpy()
    X = X[order]
    df = df.reset_index(drop=True)

    y_str = df[target].astype(str).to_numpy()
    classes = sorted(np.unique(y_str).tolist())
    return Dataset(
        X=X,
        y_str=y_str,
        measurement_ids=df["measurement_id"].to_numpy(),
        splits=df["split"].to_numpy(),
        target_name=target,
        classes=classes,
    )


# ─────────────────────────────────────── Featurization (baseline) ────────────


def handcrafted_features(X: np.ndarray, target_bins=(7, 8)) -> np.ndarray:
    """For each frame (4, 17) compute per-channel: mean, std, max, argmax,
    target-bin mean (bin 7+8), background mean (bin 1, 16, 17), delta(target-bg),
    snr_db = target_mean - background_mean. Plus cross-channel: I1-I2, Q1-Q2.
    Returns (N, F).
    """
    N, C, B = X.shape
    target_idx = np.array([b - 1 for b in target_bins], dtype=int)
    bg_idx = np.array([0, B - 2, B - 1], dtype=int)  # bin 1, 16, 17 for B=17

    means = X.mean(axis=2)
    stds = X.std(axis=2)
    maxs = X.max(axis=2)
    argmax = X.argmax(axis=2).astype(np.float32)
    tgt_mean = X[:, :, target_idx].mean(axis=2)
    bg_mean = X[:, :, bg_idx].mean(axis=2)
    delta = tgt_mean - bg_mean
    snr_db = delta  # in dBm; delta IS the SNR-like proxy

    cross = np.stack([X[:, 0, :].mean(axis=1) - X[:, 2, :].mean(axis=1),
                      X[:, 1, :].mean(axis=1) - X[:, 3, :].mean(axis=1)], axis=1)

    feats = np.concatenate([means, stds, maxs, argmax, tgt_mean, bg_mean, delta, snr_db, cross], axis=1)
    return feats.astype(np.float32)


def flat_features(X: np.ndarray) -> np.ndarray:
    return X.reshape(X.shape[0], -1).astype(np.float32)


# ─────────────────────────────────────── Baseline trainer ────────────────────


def train_baseline(ds: Dataset, *, algo: Literal["logreg", "rf"], feat: Literal["hc", "flat", "both"], out_path: Path) -> dict:
    train_mask = ds.splits == "train"
    val_mask = ds.splits == "val"
    test_mask = ds.splits == "test"

    if feat == "hc":
        F = handcrafted_features(ds.X)
    elif feat == "flat":
        F = flat_features(ds.X)
    else:
        F = np.concatenate([handcrafted_features(ds.X), flat_features(ds.X)], axis=1)

    Xtr, ytr = F[train_mask], ds.y_str[train_mask]
    Xv, yv = F[val_mask], ds.y_str[val_mask]
    Xte, yte = F[test_mask], ds.y_str[test_mask]

    if algo == "logreg":
        model = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=2000, class_weight="balanced", n_jobs=-1)),
        ])
    elif algo == "rf":
        model = Pipeline([
            ("clf", RandomForestClassifier(n_estimators=300, class_weight="balanced", n_jobs=-1, random_state=42)),
        ])
    else:
        raise ValueError(algo)

    model.fit(Xtr, ytr)
    yv_hat = model.predict(Xv)
    yte_hat = model.predict(Xte)

    metrics = {
        "algo": algo,
        "feat": feat,
        "target": ds.target_name,
        "n_train": int(train_mask.sum()),
        "n_val": int(val_mask.sum()),
        "n_test": int(test_mask.sum()),
        "val_accuracy": float(accuracy_score(yv, yv_hat)),
        "val_macro_f1": float(f1_score(yv, yv_hat, average="macro")),
        "test_accuracy": float(accuracy_score(yte, yte_hat)),
        "test_macro_f1": float(f1_score(yte, yte_hat, average="macro")),
        "test_per_class_report": classification_report(yte, yte_hat, output_dict=True, zero_division=0),
        "test_confusion_matrix": {
            "labels": ds.classes,
            "matrix": confusion_matrix(yte, yte_hat, labels=ds.classes).tolist(),
        },
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    bundle = {
        "model": model,
        "classes": ds.classes,
        "target": ds.target_name,
        "feat": feat,
        "algo": algo,
        "input_shape": list(ds.X.shape[1:]),
    }
    joblib.dump(bundle, out_path)
    return metrics


# ─────────────────────────────────────── Transformer trainer ─────────────────


def train_transformer(
    ds: Dataset,
    *,
    out_path: Path,
    d_model: int = 64,
    depth: int = 4,
    heads: int = 4,
    mlp_ratio: int = 2,
    dropout: float = 0.1,
    epochs: int = 30,
    batch_size: int = 64,
    lr: float = 3e-4,
    weight_decay: float = 1e-4,
    noise_db: float = 0.5,
    channel_mask_p: float = 0.2,
    seed: int = 42,
) -> dict:
    import torch
    from torch import nn
    from torch.utils.data import DataLoader, TensorDataset

    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Encode labels
    class_to_idx = {c: i for i, c in enumerate(ds.classes)}
    y = np.array([class_to_idx[c] for c in ds.y_str], dtype=np.int64)
    train_mask = ds.splits == "train"
    val_mask = ds.splits == "val"
    test_mask = ds.splits == "test"

    # Per-frame standardisation (using train mean/std per channel)
    X = ds.X.copy()
    train_mean = X[train_mask].mean(axis=(0, 2), keepdims=True)
    train_std = X[train_mask].std(axis=(0, 2), keepdims=True) + 1e-6
    Xn = (X - train_mean) / train_std

    def loader(mask, shuffle):
        ds_ = TensorDataset(torch.from_numpy(Xn[mask]).float(), torch.from_numpy(y[mask]))
        return DataLoader(ds_, batch_size=batch_size, shuffle=shuffle, num_workers=0)

    train_loader = loader(train_mask, True)
    val_loader = loader(val_mask, False)
    test_loader = loader(test_mask, False)

    class CompactEncoder(nn.Module):
        def __init__(self, in_ch: int, n_bins: int, n_classes: int):
            super().__init__()
            self.embed = nn.Conv1d(in_ch, d_model, kernel_size=1)
            self.pos = nn.Parameter(torch.zeros(1, n_bins, d_model))
            nn.init.trunc_normal_(self.pos, std=0.02)
            enc_layer = nn.TransformerEncoderLayer(
                d_model=d_model,
                nhead=heads,
                dim_feedforward=d_model * mlp_ratio,
                dropout=dropout,
                activation="gelu",
                batch_first=True,
                norm_first=True,
            )
            self.encoder = nn.TransformerEncoder(enc_layer, num_layers=depth)
            self.norm = nn.LayerNorm(d_model)
            self.head = nn.Linear(d_model, n_classes)

        def forward(self, x):
            # x: (B, C, T) → (B, T, d_model)
            z = self.embed(x).transpose(1, 2) + self.pos
            z = self.encoder(z)
            z = self.norm(z).mean(dim=1)
            return self.head(z)

    n_ch, n_bins = ds.X.shape[1], ds.X.shape[2]
    model = CompactEncoder(n_ch, n_bins, len(ds.classes)).to(device)

    # class weights for imbalance
    cls_counts = np.bincount(y[train_mask], minlength=len(ds.classes)).astype(np.float32)
    cls_weights = (cls_counts.sum() / (len(ds.classes) * np.maximum(cls_counts, 1))).astype(np.float32)
    class_weight = torch.from_numpy(cls_weights).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weight)
    optim = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(optim, T_max=epochs)

    def aug(batch_x):
        # gaussian noise σ in standardised units (≈ noise_db / train_std_avg)
        noise = torch.randn_like(batch_x) * (noise_db / 5.0)  # rough scaling
        batch_x = batch_x + noise
        if channel_mask_p > 0:
            for i in range(batch_x.shape[0]):
                if rng.random() < channel_mask_p:
                    c = rng.integers(0, n_ch)
                    batch_x[i, c, :] = 0.0
        return batch_x

    def evaluate(loader_):
        model.eval()
        preds, gts = [], []
        with torch.no_grad():
            for xb, yb in loader_:
                xb = xb.to(device)
                pred = model(xb).argmax(dim=1).cpu().numpy()
                preds.append(pred)
                gts.append(yb.numpy())
        return np.concatenate(gts), np.concatenate(preds)

    best_val_f1 = -1.0
    best_state = None
    history = []
    for epoch in range(1, epochs + 1):
        model.train()
        total = 0.0
        n = 0
        for xb, yb in train_loader:
            xb, yb = xb.to(device), yb.to(device)
            xb = aug(xb)
            optim.zero_grad()
            logits = model(xb)
            loss = criterion(logits, yb)
            loss.backward()
            optim.step()
            total += float(loss.item()) * xb.size(0)
            n += xb.size(0)
        sched.step()

        val_y, val_pred = evaluate(val_loader)
        val_acc = accuracy_score(val_y, val_pred)
        val_f1 = f1_score(val_y, val_pred, average="macro")
        history.append({"epoch": epoch, "train_loss": total / n, "val_acc": val_acc, "val_macro_f1": val_f1})
        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
        print(f"  epoch {epoch:3d}  loss={total/n:.4f}  val_acc={val_acc:.3f}  val_f1={val_f1:.3f}")

    assert best_state is not None
    model.load_state_dict(best_state)
    test_y, test_pred = evaluate(test_loader)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({
        "state_dict": best_state,
        "classes": ds.classes,
        "target": ds.target_name,
        "input_shape": list(ds.X.shape[1:]),
        "normalization": {"mean": train_mean.tolist(), "std": train_std.tolist()},
        "config": {
            "d_model": d_model, "depth": depth, "heads": heads,
            "mlp_ratio": mlp_ratio, "dropout": dropout,
        },
    }, out_path)

    return {
        "algo": "transformer",
        "target": ds.target_name,
        "epochs": epochs,
        "best_val_macro_f1": float(best_val_f1),
        "test_accuracy": float(accuracy_score(test_y, test_pred)),
        "test_macro_f1": float(f1_score(test_y, test_pred, average="macro")),
        "test_per_class_report": classification_report(
            [ds.classes[i] for i in test_y],
            [ds.classes[i] for i in test_pred],
            output_dict=True, zero_division=0,
        ),
        "test_confusion_matrix": {
            "labels": ds.classes,
            "matrix": confusion_matrix(test_y, test_pred, labels=range(len(ds.classes))).tolist(),
        },
        "history": history,
    }


# ─────────────────────────────────────── CLI ─────────────────────────────────


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--release", type=Path, default=RELEASE)
    p.add_argument("--target", default="label_category",
                   choices=["label_category", "label_name", "label_contamination_present"])
    p.add_argument("--model", default="baseline", choices=["baseline", "transformer"])
    p.add_argument("--algo", default="logreg", choices=["logreg", "rf"], help="baseline only")
    p.add_argument("--feat", default="both", choices=["hc", "flat", "both"], help="baseline only")
    p.add_argument("--epochs", type=int, default=30)
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--lr", type=float, default=3e-4)
    p.add_argument("--run-name", type=str, default=None)
    p.add_argument("--models-dir", type=Path, default=MODELS_DIR)
    args = p.parse_args()

    ds = load_dataset(args.release, args.target)
    run = args.run_name or f"{args.model}_{args.algo if args.model=='baseline' else 'transformer'}_{args.target}"
    print(f"[run] {run}  | classes={len(ds.classes)}  N={len(ds.y_str)}  splits={np.unique(ds.splits, return_counts=True)}")

    if args.model == "baseline":
        out_path = args.models_dir / f"{run}.joblib"
        metrics = train_baseline(ds, algo=args.algo, feat=args.feat, out_path=out_path)
    else:
        out_path = args.models_dir / f"{run}.pt"
        metrics = train_transformer(ds, out_path=out_path, epochs=args.epochs,
                                    batch_size=args.batch_size, lr=args.lr)

    metrics_path = args.models_dir / f"{run}.metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False))
    print(f"[OK] model:   {out_path}")
    print(f"[OK] metrics: {metrics_path}")
    print(f"     test_acc={metrics.get('test_accuracy'):.3f}  test_macro_f1={metrics.get('test_macro_f1'):.3f}")


if __name__ == "__main__":
    main()
