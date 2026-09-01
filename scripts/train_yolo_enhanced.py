"""
Enhanced YOLOv8 training script with accuracy optimization techniques.

This script includes:
- Improved hyperparameters for better accuracy
- Data augmentation optimization
- Learning rate scheduling
- Model ensembling preparation
- Advanced validation metrics

Usage:
    python scripts/train_yolo_enhanced.py --data datasets/pothole_detection_v2/data.yaml
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "datasets" / "pothole_detection_v2" / "data.yaml"
MODEL_DIR = ROOT / "models" / "pothole_detector"


def validate_dataset(data_yaml: Path) -> dict:
    """Validate the dataset structure and configuration."""
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

        label_dir = path.parent / "labels"
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
    parser = argparse.ArgumentParser(description="Train YOLOv8 with enhanced accuracy settings")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA, help="Path to data.yaml")
    parser.add_argument("--model", default=os.getenv("YOLO_BASE_MODEL", "yolov8x.pt"),
                       help="Base model (yolov8n/s/m/l/x.pt)")
    parser.add_argument("--epochs", type=int, default=int(os.getenv("YOLO_EPOCHS", "300")),
                       help="Number of training epochs")
    parser.add_argument("--imgsz", type=int, default=int(os.getenv("YOLO_IMGSZ", "640")),
                       help="Input image size")
    parser.add_argument("--batch", type=int, default=int(os.getenv("YOLO_BATCH", "-1")),
                       help="Batch size (-1 for auto)")
    parser.add_argument("--device", default=os.getenv("YOLO_DEVICE", "auto"),
                       help="Device to use (auto/cpu/0/1/...)")
    parser.add_argument("--workers", type=int, default=int(os.getenv("YOLO_WORKERS", "8")),
                       help="Number of dataloader workers")
    parser.add_argument("--patience", type=int, default=50,
                       help="Early stopping patience")
    parser.add_argument("--optimizer", default="AdamW",
                       help="Optimizer (SGD/Adam/AdamW/NAdam/RAdam/RMSProp)")
    parser.add_argument("--lr0", type=float, default=0.001,
                       help="Initial learning rate")
    parser.add_argument("--lrf", type=float, default=0.01,
                       help="Final learning rate (lr0 * lrf)")
    parser.add_argument("--momentum", type=float, default=0.937,
                       help="SGD momentum/Adam beta1")
    parser.add_argument("--weight-decay", type=float, default=0.0005,
                       help="Optimizer weight decay")
    parser.add_argument("--warmup-epochs", type=float, default=3.0,
                       help="Warmup epochs")
    parser.add_argument("--hsv-h", type=float, default=0.015,
                       help="HSV-Hue augmentation")
    parser.add_argument("--hsv-s", type=float, default=0.7,
                       help="HSV-Saturation augmentation")
    parser.add_argument("--hsv-v", type=float, default=0.4,
                       help="HSV-Value augmentation")
    parser.add_argument("--degrees", type=float, default=0.0,
                       help="Rotation augmentation (degrees)")
    parser.add_argument("--translate", type=float, default=0.1,
                       help="Translation augmentation")
    parser.add_argument("--scale", type=float, default=0.5,
                       help="Scaling augmentation")
    parser.add_argument("--shear", type=float, default=0.0,
                       help="Shear augmentation (degrees)")
    parser.add_argument("--perspective", type=float, default=0.0,
                       help="Perspective augmentation")
    parser.add_argument("--flipud", type=float, default=0.0,
                       help="Vertical flip probability")
    parser.add_argument("--fliplr", type=float, default=0.5,
                       help="Horizontal flip probability")
    parser.add_argument("--mosaic", type=float, default=1.0,
                       help="Mosaic augmentation probability")
    parser.add_argument("--mixup", type=float, default=0.0,
                       help="Mixup augmentation probability")
    parser.add_argument("--copy-paste", type=float, default=0.0,
                       help="Copy-paste augmentation probability")
    parser.add_argument("--conf", type=float, default=None,
                       help="Confidence threshold for predictions")
    parser.add_argument("--iou", type=float, default=0.7,
                       help="IoU threshold for NMS")
    parser.add_argument("--resume", action="store_true",
                       help="Resume training from last checkpoint")

    args = parser.parse_args()

    data_yaml = args.data.resolve()
    config = validate_dataset(data_yaml)

    from ultralytics import YOLO
    import torch

    device = args.device
    if device == "auto":
        device = 0 if torch.cuda.is_available() else "cpu"

    print(f"\n{'='*60}")
    print(f"Enhanced YOLOv8 Training Configuration")
    print(f"{'='*60}")
    print(f"Dataset: {data_yaml}")
    print(f"Classes: {config['names']}")
    print(f"Base Model: {args.model}")
    print(f"Device: {device}")
    print(f"Image Size: {args.imgsz}")
    print(f"Batch Size: {args.batch}")
    print(f"Epochs: {args.epochs}")
    print(f"Patience: {args.patience}")
    print(f"Optimizer: {args.optimizer}")
    print(f"Learning Rate: {args.lr0} → {args.lr0 * args.lrf}")
    print(f"Weight Decay: {args.weight_decay}")
    print(f"{'='*60}\n")

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    # Load model
    model = YOLO(args.model)

    # Train with enhanced parameters
    results = model.train(
        data=str(data_yaml),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=device,
        workers=args.workers,
        project=str(MODEL_DIR),
        name="training_enhanced",
        exist_ok=True,
        pretrained=True,

        # Optimizer settings
        optimizer=args.optimizer,
        lr0=args.lr0,
        lrf=args.lrf,
        momentum=args.momentum,
        weight_decay=args.weight_decay,
        warmup_epochs=args.warmup_epochs,
        warmup_momentum=0.8,
        warmup_bias_lr=0.1,

        # Augmentation settings
        hsv_h=args.hsv_h,
        hsv_s=args.hsv_s,
        hsv_v=args.hsv_v,
        degrees=args.degrees,
        translate=args.translate,
        scale=args.scale,
        shear=args.shear,
        perspective=args.perspective,
        flipud=args.flipud,
        fliplr=args.fliplr,
        mosaic=args.mosaic,
        mixup=args.mixup,
        copy_paste=args.copy_paste,

        # Training settings
        patience=args.patience,
        save=True,
        save_period=-1,
        cache=False,
        rect=False,
        cos_lr=True,
        close_mosaic=10,
        amp=bool(device != "cpu"),
        fraction=1.0,
        profile=False,
        freeze=None,

        # Validation settings
        val=True,
        split="val",

        # Other settings
        seed=42,
        deterministic=True,
        single_cls=False,
        plots=True,
        verbose=True,
        resume=args.resume,
    )

    # Find best model
    best = MODEL_DIR / "training_enhanced" / "weights" / "best.pt"
    if not best.exists():
        raise FileNotFoundError(f"Training finished without {best}")

    # Copy to stable location
    stable = MODEL_DIR / "weights" / "best.pt"
    stable.parent.mkdir(parents=True, exist_ok=True)
    stable.write_bytes(best.read_bytes())

    print(f"\n{'='*60}")
    print(f"Training Complete - Running Test Evaluation")
    print(f"{'='*60}\n")

    # Evaluate on test split
    test_metrics = model.val(
        data=str(data_yaml),
        split="test",
        imgsz=args.imgsz,
        batch=args.batch,
        device=device,
        conf=args.conf or 0.001,
        iou=args.iou,
        max_det=300,
        plots=True,
        save_json=True,
        save_hybrid=False,
        verbose=True,
    )

    # Per-class metrics
    per_class_metrics = {}
    for i, class_name in enumerate(config["names"]):
        per_class_metrics[class_name] = {
            "precision": float(test_metrics.box.p[i]) if hasattr(test_metrics.box, 'p') else 0.0,
            "recall": float(test_metrics.box.r[i]) if hasattr(test_metrics.box, 'r') else 0.0,
            "mAP50": float(test_metrics.box.ap50[i]) if hasattr(test_metrics.box, 'ap50') else 0.0,
            "mAP50_95": float(test_metrics.box.ap[i]) if hasattr(test_metrics.box, 'ap') else 0.0,
        }

    # Compile comprehensive metrics
    metrics = {
        "dataset": str(data_yaml),
        "classes": config["names"],
        "base_model": args.model,
        "epochs": args.epochs,
        "imgsz": args.imgsz,
        "batch": args.batch,
        "device": str(device),
        "optimizer": args.optimizer,
        "learning_rate": f"{args.lr0} → {args.lr0 * args.lrf}",
        "weight_decay": args.weight_decay,
        "best_weights": str(stable),

        # Overall metrics
        "test_mAP50": float(test_metrics.box.map50),
        "test_mAP50_95": float(test_metrics.box.map),
        "test_precision": float(test_metrics.box.mp),
        "test_recall": float(test_metrics.box.mr),
        "test_f1": float(2 * test_metrics.box.mp * test_metrics.box.mr / (test_metrics.box.mp + test_metrics.box.mr + 1e-6)),

        # Per-class metrics
        "per_class": per_class_metrics,

        # Speed metrics
        "inference_time_ms": float(test_metrics.speed.get('inference', 0)) if hasattr(test_metrics, 'speed') else 0.0,
        "nms_time_ms": float(test_metrics.speed.get('nms', 0)) if hasattr(test_metrics, 'speed') else 0.0,
    }

    # Save metrics
    metrics_path = MODEL_DIR / "test_metrics_enhanced.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"Final Test Metrics")
    print(f"{'='*60}")
    print(json.dumps(metrics, indent=2))
    print(f"\n{'='*60}")
    print(f"✅ Model ready: {stable}")
    print(f"📊 Metrics saved: {metrics_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
