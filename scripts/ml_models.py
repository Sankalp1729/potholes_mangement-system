"""
Production ML models for the Pothole Detection System.

The image detector is trained with the supplied IIT Madras / Roboflow
YOLOv8 dataset. Sensor and future-count models are kept separate because
the supplied dataset contains image bounding boxes only.
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

ROOT_DIR = Path(__file__).resolve().parents[1]
MODEL_DIR = Path(os.getenv("MODEL_DIR", ROOT_DIR / "models"))
YOLO_MODEL_PATH = Path(
    os.getenv("YOLO_MODEL_PATH", MODEL_DIR / "pothole_detector" / "weights" / "best.pt")
)


class PotholeMLModels:
    """Lazy-loading model registry used by scripts and the API."""

    def __init__(self) -> None:
        self.yolo_model = None
        self.sensor_model = None
        self.prediction_model = None

    def train_yolo_model(
        self,
        dataset_yaml: str | os.PathLike[str],
        model_name: str = "yolov8m.pt",
        epochs: int = 150,
        imgsz: int = 640,
        batch: int = -1,
        device: str | int = "auto",
    ) -> dict[str, Any]:
        """Train a real YOLOv8 detector and persist the best checkpoint."""
        from ultralytics import YOLO

        dataset_yaml = Path(dataset_yaml).resolve()
        if not dataset_yaml.exists():
            raise FileNotFoundError(f"Dataset YAML not found: {dataset_yaml}")

        output_dir = MODEL_DIR / "pothole_detector"
        output_dir.mkdir(parents=True, exist_ok=True)

        model = YOLO(model_name)
        if device == "auto":
            device = 0 if __import__("torch").cuda.is_available() else "cpu"

        results = model.train(
            data=str(dataset_yaml),
            epochs=epochs,
            imgsz=imgsz,
            batch=batch,
            device=device,
            project=str(output_dir),
            name="training",
            exist_ok=True,
            pretrained=True,
            optimizer="auto",
            patience=35,
            cos_lr=True,
            close_mosaic=10,
            cache=False,
            workers=min(4, os.cpu_count() or 1),
            amp=bool(device != "cpu"),
            seed=42,
            deterministic=True,
            plots=True,
            verbose=True,
        )

        best_weight = output_dir / "training" / "weights" / "best.pt"
        if not best_weight.exists():
            raise FileNotFoundError(
                f"Training completed but best.pt was not produced at {best_weight}"
            )

        stable_path = output_dir / "weights" / "best.pt"
        stable_path.parent.mkdir(parents=True, exist_ok=True)
        stable_path.write_bytes(best_weight.read_bytes())

        self.yolo_model = model
        return {
            "weights": str(stable_path),
            "results_dir": str(output_dir / "training"),
            "epochs": epochs,
            "imgsz": imgsz,
            "device": str(device),
            "results": str(results),
        }

    def train_sensor_model(self, sensor_data: pd.DataFrame) -> float:
        """Train the optional sensor classifier from real sensor data."""
        features = ["vibration_x", "vibration_y", "vibration_z", "acceleration"]
        missing = [c for c in features + ["pothole_detected"] if c not in sensor_data]
        if missing:
            raise ValueError(f"Sensor dataset is missing columns: {missing}")

        X = sensor_data[features]
        y = sensor_data["pothole_detected"]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        self.sensor_model = RandomForestClassifier(
            n_estimators=300,
            random_state=42,
            max_depth=None,
            class_weight="balanced",
            n_jobs=-1,
        )
        self.sensor_model.fit(X_train, y_train)
        y_pred = self.sensor_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.sensor_model, MODEL_DIR / "sensor_model.pkl")
        print(classification_report(y_test, y_pred))
        return float(accuracy)

    def predict_sensor_pothole(self, sensor_reading: dict) -> dict[str, Any]:
        """Predict a pothole from an IoT sensor reading."""
        if self.sensor_model is None:
            self.sensor_model = joblib.load(MODEL_DIR / "sensor_model.pkl")
        features = np.array([[
            sensor_reading["vibration_x"],
            sensor_reading["vibration_y"],
            sensor_reading["vibration_z"],
            sensor_reading["acceleration"],
        ]])
        prediction = self.sensor_model.predict(features)[0]
        probability = self.sensor_model.predict_proba(features)[0]
        return {
            "pothole_detected": bool(prediction),
            "confidence": float(max(probability)),
        }


async def train_all_models(
    dataset_yaml: str | os.PathLike[str] = ROOT_DIR / "datasets" / "pothole_detection_v2" / "data.yaml",
) -> None:
    """Train only models for which real training data is available."""
    ml_models = PotholeMLModels()
    print("🚀 Starting image-detection training...")
    result = ml_models.train_yolo_model(dataset_yaml)
    print(json.dumps(result, indent=2))
    print(
        "ℹ️ Sensor and future-count models are not trained here: "
        "the supplied dataset is image-only."
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data",
        default=str(ROOT_DIR / "datasets" / "pothole_detection_v2" / "data.yaml"),
        help="Path to YOLO data.yaml",
    )
    args = parser.parse_args()
    asyncio.run(train_all_models(args.data))
