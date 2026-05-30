"""
Generate combined figures used in the FYP report appendix.

Run from the evaluation/ directory (or anywhere) after the underlying studies
have produced their per-study outputs.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPORT_CHARTS_DIR = Path(__file__).resolve().parent

GENERATORS = {
    "ingestion": REPORT_CHARTS_DIR / "ingestion_charts" / "generate_combined_chart.py",
    "spearman": REPORT_CHARTS_DIR / "spearman_charts" / "generate_combined_chart.py",
    "shapley": REPORT_CHARTS_DIR / "shapley_charts" / "generate_combined_chart.py",
    "hci": REPORT_CHARTS_DIR / "hci_charts" / "generate_combined_chart.py",
    "bias": REPORT_CHARTS_DIR / "bias_charts" / "generate_combined_chart.py",
    "adversarial": REPORT_CHARTS_DIR / "adversarial_charts" / "generate_combined_chart.py",
    "runtime": REPORT_CHARTS_DIR / "runtime_charts" / "generate_combined_chart.py",
    "spacetime": REPORT_CHARTS_DIR / "spacetime_charts" / "generate_combined_chart.py",
    "scalability": REPORT_CHARTS_DIR / "scalability_charts" / "generate_combined_chart.py",
    "study13_scatter_heatmap": (
        REPORT_CHARTS_DIR / "study13_scatter_heatmap_charts" / "generate_combined_chart.py"
    ),
}


def _run(script: Path) -> None:
    print(f"\n>>> {script.relative_to(REPORT_CHARTS_DIR.parent)}")
    subprocess.run([sys.executable, str(script)], check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate FYP report appendix charts.")
    parser.add_argument(
        "--only",
        choices=[
            "ingestion",
            "spearman",
            "shapley",
            "hci",
            "bias",
            "adversarial",
            "runtime",
            "spacetime",
            "scalability",
            "study13_scatter_heatmap",
            "all",
        ],
        default="all",
        help="Which combined chart(s) to build (default: all).",
    )
    args = parser.parse_args()

    keys = list(GENERATORS) if args.only == "all" else [args.only]
    for key in keys:
        _run(GENERATORS[key])

    print("\n[SUCCESS] Report chart generation complete.")


if __name__ == "__main__":
    main()
