from flask import Blueprint, jsonify, request
from core.supabase import supabase

candidates_bp = Blueprint("candidates", __name__)

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
        gh = c.get("github_enriched")
        if gh:
            username = gh.get("username")
            gh_profile_res = supabase.table("github_profiles").upsert({
                "username": username,
                "name": gh.get("name"),
                "bio": gh.get("bio"),
                "company": gh.get("company"),
                "location": gh.get("location"),
                "email": gh.get("email"),
                "avatar_url": gh.get("avatar_url"),
                "profile_url": gh.get("profile_url"),
                "created_at_platform": gh.get("created_at"),
                "followers": gh.get("followers", 0),
                "total_prs": gh.get("total_prs", 0),
                "total_commits": gh.get("total_commits", 0),
                "total_stars": gh.get("total_stars", 0),
                "total_lines": gh.get("total_lines", 0),
                "languages": gh.get("languages", []),
                "raw_data": gh
            }, on_conflict="username").execute()
            
            if gh_profile_res.data:
                github_profile_id = gh_profile_res.data[0]['id']
                supabase.table("github_projects").delete().eq("profile_id", github_profile_id).execute()
                
                projects = []
                for p in gh.get("featured_projects", []):
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

        # linkedin data
        li = c.get("linkedin_enriched")
        if li:
            p_url = li.get("profile_url") or c.get("links", {}).get("linkedin", [None])[0]
            li_profile_res = supabase.table("linkedin_profiles").upsert({
                "profile_url": p_url,
                "full_name": li.get("full_name"),
                "headline": li.get("headline"),
                "location": li.get("location"),
                "followers": li.get("followers", 0),
                "about": li.get("about"),
                "profile_photo": li.get("profile_photo"),
                "raw_data": li
            }, on_conflict="profile_url").execute()

            if li_profile_res.data:
                linkedin_profile_id = li_profile_res.data[0]['id']
                
                supabase.table("linkedin_experience").delete().eq("profile_id", linkedin_profile_id).execute()
                supabase.table("linkedin_education").delete().eq("profile_id", linkedin_profile_id).execute()
                
                exp_data = []
                for exp in li.get("experience", []):
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
                for edu in li.get("education", []):
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
            "linkedin_profile_id": linkedin_profile_id
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
