#!/usr/bin/env python3
"""Dedicated, per-exercise diagram generator for chapter 9, subtopic 5.1
(תזכורת: היקף ושטח מלבן וריבוע). Each exercise gets a hand-built diagram
with the actual numeric dimensions from the question text, matching the
corrected values verified in the quality-check pass.

Run directly: python3 scripts/gen_9_5_1_images.py
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
# double-reverses the text and produces garbled output (this is the exact
# bug the quality-check skill warns about, and it turns out to also affect
# generate_ch9_graphs.py's rtl_text helper, not just chapter 6's). Plain
# Hebrew strings in logical order render correctly as-is here.

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
    fig, ax = new_fig()
    rect(ax, 2, 1.5, 8, 5)
    dim_h(ax, 2, 10, 1.5, "8 מ'")
    dim_v(ax, 1.5, 6.5, 2, "5 מ'")
    save(fig, "9_5.1_ex01.png")


def ex02():
    fig, ax = new_fig()
    rect(ax, 3.5, 1.5, 5, 5)
    dim_h(ax, 3.5, 8.5, 1.5, "7 מ'")
    dim_v(ax, 1.5, 6.5, 3.5, "7 מ'")
    save(fig, "9_5.1_ex02.png")


def ex03():
    fig, ax = new_fig()
    rect(ax, 1.5, 1.7, 9, 4.6)
    dim_h(ax, 1.5, 10.5, 1.7, "12 מ'")
    dim_v(ax, 1.7, 6.3, 1.5, "9 מ'")
    save(fig, "9_5.1_ex03.png")


def ex04():
    fig, ax = new_fig()
    rect(ax, 2.5, 2, 6, 4)
    dim_h(ax, 2.5, 8.5, 2, "6 מ'")
    dim_v(ax, 2, 6, 2.5, "4 מ'")
    save(fig, "9_5.1_ex04.png")


def ex05():
    fig, ax = new_fig()
    rect(ax, 3, 1.5, 5, 5)
    dim_h(ax, 3, 8, 1.5, "10 מ'")
    dim_v(ax, 1.5, 6.5, 3, "10 מ'")
    save(fig, "9_5.1_ex05.png")


def ex06():
    fig, ax = new_fig()
    rect(ax, 2, 1.8, 8, 4.4)
    dim_h(ax, 2, 10, 1.8, "9 מ'")
    dim_v(ax, 1.8, 6.2, 2, "?")
    ax.text(6, 7.2, "היקף = 30 מ'", fontsize=13, ha="center", color=NAVY, weight="bold")
    save(fig, "9_5.1_ex06.png")


def ex07():
    fig, ax = new_fig()
    rect(ax, 2, 1.8, 8, 4.4)
    dim_h(ax, 2, 10, 1.8, "9 מ'")
    dim_v(ax, 1.8, 6.2, 2, "?")
    ax.text(6, 4, 'שטח = 54 מ"ר', fontsize=12, ha="center", va="center", color=GREEN, weight="bold")
    save(fig, "9_5.1_ex07.png")


def ex08():
    fig, ax = new_fig()
    rect(ax, 3.5, 1.8, 5, 5)
    dim_h(ax, 3.5, 8.5, 1.8, "?")
    ax.text(6, 4.3, 'שטח = 49 מ"ר', fontsize=12, ha="center", va="center", color=GREEN, weight="bold")
    save(fig, "9_5.1_ex08.png")


def ex09():
    fig, ax = new_fig(xlim=(0, 14))
    rect(ax, 2, 1.8, 9, 3, facecolor=GREEN_FILL, alpha=0.5)
    dim_h(ax, 2, 11, 1.8, "3x")
    dim_v(ax, 1.8, 4.8, 2, "x")
    ax.text(7, 6.4, "היקף = 48 מ'", fontsize=13, ha="center", color=NAVY, weight="bold")
    save(fig, "9_5.1_ex09.png")


def ex10():
    fig, ax = new_fig()
    rect(ax, 1.2, 0.9, 9.6, 6.2, facecolor=BLUE_FILL, alpha=0.5)
    rect(ax, 2.2, 1.9, 7.6, 4.2)
    dim_h(ax, 2.2, 9.8, 1.9, "15 מ'", offset=-0.4)
    dim_v(ax, 1.9, 6.1, 2.2, "8 מ'", offset=-0.4)
    ax.annotate("", xy=(1.2, 5.6), xytext=(2.2, 5.6),
                arrowprops=dict(arrowstyle="<->", color=GREEN, lw=1.3))
    ax.text(1.7, 6.0, "1 מ'", fontsize=10, ha="center", color=GREEN, weight="bold")
    save(fig, "9_5.1_ex10.png")


def ex11():
    fig, ax = new_fig()
    rect(ax, 3, 1.5, 5.5, 5.5)
    dim_h(ax, 3, 8.5, 1.5, "?")
    ax.text(5.75, 7.3, "היקף = 52 מ'", fontsize=13, ha="center", color=NAVY, weight="bold")
    save(fig, "9_5.1_ex11.png")


def ex12():
    fig, ax = new_fig(xlim=(0, 13))
    rect(ax, 2, 1.8, 8, 4, facecolor=GREEN_FILL, alpha=0.5)
    dim_h(ax, 2, 10, 1.8, "x+6")
    dim_v(ax, 1.8, 5.8, 2, "x")
    ax.text(6, 3.8, 'שטח = 72 מ"ר', fontsize=12, ha="center", va="center", color=GREEN, weight="bold")
    save(fig, "9_5.1_ex12.png")


def ex13():
    fig, ax = new_fig()
    rect(ax, 1.5, 1.8, 9, 4.4, facecolor="#fef3c7", alpha=0.5)
    dim_h(ax, 1.5, 10.5, 1.8, "14 מ'")
    dim_v(ax, 1.8, 6.2, 1.5, "10 מ'")
    save(fig, "9_5.1_ex13.png")


def ex14():
    fig, ax = new_fig(xlim=(0, 12))
    rect(ax, 1.2, 1.5, 5, 5, facecolor=GREEN_FILL, alpha=0.35)
    rect(ax, 2.2, 2.5, 3, 3)
    dim_h(ax, 2.2, 5.2, 2.5, "5 מ'", offset=-0.4)
    dim_h(ax, 1.2, 6.2, 1.5, "7 מ'", offset=-1.1)
    ax.text(3.7, 6.9, "לפני ואחרי ההרחבה", fontsize=11, ha="center", color=NAVY, weight="bold")
    save(fig, "9_5.1_ex14.png")


def ex15():
    fig, ax = new_fig(xlim=(0, 13), ylim=(0, 8.6))
    x, y, w, h = 1.5, 2.4, 9.5, 4.4
    rect(ax, x, y, w, h)
    dim_h(ax, x, x + w, y, "20 מ'", offset=-1.15)
    dim_v(ax, y, y + h, x, "13 מ'")
    gate_c = x + w / 2
    ax.plot([gate_c - 0.9, gate_c + 0.9], [y, y], color="white", linewidth=4, zorder=3)
    ax.plot([gate_c - 0.9, gate_c + 0.9], [y, y], color=GRAY, linewidth=1.6, linestyle="--", zorder=4)
    ax.text(gate_c, y - 0.5, "כניסה 4 מ'", fontsize=10, ha="center", va="top", color=GREEN, weight="bold")
    save(fig, "9_5.1_ex15.png")


def ex16():
    fig, ax = new_fig(xlim=(0, 13))
    rect(ax, 2, 1.8, 8, 4, facecolor=GREEN_FILL, alpha=0.5)
    dim_h(ax, 2, 10, 1.8, "2x")
    dim_v(ax, 1.8, 5.8, 2, "x")
    ax.text(6, 6.6, "היקף = 24 מ'", fontsize=13, ha="center", color=NAVY, weight="bold")
    save(fig, "9_5.1_ex16.png")


def ex17():
    fig, ax = new_fig(xlim=(0, 13))
    rect(ax, 1.2, 1.2, 9, 6)
    rect(ax, 2.7, 2.7, 6, 3, edgecolor=GREEN)
    dim_h(ax, 1.2, 10.2, 1.2, "x+4", offset=-0.5)
    dim_v(ax, 1.2, 7.2, 1.2, "x", offset=-0.5)
    ax.text(5.7, 4.2, "בית", fontsize=11, color=GREEN, ha="center", weight="bold")
    ax.annotate("", xy=(1.2, 6.6), xytext=(2.7, 6.6), arrowprops=dict(arrowstyle="<->", color=GREEN, lw=1.2))
    ax.text(2.0, 6.9, "3 מ'", fontsize=9, ha="center", color=GREEN, weight="bold")
    save(fig, "9_5.1_ex17.png")


def ex18():
    fig, ax = new_fig(xlim=(0, 14), ylim=(0, 8), figsize=(7, 4.2))
    rect(ax, 1.2, 1.8, 4, 2, facecolor=BLUE_FILL, alpha=0.6)
    dim_h(ax, 1.2, 5.2, 1.8, '80 ס"מ', offset=-0.45)
    dim_v(ax, 1.8, 3.8, 1.2, '40 ס"מ', offset=-0.45)
    ax.text(3.2, 6.0, "ליאור", fontsize=12, ha="center", color=NAVY, weight="bold")

    rect(ax, 7.5, 1.4, 4.5, 2.5, facecolor=GREEN_FILL, alpha=0.6)
    dim_h(ax, 7.5, 12, 1.4, '90 ס"מ', offset=-0.45)
    dim_v(ax, 1.4, 3.9, 7.5, '50 ס"מ', offset=-0.45)
    ax.text(9.75, 6.0, "מיה", fontsize=12, ha="center", color=NAVY, weight="bold")
    save(fig, "9_5.1_ex18.png")


def ex19():
    fig, ax = new_fig(xlim=(0, 14), ylim=(0, 8), figsize=(7.2, 4.2))
    rect(ax, 1.0, 1.5, 4, 2.2, facecolor=BLUE_FILL, alpha=0.5)
    dim_h(ax, 1.0, 5.0, 1.5, "x", offset=-0.4)
    dim_v(ax, 1.5, 3.7, 1.0, "16-x", offset=-0.4)
    ax.text(3.0, 6.5, "לפני השינוי", fontsize=11, ha="center", color=NAVY, weight="bold")

    rect(ax, 8.0, 1.2, 5, 2.8, facecolor=GREEN_FILL, alpha=0.5)
    dim_h(ax, 8.0, 13.0, 1.2, "1.5x", offset=-0.4)
    dim_v(ax, 1.2, 4.0, 8.0, "19-x", offset=-0.4)
    ax.text(10.5, 6.5, "אחרי השינוי", fontsize=11, ha="center", color=NAVY, weight="bold")
    save(fig, "9_5.1_ex19.png")


def ex20():
    fig, ax = new_fig(xlim=(0, 13))
    x, y, w, h = 1.5, 1.8, 9, 4.2
    ax.plot([x, x + w], [y + h, y + h], color=NAVY, linewidth=3)
    ax.plot([x, x], [y, y + h], color=NAVY, linewidth=3)
    ax.plot([x + w, x + w], [y, y + h], color=NAVY, linewidth=3)
    ax.plot([x, x + w], [y, y], color=GRAY, linewidth=2, linestyle="--")
    dim_h(ax, x, x + w, y + h, "15 מ'", offset=0.55)
    dim_v(ax, y, y + h, x, "6 מ'", offset=-0.55)
    dim_v(ax, y, y + h, x + w, "6 מ'", offset=0.55)
    ax.text((2 * x + w) / 2, y - 0.75, "ללא גדר", fontsize=9, ha="center", color=GRAY, style="italic")
    corner_labels(ax, x, y, w, h)
    save(fig, "9_5.1_ex20.png")


def main():
    for fn in [ex01, ex02, ex03, ex04, ex05, ex06, ex07, ex08, ex09, ex10,
               ex11, ex12, ex13, ex14, ex15, ex16, ex17, ex18, ex19, ex20]:
        fn()


if __name__ == "__main__":
    main()
