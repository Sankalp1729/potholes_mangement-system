"""
FastAPI backend for the Pothole Detection System.

Image detection is backed by the trained YOLOv8 checkpoint produced by
scripts/train_yolo.py. The API never fabricates detections: if the model
is not installed/trained, image detection returns a clear 503 response.
"""

from __future__ import annotations

import io
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import asyncpg
import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pydantic import BaseModel

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_PATH = ROOT_DIR / "models" / "pothole_detector" / "weights" / "best.pt"
YOLO_MODEL_PATH = Path(os.getenv("YOLO_MODEL_PATH", DEFAULT_MODEL_PATH))
YOLO_CONFIDENCE = float(os.getenv("YOLO_CONFIDENCE", "0.25"))
YOLO_IOU = float(os.getenv("YOLO_IOU", "0.50"))

_yolo_model = None


class PotholeCreate(BaseModel):
    latitude: float
    longitude: float
    severity: str
    description: Optional[str] = None
    report_source: str = "mobile"


class PotholeResponse(BaseModel):
    id: int
    latitude: float
    longitude: float
    severity: str
    status: str
    report_source: str
    description: Optional[str]
    timestamp: datetime


class PredictionResponse(BaseModel):
    region: str
    date: str
    pothole_count: int
    confidence_score: float


class DetectionResult(BaseModel):
    detected: bool
    confidence: float
    severity: str
    bounding_boxes: List[dict]


app = FastAPI(
    title="Pothole Detection API",
    description="Pothole detection, reporting, and management API",
    version="2.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://username:password@localhost:5432/pothole_db",
)


async def get_db_connection():
    return await asyncpg.connect(DATABASE_URL)


def get_yolo_model():
    """Load the detector once, on first inference."""
    global _yolo_model
    if _yolo_model is not None:
        return _yolo_model

    if not YOLO_MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained YOLO model not found at {YOLO_MODEL_PATH}. "
            "Run scripts/train_yolo.py first."
        )

    from ultralytics import YOLO

    _yolo_model = YOLO(str(YOLO_MODEL_PATH))
    return _yolo_model


@app.get("/")
async def root():
    return {
        "message": "Pothole Detection API is running",
        "version": "2.1.0",
        "model_path": str(YOLO_MODEL_PATH),
        "model_ready": YOLO_MODEL_PATH.exists(),
    }


@app.get("/model-status")
async def model_status():
    return {
        "ready": YOLO_MODEL_PATH.exists(),
        "model_path": str(YOLO_MODEL_PATH),
        "confidence_threshold": YOLO_CONFIDENCE,
        "iou_threshold": YOLO_IOU,
    }


@app.post("/upload-report", response_model=dict)
async def upload_report(
    latitude: float = Form(...),
    longitude: float = Form(...),
    severity: str = Form(...),
    description: Optional[str] = Form(None),
    report_source: str = Form("web"),
    image: Optional[UploadFile] = File(None),
):
    """Create a report from multipart form data and optionally run YOLO."""
    detection_result = None
    if image:
        try:
            detection_result = await run_yolo_detection(image)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=503, detail=str(exc))

        # If the caller did not choose a severity, use the explicit detector
        # heuristic; otherwise preserve the user's selected severity.
        if not severity and detection_result.detected:
            severity = detection_result.severity

    try:
        conn = await get_db_connection()
        image_url = f"uploaded://{image.filename}" if image else None
        query = """
            INSERT INTO potholes
                (latitude, longitude, severity, report_source, description, image_url)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id
        """
        pothole_id = await conn.fetchval(
            query,
            latitude,
            longitude,
            severity,
            report_source,
            description,
            image_url,
        )
        await conn.close()

        return {
            "success": True,
            "pothole_id": pothole_id,
            "message": "Report uploaded successfully",
            "detection_result": detection_result.model_dump() if detection_result else None,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error uploading report: {exc}")


@app.get("/potholes", response_model=List[PotholeResponse])
async def get_potholes(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 100,
):
    try:
        conn = await get_db_connection()
        query = "SELECT * FROM potholes WHERE 1=1"
        params = []
        param_count = 0
        if status:
            param_count += 1
            query += f" AND status = ${param_count}"
            params.append(status)
        if severity:
            param_count += 1
            query += f" AND severity = ${param_count}"
            params.append(severity)
        query += f" ORDER BY timestamp DESC LIMIT ${param_count + 1}"
        params.append(limit)
        rows = await conn.fetch(query, *params)
        await conn.close()
        return [dict(row) for row in rows]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error fetching potholes: {exc}")


@app.post("/detect-image", response_model=DetectionResult)
async def detect_image(image: UploadFile = File(...)):
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="Please upload a valid image file.")
    try:
        return await run_yolo_detection(image)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error detecting potholes: {exc}")


