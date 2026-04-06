from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

from .general.routes import general_bp
from .extraction.routes import extraction_bp
from .job_requirements.routes import job_reqs_bp
from .candidates.routes import candidates_bp

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(general_bp, url_prefix="/api")
    app.register_blueprint(extraction_bp, url_prefix="/api")
    app.register_blueprint(job_reqs_bp, url_prefix="/api")
    app.register_blueprint(candidates_bp, url_prefix="/api")

    return app
