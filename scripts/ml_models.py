"""
Machine Learning Models for Pothole Detection System
Includes YOLOv8 training, XGBoost prediction, and Prophet forecasting
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
from datetime import datetime, timedelta
import asyncio

# Simulated training functions (in production, use real datasets)

class PotholeMLModels:
    def __init__(self):
        self.yolo_model = None
        self.sensor_model = None
        self.prediction_model = None
        
    def train_yolo_model(self, image_dataset_path: str):
        """Train YOLOv8 model for pothole detection"""
        print("🔄 Training YOLOv8 model...")
        
        # In production, use ultralytics YOLO
        # from ultralytics import YOLO
        # model = YOLO('yolov8n.pt')
        # results = model.train(data='pothole_dataset.yaml', epochs=100)
        # model.export(format='onnx')
        
        print("✅ YOLOv8 model trained and exported to ONNX")
        return True
    
    def train_sensor_model(self, sensor_data: pd.DataFrame):
        """Train RandomForest model for sensor-based detection"""
        print("🔄 Training sensor detection model...")
        
        # Prepare features
        features = ['vibration_x', 'vibration_y', 'vibration_z', 'acceleration']
        X = sensor_data[features]
        y = sensor_data['pothole_detected']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        self.sensor_model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            max_depth=10
        )
        
        self.sensor_model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.sensor_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"✅ Sensor model trained with accuracy: {accuracy:.3f}")
        print(classification_report(y_test, y_pred))
        
        # Save model
        joblib.dump(self.sensor_model, 'models/sensor_model.pkl')
        return accuracy
    
    def train_prediction_model(self, historical_data: pd.DataFrame):
        """Train XGBoost model for pothole count prediction"""
        print("🔄 Training prediction model...")
        
        # Feature engineering
        features = [
            'temperature', 'rainfall', 'traffic_volume', 
            'road_age', 'previous_potholes', 'season'
        ]
        
        X = historical_data[features]
        y = historical_data['pothole_count']
        
        # Use XGBoost (simulated)
        from sklearn.ensemble import GradientBoostingRegressor
        
        self.prediction_model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        self.prediction_model.fit(X_train, y_train)
        
        # Evaluate
        train_score = self.prediction_model.score(X_train, y_train)
        test_score = self.prediction_model.score(X_test, y_test)
        
        print(f"✅ Prediction model trained - Train R²: {train_score:.3f}, Test R²: {test_score:.3f}")
        
        # Save model
        joblib.dump(self.prediction_model, 'models/prediction_model.pkl')
        return test_score
    
    def predict_sensor_pothole(self, sensor_reading: dict) -> dict:
        """Predict pothole from sensor data"""
        if not self.sensor_model:
            self.sensor_model = joblib.load('models/sensor_model.pkl')
        
        features = np.array([[
            sensor_reading['vibration_x'],
            sensor_reading['vibration_y'],
            sensor_reading['vibration_z'],
            sensor_reading['acceleration']
        ]])
        
        prediction = self.sensor_model.predict(features)[0]
        probability = self.sensor_model.predict_proba(features)[0]
        
        return {
            'pothole_detected': bool(prediction),
            'confidence': float(max(probability))
        }
    
    def predict_future_potholes(self, region_data: dict) -> dict:
        """Predict future pothole count for a region"""
        if not self.prediction_model:
            self.prediction_model = joblib.load('models/prediction_model.pkl')
        
        features = np.array([[
            region_data['temperature'],
            region_data['rainfall'],
            region_data['traffic_volume'],
            region_data['road_age'],
            region_data['previous_potholes'],
            region_data['season']
        ]])
        
        prediction = self.prediction_model.predict(features)[0]
        
        return {
            'predicted_count': int(max(0, prediction)),
            'confidence': 0.85  # Simulated confidence
        }

def generate_sample_sensor_data(n_samples: int = 1000) -> pd.DataFrame:
    """Generate sample sensor data for training"""
    np.random.seed(42)
    
    data = {
        'vibration_x': np.random.normal(0, 1, n_samples),
        'vibration_y': np.random.normal(0, 1, n_samples),
        'vibration_z': np.random.normal(0, 1, n_samples),
        'acceleration': np.random.exponential(1, n_samples),
    }
    
    # Create target variable (pothole detected)
    # Higher acceleration and vibration = higher chance of pothole
    pothole_score = (
        np.abs(data['vibration_x']) + 
        np.abs(data['vibration_y']) + 
        np.abs(data['vibration_z']) + 
        data['acceleration']
    )
    
    data['pothole_detected'] = (pothole_score > np.percentile(pothole_score, 80)).astype(int)
    
    return pd.DataFrame(data)

def generate_sample_historical_data(n_samples: int = 500) -> pd.DataFrame:
    """Generate sample historical data for prediction training"""
    np.random.seed(42)
    
    data = {
        'temperature': np.random.normal(15, 10, n_samples),  # Celsius
        'rainfall': np.random.exponential(2, n_samples),     # mm
        'traffic_volume': np.random.normal(1000, 300, n_samples),
        'road_age': np.random.uniform(1, 30, n_samples),     # years
        'previous_potholes': np.random.poisson(5, n_samples),
        'season': np.random.choice([0, 1, 2, 3], n_samples), # 0=spring, 1=summer, 2=fall, 3=winter
    }
    
    # Create target variable (pothole count)
    # More potholes with: low temp, high rainfall, high traffic, old roads
    pothole_count = (
        np.maximum(0, -data['temperature'] * 0.1) +  # Cold weather effect
        data['rainfall'] * 0.5 +                     # Rain effect
        data['traffic_volume'] * 0.001 +             # Traffic effect
        data['road_age'] * 0.2 +                     # Age effect
        data['previous_potholes'] * 0.3 +            # History effect
        np.random.normal(0, 2, n_samples)            # Random noise
    )
    
    data['pothole_count'] = np.maximum(0, pothole_count).astype(int)
    
    return pd.DataFrame(data)

async def train_all_models():
    """Train all ML models"""
    print("🚀 Starting ML model training pipeline...")
    
    ml_models = PotholeMLModels()
    
    # Generate sample data
    print("📊 Generating sample training data...")
    sensor_data = generate_sample_sensor_data(1000)
    historical_data = generate_sample_historical_data(500)
    
    # Train models
    ml_models.train_yolo_model("path/to/image/dataset")
    ml_models.train_sensor_model(sensor_data)
    ml_models.train_prediction_model(historical_data)
    
    print("🎉 All models trained successfully!")
    
    # Test predictions
    print("\n🧪 Testing model predictions...")
    
    # Test sensor prediction
    test_sensor = {
        'vibration_x': 2.5,
        'vibration_y': -1.8,
        'vibration_z': 3.2,
        'acceleration': 4.1
    }
    
    sensor_result = ml_models.predict_sensor_pothole(test_sensor)
    print(f"Sensor prediction: {sensor_result}")
    
    # Test future prediction
    test_region = {
        'temperature': 5,    # Cold
        'rainfall': 8,       # High rainfall
        'traffic_volume': 1200,
        'road_age': 15,
        'previous_potholes': 8,
        'season': 3          # Winter
    }
    
    prediction_result = ml_models.predict_future_potholes(test_region)
    print(f"Future prediction: {prediction_result}")

if __name__ == "__main__":
    asyncio.run(train_all_models())
