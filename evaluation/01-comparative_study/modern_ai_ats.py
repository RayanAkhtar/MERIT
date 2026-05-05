import sys
import os
import csv
import json
from typing import List, Dict, Any

# ensure we can import the semantic logic from the backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

from core.scoring.semantic_utils import semantic_matcher

class SemanticATSModel:
    """
    this class replicates a modern ai-powered ats
    unlike the baseline it doesn't just count keywords but uses semantic embeddings
    to understand context
    
    using sentencetransformers here to show that even smart 
    cv-only systems can be fooled without multi-source validation
    """
    
    def __init__(self, job_description: Dict[str, Any]):
        self.jd = job_description
        self.target_skills = []
        metrics = job_description.get("metrics", {})
        for cat in ["Technologies", "Languages"]:
            if cat in metrics:
                self.target_skills.extend([str(k).lower() for k in metrics[cat].get("value", [])])
                
    def score_candidate(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        cv_text = candidate_data.get("raw_cv_text") or candidate_data.get("full_cv_text") or ""
        
        # breaking the cv into chunks to simulate ai context windows
        cv_chunks = [chunk.strip() for chunk in cv_text.replace('.', '\n').split('\n') if len(chunk.strip()) > 5]
        
        if not cv_chunks:
            cv_chunks = [cv_text] # fallback if parsing fails
            
        semantic_hits = {}
        total_semantic_score = 0.0
        
        # simulating vector similarity matching
        for skill in self.target_skills:
            # using the project's internal matcher to simulate the ai layer
            match_result = semantic_matcher.find_best_match(skill, cv_chunks, threshold=0.55)
            
            if match_result["match"]:
                # scoring based on semantic confidence rather than frequency
                score = match_result["score"]
                semantic_hits[skill] = round(score, 2)
                total_semantic_score += score
            else:
                semantic_hits[skill] = 0.0
                
        # total years of experience normalized by ai tools
        total_years = 0
        exp_list = candidate_data.get("experience", [])
        for exp in exp_list:
            total_years += exp.get("years", 0)
            
        jd_min_years = self.jd.get("metrics", {}).get("Experience", {}).get("min_years", 5)
        # normalise years based on the jd requirement
        normalised_years = min(1.0, total_years / jd_min_years) if jd_min_years > 0 else 1.0
            
        # final scoring where semantic context alignment is the highest factor
        final_score = (total_semantic_score * 0.7) + (normalised_years * 0.3 * 10) 
        
        return {
            "candidate_name": candidate_data.get("name"),
            "ai_score": round(final_score, 2),
            "semantic_matches": semantic_hits,
            "total_years": total_years
        }

def export_results(results: List[Dict[str, Any]], filename: str = "modern_ai_ats_rankings.csv"):
    if not results:
        return
    
    os.makedirs("output", exist_ok=True)
    filepath = os.path.join("output", filename)
    
    headers = ["Rank", "Candidate Name", "Modern AI Score", "Total Years"]
    all_skills = set()
    for res in results:
        all_skills.update(res["semantic_matches"].keys())
    
    skill_list = sorted(list(all_skills))
    headers.extend([f"AI Match: {skill}" for skill in skill_list])
    
    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        
        for i, res in enumerate(results):
            row = [
                i + 1,
                res["candidate_name"],
                res["ai_score"],
                res["total_years"]
            ]
            for skill in skill_list:
                row.append(res["semantic_matches"].get(skill, 0))
            writer.writerow(row)
    
    print(f"\n[SUCCESS] Modern AI ATS rankings exported to: {os.path.abspath(filepath)}")

def load_all_candidates():
    # helper to load the test personas from the evaluation data folder
    base_path = os.path.join(os.path.dirname(__file__), 'test_data/candidates')
    cv_dir = os.path.join(base_path, 'cv')
    candidates = []
    
    if not os.path.exists(cv_dir):
        print(f"Error: CV directory not found at {cv_dir}")
        return []

    for filename in os.listdir(cv_dir):
        if filename.endswith(".json"):
            with open(os.path.join(cv_dir, filename), 'r') as f:
                cand = json.load(f)
            candidates.append(cand)
    return candidates

def run_ai_study(candidates: List[Dict[str, Any]], job_description: Dict[str, Any]):
    print("Initialising Semantic Embeddings model... (This simulates modern AI parsing)")
    engine = SemanticATSModel(job_description)
    results = []
    for cand in candidates:
        results.append(engine.score_candidate(cand))
    
    # sort to find the top candidates under the ai model
    results.sort(key=lambda x: x["ai_score"], reverse=True)
    return results

if __name__ == "__main__":
    # pointing to the central jd for the study
    jd_path = os.path.join(os.path.dirname(__file__), 'test_data/job_description/fullstack_developer.json')
    if not os.path.exists(jd_path):
        print(f"Error: JD not found at {jd_path}")
        sys.exit(1)

    with open(jd_path, 'r') as f:
        job_description = json.load(f)
    
    test_candidates = load_all_candidates()
    if test_candidates:
        study_results = run_ai_study(test_candidates, job_description)
        export_results(study_results)
