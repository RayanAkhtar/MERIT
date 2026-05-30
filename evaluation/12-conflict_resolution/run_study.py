import os
import sys
import matplotlib.pyplot as plt
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
backend_path = os.path.join(project_root, "backend")

if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# verify the path is correct
if not os.path.exists(os.path.join(backend_path, "core")):
    # fallback for different environments
    backend_path = os.path.join(project_root, "backend")
    sys.path.insert(0, backend_path)

# pyrefly: ignore [missing-import]
from core.scoring.constants import SCORING_CONSTANTS
# pyrefly: ignore [missing-import]
from core.fusion.bayesian import BayesianEvidenceFusion, Evidence

import json

def run_conflict_resolution_study():
    print("[STUDY 12] Starting Conflict Resolution Verification...")
    
    # load data
    data_dir = os.path.join(os.path.dirname(__file__), "test_data")
    with open(os.path.join(data_dir, "cv", "felix_vance.json"), "r") as f:
        cv_data = json.load(f)
    with open(os.path.join(data_dir, "github", "felix_vance.json"), "r") as f:
        gh_data = json.load(f)
    with open(os.path.join(data_dir, "linkedin", "felix_vance.json"), "r") as f:
        li_data = json.load(f)
    with open(os.path.join(data_dir, "job_description", "fullstack_developer.json"), "r") as f:
        jd_data = json.load(f)

    # extract signals for a core requirement
    target_skill = jd_data["metrics"]["Languages"]["value"][0] # "Java"
    print(f"[INFO] Analyzing multi-source evidence for target skill: {target_skill}")

    # CV: mention in summary and experience
    cv_strength = 1.0 if target_skill in cv_data["summary"] else 0.0
    
    # GitHub: check language history
    gh_skill_percent = next((l["percentage"] for l in gh_data["language_history"] if l["language"] == target_skill), 0)
    gh_strength = gh_skill_percent / 100.0
    
    # LinkedIn: check certifications
    li_strength = 0.8 if any(target_skill in c for l in [li_data.get("certifications", [])] for c in l) else 0.0


    tech_conf = SCORING_CONSTANTS["FUSION"]["SOURCE_CONFIDENCE"]["TECHNICAL_SKILLS"]
    cv_conf = tech_conf["CV"]
    gh_conf = tech_conf["GITHUB"]
    li_conf = tech_conf["LINKEDIN"]
    
    print(f"[INFO] Using backend source confidences: CV={cv_conf}, GitHub={gh_conf}, LinkedIn={li_conf}")

    # create evidence objects
    evidence_steps = [
        Evidence(source="Prior", confidence=1.0, strength=0.0), # Starting point
        Evidence(source="CV (Self-Report)", confidence=cv_conf, strength=cv_strength),
        Evidence(source="GitHub (Evidence)", confidence=gh_conf, strength=gh_strength),
        Evidence(source="LinkedIn (Endorse)", confidence=li_conf, strength=li_strength)
    ]
    
    # 0.1, 0.1 prior - very sensitive to new data (currently what we're using on the frontend)
    fusion = BayesianEvidenceFusion(prior_alpha=0.1, prior_beta=0.1)
    history = []
    
    # initial state for 0.1, 0.1 prior
    # SD for Beta(0.1, 0.1) is approx 0.456
    history.append({
        "step": "Prior",
        "alpha": 0.1,
        "beta": 0.1,
        "score": 0.5,
        "uncertainty": 0.456
    })
    
    # Incremental fusion
    current_evidence = []
    for i in range(1, len(evidence_steps)):
        current_evidence.append(evidence_steps[i])
        result = fusion.fuse(current_evidence)
        history.append({
            "step": evidence_steps[i].source,
            "alpha": result["alpha"],
            "beta": result["beta"],
            "score": result["fused_score"],
            "uncertainty": result["uncertainty"]
        })
    
    # save results to CSV
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    csv_path = os.path.join(output_dir, "bayesian_conflict_resolution.csv")
    with open(csv_path, "w") as f:
        f.write("Step,Alpha (Success),Beta (Conflict),Mean Score,Uncertainty (StdDev)\n")
        for h in history:
            f.write(f"{h['step']},{h['alpha']:.3f},{h['beta']:.3f},{h['score']:.3f},{h['uncertainty']:.3f}\n")
    
    print(f"[SUCCESS] CSV saved to {csv_path}")
    
    # generate plots
    generate_plots(history, output_dir)
    print("[SUCCESS] Plots generated.")

