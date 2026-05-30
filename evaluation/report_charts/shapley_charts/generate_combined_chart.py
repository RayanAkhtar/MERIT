"""
Combine Study 11 Shapley charts into one 2-panel figure (top + bottom).

Reads the PNGs produced by:
  - 11-shapley_verification/output/shapley_attribution_breakdown.png
  - 11-shapley_verification/output/shapley_source_dominance.png
"""
from __future__ import annotations

import os

import matplotlib.image as mpimg
import matplotlib.pyplot as plt

EVAL_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
STUDY_DIR = os.path.join(EVAL_ROOT, "11-shapley_verification", "output")

BREAKDOWN_CHART = os.path.join(STUDY_DIR, "shapley_attribution_breakdown.png")
DOMINANCE_CHART = os.path.join(STUDY_DIR, "shapley_source_dominance.png")

PANELS = [
    {"panel": "a", "path": BREAKDOWN_CHART},
    {"panel": "b", "path": DOMINANCE_CHART},
]


def _require_chart(path: str) -> None:
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"Missing {path}. Run Study 11 first (11-shapley_verification/run_study.py)."
        )


def generate_combined_chart() -> str:
    for panel in PANELS:
        _require_chart(panel["path"])

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    fig, axes = plt.subplots(
        2,
        1,
        figsize=(12, 11),
        dpi=300,
        gridspec_kw={"height_ratios": [1.6, 1.0]},
    )
    fig.patch.set_facecolor("white")

    for ax, panel in zip(axes, PANELS):
        ax.imshow(mpimg.imread(panel["path"]))
        ax.axis("off")
        # Panel letter only — source PNGs already include chart titles.
        ax.text(
            0.02,
            0.98,
            f"({panel['panel']})",
            transform=ax.transAxes,
            fontsize=12,
            fontweight="bold",
            va="top",
            ha="left",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="none", alpha=1.0),
        )

    fig.tight_layout(h_pad=0.4)

    chart_path = os.path.join(OUTPUT_DIR, "shapley_combined_chart.png")
    plt.savefig(chart_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    print(f"[SUCCESS] {chart_path} generated.")
    return chart_path


if __name__ == "__main__":
    generate_combined_chart()
