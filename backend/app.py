from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import get_config
from model import db
from api_utils import CustomJSONProvider
from routes.auth import auth_ns
from routes.profile import profile_ns
from routes.lesson import lesson_ns
from routes.module import module_ns
from routes.topic import topic_ns
from routes.quiz import quiz_ns
from swagger_setup import configure_swagger  # Import Swagger configuration
# Import other namespaces as needed
# from routes.learn import learn_ns
# from routes.quiz import quiz_ns

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

    # Initialize Flask-RESTx with Swagger configuration
    api = configure_swagger(app)

    # Register namespaces
    api.add_namespace(auth_ns, path='/api')
    api.add_namespace(profile_ns, path='/api')
    api.add_namespace(lesson_ns, path='/api')
    api.add_namespace(module_ns, path='/api')
    api.add_namespace(topic_ns, path='/api')
    api.add_namespace(quiz_ns, path='/api')
    # Add other namespaces as needed
    # api.add_namespace(learn_ns, path='/api')
    # api.add_namespace(quiz_ns, path='/api')

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)