"""
Generate Study 13 figures (consensus vs TF-IDF metric prediction).
Requires: run_study.py and populated ground truth.
"""
from __future__ import annotations

import csv
import json
import os
import textwrap
from typing import Any, Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EVAL_ROOT = os.path.dirname(SCRIPT_DIR)
REPORT_CHARTS_DIR = os.path.join(EVAL_ROOT, "report_charts")
if REPORT_CHARTS_DIR not in sys.path:
    sys.path.insert(0, REPORT_CHARTS_DIR)
from plot_style import add_panel_label  # noqa: E402
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
PER_SKILL_CSV = os.path.join(OUTPUT_DIR, "per_skill_results.csv")
REPORT_JSON = os.path.join(OUTPUT_DIR, "evaluation_report.json")
SUMMARY_JSON = os.path.join(SCRIPT_DIR, "test_data", "ground_truth", "recruiter_weights_summary.json")

THEME_BLUE = "#2b5c8f"
THEME_GOLD = "#cca43b"
SUCCESS_GREEN = "#2e7d32"
ALERT_RED = "#c62828"
BG_GRAY = "#eceff1"
HOLDOUT_LABELS = {
    "holdout_01_junior_frontend_react": "Junior Frontend",
    "holdout_02_senior_ml_research": "Senior ML",
    "holdout_04_lead_devops_platform": "Lead DevOps",
}

HOLDOUT_ORDER = list(HOLDOUT_LABELS.keys())

ROLE_SHORT = {
    "holdout_01_junior_frontend_react": "FE",
    "holdout_02_senior_ml_research": "ML",
    "holdout_04_lead_devops_platform": "DevOps",
}

# Chart-only short labels (full strings remain in data / tables).
SKILL_SHORT: Dict[str, str] = {
    "PhD or MSc in Machine Learning, Statistics, or Computer Science": "PhD/MSc requirement",
    "BSc Computer Science or equivalent": "BSc CS (equiv.)",
    "Degree in Computer Science or related field": "CS degree (related)",
}


def _load_rows() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with open(PER_SKILL_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["recruiter_weight"] = int(row["recruiter_weight"])
            row["tfidf_likert"] = int(row["tfidf_likert"])
            row["abs_error"] = int(row["abs_error"])
            row["exact_match"] = row["exact_match"] == "True"
            rows.append(row)
    return rows


def _load_report() -> Dict[str, Any]:
    with open(REPORT_JSON, encoding="utf-8") as f:
        return json.load(f)


def _load_summary() -> List[Dict[str, Any]]:
    with open(SUMMARY_JSON, encoding="utf-8") as f:
        return json.load(f)


def chart_holdout_metrics(report: Dict[str, Any]) -> None:
    holdouts = [h for h in report["holdouts"] if h["holdout_id"] in HOLDOUT_ORDER]
    holdouts.sort(key=lambda h: HOLDOUT_ORDER.index(h["holdout_id"]))
    labels = [HOLDOUT_LABELS[h["holdout_id"]] for h in holdouts]
    mae = [h["mae"] for h in holdouts]
    exact = [h["exact_match_rate"] * 100 for h in holdouts]
    rho = [h["spearman_rho"] for h in holdouts]

    fig, axes = plt.subplots(1, 3, figsize=(12, 4.2))

    x = np.arange(len(labels))
    axes[0].bar(x, mae, color=THEME_BLUE, edgecolor="white", linewidth=0.8)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(labels, rotation=18, ha="right", fontsize=9)
    axes[0].set_ylabel("Mean absolute error (1–5 scale)")
    axes[0].set_title("Calibration error by role", fontweight="bold", fontsize=10)
    axes[0].set_ylim(0, max(mae) * 1.25)
    for i, v in enumerate(mae):
        axes[0].text(i, v + 0.04, f"{v:.2f}", ha="center", fontsize=8)

    axes[1].bar(x, exact, color=THEME_GOLD, edgecolor="white", linewidth=0.8)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels, rotation=18, ha="right", fontsize=9)
    axes[1].set_ylabel("Exact match rate (%)")
    axes[1].set_title("Rounded TF-IDF = consensus", fontweight="bold", fontsize=10)
    axes[1].set_ylim(0, 60)
    for i, v in enumerate(exact):
        axes[1].text(i, v + 1.5, f"{v:.0f}%", ha="center", fontsize=8)

    colors = [SUCCESS_GREEN if r >= 0.5 else THEME_BLUE if r >= 0.3 else ALERT_RED for r in rho]
    axes[2].bar(x, rho, color=colors, edgecolor="white", linewidth=0.8)
    axes[2].axhline(0, color="#666", linewidth=0.8)
    axes[2].set_xticks(x)
    axes[2].set_xticklabels(labels, rotation=18, ha="right", fontsize=9)
    axes[2].set_ylabel("Spearman ρ")
    axes[2].set_title("Ordinal alignment by role", fontweight="bold", fontsize=10)
    axes[2].set_ylim(-0.1, 1.0)
    for i, v in enumerate(rho):
        axes[2].text(i, v + 0.03, f"{v:.2f}", ha="center", fontsize=8)

    agg = report["aggregate"]
    fig.suptitle(
        f"Study 13 — Aggregate: MAE {agg['mae']:.2f}, exact match {agg['exact_match_rate']*100:.1f}%, "
        f"ρ = {agg['spearman_rho']:.2f} (p = {agg['spearman_p']:.3f})",
        fontsize=11,
        fontweight="bold",
        y=1.02,
    )
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "study13_holdout_metrics.png"), dpi=300, bbox_inches="tight")
    plt.close()


