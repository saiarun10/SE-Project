# config.py
import os
from dotenv import load_dotenv
from datetime import timedelta

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
    SECRET_KEY = os.environ.get("SECRET_KEY", "a-default-secret-key")
    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT", "a-default-salt")
   
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "a-default-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 1)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.environ.get("JWT_REFRESH_TOKEN_EXPIRES", 1)))

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", "false").lower() == "true"
    
    # Groq API Key
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    
    # Frontend URL for CORS
    FRONTEND_URL = os.getenv("FRONTEND_URL")
    

class DevelopmentConfig(Config):
    """Development Configuration"""
    DEBUG = True

class TestingConfig(Config):
    """Testing Configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False 

class ProductionConfig(Config):
    """Production Configuration"""
    DEBUG = False
    WTF_CSRF_ENABLED = True  

# Configuration selector based on environment
def get_config():
    env = os.getenv("FLASK_ENV", "development").lower()
    if env == "production":
        return ProductionConfig
    # The conftest.py will set TESTING=True, but we can also select by an env var
    if env == "testing" or os.environ.get('TESTING'):
        return TestingConfig
    return DevelopmentConfig
