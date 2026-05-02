from flask import Blueprint, jsonify, request
from core.supabase import supabase
from core.parsers.registry import datasource_registry

candidates_bp = Blueprint("candidates", __name__)

def _upsert_github_profile(gh_data):
    """Helper to process and save github profile data to database"""
    if not gh_data:
        return None
    
    username = gh_data.get("username")
    if not username:
        # TODO: figure out how to extract this if missing, maybe from url?
        return None

    gh_profile_res = supabase.table("github_profiles").upsert({
        "username": username,
        "name": gh_data.get("name"),
        "bio": gh_data.get("bio"),
        "company": gh_data.get("company"),
        "location": gh_data.get("location"),
        "email": gh_data.get("email"),
        "avatar_url": gh_data.get("avatar_url"),
        "profile_url": gh_data.get("profile_url"),
        "created_at_platform": gh_data.get("created_at"),
        "followers": gh_data.get("followers", 0),
        "total_prs": gh_data.get("total_prs", 0),
        "total_commits": gh_data.get("total_commits", 0),
        "total_stars": gh_data.get("total_stars", 0),
        "total_lines": gh_data.get("total_lines", 0),
        "languages": gh_data.get("languages", []),
        "raw_data": gh_data
    }, on_conflict="username").execute()
    
    if not gh_profile_res.data:
        return None
        
    github_profile_id = gh_profile_res.data[0]['id']
    supabase.table("github_projects").delete().eq("profile_id", github_profile_id).execute()
    
    projects = []
    for p in gh_data.get("repositories", []):
        projects.append({
            "profile_id": github_profile_id,
            "name": p.get("name"),
            "description": p.get("description"),
            "url": p.get("url"),
            "stars": p.get("stars", 0),
            "lines": p.get("lines", 0),
            "is_fork": p.get("is_fork", False),
            "language": p.get("language"),
            "is_featured": p.get("stars", 0) > 10 # arbitrary cutoff for featured repos to prevent flooding the UI
        })
    if projects:
        supabase.table("github_projects").insert(projects).execute()
        
    return github_profile_id

def _get_text(val):
    """Extract text from nested linkedin date/location objects if necessary"""
    if isinstance(val, dict):
        return val.get("text") or val.get("name")
    return val

def _upsert_linkedin_profile(li_data, fallback_url=None):
    """Helper to process and save linkedin profile data to database"""
    if not li_data:
        return None
        
    p_url = li_data.get("profile_url") or fallback_url
    if not p_url:
        return None

    li_profile_res = supabase.table("linkedin_profiles").upsert({
        "profile_url": p_url,
        "full_name": li_data.get("full_name"),
        "headline": li_data.get("headline"),
        "location": _get_text(li_data.get("location")),
        "followers": li_data.get("followers", 0),
        "connections": li_data.get("connections", 0),
        "about": li_data.get("about"),
        "profile_photo": li_data.get("profile_photo"),
        "raw_data": li_data
    }, on_conflict="profile_url").execute()

    if not li_profile_res.data:
        return None
        
    linkedin_profile_id = li_profile_res.data[0]['id']
    
    supabase.table("linkedin_experience").delete().eq("profile_id", linkedin_profile_id).execute()
    supabase.table("linkedin_education").delete().eq("profile_id", linkedin_profile_id).execute()
    
    exp_data = []
    for exp in li_data.get("experience", []):
        exp_data.append({
            "profile_id": linkedin_profile_id,
            "company_name": exp.get("company_name"),
            "position": exp.get("position"),
            "start_date": _get_text(exp.get("start_date")),
            "end_date": _get_text(exp.get("end_date")),
            "description": exp.get("description"),
            "skills": exp.get("skills", [])
        })
    if exp_data:
        supabase.table("linkedin_experience").insert(exp_data).execute()
        
    edu_data = []
    for edu in li_data.get("education", []):
        edu_data.append({
            "profile_id": linkedin_profile_id,
            "school_name": edu.get("school_name"),
            "degree": edu.get("degree"),
            "field_of_study": edu.get("field_of_study"),
            "start_date": _get_text(edu.get("start_date")),
            "end_date": _get_text(edu.get("end_date"))
        })
    if edu_data:
        supabase.table("linkedin_education").insert(edu_data).execute()

    # New sections from raw data
    certs = []
    for c in li_data.get("certifications", []):
        certs.append({
            "profile_id": linkedin_profile_id,
            "title": c.get("title"),
            "issuer": c.get("issuer"),
            "issue_date": _get_text(c.get("issue_date")),
            "credential_url": c.get("credential_url")
        })
    if certs:
        supabase.table("linkedin_certifications").upsert(certs).execute()

    projs = []
    for p in li_data.get("projects", []):
        projs.append({
            "profile_id": linkedin_profile_id,
            "title": p.get("title"),
            "description": p.get("description"),
            "start_date": _get_text(p.get("start_date")),
            "end_date": _get_text(p.get("end_date"))
        })
    if projs:
        supabase.table("linkedin_projects").upsert(projs).execute()
        
    return linkedin_profile_id

