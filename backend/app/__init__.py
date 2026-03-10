from flask import Flask
from flask_cors import CORS
from app.config import Config 
from app.extensions import init_extensions, celery
from app.blueprints import register_blueprints

def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    init_extensions(app)
    register_blueprints(app)

    CORS(app, resources = {r"/api/*": {
        "origins": [
            "http://localhost:8080",
            "http://127.0.0.1:8080",
            "http://172.24.78.93:8080"
        ]
    }},
    supports_credentials=True)
    
    return app 
