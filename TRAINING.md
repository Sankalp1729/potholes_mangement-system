# YOLOv8 training

This repository is wired to the supplied **IIT Madras Pothole Detection v2** dataset (2,722 images; 1,906 train / 542 validation / 274 test). The export is YOLOv8 object-detection format and contains three classes:

- `crocodile crack`
- `longitudinal crack`
- `pothole`

The dataset itself is not committed to Git because the images are too large for normal source control.

## 1. Prepare the supplied ZIP

Install only the lightweight training dependencies:

```bash
python -m pip install -r requirements-training.txt
```

Then extract/validate the ZIP with the project utility:

```bash
python scripts/prepare_dataset.py --zip "path/to/Pothole detection.v2i.yolov8.zip"
```

This creates:

```text
datasets/pothole_detection_v2/data.yaml
datasets/pothole_detection_v2/train/images/
datasets/pothole_detection_v2/train/labels/
datasets/pothole_detection_v2/valid/images/
datasets/pothole_detection_v2/valid/labels/
datasets/pothole_detection_v2/test/images/
datasets/pothole_detection_v2/test/labels/
```

## 2. Train

```bash
python scripts/train_yolo.py --data datasets/pothole_detection_v2/data.yaml
```

The default configuration uses a pretrained `yolov8m.pt`, 640px images, 150 epochs, early stopping (`patience=35`), deterministic seed 42, cosine learning-rate scheduling, and held-out test evaluation.

On a CUDA GPU, `--batch -1` lets Ultralytics auto-select a batch size. On CPU, use a small explicit batch such as `--batch 4`.

## 3. Evaluate

```bash
python scripts/evaluate_yolo.py \
  --model models/pothole_detector/weights/best.pt \
  --data datasets/pothole_detection_v2/data.yaml
```

Metrics are written to `models/pothole_detector/test_metrics.json`.

The primary object-detection metrics are **mAP@50, mAP@50:95, precision, and recall**. There is deliberately no fake "100% accuracy" value.

## 4. API inference

The FastAPI endpoint loads the trained checkpoint:

```text
POST /detect-image
```

The report form also sends uploaded images to `/upload-report`, where the same detector is used before the report is stored.

Set a custom checkpoint path if required:

```text
YOLO_MODEL_PATH=/absolute/path/to/best.pt
```

Optional thresholds:

```text
YOLO_CONFIDENCE=0.25
YOLO_IOU=0.50
```

If the checkpoint does not exist, the API returns HTTP 503 instead of inventing a detection.

## Important scope

The supplied dataset is image-only. It can train the YOLO road-damage detector, but it cannot legitimately train the repository's separate IoT sensor classifier or future-count model. Those components are therefore not fed synthetic data.
