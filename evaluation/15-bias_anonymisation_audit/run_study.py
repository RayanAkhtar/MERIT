import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "test_data", "responses.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
sys.path.append(os.path.abspath(os.path.join(BASE_DIR, "..")))

from common.utils import load_job_description, load_candidates
from engines.merit_engine import MeritEngine

ICL_NAVY = "#003E74"
VISIBLE_COLOR = "#888888"
BLIND_COLOR = "#2e7d32"
ALERT_RED = "#c62828"

CANDIDATE_KEYS = ["aisling_hunt", "vincent_germain", "riko_altayer", "jude_washington"]
CANDIDATE_LABELS = {
    "aisling_hunt": "Aisling Hunt\n(Junior DS)",
    "vincent_germain": "Vincent Germain\n(Intern)",
    "riko_altayer": "Riko Al-Tayer\n(Senior)",
    "jude_washington": "Jude Washington\n(Junior iOS)",
}


def score_candidates_with_merit():
    jd = load_job_description(BASE_DIR)
    engine = MeritEngine(jd, cv_only=False)
    scores = {}
    file_map = {
        "0138_Aisling_Hunt_Junior_Data_Scientist.json": "aisling_hunt",
        "0203_Vincent_Germain_Intern_Backend_Engineer.json": "vincent_germain",
        "013_Riko_AlTayer_Senior_Backend_Engineer.json": "riko_altayer",
        "0108_Jude_Washington_Junior_iOS_Developer.json": "jude_washington",
    }
    cv_dir = os.path.join(BASE_DIR, "test_data/candidates/cv")
    for fname, key in file_map.items():
        cv_path = os.path.join(cv_dir, fname)
        with open(cv_path, "r", encoding="utf-8") as f:
            cand = json.load(f)
        gh_path = os.path.join(BASE_DIR, "test_data/candidates/github", fname)
        li_path = os.path.join(BASE_DIR, "test_data/candidates/linkedin", fname)
        cand["github_enriched"] = json.load(open(gh_path, encoding="utf-8")) if os.path.exists(gh_path) else None
        cand["linkedin_enriched"] = json.load(open(li_path, encoding="utf-8")) if os.path.exists(li_path) else None
        if "full_cv_text" not in cand:
            cand["full_cv_text"] = cand.get("raw_cv_text", "")
        scores[key] = round(engine.score_candidate(cand)["score"], 2)
    return scores


def load_responses():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_decision(eval_entry):
    ce = eval_entry
    if "decision" in ce:
        return ce["decision"], ce.get("confidence"), ce.get("justification", "")
    return ce["visible_decision"], ce.get("visible_confidence"), ce.get("visible_justification", "")


def human_rank_from_shortlists(shortlist_counts):
    order = sorted(CANDIDATE_KEYS, key=lambda k: (-shortlist_counts[k], k))
    return {k: i + 1 for i, k in enumerate(order)}


def merit_rank(scores):
    order = sorted(CANDIDATE_KEYS, key=lambda k: (-scores[k], k))
    return {k: i + 1 for i, k in enumerate(order)}


def prestige_gap(shortlist_counts, metadata, n_eval):
    high = [k for k in CANDIDATE_KEYS if metadata[k]["proxy_prestige"] in ("elite", "high")]
    low = [k for k in CANDIDATE_KEYS if metadata[k]["proxy_prestige"] in ("mid", "low")]
    avg_high = np.mean([shortlist_counts[k] for k in high]) / n_eval * 100
    avg_low = np.mean([shortlist_counts[k] for k in low]) / n_eval * 100
    return avg_high, avg_low, avg_high - avg_low