def _find_row(rows: List[Dict[str, Any]], skill: str, holdout_id: str | None = None) -> Dict[str, Any] | None:
    for r in rows:
        if r["skill"] != skill:
            continue
        if holdout_id and r.get("holdout_id") != holdout_id:
            continue
        return r
    return None


def chart_scatter(rows: List[Dict[str, Any]]) -> None:
    x = np.array([r["tfidf_likert"] for r in rows], dtype=float)
    y = np.array([r["recruiter_weight"] for r in rows], dtype=float)
    jitter_x = x + np.random.default_rng(13).uniform(-0.1, 0.1, size=len(x))
    jitter_y = y + np.random.default_rng(42).uniform(-0.1, 0.1, size=len(y))
    index = {id(r): i for i, r in enumerate(rows)}

    fig, ax = plt.subplots(figsize=(8.5, 7.5))
    ax.scatter(jitter_x, jitter_y, alpha=0.55, s=55, c=THEME_BLUE, edgecolors="white", linewidths=0.5, zorder=1)
    ax.plot([0.5, 5.5], [0.5, 5.5], "--", color=ALERT_RED, linewidth=1.3, label="Perfect agreement", zorder=2)
    ax.set_xlim(0.75, 5.35)
    ax.set_ylim(0.75, 5.35)
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_xlabel("TF-IDF → UI priority (1 = essential, 5 = optional)")
    ax.set_ylabel("Consensus human priority (1 = essential, 5 = optional)")
    ax.set_title("Consensus vs TF-IDF priorities (pilot, n = 27 skills)", fontweight="bold", pad=12)
    ax.set_aspect("equal")
    ax.grid(True, linestyle=":", alpha=0.35)
    ax.legend(loc="upper left", frameon=True, fontsize=9)

    label_box = dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#b0bec5", alpha=0.94, linewidth=0.8)

    # Curated labels: skill, display name, holdout (optional), offset (dx, dy), ha, highlight
    label_specs: List[Dict[str, Any]] = [
        # Agreement diagonal (essential / near-essential)
        {"skill": "React", "label": "React", "offset": (10, 10), "highlight": True},
        {"skill": "C++", "label": "C++", "offset": (-12, 12), "highlight": True},
        {"skill": "Linux", "holdout": "holdout_04_lead_devops_platform", "label": "Linux", "offset": (12, -14), "highlight": True},
        # Frontend / web cluster (human P-2, TF-IDF P-3–4) — spread offsets to avoid overlap
        {"skill": "JavaScript", "label": "JavaScript", "offset": (-72, -6), "ha": "right"},
        {"skill": "TypeScript", "label": "TypeScript", "offset": (16, -28), "ha": "left"},
        {"skill": "HTML", "label": "HTML", "offset": (-72, 18), "ha": "right"},
        {"skill": "CSS", "label": "CSS", "offset": (16, 22), "ha": "left"},
        # Major language misalignments
        {
            "skill": "Python",
            "holdout": "holdout_02_senior_ml_research",
            "label": "Python (ML)",
            "offset": (14, -38),
            "color": ALERT_RED,
            "highlight": True,
        },
        {
            "skill": "Python",
            "holdout": "holdout_04_lead_devops_platform",
            "label": "Python (DevOps)",
            "offset": (-78, -18),
            "ha": "right",
        },
        # ML / systems
        {"skill": "PyTorch", "label": "PyTorch", "offset": (-70, 8), "ha": "right"},
        {"skill": "CUDA", "label": "CUDA", "offset": (12, 12)},
        {"skill": "Kubernetes", "holdout": "holdout_04_lead_devops_platform", "label": "Kubernetes", "offset": (14, -8)},
        {"skill": "Docker", "label": "Docker", "offset": (-70, -14), "ha": "right"},
        {"skill": "Terraform", "holdout": "holdout_04_lead_devops_platform", "label": "Terraform", "offset": (14, 18)},
        {"skill": "Go", "label": "Go", "offset": (-12, -24)},
        # Data / quant
        {"skill": "Git", "label": "Git", "offset": (12, -10)},
        {"skill": "PostgreSQL", "label": "PostgreSQL", "offset": (-78, -8), "ha": "right"},
        {"skill": "AWS", "label": "AWS", "offset": (14, 6)},
        {"skill": "MLflow", "label": "MLflow", "offset": (-12, 16)},
        {"skill": "Jest", "label": "Jest", "offset": (10, -12)},
        {"skill": "REST", "label": "REST", "offset": (-70, 22), "ha": "right"},
    ]

    for spec in label_specs:
        row = _find_row(rows, spec["skill"], spec.get("holdout"))
        if not row:
            continue
        i = index[id(row)]
        ha = spec.get("ha", "left")
        color = spec.get("color", "#1a237e")
        fontweight = "bold" if spec.get("highlight") else "normal"
        ax.scatter(
            jitter_x[i],
            jitter_y[i],
            s=95 if spec.get("highlight") else 72,
            c=THEME_GOLD if spec.get("highlight") else THEME_BLUE,
            edgecolors="white",
            linewidths=0.8,
            zorder=4,
        )
        ax.annotate(
            spec["label"],
            (jitter_x[i], jitter_y[i]),
            textcoords="offset points",
            xytext=spec["offset"],
            ha=ha,
            fontsize=8 if spec.get("highlight") else 7.5,
            color=color,
            fontweight=fontweight,
            bbox=label_box,
            arrowprops=dict(arrowstyle="-", color="#78909c", lw=0.7, shrinkA=2, shrinkB=2),
            zorder=5,
        )

    # Region guide for dense clusters (no overlap with skill labels)
    ax.text(
        3.7,
        4.35,
        "Hygiene skills\n(human P-4/5)",
        fontsize=7,
        color="#546e7a",
        ha="center",
        style="italic",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="#f5f5f5", edgecolor="none", alpha=0.85),
        zorder=3,
    )
    ax.text(
        1.15,
        1.15,
        "Strong\nagreement",
        fontsize=7,
        color="#546e7a",
        ha="center",
        style="italic",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="#e8f5e9", edgecolor="none", alpha=0.85),
        zorder=3,
    )

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "study13_consensus_vs_tfidf_scatter.png"), dpi=300, bbox_inches="tight")
    plt.close()


