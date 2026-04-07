from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
import os
from core.parsers.job_description import parse_jd, parse_job
from core.parsers.cv import parse_cv
from core.parsers.registry import datasource_registry
from core.utils.cache import get_cached_data, save_to_cache
from core.supabase import supabase
import hashlib

extraction_bp = Blueprint("extraction", __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'md'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@extraction_bp.route("/extract-job-description", methods=["POST"])
def extract_job_description():
    """Handle extraction and structuring of Job Descriptions"""
    text = request.form.get('text', '').strip()
    custom_title = request.form.get('title', '').strip()
    file = request.files.get('file')
    cache_enabled = request.form.get('cache_data', 'false').lower() == 'true'
    
    if not file and not text:
        return jsonify({"error": "No files or text provided"}), 400

    # caching check for job requirements
    content_hash = ""
    if file:
        file.seek(0)
        content_hash = hashlib.md5(file.read()).hexdigest()
        file.seek(0)
    else:
        content_hash = hashlib.md5(text.encode()).hexdigest()

    if cache_enabled:
        cached = get_cached_data("job_desc", content_hash)
        if cached:
            cached["cached"] = True
            return jsonify(cached), 200

    results = []

    # preference for file JD over text JD
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        meta = {"job_title": custom_title} if custom_title else None
        parsed_file = parse_jd(filepath, meta=meta)

        if isinstance(parsed_file, list):
            results = parsed_file
        else:
            results = [parsed_file]
    elif text:
        meta = {"job_title": custom_title} if custom_title else None
        parsed_text = parse_job(text, source_file="manual_input", meta=meta)
        results = [parsed_text]

    if not results:
        return jsonify({"error": "No data could be extracted"}), 422

    combined = results[0]
    formatted_metrics = []
    
    # should probably change the way this is done later, but not too big an issue for now
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
        "metrics": formatted_metrics,
        "cached": False
    }

    if cache_enabled:
        save_to_cache("job_desc", content_hash, response_data)

    return jsonify(response_data), 200

@extraction_bp.route("/extract-cv", methods=["POST"])
def extract_cv():
    """Handle extraction and structuring of a single CV"""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    cache_enabled = request.form.get('cache_data', 'false').lower() == 'true'
    
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        with open(filepath, 'rb') as f:
            file_content = f.read()
            cache_id = hashlib.md5(file_content).hexdigest()

        if cache_enabled:
            cached_res = get_cached_data("cv", cache_id)
            if cached_res and cached_res.get("cv_url"):
                cached_res["cached"] = True
                cached_res["file_id"] = cache_id
                return jsonify(cached_res), 200
            elif cached_res:
                # if cached but no cv_url, we keep the parsed data but proceed to upload
                parsed_data = cached_res
            else:
                parsed_data = parse_cv(filepath)
        else:
            parsed_data = parse_cv(filepath)
            
        parsed_data["cached"] = False
        parsed_data["file_id"] = cache_id
        
        # uploading CV to Supabase Storage
        cv_url = None
        if supabase:
            try:
                supabase.storage.create_bucket('cvs', options={'public': True})

                # uploading file
                storage_path = f"{cache_id}_{filename}"
                with open(filepath, 'rb') as f:
                    supabase.storage.from_('cvs').upload(
                        path=storage_path,
                        file=f,
                        file_options={"content-type": file.content_type}
                    )
                
                # getting public URL
                cv_url = supabase.storage.from_('cvs').get_public_url(storage_path)
            except Exception as e:
                print(f"Warning: Failed to upload CV to storage: {str(e)}")

        parsed_data["cv_url"] = cv_url

        if cache_enabled:
            save_to_cache("cv", cache_id, parsed_data)

        return jsonify(parsed_data), 200
    
    return jsonify({"error": "Invalid file type"}), 400

@extraction_bp.route("/scan-datasource", methods=["POST"])
def scan_datasource():
    """Generic endpoint to scan any supported data source"""
    source_type = request.json.get('source_type')
    url = request.json.get('url')
    cache_enabled = request.json.get('cache_data', False)
    
    if not source_type or not url:
        return jsonify({"error": "Missing source_type or url"}), 400
        
    if cache_enabled:
        cached = get_cached_data(source_type, url)
        if cached:
            cached["cached"] = True
            return jsonify(cached), 200
    
    try:
        source = datasource_registry.get_source(source_type)
        data = source.process(url)
        data["cached"] = False
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Enrichment failed: {str(e)}"}), 500
    
    if cache_enabled:
        save_to_cache(source_type, url, data)
        
    return jsonify(data), 200
