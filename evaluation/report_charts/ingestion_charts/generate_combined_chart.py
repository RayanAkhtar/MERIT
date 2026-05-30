"""
Combine CV and JD ingestion accuracy charts (Studies 04 & 05) into one 2-panel figure.

Reads the PNGs produced by:
  - 04-ir_parser_test/output/ir_parser_accuracy.png
  - 05-jd_parser_test/output/jd_parser_accuracy.png
"""
from __future__ import annotations

import os
import sys

import matplotlib.image as mpimg
import matplotlib.pyplot as plt

REPORT_CHARTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPORT_CHARTS_DIR)
from plot_style import add_panel_label  # noqa: E402

EVAL_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

PANELS = [
    {
        "panel": "a",
        "path": os.path.join(EVAL_ROOT, "04-ir_parser_test", "output", "ir_parser_accuracy.png"),
    },
    {
        "panel": "b",
        "path": os.path.join(EVAL_ROOT, "05-jd_parser_test", "output", "jd_parser_accuracy.png"),
    },
]


def _require_chart(path: str) -> None:
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"Missing {path}. Run Studies 04 and 05 first (run_study.py in each folder)."
        )


def generate_combined_chart() -> str:
    for panel in PANELS:
        _require_chart(panel["path"])

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    fig, axes = plt.subplots(2, 1, figsize=(12, 13), dpi=300)
    fig.patch.set_facecolor("white")

    for ax, panel in zip(axes, PANELS):
        ax.imshow(mpimg.imread(panel["path"]))
        ax.axis("off")
        add_panel_label(ax, panel["panel"])

    fig.tight_layout(h_pad=0.6)

    chart_path = os.path.join(OUTPUT_DIR, "ingestion_combined_chart.png")
    plt.savefig(chart_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    print(f"[SUCCESS] {chart_path} generated.")
    return chart_path


if __name__ == "__main__":
    generate_combined_chart()
