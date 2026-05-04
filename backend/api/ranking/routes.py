from flask import Blueprint, jsonify, request
from core.supabase import supabase
from core.scoring.registry import scoring_registry
import traceback

ranking_bp = Blueprint("ranking", __name__)

@ranking_bp.route("/rank-candidates/<config_id>", methods=["GET"])
def rank_candidates(config_id):
    try:
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
            # shove things into the structure the scoring engine and frontend want
            gh_profile = candidate.get("github_profile")
            if gh_profile:
                # map db columns to frontend keys
                # ensure we get the correct history key from the database or raw_data failover
                history = gh_profile.get("language_history") or gh_profile.get("contribution_history")
                if history is None and "raw_data" in gh_profile and isinstance(gh_profile["raw_data"], dict):
                    # failover to common raw data aliases
                    rd = gh_profile["raw_data"]
                    history = rd.get("language_history") or rd.get("contribution_history") or rd.get("history")
                
                gh_profile["language_history"] = history or []
                
                projects = gh_profile.get("github_projects", [])
                if "raw_data" in gh_profile and isinstance(gh_profile["raw_data"], dict):
                    raw_repos = gh_profile["raw_data"].get("repositories") or \
                                gh_profile["raw_data"].get("featured_projects") or []
                    raw_map = {r.get("name"): r for r in raw_repos if r.get("name")}
                    for p in projects:
                        if p.get("name") in raw_map:
                            raw_p = raw_map[p["name"]]
                            if p.get("lines") is None or p.get("lines") == 0:
                                # try to grab the lines from the raw json
                                p["lines"] = raw_p.get("lines") or raw_p.get("estimated_lines") or 0
                            if p.get("is_fork") is None:
                                # and check if it's a fork
                                p["is_fork"] = raw_p.get("is_fork") or raw_p.get("fork") or False
                            
                            # some extra bits for the verification check
                            p["commits"] = raw_p.get("commits") or raw_p.get("user_commits") or 0
                            p["forks"] = raw_p.get("forks") or raw_p.get("forks_count") or 0
                            p["languages_distribution"] = raw_p.get("languages_distribution") or {}

                gh_profile["featured_projects"] = projects
                candidate["github_enriched"] = gh_profile
                
            li_profile = candidate.get("linkedin_profile")
            if li_profile:
                candidate["linkedin_enriched"] = li_profile
                
            candidate["linkedin_experience"] = (li_profile or {}).get("linkedin_experience", [])
            candidate["linkedin_education"] = (li_profile or {}).get("linkedin_education", [])
            
            # Ensure full_cv_text is available as fallback for CV skill detection if raw_cv_text is missing
            if not candidate.get("raw_cv_text"):
                full_text_parts = []
                full_text_parts.append(str(candidate.get('name') or 'CANDIDATE'))
                full_text_parts.append(f"{str(candidate.get('email') or '')} | {str(candidate.get('phone') or '')}")
                full_text_parts.append("\nPROFESSIONAL SUMMARY")
                full_text_parts.append(str(candidate.get("experience_summary") or ""))
                
                if candidate.get("cv_education"):
                    full_text_parts.append("\nEDUCATION")
                    for edu in candidate["cv_education"]:
                        if isinstance(edu, dict):
                            full_text_parts.append(f"• {str(edu.get('school_name') or '')} - {str(edu.get('degree') or '')} ({str(edu.get('start_date') or '')} - {str(edu.get('end_date') or '')})")
                
                if candidate.get("projects_history"):
                    full_text_parts.append("\nPROJECTS")
                    for proj in candidate["projects_history"]:
                        if isinstance(proj, dict):
                            full_text_parts.append(f"• {str(proj.get('title') or proj.get('name') or 'Unnamed Project')}: {str(proj.get('description') or '')}")
                
                if candidate.get("extracurricular"):
                    full_text_parts.append("\nEXTRACURRICULAR")
                    for extra in candidate["extracurricular"]:
                        if isinstance(extra, dict):
                            full_text_parts.append(f"• {str(extra.get('title') or 'Activity')}: {str(extra.get('description') or '')}")
                
                candidate["full_cv_text"] = "\n".join(full_text_parts)

            active_metrics = config.get("active_metrics", [])
            
            # first pass: just getting the raw metrics
            raw_scored_data = scoring_registry.run_all(candidate, job_reqs, active_metrics, weights)
            exp_metrics = raw_scored_data["metrics"].get("experience", {})
            candidate["raw_tenure_months"] = exp_metrics.get("raw_months") or 0
            candidate["raw_cv_tenure_months"] = exp_metrics.get("raw_cv_months") or 0
            candidate["raw_li_tenure_months"] = exp_metrics.get("raw_li_months") or 0
            candidate["raw_gh_complexity"] = raw_scored_data["metrics"].get("intel_github_complexity", {}).get("raw_complexity_sum") or 0
            candidate["raw_gh_traction"] = raw_scored_data["metrics"].get("projects", {}).get("raw_traction_points") or 0
            
            gh_p = candidate.get("github_enriched", {}) or {}
            li_p = candidate.get("linkedin_enriched", {}) or {}
            repos = (gh_p.get("featured_projects") or []) or (gh_p.get("repositories") or [])
            
            candidate["raw_star_count"] = gh_p.get("total_stars") or sum(p.get("stars", 0) for p in repos if p)
            candidate["raw_fork_count"] = gh_p.get("total_forks") or sum(p.get("forks", 0) for p in repos if p)
            candidate["raw_repo_count"] = gh_p.get("repo_count") or len(repos)
            candidate["raw_impact_points"] = ((candidate.get("raw_star_count") or 0) * 1.0) + ((candidate.get("raw_fork_count") or 0) * 2.5)
            candidate["raw_connections"] = li_p.get("connections", 0) or li_p.get("followers", 0) or 0
            
            unique_skills = set([s.lower() for s in candidate.get('skills', []) if s])
            candidate["raw_skill_count"] = len(unique_skills)

            results.append({
                "candidate": candidate,
                "raw_scored_data": raw_scored_data
            })

        # work out the batch stats for relative scoring
        max_tenure = max([r["candidate"].get("raw_tenure_months") or 0 for r in results] + [60])
        max_cv_tenure = max([r["candidate"].get("raw_cv_tenure_months") or 0 for r in results] + [60])
        max_li_tenure = max([r["candidate"].get("raw_li_tenure_months") or 0 for r in results] + [60])
        max_complexity = max([r["candidate"].get("raw_gh_complexity") or 0.0 for r in results] + [1.0])
        max_traction = max([r["candidate"].get("raw_gh_traction") or 0.0 for r in results] + [0.5])
        max_impact = max([r["candidate"].get("raw_impact_points") or 0.0 for r in results] + [1.0])
        max_repos = max([r["candidate"].get("raw_repo_count") or 0 for r in results] + [5])
        max_stars = max([r["candidate"].get("raw_star_count") or 0 for r in results] + [0])
        max_forks = max([r["candidate"].get("raw_fork_count") or 0 for r in results] + [0])
        max_connections = max([r["candidate"].get("raw_connections") or 0 for r in results] + [1])
        max_skills = max([r["candidate"].get("raw_skill_count") or 0 for r in results] + [5])
        
        final_results = []
        for r in results:
            candidate = r["candidate"]
            # second pass: final score using the batch context we just found
            candidate["batch_max_tenure"] = max_tenure
            candidate["batch_max_cv_tenure"] = max_cv_tenure
            candidate["batch_max_li_tenure"] = max_li_tenure
            candidate["batch_max_complexity"] = max_complexity
            candidate["batch_max_traction"] = max_traction
            candidate["batch_max_impact"] = max_impact
            candidate["batch_max_repos"] = max_repos
            candidate["batch_max_stars"] = max_stars
            candidate["batch_max_forks"] = max_forks
            candidate["batch_max_connections"] = max_connections
            candidate["batch_max_skill_count"] = max_skills
            
            # shove in full metric data and weights from the first pass
            candidate["skill_metrics"] = r["raw_scored_data"]["metrics"]
            candidate["skill_scores"] = {k: (v.get("score") or 0.0) for k, v in r["raw_scored_data"]["metrics"].items()}
            candidate["skill_weights"] = weights
            candidate["active_keys"] = [k for k, v in active_metrics.items() if v is True] if isinstance(active_metrics, dict) else active_metrics
            
            scored_data = scoring_registry.run_all(candidate, job_reqs, active_metrics, weights)
            
            # calculate explainable AI (XAI) metrics via Shapley Values
            from core.scoring.explainability import ShapleyExplainer
            explainer = ShapleyExplainer(scoring_registry)
            shapley_results = explainer.calculate_contributions(candidate, job_reqs, active_metrics, weights)
            
            # inject "per metric" Shapley values into the metrics breakdown for the UI
            for m_key, m_val in scored_data["metrics"].items():
                if m_key in shapley_results["metrics"]:
                    if m_val.get("breakdown") and len(m_val["breakdown"]) > 0:
                        m_val["breakdown"][0]["impact_attribution"] = shapley_results["metrics"][m_key]
            
            final_results.append({
                "candidate_id": candidate["id"],
                "name": candidate["name"],
                "email": candidate["email"],
                "total_score": scored_data["overall_score"],
                "integrity_penalty": scored_data.get("integrity_penalty", 0.0),
                "metrics": scored_data["metrics"],
                "shapley_values": shapley_results["overall"],
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

    except Exception as e:
        print(f"CRITICAL: Ranking failure: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": f"Failed to execute ranking: {str(e)}"}), 500

@ranking_bp.route("/get-past-results", methods=["GET"])
def get_past_results():
    # don't fetch the massive results_payload here, it'll take ages
    res = supabase.table("past_results").select(
        "id, config_id, summary_data, created_at, matching_configs(name)"
    ).order("created_at", desc=True).execute()
    return jsonify(res.data), 200

@ranking_bp.route("/get-past-result/<snapshot_id>", methods=["GET"])
def get_past_result_detail(snapshot_id):
    res = supabase.table("past_results").select(
        "*, matching_configs(name, job_requirements(title), batch_data(batch_name))"
    ).eq("id", snapshot_id).execute()

    if not res.data:
        return jsonify({"error": "Snapshot not found"}), 404
        
    snapshot = res.data[0]
    config = snapshot.get("matching_configs", {})
    
    return jsonify({
        "id": snapshot["id"],
        "config_name": config.get("name"),
        "job_title": config.get("job_requirements", {}).get("title"),
        "batch_name": config.get("batch_data", {}).get("batch_name"),
        "results": snapshot["results_payload"],
        "is_snapshot": True,
        "created_at": snapshot["created_at"]
    }), 200