def _compact_row_label(holdout_id: str, skill: str) -> str:
    role = ROLE_SHORT.get(holdout_id, HOLDOUT_LABELS.get(holdout_id, holdout_id))
    name = SKILL_SHORT.get(skill, skill)
    return f"{role} · {name}"


def chart_top_misalignments(rows: List[Dict[str, Any]], n_top: int = 12) -> None:
    """Two-panel figure: largest gaps (top) and exact agreements (bottom)."""
    mismatches = sorted(
        [r for r in rows if not r["exact_match"]],
        key=lambda r: r["abs_error"],
        reverse=True,
    )[:n_top]
    matches = sorted(
        [r for r in rows if r["exact_match"]],
        key=lambda r: (HOLDOUT_ORDER.index(r["holdout_id"]), r["skill"]),
    )

    fig = plt.figure(figsize=(10, 8.2))
    gs = fig.add_gridspec(2, 1, height_ratios=[2.35, 1], hspace=0.38)
    ax_gap = fig.add_subplot(gs[0])
    ax_agree = fig.add_subplot(gs[1])

    # --- Panel A: largest mismatches (largest gap at top) ---
    miss_plot = list(reversed(mismatches))
    y_m = np.arange(len(miss_plot))
    errs = [r["abs_error"] for r in miss_plot]
    labels_m = [_compact_row_label(r["holdout_id"], r["skill"]) for r in miss_plot]

    bars = ax_gap.barh(y_m, errs, color=ALERT_RED, alpha=0.88, height=0.62)
    for bar, err in zip(bars, errs):
        if err >= 3:
            bar.set_color("#b71c1c")

    ax_gap.set_yticks(y_m)
    ax_gap.set_yticklabels(labels_m, fontsize=8.5)
    ax_gap.set_xlim(0, 4.5)
    ax_gap.set_xlabel("|Consensus − TF-IDF| on 1–5 scale", fontsize=9)
    ax_gap.set_title(
        f"Largest priority gaps (top {len(miss_plot)} of {sum(1 for r in rows if not r['exact_match'])} mismatches)",
        fontweight="bold",
        fontsize=10,
        pad=8,
    )
    ax_gap.grid(axis="x", linestyle=":", alpha=0.35)
    for i, r in enumerate(miss_plot):
        c, t, e = r["recruiter_weight"], r["tfidf_likert"], r["abs_error"]
        ax_gap.text(
            e + 0.07,
            i,
            f"consensus P-{c}  ·  TF-IDF P-{t}",
            va="center",
            fontsize=7.8,
            color="#263238",
        )

    # --- Panel B: exact matches as a compact agreement strip ---
    n_match = len(matches)
    cols = 3
    rows_grid = int(np.ceil(n_match / cols))
    ax_agree.set_xlim(0, cols)
    ax_agree.set_ylim(0, rows_grid)
    ax_agree.axis("off")
    ax_agree.set_title(
        f"Exact agreement (n = {n_match} of {len(rows)} skill–role pairs)",
        fontweight="bold",
        fontsize=10,
        loc="left",
        pad=6,
    )

    for idx, r in enumerate(matches):
        col = idx % cols
        row_i = rows_grid - 1 - (idx // cols)
        p = r["recruiter_weight"]
        label = _compact_row_label(r["holdout_id"], r["skill"])
        ax_agree.add_patch(
            plt.Rectangle(
                (col + 0.04, row_i + 0.12),
                0.92,
                0.76,
                facecolor="#e8f5e9",
                edgecolor=SUCCESS_GREEN,
                linewidth=1.2,
                alpha=0.95,
            )
        )
        ax_agree.text(
            col + 0.5,
            row_i + 0.62,
            label,
            ha="center",
            va="center",
            fontsize=8,
            color="#1b5e20",
            fontweight="bold",
        )
        ax_agree.text(
            col + 0.5,
            row_i + 0.32,
            f"both P-{p}",
            ha="center",
            va="center",
            fontsize=7.5,
            color="#37474f",
        )

    fig.suptitle("Study 13: consensus vs TF-IDF (gaps and agreements)", fontweight="bold", fontsize=11, y=0.98)
    add_panel_label(ax_gap, "a")
    add_panel_label(ax_agree, "b")
    fig.subplots_adjust(left=0.2, right=0.96, top=0.92, bottom=0.08)
    plt.savefig(os.path.join(OUTPUT_DIR, "study13_top_misalignments.png"), dpi=300)
    plt.close()


def chart_per_role_dumbbell(rows: List[Dict[str, Any]]) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(12, 5.5))
    axes_flat = list(axes)
    for idx, hid in enumerate(HOLDOUT_ORDER):
        ax = axes_flat[idx]
        subset = [r for r in rows if r["holdout_id"] == hid]
        subset.sort(key=lambda r: r["recruiter_weight"], reverse=True)
        skills = [r["skill"][:22] for r in subset]
        human = [r["recruiter_weight"] for r in subset]
        tfidf = [r["tfidf_likert"] for r in subset]
        y = np.arange(len(skills))
        for i, (h, t) in enumerate(zip(human, tfidf)):
            color = SUCCESS_GREEN if h == t else THEME_GOLD if abs(h - t) == 1 else ALERT_RED
            ax.plot([t, h], [i, i], color=color, linewidth=2.5, solid_capstyle="round")
            ax.scatter([t], [i], s=40, color=THEME_BLUE, zorder=3, label="TF-IDF" if i == 0 else "")
            ax.scatter([h], [i], s=40, color=THEME_GOLD, zorder=3, label="Consensus" if i == 0 else "")
        ax.set_yticks(y)
        ax.set_yticklabels(skills, fontsize=7)
        ax.set_xlim(0.5, 5.5)
        ax.set_xticks([1, 2, 3, 4, 5])
        ax.set_title(HOLDOUT_LABELS[hid], fontweight="bold", fontsize=9)
        ax.grid(axis="x", linestyle=":", alpha=0.3)
        if idx == 0:
            ax.legend(loc="lower right", fontsize=7, frameon=True)

    fig.suptitle("Per-role priority profiles: TF-IDF (blue) vs consensus (gold)", fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "study13_per_role_dumbbell.png"), dpi=300, bbox_inches="tight")
    plt.close()