def run_study():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    data = load_responses()
    evaluators = data["evaluators"]
    merit_scores = score_candidates_with_merit()
    metadata = data["candidate_metadata"]

    visible_evs = [e for e in evaluators if e.get("ui_condition") == "visible"]
    blind_evs = [e for e in evaluators if e.get("ui_condition") == "blind"]

    visible_shortlists = {k: 0 for k in CANDIDATE_KEYS}
    blind_shortlists = {k: 0 for k in CANDIDATE_KEYS}

    rows = []
    for ev in evaluators:
        cond = ev.get("ui_condition", "visible")
        for key in CANDIDATE_KEYS:
            dec, conf, _ = get_decision(ev["candidate_evaluations"][key])
            if dec == "Shortlist":
                if cond == "visible":
                    visible_shortlists[key] += 1
                else:
                    blind_shortlists[key] += 1
            rows.append({
                "Evaluator": ev["id"],
                "Role": ev["role"],
                "UI Condition": cond,
                "Candidate": key,
                "Decision": dec,
                "Confidence": conf,
                "MERIT Score": merit_scores.get(key, np.nan),
            })

    pd.DataFrame(rows).to_csv(os.path.join(OUTPUT_DIR, "evaluator_decisions.csv"), index=False)

    n_vis = len(visible_evs)
    n_blind = len(blind_evs)
    m_rank = merit_rank(merit_scores)
    v_rank = human_rank_from_shortlists(visible_shortlists)
    b_rank = human_rank_from_shortlists(blind_shortlists)

    m_r = [m_rank[k] for k in CANDIDATE_KEYS]
    rho_visible, p_visible = spearmanr(m_r, [v_rank[k] for k in CANDIDATE_KEYS])
    rho_blind, p_blind = spearmanr(m_r, [b_rank[k] for k in CANDIDATE_KEYS])

    v_high, v_low, v_gap = prestige_gap(visible_shortlists, metadata, n_vis)
    b_high, b_low, b_gap = prestige_gap(blind_shortlists, metadata, n_blind)

    summary_rows = []
    for key in CANDIDATE_KEYS:
        meta = metadata[key]
        v_rate = visible_shortlists[key] / n_vis * 100 if n_vis else 0
        b_rate = blind_shortlists[key] / n_blind * 100 if n_blind else 0
        summary_rows.append({
            "Candidate": meta["display_name"],
            "Key": key,
            "MERIT Score (%)": merit_scores.get(key),
            "MERIT Rank": m_rank[key],
            "Visible Shortlist Rate (%)": round(v_rate, 1),
            "Blind Shortlist Rate (%)": round(b_rate, 1),
            "Delta Rate (pp)": round(b_rate - v_rate, 1),
            "Visible Human Rank": v_rank[key],
            "Blind Human Rank": b_rank[key],
            "Rank Shift (Blind - Visible)": b_rank[key] - v_rank[key],
        })

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(os.path.join(OUTPUT_DIR, "bias_audit_summary.csv"), index=False)

    disparity_df = pd.DataFrame([
        {
            "Metric": "Evaluators per condition",
            "Visible": f"{n_vis} (2 recruiters, 2 peers)",
            "Blind": f"{n_blind} (2 recruiters, 2 peers)",
        },
        {
            "Metric": "Spearman rho (MERIT rank vs human shortlist rank)",
            "Visible": round(rho_visible, 4),
            "Blind": round(rho_blind, 4),
        },
        {
            "Metric": "Mean shortlist rate — prestige-high group (%)",
            "Visible": round(v_high, 1),
            "Blind": round(b_high, 1),
        },
        {
            "Metric": "Mean shortlist rate — prestige-mid/low group (%)",
            "Visible": round(v_low, 1),
            "Blind": round(b_low, 1),
        },
        {
            "Metric": "Prestige gap (high minus mid/low, pp)",
            "Visible": round(v_gap, 1),
            "Blind": round(b_gap, 1),
        },
    ])
    disparity_df.to_csv(os.path.join(OUTPUT_DIR, "disparity_metrics.csv"), index=False)

    print("\n" + "=" * 55)
    print("  STUDY 15: BIAS & ANONYMISATION AUDIT (between-subjects)")
    print("=" * 55)
    print(f"Visible arm: N = {n_vis} | Blind arm: N = {n_blind}")
    print(f"MERIT scores: {merit_scores}")
    print(f"Spearman — Visible: rho={rho_visible:.3f}, Blind: rho={rho_blind:.3f}")
    print(f"Prestige gap — Visible: {v_gap:.1f}pp, Blind: {b_gap:.1f}pp")
    print(summary_df.to_string(index=False))
    print("=" * 55)

    generate_plots(summary_df, visible_shortlists, blind_shortlists, n_vis, n_blind, rho_visible, rho_blind)


