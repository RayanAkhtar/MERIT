import os
import sys
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import spearmanr
from tqdm import tqdm

evaluation_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(evaluation_dir, '../backend'))
sys.path.append(backend_dir)
sys.path.append(evaluation_dir)

from common.utils import load_job_description, load_candidates, export_to_csv
from engines.traditional_ats import TraditionalATS
from engines.modern_ai_ats import SemanticATSModel
from engines.merit_engine import MeritEngine

def run_spearman_analysis(study_dir, human_rank_file, output_dir):
    print(f"\n[SPEARMAN STUDY] Study Dir: {study_dir}")
    
    # load jd
    print(f"  [1/4] Loading Job Description...")
    jd = load_job_description(study_dir)
    
    # load candidates
    print(f"  [2/4] Loading Multi-Source Candidates...")
    cv_dir = os.path.join(study_dir, "test_data/candidates/cv")
    if not os.path.exists(cv_dir):
        print(f"    [ERROR] CV directory not found: {cv_dir}")
        return

    # load human rankings (with encoding robustness)
    human_ordered_files = []
    encodings = ['utf-8', 'utf-16', 'utf-16-le', 'utf-8-sig']
    for enc in encodings:
        try:
            with open(human_rank_file, 'r', encoding=enc) as f:
                content = f.read()
                # Remove nul characters if any (common in utf-16 to utf-8 mess)
                lines = [l.strip().replace('\x00', '') for l in content.splitlines() if l.strip()]
                if lines:
                    human_ordered_files = lines
                    break
        except:
            continue
            
    if not human_ordered_files:
        print(f"    [ERROR] Could not read human rankings from {human_rank_file}")
        return

    human_rank_map = {name: i+1 for i, name in enumerate(human_ordered_files)}
    
    # initialize engines
    print(f"  [3/4] Initialising Ranking Engines...")
    trad_ats = TraditionalATS(jd)
    modern_ats = SemanticATSModel(jd)
    merit_cv = MeritEngine(jd, cv_only=True)
    merit_full = MeritEngine(jd, cv_only=False)
    
    engines = {
        "Traditional ATS": trad_ats,
        "Modern AI ATS": modern_ats,
        "MERIT (CV Only)": merit_cv,
        "MERIT (Full)": merit_full
    }
    
    # score and compare
    print(f"  [4/4] Generating Ranks and Calculating Correlation...")
    engine_scores = {name: {} for name in engines}
    
    filenames = [f for f in os.listdir(cv_dir) if f.endswith(".json")]
    matched_count = 0
    
    for fname in tqdm(filenames, desc="Scoring"):
        pdf_name = fname.replace(".json", ".pdf")
        if pdf_name not in human_rank_map:
            continue
            
        cv_path = os.path.join(cv_dir, fname)
        with open(cv_path, 'r', encoding='utf-8') as jf:
            cand = json.load(jf)
            
        gh_path = os.path.join(study_dir, "test_data/candidates/github", fname)
        cand["github_enriched"] = json.load(open(gh_path, 'r', encoding='utf-8')) if os.path.exists(gh_path) else None
        
        li_path = os.path.join(study_dir, "test_data/candidates/linkedin", fname)
        cand["linkedin_enriched"] = json.load(open(li_path, 'r', encoding='utf-8')) if os.path.exists(li_path) else None
        
        if "full_cv_text" not in cand:
            cand["full_cv_text"] = cand.get("raw_cv_text", "")

        for name, engine in engines.items():
            score_res = engine.score_candidate(cand)
            engine_scores[name][pdf_name] = score_res["score"]
        matched_count += 1
            
    if matched_count == 0:
        print(f"    [ERROR] No candidates matched human rankings. (PDF names in rankings vs filenames mismatch?)")
        print(f"    Ranking samples: {list(human_rank_map.keys())[:3]}")
        print(f"    Candidate samples: {[f.replace('.json', '.pdf') for f in filenames[:3]]}")
        return

    results = []
    for name in engines:
        sorted_files = sorted(engine_scores[name].keys(), key=lambda x: engine_scores[name][x], reverse=True)
        engine_ranking_map = {fname: i+1 for i, fname in enumerate(sorted_files)}
        
        h_ranks = []
        e_ranks = []
        for fname in human_rank_map:
            if fname in engine_ranking_map:
                h_ranks.append(human_rank_map[fname])
                e_ranks.append(engine_ranking_map[fname])
        
        if len(h_ranks) > 1:
            rho, p = spearmanr(h_ranks, e_ranks)
            results.append({
                "Engine": name,
                "Spearman Rho": round(rho, 4),
                "P-Value": round(p, 4),
                "Candidate Count": len(h_ranks)
            })
            
    if not results:
        print(f"    [ERROR] Could not calculate Spearman coefficients.")
        return

    # export results
    os.makedirs(output_dir, exist_ok=True)
    results_df = pd.DataFrame(results)
    output_path = os.path.join(output_dir, "spearman_results.csv")
    results_df.to_csv(output_path, index=False)
    
    detailed_data = []
    all_engine_ranks = {}
    for name in engines:
        sorted_files = sorted(engine_scores[name].keys(), key=lambda x: engine_scores[name][x], reverse=True)
        all_engine_ranks[name] = {fname: i+1 for i, fname in enumerate(sorted_files)}

    for fname in human_rank_map:
        row = {
            "Candidate": fname,
            "Human Rank": human_rank_map[fname]
        }
        for name in engines:
            if fname in engine_scores[name]:
                row[f"{name} Score"] = round(engine_scores[name][fname], 2)
                row[f"{name} Rank"] = all_engine_ranks[name].get(fname, "N/A")
            else:
                row[f"{name} Score"] = "N/A"
                row[f"{name} Rank"] = "N/A"
        detailed_data.append(row)
    
    detailed_df = pd.DataFrame(detailed_data)

    # Sort by human rank for readability
    detailed_df = detailed_df.sort_values("Human Rank")
    detailed_output_path = os.path.join(output_dir, "detailed_rankings.csv")
    detailed_df.to_csv(detailed_output_path, index=False)
    print(f"  [Detailed] Candidate breakdown saved to: {detailed_output_path}")
    

    print(f"  [V] Generating Bar Chart...")
    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")
    
    colors = ["#95a5a6", "#3498db", "#e67e22", "#2ecc71"]
    
    ax = sns.barplot(x="Engine", y="Spearman Rho", data=results_df, palette=colors)
    
    for p in ax.patches:
        ax.annotate(format(p.get_height(), '.3f'), 
                   (p.get_x() + p.get_width() / 2., p.get_height()), 
                   ha = 'center', va = 'center', 
                   xytext = (0, 9), 
                   textcoords = 'offset points',
                   fontsize=11, fontweight='bold')

    study_name = os.path.basename(os.path.dirname(output_dir)).replace("-", " ").title()
    plt.title(f"Spearman's Rank Correlation: {study_name}", fontsize=15, pad=20)
    plt.ylabel("Spearman's Rho (ρ)", fontsize=12)
    plt.xlabel("Ranking Engine", fontsize=12)
    plt.ylim(-1.1, 1.1)
    plt.axhline(0, color='black', linewidth=0.8)
    
    chart_path = os.path.join(output_dir, "spearman_chart.png")
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\n[SUCCESS] Spearman Analysis Complete ({matched_count} candidates matched).")
    print(results_df.to_string(index=False))

if __name__ == "__main__":
    pass
