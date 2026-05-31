import os
import sys
import re
import json
import csv
import matplotlib.pyplot as plt
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
backend_path = os.path.join(project_root, "backend")

if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

if not os.path.exists(os.path.join(backend_path, "core")):
    backend_path = os.path.join(project_root, "backend")
    sys.path.insert(0, backend_path)

# pyrefly: ignore [missing-import]
from core.scoring.constants import SCORING_CONSTANTS
# pyrefly: ignore [missing-import]
from core.fusion.bayesian import BayesianEvidenceFusion, Evidence

CLAIMED_SOURCE_MAX_STRENGTH = 0.8
CV_MENTION_WEIGHT = 0.2
PRIOR_UNCERTAINTY = 0.456


def _build_cv_text(cv_data: dict) -> str:
    parts = [cv_data.get("summary", "")]
    for exp in cv_data.get("experience", []):
        parts.extend([exp.get("role", ""), exp.get("description", "")])
        parts.extend(exp.get("skills", []))
    parts.extend(cv_data.get("skills", []))
    return " ".join(str(p) for p in parts if p)


def _count_mentions(skill: str, cv_text: str) -> int:
    if not cv_text:
        return 0
    pattern = rf"\b{re.escape(skill.lower())}\b"
    return len(re.findall(pattern, cv_text.lower()))


def _claimed_cv_strength(skill: str, cv_data: dict) -> float:
    mentions = _count_mentions(skill, _build_cv_text(cv_data))
    if mentions <= 0:
        return 0.0
    return min(CLAIMED_SOURCE_MAX_STRENGTH, mentions * CV_MENTION_WEIGHT)


def _github_strength(skill: str, gh_data: dict) -> float:
    gh_skill_percent = next(
        (l["percentage"] for l in gh_data["language_history"] if l["language"] == skill),
        0,
    )
    return gh_skill_percent / 100.0


def _claimed_linkedin_strength(skill: str, li_data: dict) -> float:
    certs = li_data.get("certifications", [])
    has_signal = any(skill.lower() in str(c).lower() for c in certs)
    li_experience = li_data.get("linkedin_experience") or li_data.get("experience") or []
    has_signal = has_signal or any(
        skill.lower() in str(e.get("description", "")).lower() for e in li_experience
    )
    return CLAIMED_SOURCE_MAX_STRENGTH if has_signal else 0.0


def _run_fusion_walkthrough(
    cv_strength: float,
    gh_strength: float,
    li_strength: float,
    cv_conf: float,
    gh_conf: float,
    li_conf: float,
) -> list[dict]:
    evidence_steps = [
        {"step": "Prior", "strength": None, "confidence": None},
        {"step": "CV", "strength": cv_strength, "confidence": cv_conf},
        {"step": "GitHub", "strength": gh_strength, "confidence": gh_conf},
        {"step": "LinkedIn", "strength": li_strength, "confidence": li_conf},
    ]

    fusion = BayesianEvidenceFusion(prior_alpha=0.1, prior_beta=0.1)
    history = [{
        "step": "Prior",
        "strength": None,
        "confidence": None,
        "alpha": 0.1,
        "beta": 0.1,
        "score": 0.5,
        "uncertainty": PRIOR_UNCERTAINTY,
    }]

    current_evidence = []
    for step in evidence_steps[1:]:
        current_evidence.append(Evidence(
            source=step["step"],
            confidence=step["confidence"],
            strength=step["strength"],
        ))
        result = fusion.fuse(current_evidence)
        history.append({
            "step": step["step"],
            "strength": step["strength"],
            "confidence": step["confidence"],
            "alpha": result["alpha"],
            "beta": result["beta"],
            "score": result["fused_score"],
            "uncertainty": result["uncertainty"],
        })

    return history


def _write_walkthrough_csv(history: list[dict], csv_path: str) -> None:
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Step", "Signal Strength", "Source Confidence",
            "Alpha (Success)", "Beta (Conflict)", "Mean Score", "Uncertainty (StdDev)",
        ])
        for h in history:
            strength = "" if h["strength"] is None else f"{h['strength']:.3f}"
            confidence = "" if h["confidence"] is None else f"{h['confidence']:.3f}"
            writer.writerow([
                h["step"], strength, confidence,
                f"{h['alpha']:.3f}", f"{h['beta']:.3f}",
                f"{h['score']:.3f}", f"{h['uncertainty']:.3f}",
            ])