def generate_plots(summary_df, visible_shortlists, blind_shortlists, n_vis, n_blind, rho_v, rho_b):
    x = np.arange(len(CANDIDATE_KEYS))
    width = 0.35

    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    v_rates = [visible_shortlists[k] / n_vis * 100 for k in CANDIDATE_KEYS]
    b_rates = [blind_shortlists[k] / n_blind * 100 for k in CANDIDATE_KEYS]
    ax.bar(x - width / 2, v_rates, width, label=f"Visible PII ($N={n_vis}$)", color=VISIBLE_COLOR)
    ax.bar(x + width / 2, b_rates, width, label=f"Blind Mode ($N={n_blind}$)", color=BLIND_COLOR)
    ax.set_ylabel("Shortlist Rate (%)")
    ax.set_title("Study 15: Shortlist Rates by UI Condition (Between-Subjects)", fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([CANDIDATE_LABELS[k] for k in CANDIDATE_KEYS], fontsize=9)
    ax.set_ylim(0, 105)
    ax.legend()
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    for i, (v, b) in enumerate(zip(v_rates, b_rates)):
        ax.text(i - width / 2, v + 2, f"{v:.0f}%", ha="center", fontsize=8)
        ax.text(i + width / 2, b + 2, f"{b:.0f}%", ha="center", fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "bias_shortlist_rates.png"), bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(7, 6), dpi=300)
    merit_ranks = summary_df["MERIT Rank"].values
    v_ranks = summary_df["Visible Human Rank"].values
    b_ranks = summary_df["Blind Human Rank"].values
    short_names = ["AH", "VG", "RA", "JW"]

    ax.plot([1, 4], [1, 4], linestyle="--", color="0.55", linewidth=1.2, label="Perfect agreement (y = x)")
    for i, label in enumerate(short_names):
        ax.scatter(merit_ranks[i], v_ranks[i], s=120, facecolors="white", edgecolors=VISIBLE_COLOR, linewidths=2, zorder=3)
        ax.scatter(merit_ranks[i], b_ranks[i], s=120, color=BLIND_COLOR, zorder=4)
        ax.annotate(label, (merit_ranks[i], b_ranks[i]), xytext=(6, 4), textcoords="offset points", fontsize=9, fontweight="bold")

    ax.scatter([], [], s=120, facecolors="white", edgecolors=VISIBLE_COLOR, linewidths=2, label=f"Visible arm ($N={n_vis}$)")
    ax.scatter([], [], s=120, color=BLIND_COLOR, label=f"Blind arm ($N={n_blind}$)")
    ax.set_xlim(0.6, 4.4)
    ax.set_ylim(4.4, 0.6)
    ax.set_xticks([1, 2, 3, 4])
    ax.set_yticks([1, 2, 3, 4])
    ax.set_xlabel("MERIT rank from automated score (1 = best)", fontsize=10)
    ax.set_ylabel("Human rank from shortlist rates (1 = best)", fontsize=10)
    ax.set_title(
        "Study 15: Human vs MERIT rank by condition\n(between-subjects; $n = 4$ per arm)",
        fontweight="bold",
        fontsize=11,
    )
    ax.grid(True, linestyle=":", alpha=0.4)
    ax.legend(loc="lower right", fontsize=8)
    ax.text(
        0.03, 0.03,
        f"$\\rho_{{visible}}$ = {rho_v:.2f}\n$\\rho_{{blind}}$ = {rho_b:.2f}",
        transform=ax.transAxes, fontsize=9, va="bottom",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor="0.8", alpha=0.9),
    )
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "bias_rank_displacement.png"), bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(6, 4), dpi=300)
    gaps = [summary_df.iloc[i]["Delta Rate (pp)"] for i in range(len(CANDIDATE_KEYS))]
    colors = [BLIND_COLOR if g >= 0 else ALERT_RED for g in gaps]
    ax.barh([CANDIDATE_LABELS[k] for k in CANDIDATE_KEYS], gaps, color=colors)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Shortlist rate difference (Blind arm − Visible arm, pp)")
    ax.set_title("Per-Candidate Rate Shift Between Conditions", fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "bias_blind_uplift.png"), bbox_inches="tight")
    plt.close()

    print("[SUCCESS] Charts saved to output/")


if __name__ == "__main__":
    run_study()
