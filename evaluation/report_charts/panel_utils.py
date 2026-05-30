"""Shared helpers for equal-size side-by-side appendix panel figures."""
from __future__ import annotations

import os
from typing import Sequence

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from plot_style import PANEL_PIXEL_SIZE

# Identical panel slots in figure coordinates (left, bottom, width, height).
PANEL_SLOT_A = (0.015, 0.04, 0.475, 0.92)
PANEL_SLOT_B = (0.510, 0.04, 0.475, 0.92)
COMBINED_FIGSIZE = (14.0, 5.6)
GRID_2X2_FIGSIZE = (14.0, 13.2)

# 2x2 grid: top row runtime (a,b), bottom row spacetime (c,d).
GRID_2X2_SLOTS = [
    (0.012, 0.502, 0.482, 0.488),  # (a) top-left
    (0.506, 0.502, 0.482, 0.488),  # (b) top-right
    (0.012, 0.010, 0.482, 0.488),  # (c) bottom-left
    (0.506, 0.010, 0.482, 0.488),  # (d) bottom-right
]


def _to_uint8_rgb(img: np.ndarray) -> Image.Image:
    if img.dtype in (np.float32, np.float64) and img.max() <= 1.0:
        arr = (np.clip(img, 0.0, 1.0) * 255).astype(np.uint8)
    else:
        arr = img.astype(np.uint8)
    if arr.ndim == 2:
        arr = np.stack([arr] * 3, axis=-1)
    if arr.shape[-1] == 4:
        arr = arr[..., :3]
    return Image.fromarray(arr)


def _load_panel_image(image_path: str) -> np.ndarray:
    """Load a panel PNG and normalise to the standard pixel canvas."""
    pil = _to_uint8_rgb(mpimg.imread(image_path))
    if pil.size != PANEL_PIXEL_SIZE:
        pil = pil.resize(PANEL_PIXEL_SIZE, Image.Resampling.LANCZOS)
    return np.asarray(pil)


def draw_equal_panel(ax, image_path: str, panel: str) -> None:
    img = _load_panel_image(image_path)
    ax.imshow(img, aspect="auto", interpolation="bilinear")
    ax.set_axis_off()
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


def combine_horizontal_panels(
    panels: Sequence[dict],
    output_path: str,
    *,
    figsize: tuple[float, float] = COMBINED_FIGSIZE,
) -> str:
    if len(panels) != 2:
        raise ValueError("combine_horizontal_panels expects exactly two panels")

    fig = plt.figure(figsize=figsize, dpi=300)
    fig.patch.set_facecolor("white")

    slots = [PANEL_SLOT_A, PANEL_SLOT_B]
    for slot, info in zip(slots, panels):
        ax = fig.add_axes(slot)
        draw_equal_panel(ax, info["path"], info["panel"])

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, facecolor="white")
    plt.close(fig)
    return output_path


def combine_grid_2x2(
    panels: Sequence[dict],
    output_path: str,
    *,
    figsize: tuple[float, float] = GRID_2X2_FIGSIZE,
) -> str:
    if len(panels) != 4:
        raise ValueError("combine_grid_2x2 expects exactly four panels")

    fig = plt.figure(figsize=figsize, dpi=300)
    fig.patch.set_facecolor("white")

    for slot, info in zip(GRID_2X2_SLOTS, panels):
        ax = fig.add_axes(slot)
        draw_equal_panel(ax, info["path"], info["panel"])

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, facecolor="white")
    plt.close(fig)
    return output_path
