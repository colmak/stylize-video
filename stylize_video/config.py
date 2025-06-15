"""Configuration settings and constants for the stylize-video tool."""

import os
from pathlib import Path

# Default settings
DEFAULT_FPS = 30
DEFAULT_RESIZE = 512
DEFAULT_BACKEND = "local"
DEFAULT_MODEL = "mosaic"

# Supported models and their properties
SUPPORTED_MODELS = {
    "mosaic": {
        "type": "feedforward",
        "source": "local",
        "description": "Mosaic painting style",
        "url": None  # Use random initialization for now
    },
    "candy": {
        "type": "feedforward", 
        "source": "local",
        "description": "Candy art style",
        "url": None  # Use random initialization for now
    },
    "rain_princess": {
        "type": "feedforward",
        "source": "local", 
        "description": "Rain Princess style",
        "url": None  # Use random initialization for now
    },
    "udnie": {
        "type": "feedforward",
        "source": "local",
        "description": "Udnie style",
        "url": None  # Use random initialization for now
    },
    "animegan": {
        "type": "gan",
        "source": "local",
        "description": "Anime look",
        "url": None  # Use random initialization for now
    },
    "cartoon": {
        "type": "gan",
        "source": "local", 
        "description": "Cartoon filter",
        "url": None  # Use random initialization for now
    }
}

# Supported backends
SUPPORTED_BACKENDS = ["local", "colab", "runpod", "docker"]

# File paths
PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / "models" / "checkpoints"
TEMP_DIR = PROJECT_ROOT / "temp"
PRESETS_DIR = PROJECT_ROOT / "presets"

# Create directories if they don't exist
MODELS_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Video processing settings
SUPPORTED_VIDEO_FORMATS = [".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv"]
SUPPORTED_IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]

# Logging configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"
