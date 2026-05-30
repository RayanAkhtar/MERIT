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


def _engine_colors(engines) -> list[str]:
    return [
        ICL_NAVY if "MERIT" in e else ICL_ORANGE if "AI" in e else "#888888" for e in engines
    ]


def _plot_static_footprint(ax, df_static: pd.DataFrame) -> None:
    engines = df_static["Engine"].tolist()
    loads = df_static["Static Load (MB)"].tolist()
    colors = _engine_colors(engines)
    x_pos = list(range(len(engines)))

    bars = ax.bar(
        x_pos,
        loads,
        width=0.72,
        color=colors,
        alpha=0.8,
        edgecolor="black",
        linewidth=1,
        align="center",
    )
    ax.set_title("Static Footprint: Initialisation Cost", **TITLE_KW)
    ax.set_ylabel("Memory (MB)", **AXIS_LABEL_KW)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(engines, rotation=30, ha="right")
    ax.tick_params(axis="both", **TICK_KW)
    ax.grid(axis="y", linestyle=":", alpha=0.5)

    max_load = max(loads) if loads else 1.0
    for bar in bars:
        yval = bar.get_height()
        if yval > 0:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                yval + (max_load * 0.02),
                f"{yval:.0f}MB",
                ha="center",
                va="bottom",
                fontsize=8,
                fontweight="bold",
            )
    ax.set_ylim(0, max_load * 1.2)


def _plot_scaling(ax, df_scaling: pd.DataFrame) -> None:
    x = df_scaling["Candidates"]

    ax.plot(
        x,
        df_scaling["Traditional ATS (MB)"],
        marker="o",
        markersize=4,
        label="Traditional ATS",
        color="#888888",
        linestyle="--",
    )
    ax.plot(
        x,
        df_scaling["Modern AI ATS (MB)"],
        marker="s",
        markersize=4,
        label="Modern AI ATS",
        color=ICL_ORANGE,
    )
    ax.plot(
        x,
        df_scaling["MERIT CV-Only (MB)"],
        marker="^",
        markersize=4,
        label="MERIT (CV-Only)",
        color=ICL_GREEN,
    )
    ax.plot(
        x,
        df_scaling["MERIT Full (MB)"],
        marker="D",
        markersize=4,
        label="MERIT (Full)",
        color=ICL_NAVY,
    )
    ax.plot(
        x,
        df_scaling["MERIT Explainable (MB)"],
        marker="*",
        markersize=6,
        label="MERIT (Explainable)",
        color=ICL_RED,
    )

    ax.set_title("Operational Scaling: Memory Overhead", **TITLE_KW)
    ax.set_xlabel("Number of Candidates ($N$)", **AXIS_LABEL_KW)
    ax.set_ylabel("Incremental Memory (MB)", **AXIS_LABEL_KW)
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend(**LEGEND_KW)
    ax.tick_params(axis="both", **TICK_KW)


def generate_spacetime_plots() -> None:
    """Generate per-panel PNGs for Study 03 (combined by report_charts/spacetime_charts)."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(current_dir, "output")
    scaling_data = os.path.join(out_dir, "spacetime_results.csv")
    static_data = os.path.join(out_dir, "engine_load_costs.csv")

    if not os.path.exists(scaling_data) or not os.path.exists(static_data):
        print("Error: Spacetime data not found. Run the study first.")
        return

    df_scaling = pd.read_csv(scaling_data)
    df_static = pd.read_csv(static_data)
    os.makedirs(out_dir, exist_ok=True)

    plt.style.use("default")

    fig1, ax1 = init_panel_figure()
    _plot_static_footprint(ax1, df_static)
    static_path = os.path.join(out_dir, "spacetime_static_footprint.png")
    save_panel(fig1, static_path)

    fig2, ax2 = init_panel_figure()
    _plot_scaling(ax2, df_scaling)
    scaling_path = os.path.join(out_dir, "spacetime_scaling.png")
    save_panel(fig2, scaling_path)

    print(f"[SUCCESS] Static footprint plot saved to {static_path}")
    print(f"[SUCCESS] Scaling plot saved to {scaling_path}")


if __name__ == "__main__":
    import matplotlib

    matplotlib.use("Agg")
    generate_spacetime_plots()
