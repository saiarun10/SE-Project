# /app.py
from flask import Flask
from flask_cors import CORS
from config import get_config
from model import db


def create_app():
    app = Flask(__name__)
    config_class = get_config()
    app.config.from_object(config_class)
    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

    # Initialize extensions
    db.init_app(app)

    return app

app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
