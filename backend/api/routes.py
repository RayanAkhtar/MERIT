from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
import os
from core.service.upload_service import handle_file_upload, get_file_link_counts
from core.parsers.job_description import parse_jd, parse_job
from core.supabase import supabase


api_bp = Blueprint("api", __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'md'}

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
    custom_title = request.form.get('title', '').strip()
    
    if not files and not text:
        return jsonify({"error": "No files or text provided"}), 400

    results = []

    # Process text input
    if text:
        meta = {"job_title": custom_title} if custom_title else None
        parsed_text = parse_job(text, source_file="manual_input", meta=meta)
        results.append(parsed_text)

    # Process file inputs
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            try:
                meta = {"job_title": custom_title} if custom_title else None
                parsed_file = parse_jd(filepath, meta=meta)
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
    
    # 1. Basic Info
    if combined.get("company"):
        formatted_metrics.append({"id": os.urandom(4).hex(), "label": "Company", "value": combined["company"], "category": "General"})
    if combined.get("job_title"):
        formatted_metrics.append({"id": os.urandom(4).hex(), "label": "Job Role", "value": combined["job_title"], "category": "General"})

    # 2. Location
    if combined.get("location"):
        formatted_metrics.append({"id": os.urandom(4).hex(), "label": "Location", "value": combined["location"], "category": "General"})
    
    # 3. Job Type & Level
    if combined.get("employment_type"):
        formatted_metrics.append({"id": os.urandom(4).hex(), "label": "Job Type", "value": combined["employment_type"], "category": "General"})
    if combined.get("experience_level"):
        formatted_metrics.append({"id": os.urandom(4).hex(), "label": "Experience Level", "value": combined["experience_level"], "category": "General"})

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

    # 8. Responsibilities
    for s in combined.get("responsibilities", []):
        formatted_metrics.append({"id": os.urandom(4).hex(), "label": "Duty", "value": s, "category": "Responsibilities"})

    # 9. Requirements (Generic)
    for s in combined.get("requirements", []):
        formatted_metrics.append({"id": os.urandom(4).hex(), "label": "Requirement", "value": s, "category": "Requirements"})

    company = combined.get("company")
    job_title = combined.get("job_title")
    display_title = f"{company} - {job_title}" if company and job_title else (job_title or company or "Extracted Role")

    response_data = {
        "title": display_title,
        "description": combined.get("raw_text", ""),
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

        # Define category structures: 'list' (flat string array) vs 'key-value' (label-value objects)
        list_type_cats = ["Languages", "Technologies", "Soft Skills", "Responsibilities", "Requirements", "Education"]
        
        # Group and structure metrics by category
        grouped_metrics = {}
        for m in metrics:
            cat = m.get("category", "General")
            val = m.get("value", "")
            lbl = m.get("label", "")
            
            if cat not in grouped_metrics:
                # Initialize category structure
                cat_type = "list" if cat in list_type_cats else "key-value"
                grouped_metrics[cat] = {
                    "type": cat_type,
                    "value": []
                }
            
            if grouped_metrics[cat]["type"] == "list":
                # For list sections, extract plain string
                if val: grouped_metrics[cat]["value"].append(val)
            else:
                # For key-value sections, preserve label-value pair (cleaned)
                item = {k: v for k, v in m.items() if k != 'category'}
                grouped_metrics[cat]["value"].append(item)

        response = supabase.table("job_requirements").insert({
            "title": title,
            "description": description,
            "metrics": grouped_metrics
        }).execute()

        return jsonify({"success": True, "data": response.data}), 201

    except Exception as e:
        print(f"ERROR saving job requirements: {str(e)}")
        return jsonify({"error": f"Failed to save to database: {str(e)}"}), 500

