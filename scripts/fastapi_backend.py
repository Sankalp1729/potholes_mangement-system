"""
FastAPI Backend for Pothole Detection System
This demonstrates the core API structure based on your roadmap
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import asyncpg
import asyncio
import os
from pathlib import Path

# Pydantic models
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

# FastAPI app initialization
app = FastAPI(
    title="Pothole Detection API",
    description="API for pothole detection, reporting, and management system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/pothole_db")

async def get_db_connection():
    """Get database connection"""
    return await asyncpg.connect(DATABASE_URL)

# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Pothole Detection API is running", "version": "1.0.0"}

@app.post("/upload-report", response_model=dict)
async def upload_report(
    pothole: PotholeCreate,
    image: Optional[UploadFile] = File(None)
):
    """Upload a new pothole report with optional image"""
    try:
        conn = await get_db_connection()
        
        # Save image to S3 (simulated)
        image_url = None
        if image:
            # In production, upload to AWS S3
            image_url = f"https://s3.amazonaws.com/pothole-images/{image.filename}"
        
        # Insert pothole record
        query = '''
            INSERT INTO potholes (latitude, longitude, severity, report_source, description, image_url)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id
        '''
        
        pothole_id = await conn.fetchval(
            query,
            pothole.latitude,
            pothole.longitude,
            pothole.severity,
            pothole.report_source,
            pothole.description,
            image_url
        )
        
        await conn.close()
        
        # Trigger ML detection if image provided (simulated)
        detection_result = None
        if image:
            detection_result = await run_yolo_detection(image)
        
        return {
            "success": True,
            "pothole_id": pothole_id,
            "message": "Report uploaded successfully",
            "detection_result": detection_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading report: {str(e)}")

@app.get("/potholes", response_model=List[PotholeResponse])
async def get_potholes(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 100
):
    """Get all potholes with optional filtering"""
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
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching potholes: {str(e)}")

@app.post("/detect-image", response_model=DetectionResult)
async def detect_image(image: UploadFile = File(...)):
    """Run YOLO detection on uploaded image"""
    try:
        detection_result = await run_yolo_detection(image)
        return detection_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting potholes: {str(e)}")

@app.get("/predict", response_model=List[PredictionResponse])
async def get_predictions(region: Optional[str] = None):
    """Get pothole predictions using ML models"""
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
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching predictions: {str(e)}")

@app.post("/update-status")
async def update_pothole_status(pothole_id: int, new_status: str):
    """Update pothole status (for authorities)"""
    try:
        conn = await get_db_connection()
        
        query = '''
            UPDATE potholes 
            SET status = $1, updated_at = CURRENT_TIMESTAMP
            WHERE id = $2
        '''
        
        await conn.execute(query, new_status, pothole_id)
        await conn.close()
        
        # Send notification to reporter (simulated)
        await send_status_notification(pothole_id, new_status)
        
        return {"success": True, "message": "Status updated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating status: {str(e)}")

@app.post("/iot-data")
async def receive_iot_data(sensor_data: dict):
    """Receive data from IoT sensors (ESP32 + accelerometer)"""
    try:
        conn = await get_db_connection()
        
        # Insert sensor reading
        query = '''
            INSERT INTO sensor_readings 
            (sensor_id, vibration_x, vibration_y, vibration_z, acceleration)
            VALUES ($1, $2, $3, $4, $5)
        '''
        
        await conn.execute(
            query,
            sensor_data["sensor_id"],
            sensor_data["vibration_x"],
            sensor_data["vibration_y"],
            sensor_data["vibration_z"],
            sensor_data["acceleration"]
        )
        
        # Run ML model to detect pothole from sensor data
        pothole_detected = await detect_pothole_from_sensor(sensor_data)
        
        if pothole_detected:
            # Create automatic pothole report
            await create_automatic_report(sensor_data)
        
        await conn.close()
        
        return {"success": True, "pothole_detected": pothole_detected}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing IoT data: {str(e)}")

# Helper functions (simulated ML operations)

async def run_yolo_detection(image: UploadFile) -> DetectionResult:
    """Simulate YOLOv8 pothole detection"""
    # In production, this would load your trained YOLO model and run inference
    return DetectionResult(
        detected=True,
        confidence=0.87,
        severity="medium",
        bounding_boxes=[
            {"x": 100, "y": 150, "width": 80, "height": 60, "confidence": 0.87}
        ]
    )

async def detect_pothole_from_sensor(sensor_data: dict) -> bool:
    """Simulate ML model for sensor-based pothole detection"""
    # In production, this would use your trained RandomForest/XGBoost model
    acceleration = sensor_data.get("acceleration", 0)
    return acceleration > 2.5  # Threshold for pothole detection

async def create_automatic_report(sensor_data: dict):
    """Create automatic pothole report from IoT sensor"""
    conn = await get_db_connection()
    
    # Get sensor location
    sensor_query = "SELECT latitude, longitude FROM iot_sensors WHERE sensor_id = $1"
    sensor_info = await conn.fetchrow(sensor_query, sensor_data["sensor_id"])
    
    if sensor_info:
        # Insert automatic pothole report
        query = '''
            INSERT INTO potholes (latitude, longitude, severity, report_source, description)
            VALUES ($1, $2, $3, $4, $5)
        '''
        
        await conn.execute(
            query,
            sensor_info["latitude"],
            sensor_info["longitude"],
            "medium",  # Default severity for IoT detection
            "iot",
            f"Automatically detected by sensor {sensor_data['sensor_id']}"
        )
    
    await conn.close()

async def send_status_notification(pothole_id: int, status: str):
    """Send notification about status update"""
    # In production, integrate with SendGrid/Twilio
    print(f"Notification: Pothole {pothole_id} status updated to {status}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
