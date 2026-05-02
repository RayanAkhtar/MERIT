from flask import Blueprint, jsonify, request
from core.supabase import supabase
from core.scoring.registry import scoring_registry

ranking_bp = Blueprint("ranking", __name__)

@ranking_bp.route("/rank-candidates/<config_id>", methods=["GET"])
def rank_candidates(config_id):
    config_res = supabase.table("matching_configs").select(
        "*, job_requirements(*), batch_data(*)"
    ).eq("id", config_id).execute()
    
    if not config_res.data:
        return jsonify({"error": "Configuration not found"}), 404
        
    config = config_res.data[0]
    job_reqs = config.get("job_requirements")
    batch = config.get("batch_data")
    weights = config.get("weights", {})
    
    if not job_reqs or not batch:
        return jsonify({"error": "Configuration is missing job or batch link"}), 400

    # Performance Optimised: Single Relational Query (Batch Fetch + Resource Embedding)
    candidate_ids = batch.get("candidate_ids", [])
    if not candidate_ids:
        return jsonify({"results": [], "message": "No candidates in this batch."}), 200

    candidates_res = supabase.table("candidate_data").select("""
        *,
        cv_education:candidate_education(*),
        github_profile:github_profiles(*, github_projects(*)),
        linkedin_profile:linkedin_profiles(*, linkedin_experience(*), linkedin_education(*))
    """).in_("id", candidate_ids).execute()

    if not candidates_res.data:
        return jsonify({"results": [], "message": "Candidates not found."}), 404

    results = []
    for candidate in candidates_res.data:
        # Map the embedded data to the structure the scoring engine and frontend expect
        gh_profile = candidate.get("github_profile")
        if gh_profile:
            # Re-map database columns to frontend interface keys
            # Failover: If dedicated column is missing, try to extract from raw_data blob
            history = gh_profile.get("contribution_history")
            if history is None and "raw_data" in gh_profile and isinstance(gh_profile["raw_data"], dict):
                history = gh_profile["raw_data"].get("contribution_history")
            
            gh_profile["language_history"] = history or []
            
            # Failover: If database columns for lines/forks are missing, pull from raw_data
            projects = gh_profile.get("github_projects", [])
            if "raw_data" in gh_profile and isinstance(gh_profile["raw_data"], dict):
                raw_repos = gh_profile["raw_data"].get("repositories") or \
                            gh_profile["raw_data"].get("featured_projects") or []
                raw_map = {r.get("name"): r for r in raw_repos if r.get("name")}
                for p in projects:
                    if p.get("name") in raw_map:
                        raw_p = raw_map[p["name"]]
                        # Map both 'lines' and 'is_fork' keys from raw JSON
                        if p.get("lines") is None or p.get("lines") == 0:
                            p["lines"] = raw_p.get("lines") or raw_p.get("estimated_lines") or 0
                        if p.get("is_fork") is None:
                            p["is_fork"] = raw_p.get("is_fork") or raw_p.get("fork") or False

            gh_profile["featured_projects"] = projects
            # Map to the key expected by the scoring engine
            candidate["github_enriched"] = gh_profile
            
        li_profile = candidate.get("linkedin_profile")
        if li_profile:
            candidate["linkedin_enriched"] = li_profile
            
        candidate["linkedin_experience"] = (li_profile or {}).get("linkedin_experience", [])
        candidate["linkedin_education"] = (li_profile or {}).get("linkedin_education", [])
        
        active_metrics = config.get("active_metrics", [])
        
        # Pass 1: Raw Metrics (specifically for relative tenure, github depth, and traction)
        raw_scored_data = scoring_registry.run_all(candidate, job_reqs, active_metrics, weights)
        candidate["raw_tenure_months"] = raw_scored_data["metrics"].get("experience", {}).get("raw_months", 0)
        candidate["raw_gh_complexity"] = raw_scored_data["metrics"].get("intel_github_complexity", {}).get("raw_complexity_sum", 0)
        candidate["raw_gh_traction"] = raw_scored_data["metrics"].get("projects", {}).get("raw_traction_points", 0)
        
        # Extract Actual Stats for leader-based feedback
        gh_p = candidate.get("github_enriched", {}) or {}
        # Count repositories from featured_projects (mapped) or raw repo list
        repos = gh_p.get("featured_projects", []) or gh_p.get("repositories", [])
        candidate["raw_repo_count"] = gh_p.get("public_repos") or len(repos)
        candidate["raw_star_count"] = gh_p.get("total_stars") or sum(p.get("stars", 0) for p in repos)
        candidate["raw_fork_count"] = gh_p.get("total_forks") or sum(p.get("forks", 0) for p in repos)
        # Weighted Impact: Forks (2.5x) are more valuable than Stars (1.0x)
        candidate["raw_impact_points"] = (candidate["raw_star_count"] * 1.0) + (candidate["raw_fork_count"] * 2.5)
        
        li_p = candidate.get("linkedin_enriched", {}) or {}
        candidate["raw_connections"] = li_p.get("connections", 0) or li_p.get("followers", 0)
        
        # Track total skill breadth (CV + LI + GH detected)
        unique_skills = set([s.lower() for s in candidate.get('skills', [])])
        candidate["raw_skill_count"] = len(unique_skills)

        results.append({
            "candidate": candidate,
            "raw_scored_data": raw_scored_data
        })

    # Calculate Batch Stats for relative scoring
    max_tenure = max([r["candidate"].get("raw_tenure_months", 1) for r in results]) if results else 60
    max_complexity = max([r["candidate"].get("raw_gh_complexity", 1.0) for r in results]) if results else 1.0
    max_traction = max([r["candidate"].get("raw_gh_traction", 0.5) for r in results]) if results else 0.5
    max_impact = max([r["candidate"].get("raw_impact_points", 1.0) for r in results]) if results else 1.0
    max_repos = max([r["candidate"].get("raw_repo_count", 1) for r in results]) if results else 5
    max_stars = max([r["candidate"].get("raw_star_count", 0) for r in results]) if results else 0
    max_forks = max([r["candidate"].get("raw_fork_count", 0) for r in results]) if results else 0
    max_connections = max([r["candidate"].get("raw_connections", 1) for r in results]) if results else 1
    max_skills = max([r["candidate"].get("raw_skill_count", 5) for r in results]) if results else 5
    
    final_results = []
    for r in results:
        candidate = r["candidate"]
        # Pass 2: Final Scored Result with batch context
        candidate["batch_max_tenure"] = max_tenure
        candidate["batch_max_complexity"] = max_complexity
        candidate["batch_max_traction"] = max_traction
        candidate["batch_max_impact"] = max_impact
        candidate["batch_max_repos"] = max_repos
        candidate["batch_max_stars"] = max_stars
        candidate["batch_max_forks"] = max_forks
        candidate["batch_max_connections"] = max_connections
        candidate["batch_max_skill_count"] = max_skills
        # Inject individual skill scores, weights, and active status from Pass 1
        candidate["skill_scores"] = {k: v.get("score", 0) for k, v in r["raw_scored_data"]["metrics"].items()}
        candidate["skill_weights"] = weights
        candidate["active_keys"] = [k for k, v in active_metrics.items() if v is True] if isinstance(active_metrics, dict) else active_metrics
        
        scored_data = scoring_registry.run_all(candidate, job_reqs, active_metrics, weights)
        
        final_results.append({
            "candidate_id": candidate["id"],
            "name": candidate["name"],
            "email": candidate["email"],
            "total_score": scored_data["overall_score"],
            "metrics": scored_data["metrics"],
            "calculation_summary": scored_data["calculation_summary"]
        })

    final_results.sort(key=lambda x: x["total_score"], reverse=True)

    snapshot_data = {
        "config_id": config_id,
        "results_payload": final_results,
        "summary_data": {
            "top_candidate": final_results[0]["name"] if final_results else "N/A",
            "top_score": final_results[0]["total_score"] if final_results else 0,
            "candidate_count": len(final_results)
        }
    }
    supabase.table("past_results").insert(snapshot_data).execute()

    return jsonify({
        "config_name": config["name"],
        "job_title": job_reqs["title"],
        "batch_name": batch["batch_name"],
        "results": final_results
    }), 200

@ranking_bp.route("/get-past-results", methods=["GET"])
def get_past_results():
    res = supabase.table("past_results").select(
        "*, matching_configs(name)"
    ).order("created_at", desc=True).execute()

    return jsonify(res.data), 200