def _wrap_y_label(skill: str, width: int = 38) -> str:
    if len(skill) <= width:
        return skill
    return "\n".join(textwrap.wrap(skill, width=width))


def chart_rater_heatmap(summary: List[Dict[str, Any]], holdout_id: str) -> None:
    """One detailed heatmap for the ML hold-out (largest TF-IDF gaps)."""
    subset = [s for s in summary if s["holdout_id"] == holdout_id]
    skills = [s["skill"] for s in subset]
    y_labels = [_wrap_y_label(s) for s in skills]
    raters = ["R_1", "R_2", "P_1", "P_2"]
    matrix = np.array([[s["rater_weights"][r] for r in raters] for s in subset])

    fig, ax = plt.subplots(figsize=(7, 6.2))
    im = ax.imshow(matrix, aspect="auto", cmap="YlOrRd", vmin=1, vmax=5)
    ax.set_xticks(np.arange(len(raters)))
    ax.set_xticklabels(["Recruiter 1", "Recruiter 2", "Peer 1", "Peer 2"], fontsize=9)
    ax.set_yticks(np.arange(len(skills)))
    ax.set_yticklabels(y_labels, fontsize=7.5)
    ax.set_title(f"Rater weights — {HOLDOUT_LABELS[holdout_id]}", fontweight="bold", pad=10)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(j, i, int(matrix[i, j]), ha="center", va="center", color="black", fontsize=9)
    plt.colorbar(im, ax=ax, label="Priority (1–5)")
    plt.tight_layout()
    out = os.path.join(OUTPUT_DIR, "study13_rater_heatmap_ml.png")
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()


def generate_all() -> List[str]:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if not os.path.isfile(PER_SKILL_CSV):
        raise FileNotFoundError(f"Run run_study.py first — missing {PER_SKILL_CSV}")

    rows = _load_rows()
    report = _load_report()
    summary = _load_summary()

    chart_holdout_metrics(report)
    chart_scatter(rows)
    chart_top_misalignments(rows)
    chart_per_role_dumbbell(rows)
    chart_rater_heatmap(summary, "holdout_02_senior_ml_research")

    names = [
        "study13_holdout_metrics.png",
        "study13_consensus_vs_tfidf_scatter.png",
        "study13_top_misalignments.png",
        "study13_per_role_dumbbell.png",
        "study13_rater_heatmap_ml.png",
    ]
    return names


if __name__ == "__main__":
    created = generate_all()
    print("[Study 13] Wrote charts:")
    for n in created:
        print(f"  - output/{n}")
