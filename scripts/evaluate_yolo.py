"""Evaluate an existing pothole YOLOv8 checkpoint on the held-out test split."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = ROOT / "models" / "pothole_detector" / "weights" / "best.pt"
DEFAULT_DATA = ROOT / "datasets" / "pothole_detection_v2" / "data.yaml"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", default="auto")
    args = parser.parse_args()

    if not args.model.exists():
        raise FileNotFoundError(f"Model not found: {args.model}")
    if not args.data.exists():
        raise FileNotFoundError(f"Dataset YAML not found: {args.data}")

    from ultralytics import YOLO
    import torch

    device = args.device
    if device == "auto":
        device = 0 if torch.cuda.is_available() else "cpu"

    model = YOLO(str(args.model))
    metrics = model.val(
        data=str(args.data),
        split="test",
        imgsz=args.imgsz,
        device=device,
        plots=True,
        verbose=True,
    )

    output = {
        "model": str(args.model),
        "dataset": str(args.data),
        "device": str(device),
        "mAP50": float(metrics.box.map50),
        "mAP50_95": float(metrics.box.map),
        "precision": float(metrics.box.mp),
        "recall": float(metrics.box.mr),
    }

    out_path = args.model.parent.parent / "test_metrics.json"
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
