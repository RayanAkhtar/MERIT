import os
import json
import csv
from typing import List, Dict, Any

def load_job_description(study_path: str) -> Dict[str, Any]:
    jd_path = os.path.join(study_path, 'test_data/job_description/fullstack_developer.json')
    if not os.path.exists(jd_path):
        jd_path = os.path.join(os.path.dirname(study_path), '01-comparative_study/test_data/job_description/fullstack_developer.json')
    
    with open(jd_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_candidates(study_path: str, limit: int = None) -> List[Dict[str, Any]]:
    base_path = os.path.join(study_path, 'test_data/candidates')
    cv_dir = os.path.join(base_path, 'cv')
    
    if not os.path.exists(cv_dir):
        base_path = os.path.join(os.path.dirname(study_path), '01-comparative_study/test_data/candidates')
        cv_dir = os.path.join(base_path, 'cv')
    
    candidates = []
    if not os.path.exists(cv_dir):
        return []

    filenames = [f for f in os.listdir(cv_dir) if f.endswith(".json")]
    print(f"[DATA LOAD] Reading {len(filenames)} candidates from: {os.path.abspath(base_path)}")
    
    if limit and len(filenames) < limit:
        base_files = filenames.copy()
        while len(filenames) < limit:
            filenames.extend(base_files)
    
    if limit:
        filenames = filenames[:limit]

    for filename in filenames:
        cv_path = os.path.join(cv_dir, filename)
        with open(cv_path, 'r', encoding='utf-8') as f:
            cand = json.load(f)
            
            gh_path = os.path.join(base_path, 'github', filename)
            if os.path.exists(gh_path):
                with open(gh_path, 'r', encoding='utf-8') as gh_f:
                    cand["github_enriched"] = json.load(gh_f)
            else:
                cand["github_enriched"] = None
                
            li_path = os.path.join(base_path, 'linkedin', filename)
            if os.path.exists(li_path):
                with open(li_path, 'r', encoding='utf-8') as li_f:
                    cand["linkedin_enriched"] = json.load(li_f)
            else:
                cand["linkedin_enriched"] = None

            if "full_cv_text" not in cand:
                skills_text = ", ".join(cand.get("skills", []))
                
                exp_data = cand.get("experience", [])
                if exp_data is None:
                    exp_data = []
                if isinstance(exp_data, str):
                    exp_text = exp_data
                else:
                    exp_text = " ".join([str(e.get("description", "")) for e in exp_data])
                    
                cand["full_cv_text"] = f"{cand.get('summary', '')} {exp_text} {skills_text}"
            
            candidates.append(cand)
            
    return candidates

def export_to_csv(results: List[Dict[str, Any]], output_path: str):
    if not results:
        return
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    keys = results[0].keys()
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"[SUCCESS] Results exported to {output_path}")
