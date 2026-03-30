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

@api_bp.route("/save-cvs", methods=["POST"])
def save_cvs():
    """Attempt to save multiple CVs. Returns error as it's not implemented yet."""
    if 'files' not in request.files or not request.files.getlist('files'):
        return jsonify({"error": "No files provided"}), 400
    return jsonify({"error": "Saving CVs is not implemented yet."}), 501

@api_bp.route("/save-job-requirements", methods=["POST"])
def save_job_requirements():
    """Attempt to save Job Requirements. Returns error as it's not implemented yet."""
    has_files = 'files' in request.files and request.files.getlist('files')
    has_text = 'text' in request.form and request.form.get('text', '').strip()
    
    if not has_files and not has_text:
        return jsonify({"error": "No files or text provided for Job Requirements"}), 400
        
    return jsonify({"error": "Saving Job Requirements is not implemented yet."}), 501

