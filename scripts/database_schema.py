"""
Database schema setup for the Pothole Detection System
Run this script to create the initial database tables
"""

import asyncio
import asyncpg
from datetime import datetime
from typing import Optional

# Database connection configuration
DATABASE_URL = "postgresql://username:password@localhost:5432/pothole_db"

async def create_database_schema():
    """Create all necessary tables for the pothole detection system"""
    
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        # Users table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                role VARCHAR(50) DEFAULT 'citizen',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Potholes table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS potholes (
                id SERIAL PRIMARY KEY,
                image_url VARCHAR(500),
                latitude DECIMAL(10, 8) NOT NULL,
                longitude DECIMAL(11, 8) NOT NULL,
                severity VARCHAR(20) CHECK (severity IN ('low', 'medium', 'high', 'critical')),
                report_source VARCHAR(20) CHECK (report_source IN ('mobile', 'iot', 'manual')),
                status VARCHAR(20) DEFAULT 'reported' CHECK (status IN ('reported', 'verified', 'in_progress', 'completed')),
                description TEXT,
                reporter_id INTEGER REFERENCES users(id),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                verified_at TIMESTAMP,
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Predictions table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id SERIAL PRIMARY KEY,
                region VARCHAR(100) NOT NULL,
                date DATE NOT NULL,
                pothole_count INTEGER NOT NULL,
                confidence_score DECIMAL(5, 4),
                model_version VARCHAR(50),
                weather_factors JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # IoT Sensors table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS iot_sensors (
                id SERIAL PRIMARY KEY,
                sensor_id VARCHAR(100) UNIQUE NOT NULL,
                latitude DECIMAL(10, 8) NOT NULL,
                longitude DECIMAL(11, 8) NOT NULL,
                status VARCHAR(20) DEFAULT 'active',
                last_reading TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Sensor Readings table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id SERIAL PRIMARY KEY,
                sensor_id VARCHAR(100) REFERENCES iot_sensors(sensor_id),
                vibration_x DECIMAL(8, 4),
                vibration_y DECIMAL(8, 4),
                vibration_z DECIMAL(8, 4),
                acceleration DECIMAL(8, 4),
                pothole_detected BOOLEAN DEFAULT FALSE,
                confidence_score DECIMAL(5, 4),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Notifications table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY,
                pothole_id INTEGER REFERENCES potholes(id),
                recipient_email VARCHAR(255) NOT NULL,
                notification_type VARCHAR(50),
                status VARCHAR(20) DEFAULT 'pending',
                sent_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for better performance
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_potholes_location ON potholes(latitude, longitude)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_potholes_status ON potholes(status)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_potholes_timestamp ON potholes(timestamp)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_predictions_region_date ON predictions(region, date)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_sensor_readings_timestamp ON sensor_readings(timestamp)')
        
        print("✅ Database schema created successfully!")
        
        # Insert sample data
        await insert_sample_data(conn)
        
    except Exception as e:
        print(f"❌ Error creating database schema: {e}")
    finally:
        await conn.close()

async def insert_sample_data(conn):
    """Insert sample data for testing"""
    
    # Insert sample users
    await conn.execute('''
        INSERT INTO users (name, email, role) VALUES 
        ('John Doe', 'john@example.com', 'citizen'),
        ('Jane Smith', 'jane@example.com', 'authority'),
        ('Mike Johnson', 'mike@example.com', 'admin')
        ON CONFLICT (email) DO NOTHING
    ''')
    
    # Insert sample potholes
    await conn.execute('''
        INSERT INTO potholes (latitude, longitude, severity, report_source, description, reporter_id) VALUES 
        (40.7128, -74.0060, 'high', 'mobile', 'Large pothole on Main Street', 1),
        (40.7589, -73.9851, 'medium', 'iot', 'Detected via sensor network', 1),
        (40.7505, -73.9934, 'critical', 'mobile', 'Deep pothole causing vehicle damage', 1)
        ON CONFLICT DO NOTHING
    ''')
    
    # Insert sample IoT sensors
    await conn.execute('''
        INSERT INTO iot_sensors (sensor_id, latitude, longitude) VALUES 
        ('ESP32_001', 40.7128, -74.0060),
        ('ESP32_002', 40.7589, -73.9851),
        ('ESP32_003', 40.7505, -73.9934)
        ON CONFLICT (sensor_id) DO NOTHING
    ''')
    
    print("✅ Sample data inserted successfully!")

if __name__ == "__main__":
    asyncio.run(create_database_schema())
