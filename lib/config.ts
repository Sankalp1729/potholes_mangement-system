// Configuration management for the Pothole Detection System
// Based on your Phase 1 requirements

export const config = {
  // API Configuration
  api: {
    baseUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
    timeout: 30000,
  },

  // Database Configuration
  database: {
    url: process.env.DATABASE_URL || "postgresql://username:password@localhost:5432/pothole_db",
    maxConnections: 20,
  },

  // AWS Configuration
  aws: {
    region: process.env.AWS_REGION || "us-east-1",
    s3: {
      bucket: process.env.AWS_S3_BUCKET || "pothole-images",
      accessKeyId: process.env.AWS_ACCESS_KEY_ID,
      secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
    },
    rds: {
      endpoint: process.env.AWS_RDS_ENDPOINT,
    },
  },

  // ML Models Configuration
  ml: {
    yolo: {
      modelPath: "/models/yolov8_pothole.onnx",
      confidenceThreshold: 0.5,
      nmsThreshold: 0.4,
    },
    xgboost: {
      modelPath: "/models/prediction_model.pkl",
      features: ["temperature", "rainfall", "traffic_volume", "road_age", "previous_potholes", "season"],
    },
    sensor: {
      modelPath: "/models/sensor_model.pkl",
      vibrationThreshold: 2.5,
    },
  },

  // IoT Configuration
  iot: {
    mqtt: {
      broker: process.env.MQTT_BROKER || "mqtt://localhost:1883",
      topics: {
        sensorData: "pothole/sensor/+/data",
        alerts: "pothole/alerts",
        status: "pothole/sensor/+/status",
      },
      qos: 1,
    },
    esp32: {
      accelerometerSensitivity: 2.0,
      gpsAccuracy: 5, // meters
      reportingInterval: 30000, // milliseconds
    },
  },

  // Notification Configuration
  notifications: {
    email: {
      provider: "sendgrid",
      apiKey: process.env.SENDGRID_API_KEY,
      fromEmail: process.env.FROM_EMAIL || "noreply@potholedetection.com",
    },
    sms: {
      provider: "twilio",
      accountSid: process.env.TWILIO_ACCOUNT_SID,
      authToken: process.env.TWILIO_AUTH_TOKEN,
      fromNumber: process.env.TWILIO_FROM_NUMBER,
    },
    push: {
      fcmServerKey: process.env.FCM_SERVER_KEY,
    },
  },

  // Security Configuration
  security: {
    jwt: {
      secret: process.env.JWT_SECRET || "your-super-secret-jwt-key",
      expiresIn: "24h",
    },
    rateLimit: {
      windowMs: 15 * 60 * 1000, // 15 minutes
      maxRequests: 100,
    },
    cors: {
      origins: process.env.ALLOWED_ORIGINS?.split(",") || ["http://localhost:3000"],
    },
  },

  // Map Configuration
  maps: {
    provider: "mapbox", // or 'google'
    mapbox: {
      accessToken: process.env.MAPBOX_ACCESS_TOKEN,
      style: "mapbox://styles/mapbox/streets-v11",
    },
    google: {
      apiKey: process.env.GOOGLE_MAPS_API_KEY,
    },
    defaultCenter: {
      lat: 40.7128,
      lng: -74.006,
    },
    defaultZoom: 12,
  },

  // Monitoring Configuration
  monitoring: {
    sentry: {
      dsn: process.env.SENTRY_DSN,
      environment: process.env.NODE_ENV || "development",
    },
    prometheus: {
      enabled: process.env.PROMETHEUS_ENABLED === "true",
      port: Number.parseInt(process.env.PROMETHEUS_PORT || "9090"),
    },
  },

  // Cache Configuration
  cache: {
    redis: {
      url: process.env.REDIS_URL || "redis://localhost:6379",
      ttl: 3600, // 1 hour
    },
  },

  // File Upload Configuration
  upload: {
    maxFileSize: 10 * 1024 * 1024, // 10MB
    allowedTypes: ["image/jpeg", "image/png", "image/webp"],
    uploadPath: "/tmp/uploads",
  },

  // Prediction Configuration
  prediction: {
    updateInterval: 24 * 60 * 60 * 1000, // 24 hours
    forecastDays: 30,
    regions: ["downtown", "suburbs", "industrial", "residential", "highway"],
  },
}

// Environment-specific overrides
if (process.env.NODE_ENV === "production") {
  config.api.baseUrl = process.env.PRODUCTION_API_URL || config.api.baseUrl
  config.security.cors.origins = process.env.PRODUCTION_ORIGINS?.split(",") || config.security.cors.origins
}

export default config
