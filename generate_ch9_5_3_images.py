#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate per-exercise PNG diagrams for chapter 9, sub-topic 5.3
(בעיות שינוי מידות עם אחוזים).

Each exercise gets its own diagram carrying the actual numbers from the
question (no generic/duplicated drawing across exercises).
"""
from __future__ import annotations

import os
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.axes import Axes  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

WORKSPACE = os.path.dirname(os.path.abspath(__file__))
CHAPTER_DIR = os.path.join(WORKSPACE, "9 - שאלות מילוליות")
IMAGES_DIR = os.path.join(CHAPTER_DIR, "images")

plt.rcParams["font.family"] = ["Arial Hebrew", "Arial Unicode MS", "DejaVu Sans", "Arial"]
plt.rcParams["axes.unicode_minus"] = False
HEBREW_RE = re.compile(r"[\u0590-\u05FF]")

# matplotlib in this environment shapes Hebrew RTL natively (libraqm).
# Do NOT run python-bidi/get_display() on top of it -- see quality-check prompt.
_orig_text = Axes.text


def plain_text(ax, x, y, s, **kwargs):
    return _orig_text(ax, x, y, s, **kwargs)


C_EDGE = "#1f2937"
C_INNER = "#0f766e"
_DIM_ARROW = dict(arrowstyle="<->", color="#333333", lw=0.9, mutation_scale=8)


def dim_h(ax, x1, x2, y, label, off=-0.6, fs=11):
    ya = y + off
    ax.annotate("", xy=(x1, ya), xytext=(x2, ya), arrowprops=_DIM_ARROW)
    ax.plot([x1, x1], [y, ya], color="#555555", lw=0.6)
    ax.plot([x2, x2], [y, ya], color="#555555", lw=0.6)
    ax.text(
        (x1 + x2) / 2,
        ya + (0.32 if off < 0 else -0.42),
        label,
        ha="center",
        fontsize=fs,
        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.9),
    )


def dim_v(ax, x, y1, y2, label, off=-0.6, fs=11):
    xa = x + off
    ax.annotate("", xy=(xa, y1), xytext=(xa, y2), arrowprops=_DIM_ARROW)
    ax.plot([x, xa], [y1, y1], color="#555555", lw=0.6)
    ax.plot([x, xa], [y2, y2], color="#555555", lw=0.6)
    ax.text(
        xa + (0.4 if off < 0 else -0.6),
        (y1 + y2) / 2,
        label,
        va="center",
        fontsize=fs,
        rotation=90,
        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.9),
    )


def mark_pt(ax, x, y, lbl, dx=0.15, dy=0.15, fs=13):
    ax.plot(x, y, "o", color="#C41E3A", ms=5, zorder=5)
    ax.text(x + dx, y + dy, lbl, fontsize=fs, weight="bold")


def base_fig(figsize=(6.4, 4.6)):
    fig, ax = plt.subplots(figsize=figsize, facecolor="white")
    ax.set_facecolor("white")
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def save(fig, n: int) -> None:
    path = os.path.join(IMAGES_DIR, f"9_5.3_ex{n:02d}.png")
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def simple_rect(n, x0, y0, w, h, label_bottom, label_left, note=None, note_dy=0.9,
                 top_note=None, right_note=None, xpad=2.4, ypad=2.0, figsize=(6.4, 4.6)):
    fig, ax = base_fig(figsize=figsize)
    ax.set_xlim(x0 - xpad, x0 + w + xpad)
    ax.set_ylim(y0 - ypad, y0 + h + ypad + note_dy)
    rect = Rectangle((x0, y0), w, h, fill=False, linewidth=2, edgecolor=C_EDGE)
    ax.add_patch(rect)
    mark_pt(ax, x0, y0, "A", dx=-0.35, dy=-0.55)
    mark_pt(ax, x0 + w, y0, "B", dx=0.15, dy=-0.55)
    mark_pt(ax, x0 + w, y0 + h, "C", dx=0.15, dy=0.15)
    mark_pt(ax, x0, y0 + h, "D", dx=-0.35, dy=0.15)
    dim_h(ax, x0, x0 + w, y0, label_bottom, off=-1.0)
    dim_v(ax, x0, y0, y0 + h, label_left, off=-1.0)
    if top_note:
        plain_text(ax, x0 + w / 2, y0 + h + 0.55, top_note, ha="center", fontsize=11, color="#b91c1c")
    if right_note:
        plain_text(ax, x0 + w + 0.55, y0 + h / 2, right_note, va="center", fontsize=11, color="#b91c1c", rotation=90)
    if note:
        plain_text(ax, x0 + w / 2, y0 + h + note_dy, note, ha="center", fontsize=11, color="#1d4ed8")
    save(fig, n)


def gen_10():
    simple_rect(10, 0, 0, 8, 4, "2W (אורך)", "W (רוחב)", note="היקף = 48 מ'", note_dy=1.1)


def gen_11():
    simple_rect(11, 0, 0, 8, 4, "20 מ' (אורך)", "10 מ' (רוחב)", top_note="אורך +50% ←")


def gen_12():
    simple_rect(12, 0, 0, 8, 6, "20 מ' (אורך)", "15 מ' (רוחב)", top_note="אורך −20%", right_note="רוחב +15%")


def gen_13():
    fig, ax = base_fig(figsize=(6.0, 4.4))
    ax.set_xlim(-2.4, 10.4)
    ax.set_ylim(-1.8, 6.2)
    rect = Rectangle((0, 0), 8, 4, fill=False, linewidth=2, edgecolor=C_EDGE)
    ax.add_patch(rect)
    mark_pt(ax, 0, 0, "A", dx=-0.35, dy=-0.55)
    mark_pt(ax, 8, 0, "B", dx=0.15, dy=-0.55)
    mark_pt(ax, 8, 4, "C", dx=0.15, dy=0.15)
    mark_pt(ax, 0, 4, "D", dx=-0.35, dy=0.15)
    plain_text(ax, 4, 2, 'שטח = 300 מ"ר', ha="center", va="center", fontsize=13,
               bbox=dict(boxstyle="round,pad=0.3", fc="#f1f5f9", ec="#94a3b8"))
    plain_text(ax, 4, 4.65, "אורך +25% ←", ha="center", fontsize=11, color="#b91c1c")
    save(fig, 13)


def gen_14():
    simple_rect(14, 0, 0, 6, 4, "15 מ' (אורך)", "10 מ' (רוחב)", top_note="אורך +20%, השטח ללא שינוי")


def gen_15():
    simple_rect(15, 0, 0, 9, 3, "3W (אורך)", "W (רוחב)", note="היקף = 40 מ'", note_dy=1.1, figsize=(6.8, 3.8))


def gen_16():
    simple_rect(16, 0, 0, 7.2, 4, "18 מ' (אורך)", "10 מ' (רוחב)", top_note="אורך −10%", right_note="רוחב +20%")


def gen_17():
    fig, ax = base_fig(figsize=(6.6, 5.0))
    ax.set_xlim(-1.2, 13.2)
    ax.set_ylim(-1.6, 10.4)
    outer = Rectangle((0, 0), 12, 8, fill=False, linewidth=2, edgecolor=C_EDGE)
    ax.add_patch(outer)
    mark_pt(ax, 0, 0, "A", dx=-0.4, dy=-0.55)
    mark_pt(ax, 12, 0, "B", dx=0.15, dy=-0.55)
    mark_pt(ax, 12, 8, "C", dx=0.15, dy=0.15)
    mark_pt(ax, 0, 8, "D", dx=-0.4, dy=0.15)
    plain_text(ax, 6, 9.0, 'שטח המגרש = 500 מ"ר', ha="center", fontsize=12, color="#1d4ed8")

    ix0, iy0, iw, ih = 3.0, 2.0, 7.2, 4.8
    inner = Rectangle((ix0, iy0), iw, ih, fill=False, linewidth=2, edgecolor=C_INNER)
    ax.add_patch(inner)
    dim_h(ax, ix0, ix0 + iw, iy0, "18 מ' (אורך) −20%", off=-1.0, fs=10)
    dim_v(ax, ix0, iy0, iy0 + ih, "12 מ' (רוחב) +15%", off=-1.0, fs=10)
    plain_text(ax, ix0 + iw / 2, iy0 + ih / 2, "המבנה", ha="center", va="center", fontsize=10, color=C_INNER)
    save(fig, 17)


def gen_18():
    fig, ax = base_fig(figsize=(7.4, 4.6))
    ax.set_xlim(-1.5, 13.5)
    ax.set_ylim(-1.6, 9.4)

    x0 = 0
    w1, h1 = 50 / 15, 110 / 15
    rect1 = Rectangle((x0, 0), w1, h1, fill=False, linewidth=2, edgecolor=C_EDGE)
    ax.add_patch(rect1)
    dim_h(ax, x0, x0 + w1, 0, '50 ס"מ', off=-1.0, fs=10)
    dim_v(ax, x0, 0, h1, '110 ס"מ', off=-1.0, fs=10)
    plain_text(ax, x0 + w1 / 2, h1 + 0.55, "ענבל", ha="center", fontsize=12, weight="bold")

    x1 = x0 + w1 + 3.6
    w2, h2 = 60 / 15, 120 / 15
    rect2 = Rectangle((x1, 0), w2, h2, fill=False, linewidth=2, edgecolor=C_INNER)
    ax.add_patch(rect2)
    dim_h(ax, x1, x1 + w2, 0, '60 ס"מ', off=-1.0, fs=10)
    dim_v(ax, x1 + w2, 0, h2, '120 ס"מ', off=1.0, fs=10)
    plain_text(ax, x1 + w2 / 2, h2 + 0.55, "נעמה", ha="center", fontsize=12, weight="bold", color=C_INNER)
    save(fig, 18)


def gen_19():
    fig, ax = base_fig(figsize=(6.6, 4.4))
    w, h = 9, 5
    ax.set_xlim(-2.6, w + 2.4)
    ax.set_ylim(-1.8, h + 2.6)
    rect = Rectangle((0, 0), w, h, fill=False, linewidth=2, edgecolor=C_EDGE)
    ax.add_patch(rect)
    mark_pt(ax, 0, 0, "A", dx=-0.35, dy=-0.55)
    mark_pt(ax, w, 0, "B", dx=0.15, dy=-0.55)
    mark_pt(ax, w, h, "C", dx=0.15, dy=0.15)
    mark_pt(ax, 0, h, "D", dx=-0.35, dy=0.15)
    dim_h(ax, 0, w, 0, "x (צלע ארוכה)", off=-1.0)
    dim_v(ax, 0, 0, h, "y (צלע קצרה)", off=-1.0)
    plain_text(ax, w / 2, h + 0.55, "היקף = 28 מ'", ha="center", fontsize=11, color="#1d4ed8")
    plain_text(ax, w / 2, -1.55, "x: גדל ב-50%", ha="center", fontsize=10, color="#b91c1c")
    plain_text(ax, w + 1.6, h / 2, "y: גדל ב-4 מ'", va="center", fontsize=10, color="#b91c1c", rotation=90)
    save(fig, 19)


def gen_20():
    fig, ax = base_fig(figsize=(6.8, 5.4))
    ax.set_xlim(-3.0, 13.4)
    ax.set_ylim(-2.6, 10.6)
    outer = Rectangle((0, 0), 12, 8, fill=False, linewidth=2, edgecolor=C_EDGE)
    ax.add_patch(outer)
    mark_pt(ax, 0, 0, "A", dx=-0.4, dy=-0.55)
    mark_pt(ax, 12, 0, "B", dx=0.15, dy=-0.55)
    mark_pt(ax, 12, 8, "C", dx=0.15, dy=0.15)
    mark_pt(ax, 0, 8, "D", dx=-0.4, dy=0.15)
    plain_text(ax, 6, 8.9, 'שטח המגרש (a×b) = 1,600 מ"ר', ha="center", fontsize=11, color="#1d4ed8")

    margin = 2.2
    ix0, iy0 = margin, margin
    iw, ih = 12 - 2 * margin, 8 - 2 * margin
    inner = Rectangle((ix0, iy0), iw, ih, fill=False, linewidth=2, edgecolor=C_INNER)
    ax.add_patch(inner)
    plain_text(ax, ix0 + iw / 2, iy0 + ih / 2, 'בית\nשטח = 280 מ"ר', ha="center", va="center", fontsize=10, color=C_INNER)

    dim_h(ax, 0, ix0, 0, "שוליים = 8 מ'", off=-1.4, fs=8)
    dim_v(ax, 0, 0, iy0, "שוליים\n8 מ'", off=-1.4, fs=8)
    save(fig, 20)


def main():
    os.makedirs(IMAGES_DIR, exist_ok=True)
    for fn in (gen_10, gen_11, gen_12, gen_13, gen_14, gen_15, gen_16, gen_17, gen_18, gen_19, gen_20):
        fn()
    print("done")


if __name__ == "__main__":
    main()
