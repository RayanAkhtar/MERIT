import os
import sys

import matplotlib.pyplot as plt
import pandas as pd

EVAL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(EVAL_ROOT, "report_charts"))
from plot_style import (  # noqa: E402
    AXIS_LABEL_KW,
    LEGEND_KW,
    TICK_KW,
    TITLE_KW,
    init_panel_figure,
    save_panel,
)

# Imperial College London Official Palette
ICL_NAVY = "#003E74"
ICL_RED = "#D50032"
ICL_GREEN = "#00853F"
ICL_ORANGE = "#E87722"


def generate_runtime_plots():
    """Publication-quality runtime panels with identical canvas layout."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, "output/runtime_results.csv")

    if not os.path.exists(data_path):
        print(f"Error: Data not found at {data_path}")
        return

    df = pd.read_csv(data_path)

    system_styles = {
        "Traditional ATS (s)": {
            "color": "#888888",
            "marker": "o",
            "ls": "--",
            "label": "Traditional ATS",
        },
        "Modern AI ATS (s)": {
            "color": ICL_ORANGE,
            "marker": "s",
            "ls": "-",
            "label": "Modern AI ATS",
        },
        "MERIT CV-Only (s)": {
            "color": ICL_GREEN,
            "marker": "^",
            "ls": "-",
            "label": "MERIT CV-Only",
        },
        "MERIT Full (s)": {
            "color": ICL_NAVY,
            "marker": "D",
            "ls": "-",
            "label": "MERIT Full",
        },
        "MERIT Explainable (s)": {
            "color": ICL_RED,
            "marker": "*",
            "ls": "-",
            "label": "MERIT Explainable",
        },
    }

    plt.style.use("default")
    x = df["Candidates"]

    fig, ax = init_panel_figure()
    for col, style in system_styles.items():
        if col in df.columns:
            ax.plot(
                x,
                df[col],
                marker=style["marker"],
                label=style["label"],
                color=style["color"],
                linestyle=style["ls"],
                linewidth=2.5 if "MERIT" in style["label"] else 2,
            )

    ax.set_title("Runtime Complexity: Ranking Latency vs Candidate Volume", **TITLE_KW)
    ax.set_xlabel("Number of Candidates ($N$)", **AXIS_LABEL_KW)
    ax.set_ylabel("Execution Time (seconds)", **AXIS_LABEL_KW)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(**LEGEND_KW)
    ax.tick_params(axis="both", **TICK_KW)
    save_panel(fig, os.path.join(current_dir, "output/runtime_complexity_plot.png"))

    fig2, ax2 = init_panel_figure()
    for col, style in system_styles.items():
        if col in df.columns:
            ax2.plot(
                x,
                df[col] / x * 1000,
                marker=style["marker"],
                label=style["label"],
                color=style["color"],
                linestyle=style["ls"],
                linewidth=2,
            )

    ax2.set_title("Algorithmic Efficiency: Latency per 1000 Candidates", **TITLE_KW)
    ax2.set_xlabel("Batch Size ($N$)", **AXIS_LABEL_KW)
    ax2.set_ylabel("Time per 1000 items (ms)", **AXIS_LABEL_KW)
    ax2.set_yscale("log")
    ax2.grid(True, which="both", ls="-", alpha=0.2)
    ax2.legend(**LEGEND_KW)
    ax2.tick_params(axis="both", **TICK_KW)
    output_eff = os.path.join(current_dir, "output/runtime_efficiency_log.png")
    save_panel(fig2, output_eff)
    print(f"[SUCCESS] Efficiency plot saved to {output_eff}")


if __name__ == "__main__":
    import matplotlib

    matplotlib.use("Agg")
    generate_runtime_plots()