@candidates_bp.route("/save-candidates", methods=["POST"])
def save_candidates():
    data = request.json
    if not data or 'candidates' not in data:
        return jsonify({"error": "No candidate data provided"}), 400

    candidates = data['candidates']
    batch_name = data.get('batch_name', f"Batch {len(candidates)} candidates")
    
    final_candidate_ids = []

    for c in candidates:
        github_profile_id = _upsert_github_profile(c.get("github_enriched"))

        links_map = c.get("links", {})
        li_links = links_map.get("linkedin", [])
        fallback_linkedin_url = li_links[0] if isinstance(li_links, list) and len(li_links) > 0 else None
        
        linkedin_profile_id = _upsert_linkedin_profile(c.get("linkedin_enriched"), fallback_linkedin_url)

        try:
            candidate_res = supabase.table("candidate_data").insert({
                "name": c.get("name"),
                "email": c.get("email"),
                "phone": c.get("phone"),
                "skills": c.get("skills", []),
                "cv_experience": c.get("cv_experience", []),
                "experience_summary": c.get("experience"),
                "projects_history": c.get("projects", []),
                "extracurricular": c.get("extracurricular", []),
                "source_links": c.get("links", {}),
                "github_profile_id": github_profile_id,
                "linkedin_profile_id": linkedin_profile_id,
                "cv_url": c.get("cv_url"),
                "raw_cv_text": c.get("raw_cv_text")
            }).execute()
        except Exception as e:
            print(f"CRITICAL: Failed to insert candidate into database: {str(e)}")
            import traceback
            traceback.print_exc()
            continue

        if candidate_res.data:
            candidate_db_id = candidate_res.data[0]['id']
            final_candidate_ids.append(candidate_db_id)
            
            cv_education = []
            for edu in c.get("education", []):
                cv_education.append({
                    "candidate_id": candidate_db_id,
                    "school_name": edu.get("name"),
                    "degree": edu.get("subtitle"),
                    "grade": edu.get("grade"),
                    "start_date": edu.get("start_date"),
                    "end_date": edu.get("end_date")
                })
            if cv_education:
                supabase.table("candidate_education").insert(cv_education).execute()

    batch_response = supabase.table("batch_data").insert({
        "batch_name": batch_name,
        "candidate_ids": final_candidate_ids
    }).execute()

    return jsonify({
        "success": True, 
        "candidates_count": len(final_candidate_ids),
        "batch": batch_response.data[0] if batch_response.data else None
    }), 201

@candidates_bp.route("/get-candidate-batches", methods=["GET"])
def get_candidate_batches():
    response = supabase.table("batch_data").select("*").order("created_at", desc=True).execute()
    return jsonify(response.data), 200

@candidates_bp.route("/get-batch-candidates/<batch_id>", methods=["GET"])
def get_batch_candidates(batch_id):
    batch_res = supabase.table("batch_data").select("candidate_ids").eq("id", batch_id).execute()
    if not batch_res.data:
        return jsonify({"error": "Batch not found"}), 404
        
    candidate_ids = batch_res.data[0].get("candidate_ids", [])
    if not candidate_ids:
        return jsonify([]), 200
        
    candidates_res = supabase.table("candidate_data").select("*").in_("id", candidate_ids).execute()
    return jsonify(candidates_res.data), 200

@candidates_bp.route("/update-candidate/<candidate_id>", methods=["PUT"])
def update_candidate(candidate_id):
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    update_fields = {}
    for field in ['name', 'email', 'phone', 'cv_url']:
        if field in data:
            update_fields[field] = data[field]
            
    if 'source_links' in data:
        update_fields['source_links'] = data['source_links']
    elif 'github_url' in data or 'linkedin_url' in data:
        current_res = supabase.table("candidate_data").select("source_links", "github_profile_id", "linkedin_profile_id").eq("id", candidate_id).execute()
        current_data = current_res.data[0] if current_res.data else {}
        links = current_data.get("source_links", {})
        
        if 'github_url' in data:
            new_gh = data['github_url']
            gh_list = links.get('github')
            current_gh = gh_list[0] if isinstance(gh_list, list) and len(gh_list) > 0 else None
            if new_gh != current_gh:
                links['github'] = [new_gh] if new_gh else []
                if new_gh:
                    try:
                        scanner = datasource_registry.get_source('github')
                        gh_data = scanner.process(new_gh)
                        update_fields['github_profile_id'] = _upsert_github_profile(gh_data)
                    except Exception as e:
                        print("github scan failed:", e)
                        update_fields['github_profile_id'] = None
                else:
                    update_fields['github_profile_id'] = None
                
        if 'linkedin_url' in data:
            new_li = data['linkedin_url']
            li_list = links.get('linkedin')
            current_li = li_list[0] if isinstance(li_list, list) and len(li_list) > 0 else None
            if new_li != current_li:
                links['linkedin'] = [new_li] if new_li else []
                if new_li:
                    try:
                        scanner = datasource_registry.get_source('linkedin')
                        li_data = scanner.process(new_li)
                        update_fields['linkedin_profile_id'] = _upsert_linkedin_profile(li_data, new_li)
                    except Exception as e:
                        print("linkedin scan failed:", e)
                        update_fields['linkedin_profile_id'] = None
                else:
                    update_fields['linkedin_profile_id'] = None
        
        update_fields['source_links'] = links

    if not update_fields:
        return jsonify({"error": "No valid fields to update"}), 400

    response = supabase.table("candidate_data").update(update_fields).eq("id", candidate_id).execute()
    return jsonify({"success": True, "data": response.data}), 200

