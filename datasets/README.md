# Dataset location

The YOLOv8 dataset archive is intentionally not committed to Git. Extract it with:

```bash
python scripts/prepare_dataset.py --zip "path/to/Pothole detection.v2i.yolov8.zip"
```

The expected result is:

```text
datasets/pothole_detection_v2/
  data.yaml
  train/images/
  train/labels/
  valid/images/
  valid/labels/
  test/images/
  test/labels/
```

The supplied dataset is the IIT Madras / Roboflow Pothole Detection v2 export.
