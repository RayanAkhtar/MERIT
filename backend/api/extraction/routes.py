from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
import os
from core.parsers.job_description import parse_jd, parse_job

extraction_bp = Blueprint("extraction", __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'md'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@extraction_bp.route("/extract-job-requirements", methods=["POST"])
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
                pass

    if not results:
        return jsonify({"error": "No data could be extracted"}), 422

    combined = results[0]
    formatted_metrics = []
    
    # Mapping logic
    if combined.get("company"):
        formatted_metrics.append({"id": os.urandom(4).hex(), "label": "Company", "value": combined["company"], "category": "General"})
    if combined.get("job_title"):
        formatted_metrics.append({"id": os.urandom(4).hex(), "label": "Job Role", "value": combined["job_title"], "category": "General"})
    if combined.get("location"):
        formatted_metrics.append({"id": os.urandom(4).hex(), "label": "Location", "value": combined["location"], "category": "General"})
    if combined.get("employment_type"):
        formatted_metrics.append({"id": os.urandom(4).hex(), "label": "Job Type", "value": combined["employment_type"], "category": "General"})
    if combined.get("experience_level"):
        formatted_metrics.append({"id": os.urandom(4).hex(), "label": "Experience Level", "value": combined["experience_level"], "category": "General"})

    for s in combined.get("languages", []):
        formatted_metrics.append({"id": os.urandom(4).hex(), "label": "Language", "value": s, "category": "Languages"})
    for s in combined.get("technical_skills", []):
        formatted_metrics.append({"id": os.urandom(4).hex(), "label": "Technology", "value": s, "category": "Technologies"})
    for s in combined.get("experience_required", []):
        formatted_metrics.append({"id": os.urandom(4).hex(), "label": "Required Experience", "value": s, "category": "Experience"})
    for s in combined.get("education_required", []):
        formatted_metrics.append({"id": os.urandom(4).hex(), "label": "Degree", "value": s, "category": "Education"})
    for s in combined.get("soft_skills", []):
        formatted_metrics.append({"id": os.urandom(4).hex(), "label": "Soft Skill", "value": s, "category": "Soft Skills"})
    for s in combined.get("responsibilities", []):
        formatted_metrics.append({"id": os.urandom(4).hex(), "label": "Duty", "value": s, "category": "Responsibilities"})
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
