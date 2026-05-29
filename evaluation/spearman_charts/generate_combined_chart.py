"""
Combine Spearman bar charts from Studies 07--10 into a single 2x2 panel figure.

Reads spearman_results.csv from each study output directory (produced by spearman_utils).
"""
from __future__ import annotations

import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

EVAL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

ENGINE_ORDER = [
    "Traditional ATS",
    "Modern AI ATS",
    "MERIT (CV Only)",
    "MERIT (Full)",
]
ENGINE_COLORS = ["#95a5a6", "#3498db", "#e67e22", "#2ecc71"]

STUDIES = [
    {
        "id": "07",
        "panel": "a",
        "folder": "07-spearman_high_discrimination",
        "title": "Study 07: High Discrimination",
    },
    {
        "id": "08",
        "panel": "b",
        "folder": "08-spearman_seniority_bias_audit",
        "title": "Study 08: Seniority Bias Audit",
    },
    {
        "id": "09",
        "panel": "c",
        "folder": "09-spearman_peer_competition",
        "title": "Study 09: Peer Competition",
    },
    {
        "id": "10",
        "panel": "d",
        "folder": "10-spearman_signal_dissonance_failure_case",
        "title": "Study 10: Signal Dissonance",
    },
]


def _load_results(study_folder: str) -> pd.DataFrame:
    csv_path = os.path.join(EVAL_ROOT, study_folder, "output", "spearman_results.csv")
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(
            f"Missing {csv_path}. Run the corresponding study first (run_study.py)."
        )
    df = pd.read_csv(csv_path)
    df["Engine"] = pd.Categorical(df["Engine"], categories=ENGINE_ORDER, ordered=True)
    return df.sort_values("Engine")


def _plot_panel(ax, results_df: pd.DataFrame, title: str, panel_label: str) -> None:
    sns.barplot(
        x="Engine",
        y="Spearman Rho",
        hue="Engine",
        data=results_df,
        palette=ENGINE_COLORS,
        order=ENGINE_ORDER,
        hue_order=ENGINE_ORDER,
        legend=False,
        width=0.92,
        ax=ax,
    )

    for patch in ax.patches:
        height = patch.get_height()
        ax.annotate(
            f"{height:.3f}",
            (patch.get_x() + patch.get_width() / 2.0, height),
            ha="center",
            va="center",
            xytext=(0, 7),
            textcoords="offset points",
            fontsize=9,
            fontweight="bold",
        )

    ax.set_title(f"({panel_label}) {title}", fontsize=11, fontweight="bold", pad=8)
    ax.set_ylabel("Spearman's ρ", fontsize=10)
    ax.set_xlabel("")
    ax.set_ylim(-1.05, 1.05)
    ax.axhline(0, color="black", linewidth=0.7)
    ax.tick_params(axis="x", rotation=25, labelsize=8)
    ax.tick_params(axis="y", labelsize=9)
    ax.grid(True, axis="y", color="#F0F0F0", linewidth=0.8)


def generate_combined_chart() -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(14, 9), dpi=300)
    fig.patch.set_facecolor("white")
    sns.set_style("whitegrid")

    combined_rows = []
    for study, ax in zip(STUDIES, axes.flat):
        results_df = _load_results(study["folder"])
        _plot_panel(ax, results_df, study["title"], study["panel"])
        for _, row in results_df.iterrows():
            combined_rows.append(
                {
                    "Study": study["id"],
                    "Engine": row["Engine"],
                    "Spearman Rho": row["Spearman Rho"],
                    "P-Value": row["P-Value"],
                    "Candidate Count": row["Candidate Count"],
                }
            )

    fig.tight_layout(h_pad=2.8, w_pad=1.6)

    chart_path = os.path.join(OUTPUT_DIR, "spearman_combined_chart.png")
    plt.savefig(chart_path, dpi=300, bbox_inches="tight")
    plt.close()

    combined_csv = os.path.join(OUTPUT_DIR, "spearman_combined_results.csv")
    pd.DataFrame(combined_rows).to_csv(combined_csv, index=False)

    print(f"[SUCCESS] {chart_path} generated.")
    print(f"[SUCCESS] {combined_csv} generated.")
    return chart_path


if __name__ == "__main__":
    generate_combined_chart()
