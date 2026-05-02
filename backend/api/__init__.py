from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

from .general.routes import general_bp
from .extraction.routes import extraction_bp
from .job_descriptions.routes import job_descriptions_bp
from .candidates.routes import candidates_bp
from .config.routes import config_bp
from .ranking.routes import ranking_bp
from .system.routes import system_bp

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(general_bp, url_prefix="/api")
    app.register_blueprint(extraction_bp, url_prefix="/api")
    app.register_blueprint(job_descriptions_bp, url_prefix="/api")
    app.register_blueprint(candidates_bp, url_prefix="/api")
    app.register_blueprint(config_bp, url_prefix="/api")
    app.register_blueprint(ranking_bp, url_prefix="/api")
    app.register_blueprint(system_bp, url_prefix="/api")

    @app.errorhandler(Exception)
    def handle_exception(e):
        # global error handler for all unhandled exceptions
        # print(f"DEBUG: ERROR - {str(e)}")
        # Log the error (optional, could use app.logger)
        response = {
            "error": str(e),
            "type": e.__class__.__name__,
            "message": "An internal server error occurred."
        }
        return response, 500

    return app
