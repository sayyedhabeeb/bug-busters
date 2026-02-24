# Configuration settings for Job Recommendation System

import os
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# Data paths
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_EXTERNAL = PROJECT_ROOT / "data" / "external"

# Output paths
OUTPUTS_ROOT = PROJECT_ROOT / "outputs"
OUTPUT_MODELS = OUTPUTS_ROOT / "models"
OUTPUT_REPORTS = OUTPUTS_ROOT / "reports"
OUTPUT_FEATURES = OUTPUTS_ROOT / "features"

# Model settings
MODEL_PARAMS = {
    "n_estimators": 100,
    "max_depth": 6,
    "learning_rate": 0.1,
    "random_state": 42
}

# Feature settings
USE_TF_IDF = True
USE_EMBEDDINGS = True
USE_FUZZY_MATCHING = True

# API settings
API_HOST = "0.0.0.0"
API_PORT = 5000
DEBUG = False

# Logging
LOG_LEVEL = "INFO"
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
