import sys
import os

# Path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(current_dir, '..')))

from engines.merit_engine import MeritEngine
from common.utils import load_job_description, load_candidates, export_to_csv

def run_cv_ablation_study():
    print("Running MERIT (CV-Only) Ablation Study...")
    jd = load_job_description(current_dir)
    candidates = load_candidates(current_dir)
    
    engine = MeritEngine(jd, cv_only=True)
    results = []
    
    from tqdm.auto import tqdm
    for cand in tqdm(candidates, desc="Scoring Candidates (MERIT CV-Only)"):
        raw_res = engine.score_candidate(cand)
        results.append({
            "Candidate Name": raw_res["name"],
            "MERIT CV Score (%)": raw_res["score"]
        })
    
    # Sort by score
    results.sort(key=lambda x: x["MERIT CV Score (%)"], reverse=True)
    
    # Add rank
    for i, res in enumerate(results):
        res["Rank"] = i + 1
        
    output_path = os.path.join(current_dir, 'output/merit_cv_only_rankings.csv')
    export_to_csv(results, output_path)

if __name__ == "__main__":
    run_cv_ablation_study()
