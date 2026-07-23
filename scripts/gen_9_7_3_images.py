#!/usr/bin/env python3
"""Dedicated, per-exercise diagram generator for chapter 9, subtopic 7.3
(סימולציה: שאלות גמר מקיפות של מה"ט). Only exercises that actually describe
a geometric shape get a hand-built diagram with the real numeric/algebraic
dimensions from the (corrected) question text - unlike the generic identical
ABCD placeholder that generate_ch9_graphs.py used to attach to every single
exercise regardless of content.

Exercises without a geometric shape (discounts, ticket prices, mixtures,
interest, etc.) intentionally get no image, matching the convention used
elsewhere in this chapter (e.g. 3.2, 7.2).

Run directly: python3 scripts/gen_9_7_3_images.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# NOTE: matplotlib in this environment already lays out Hebrew RTL text
# correctly on its own (raqm/harfbuzz shaping). Do NOT run python-bidi's
# get_display() on the strings before handing them to ax.text - doing so
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


def dim_h(ax, x1, x2, y, label, offset=-0.55, fontsize=12):
    ax.annotate("", xy=(x1, y + offset), xytext=(x2, y + offset),
                arrowprops=dict(arrowstyle="<->", color=NAVY, lw=1.2))
    if offset < 0:
        text_y, va = y + offset - 0.32, "top"
    else:
        text_y, va = y + offset + 0.32, "bottom"
    ax.text((x1 + x2) / 2, text_y, label, fontsize=fontsize,
            ha="center", va=va, color=NAVY)


def dim_v(ax, y1, y2, x, label, offset=-0.55, fontsize=12):
    ax.annotate("", xy=(x + offset, y1), xytext=(x + offset, y2),
                arrowprops=dict(arrowstyle="<->", color=NAVY, lw=1.2))
    ax.text(x + offset - 0.25, (y1 + y2) / 2, label, fontsize=fontsize,
            ha="center", va="center", color=NAVY, rotation=90)


def corner_labels(ax, x, y, w, h, labels=("A", "B", "C", "D")):
    pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    for (px, py), lbl in zip(pts, labels):
        ax.text(px, py, lbl, fontsize=12, weight="bold", ha="center", va="center",
                color=NAVY, bbox=dict(boxstyle="circle,pad=0.15", fc="white", ec="none"))


def save(fig, name):
    out = IMAGES_DIR / name
    fig.savefig(out, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved", out.name)


def ex01():
    # חדר מלבני 8 מ' על 5 מ' - שטח והיקף
    fig, ax = new_fig()
    x, y, w, h = 2, 1.5, 8, 5
    rect(ax, x, y, w, h)
    dim_h(ax, x, x + w, y, "8 מ'")
    dim_v(ax, y, y + h, x, "5 מ'")
    corner_labels(ax, x, y, w, h)
    save(fig, "9_7.3_ex01.png")


def ex04():
    # גינה: רק שטח נתון (60 מ"ר), אין ממדים - מסמנים "?" על הצלעות
    fig, ax = new_fig()
    x, y, w, h = 2.5, 1.6, 7, 4.8
    rect(ax, x, y, w, h, facecolor=GREEN_FILL, alpha=0.5)
    dim_h(ax, x, x + w, y, "?")
    dim_v(ax, y, y + h, x, "?")
    ax.text(x + w / 2, y + h / 2, 'שטח = 60 מ"ר', fontsize=13, ha="center",
            va="center", color=GREEN, weight="bold")
    save(fig, "9_7.3_ex04.png")


def ex08():
    # מלבן 12 מ' על 7 מ', גדר מסביב (כל ארבע הצלעות)
    fig, ax = new_fig(xlim=(0, 13))
    x, y, w, h = 1.5, 1.5, 9, 5
    rect(ax, x, y, w, h)
    dim_h(ax, x, x + w, y, "12 מ'")
    dim_v(ax, y, y + h, x, "7 מ'")
    corner_labels(ax, x, y, w, h)
    ax.text(x + w / 2, y + h + 0.85, "גדר מסביב", fontsize=11, ha="center",
            color=NAVY, weight="bold")
    save(fig, "9_7.3_ex08.png")


def ex09():
    # חצר מלבנית: רוחב w, אורך w+4, עלות ריצוף 4,050 ₪ ב-90 ₪/מ"ר (שטח=45)
    fig, ax = new_fig(xlim=(0, 13))
    x, y, w, h = 1.8, 1.6, 8.5, 4.2
    rect(ax, x, y, w, h, facecolor=BLUE_FILL, alpha=0.5)
    dim_h(ax, x, x + w, y, "w+4")
    dim_v(ax, y, y + h, x, "w")
    ax.text(x + w / 2, y + h + 0.85, 'שטח = 45 מ"ר (עלות ריצוף 4,050 ש"ח)',
            fontsize=11, ha="center", color=NAVY, weight="bold")
    save(fig, "9_7.3_ex09.png")


def ex11():
    # אדריכל: חדר 10x6 לפני, ואחרי הקטנת שטח ב-20% (48 מ"ר, רוחב קבוע 6)
    fig, ax = new_fig(xlim=(0, 14), ylim=(0, 8), figsize=(7.2, 4.2))
    x1, y1, w1, h1 = 1.0, 1.4, 6, 4
    rect(ax, x1, y1, w1, h1, facecolor=BLUE_FILL, alpha=0.5)
    dim_h(ax, x1, x1 + w1, y1, "10 מ'", offset=-0.45)
    dim_v(ax, y1, y1 + h1, x1, "6 מ'", offset=-0.45)
    ax.text(x1 + w1 / 2, y1 + h1 + 0.6, "לפני", fontsize=12, ha="center", color=NAVY, weight="bold")

    x2, y2, w2, h2 = 8.6, 1.4, 4.8, 4
    rect(ax, x2, y2, w2, h2, facecolor=GREEN_FILL, alpha=0.5)
    dim_h(ax, x2, x2 + w2, y2, "8 מ'", offset=-0.45)
    dim_v(ax, y2, y2 + h2, x2, "6 מ'", offset=-0.45)
    ax.text(x2 + w2 / 2, y2 + h2 + 0.6, 'אחרי (שטח קטן ב-20%)', fontsize=11, ha="center", color=NAVY, weight="bold")
    save(fig, "9_7.3_ex11.png")


def ex16():
    # גדר על 3 צלעות (2 קצרות + ארוכה אחת): קצרה w, ארוכה 2w
    fig, ax = new_fig(xlim=(0, 13))
    x, y, w, h = 2, 1.6, 8, 4.4
    ax.plot([x, x + w], [y + h, y + h], color=NAVY, linewidth=3)
    ax.plot([x, x], [y, y + h], color=NAVY, linewidth=3)
    ax.plot([x + w, x + w], [y, y + h], color=NAVY, linewidth=3)
    ax.plot([x, x + w], [y, y], color=GRAY, linewidth=2, linestyle="--")
    dim_h(ax, x, x + w, y + h, "2w", offset=0.55)
    dim_v(ax, y, y + h, x, "w", offset=-0.55)
    dim_v(ax, y, y + h, x + w, "w", offset=0.55)
    ax.text((2 * x + w) / 2, y - 0.75, "ללא גדר", fontsize=9, ha="center", color=GRAY, style="italic")
    corner_labels(ax, x, y, w, h)
    save(fig, "9_7.3_ex16.png")


def ex17():
    # מה"ט 2024: חצר ABCD, גדר על הצלע הארוכה (l) + שתי הצלעות הקצרות (w)
    fig, ax = new_fig(xlim=(0, 13))
    x, y, w, h = 2, 1.6, 8, 4.4
    ax.plot([x, x + w], [y + h, y + h], color=NAVY, linewidth=3)
    ax.plot([x, x], [y, y + h], color=NAVY, linewidth=3)
    ax.plot([x + w, x + w], [y, y + h], color=NAVY, linewidth=3)
    ax.plot([x, x + w], [y, y], color=GRAY, linewidth=2, linestyle="--")
    dim_h(ax, x, x + w, y + h, "l", offset=0.55)
    dim_v(ax, y, y + h, x, "w", offset=-0.55)
    dim_v(ax, y, y + h, x + w, "w", offset=0.55)
    corner_labels(ax, x, y, w, h)
    ax.text((2 * x + w) / 2, y - 0.75, "ללא גדר", fontsize=9, ha="center", color=GRAY, style="italic")
    ax.text(x + w / 2, y + h + 1.15, 'עלות גדר 250 ש"ח למ׳, עלות דשא 110 ש"ח למ"ר',
            fontsize=10, ha="center", color=GREEN, weight="bold")
    save(fig, "9_7.3_ex17.png")


def ex20():
    # אדריכל: חדר 18x12 לפני, ואחרי שני השלבים (14.4 x 11.04)
    fig, ax = new_fig(xlim=(0, 15), ylim=(0, 9), figsize=(7.6, 4.6))
    x1, y1, w1, h1 = 1.0, 1.4, 6, 4
    rect(ax, x1, y1, w1, h1, facecolor=BLUE_FILL, alpha=0.5)
    dim_h(ax, x1, x1 + w1, y1, "18 מ'", offset=-0.45)
    dim_v(ax, y1, y1 + h1, x1, "12 מ'", offset=-0.45)
    ax.text(x1 + w1 / 2, y1 + h1 + 0.6, "לפני", fontsize=12, ha="center", color=NAVY, weight="bold")

    x2, y2, w2, h2 = 9.0, 1.4, 4.8, 3.68
    rect(ax, x2, y2, w2, h2, facecolor=GREEN_FILL, alpha=0.5)
    dim_h(ax, x2, x2 + w2, y2, "14.4 מ'", offset=-0.45)
    dim_v(ax, y2, y2 + h2, x2, "11.04 מ'", offset=-0.45)
    ax.text(x2 + w2 / 2, y2 + h2 + 0.6, "אחרי (שלב א' + שלב ב')", fontsize=11, ha="center", color=NAVY, weight="bold")
    save(fig, "9_7.3_ex20.png")


def main():
    for fn in [ex01, ex04, ex08, ex09, ex11, ex16, ex17, ex20]:
        fn()


if __name__ == "__main__":
    main()
