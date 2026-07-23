#!/usr/bin/env python3
"""Dedicated, per-exercise diagram generator for chapter 9, subtopic 7.2
(פסילת תשובות לפי הגיון הבעיה). Each exercise gets a hand-built diagram
with the actual algebraic dimensions from the question text (not the
generic unlabeled ABCD placeholder / wrong square shape that the shared
generate_ch9_graphs.py picked for these exercises), matching the values
verified in the quality-check pass.

Run directly: python3 scripts/gen_9_7_2_images.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# NOTE: matplotlib in this environment already lays out Hebrew RTL text
# correctly on its own (raqm/harfbuzz shaping). Do NOT run python-bidi's
# get_display() on the strings before handing them to ax.text — doing so
# double-reverses the text and produces garbled output.

REPO_ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = REPO_ROOT / "9 - שאלות מילוליות" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

NAVY = "#1f2937"
GREEN = "#0f766e"
GRAY = "#9ca3af"
BLUE_FILL = "#dbeafe"
GREEN_FILL = "#dcfce7"


def new_fig(xlim=(0, 12), ylim=(0, 8), figsize=(6.4, 4.2)):
    fig, ax = plt.subplots(figsize=figsize, facecolor="white")
    ax.set_facecolor("white")
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def rect(ax, x, y, w, h, edgecolor=NAVY, lw=2, facecolor="none", alpha=1.0, ls="-"):
    ax.add_patch(Rectangle((x, y), w, h, fill=facecolor != "none", facecolor=facecolor,
                            edgecolor=edgecolor, linewidth=lw, alpha=alpha, linestyle=ls))


def dim_h(ax, x1, x2, y, label, offset=-0.55, fontsize=13):
    ax.annotate("", xy=(x1, y + offset), xytext=(x2, y + offset),
                arrowprops=dict(arrowstyle="<->", color=NAVY, lw=1.2))
    if offset < 0:
        text_y, va = y + offset - 0.32, "top"
    else:
        text_y, va = y + offset + 0.32, "bottom"
    ax.text((x1 + x2) / 2, text_y, label, fontsize=fontsize, ha="center", va=va, color=NAVY)


def dim_v(ax, y1, y2, x, label, offset=-0.55, fontsize=13):
    ax.annotate("", xy=(x + offset, y1), xytext=(x + offset, y2),
                arrowprops=dict(arrowstyle="<->", color=NAVY, lw=1.2))
    ax.text(x + offset - 0.28, (y1 + y2) / 2, label, fontsize=fontsize,
            ha="center", va="center", color=NAVY, rotation=90)


def save(fig, name):
    out = IMAGES_DIR / name
    fig.savefig(out, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved", out.name)


def ex12():
    # רוחב חדר x מ' (2x^2 - x - 6 = 0); רק הרוחב נתון בשאלה, האורך אינו נתון.
    fig, ax = new_fig(xlim=(0, 12), figsize=(6.4, 4.2))
    x, y, w, h = 1.8, 1.6, 7.5, 4.2
    rect(ax, x, y, w, h, facecolor=BLUE_FILL, alpha=0.5)
    dim_h(ax, x, x + w, y, "$x$")
    ax.text(x + w / 2, y + h / 2, "חדר", fontsize=12, ha="center", color=NAVY, weight="bold")
    save(fig, "9_7.2_ex12.png")


def ex15():
    # אורך שביל בגן x מ' (3x^2 - 12x + 9 = 0)
    fig, ax = new_fig(xlim=(0, 13), ylim=(0, 6), figsize=(7.2, 3.2))
    x, y, w, h = 1.2, 1.6, 10.2, 1.4
    rect(ax, x, y, w, h, facecolor=GREEN_FILL, alpha=0.55, edgecolor=GREEN)
    dim_h(ax, x, x + w, y, "$x$", offset=-0.9)
    ax.text(x + w / 2, y + h + 0.7, "שביל בגן", fontsize=12, ha="center", color=NAVY, weight="bold")
    save(fig, "9_7.2_ex15.png")


def ex16():
    # שטח ריבוע (x^2 - 8x + 15 = 0), צלע x
    fig, ax = new_fig(xlim=(0, 12), figsize=(6.0, 5.2))
    x, y, s = 3.0, 1.5, 5.5
    rect(ax, x, y, s, s, facecolor=GREEN_FILL, alpha=0.5)
    dim_h(ax, x, x + s, y, "$x$")
    dim_v(ax, y, y + s, x, "$x$")
    ax.text(x + s / 2, y + s / 2, 'שטח הריבוע', fontsize=11, ha="center", va="center", color=GREEN, weight="bold")
    save(fig, "9_7.2_ex16.png")


def ex17():
    # גינה מלבנית: היקף 26 מ', שטח 40 מ"ר; l = אורך, w = רוחב (לא מלבן ריבועי!)
    fig, ax = new_fig(xlim=(0, 13), ylim=(0, 8), figsize=(7.2, 4.4))
    x, y, w, h = 1.5, 1.6, 9.0, 4.0
    rect(ax, x, y, w, h, facecolor=BLUE_FILL, alpha=0.5)
    dim_h(ax, x, x + w, y, "$l$")
    dim_v(ax, y, y + h, x, "$w$")
    ax.text(x + w / 2, y + h + 1.0, 'היקף = 26 מ\', שטח = 40 מ"ר', fontsize=12,
            ha="center", color=NAVY, weight="bold")
    ax.text(x + w / 2, y + h / 2, "גינה", fontsize=11, ha="center", va="center", color=GREEN, weight="bold")
    save(fig, "9_7.2_ex17.png")


def ex20():
    # משולש ישר-זווית: רגליים x ו-x+2, יתר 10
    fig, ax = new_fig(xlim=(0, 12), ylim=(0, 8), figsize=(6.4, 4.2))
    ax_pt, bx_pt, cx_pt = (2.0, 1.5), (8.0, 1.5), (8.0, 6.5)
    ax.plot([ax_pt[0], bx_pt[0]], [ax_pt[1], bx_pt[1]], color=NAVY, linewidth=2.2)
    ax.plot([bx_pt[0], cx_pt[0]], [bx_pt[1], cx_pt[1]], color=NAVY, linewidth=2.2)
    ax.plot([ax_pt[0], cx_pt[0]], [ax_pt[1], cx_pt[1]], color=NAVY, linewidth=2.2)
    ax.plot([bx_pt[0] - 0.5, bx_pt[0] - 0.5, bx_pt[0]], [bx_pt[1], bx_pt[1] + 0.5, bx_pt[1] + 0.5],
            color=NAVY, linewidth=1.3)
    for (px, py), lbl in zip([ax_pt, bx_pt, cx_pt], ["A", "B", "C"]):
        ax.text(px, py, lbl, fontsize=12, weight="bold", ha="center", va="center", color=NAVY,
                bbox=dict(boxstyle="circle,pad=0.15", fc="white", ec="none"))
    ax.text((ax_pt[0] + bx_pt[0]) / 2, ax_pt[1] - 0.55, "$x$", fontsize=13, ha="center", color=NAVY)
    ax.text(bx_pt[0] + 0.55, (bx_pt[1] + cx_pt[1]) / 2, "$x+2$", fontsize=13, ha="center", va="center", color=NAVY)
    ax.text((ax_pt[0] + cx_pt[0]) / 2 - 0.7, (ax_pt[1] + cx_pt[1]) / 2 + 0.35, "$10$", fontsize=13,
            ha="center", color=NAVY)
    save(fig, "9_7.2_ex20.png")


def main():
    for fn in [ex12, ex15, ex16, ex17, ex20]:
        fn()


if __name__ == "__main__":
    main()
