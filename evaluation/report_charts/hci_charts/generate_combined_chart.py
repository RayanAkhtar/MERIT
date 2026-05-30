"""
Combine Study 14 HCI charts into one 3-panel figure.

Layout (top to bottom): decision reversals (a) | confidence calibration (b) | SUS (c)

Reads PNGs from 14-hci_trial/output/.
"""
from __future__ import annotations

import os

import matplotlib.image as mpimg
import matplotlib.pyplot as plt

EVAL_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
STUDY_DIR = os.path.join(EVAL_ROOT, "14-hci_trial", "output")

PANELS = [
    {"panel": "a", "path": os.path.join(STUDY_DIR, "hci_decision_reversals.png")},
    {"panel": "b", "path": os.path.join(STUDY_DIR, "hci_confidence_calibration.png")},
    {"panel": "c", "path": os.path.join(STUDY_DIR, "hci_sus_distribution.png")},
]


def _require_chart(path: str) -> None:
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"Missing {path}. Run Study 14 first (14-hci_trial/run_study.py)."
        )


def _draw_panel(ax, panel: str, image_path: str) -> None:
    ax.imshow(mpimg.imread(image_path))
    ax.axis("off")
    ax.text(
        0.02,
        0.98,
        f"({panel})",
        transform=ax.transAxes,
        fontsize=12,
        fontweight="bold",
        va="top",
        ha="left",
        bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="none", alpha=1.0),
    )


def generate_combined_chart() -> str:
    for panel in PANELS:
        _require_chart(panel["path"])

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    fig, axes = plt.subplots(
        3,
        1,
        figsize=(9.5, 8.6),
        dpi=300,
        gridspec_kw={"height_ratios": [1.0, 1.0, 0.72]},
    )
    fig.patch.set_facecolor("white")

    for ax, panel in zip(axes, PANELS):
        _draw_panel(ax, panel["panel"], panel["path"])

    fig.subplots_adjust(left=0.02, right=0.98, top=0.99, bottom=0.01, hspace=0.06)

    chart_path = os.path.join(OUTPUT_DIR, "hci_combined_chart.png")
    plt.savefig(chart_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    print(f"[SUCCESS] {chart_path} generated.")
    return chart_path


if __name__ == "__main__":
    generate_combined_chart()
