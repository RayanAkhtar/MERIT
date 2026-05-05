import sys
import os
import csv
import json
from typing import List, Dict, Any

# link to the backend core to run the real merit logic
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

from core.scoring.registry import scoring_registry

def save_cv_only_results(results: List[Dict[str, Any]], filename: str = "merit_cv_only_rankings.csv"):
    """
    helper to save the results for the cv-only ablation study
    keeping this separate to compare against the full multi-source version later
    """
    if not results:
        return
    
    os.makedirs("output", exist_ok=True)
    filepath = os.path.join("output", filename)
    
    headers = ["Rank", "Candidate Name", "MERIT CV Score (%)", "Total Years", "Has Degree"]
    
    sample_metrics = results[0]["metrics"]
    metric_keys = sorted(list(sample_metrics.keys()))
    headers.extend([f"Metric: {k}" for k in metric_keys])
    
    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        
        for i, res in enumerate(results):
            exp_metric = res["metrics"].get("experience", {})
            total_years = (exp_metric.get("raw_cv_months", 0) / 12.0)
            
            row = [
                i + 1,
                res["name"],
                round(res["total_score"] * 100, 2),
                round(total_years, 2),
                "Yes"
            ]
            
            for k in metric_keys:
                row.append(round(res["metrics"][k].get("score", 0) * 100, 2))
                
            writer.writerow(row)
    
    print(f"\n[SUCCESS] MERIT (CV-Only) rankings exported to: {os.path.abspath(filepath)}")

def load_test_candidates():
    # loading the personas created for the comparative study
    base_path = os.path.join(os.path.dirname(__file__), 'test_data/candidates')
    cv_dir = os.path.join(base_path, 'cv')
    candidates = []
    
    if not os.path.exists(cv_dir):
        return []

    for filename in os.listdir(cv_dir):
        if filename.endswith(".json"):
            with open(os.path.join(cv_dir, filename), 'r') as f:
                cand = json.load(f)
                
            # synthesising full_cv_text so the keyword and semantic logic has a single field to scan
            skills_text = ", ".join(cand.get("skills", []))
            exp_text = " ".join([str(e.get("description", "")) for e in cand.get("experience", [])])
            cand["full_cv_text"] = f"{cand.get('summary', '')} {exp_text} {skills_text}"
            
            candidates.append(cand)
    return candidates

def run_cv_ablation_study(candidates: List[Dict[str, Any]], job_description: Dict[str, Any]):
    """
    core of the ablation study forcing merit to ignore external data
    this shows how the engine behaves when it only has the cv to work with
    """
    results = []
    active_metrics = {}
    weights = {}
    
    # extracting requirements from the jd
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

    # standard metrics for the fyp baseline
    active_metrics["experience"] = True
    weights["experience"] = jd_metrics.get("Experience", {}).get("weight", 0.4)
    
    active_metrics["projects"] = True
    weights["projects"] = 0.5
    
    active_metrics["professional_gravity"] = True
    weights["professional_gravity"] = 0.2
    
    active_metrics["education"] = True
    weights["education"] = jd_metrics.get("Education", {}).get("weight", 0.4)
    
    for candidate in candidates:
        # zero out the external sources for this ablation study
        candidate["github_enriched"] = None
        candidate["linkedin_enriched"] = None
        candidate["linkedin_experience"] = []
        
        # initialise the local scoring parameters
        candidate["active_keys"] = list(active_metrics.keys())
        candidate["skill_weights"] = weights
        
        # run the real merit scoring registry
        scored_data = scoring_registry.run_all(candidate, job_description, active_metrics, weights)
        
        results.append({
            "name": candidate["name"],
            "total_score": scored_data["overall_score"],
            "metrics": scored_data["metrics"]
        })
    
    # sort to see who the cv-only engine prioritises
    results.sort(key=lambda x: x["total_score"], reverse=True)
    return results

if __name__ == "__main__":
    # path to the standard study jd
    jd_path = os.path.join(os.path.dirname(__file__), 'test_data/job_description/fullstack_developer.json')
    with open(jd_path, 'r') as f:
        job_description = json.load(f)
    
    mock_candidates = load_test_candidates()
    
    # set the batch context for normalisation using research dataset values
    for c in mock_candidates:
        c["batch_max_tenure"] = 180
        c["batch_max_cv_tenure"] = 180
        c["batch_max_skill_count"] = 15
        c["batch_max_complexity"] = 50000
        c["batch_max_impact"] = 1000
    
    study_results = run_cv_ablation_study(mock_candidates, job_description)
    save_cv_only_results(study_results)
