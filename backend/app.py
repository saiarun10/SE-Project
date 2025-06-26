from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from config import get_config
from model import db
from routes.auth import auth_bp
from datetime import date
from flask.json.provider import DefaultJSONProvider
import json

class CustomJSONProvider(DefaultJSONProvider):
    """Custom JSON provider to handle date objects"""
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)

def create_app():
    app = Flask(__name__)
    config_class = get_config()
    app.config.from_object(config_class)
    
    # Set custom JSON provider
    app.json = CustomJSONProvider(app)
    
    # Initialize logging
    config_class.init_logging()

    # Configure CORS
    CORS(app, resources={r"/*": {"origins": app.config['FRONTEND_URL']}})

    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    
    # Configure Swagger with security definitions
    swagger_config = {
        "swagger": "2.0",
        "title": "API Documentation",
        "uiversion": 3,
        "specs": [
            {
                "endpoint": "apispec_1",
                "route": "/apispec_1.json"
            }
        ],
        "securityDefinitions": {
            "JWT": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "Enter JWT token with 'Bearer <token>' format"
            }
        }
    }
    Swagger(app, template=swagger_config)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api')

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)