"""Configuration module for MyFluence application.

Loads configuration from environment variables with sensible defaults.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

# MongoDB Configuration
MONGODB_HOST = os.getenv('MONGODB_HOST', 'localhost')
MONGODB_PORT = os.getenv('MONGODB_PORT', '27017')
MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'myfluence')
MONGODB_USERNAME = os.getenv('MONGODB_USERNAME', '')
MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD', '')

# Build MongoDB URI
# FIXME: Make this able to handle MongoDB Atlast (mongodb+srv) URI gracefully 
if MONGODB_USERNAME and MONGODB_PASSWORD:
    MONGODB_URI = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOST}/"
else:
    MONGODB_URI = f"mongodb://{MONGODB_HOST}:{MONGODB_PORT}/"

# Project Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = Path(__file__).parent / 'data'
VIDEOS_DIR = DATA_DIR / 'videos'
METRICS_DIR = DATA_DIR / 'metrics'
SENTIMENT_DIR = DATA_DIR / 'sentiment'
INFO_DIR = DATA_DIR / 'info'
STATS_DIR = DATA_DIR / 'stats'
OUTPUT_DIR = PROJECT_ROOT / 'output'

# Application Configuration
DEFAULT_COUNTRY = os.getenv('DEFAULT_COUNTRY', 'ID')

def get_mongodb_uri() -> str:
    """Get the configured MongoDB URI."""
    return MONGODB_URI

def get_mongodb_database() -> str:
    """Get the configured MongoDB database name."""
    return MONGODB_DATABASE
