from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from config import get_config
from model import db
from swagger_config import swagger_config
from api_utils import CustomJSONProvider
from routes.auth import auth_bp
from flask_jwt_extended import JWTManager

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

    JWTManager(app)
    # Initialize Swagger
    Swagger(app, template=swagger_config)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api')

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)