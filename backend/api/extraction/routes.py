from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
import os
from core.parsers.job_description import parse_jd, parse_job
from core.parsers.cv import parse_cv
from core.parsers.registry import datasource_registry
from core.utils.cache import get_cached_data, save_to_cache
from core.supabase import supabase, SUPABASE_URL
import hashlib

extraction_bp = Blueprint("extraction", __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'md'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    # check if file extension is allowed
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@extraction_bp.route("/extract-job-description", methods=["POST"])
def extract_job_description():
    text = request.form.get('text', '').strip()
    custom_title = request.form.get('title', '').strip()
    file = request.files.get('file')
    cache_enabled = request.form.get('cache_data', 'false').lower() == 'true'
    
    if not file and not text:
        return jsonify({"error": "No files or text provided"}), 400

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
            # print("DEBUG: found cache jd")
            cached["cached"] = True
            return jsonify(cached), 200

    results = []

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

    # build a nice title for the UI
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
            cached_url = cached_res.get("cv_url") if cached_res else None
            
            # only return early if we have a cloud url (not a local fallback)
            if cached_res and cached_url and not cached_url.startswith("http://localhost"):
                cached_res["cached"] = True
                cached_res["file_id"] = cache_id
                cached_res["cv_hash"] = cache_id
                return jsonify(cached_res), 200
            elif cached_res:
                print("DEBUG: Cached CV is local-only or missing URL. Attempting cloud upgrade...")
                parsed_data = cached_res
            else:
                # if it's not in the local cache, check the database to see if we've seen this hash before
                db_res = supabase.table("candidate_data").select("""
                    *,
                    github_profile:github_profiles(*, github_projects(*)),
                    linkedin_profile:linkedin_profiles(*, 
                        linkedin_experience(*), 
                        linkedin_education(*)
                    )
                """).eq("cv_hash", cache_id).execute()
                
                if db_res.data:
                    existing = db_res.data[0]
                    # map the database fields back to the format the extraction engine expects
                    parsed_data = {
                        "name": existing.get("name"),
                        "email": existing.get("email"),
                        "phone": existing.get("phone"),
                        "skills": existing.get("skills", []),
                        "experience": existing.get("experience_summary"),
                        "cv_experience": existing.get("cv_experience", []),
                        "projects": existing.get("projects_history", []),
                        "extracurricular": existing.get("extracurricular", []),
                        "cv_url": existing.get("cv_url"),
                        "cv_hash": cache_id,
                        "file_id": cache_id,
                        "cached": True,
                        "reused_from_db": True
                    }
                    
                    # if we already have the profile data, just grab it so we don't have to scan again
                    gh_profile = existing.get("github_profile")
                    if gh_profile:
                        # shove it into the format the frontend and scoring engine expect
                        parsed_data["github_enriched"] = gh_profile
                        parsed_data["github_enriched"]["language_history"] = gh_profile.get("language_history", [])
                        all_projects = gh_profile.get("github_projects", [])
                        
                        # split out the starred projects from the rest of the repos
                        parsed_data["github_enriched"]["featured_projects"] = [
                            {
                                "name": p["name"],
                                "description": p["description"],
                                "url": p["url"],
                                "stars": p["stars"],
                                "type": "Repository", # lazy default
                                "top_languages": [p["language"]] if p["language"] else []
                            }
                            for p in all_projects if p.get("is_featured")
                        ]
                        parsed_data["github_enriched"]["repositories"] = [
                            {
                                "name": p["name"],
                                "description": p["description"],
                                "url": p["url"],
                                "stars": p["stars"],
                                "language": p["language"]
                            }
                            for p in all_projects
                        ]
                        # make sure languages list isn't null or it'll crash later
                        if "languages" not in parsed_data["github_enriched"] or parsed_data["github_enriched"]["languages"] is None:
                            parsed_data["github_enriched"]["languages"] = []
                        
                        # frontend wants 'created_at' but the db uses 'created_at_platform'
                        if gh_profile.get("created_at_platform"):
                            parsed_data["github_enriched"]["created_at"] = gh_profile["created_at_platform"]
                    if li_profile:
                        # Map to the format scan-datasource returns
                        parsed_data["linkedin_enriched"] = li_profile
                        parsed_data["linkedin_enriched"]["experience"] = li_profile.get("linkedin_experience", [])
                        parsed_data["linkedin_enriched"]["education"] = li_profile.get("linkedin_education", [])
                    
                    # Also need education records
                    edu_res = supabase.table("candidate_education").select("*").eq("candidate_id", existing["id"]).execute()
                    parsed_data["education"] = [
                        {"name": e["school_name"], "subtitle": e["degree"], "grade": e["grade"], "start_date": e["start_date"], "end_date": e["end_date"]}
                        for e in edu_res.data
                    ]
                    # Also need source links
                    parsed_data["links"] = existing.get("source_links", {})
                    
                    return jsonify(parsed_data), 200
                
                parsed_data = parse_cv(filepath)
        else:
            # check the database to see if we've seen this hash before (even if cache is disabled)
            db_res = supabase.table("candidate_data").select("""
                *,
                github_profile:github_profiles(*, github_projects(*)),
                linkedin_profile:linkedin_profiles(*, 
                    linkedin_experience(*), 
                    linkedin_education(*)
                )
            """).eq("cv_hash", cache_id).execute()
            
            if db_res.data:
                 # Reuse logic same as above...
                 existing = db_res.data[0]
                 parsed_data = {
                    "name": existing.get("name"),
                    "email": existing.get("email"),
                    "phone": existing.get("phone"),
                    "skills": existing.get("skills", []),
                    "experience": existing.get("experience_summary"),
                    "cv_experience": existing.get("cv_experience", []),
                    "projects": existing.get("projects_history", []),
                    "extracurricular": existing.get("extracurricular", []),
                    "cv_url": existing.get("cv_url"),
                    "cv_hash": cache_id,
                    "file_id": cache_id,
                    "cached": True,
                    "reused_from_db": True
                }
                 
                 gh_profile = existing.get("github_profile")
                 if gh_profile:
                     parsed_data["github_enriched"] = gh_profile
                     parsed_data["github_enriched"]["language_history"] = gh_profile.get("language_history", [])
                     all_projects = gh_profile.get("github_projects", [])
                     
                     parsed_data["github_enriched"]["featured_projects"] = [
                         {
                             "name": p["name"],
                             "description": p["description"],
                             "url": p["url"],
                             "stars": p["stars"],
                             "type": "Repository",
                             "top_languages": [p["language"]] if p["language"] else []
                         }
                         for p in all_projects if p.get("is_featured")
                     ]
                     parsed_data["github_enriched"]["repositories"] = [
                         {
                             "name": p["name"],
                             "description": p["description"],
                             "url": p["url"],
                             "stars": p["stars"],
                             "language": p["language"]
                         }
                         for p in all_projects
                     ]
                     if "languages" not in parsed_data["github_enriched"] or parsed_data["github_enriched"]["languages"] is None:
                         parsed_data["github_enriched"]["languages"] = []
                     
                     if gh_profile.get("created_at_platform"):
                        parsed_data["github_enriched"]["created_at"] = gh_profile["created_at_platform"]
                 
                 li_profile = existing.get("linkedin_profile")
                 if li_profile:
                     parsed_data["linkedin_enriched"] = li_profile
                     parsed_data["linkedin_enriched"]["experience"] = li_profile.get("linkedin_experience", [])
                     parsed_data["linkedin_enriched"]["education"] = li_profile.get("linkedin_education", [])

                 edu_res = supabase.table("candidate_education").select("*").eq("candidate_id", existing["id"]).execute()
                 parsed_data["education"] = [
                    {"name": e["school_name"], "subtitle": e["degree"], "grade": e["grade"], "start_date": e["start_date"], "end_date": e["end_date"]}
                    for e in edu_res.data
                 ]
                 parsed_data["links"] = existing.get("source_links", {})
                 return jsonify(parsed_data), 200
                 
            parsed_data = parse_cv(filepath)
            
        parsed_data["cached"] = False
        parsed_data["file_id"] = cache_id
        parsed_data["cv_hash"] = cache_id
        
        cv_url = None
        print(f"DEBUG: Supabase Client Status: {'Initialised' if supabase else 'NOT INITIALISED'}")
        if supabase:
            try:
                # attempt to create bucket, but ignore if it already exists
                try:
                    supabase.storage.create_bucket('cvs', options={'public': True})
                    print("DEBUG: Verified/Created 'cvs' bucket.")
                except Exception:
                    pass 

                storage_path = f"{cache_id}_{filename}"
                print(f"DEBUG: Attempting upload to path: {storage_path}")
                
                with open(filepath, 'rb') as f:
                    # use upsert to prevent "File already exists" errors
                    print(f"DEBUG: Uploading {filename} to Supabase Storage...")
                    res = supabase.storage.from_('cvs').upload(
                        path=storage_path,
                        file=f,
                        file_options={
                            "content-type": "application/pdf" if filename.endswith(".pdf") else "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            "upsert": "true" 
                        }
                    )
                    # print(f"DEBUG: Storage Response: {res}")
                
                # construct the public url manually
                cv_url = f"{SUPABASE_URL}/storage/v1/object/public/cvs/{storage_path}"
                print(f"SUCCESS: CV uploaded to storage. URL: {cv_url}")
            except Exception as e:
                print(f"CRITICAL: Supabase Storage Upload Failed: {str(e)}")
                import traceback
                traceback.print_exc()
                # fallback to local path if storage fails
                cv_url = f"http://localhost:5000/uploads/{filename}" 
                #print(f"DEBUG: Falling back to local URL: {cv_url}")
        else:
            print("WARNING: Supabase client is None. Check your .env for SUPABASE_URL and SUPABASE_KEY.")
            cv_url = f"http://localhost:5000/uploads/{filename}"

        parsed_data["cv_url"] = cv_url

        if cache_enabled:
            save_to_cache("cv", cache_id, parsed_data)

        return jsonify(parsed_data), 200
    
    return jsonify({"error": "Invalid file type"}), 400

@extraction_bp.route("/scan-datasource", methods=["POST"])
def scan_datasource():
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
