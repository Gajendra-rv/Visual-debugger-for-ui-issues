import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "cnn-debugger-secret-2026-change-in-prod")
    DATABASE = os.path.join(BASE_DIR, "instance", "debugger.db")
    SCHEMA = os.path.join(BASE_DIR, "app", "database", "schema.sql")
    
    # Uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "static", "uploads")
    HEATMAP_FOLDER = os.path.join(BASE_DIR, "app", "static", "heatmaps")
    REPORT_FOLDER = os.path.join(BASE_DIR, "app", "static", "reports")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # ML Model
    MODEL_PATH = os.path.join(BASE_DIR, "app", "static", "models", "ui_bug_detector.keras")
    IMG_SIZE = (224, 224)
    CONFIDENCE_THRESHOLD = 0.5

    # Selenium
    CHROME_HEADLESS = True
    SCREENSHOT_TIMEOUT = 30

    # Logging
    LOG_FILE = os.path.join(BASE_DIR, "logs", "app.log")
    LOG_LEVEL = "DEBUG"

    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = "WARNING"
    SECRET_KEY = os.environ.get("SECRET_KEY")


class TestingConfig(Config):
    TESTING = True
    DATABASE = os.path.join(BASE_DIR, "instance", "test_debugger.db")


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
