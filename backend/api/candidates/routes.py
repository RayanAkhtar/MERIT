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
        # TODO: maybe we can extract from profile url?
        # but scanner should return username
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
    for p in gh_data.get("featured_projects", []):
        projects.append({
            "profile_id": github_profile_id,
            "name": p.get("name"),
            "description": p.get("description"),
            "url": p.get("url"),
            "stars": p.get("stars", 0),
            "language": p.get("top_languages", [None])[0] if p.get("top_languages") else None,
            "is_featured": True
        })
    if projects:
        supabase.table("github_projects").insert(projects).execute()
        
    return github_profile_id

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
        "location": li_data.get("location"),
        "followers": li_data.get("followers", 0),
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
            "start_date": exp.get("start_date"),
            "end_date": exp.get("end_date"),
            "description": exp.get("description")
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
            "start_date": edu.get("start_date"),
            "end_date": edu.get("end_date")
        })
    if edu_data:
        supabase.table("linkedin_education").insert(edu_data).execute()
        
    return linkedin_profile_id

@candidates_bp.route("/save-candidates", methods=["POST"])
def save_candidates():
    """Save enriched candidate data into normalised relational tables"""
    data = request.json
    if not data or 'candidates' not in data:
        return jsonify({"error": "No candidate data provided"}), 400

    candidates = data['candidates']
    batch_name = data.get('batch_name', f"Batch {len(candidates)} candidates")
    
    final_candidate_ids = []

    if not supabase:
         return jsonify({"error": "Database connection not established"}), 500

    for c in candidates:
        github_profile_id = None
        linkedin_profile_id = None

        # github data
        github_profile_id = _upsert_github_profile(c.get("github_enriched"))

        # linkedin data
        fallback_linkedin_url = c.get("links", {}).get("linkedin", [None])[0]
        linkedin_profile_id = _upsert_linkedin_profile(c.get("linkedin_enriched"), fallback_linkedin_url)

        # main candidate data
        candidate_res = supabase.table("candidate_data").insert({
            "name": c.get("name"),
            "email": c.get("email"),
            "phone": c.get("phone"),
            "skills": c.get("skills", []),
            "experience_summary": c.get("experience"),
            "projects_history": c.get("projects", []),
            "extracurricular": c.get("extracurricular", []),
            "source_links": c.get("links", {}),
            "github_profile_id": github_profile_id,
            "linkedin_profile_id": linkedin_profile_id,
            "cv_url": c.get("cv_url")
        }).execute()

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
    """Fetch all candidate extraction batches"""
    try:
        if not supabase:
            return jsonify({"error": "Database connection not established"}), 500
            
        response = supabase.table("batch_data").select("*").order("created_at", desc=True).execute()
        return jsonify(response.data), 200
    except Exception as e:
        print(f"ERROR fetching candidate batches: {str(e)}")
        return jsonify({"error": f"Failed to fetch from database: {str(e)}"}), 500

@candidates_bp.route("/get-batch-candidates/<batch_id>", methods=["GET"])
def get_batch_candidates(batch_id):
    """Fetch all candidates belonging to a specific batch"""
    try:
        if not supabase:
            return jsonify({"error": "Database connection not established"}), 500
            
        # first get batch to get candidate ids
        batch_res = supabase.table("batch_data").select("candidate_ids").eq("id", batch_id).execute()
        if not batch_res.data:
            return jsonify({"error": "Batch not found"}), 404
            
        candidate_ids = batch_res.data[0].get("candidate_ids", [])
        if not candidate_ids:
            return jsonify([]), 200
            
        # then find candidates matching that those ids in batch
        candidates_res = supabase.table("candidate_data").select("*").in_("id", candidate_ids).execute()
        return jsonify(candidates_res.data), 200
    except Exception as e:
        print(f"ERROR fetching batch candidates: {str(e)}")
        return jsonify({"error": f"Failed to fetch from database: {str(e)}"}), 500