def generate_plots(history, output_dir):
    steps = [h["step"] for h in history]
    scores = [h["score"] for h in history]
    uncertainty = [h["uncertainty"] for h in history]
        
    # PLOT 1: One panel version (only the score change + uncertainty visualisation)
    fig1, ax1_sim = plt.subplots(figsize=(10, 6))
    ax1_sim.plot(steps, scores, marker='o', linestyle='-', linewidth=3, color='#2196F3', label='Fused Score (Mean)')
    ax1_sim.fill_between(steps, 
                         [s - u for s, u in zip(scores, uncertainty)], 
                         [s + u for s, u in zip(scores, uncertainty)], 
                         color='#2196F3', alpha=0.15, label='Uncertainty (1σ)')
    
    for i, (s, u) in enumerate(zip(scores, uncertainty)):
        ax1_sim.vlines(steps[i], s - u, s, linestyles='dotted', colors='black', alpha=0.7, linewidth=1.5)
        ax1_sim.text(steps[i], s - (u/2), f' $\sigma$={u:.3f}', verticalalignment='center', fontsize=9, fontweight='bold')
    
    ax1_sim.set_ylim(0, 1.05)
    ax1_sim.set_title("Bayesian Fusion: Conflict Resolution Walkthrough", fontsize=14, fontweight='bold', pad=15)
    ax1_sim.set_ylabel("Score / Probability", fontsize=12)
    ax1_sim.grid(True, linestyle='--', alpha=0.6)
    ax1_sim.legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "fusion_convergence.png"), dpi=150)
    plt.close(fig1)

    # PLOT 2: Two panel version (score change + uncertainty + bar charts for standard deviation)
    fig2, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 10), gridspec_kw={'height_ratios': [2, 1]})
    
    # Top Panel
    ax1.plot(steps, scores, marker='o', linestyle='-', linewidth=3, color='#2196F3', label='Fused Score (Mean)')
    ax1.fill_between(steps, 
                     [s - u for s, u in zip(scores, uncertainty)], 
                     [s + u for s, u in zip(scores, uncertainty)], 
                     color='#2196F3', alpha=0.15, label='Uncertainty (1σ)')
    
    for i, (s, u) in enumerate(zip(scores, uncertainty)):
        ax1.vlines(steps[i], s - u, s, linestyles='dotted', colors='black', alpha=0.7, linewidth=1.5)
        ax1.text(steps[i], s - (u/2), f' $\sigma$={u:.3f}', verticalalignment='center', fontsize=9, fontweight='bold')
    
    ax1.set_ylim(0, 1.05)
    ax1.set_title("Bayesian Fusion: Conflict Resolution Walkthrough", fontsize=16, fontweight='bold', pad=20)
    ax1.set_ylabel("Score / Probability", fontsize=12)
    ax1.grid(True, linestyle='--', alpha=0.6)
    ax1.legend(loc='upper right', frameon=True)
    
    # Annotations
    ax1.annotate('CV Claim: 100%', xy=(steps[1], scores[1]), xytext=(0.5, 0.95),
                 arrowprops=dict(facecolor='black', shrink=0.08, width=1.5, headwidth=7),
                 fontsize=11, fontweight='bold')
    ax1.annotate('GitHub: 0% (CONFLICT)', xy=(steps[2], scores[2]), xytext=(1.2, 0.2),
                 arrowprops=dict(facecolor='#D32F2F', shrink=0.08, width=1.5, headwidth=7),
                 fontsize=11, fontweight='bold', color='#D32F2F')

    # Bottom Panel
    bars = ax2.bar(steps, uncertainty, color=['#9E9E9E', '#4CAF50', '#FF9800', '#2196F3'], alpha=0.8)
    ax2.set_ylim(0, 0.55)
    ax2.set_ylabel("Uncertainty (σ)", fontsize=12)
    ax2.set_title("Mathematical Uncertainty (Standard Deviation)", fontsize=13, fontweight='bold')
    ax2.grid(axis='y', linestyle='--', alpha=0.6)
    
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                 f'σ={height:.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    eval_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    report_charts = os.path.join(eval_root, "report_charts")
    if report_charts not in sys.path:
        sys.path.insert(0, report_charts)
    from plot_style import add_panel_label  # noqa: E402

    add_panel_label(ax1, "a")
    add_panel_label(ax2, "b")

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "fusion_convergence_detailed.png"), dpi=150)
    plt.close(fig2)
    
    # alpha/beta plot
    plt.figure(figsize=(10, 6))
    x = np.arange(len(steps))
    width = 0.35
    
    alphas = [h["alpha"] for h in history]
    betas = [h["beta"] for h in history]
    
    plt.bar(x - width/2, alphas, width, label='Alpha (Success Signals)', color='#4CAF50')
    plt.bar(x + width/2, betas, width, label='Beta (Conflict/Uncertainty)', color='#F44336')
    
    plt.title("Bayesian Parameter Shift (Dissonance Handling)", fontsize=14, fontweight='bold')
    plt.xticks(x, steps)
    plt.ylabel("Parameter Value", fontsize=12)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "alpha_beta_shift.png"), dpi=150)
    plt.close()

if __name__ == "__main__":
    run_conflict_resolution_study()
