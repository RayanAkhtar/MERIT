from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
import os
from core.service.upload_service import handle_file_upload, get_file_link_counts
from core.parsers.job_description import parse_jd, parse_job
from core.supabase import supabase

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

@api_bp.route("/extract-job-requirements", methods=["POST"])
def extract_job_requirements():
    """Handle extraction and structuring of Job Requirements"""
    files = request.files.getlist('files') if 'files' in request.files else []
    text = request.form.get('text', '').strip()
    
    if not files and not text:
        return jsonify({"error": "No files or text provided"}), 400

    results = []

    # Process text input
    if text:
        parsed_text = parse_job(text, source_file="manual_input")
        results.append(parsed_text)

    # Process file inputs
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            try:
                parsed_file = parse_jd(filepath)
                if isinstance(parsed_file, list):
                    results.extend(parsed_file)
                else:
                    results.append(parsed_file)
            finally:
                # Cleanup if needed or keep for reference
                pass

    if not results:
        return jsonify({"error": "No data could be extracted"}), 422

    # For now, if multiple sources are provided, we merge them or return the first
    # The frontend expects a single structured job object
    combined = results[0] # Simplistic merge for now
    
    # Map backend fields to frontend expected format following user request
    formatted_metrics = []
    
    # 1. Location
    if combined.get("location"):
        formatted_metrics.append({"id": os.urandom(4).hex(), "label": "Location", "value": combined["location"], "category": "General"})
    
    # 2. Job Type
    if combined.get("employment_type"):
        formatted_metrics.append({"id": os.urandom(4).hex(), "label": "Job Type", "value": combined["employment_type"], "category": "General"})

    # 3. Languages
    for s in combined.get("languages", []):
        formatted_metrics.append({"id": os.urandom(4).hex(), "label": "Language", "value": s, "subValue": "3+ years", "category": "Languages"})
    
    # 4. Technologies
    for s in combined.get("technical_skills", []):
        formatted_metrics.append({"id": os.urandom(4).hex(), "label": "Technology", "value": s, "category": "Technologies"})
        
    # 5. Experience
    for s in combined.get("experience_required", []):
        formatted_metrics.append({"id": os.urandom(4).hex(), "label": "Required Experience", "value": s, "category": "Experience"})
        
    # 6. Education
    for s in combined.get("education_required", []):
        formatted_metrics.append({"id": os.urandom(4).hex(), "label": "Degree", "value": s, "category": "Education"})
        
    # 7. Soft Skills
    for s in combined.get("soft_skills", []):
        formatted_metrics.append({"id": os.urandom(4).hex(), "label": "Soft Skill", "value": s, "category": "Soft Skills"})

    response_data = {
        "title": combined.get("job_title") or "Extracted Role",
        "description": combined.get("raw_text")[:500] + "..." if len(combined.get("raw_text", "")) > 500 else combined.get("raw_text", ""),
        "metrics": formatted_metrics
    }

    return jsonify(response_data), 200

@api_bp.route("/save-job-requirements", methods=["POST"])
def save_job_requirements():
    """Save finalized Job Requirements to Supabase"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        title = data.get("title")
        description = data.get("description")
        metrics = data.get("metrics")

        if not title or not metrics:
            return jsonify({"error": "Title and Metrics are required fields"}), 400

        # Insert into Supabase
        if not supabase:
             return jsonify({"error": "Database connection not established"}), 500

        response = supabase.table("job_requirements").insert({
            "title": title,
            "description": description,
            "metrics": metrics
        }).execute()

        return jsonify({"success": True, "data": response.data}), 201

    except Exception as e:
        print(f"ERROR saving job requirements: {str(e)}")
        return jsonify({"error": f"Failed to save to database: {str(e)}"}), 500