@app.get("/predict", response_model=List[PredictionResponse])
async def get_predictions(region: Optional[str] = None):
    try:
        conn = await get_db_connection()
        query = "SELECT * FROM predictions WHERE 1=1"
        params = []
        if region:
            query += " AND region = $1"
            params.append(region)
        query += " ORDER BY date DESC LIMIT 30"
        rows = await conn.fetch(query, *params)
        await conn.close()
        return [dict(row) for row in rows]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error fetching predictions: {exc}")


@app.post("/update-status")
async def update_pothole_status(pothole_id: int, new_status: str):
    try:
        conn = await get_db_connection()
        query = """
            UPDATE potholes
            SET status = $1, updated_at = CURRENT_TIMESTAMP
            WHERE id = $2
        """
        await conn.execute(query, new_status, pothole_id)
        await conn.close()
        await send_status_notification(pothole_id, new_status)
        return {"success": True, "message": "Status updated successfully"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error updating status: {exc}")


@app.post("/iot-data")
async def receive_iot_data(sensor_data: dict):
    """Store IoT data using the current rule-based fallback.

    The supplied dataset contains images only, so it cannot legitimately
    train the sensor classifier.
    """
    try:
        conn = await get_db_connection()
        query = """
            INSERT INTO sensor_readings
                (sensor_id, vibration_x, vibration_y, vibration_z, acceleration)
            VALUES ($1, $2, $3, $4, $5)
        """
        await conn.execute(
            query,
            sensor_data["sensor_id"],
            sensor_data["vibration_x"],
            sensor_data["vibration_y"],
            sensor_data["vibration_z"],
            sensor_data["acceleration"],
        )
        pothole_detected = await detect_pothole_from_sensor(sensor_data)
        if pothole_detected:
            await create_automatic_report(sensor_data)
        await conn.close()
        return {"success": True, "pothole_detected": pothole_detected, "method": "rule_based_fallback"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error processing IoT data: {exc}")


async def run_yolo_detection(image: UploadFile) -> DetectionResult:
    """Run real YOLO inference on an uploaded image."""
    model = get_yolo_model()
    raw = await image.read()
    if not raw:
        raise ValueError("Uploaded image is empty.")

    pil_image = Image.open(io.BytesIO(raw)).convert("RGB")
    results = model.predict(
        source=np.asarray(pil_image),
        conf=YOLO_CONFIDENCE,
        iou=YOLO_IOU,
        imgsz=640,
        verbose=False,
    )

    result = results[0]
    names = result.names or {}
    boxes = []
    pothole_confidences = []
    pothole_areas = []
    image_area = pil_image.width * pil_image.height

    if result.boxes is not None:
        xyxy = result.boxes.xyxy.cpu().numpy()
        confidences = result.boxes.conf.cpu().numpy()
        classes = result.boxes.cls.cpu().numpy().astype(int)
        for coords, confidence, class_id in zip(xyxy, confidences, classes):
            x1, y1, x2, y2 = map(float, coords)
            class_name = str(names.get(int(class_id), int(class_id)))
            width = max(0.0, x2 - x1)
            height = max(0.0, y2 - y1)
            area_ratio = (width * height) / max(image_area, 1)
            boxes.append({
                "x": round(x1, 2),
                "y": round(y1, 2),
                "width": round(width, 2),
                "height": round(height, 2),
                "confidence": round(float(confidence), 4),
                "class_id": int(class_id),
                "class_name": class_name,
                "area_ratio": round(area_ratio, 6),
            })
            if class_name.strip().lower() == "pothole":
                pothole_confidences.append(float(confidence))
                pothole_areas.append(area_ratio)

    detected = bool(pothole_confidences)
    confidence = max(pothole_confidences, default=0.0)
    largest_area = max(pothole_areas, default=0.0)

    # The dataset has no severity labels. This is an explicit area heuristic,
    # not a learned severity score.
    if largest_area >= 0.08:
        severity = "high"
    elif largest_area >= 0.03:
        severity = "medium"
    elif detected:
        severity = "low"
    else:
        severity = "none"

    return DetectionResult(
        detected=detected,
        confidence=round(confidence, 4),
        severity=severity,
        bounding_boxes=boxes,
    )


async def detect_pothole_from_sensor(sensor_data: dict) -> bool:
    return sensor_data.get("acceleration", 0) > 2.5


async def create_automatic_report(sensor_data: dict):
    conn = await get_db_connection()
    sensor_query = "SELECT latitude, longitude FROM iot_sensors WHERE sensor_id = $1"
    sensor_info = await conn.fetchrow(sensor_query, sensor_data["sensor_id"])
    if sensor_info:
        query = """
            INSERT INTO potholes
                (latitude, longitude, severity, report_source, description)
            VALUES ($1, $2, $3, $4, $5)
        """
        await conn.execute(
            query,
            sensor_info["latitude"],
            sensor_info["longitude"],
            "medium",
            "iot",
            f"Automatically detected by sensor {sensor_data['sensor_id']}",
        )
    await conn.close()


async def send_status_notification(pothole_id: int, status: str):
    print(f"Notification: Pothole {pothole_id} status updated to {status}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
