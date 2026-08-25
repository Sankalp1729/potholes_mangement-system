"""
Train and evaluate the supplied IIT Madras pothole dataset with YOLOv8.

Expected dataset layout:
    <dataset>/
      data.yaml
      train/images + train/labels
      valid/images + valid/labels
      test/images + test/labels

Usage:
    python scripts/train_yolo.py --data /path/to/data.yaml
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "datasets" / "pothole_detection_v2" / "data.yaml"
MODEL_DIR = ROOT / "models" / "pothole_detector"


def validate_dataset(data_yaml: Path) -> dict:
    import yaml

    if not data_yaml.exists():
        raise FileNotFoundError(
            f"data.yaml not found: {data_yaml}\n"
            "Extract the supplied YOLOv8 ZIP and pass its data.yaml with --data."
        )

    config = yaml.safe_load(data_yaml.read_text(encoding="utf-8"))
    names = config.get("names", [])
    if len(names) != 3:
        raise ValueError(f"Expected 3 classes, found {len(names)}: {names}")

    expected = {"crocodile crack", "longitudinal crack", "pothole"}
    if set(map(str, names)) != expected:
        raise ValueError(
            f"Unexpected class names: {names}. Expected: "
            "crocodile crack, longitudinal crack, pothole."
        )

    base = data_yaml.parent
    for key in ("train", "val", "test"):
        value = config.get(key)
        if not value:
            raise ValueError(f"data.yaml is missing '{key}'.")
        path = (base / value).resolve()
        if not path.exists():
            raise FileNotFoundError(f"{key} image directory does not exist: {path}")

        label_dir = path.parent.parent / "labels"
        if not label_dir.exists():
            raise FileNotFoundError(f"Label directory does not exist: {label_dir}")

        images = [
            p for p in path.iterdir()
            if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        ]
        labels = list(label_dir.glob("*.txt"))
        if not images:
            raise ValueError(f"No images found in {path}")
        if len(images) != len(labels):
            raise ValueError(
                f"{key}: image/label count mismatch: "
                f"{len(images)} images vs {len(labels)} labels"
            )

    return config


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--model", default=os.getenv("YOLO_BASE_MODEL", "yolov8m.pt"))
    parser.add_argument("--epochs", type=int, default=int(os.getenv("YOLO_EPOCHS", "150")))
    parser.add_argument("--imgsz", type=int, default=int(os.getenv("YOLO_IMGSZ", "640")))
    parser.add_argument("--batch", type=int, default=int(os.getenv("YOLO_BATCH", "-1")))
    parser.add_argument("--device", default=os.getenv("YOLO_DEVICE", "auto"))
    parser.add_argument("--workers", type=int, default=int(os.getenv("YOLO_WORKERS", "2")))
    args = parser.parse_args()

    data_yaml = args.data.resolve()
    config = validate_dataset(data_yaml)

    from ultralytics import YOLO
    import torch

    device = args.device
    if device == "auto":
        device = 0 if torch.cuda.is_available() else "cpu"

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model = YOLO(args.model)
    model.train(
        data=str(data_yaml),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=device,
        workers=args.workers,
        project=str(MODEL_DIR),
        name="training",
        exist_ok=True,
        pretrained=True,
        optimizer="auto",
        patience=35,
        cos_lr=True,
        close_mosaic=10,
        cache=False,
        seed=42,
        deterministic=True,
        amp=bool(device != "cpu"),
        plots=True,
        verbose=True,
    )

    best = MODEL_DIR / "training" / "weights" / "best.pt"
    if not best.exists():
        raise FileNotFoundError(f"Training finished without {best}")

    stable = MODEL_DIR / "weights" / "best.pt"
    stable.parent.mkdir(parents=True, exist_ok=True)
    stable.write_bytes(best.read_bytes())

    # Evaluate on the untouched test split, not the validation split.
    test_metrics = model.val(
        data=str(data_yaml),
        split="test",
        imgsz=args.imgsz,
        batch=args.batch,
        device=device,
        plots=True,
        verbose=True,
    )

    metrics = {
        "dataset": str(data_yaml),
        "classes": config["names"],
        "base_model": args.model,
        "epochs": args.epochs,
        "imgsz": args.imgsz,
        "device": str(device),
        "best_weights": str(stable),
        "test_mAP50": float(test_metrics.box.map50),
        "test_mAP50_95": float(test_metrics.box.map),
        "test_precision": float(test_metrics.box.mp),
        "test_recall": float(test_metrics.box.mr),
    }

    metrics_path = MODEL_DIR / "test_metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    print(f"\n✅ Model ready: {stable}")


if __name__ == "__main__":
    main()
