# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration"""
    DEBUG = False
    TESTING = False



    # Logging Configuration
    try:
        LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
        LOG_FILE = os.environ.get("LOG_FILE", "app.log")
        LOG_FORMAT = os.environ.get("LOG_FORMAT", "%(asctime)s - %(levelname)s - %(message)s")
    except KeyError as e:
        raise KeyError(f"Missing required environment variable: {e}")   
    @staticmethod
    def init_logging():
        import logging
        from logging.handlers import RotatingFileHandler

        log_level = getattr(logging, Config.LOG_LEVEL, logging.INFO)
        logging.basicConfig(level=log_level, format=Config.LOG_FORMAT)

        # Create a file handler for logging
        file_handler = RotatingFileHandler(Config.LOG_FILE, maxBytes=1000000, backupCount=5)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(Config.LOG_FORMAT))
        
        # Add the file handler to the root logger
        logging.getLogger().addHandler(file_handler)        

    # General Config
    try:
        SECRET_KEY = os.environ["SECRET_KEY"]
        SECURITY_PASSWORD_SALT = os.environ["SECURITY_PASSWORD_SALT"]
    except KeyError as e:
        raise KeyError(f"Missing required environment variable: {e}")
   
    try:
        # JWT Configuration
        JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
        JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 3600))  # Default to 1 hour
        JWT_REFRESH_TOKEN_EXPIRES = int(os.environ.get("JWT_REFRESH_TOKEN_EXPIRES", 86400))  # Default to 24 hours
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