@candidates_bp.route("/delete-candidate-batch/<batch_id>", methods=["DELETE"])
def delete_candidate_batch(batch_id):
    batch_res = supabase.table("batch_data").select("candidate_ids").eq("id", batch_id).execute()
    if not batch_res.data:
        return jsonify({"error": "Batch not found"}), 404
        
    candidate_ids = batch_res.data[0].get("candidate_ids", [])
    
    if candidate_ids:
        supabase.table("candidate_data").delete().in_("id", candidate_ids).execute()
    
    supabase.table("batch_data").delete().eq("id", batch_id).execute()
    
    return jsonify({"success": True}), 200

@candidates_bp.route("/delete-candidate/<candidate_id>", methods=["DELETE"])
def delete_candidate(candidate_id):
    batch_res = supabase.table("batch_data").select("id", "candidate_ids").contains("candidate_ids", [candidate_id]).execute()
    
    for batch in batch_res.data:
        updated_ids = [cid for cid in batch["candidate_ids"] if cid != candidate_id]
        supabase.table("batch_data").update({"candidate_ids": updated_ids}).eq("id", batch["id"]).execute()
    
    supabase.table("candidate_data").delete().eq("id", candidate_id).execute()
    
    return jsonify({"success": True}), 200

@candidates_bp.route("/get-candidate-detail/<candidate_id>", methods=["GET"])
def get_candidate_detail(candidate_id):
    # Optimised: Safe-Hybrid Query (Join core data, defensive fetch for optional extras)
    response = supabase.table("candidate_data").select("""
        *,
        cv_education:candidate_education(*),
        github_profile:github_profiles(*, github_projects(*)),
        linkedin_profile:linkedin_profiles(*, 
            linkedin_experience(*), 
            linkedin_education(*)
        )
    """).eq("id", candidate_id).execute()

    if not response.data:
        return jsonify({"error": "Candidate not found"}), 404
        
    candidate = response.data[0]
    
    # Map the embedded data
    candidate["cv_education"] = candidate.get("cv_education", [])
    
    gh_profile = candidate.get("github_profile")
    if gh_profile:
        # Re-map database columns to frontend interface keys
        history = gh_profile.get("contribution_history")
        if history is None and "raw_data" in gh_profile and isinstance(gh_profile["raw_data"], dict):
            # Failover to common raw data aliases
            history = gh_profile["raw_data"].get("contribution_history") or \
                      gh_profile["raw_data"].get("history") or \
                      gh_profile["raw_data"].get("language_history")
        
        gh_profile["language_history"] = history or []
        candidate["github_projects"] = gh_profile.get("github_projects", [])
            
    li_profile = candidate.get("linkedin_profile")
    if li_profile:
        candidate["linkedin_experience"] = li_profile.get("linkedin_experience", [])
        candidate["linkedin_education"] = li_profile.get("linkedin_education", [])
        
        # Defensive separate fetches for potentially missing optional tables
        li_id = li_profile.get("id")
        for key, table in [("linkedin_projects", "linkedin_projects"), 
                           ("linkedin_certifications", "linkedin_certifications"), 
                           ("linkedin_volunteering", "linkedin_volunteering")]:
            try:
                extra_res = supabase.table(table).select("*").eq("profile_id", li_id).execute()
                candidate[key] = extra_res.data
            except Exception:
                candidate[key] = []
            
    # Construct virtual full text for the "AI Evidence" view
    full_text_parts = []
    full_text_parts.append(f"{candidate.get('name', 'CANDIDATE')}")
    full_text_parts.append(f"{candidate.get('email', '')} | {candidate.get('phone', '')}")
    full_text_parts.append("\nPROFESSIONAL SUMMARY")
    full_text_parts.append(candidate.get("experience_summary", ""))
    
    if candidate.get("cv_education"):
        full_text_parts.append("\nEDUCATION")
        for edu in candidate["cv_education"]:
            full_text_parts.append(f"• {edu.get('school_name')} - {edu.get('degree')} ({edu.get('start_date')} - {edu.get('end_date')})")
    
    if candidate.get("projects_history"):
        full_text_parts.append("\nPROJECTS")
        for proj in candidate["projects_history"]:
            full_text_parts.append(f"• {proj.get('title')}: {proj.get('description')}")
    
    if candidate.get("extracurricular"):
        full_text_parts.append("\nEXTRACURRICULAR")
        for extra in candidate["extracurricular"]:
            full_text_parts.append(f"• {extra.get('title')}: {extra.get('description')}")
    
    candidate["full_cv_text"] = "\n".join(full_text_parts)
            
    return jsonify(candidate), 200
