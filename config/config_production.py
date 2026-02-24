"""
Enhanced configuration with environment support, secrets management, and feature flags.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from enum import Enum
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Environment(str, Enum):
    """Environment types."""
    DEV = "development"
    STAGING = "staging"
    PROD = "production"
    TEST = "testing"

class Config:
    """Base configuration."""
    
    # Project structure
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    DATA_DIR = PROJECT_ROOT / "data"
    OUTPUT_DIR = PROJECT_ROOT / "outputs"
    LOG_DIR = PROJECT_ROOT / "logs"
    
    # Create directories
    for dir_path in [DATA_DIR, OUTPUT_DIR, LOG_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Environment
    ENVIRONMENT = Environment(os.getenv("ENVIRONMENT", "development"))
    DEBUG = ENVIRONMENT == Environment.DEV
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "json" if ENVIRONMENT != Environment.DEV else "standard"
    LOG_FILE = LOG_DIR / "app.log"
    ERROR_LOG_FILE = LOG_DIR / "errors.log"
    
    # Data paths
    DATA_RAW = DATA_DIR / "raw"
    DATA_PROCESSED = DATA_DIR / "processed"
    DATA_EXTERNAL = DATA_DIR / "external"
    
    OUTPUT_MODELS = OUTPUT_DIR / "models"
    OUTPUT_FEATURES = OUTPUT_DIR / "features"
    OUTPUT_REPORTS = OUTPUT_DIR / "reports"
    OUTPUT_MONITORING = OUTPUT_DIR / "monitoring"
    
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))
    API_WORKERS = int(os.getenv("API_WORKERS", 4))
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", 30))
    API_MAX_CONTENT_LENGTH = int(os.getenv("API_MAX_CONTENT_LENGTH", 16 * 1024 * 1024))  # 16MB
    
    # Database Configuration
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:root@localhost:3306/job_recommendation"
    )
    
    # Redis Configuration (for caching)
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_CACHE_TTL = int(os.getenv("REDIS_CACHE_TTL", 3600))  # 1 hour
    
    # Model Configuration
    MODEL_PARAMS = {
        "n_estimators": int(os.getenv("MODEL_N_ESTIMATORS", 100)),
        "max_depth": int(os.getenv("MODEL_MAX_DEPTH", 6)),
        "learning_rate": float(os.getenv("MODEL_LEARNING_RATE", 0.1)),
        "random_state": 42,
        "verbosity": 0 if ENVIRONMENT == Environment.PROD else 1,
    }
    
    # Feature Engineering
    FEATURES_CONFIG = {
        "use_tfidf": os.getenv("USE_TFIDF", "true").lower() == "true",
        "use_embeddings": os.getenv("USE_EMBEDDINGS", "true").lower() == "true",
        "use_fuzzy_matching": os.getenv("USE_FUZZY_MATCHING", "true").lower() == "true",
        "embedding_model": os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
        "embedding_dim": int(os.getenv("EMBEDDING_DIM", 384)),
    }
    
    # Monitoring
    MONITORING_CONFIG = {
        "enable_drift_detection": os.getenv("ENABLE_DRIFT_DETECTION", "true").lower() == "true",
        "drift_threshold": float(os.getenv("DRIFT_THRESHOLD", 0.1)),
        "metrics_retention_days": int(os.getenv("METRICS_RETENTION_DAYS", 30)),
        "enable_prediction_logging": os.getenv("ENABLE_PREDICTION_LOGGING", "true").lower() == "true",
    }
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    API_KEY_REQUIRED = os.getenv("API_KEY_REQUIRED", "false").lower() == "true"
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Feature Flags
    FEATURE_FLAGS = {
        "enable_batch_predictions": os.getenv("FF_BATCH_PREDICTIONS", "true").lower() == "true",
        "enable_explainability": os.getenv("FF_EXPLAINABILITY", "true").lower() == "true",
        "enable_feedback_loop": os.getenv("FF_FEEDBACK_LOOP", "true").lower() == "true",
        "enable_caching": os.getenv("FF_CACHING", "true").lower() == "true",
        "enable_drift_monitoring": os.getenv("FF_DRIFT_MONITORING", "true").lower() == "true",
    }
    
    # Validation
    VALIDATION_CONFIG = {
        "min_resume_length": int(os.getenv("MIN_RESUME_LENGTH", 50)),
        "max_resume_length": int(os.getenv("MAX_RESUME_LENGTH", 1000000)),
        "min_job_length": int(os.getenv("MIN_JOB_LENGTH", 50)),
        "max_job_length": int(os.getenv("MAX_JOB_LENGTH", 500000)),
    }
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Get all configuration as dictionary."""
        return {
            "environment": cls.ENVIRONMENT.value,
            "debug": cls.DEBUG,
            "api": {
                "host": cls.API_HOST,
                "port": cls.API_PORT,
                "workers": cls.API_WORKERS,
                "timeout": cls.API_TIMEOUT,
            },
            "database": {
                "url": cls.DATABASE_URL[:50] + "..." if len(cls.DATABASE_URL) > 50 else cls.DATABASE_URL,
            },
            "redis": {
                "url": cls.REDIS_URL,
                "cache_ttl": cls.REDIS_CACHE_TTL,
            },
            "model": cls.MODEL_PARAMS,
            "features": cls.FEATURES_CONFIG,
            "monitoring": cls.MONITORING_CONFIG,
            "feature_flags": cls.FEATURE_FLAGS,
        }

class DevelopmentConfig(Config):
    """Development environment configuration."""
    ENVIRONMENT = Environment.DEV
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    API_KEY_REQUIRED = False

class StagingConfig(Config):
    """Staging environment configuration."""
    ENVIRONMENT = Environment.STAGING
    DEBUG = False
    LOG_LEVEL = "INFO"
    API_KEY_REQUIRED = True

class ProductionConfig(Config):
    """Production environment configuration."""
    ENVIRONMENT = Environment.PROD
    DEBUG = False
    LOG_LEVEL = "WARNING"
    API_KEY_REQUIRED = True
    SECRET_KEY = os.getenv("SECRET_KEY")

class TestingConfig(Config):
    """Testing environment configuration."""
    ENVIRONMENT = Environment.TEST
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    DATABASE_URL = "sqlite:///:memory:"
    REDIS_URL = "redis://localhost:6379/1"

# Config factory
_config_map = {
    Environment.DEV: DevelopmentConfig,
    Environment.STAGING: StagingConfig,
    Environment.PROD: ProductionConfig,
    Environment.TEST: TestingConfig,
}

def get_config() -> Config:
    """Get appropriate config based on environment."""
    env = Environment(os.getenv("ENVIRONMENT", "development"))
    return _config_map[env]()

# Export default config
config = get_config()
