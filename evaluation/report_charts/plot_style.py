"""Fixed layout for single-panel study charts stitched in the appendix."""
from __future__ import annotations

import os

import matplotlib.pyplot as plt

PANEL_FIGSIZE = (7.0, 5.25)
PANEL_DPI = 300
PANEL_PIXEL_SIZE = (int(PANEL_FIGSIZE[0] * PANEL_DPI), int(PANEL_FIGSIZE[1] * PANEL_DPI))

# Identical axes box on every exported panel (do not use tight_layout).
PANEL_MARGINS = dict(left=0.13, right=0.97, bottom=0.20, top=0.86)

TITLE_KW = dict(fontsize=11, fontweight="bold", pad=10)
AXIS_LABEL_KW = dict(fontsize=10)
TICK_KW = dict(labelsize=9)
LEGEND_KW = dict(fontsize=7.5, loc="upper left", frameon=True, borderaxespad=0.4)


def init_panel_figure():
    fig, ax = plt.subplots(figsize=PANEL_FIGSIZE, dpi=PANEL_DPI)
    fig.patch.set_facecolor("white")
    fig.subplots_adjust(**PANEL_MARGINS)
    return fig, ax


def save_panel(fig, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=PANEL_DPI, facecolor="white")
    plt.close(fig)


def add_panel_label(ax, panel: str) -> None:
    """Appendix-style panel tag in the top-left of an axes."""
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
        zorder=10,
    )
