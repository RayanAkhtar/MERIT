import sys
import os

# Path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(current_dir, '..')))

from engines.modern_ai_ats import SemanticATSModel
from common.utils import load_job_description, load_candidates, export_to_csv

def run_ai_study():
    print("Running Modern AI ATS (Semantic) Study...")
    jd = load_job_description(current_dir)
    candidates = load_candidates(current_dir)
    
    engine = SemanticATSModel(jd)
    results = []
    
    from tqdm.auto import tqdm
    for cand in tqdm(candidates, desc="Scoring Candidates (Modern AI ATS)"):
        raw_res = engine.score_candidate(cand)
        results.append({
            "Candidate Name": raw_res["name"],
            "Modern AI Score": raw_res["score"]
        })
    
    # Sort by score
    results.sort(key=lambda x: x["Modern AI Score"], reverse=True)
    
    # Add rank
    for i, res in enumerate(results):
        res["Rank"] = i + 1
        
    output_path = os.path.join(current_dir, 'output/modern_ai_ats_rankings.csv')
    export_to_csv(results, output_path)

if __name__ == "__main__":
    run_ai_study()
