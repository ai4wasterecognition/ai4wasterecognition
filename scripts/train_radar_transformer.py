#!/usr/bin/env python3
"""Train a compact transformer baseline on exported radar tensors."""

from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch.utils.data import DataLoader, Dataset
except ImportError:
    torch = None
    nn = None
    F = None
    DataLoader = None
    Dataset = object


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    return parser.parse_args()


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    if torch is not None:
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)


def ensure_runtime() -> None:
    if torch is None or nn is None or F is None or DataLoader is None:
        raise SystemExit(
            "PyTorch is not installed in this environment. "
            "Install it from https://pytorch.org/get-started/locally/ and rerun the script."
        )


def compute_channel_stats(signal: np.ndarray, valid_mask: np.ndarray, train_mask: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    stats_signal = signal[train_mask]
    stats_mask = valid_mask[train_mask]

    means = []
    stds = []
    for channel_idx in range(signal.shape[-1]):
        values = stats_signal[:, :, channel_idx][stats_mask]
        mean = float(values.mean()) if len(values) else 0.0
        std = float(values.std()) if len(values) else 1.0
        if std == 0:
            std = 1.0
        means.append(mean)
        stds.append(std)
    return np.array(means, dtype=np.float32), np.array(stds, dtype=np.float32)


def normalize_signal(signal: np.ndarray, valid_mask: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    normalized = signal.copy()
    normalized = (normalized - mean.reshape(1, 1, -1)) / std.reshape(1, 1, -1)
    normalized[~valid_mask] = 0.0
    return normalized


def encode_labels(labels: pd.Series) -> tuple[np.ndarray, dict[str, int]]:
    classes = sorted(label for label in labels.dropna().astype(str).unique().tolist())
    vocab = {label: idx for idx, label in enumerate(classes)}
    encoded = labels.astype(str).map(vocab).to_numpy(dtype=np.int64)
    return encoded, vocab


def compute_class_weights(targets: np.ndarray, num_classes: int) -> np.ndarray:
    counts = np.bincount(targets, minlength=num_classes).astype(np.float32)
    counts[counts == 0] = 1.0
    weights = counts.sum() / (num_classes * counts)
    return weights.astype(np.float32)


def accuracy_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float((y_true == y_pred).mean())


def macro_f1_score(y_true: np.ndarray, y_pred: np.ndarray, num_classes: int) -> float:
    f1_scores = []
    for class_idx in range(num_classes):
        tp = np.logical_and(y_true == class_idx, y_pred == class_idx).sum()
        fp = np.logical_and(y_true != class_idx, y_pred == class_idx).sum()
        fn = np.logical_and(y_true == class_idx, y_pred != class_idx).sum()
        if tp == 0 and fp == 0 and fn == 0:
            continue
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 0.0 if (precision + recall) == 0 else 2 * precision * recall / (precision + recall)
        f1_scores.append(f1)
    return float(np.mean(f1_scores)) if f1_scores else 0.0


@dataclass
class SplitData:
    signal: np.ndarray
    valid_mask: np.ndarray
    targets: np.ndarray
    measurement_id: np.ndarray


class RadarTensorDataset(Dataset):
    def __init__(self, split_data: SplitData):
        self.signal = torch.from_numpy(split_data.signal)
        self.valid_mask = torch.from_numpy(split_data.valid_mask)
        self.targets = torch.from_numpy(split_data.targets)
        self.measurement_id = split_data.measurement_id

    def __len__(self) -> int:
        return len(self.targets)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        return {
            "signal": self.signal[idx],
            "valid_mask": self.valid_mask[idx],
            "target": self.targets[idx],
            "measurement_id": self.measurement_id[idx],
        }


if nn is not None:

    class RadarTransformerClassifier(nn.Module):
        def __init__(
            self,
            input_channels: int,
            max_seq_len: int,
            num_classes: int,
            d_model: int = 128,
            nhead: int = 4,
            num_layers: int = 4,
            dim_feedforward: int = 256,
            dropout: float = 0.1,
            patch_len: int = 1,
            patch_stride: int = 1,
            pooling: str = "cls",
        ) -> None:
            super().__init__()
            self.patch_len = patch_len
            self.patch_stride = patch_stride
            self.pooling = pooling
            self.max_tokens = self._compute_token_count(max_seq_len)

            if patch_len > 1:
                self.patch_embed = nn.Conv1d(
                    in_channels=input_channels,
                    out_channels=d_model,
                    kernel_size=patch_len,
                    stride=patch_stride,
                )
                self.input_proj = None
            else:
                self.patch_embed = None
                self.input_proj = nn.Linear(input_channels, d_model)

            self.cls_token = nn.Parameter(torch.zeros(1, 1, d_model))
            self.pos_embed = nn.Parameter(torch.zeros(1, self.max_tokens + 1, d_model))

            encoder_layer = nn.TransformerEncoderLayer(
                d_model=d_model,
                nhead=nhead,
                dim_feedforward=dim_feedforward,
                dropout=dropout,
                batch_first=True,
                norm_first=True,
            )
            self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
            self.norm = nn.LayerNorm(d_model)
            self.head = nn.Linear(d_model, num_classes)

            nn.init.normal_(self.cls_token, std=0.02)
            nn.init.normal_(self.pos_embed, std=0.02)

        def _compute_token_count(self, max_seq_len: int) -> int:
            if self.patch_len <= 1:
                return max_seq_len
            return ((max_seq_len - self.patch_len) // self.patch_stride) + 1

        def _tokenize(self, signal: torch.Tensor, valid_mask: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
            if self.patch_embed is not None:
                tokens = self.patch_embed(signal.transpose(1, 2)).transpose(1, 2)
                token_mask = F.max_pool1d(
                    valid_mask.float().unsqueeze(1),
                    kernel_size=self.patch_len,
                    stride=self.patch_stride,
                ).squeeze(1) > 0
            else:
                tokens = self.input_proj(signal)
                token_mask = valid_mask
            return tokens, token_mask

        def forward(self, signal: torch.Tensor, valid_mask: torch.Tensor) -> torch.Tensor:
            tokens, token_mask = self._tokenize(signal, valid_mask)
            batch_size = tokens.size(0)

            cls_tokens = self.cls_token.expand(batch_size, -1, -1)
            tokens = torch.cat([cls_tokens, tokens], dim=1)

            cls_mask = torch.ones((batch_size, 1), dtype=torch.bool, device=signal.device)
            token_mask = torch.cat([cls_mask, token_mask], dim=1)

            pos = self.pos_embed[:, : tokens.size(1), :]
            encoded = self.encoder(tokens + pos, src_key_padding_mask=~token_mask)
            encoded = self.norm(encoded)

            if self.pooling == "mean":
                masked = encoded[:, 1:, :] * token_mask[:, 1:].unsqueeze(-1)
                pooled = masked.sum(dim=1) / token_mask[:, 1:].sum(dim=1, keepdim=True).clamp_min(1)
            else:
                pooled = encoded[:, 0, :]

            return self.head(pooled)


else:
    RadarTransformerClassifier = None


def load_exported_dataset(dataset_dir: Path, task: str) -> tuple[SplitData, SplitData, SplitData, dict[str, Any]]:
    tensor = np.load(dataset_dir / "measurement_tensor.npz")
    signal = tensor["signal"].astype(np.float32)
    valid_mask = tensor["valid_mask"].astype(bool)
    measurement_ids = tensor["measurement_id"].astype(str)

    labels = pd.read_parquet(dataset_dir / "measurement_labels.parquet")
    splits = pd.read_parquet(dataset_dir / "splits.parquet")
    merged = labels.merge(splits[["measurement_id", "split"]], on="measurement_id", how="inner")

    id_to_row = {measurement_id: idx for idx, measurement_id in enumerate(measurement_ids.tolist())}
    merged = merged[merged["measurement_id"].isin(id_to_row)].copy()

    if task == "biomass_binary":
        merged = merged[merged["has_biomass"].notna()].copy()
        merged["target_label"] = merged["has_biomass"].astype(bool).map({False: "no_biomass", True: "biomass"})
    elif task == "material_primary":
        merged = merged[merged["material_primary"].notna()].copy()
        merged["target_label"] = merged["material_primary"].astype(str)
    elif task == "material_fine":
        merged = merged[merged["material_name_auto"].notna()].copy()
        merged["target_label"] = merged["material_name_auto"].astype(str)
    else:
        raise ValueError(f"Unsupported task: {task}")

    ordered_ids = merged["measurement_id"].tolist()
    row_index = np.array([id_to_row[mid] for mid in ordered_ids], dtype=np.int64)
    signal = signal[row_index]
    valid_mask = valid_mask[row_index]

    targets, label_vocab = encode_labels(merged["target_label"])
    split_values = merged["split"].astype(str).to_numpy()
    measurement_ids = np.array(ordered_ids, dtype="U32")

    train_mask = split_values == "train"
    mean, std = compute_channel_stats(signal=signal, valid_mask=valid_mask, train_mask=train_mask)
    signal = normalize_signal(signal=signal, valid_mask=valid_mask, mean=mean, std=std)

    def make_split(split_name: str) -> SplitData:
        mask = split_values == split_name
        return SplitData(
            signal=signal[mask],
            valid_mask=valid_mask[mask],
            targets=targets[mask],
            measurement_id=measurement_ids[mask],
        )

    artifacts = {
        "label_vocab": label_vocab,
        "normalization": {"mean": mean.tolist(), "std": std.tolist()},
        "channel_names": tensor["channel_names"].astype(str).tolist(),
        "max_seq_len": int(signal.shape[1]),
        "task": task,
    }
    return make_split("train"), make_split("val"), make_split("test"), artifacts


def create_loader(split_data: SplitData, batch_size: int, num_workers: int, shuffle: bool) -> DataLoader:
    dataset = RadarTensorDataset(split_data)
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers)


def evaluate(
    model: nn.Module,
    loader: DataLoader,
    device: torch.device,
    criterion: nn.Module,
    num_classes: int,
) -> dict[str, float]:
    model.eval()
    losses = []
    all_targets = []
    all_preds = []
    with torch.no_grad():
        for batch in loader:
            signal = batch["signal"].to(device)
            valid_mask = batch["valid_mask"].to(device)
            targets = batch["target"].to(device)

            logits = model(signal, valid_mask)
            loss = criterion(logits, targets)
            losses.append(float(loss.item()))

            preds = logits.argmax(dim=1).cpu().numpy()
            all_preds.append(preds)
            all_targets.append(targets.cpu().numpy())

    y_true = np.concatenate(all_targets) if all_targets else np.array([], dtype=np.int64)
    y_pred = np.concatenate(all_preds) if all_preds else np.array([], dtype=np.int64)

    return {
        "loss": float(np.mean(losses)) if losses else math.nan,
        "accuracy": accuracy_score(y_true, y_pred) if len(y_true) else math.nan,
        "macro_f1": macro_f1_score(y_true, y_pred, num_classes=num_classes) if len(y_true) else math.nan,
    }


def train_model(config: dict[str, Any]) -> dict[str, Any]:
    ensure_runtime()
    set_seed(int(config.get("seed", 42)))

    dataset_dir = Path(config["dataset_dir"])
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    train_split, val_split, test_split, artifacts = load_exported_dataset(
        dataset_dir=dataset_dir,
        task=config["task"],
    )
    label_vocab = artifacts["label_vocab"]
    num_classes = len(label_vocab)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model_cfg = config["model"]
    model = RadarTransformerClassifier(
        input_channels=len(artifacts["channel_names"]),
        max_seq_len=int(artifacts["max_seq_len"]),
        num_classes=num_classes,
        d_model=int(model_cfg["d_model"]),
        nhead=int(model_cfg["nhead"]),
        num_layers=int(model_cfg["num_layers"]),
        dim_feedforward=int(model_cfg["dim_feedforward"]),
        dropout=float(model_cfg["dropout"]),
        patch_len=int(model_cfg.get("patch_len", 1)),
        patch_stride=int(model_cfg.get("patch_stride", 1)),
        pooling=str(model_cfg.get("pooling", "cls")),
    ).to(device)

    train_cfg = config["training"]
    train_loader = create_loader(
        train_split,
        batch_size=int(train_cfg["batch_size"]),
        num_workers=int(train_cfg.get("num_workers", 0)),
        shuffle=True,
    )
    val_loader = create_loader(
        val_split,
        batch_size=int(train_cfg["batch_size"]),
        num_workers=int(train_cfg.get("num_workers", 0)),
        shuffle=False,
    )
    test_loader = create_loader(
        test_split,
        batch_size=int(train_cfg["batch_size"]),
        num_workers=int(train_cfg.get("num_workers", 0)),
        shuffle=False,
    )

    class_weights = compute_class_weights(train_split.targets, num_classes)
    criterion = nn.CrossEntropyLoss(weight=torch.tensor(class_weights, dtype=torch.float32, device=device))
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=float(train_cfg["learning_rate"]),
        weight_decay=float(train_cfg["weight_decay"]),
    )

    best_val_f1 = -float("inf")
    best_state = None
    patience = int(train_cfg["patience"])
    epochs = int(train_cfg["epochs"])
    epochs_without_improvement = 0
    history = []

    for epoch in range(1, epochs + 1):
        model.train()
        epoch_losses = []
        for batch in train_loader:
            signal = batch["signal"].to(device)
            valid_mask = batch["valid_mask"].to(device)
            targets = batch["target"].to(device)

            optimizer.zero_grad(set_to_none=True)
            logits = model(signal, valid_mask)
            loss = criterion(logits, targets)
            loss.backward()
            optimizer.step()
            epoch_losses.append(float(loss.item()))

        train_metrics = evaluate(model, train_loader, device, criterion, num_classes)
        val_metrics = evaluate(model, val_loader, device, criterion, num_classes)
        row = {
            "epoch": epoch,
            "train_loss": float(np.mean(epoch_losses)) if epoch_losses else math.nan,
            "train_accuracy": train_metrics["accuracy"],
            "train_macro_f1": train_metrics["macro_f1"],
            "val_loss": val_metrics["loss"],
            "val_accuracy": val_metrics["accuracy"],
            "val_macro_f1": val_metrics["macro_f1"],
        }
        history.append(row)

        if val_metrics["macro_f1"] > best_val_f1:
            best_val_f1 = val_metrics["macro_f1"]
            best_state = {k: v.detach().cpu() for k, v in model.state_dict().items()}
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement >= patience:
                break

    if best_state is None:
        raise RuntimeError("Training finished without producing a checkpoint.")

    model.load_state_dict(best_state)
    test_metrics = evaluate(model, test_loader, device, criterion, num_classes)

    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "config": config,
            "label_vocab": label_vocab,
            "normalization": artifacts["normalization"],
            "channel_names": artifacts["channel_names"],
        },
        output_dir / "best.pt",
    )

    with (output_dir / "history.json").open("w", encoding="utf-8") as handle:
        json.dump(history, handle, indent=2, ensure_ascii=True)
    with (output_dir / "artifacts.json").open("w", encoding="utf-8") as handle:
        json.dump(
            {
                "label_vocab": label_vocab,
                "normalization": artifacts["normalization"],
                "channel_names": artifacts["channel_names"],
                "task": artifacts["task"],
                "max_seq_len": artifacts["max_seq_len"],
                "test_metrics": test_metrics,
                "device": str(device),
            },
            handle,
            indent=2,
            ensure_ascii=True,
        )

    return {
        "history": history,
        "test_metrics": test_metrics,
    }


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    train_model(config)


if __name__ == "__main__":
    main()
