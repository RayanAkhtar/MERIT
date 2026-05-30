"""
Combine Studies 02 and 03 into one 2x2 appendix figure.

Top row: runtime latency + efficiency (a--b).
Bottom row: spacetime static footprint + scaling (c--d).
"""
from __future__ import annotations

import os
import sys

EVAL_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPORT_CHARTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPORT_CHARTS_DIR)

from panel_utils import combine_grid_2x2  # noqa: E402

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
RUNTIME_DIR = os.path.join(EVAL_ROOT, "02-runtime_study", "output")
SPACETIME_DIR = os.path.join(EVAL_ROOT, "03-spacetime_study", "output")

PANELS = [
    {"panel": "a", "path": os.path.join(RUNTIME_DIR, "runtime_complexity_plot.png")},
    {"panel": "b", "path": os.path.join(RUNTIME_DIR, "runtime_efficiency_log.png")},
    {"panel": "c", "path": os.path.join(SPACETIME_DIR, "spacetime_static_footprint.png")},
    {"panel": "d", "path": os.path.join(SPACETIME_DIR, "spacetime_scaling.png")},
]


def _require_chart(path: str) -> None:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Missing {path}. Run Studies 02 and 03 first.")


def generate_combined_chart() -> str:
    for panel in PANELS:
        _require_chart(panel["path"])

    chart_path = os.path.join(OUTPUT_DIR, "scalability_combined_chart.png")
    combine_grid_2x2(PANELS, chart_path)

    print(f"[SUCCESS] {chart_path} generated.")
    return chart_path


if __name__ == "__main__":
    generate_combined_chart()
