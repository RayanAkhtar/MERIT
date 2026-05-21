import os
import sys
import json
import pandas as pd

# Add the evaluation directory to path to reach engines
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(current_dir, "../")))

from engines.merit_engine import MeritEngine

def run_adversarial_benchmark():
    jd_path = os.path.join(current_dir, "test_data/job_description/fullstack_developer.json")
    with open(jd_path, 'r', encoding='utf-8') as f:
        jd = json.load(f)

    engine_cv_only = MeritEngine(jd, cv_only=True)
    engine_full = MeritEngine(jd, cv_only=False)

    cv_dir = os.path.join(current_dir, "test_data/cvs")
    gh_dir = os.path.join(current_dir, "test_data/github")
    li_dir = os.path.join(current_dir, "test_data/linkedin")

    results = []

    scenarios = [
        ("Honest", "honest"),
        ("Ghost", "ghost"),
        ("Fraud", "fraud"),
        ("Stale", "stale"),
        ("Gamer", "gamer"),
        ("Squatter", "squatter"),
        ("Smart Squatter", "smart_squatter"),
        ("Shadow", "shadow"),
        ("Inflater", "inflater")
    ]

    for label, sc in scenarios:
        with open(os.path.join(cv_dir, f"{sc}_cv.json"), 'r', encoding='utf-8') as f:
            cv = json.load(f)
        with open(os.path.join(gh_dir, f"{sc}_gh.json"), 'r', encoding='utf-8') as f:
            gh = json.load(f)
        with open(os.path.join(li_dir, f"{sc}_li.json"), 'r', encoding='utf-8') as f:
            li = json.load(f)

        candidate = cv.copy()
        candidate["github_enriched"] = gh
        candidate["linkedin_enriched"] = li

        # Score with CV-Only (ATS Baseline)
        res_cv = engine_cv_only.score_candidate(candidate)
        
        # Score with Full Merit (Multi-Source)
        res_full = engine_full.score_candidate(candidate)

        results.append({
            "Scenario": label,
            "Candidate": cv["name"],
            "ATS Score (CV Only)": round(res_cv["score"], 1),
            "MERIT Score (Multi-Source)": round(res_full["score"], 1),
            "Delta Fusion": round(res_full["score"] - res_cv["score"], 1),
        })

    df = pd.DataFrame(results)
    honest_full = df.loc[df["Scenario"] == "Honest", "MERIT Score (Multi-Source)"].iloc[0]
    honest_cv = df.loc[df["Scenario"] == "Honest", "ATS Score (CV Only)"].iloc[0]
    df["Delta vs Honest (Full)"] = (df["MERIT Score (Multi-Source)"] - honest_full).round(1)
    df["Delta vs Honest (CV Only)"] = (df["ATS Score (CV Only)"] - honest_cv).round(1)
    output_path = os.path.join(current_dir, "output/multi_source_adversarial_matrix.csv")
    df.to_csv(output_path, index=False)

    print("\n--- Adversarial Benchmark Results ---")
    print(df.to_string(index=False))
    print(f"\nResults saved to {output_path}")

if __name__ == "__main__":
    run_adversarial_benchmark()