@candidates_bp.route("/update-candidate/<candidate_id>", methods=["PUT"])
def update_candidate(candidate_id):
    """Update specific fields for a single candidate"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        if not supabase:
            return jsonify({"error": "Database connection not established"}), 500
            
        # editable fields being extracted
        # the main reason we even get here is because we want to update their linkedin and github urls
        update_fields = {}
        for field in ['name', 'email', 'phone', 'cv_url']:
            if field in data:
                update_fields[field] = data[field]
                
        # handling source_links (GitHub/LinkedIn URLs)
        if 'source_links' in data:
            update_fields['source_links'] = data['source_links']
        elif 'github_url' in data or 'linkedin_url' in data:
            # if individual URL fields provided, update source_links map
            current_res = supabase.table("candidate_data").select("source_links", "github_profile_id", "linkedin_profile_id").eq("id", candidate_id).execute()
            current_data = current_res.data[0] if current_res.data else {}
            links = current_data.get("source_links", {})
            
            # checking if GitHub URL changed to clear stale profile data
            if 'github_url' in data:
                new_gh = data['github_url']
                gh_list = links.get('github')
                current_gh = gh_list[0] if isinstance(gh_list, list) and len(gh_list) > 0 else None
                if new_gh != current_gh:
                    links['github'] = [new_gh] if new_gh else []
                    if new_gh:
                        try:
                            # triggering deep scan for new datasource URL
                            scanner = datasource_registry.get_source('github')
                            gh_data = scanner.process(new_gh)
                            update_fields['github_profile_id'] = _upsert_github_profile(gh_data)
                        except Exception as e:
                            print(f"Deep scan failed for github: {str(e)}")
                            update_fields['github_profile_id'] = None
                    else:
                        update_fields['github_profile_id'] = None
                    
            # checking if LinkedIn URL changed to clear stale profile data
            if 'linkedin_url' in data:
                new_li = data['linkedin_url']
                li_list = links.get('linkedin')
                current_li = li_list[0] if isinstance(li_list, list) and len(li_list) > 0 else None
                if new_li != current_li:
                    links['linkedin'] = [new_li] if new_li else []
                    if new_li:
                        try:
                            # triggering deep scan for new datasource URL
                            scanner = datasource_registry.get_source('linkedin')
                            li_data = scanner.process(new_li)
                            update_fields['linkedin_profile_id'] = _upsert_linkedin_profile(li_data, new_li)
                        except Exception as e:
                            print(f"Deep scan failed for linkedin: {str(e)}")
                            update_fields['linkedin_profile_id'] = None
                    else:
                        update_fields['linkedin_profile_id'] = None
            
            update_fields['source_links'] = links

        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400

        response = supabase.table("candidate_data").update(update_fields).eq("id", candidate_id).execute()
        return jsonify({"success": True, "data": response.data}), 200
        
    except Exception as e:
        print(f"ERROR updating candidate info: {str(e)}")
        return jsonify({"error": f"Failed to update database: {str(e)}"}), 500

@candidates_bp.route("/delete-candidate-batch/<batch_id>", methods=["DELETE"])
def delete_candidate_batch(batch_id):
    """Permanently delete a candidate batch and all associated candidates"""
    try:
        if not supabase:
            return jsonify({"error": "Database connection not established"}), 500
            
        # getting candidate IDs before deleting batch
        batch_res = supabase.table("batch_data").select("candidate_ids").eq("id", batch_id).execute()
        if not batch_res.data:
            return jsonify({"error": "Batch not found"}), 404
            
        candidate_ids = batch_res.data[0].get("candidate_ids", [])
        
        # deleting candidates first
        if candidate_ids:
            supabase.table("candidate_data").delete().in_("id", candidate_ids).execute()
        
        # deleting the batch itself
        supabase.table("batch_data").delete().eq("id", batch_id).execute()
        
        return jsonify({"success": True}), 200
    except Exception as e:
        print(f"ERROR deleting candidate batch: {str(e)}")
        return jsonify({"error": f"Failed to delete from database: {str(e)}"}), 500

@candidates_bp.route("/delete-candidate/<candidate_id>", methods=["DELETE"])
def delete_candidate(candidate_id):
    """Delete a single candidate and remove them from any associated batches"""
    try:
        if not supabase:
            return jsonify({"error": "Database connection not established"}), 500
        
        # finding batches that contain this candidate ID
        batch_res = supabase.table("batch_data").select("id", "candidate_ids").contains("candidate_ids", [candidate_id]).execute()
        
        # removing candidate ID from those batches
        for batch in batch_res.data:
            updated_ids = [cid for cid in batch["candidate_ids"] if cid != candidate_id]
            supabase.table("batch_data").update({"candidate_ids": updated_ids}).eq("id", batch["id"]).execute()
        
        supabase.table("candidate_data").delete().eq("id", candidate_id).execute()
        
        return jsonify({"success": True}), 200
    except Exception as e:
        print(f"ERROR deleting candidate: {str(e)}")
        return jsonify({"error": f"Failed to delete from database: {str(e)}"}), 500

@candidates_bp.route("/get-candidate-detail/<candidate_id>", methods=["GET"])
def get_candidate_detail(candidate_id):
    """Fetch full-fidelity candidate data including all related source profiles"""
    try:
        if not supabase:
            return jsonify({"error": "Database connection not established"}), 500
            
        # fetching main candidate record
        candidate_res = supabase.table("candidate_data").select("*").eq("id", candidate_id).execute()
        if not candidate_res.data:
            return jsonify({"error": "Candidate not found"}), 404
            
        candidate = candidate_res.data[0]
        
        edu_res = supabase.table("candidate_education").select("*").eq("candidate_id", candidate_id).execute()
        candidate["cv_education"] = edu_res.data
        
        candidate["github_profile"] = None
        candidate["github_projects"] = []
        if candidate.get("github_profile_id"):
            gh_profile = supabase.table("github_profiles").select("*").eq("id", candidate["github_profile_id"]).execute()
            if gh_profile.data:
                candidate["github_profile"] = gh_profile.data[0]
                gh_projects = supabase.table("github_projects").select("*").eq("profile_id", candidate["github_profile_id"]).execute()
                candidate["github_projects"] = gh_projects.data
                
        candidate["linkedin_profile"] = None
        candidate["linkedin_experience"] = []
        candidate["linkedin_education"] = []
        if candidate.get("linkedin_profile_id"):
            li_profile = supabase.table("linkedin_profiles").select("*").eq("id", candidate["linkedin_profile_id"]).execute()
            if li_profile.data:
                candidate["linkedin_profile"] = li_profile.data[0]
                li_exp = supabase.table("linkedin_experience").select("*").eq("profile_id", candidate["linkedin_profile_id"]).execute()
                candidate["linkedin_experience"] = li_exp.data
                li_edu = supabase.table("linkedin_education").select("*").eq("profile_id", candidate["linkedin_profile_id"]).execute()
                candidate["linkedin_education"] = li_edu.data
                
        return jsonify(candidate), 200
    except Exception as e:
        print(f"ERROR fetching candidate detail: {str(e)}")
        return jsonify({"error": f"Failed to fetch from database: {str(e)}"}), 500
