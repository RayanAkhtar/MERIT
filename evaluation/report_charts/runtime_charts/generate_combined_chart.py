"""
Combine Study 02 runtime charts into one 2-panel figure (left + right).

Reads PNGs from 02-runtime_study/output/.
"""
from __future__ import annotations

import os
import sys

EVAL_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPORT_CHARTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPORT_CHARTS_DIR)

from panel_utils import combine_horizontal_panels  # noqa: E402

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
STUDY_DIR = os.path.join(EVAL_ROOT, "02-runtime_study", "output")

PANELS = [
    {"panel": "a", "path": os.path.join(STUDY_DIR, "runtime_complexity_plot.png")},
    {"panel": "b", "path": os.path.join(STUDY_DIR, "runtime_efficiency_log.png")},
]


def _require_chart(path: str) -> None:
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"Missing {path}. Run Study 02 first (02-runtime_study/run_runtime.py)."
        )


def generate_combined_chart() -> str:
    for panel in PANELS:
        _require_chart(panel["path"])

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    chart_path = os.path.join(OUTPUT_DIR, "runtime_combined_chart.png")
    combine_horizontal_panels(PANELS, chart_path, figsize=(14.0, 5.6))

    print(f"[SUCCESS] {chart_path} generated.")
    return chart_path


if __name__ == "__main__":
    generate_combined_chart()
