import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(current_dir, '..')))

from engines.traditional_ats import TraditionalATS
from common.utils import load_job_description, load_candidates, export_to_csv

def run_baseline_study():
    print("Running Traditional ATS Baseline Study...")
    jd = load_job_description(current_dir)
    candidates = load_candidates(current_dir)
    
    ats = TraditionalATS(jd)
    results = []
    
    from tqdm.auto import tqdm
    for cand in tqdm(candidates, desc="Scoring Candidates (Baseline ATS)"):
        raw_res = ats.score_candidate(cand)
        results.append({
            "Candidate Name": raw_res["name"],
            "Score": round(raw_res["score"] * 10, 1)
        })
            
    results.sort(key=lambda x: x["Score"], reverse=True)
    
    for i, res in enumerate(results):
        res["Rank"] = i + 1
        
    output_path = os.path.join(current_dir, 'output/baseline_rankings.csv')
    export_to_csv(results, output_path)

if __name__ == "__main__":
    run_baseline_study()
