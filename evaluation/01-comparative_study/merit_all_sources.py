import sys
import os
import csv
import json
from typing import List, Dict, Any

# ensure we can link to the backend scoring engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

from core.scoring.registry import scoring_registry

def export_full_study_results(results: List[Dict[str, Any]], filename: str = "merit_all_sources_rankings.csv"):
    """
    export the holistic results of the merit study
    includes the multi-source fusion scores and the shapley values for audit transparency
    """
    if not results:
        return
    
    os.makedirs("output", exist_ok=True)
    filepath = os.path.join("output", filename)
    
    headers = ["Rank", "Candidate Name", "MERIT Total Score", "GitHub Weight", "CV Weight", "Total Years"]
    
    sample_metrics = results[0]["metrics"]
    metric_keys = sorted(list(sample_metrics.keys()))
    headers.extend([f"Metric: {k}" for k in metric_keys])
    
    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        
        for i, res in enumerate(results):
            exp_metric = res["metrics"].get("experience", {})
            total_years = (exp_metric.get("raw_months", 0) / 12.0)
            
            # using shapley values to show which source carried the candidate
            shapley = res.get("shapley_values", {})
            
            row = [
                i + 1,
                res["name"],
                round(res["total_score"] * 100, 2),
                round(shapley.get("GitHub", 0) * 100, 2),
                round(shapley.get("CV", 0) * 100, 2),
                round(total_years, 2)
            ]
            
            for k in metric_keys:
                row.append(round(res["metrics"][k].get("score", 0) * 100, 2))
                
            writer.writerow(row)
    
    print(f"\n[SUCCESS] MERIT (Full) rankings exported to: {os.path.abspath(filepath)}")

def load_all_source_data():
    """
    helper to load the multi-source persona data
    it joins the cv json with external enrichment files from github and linkedin
    """
    base_path = os.path.join(os.path.dirname(__file__), 'test_data/candidates')
    cv_dir = os.path.join(base_path, 'cv')
    candidates = []
    
    if not os.path.exists(cv_dir):
        return []

    for filename in os.listdir(cv_dir):
        if filename.endswith(".json"):
            # load basic cv data
            with open(os.path.join(cv_dir, filename), 'r') as f:
                cand = json.load(f)
            
            # join with github data
            gh_path = os.path.join(base_path, 'github', filename)
            if os.path.exists(gh_path):
                with open(gh_path, 'r') as f:
                    cand["github_enriched"] = json.load(f)
            
            # join with linkedin data
            li_path = os.path.join(base_path, 'linkedin', filename)
            if os.path.exists(li_path):
                with open(li_path, 'r') as f:
                    cand["linkedin_enriched"] = json.load(f)
            
            # synthesising resume text for keyword metrics
            skills_text = ", ".join(cand.get("skills", []))
            exp_text = " ".join([str(e.get("description", "")) for e in cand.get("experience", [])])
            cand["full_cv_text"] = f"{cand.get('summary', '')} {exp_text} {skills_text}"
            
            candidates.append(cand)
    return candidates

def run_full_fusion_study(candidates: List[Dict[str, Any]], job_description: Dict[str, Any]):
    """
    centrepiece of the evaluation running the full merit engine
    calculates weighted averages and adversarial penalties across all 10 candidates
    """
    results = []
    active_metrics = {}
    weights = {}
    
    jd_metrics = job_description.get("metrics", {})
    if "Technologies" in jd_metrics:
        tech_weight = jd_metrics["Technologies"].get("weight", 0.8)
        for tech in jd_metrics["Technologies"].get("value", []):
            clean_tech = tech.lower().replace(" ", "_")
            key = f"req_{clean_tech}"
            active_metrics[key] = True
            weights[key] = tech_weight

    if "Languages" in jd_metrics:
        lang_weight = jd_metrics["Languages"].get("weight", 0.6)
        for lang in jd_metrics["Languages"].get("value", []):
            clean_lang = lang.lower().replace(" ", "_")
            key = f"req_{clean_lang}"
            active_metrics[key] = True
            weights[key] = lang_weight

    # fyp study weightings
    active_metrics["experience"] = True
    weights["experience"] = jd_metrics.get("Experience", {}).get("weight", 0.4)
    
    active_metrics["projects"] = True
    weights["projects"] = 1.5
    
    active_metrics["intel_github_complexity"] = True
    weights["intel_github_complexity"] = 1.2
    
    active_metrics["intel_github_impact"] = True
    weights["intel_github_impact"] = 1.0
    
    active_metrics["intel_github_alignment"] = True
    weights["intel_github_alignment"] = 1.4
    
    active_metrics["professional_gravity"] = True
    weights["professional_gravity"] = 0.2
    
    active_metrics["education"] = True
    weights["education"] = jd_metrics.get("Education", {}).get("weight", 0.4)
    
    for candidate in candidates:
        # pre-process candidate for the scoring registry
        candidate["active_keys"] = list(active_metrics.keys())
        candidate["skill_weights"] = weights
        
        # calculate scores
        scored_data = scoring_registry.run_all(candidate, job_description, active_metrics, weights)
        
        # calculate shapley values for explainability and transparency audit
        from core.scoring.explainability import ShapleyExplainer
        explainer = ShapleyExplainer(scoring_registry)
        shapley_results = explainer.calculate_contributions(candidate, job_description, active_metrics, weights)
        
        results.append({
            "name": candidate["name"],
            "total_score": scored_data["overall_score"],
            "metrics": scored_data["metrics"],
            "shapley_values": shapley_results["overall"]
        })
    
    # sort to determine final project rankings
    results.sort(key=lambda x: x["total_score"], reverse=True)
    return results

if __name__ == "__main__":
    # central jd for the comparative study
    jd_path = "evaluation/01-comparative_study/test_data/job_description/fullstack_developer.json"
    with open(jd_path, 'r') as f:
        job_description = json.load(f)
    
    study_candidates = load_all_source_data()
    
    # normalisation context based on the fyp research dataset
    for c in study_candidates:
        c["batch_max_tenure"] = 180
        c["batch_max_cv_tenure"] = 180
        c["batch_max_skill_count"] = 15
        c["batch_max_complexity"] = 50000
        c["batch_max_impact"] = 1000
    
    full_results = run_full_fusion_study(study_candidates, job_description)
    export_full_study_results(full_results)
