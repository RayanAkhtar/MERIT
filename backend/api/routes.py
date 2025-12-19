from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
import os
from core.service.upload_service import handle_file_upload, get_file_link_counts

# TODO
#    1. Structure this better since there will be more endpoints as it grows

api_bp = Blueprint("api", __name__)

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'} # Just cv files

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@api_bp.route("/upload", methods=["POST"])
def upload_files():
    """Handle multiple file uploads"""
    if 'files' not in request.files:
        return jsonify({"error": "No files provided"}), 400

    files = request.files.getlist('files')
    return jsonify(*handle_file_upload(files))

@api_bp.route("/supporting-links-metrics", methods=["GET"])
def file_link_counts():
    """API endpoint to get file link counts"""
    link_summary = get_file_link_counts()
    return jsonify(link_summary), 200