def run_conflict_resolution_study():
    print("[STUDY 12] Starting Conflict Resolution Verification...")

    data_dir = os.path.join(os.path.dirname(__file__), "test_data")
    with open(os.path.join(data_dir, "cv", "felix_vance.json"), "r") as f:
        claims_cv = json.load(f)
    with open(os.path.join(data_dir, "github", "felix_vance.json"), "r") as f:
        claims_gh = json.load(f)
    with open(os.path.join(data_dir, "linkedin", "felix_vance.json"), "r") as f:
        claims_li = json.load(f)
    with open(os.path.join(data_dir, "job_description", "fullstack_developer.json"), "r") as f:
        jd_data = json.load(f)

    target_skill = jd_data["metrics"]["Languages"]["value"][0]
    print(f"[INFO] Analyzing multi-source evidence for target skill: {target_skill}")

    tech_conf = SCORING_CONSTANTS["FUSION"]["SOURCE_CONFIDENCE"]["TECHNICAL_SKILLS"]
    cv_conf = tech_conf["CV"]
    gh_conf = tech_conf["GITHUB"]
    li_conf = tech_conf["LINKEDIN"]

    claims_signals = {
        "cv": _claimed_cv_strength(target_skill, claims_cv),
        "github": _github_strength(target_skill, claims_gh),
        "linkedin": _claimed_linkedin_strength(target_skill, claims_li),
    }
    demo_signals = {"cv": 0.0, "github": 1.0, "linkedin": 0.0}

    print(f"[INFO] Claims-without-demo: CV={claims_signals['cv']}, "
          f"GitHub={claims_signals['github']}, LinkedIn={claims_signals['linkedin']}")
    print(f"[INFO] Demo-without-claims: CV={demo_signals['cv']}, "
          f"GitHub={demo_signals['github']}, LinkedIn={demo_signals['linkedin']}")

    claims_history = _run_fusion_walkthrough(
        claims_signals["cv"], claims_signals["github"], claims_signals["linkedin"],
        cv_conf, gh_conf, li_conf,
    )
    demo_history = _run_fusion_walkthrough(
        demo_signals["cv"], demo_signals["github"], demo_signals["linkedin"],
        cv_conf, gh_conf, li_conf,
    )

    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)

    _write_walkthrough_csv(
        claims_history,
        os.path.join(output_dir, "bayesian_conflict_resolution.csv"),
    )
    _write_walkthrough_csv(
        demo_history,
        os.path.join(output_dir, "bayesian_demonstration_only.csv"),
    )

    comparison_path = os.path.join(output_dir, "bayesian_scenario_comparison.csv")
    with open(comparison_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Scenario", "CV Strength", "GitHub Strength", "LinkedIn Strength",
            "Score After GitHub", "Final Score", "Final Uncertainty",
        ])
        for label, signals, history in [
            ("Claims without demonstration", claims_signals, claims_history),
            ("Demonstration without claims", demo_signals, demo_history),
        ]:
            writer.writerow([
                label,
                f"{signals['cv']:.3f}",
                f"{signals['github']:.3f}",
                f"{signals['linkedin']:.3f}",
                f"{history[2]['score']:.3f}",
                f"{history[-1]['score']:.3f}",
                f"{history[-1]['uncertainty']:.3f}",
            ])

    print(f"[SUCCESS] CSVs saved to {output_dir}")
    generate_plots(claims_history, demo_history, output_dir)
    print("[SUCCESS] Plots generated.")


def _plot_trajectory_panel(ax, steps, scores, uncertainty, color, title, annotations=None):
    ax.plot(steps, scores, marker='o', linestyle='-', linewidth=2, color=color, label='Fused score')
    ax.fill_between(steps,
                    [s - u for s, u in zip(scores, uncertainty)],
                    [s + u for s, u in zip(scores, uncertainty)],
                    color=color, alpha=0.15, label='Uncertainty (1σ)')
    for i, (s, u) in enumerate(zip(scores, uncertainty)):
        ax.vlines(steps[i], s - u, s + u, linestyles='dotted', colors='black', alpha=0.5, linewidth=1)
    ax.set_ylim(0, 1.05)
    ax.set_title(title, fontsize=9.5, fontweight='bold', pad=4)
    ax.set_ylabel("Score / Probability", fontsize=8.5)
    ax.tick_params(labelsize=8)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(loc='upper right', fontsize=6.5, frameon=True)
    if annotations:
        for ann in annotations:
            ax.annotate(**ann)


def _plot_uncertainty_panel(ax, steps, uncertainty, title):
    bar_colors = ['#9E9E9E', '#4CAF50', '#FF9800', '#2196F3']
    bars = ax.bar(steps, uncertainty, color=bar_colors, alpha=0.85)
    ax.set_ylim(0, 0.55)
    ax.set_ylabel("Uncertainty (σ)", fontsize=8.5)
    ax.set_title(title, fontsize=9, fontweight='bold', pad=3)
    ax.tick_params(labelsize=8)
    ax.grid(axis='y', linestyle='--', alpha=0.6)
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2., height + 0.012,
                f'σ={height:.3f}', ha='center', va='bottom', fontsize=7.5, fontweight='bold')


