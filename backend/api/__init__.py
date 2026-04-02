from flask import Flask
from flask_cors import CORS
from .general.routes import general_bp
from .extraction.routes import extraction_bp
from .job_requirements.routes import job_reqs_bp

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Register blueprints under the /api prefix
    app.register_blueprint(general_bp, url_prefix="/api")
    app.register_blueprint(extraction_bp, url_prefix="/api")
    app.register_blueprint(job_reqs_bp, url_prefix="/api")

    return app
