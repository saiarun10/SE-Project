# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration"""
    DEBUG = False
    TESTING = False

    # General Config
    try:
        SECRET_KEY = os.environ["SECRET_KEY"]
        SECURITY_PASSWORD_SALT = os.environ["SECURITY_PASSWORD_SALT"]
    except KeyError as e:
        raise KeyError(f"Missing required environment variable: {e}")

    # Database
    try:
        SQLALCHEMY_DATABASE_URI = os.environ["SQLALCHEMY_DATABASE_URI"]
        SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", "false").lower() == "true"
    except KeyError as e:
        raise KeyError(f"Missing required environment variable: {e}")

    try:
        # Frontend URL for CORS
        FRONTEND_URL = os.getenv("FRONTEND_URL")
    except KeyError as e:
        raise KeyError(f"Missing required environment variable: {e}")
    

class DevelopmentConfig(Config):
    """Development Configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production Configuration"""
    DEBUG = False
    WTF_CSRF_ENABLED = True  

# Configuration selector based on environment
def get_config():
    env = os.getenv("FLASK_ENV", "development").lower()
    if env == "production":
        return ProductionConfig
    return DevelopmentConfig
