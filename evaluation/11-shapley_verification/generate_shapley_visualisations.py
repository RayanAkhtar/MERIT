"""
Generates visualisations for Study 11: Shapley Axiom Verification.
"""

import os
import csv
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

STUDY_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(STUDY_DIR, "output")

COLORS = {"CV": "#2196F3", "GitHub": "#4CAF50", "LinkedIn": "#FF9800"}


def _load_csv(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def generate_efficiency_chart():
    """
    Chart 1: Side-by-side bar comparing SUM(phi) vs v(N) per candidate.
    Annotates the delta on each bar pair.
    """
    rows = _load_csv("axiom1_efficiency.csv")
    if not rows:
        return

    names = [r["candidate"] for r in rows]
    phi_sums = [float(r["phi_sum"]) for r in rows]
    full_scores = [float(r["full_match_score"]) for r in rows]

    x = np.arange(len(names))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(x - width/2, phi_sums, width, label=r"$\Sigma\varphi$ (Shapley Sum)", color="#2196F3", alpha=0.85)
    ax.bar(x + width/2, full_scores, width, label="$v(N)$ (Full Score)", color="#FF9800", alpha=0.85)

    # delta = 0 for each pair
    for i in range(len(names)):
        delta = abs(phi_sums[i] - full_scores[i])
        ax.annotate(
            f"$\\Delta$={delta:.0e}",
            xy=(x[i], max(phi_sums[i], full_scores[i]) + 0.015),
            ha="center", fontsize=7, color="#666666"
        )

    ax.set_xlabel("Candidate", fontsize=12)
    ax.set_ylabel("Score", fontsize=12)
    ax.set_title(r"Axiom 1: Efficiency $-$ $\Sigma\varphi_i = v(N)$", fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=45, ha="right", fontsize=9)
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(0, max(max(phi_sums), max(full_scores)) * 1.15)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "axiom1_efficiency.png")
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"[SUCCESS] Saved {out_path}")