def generate_plots(claims_history, demo_history, output_dir):
    steps = [h["step"] for h in claims_history]
    claims_scores = [h["score"] for h in claims_history]
    demo_scores = [h["score"] for h in demo_history]
    claims_uncertainty = [h["uncertainty"] for h in claims_history]
    demo_uncertainty = [h["uncertainty"] for h in demo_history]

    eval_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    report_charts = os.path.join(eval_root, "report_charts")
    if report_charts not in sys.path:
        sys.path.insert(0, report_charts)
    from plot_style import add_panel_label  # noqa: E402

    claims_color = '#2196F3'
    demo_color = '#4CAF50'
    cv_strength = claims_history[1].get("strength", 0.8)

    fig_simple, ax_simple = plt.subplots(figsize=(10, 6))
    ax_simple.plot(steps, claims_scores, marker='o', linestyle='-', linewidth=3,
                   color=claims_color, label='Claims without demonstration')
    ax_simple.plot(steps, demo_scores, marker='s', linestyle='--', linewidth=2.5,
                   color=demo_color, label='Demonstration without claims')
    ax_simple.set_ylim(0, 1.05)
    ax_simple.set_title("Bayesian Fusion: Claims vs. Demonstration", fontsize=14, fontweight='bold', pad=15)
    ax_simple.set_ylabel("Score / Probability", fontsize=12)
    ax_simple.grid(True, linestyle='--', alpha=0.6)
    ax_simple.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "fusion_convergence.png"), dpi=150)
    plt.close(fig_simple)

    fig, axes = plt.subplots(2, 2, figsize=(12, 4.6), gridspec_kw={'height_ratios': [1.45, 1]})

    _plot_trajectory_panel(
        axes[0, 0], steps, claims_scores, claims_uncertainty, claims_color,
        "Claimed evidence (no demonstration)",
        annotations=[
            dict(text=f'CV claim: {int(cv_strength * 100)}%', xy=(steps[1], claims_scores[1]),
                 xytext=(0.15, 0.93), xycoords='data', textcoords='axes fraction',
                 arrowprops=dict(facecolor='black', shrink=0.08, width=1.0, headwidth=5),
                 fontsize=7.5, fontweight='bold'),
            dict(text='GitHub: 0% (conflict)', xy=(steps[2], claims_scores[2]),
                 xytext=(0.55, 0.12), xycoords='data', textcoords='axes fraction',
                 arrowprops=dict(facecolor='#D32F2F', shrink=0.08, width=1.0, headwidth=5),
                 fontsize=7.5, fontweight='bold', color='#D32F2F'),
        ],
    )
    _plot_uncertainty_panel(axes[1, 0], steps, claims_uncertainty, "Claimed evidence: uncertainty by step")

    _plot_trajectory_panel(
        axes[0, 1], steps, demo_scores, demo_uncertainty, demo_color,
        "Demonstrated evidence (no claims)",
        annotations=[
            dict(text='No CV mention', xy=(steps[1], demo_scores[1]),
                 xytext=(0.15, 0.18), xycoords='data', textcoords='axes fraction',
                 arrowprops=dict(facecolor='#757575', shrink=0.08, width=1.0, headwidth=5),
                 fontsize=7.5, fontweight='bold', color='#616161'),
            dict(text='GitHub: 100%', xy=(steps[2], demo_scores[2]),
                 xytext=(0.55, 0.82), xycoords='data', textcoords='axes fraction',
                 arrowprops=dict(facecolor=demo_color, shrink=0.08, width=1.0, headwidth=5),
                 fontsize=7.5, fontweight='bold', color='#2E7D32'),
        ],
    )
    _plot_uncertainty_panel(axes[1, 1], steps, demo_uncertainty, "Demonstrated evidence: uncertainty by step")

    panel_axes = [axes[0, 0], axes[1, 0], axes[0, 1], axes[1, 1]]
    for ax, label in zip(panel_axes, ("a", "b", "c", "d")):
        add_panel_label(ax, label)

    fig.subplots_adjust(left=0.07, right=0.98, top=0.96, bottom=0.14, hspace=0.55, wspace=0.22)
    fig.savefig(os.path.join(output_dir, "fusion_convergence_detailed.png"), dpi=150, bbox_inches='tight', pad_inches=0.05)
    plt.close(fig)

    plt.figure(figsize=(10, 6))
    x = np.arange(len(steps))
    width = 0.35
    alphas = [h["alpha"] for h in claims_history]
    betas = [h["beta"] for h in claims_history]
    plt.bar(x - width / 2, alphas, width, label='Alpha (Success Signals)', color='#4CAF50')
    plt.bar(x + width / 2, betas, width, label='Beta (Conflict/Uncertainty)', color='#F44336')
    plt.title("Bayesian Parameter Shift (Claims Scenario)", fontsize=14, fontweight='bold')
    plt.xticks(x, steps)
    plt.ylabel("Parameter Value", fontsize=12)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "alpha_beta_shift.png"), dpi=150)
    plt.close()


if __name__ == "__main__":
    run_conflict_resolution_study()
