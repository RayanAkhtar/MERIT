from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
import os

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
    
    if not files or files[0].filename == '':
        return jsonify({"error": "No files selected"}), 400
    
    uploaded_files = []
    errors = []
    
    for file in files:
        if file and allowed_file(file.filename):
            
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            # prevent duplicates
            counter = 1
            base_name, ext = os.path.splitext(filename)
            while os.path.exists(filepath):
                filename = f"{base_name}_{counter}{ext}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                counter += 1
            
            try:
                file.save(filepath)
                uploaded_files.append(filename)
            except Exception as e:
                errors.append(f"Failed to save {file.filename}: {str(e)}")
        else:
            errors.append(f"{file.filename} is not a valid PDF or DOCX file")
    
    if uploaded_files:
        response = {
            "uploaded": len(uploaded_files),
            "files": uploaded_files
        }
        if errors:
            response["errors"] = errors
        return jsonify(response), 200
    else:
        return jsonify({
            "error": "No files were uploaded",
            "errors": errors
        }), 400
