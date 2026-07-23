#!/usr/bin/env python3
"""Dedicated, per-exercise diagram generator for chapter 9, subtopic 6.2
(שאלות מילוליות עם ביטוי ריבועי). Each exercise gets a hand-built diagram
with the actual algebraic dimensions from the question text (not a generic
unlabeled ABCD placeholder), matching the values verified in the
quality-check pass.

Run directly: python3 scripts/gen_9_6_2_images.py
"""
from __future__ import annotations

import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle

# NOTE: matplotlib in this environment already renders RTL Hebrew correctly
# via libraqm. Do NOT run python-bidi / get_display() on top of it, or the
# text gets reversed twice and becomes unreadable. rtl_text is therefore an
# identity function (kept only so the ax.text patch below stays a no-op hook
# in case it is ever needed again).
HEBREW_RE = re.compile(r"[\u0590-\u05FF]")


def rtl_text(value):
    return value


_orig_text = Axes.text


def _patched_text(self, x, y, s, *args, **kwargs):
    return _orig_text(self, x, y, rtl_text(s), *args, **kwargs)


Axes.text = _patched_text

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
    ax.text((x1 + x2) / 2, y + offset - 0.32, label, fontsize=fontsize,
            ha="center", va="top", color=NAVY)


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


def ex10():
    # שדה חקלאי מלבני: רוחב x, אורך x+4 (S = x(x+4))
    fig, ax = new_fig(xlim=(0, 13), figsize=(6.8, 4.2))
    x, y, w, h = 1.5, 1.6, 8.5, 4.4
    rect(ax, x, y, w, h, facecolor=GREEN_FILL, alpha=0.5)
    dim_h(ax, x, x + w, y, "x+4")
    dim_v(ax, y, y + h, x, "x")
    ax.text(x + w / 2, y + h + 0.85, "$S = x(x+4)$", fontsize=13, ha="center", color=NAVY, weight="bold")
    save(fig, "9_6.2_ex10.png")


def ex11():
    # גן מלבני: רוחב x, אורך 10-x, גדר (היקף) = 20 מ'
    fig, ax = new_fig(xlim=(0, 12), figsize=(6.4, 4.2))
    x, y, w, h = 1.8, 1.6, 7.5, 4.2
    rect(ax, x, y, w, h, facecolor=BLUE_FILL, alpha=0.5)
    dim_h(ax, x, x + w, y, "10-x")
    dim_v(ax, y, y + h, x, "x")
    ax.text(x + w / 2, y + h + 0.85, 'היקף הגדר = 20 מ׳', fontsize=12, ha="center", color=NAVY, weight="bold")
    save(fig, "9_6.2_ex11.png")


def ex20():
    # מגרש ריבועי: לפני - צלע x+3 ; אחרי הוספת 2 מ' לכל צלע - צלע x+5
    fig, ax = new_fig(xlim=(0, 14), ylim=(0, 8), figsize=(7.2, 4.2))

    x1, y1, s1 = 1.0, 1.6, 3.6
    rect(ax, x1, y1, s1, s1, facecolor=GREEN_FILL, alpha=0.5)
    dim_h(ax, x1, x1 + s1, y1, "x+3", offset=-0.5)
    dim_v(ax, y1, y1 + s1, x1, "x+3", offset=-0.5)
    ax.text(x1 + s1 / 2, y1 + s1 + 0.7, "לפני", fontsize=12, ha="center", color=NAVY, weight="bold")

    x2, y2, s2 = 7.3, 0.9, 5.0
    rect(ax, x2, y2, s2, s2, facecolor=BLUE_FILL, alpha=0.5)
    dim_h(ax, x2, x2 + s2, y2, "x+5", offset=-0.5)
    dim_v(ax, y2, y2 + s2, x2, "x+5", offset=-0.5)
    ax.text(x2 + s2 / 2, y2 + s2 + 0.7, "אחרי (תוספת 2 מ׳ לכל צלע)", fontsize=11, ha="center", color=NAVY, weight="bold")

    save(fig, "9_6.2_ex20.png")


def main():
    for fn in [ex10, ex11, ex20]:
        fn()


if __name__ == "__main__":
    main()
