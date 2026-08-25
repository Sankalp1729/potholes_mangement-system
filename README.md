# Pothole Management System

A full-stack pothole/road-damage management system with a Next.js dashboard, FastAPI backend, PostgreSQL data model, and a real YOLOv8 object-detection pipeline.

## Real ML pipeline

The image-detection path uses the supplied **IIT Madras Pothole Detection v2** dataset:

- 2,722 images
- 1,906 train / 542 validation / 274 test
- 3 classes: `crocodile crack`, `longitudinal crack`, `pothole`
- YOLOv8 annotations
- 640×640 images
- no exact duplicate images were found across the supplied splits during validation

The API no longer returns hard-coded confidence scores or bounding boxes.

## Train the detector

You do **not** need the complete application dependency stack just to train the detector.

1. Download/export the dataset in YOLOv8 format from the public dataset page:
   https://universe.roboflow.com/indian-institute-of-technology-madras-xamot/pothole-detection-huf2x/dataset/2

2. Extract it to:

```text
datasets/pothole_detection_v2/
```

3. Install the lightweight training dependencies:

```bash
python -m pip install -r requirements-training.txt
```

4. Train:

```bash
python scripts/train_yolo.py --data datasets/pothole_detection_v2/data.yaml
```

5. Evaluate the untouched test set:

```bash
python scripts/evaluate_yolo.py --model models/pothole_detector/weights/best.pt --data datasets/pothole_detection_v2/data.yaml
```

The trained checkpoint is `models/pothole_detector/weights/best.pt`.

## Run the backend

Install the full backend dependencies only when you need the application/API:

```bash
python -m pip install -r requirements.txt
python scripts/fastapi_backend.py
```

The API exposes `/detect-image` for real YOLO inference and `/model-status` for checking whether the trained checkpoint is installed. If no trained checkpoint is available, `/detect-image` returns a clear 503 error instead of fabricating a prediction.

## Accuracy

Object detection does not have a meaningful single "perfect accuracy" target. The project evaluates the held-out test set using mAP@50, mAP@50:95, precision, and recall. The training pipeline uses pretrained YOLOv8 weights, deterministic seeding, early stopping, cosine learning-rate scheduling, and validation/test separation to target strong generalization without test-set leakage.

## Scope note

The supplied dataset is image-only. It can train the YOLO road-damage detector, but it cannot legitimately train the repository's separate IoT sensor classifier or future-count prediction model. Those components are therefore not trained from fabricated data.
