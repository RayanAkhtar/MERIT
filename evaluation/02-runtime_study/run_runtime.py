import sys
import os
import time
import pandas as pd

# Path setup to reach shared engines and common utils
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(current_dir, '..')))

from engines.traditional_ats import TraditionalATS
from engines.modern_ai_ats import SemanticATSModel
from engines.merit_engine import MeritEngine
from common.utils import load_job_description, load_candidates

def benchmark_runtime():
    jd = load_job_description(current_dir)
    candidate_counts = [10, 50, 100, 200, 500]
    
    results = []

    # Initialising engines
    print("Initialising engines...")
    trad_ats = TraditionalATS(jd)
    modern_ats = SemanticATSModel(jd)
    merit_cv = MeritEngine(jd, cv_only=True)
    merit_full = MeritEngine(jd, cv_only=False)
    merit_exp = MeritEngine(jd, cv_only=False, explainable=True)

    from tqdm.auto import tqdm

    for count in candidate_counts:
        print(f"\nBenchmarking with {count} candidates...")
        candidates = load_candidates(current_dir, limit=count)
        
        # 1. Traditional ATS
        start = time.time()
        for c in tqdm(candidates, desc="Traditional ATS", leave=False):
            trad_ats.score_candidate(c)
        trad_time = time.time() - start
        
        # 2. Modern AI ATS
        start = time.time()
        for c in tqdm(candidates, desc="Modern AI ATS", leave=False):
            modern_ats.score_candidate(c)
        modern_time = time.time() - start
        
        # 3. MERIT (CV-Only)
        start = time.time()
        for c in tqdm(candidates, desc="MERIT CV-Only", leave=False):
            merit_cv.score_candidate(c)
        merit_cv_time = time.time() - start
        
        # 4. MERIT (Full)
        start = time.time()
        for c in tqdm(candidates, desc="MERIT Full", leave=False):
            merit_full.score_candidate(c)
        merit_full_time = time.time() - start
        
        # 5. MERIT (Explainable)
        start = time.time()
        for c in tqdm(candidates, desc="MERIT Explainable", leave=False):
            merit_exp.score_candidate(c)
        merit_exp_time = time.time() - start
        
        results.append({
            "Candidates": count,
            "Traditional ATS (s)": round(trad_time, 4),
            "Modern AI ATS (s)": round(modern_time, 4),
            "MERIT CV-Only (s)": round(merit_cv_time, 4),
            "MERIT Full (s)": round(merit_full_time, 4),
            "MERIT Explainable (s)": round(merit_exp_time, 4)
        })

    # Save results
    df = pd.DataFrame(results)
    output_path = os.path.join(current_dir, "output/runtime_results.csv")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print("\n--- Runtime Study Complete ---")
    print(df.to_string(index=False))
    print(f"\nResults saved to {output_path}")
    
    print(f"\nResults saved to {output_path}")

if __name__ == "__main__":
    benchmark_runtime()
    
    # Generate Visualisations (only when run as a standalone script)
    try:
        from generate_runtime_visualisations import generate_runtime_plots
        generate_runtime_plots()
    except Exception as e:
        print(f"Warning: Could not generate plots: {e}")
