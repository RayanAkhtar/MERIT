"""
Combine Study 03 spacetime charts into one 2-panel figure (left + right).

Reads PNGs from 03-spacetime_study/output/ (produced by generate_spacetime_visualisations.py).
"""
from __future__ import annotations

import os
import shutil
import sys

EVAL_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPORT_CHARTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPORT_CHARTS_DIR)

from panel_utils import combine_horizontal_panels  # noqa: E402

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
STUDY_DIR = os.path.join(EVAL_ROOT, "03-spacetime_study", "output")

PANELS = [
    {
        "panel": "a",
        "path": os.path.join(STUDY_DIR, "spacetime_static_footprint.png"),
    },
    {
        "panel": "b",
        "path": os.path.join(STUDY_DIR, "spacetime_scaling.png"),
    },
]


def _require_chart(path: str) -> None:
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"Missing {path}. Run Study 03 first (03-spacetime_study/run_spacetime.py)."
        )


def generate_combined_chart() -> str:
    for panel in PANELS:
        _require_chart(panel["path"])

    chart_path = os.path.join(OUTPUT_DIR, "spacetime_combined_chart.png")
    combine_horizontal_panels(PANELS, chart_path, figsize=(14.0, 5.6))

    legacy_path = os.path.join(STUDY_DIR, "spacetime_complexity_composite.png")
    shutil.copy2(chart_path, legacy_path)

    print(f"[SUCCESS] {chart_path} generated.")
    print(f"[SUCCESS] {legacy_path} updated (notebook compatibility).")
    return chart_path


if __name__ == "__main__":
    generate_combined_chart()
