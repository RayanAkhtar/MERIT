from flask import Blueprint, jsonify, request
from core.service.upload_service import handle_file_upload, get_file_link_counts

general_bp = Blueprint("general", __name__)

@general_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@general_bp.route("/upload", methods=["POST"])
def upload_files():
    """Handle multiple file uploads"""
    if 'files' not in request.files:
        return jsonify({"error": "No files provided"}), 400

    files = request.files.getlist('files')
    return jsonify(*handle_file_upload(files))

@general_bp.route("/supporting-links-metrics", methods=["GET"])
def file_link_counts():
    """API endpoint to get file link counts"""
    link_summary = get_file_link_counts()
    return jsonify(link_summary), 200