def generate_attribution_breakdown():
    """
    Chart 2 (KEY CHART): Stacked horizontal bar showing how each candidate's
    total score decomposes into CV, GitHub, and LinkedIn Shapley contributions.
    This is the most important visualisation for the report — it demonstrates
    the explainability engine in action.
    """
    rows = _load_csv("axiom1_efficiency.csv")
    if not rows:
        return

    # sort by total score ascending (rank 1 at top, rank 10 at bottom)
    rows = sorted(rows, key=lambda r: float(r["full_match_score"]), reverse=False)

    names = [r["candidate"] for r in rows]
    cv_vals = [float(r["phi_cv"]) for r in rows]
    gh_vals = [float(r["phi_github"]) for r in rows]
    li_vals = [float(r["phi_linkedin"]) for r in rows]

    y = np.arange(len(names))
    height = 0.6

    fig, ax = plt.subplots(figsize=(12, 7))

    # handle negative values: separate positive and negative stacking
    # Shapley values can be negative (eg identity fraud)
    cv_pos = [max(0, v) for v in cv_vals]
    cv_neg = [min(0, v) for v in cv_vals]
    gh_pos = [max(0, v) for v in gh_vals]
    gh_neg = [min(0, v) for v in gh_vals]
    li_pos = [max(0, v) for v in li_vals]
    li_neg = [min(0, v) for v in li_vals]

    # positive contributions (stacked right)
    bars_cv = ax.barh(y, cv_pos, height, label="CV", color=COLORS["CV"], alpha=0.85)
    bars_gh = ax.barh(y, gh_pos, height, left=cv_pos, label="GitHub", color=COLORS["GitHub"], alpha=0.85)
    left_li = [c + g for c, g in zip(cv_pos, gh_pos)]
    bars_li = ax.barh(y, li_pos, height, left=left_li, label="LinkedIn", color=COLORS["LinkedIn"], alpha=0.85)

    # negative contributions (stacked left from 0)
    if any(v < 0 for v in cv_neg + gh_neg + li_neg):
        ax.barh(y, cv_neg, height, color=COLORS["CV"], alpha=0.4, hatch="//")
        ax.barh(y, gh_neg, height, left=cv_neg, color=COLORS["GitHub"], alpha=0.4, hatch="//")
        left_li_neg = [c + g for c, g in zip(cv_neg, gh_neg)]
        ax.barh(y, li_neg, height, left=left_li_neg, color=COLORS["LinkedIn"], alpha=0.4, hatch="//")

    def add_labels(vals, left_offsets):
        for i, (v, left) in enumerate(zip(vals, left_offsets)):
            if abs(v) > 0.02:
                x_pos = left + v/2
                ax.text(x_pos, y[i], f"{v:+.3f}", va="center", ha="center", 
                        color="white", fontsize=7.5, fontweight="bold")

    add_labels(cv_vals, [0]*len(names))
    
    # offsets for GitHub labels
    gh_offsets = [cp if gv >= 0 else cn for gv, cp, cn in zip(gh_vals, cv_pos, cv_neg)]
    add_labels(gh_vals, gh_offsets)
    
    # offsets for LinkedIn labels
    li_offsets = [cp + gp if lv >= 0 else cn + gn for lv, cp, cn, gp, gn in zip(li_vals, cv_pos, cv_neg, gh_pos, gh_neg)]
    add_labels(li_vals, li_offsets)

    # annotate total score at the far right of the bar stack (clear of segments)
    for i in range(len(names)):
        total = float(rows[i]["full_match_score"])
        # find the rightmost extent of the positive stack to avoid overlapping bars
        right_extent = cv_pos[i] + gh_pos[i] + li_pos[i]
        ax.text(right_extent + 0.015, y[i], f"{total:.3f}", va="center", fontsize=9, fontweight="bold")

    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=11)
    ax.set_xlabel("Shapley Attribution (Score Contribution)", fontsize=12)
    ax.set_title("Shapley Source Attribution Breakdown per Candidate", fontsize=14, fontweight="bold")
    ax.legend(loc="lower right", fontsize=10)
    ax.grid(axis="x", alpha=0.3)
    ax.axvline(x=0, color="black", linewidth=0.5)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "shapley_attribution_breakdown.png")
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"[SUCCESS] Saved {out_path}")


def generate_source_dominance_pie():
    """
    Chart 3: Pie chart showing aggregate source contribution across all candidates.
    Shows which source (CV, GitHub, LinkedIn) contributes most to the overall pool.
    """
    rows = _load_csv("axiom1_efficiency.csv")
    if not rows:
        return

    total_cv = sum(float(r["phi_cv"]) for r in rows)
    total_gh = sum(float(r["phi_github"]) for r in rows)
    total_li = sum(float(r["phi_linkedin"]) for r in rows)

    # only use positive contributions for pie
    values = [max(0, total_cv), max(0, total_gh), max(0, total_li)]
    labels = ["CV", "GitHub", "LinkedIn"]
    colors = [COLORS["CV"], COLORS["GitHub"], COLORS["LinkedIn"]]

    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, texts, autotexts = ax.pie(
        values, labels=labels, colors=colors, autopct="%1.1f%%",
        startangle=140, textprops={"fontsize": 12},
        wedgeprops={"edgecolor": "white", "linewidth": 2}
    )
    for at in autotexts:
        at.set_fontweight("bold")
        at.set_fontsize(13)

    ax.set_title("Aggregate Source Contribution\n(Shapley Attribution Across All Candidates)",
                 fontsize=13, fontweight="bold")

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "shapley_source_dominance.png")
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"[SUCCESS] Saved {out_path}")


def generate_visualisations():
    print("[VIS] Generating Study 11 visualisations...")
    generate_efficiency_chart()
    generate_attribution_breakdown()
    generate_source_dominance_pie()
    print("[VIS] Done.")


if __name__ == "__main__":
    generate_visualisations()
