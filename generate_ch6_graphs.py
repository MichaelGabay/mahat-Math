#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate PNG diagrams for Chapter 6 – מבוא להנדסה (MAHAT Math).
Uses matplotlib Agg backend; Hebrew-friendly font stack.
"""
from __future__ import annotations

import math
import os
import re
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.patches as mpatches  # noqa: E402
from matplotlib.axes import Axes  # noqa: E402
import numpy as np  # noqa: E402
from bidi.algorithm import get_display  # noqa: E402

WORKSPACE = os.path.dirname(os.path.abspath(__file__))
CHAPTER_DIR = os.path.join(WORKSPACE, "6 - מבוא להנדסה")
IMAGES_DIR = os.path.join(CHAPTER_DIR, "images")
os.makedirs(IMAGES_DIR, exist_ok=True)

# Hebrew-capable fonts first for מודול זה; Latin/math still fall back via DejaVu.
plt.rcParams["font.family"] = ["Arial Hebrew", "Arial Unicode MS", "DejaVu Sans", "Arial"]
plt.rcParams["axes.unicode_minus"] = False
HEBREW_RE = re.compile(r"[\u0590-\u05FF]")


def rtl_text(value):
    if isinstance(value, str) and HEBREW_RE.search(value):
        return get_display(value)
    return value


_orig_set_title = Axes.set_title
_orig_set_xlabel = Axes.set_xlabel
_orig_set_ylabel = Axes.set_ylabel
_orig_plot = Axes.plot
_orig_annotate = Axes.annotate
_orig_text = Axes.text


def _patched_set_title(self, label, *args, **kwargs):
    return _orig_set_title(self, rtl_text(label), *args, **kwargs)


def _patched_set_xlabel(self, xlabel, *args, **kwargs):
    return _orig_set_xlabel(self, rtl_text(xlabel), *args, **kwargs)


def _patched_set_ylabel(self, ylabel, *args, **kwargs):
    return _orig_set_ylabel(self, rtl_text(ylabel), *args, **kwargs)


def _patched_plot(self, *args, **kwargs):
    if "label" in kwargs:
        kwargs["label"] = rtl_text(kwargs["label"])
    return _orig_plot(self, *args, **kwargs)


def _patched_annotate(self, text, *args, **kwargs):
    return _orig_annotate(self, rtl_text(text), *args, **kwargs)


def _patched_text(self, x, y, s, *args, **kwargs):
    return _orig_text(self, x, y, rtl_text(s), *args, **kwargs)


Axes.set_title = _patched_set_title
Axes.set_xlabel = _patched_set_xlabel
Axes.set_ylabel = _patched_set_ylabel
Axes.plot = _patched_plot
Axes.annotate = _patched_annotate
Axes.text = _patched_text

C_EDGE = "#222222"
C_FILL = "#B8D4E8"
C_GRAY = "#C8C8C8"
C_SHADE = "#A0A0A0"


# ── scope: stem -> sorted list of exercise numbers ───────────────────────────
def _rng(a: int, b: int) -> list[int]:
    return list(range(a, b + 1))


SCOPE: dict[str, list[int]] = {
    # 1–6, 13: exercises 13–20
    "1_מהי_נקודה_קטע_ישר_וקרן": _rng(13, 20),
    "2_מושגי_יסוד_בזוויות": _rng(13, 20),
    "3_ההבדל_בין_היקף_לשטח": _rng(13, 20),
    "4_תכונות_המלבן_והריבוע": _rng(13, 20),
    "5_חישובי_היקף_ושטח_מלבן_וריבוע": _rng(13, 20),
    "6_שילוב_אלגברה_בסיסית": _rng(13, 20),
    "13_תכונות_המעגל": _rng(13, 20),
    # 7,8,9,10,11,12,14,15,16: 9–20
    "7_היכרות_עם_סוגי_משולשים": _rng(9, 20),
    "8_גובה_במשולש_וחישובי_שטח_והיקף": _rng(9, 20),
    "9_חיבור_וחיסור_שטחים": _rng(9, 20),
    "10_תכונות_המקבילית_והמעוין": _rng(9, 20),
    "11_חישובי_היקף_ושטח_מקבילית_ומעוין": _rng(9, 20),
    "12_תכונות_הטרפז_והדלתון": _rng(9, 20),
    "14_חישובי_היקף_ושטח_טרפז_דלתון_ומעגל": _rng(9, 20),
    "15_פירוק_צורות_מורכבות_לצורות_פשוטות": _rng(9, 20),
    "16_שטחים_צבועים_באפור_ויחסי_צלעות": _rng(9, 20),
    # 17–20: full 1–20
    "17_היכרות_עם_מערכת_הצירים_הקרטזית": _rng(1, 20),
    "18_סימון_וקריאת_נקודות_במישור": _rng(1, 20),
    "19_חישוב_אורכי_קטעים_מקבילים_לצירים": _rng(1, 20),
    "20_חישוב_שטחים_והיקפים_במערכת_צירים": _rng(1, 20),
}

SKIPPED: list[tuple[str, int, str]] = []


# ── helpers ─────────────────────────────────────────────────────────────────


def save_fig(fig, stem: str, n: int) -> None:
    fname = f"6_{stem}_ex{n:02d}.png"
    path = os.path.join(IMAGES_DIR, fname)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def fig_axes_plain(figsize=(6.2, 5.2)):
    fig, ax = plt.subplots(figsize=figsize, facecolor="white")
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def coord_plane(
    xlim,
    ylim,
    figsize=(6.2, 6.2),
    grid_step_x=None,
    grid_step_y=None,
):
    fig, ax = plt.subplots(figsize=figsize, facecolor="white")
    ax.set_facecolor("white")
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.axhline(0, color="black", lw=1.2, zorder=1)
    ax.axvline(0, color="black", lw=1.2, zorder=1)
    xr = xlim[1] - xlim[0]
    yr = ylim[1] - ylim[0]
    gx = grid_step_x or max(1, round(xr / 12))
    gy = grid_step_y or max(1, round(yr / 12))
    xt = [i for i in range(int(np.ceil(xlim[0])), int(np.floor(xlim[1])) + 1, gx)]
    yt = [i for i in range(int(np.ceil(ylim[0])), int(np.floor(ylim[1])) + 1, gy)]
    ax.set_xticks(xt)
    ax.set_yticks(yt)
    ax.grid(True, alpha=0.28, linestyle="--", color="gray")
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.tick_params(labelsize=7)
    ax.text(xlim[1] + xr * 0.02, 0, "x", fontsize=10)
    ax.text(0, ylim[1] + yr * 0.02, "y", fontsize=10, ha="center")
    return fig, ax


def poly(ax, pts, fill=C_FILL, edge=C_EDGE, lw=1.8, alpha=0.35):
    p = mpatches.Polygon(pts, closed=True, facecolor=fill, edgecolor=edge, lw=lw, alpha=alpha)
    ax.add_patch(p)


def circle(ax, xy, r, fill=None, ec=C_EDGE, lw=1.5):
    c = plt.Circle(xy, r, facecolor=fill, edgecolor=ec, lw=lw, fill=fill is not None)
    ax.add_patch(c)


def mark_pt(ax, x, y, lbl=None, dx=0.12, dy=0.12):
    ax.plot(x, y, "o", color="#C41E3A", ms=6, zorder=5)
    if lbl:
        ax.text(x + dx, y + dy, lbl, fontsize=8)


def plain_text(ax, x, y, s, **kwargs):
    """Hebrew on diagrams: logical order, no python-bidi."""
    return _orig_text(ax, x, y, s, **kwargs)


_DIM_ARROW = dict(arrowstyle="<->", color="#333333", lw=0.85, mutation_scale=8)


def dim_h(ax, x1, x2, y, label, off=-0.55, fs=8):
    ya = y + off
    ax.annotate("", xy=(x1, ya), xytext=(x2, ya), arrowprops=_DIM_ARROW)
    ax.plot([x1, x1], [y, ya], color="#555555", lw=0.5)
    ax.plot([x2, x2], [y, ya], color="#555555", lw=0.5)
    ax.text(
        (x1 + x2) / 2,
        ya + (0.28 if off < 0 else -0.38),
        label,
        ha="center",
        fontsize=fs,
        bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.9),
    )


def dim_v(ax, x, y1, y2, label, off=-0.55, fs=8):
    xa = x + off
    ax.annotate("", xy=(xa, y1), xytext=(xa, y2), arrowprops=_DIM_ARROW)
    ax.plot([x, xa], [y1, y1], color="#555555", lw=0.5)
    ax.plot([x, xa], [y2, y2], color="#555555", lw=0.5)
    ax.text(
        xa + (0.35 if off < 0 else -0.55),
        (y1 + y2) / 2,
        label,
        va="center",
        fontsize=fs,
        bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.9),
    )


def seg_label(ax, x1, y1, x2, y2, label, frac=0.5, dx=0.0, dy=0.18, fs=7):
    mx = x1 + frac * (x2 - x1) + dx
    my = y1 + frac * (y2 - y1) + dy
    ax.text(
        mx,
        my,
        label,
        ha="center",
        va="center",
        fontsize=fs,
        bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="#CCCCCC", alpha=0.92),
    )


def right_angle(ax, x, y, size=0.35, quadrant=1):
    """quadrant: 1=NE, 2=NW, 3=SW, 4=SE corner at (x,y)."""
    sx = size if quadrant in (1, 4) else -size
    sy = size if quadrant in (1, 2) else -size
    ax.plot([x, x + sx, x + sx], [y, y, y + sy], color="#444444", lw=0.7)


def plain_text(ax, x, y, s, **kwargs):
    """Hebrew on diagrams: logical order, no python-bidi."""
    return _orig_text(ax, x, y, s, **kwargs)


def number_line(ax, points, labels, xlim=None):
    """points: list of x positions; labels: same length."""
    if xlim is None:
        lo = min(points) - 1
        hi = max(points) + 1
        xlim = (lo, hi)
    ax.set_xlim(xlim)
    ax.set_ylim(-0.35, 0.55)
    ax.axhline(0, color="black", lw=1.5)
    for x, lb in zip(points, labels):
        ax.plot(x, 0, "o", color="#C41E3A", ms=7)
        ax.text(x, -0.22, lb, ha="center", fontsize=9)
    ax.axis("off")


def angle_fan(ax, Ox, Oy, rays_deg, labels):
    """rays_deg: list of angles from horizontal CCW in degrees."""
    ax.plot([Ox], [Oy], "ko", ms=5)
    L = 2.2
    for ang, lb in zip(rays_deg, labels):
        rad = math.radians(ang)
        x2 = Ox + L * math.cos(rad)
        y2 = Oy + L * math.sin(rad)
        ax.plot([Ox, x2], [Oy, y2], "k-", lw=1.3)
        ax.text(x2 + 0.15, y2 + 0.1, lb, fontsize=9)


# ═══════════════════════════════════════════════════════════════════════════
# Per-subtopic generators (schematic; matches exercise numerics where stated)

def gen_1(stem: str, n: int) -> None:
    fig, ax = fig_axes_plain()
    if n == 13:
        angle_fan(ax, 0, 0, [0, 35, 90], ["OA", "OC", "OB"])
        ax.text(-0.3, 1.3, r"$\angle AOB=90°$", fontsize=9)
        ax.text(1.1, 0.5, r"$\angle AOC=35°$", fontsize=9)
        ax.set_xlim(-0.8, 3)
        ax.set_ylim(-0.5, 2.5)
    elif n == 14:
        number_line(ax, [0, 12, 30], ["A", "C", "B"])
        ax.text(6, 0.35, "AC:CB = 2:3", fontsize=9)
    elif n == 15:
        number_line(ax, [0, 2, 5, 8, 14], ["P", "Q", "R", "S", ""], xlim=(-1, 15))
    elif n == 16:
        number_line(ax, [0, 15, 40], ["X", "Z", "Y"])
    elif n == 17:
        number_line(ax, [0, 12, 30], ["A", "B", "C"])
        ax.text(5, 0.38, r"$AB=\frac{2}{5}AC$", fontsize=9)
    elif n == 18:
        number_line(ax, [0, 5, 10, 15, 20, 25], ["A", "B", "C", "D", "E", ""], xlim=(-1, 26))
    elif n == 19:
        number_line(ax, [0, 12, 32], ["A", "D", "C"])
        ax.plot([12], [0.15], "s", color="blue", ms=6)
        ax.text(12, 0.38, "B", ha="center")
    elif n == 20:
        number_line(ax, [0, 10, 20, 30], ["A", "B", "C", "D"], xlim=(-1, 32))
    save_fig(fig, stem, n)


def gen_2(stem: str, n: int) -> None:
    fig, ax = fig_axes_plain()
    if n in (13, 14):
        ax.text(0.1, 0.55, "משלים / השלמה", fontsize=11)
        ax.set_xlim(0, 2)
        ax.set_ylim(0, 1)
    elif n == 15:
        angle_fan(ax, 0, 0, [0, 55, 90], ["OA", "OB", "OC"])
        ax.set_xlim(-0.5, 3)
        ax.set_ylim(-0.5, 2.5)
    elif n == 16:
        number_line(ax, [-1, 0, 1], ["A", "O", "B"])
        ax.plot([0, 0], [0, 1.2], "k-", lw=1.2)
        ax.text(0.15, 0.9, "C", fontsize=10)
    elif n == 17:
        ax.plot([0, 4], [0, 0], "k-", lw=1.5)
        ax.plot([0, 4], [2.8, 2.8], "k-", lw=1.5)
        ax.plot([1.2, 2.8], [0, 2.8], "k--", lw=1)
        ax.text(1, -0.38, "ישרים מקבילים וישר חותך", fontsize=8)
        ax.set_xlim(-0.5, 4.5)
        ax.set_ylim(-0.55, 3.45)
    elif n == 18:
        angle_fan(ax, 0, 0, [0, 60, 135], ["OA", "OB", "OC"])
        ax.set_xlim(-1, 3.5)
        ax.set_ylim(-1, 3)
    elif n == 19:
        poly(ax, [(0, 0), (3, 0), (1.5, 2)], alpha=0.25)
        ax.text(1.4, 0.8, r"$\triangle ABC$", fontsize=10)
        ax.set_xlim(-0.3, 3.5)
        ax.set_ylim(-0.3, 2.5)
    elif n == 20:
        poly(ax, [(0, 0), (3, 0), (3, 2), (0, 2)], alpha=0.2)
        ax.plot([0, 3], [2, 0], "k--", lw=1)
        ax.text(0.2, 1.8, r"$\angle ABD=63°$", fontsize=9)
        ax.set_xlim(-0.3, 3.5)
        ax.set_ylim(-0.3, 2.5)
    save_fig(fig, stem, n)


def gen_3(stem: str, n: int) -> None:
    fig, ax = fig_axes_plain()
    # אלפא גבוהה יותר כדי שהמלבנים ייראו בבירור במסכים ובתצוגת תמונה מוקטנת
    if n == 13:
        poly(ax, [(0, 0), (8, 0), (8, 6), (0, 6)], alpha=0.35)
        ax.text(0.5, 3, "ריצוף", fontsize=10)
    elif n == 14:
        poly(ax, [(0, 0), (5, 0), (5, 4), (0, 4)], fill="#F5E6CC", alpha=0.55)
        ax.plot([0, 5, 5, 0, 0], [0, 0, 4, 4, 0], "k-", lw=2)
        ax.text(2, 2, "מסגרת", fontsize=10)
    elif n == 15:
        poly(ax, [(0, 0), (3, 0), (3, 3), (0, 3)], alpha=0.35)
        poly(ax, [(5, 0), (8, 0), (8, 2), (5, 2)], alpha=0.35)
    elif n == 16:
        poly(ax, [(0, 0), (8, 0), (8, 3), (5, 3), (5, 6), (0, 6)], alpha=0.38)
    elif n == 17:
        poly(ax, [(0, 0), (15, 0), (15, 8), (0, 8)], alpha=0.35)
    elif n == 18:
        poly(ax, [(0, 0), (20, 0), (20, 12), (0, 12)], alpha=0.35)
    elif n == 19:
        poly(ax, [(0, 0), (12, 0), (12, 12), (0, 12)], alpha=0.32)
        poly(ax, [(3, 3), (9, 3), (9, 9), (3, 9)], fill=C_GRAY, alpha=0.45)
    elif n == 20:
        poly(ax, [(0, 0), (30, 0), (30, 20), (0, 20)], alpha=0.32)
    # גבולות מתאימים לכל צורה — לא לחתוך מלבנים גדולים (בעבר הוגדר קבוע 10×8 לכולם)
    _extent = {
        13: (8, 6),
        14: (5, 4),
        15: (8, 3),
        16: (8, 6),
        17: (15, 8),
        18: (20, 12),
        19: (12, 12),
        20: (30, 20),
    }
    emax_x, emax_y = _extent[n]
    pad_x = max(0.6, emax_x * 0.04)
    pad_y = max(0.6, emax_y * 0.04)
    ax.set_xlim(-pad_x * 0.5, emax_x + pad_x)
    ax.set_ylim(-pad_y * 0.5, emax_y + pad_y)
    save_fig(fig, stem, n)


def gen_4(stem: str, n: int) -> None:
    fig, ax = fig_axes_plain()
    if n >= 13:
        poly(ax, [(0, 0), (6, 0), (6, 4), (0, 4)], alpha=0.25)
        ax.text(0.3, 2, "מלבן / ריבוע", fontsize=10)
    ax.set_xlim(-0.5, 7)
    ax.set_ylim(-0.5, 5)
    save_fig(fig, stem, n)


def gen_5(stem: str, n: int) -> None:
    gen_4(stem, n)  # same schematic style


def gen_6(stem: str, n: int) -> None:
    fig, ax = fig_axes_plain()
    poly(ax, [(0, 0), (5, 0), (5, 3), (0, 3)], alpha=0.2)
    ax.text(0.3, 1.5, "אלגברה + צורה", fontsize=10)
    ax.set_xlim(-0.5, 6)
    ax.set_ylim(-0.5, 4)
    save_fig(fig, stem, n)


def gen_7(stem: str, n: int) -> None:
    fig, ax = fig_axes_plain()
    if n == 9:
        poly(ax, [(0, 0), (2, 3), (-2, 3)], alpha=0.3)
    elif n == 10:
        poly(ax, [(0, 0), (3, 0), (1.5, 2.6)], alpha=0.3)
    elif n == 11:
        poly(ax, [(0, 0), (3, 0), (3, 4)], alpha=0.25)
        ax.plot([3], [4], "ko", ms=4)
    elif n == 12:
        poly(ax, [(0, 0), (8, 0), (8, 6)], alpha=0.25)
    elif n == 13:
        poly(ax, [(0, 0), (3, 0), (1, 2)], alpha=0.25)
    elif n == 14:
        poly(ax, [(0, 0), (5, 0), (2.5, 4.5)], alpha=0.25)
        ax.text(-0.4, 2, "13,13,10", fontsize=8)
    elif n == 15:
        poly(ax, [(0, 0), (2, 0), (0, 2)], alpha=0.3)
    elif n == 16:
        ax.text(0.2, 0.5, "טבלת סיווג", fontsize=11)
        ax.set_xlim(0, 3)
        ax.set_ylim(0, 1)
    elif n == 17:
        poly(ax, [(0, 0), (4, 0), (1, 3.5)], alpha=0.25)
    elif n == 18:
        poly(ax, [(0, 0), (6, 0), (6, 5), (0, 5)], alpha=0.15)
        poly(ax, [(0, 5), (6, 5), (3, 9)], alpha=0.35, fill="#C8E6C9")
    elif n == 19:
        poly(ax, [(0, 0), (10, 0), (10, 10), (0, 10)], alpha=0.15)
        poly(ax, [(0, 0), (4, 0), (4, 10), (0, 10)], fill=C_SHADE, alpha=0.4)
    elif n == 20:
        poly(ax, [(0, 0), (4, 0), (2, 3.5)], alpha=0.25)
        poly(ax, [(1, 0), (3, 0), (3, 1), (1, 1)], fill=C_SHADE, alpha=0.5)
    ax.set_xlim(-1, 12)
    ax.set_ylim(-1, 12)
    save_fig(fig, stem, n)


def gen_8(stem: str, n: int) -> None:
    fig, ax = fig_axes_plain()
    if n == 9:
        poly(ax, [(0, 0), (9, 0), (0, 12)], alpha=0.3)
    elif n == 10:
        poly(ax, [(0, 0), (6, 0), (3, 5)], alpha=0.3)
        ax.plot([3, 3], [0, 5], "k--", lw=0.8)
    elif n == 11:
        poly(ax, [(0, 0), (10, 0), (5, 8.66)], alpha=0.25)
    elif n == 12:
        poly(ax, [(0, 0), (7, 0), (7, 24)], alpha=0.25)
    elif n == 13:
        poly(ax, [(0, 0), (6, 0), (3, 4)], alpha=0.25)
    elif n == 14:
        poly(ax, [(0, 0), (14, 0), (7, 8)], alpha=0.2)
        ax.plot([7, 7], [0, 8], "k--", lw=0.8)
    elif n == 15:
        poly(ax, [(0, 0), (5, 0), (5, 12), (0, 12)], alpha=0.15)
        poly(ax, [(0, 0), (5, 0), (5, 12)], fill=C_SHADE, alpha=0.35)
        ax.plot([0, 5, 2.5], [12, 12, 6], "k-", lw=1)
    elif n == 16:
        poly(ax, [(0, 0), (10, 0), (10, 10), (0, 10)], alpha=0.15)
        poly(ax, [(0, 0), (4, 0), (4, 10), (0, 10)], fill=C_SHADE, alpha=0.35)
    elif n == 17:
        poly(ax, [(0, 0), (25, 0), (25, 48), (0, 48)], alpha=0.12)
        poly(ax, [(0, 0), (25, 0), (25, 32)], fill=C_SHADE, alpha=0.25)
    elif n == 18:
        poly(ax, [(0, 0), (6, 0), (6, 5), (0, 5)], alpha=0.15)
        poly(ax, [(0, 5), (6, 5), (3, 9)], alpha=0.35, fill="#C8E6C9")
    elif n == 19:
        poly(ax, [(0, 0), (8, 0), (8, 6), (0, 6)], alpha=0.15)
    elif n == 20:
        poly(ax, [(0, 0), (8, 0), (4, 6.93)], alpha=0.2)
        poly(ax, [(1, 0), (3, 0), (3, 2), (1, 2)], fill=C_SHADE, alpha=0.45)
    ax.set_xlim(-1, 28)
    ax.set_ylim(-1, 52)
    save_fig(fig, stem, n)


def gen_9(stem: str, n: int) -> None:
    fig, ax = fig_axes_plain()
    if n == 9:
        poly(ax, [(0, 0), (10, 0), (10, 8), (4, 8), (4, 5), (0, 5)], alpha=0.35)
    elif n == 10:
        poly(ax, [(0, 0), (20, 0), (20, 12), (0, 12)], alpha=0.12)
        poly(ax, [(6, 3), (14, 3), (12, 8), (8, 8)], fill=C_GRAY, alpha=0.5)
    elif n == 11:
        poly(ax, [(0, 0), (16, 0), (16, 16), (0, 16)], alpha=0.1)
        for dx, dy in [(0, 0), (12, 0), (12, 12), (0, 12)]:
            poly(ax, [(dx, dy), (dx + 4, dy), (dx + 4, dy + 4), (dx, dy + 4)], fill=C_GRAY, alpha=0.35)
    elif n == 12:
        poly(ax, [(0, 0), (8, 0), (8, 8), (0, 8)], alpha=0.15)
        for c in [(0, 0), (6, 0), (6, 6), (0, 6)]:
            poly(
                ax,
                [c, (c[0] + 2, c[1]), (c[0] + 2, c[1] + 2), (c[0], c[1] + 2)],
                fill=C_SHADE,
                alpha=0.4,
            )
    elif n == 13:
        poly(ax, [(0, 0), (18, 0), (18, 10), (0, 10)], alpha=0.15)
        poly(ax, [(0, 0), (6, 0), (6, 10), (0, 10)], fill=C_SHADE, alpha=0.35)
        ax.plot([6, 18], [10, 0], "k-", lw=1)
    elif n == 14:
        poly(ax, [(0, 0), (14, 0), (10, 8), (4, 8)], alpha=0.25)
        circle(ax, (9, 4), 4, fill="#E8F4FF")
    elif n == 15:
        poly(ax, [(0, 0), (24, 0), (24, 10), (0, 10)], alpha=0.12)
        circle(ax, (5, 5), 5, fill="#E8F4FF")
    elif n == 16:
        poly(ax, [(0, 0), (8, 0), (8, 8), (0, 8)], alpha=0.12)
        circle(ax, (4, 4), 4, fill="#DDDDDD")
    elif n == 17:
        poly(ax, [(0, 0), (50, 0), (50, 20), (0, 20)], alpha=0.08)
        poly(ax, [(40, 5), (45, 5), (45, 15), (40, 15)], fill=C_SHADE, alpha=0.45)
    elif n == 18:
        poly(ax, [(0, 0), (10, 5), (20, 0), (10, -5)], alpha=0.2)
        poly(ax, [(4, -3), (16, -3), (16, 3), (4, 3)], alpha=0.15)
    elif n == 19:
        poly(ax, [(0, 0), (12, 0), (12, 12), (0, 12)], alpha=0.12)
        poly(ax, [(0, 12), (12, 12), (6, 20)], alpha=0.3)
        circle(ax, (6, 6), 6, fill="#E8E8E8")
    elif n == 20:
        poly(ax, [(0, 0), (14, 0), (14, 10), (0, 10)], alpha=0.12)
        poly(ax, [(3, 2), (11, 2), (11, 8), (3, 8)], fill=C_SHADE, alpha=0.35)
    ax.set_xlim(-1, 52)
    ax.set_ylim(-6, 24)
    save_fig(fig, stem, n)


def gen_10(stem: str, n: int) -> None:
    fig, ax = fig_axes_plain()
    poly(ax, [(0, 0), (5, 0), (6.5, 3), (1.5, 3)], alpha=0.25)
    if n >= 17:
        rh = [(0, 0), (4, 2), (0, 4), (-4, 2)]
        ax.clear()
        poly(ax, rh, alpha=0.3)
    ax.set_xlim(-5, 8)
    ax.set_ylim(-1, 6)
    save_fig(fig, stem, n)


def gen_11(stem: str, n: int) -> None:
    fig, ax = fig_axes_plain()
    if n <= 16:
        poly(ax, [(0, 0), (6, 0), (7, 3), (1, 3)], alpha=0.22)
    else:
        poly(ax, [(0, 0), (5, 1.5), (0, 3), (-5, 1.5)], alpha=0.28)
    ax.set_xlim(-6, 10)
    ax.set_ylim(-1, 6)
    save_fig(fig, stem, n)


def gen_12(stem: str, n: int) -> None:
    fig, ax = fig_axes_plain()
    poly(ax, [(0, 0), (8, 0), (6, 3), (2, 3)], alpha=0.28)
    if n >= 17:
        poly(ax, [(0, 0), (12, 0), (10, 4), (2, 4)], alpha=0.25)
        ax.plot([2, 2], [0, 4], "k--", lw=0.7)
        ax.plot([10, 10], [0, 4], "k--", lw=0.7)
    ax.set_xlim(-1, 14)
    ax.set_ylim(-1, 7)
    save_fig(fig, stem, n)


def gen_13(stem: str, n: int) -> None:
    fig, ax = fig_axes_plain()
    circle(ax, (0, 0), 3, fill="#E8F4FF", ec=C_EDGE)
    ax.plot([0], [0], "ko", ms=4)
    ax.set_xlim(-4, 4)
    ax.set_ylim(-4, 4)
    save_fig(fig, stem, n)


def gen_14(stem: str, n: int) -> None:
    fig, ax = fig_axes_plain()
    if n in (9, 18):
        poly(ax, [(0, 0), (20, 0), (14, 8), (6, 8)], alpha=0.22)
    elif n in (3, 4, 10, 11, 16, 17):
        circle(ax, (0, 0), 3, fill="#E8F4FF")
    elif n == 14:
        poly(ax, [(0, 0), (10, 0), (10, 10), (0, 10)], alpha=0.12)
        circle(ax, (5, 5), 5, fill="#DDDDDD")
    elif n == 15:
        poly(ax, [(0, 0), (12, 0), (12, 6), (0, 6)], alpha=0.12)
        arc = mpatches.Wedge((12, 0), 6, 90, 270, width=6, facecolor="#DDDDDD", edgecolor=C_EDGE)
        ax.add_patch(arc)
    elif n == 19:
        poly(ax, [(0, 0), (25, 0), (25, 10), (0, 10)], alpha=0.1)
        circle(ax, (12, 5), 3, fill="#E8E8E8")
    elif n == 20:
        poly(ax, [(0, 0), (26, 0), (18, 12), (10, 12)], alpha=0.2)
        circle(ax, (18, 6), 6, fill="#E8E8E8")
    else:
        poly(ax, [(0, 0), (10, 0), (8, 4), (2, 4)], alpha=0.25)
    ax.set_xlim(-4, 28)
    ax.set_ylim(-4, 16)
    save_fig(fig, stem, n)


def _factory_plan(ax, show_values: bool = False) -> None:
    """MAHAT factory: CDFG 22×5, extension ABCG 20×5, rooms ABCG / ADEF / rest."""
    sqrt13 = math.sqrt(13)
    C, D, G = (0, 0), (22, 0), (0, 5)
    D_top, F, J, A, B = (22, 5), (10, 5), (20, 5), (0, 10), (20, 10)
    E = (16, 5 + sqrt13)

    poly(ax, [C, D, D_top, J, B, A, G], alpha=0.14, edge=C_EDGE)
    poly(ax, [A, B, J, G], fill="#D8E8F5", alpha=0.62, edge=C_EDGE)
    poly(ax, [A, D, E, F], fill="#E8EEF5", alpha=0.45, edge=C_EDGE)
    poly(ax, [D_top, F, E], fill="#E0E0E0", alpha=0.7, edge=C_EDGE)

    ax.plot([G[0], J[0]], [G[1], J[1]], "k--", lw=1.0)
    ax.plot([A[0], E[0], D[0], F[0], A[0]], [A[1], E[1], D[1], F[1], A[1]], "k--", lw=0.9)

    for x, y, lb, dx, dy in [
        (A[0], A[1], "A", -0.35, 0.25),
        (B[0], B[1], "B", 0.2, 0.25),
        (C[0], C[1], "C", -0.35, -0.45),
        (D[0], D[1], "D", 0.2, -0.45),
        (E[0], E[1], "E", 0.15, 0.2),
        (F[0], F[1], "F", -0.2, 0.22),
        (G[0], G[1], "G", -0.35, 0.15),
    ]:
        mark_pt(ax, x, y, lb, dx=dx, dy=dy)

    ax.plot([D_top[0], J[0]], [D_top[1], J[1]], "k-", lw=1.2)
    ax.plot([J[0], J[0]], [J[1], B[1]], "k-", lw=1.2)

    ax.text(10, 7.5, "ABCG", ha="center", fontsize=8, color="#333333")
    ax.text(11, 2.5, "CDFG", ha="center", fontsize=8, color="#444444")
    ax.text(8.5, 4.2, "ADEF", ha="center", fontsize=7, color="#555555")
    ax.text(15.5, 7.0, "DEF", ha="center", fontsize=7, color="#555555")

    dim_h(ax, 0, 22, 0, "22", off=-0.9)
    dim_v(ax, 0, 0, 5, "5", off=-0.9)
    dim_h(ax, 0, 20, 10, "20", off=0.8)
    dim_v(ax, 20, 5, 10, "5", off=0.8)
    dim_v(ax, 0, 5, 10, "5", off=-1.3)
    dim_h(ax, 10, 22, 5, "12" if show_values else "60%", off=0.7)
    dim_h(ax, 0, 10, 5, "10", off=0.45, fs=7)
    seg_label(ax, D_top[0], D_top[1], E[0], E[1], "7" if show_values else "35%", frac=0.42, dx=0.6, dy=0.05)
    seg_label(ax, F[0], F[1], E[0], E[1], "7" if show_values else "35%", frac=0.42, dx=-0.6, dy=0.05)

    right_angle(ax, 0, 10, 0.35, quadrant=4)
    right_angle(ax, 20, 10, 0.35, quadrant=3)
    right_angle(ax, 0, 5, 0.35, quadrant=1)
    right_angle(ax, 0, 0, 0.35, quadrant=1)
    right_angle(ax, 22, 0, 0.35, quadrant=2)


def gen_15(stem: str, n: int) -> None:
    fig, ax = fig_axes_plain()
    if n == 9:
        outer = [(0, 0), (12, 0), (12, 10), (10, 10), (10, 4), (2, 4), (2, 10), (0, 10)]
        poly(ax, outer, alpha=0.35)
        ax.plot([2, 10, 10, 2, 2], [4, 4, 10, 10, 4], "k--", lw=0.9)
        dim_h(ax, 0, 12, 0, "12", off=-0.7)
        dim_v(ax, 12, 0, 10, "10", off=0.75)
        dim_h(ax, 2, 10, 10, "8", off=0.65)
        dim_v(ax, 10, 4, 10, "6", off=0.65)
        dim_h(ax, 0, 2, 10, "2", off=0.55)
        dim_h(ax, 10, 12, 10, "2", off=0.55)
        ax.set_xlim(-2, 14)
        ax.set_ylim(-1.5, 12)
    elif n == 10:
        poly(ax, [(0, 0), (15, 0), (15, 8), (8, 8), (8, 13), (0, 13)], alpha=0.35)
        ax.plot([8, 15], [8, 8], "k--", lw=0.8)
        ax.plot([0, 8], [8, 8], "k--", lw=0.8)
        dim_h(ax, 0, 15, 0, "15", off=-0.75)
        dim_v(ax, 0, 0, 8, "8", off=-0.85)
        dim_h(ax, 8, 15, 8, "7", off=0.55)
        dim_v(ax, 8, 8, 13, "5", off=-0.75)
        plain_text(ax, 7.5, 4, "חלק א'", ha="center", fontsize=8)
        plain_text(ax, 11.5, 10.5, "חלק ב'", ha="center", fontsize=8)
        ax.set_xlim(-2.5, 16.5)
        ax.set_ylim(-1.5, 14.5)
    elif n == 11:
        b, a = 4, 12
        poly(ax, [(b, 0), (a, 0), (a, a), (0, a), (0, b), (b, b)], alpha=0.35)
        ax.plot([0, b, b, 0], [b, b, 0, 0], "r--", lw=0.9)
        dim_h(ax, 0, a, 0, r"$a$", off=-0.75)
        dim_v(ax, a, 0, a, r"$a$", off=0.75)
        dim_h(ax, 0, b, b, r"$b$", off=-0.55)
        dim_v(ax, b, 0, b, r"$b$", off=-0.75)
        ax.set_xlim(-2, 14)
        ax.set_ylim(-1.5, 14)
    elif n == 12:
        poly(ax, [(0, 0), (20, 0), (20, 15), (0, 15)], alpha=0.12)
        poly(ax, [(3, 3), (17, 3), (17, 12), (3, 12)], fill="#F8F8F8", edge=C_EDGE, lw=1.2)
        dim_h(ax, 0, 20, 0, "20", off=-0.75)
        dim_v(ax, 20, 0, 15, "15", off=0.75)
        dim_h(ax, 3, 17, 3, "14", off=0.55)
        dim_v(ax, 17, 3, 12, "9", off=0.75)
        plain_text(ax, 10, 7.5, "חלל", ha="center", fontsize=8, color="#666666")
        ax.set_xlim(-2.5, 22.5)
        ax.set_ylim(-1.5, 17)
    elif n == 13:
        poly(ax, [(0, 0), (30, 0), (30, 20), (0, 20)], alpha=0.12)
        poly(ax, [(10, 20), (14, 20), (14, 23), (10, 23)], fill=C_FILL, alpha=0.55, edge=C_EDGE)
        poly(ax, [(30, 8), (36, 8), (36, 10), (30, 10)], fill=C_FILL, alpha=0.55, edge=C_EDGE)
        dim_h(ax, 0, 30, 0, "30", off=-0.85)
        dim_v(ax, 30, 0, 20, "20", off=0.85)
        dim_h(ax, 10, 14, 23, "4", off=0.55)
        dim_v(ax, 14, 20, 23, "3", off=0.75)
        dim_h(ax, 30, 36, 8, "6", off=-0.55)
        dim_v(ax, 36, 8, 10, "2", off=0.65)
        plain_text(ax, 12, 21.5, "כניסה 4×3", ha="center", fontsize=7)
        plain_text(ax, 33, 9, "קיר 6×2", ha="center", fontsize=7)
        ax.set_xlim(-2.5, 39)
        ax.set_ylim(-1.5, 25)
    elif n == 14:
        poly(
            ax,
            [(2, 0), (14, 0), (16, 2), (16, 14), (14, 16), (2, 16), (0, 14), (0, 2)],
            alpha=0.35,
        )
        for ox, oy in [(0, 0), (14, 0), (14, 14), (0, 14)]:
            ax.plot([ox, ox + 2, ox + 2, ox, ox], [oy, oy, oy + 2, oy + 2, oy], "r--", lw=0.8)
        dim_h(ax, 0, 16, 0, "16", off=-0.85)
        dim_v(ax, 16, 0, 16, "16", off=0.85)
        dim_h(ax, 0, 2, 0, "2", off=-1.55)
        dim_v(ax, 2, 0, 2, "2", off=-1.55)
        plain_text(ax, 8, 8, "4 פינות\nחתוכות", ha="center", fontsize=7, color="#AA3333")
        ax.set_xlim(-2.5, 18.5)
        ax.set_ylim(-2.5, 18.5)
    elif n == 15:
        poly(ax, [(0, 0), (10, 0), (10, 6), (5, 10), (0, 6)], alpha=0.35)
        ax.plot([0, 10], [6, 6], "k--", lw=0.7)
        dim_h(ax, 0, 10, 0, "10", off=-0.75)
        dim_v(ax, 10, 0, 6, "6", off=0.75)
        dim_v(ax, 5, 6, 10, "4", off=0.65)
        plain_text(ax, 5, 3, "מלבן", ha="center", fontsize=8)
        plain_text(ax, 5, 8.2, "משולש", ha="center", fontsize=8)
        ax.set_xlim(-2, 12.5)
        ax.set_ylim(-1.5, 11.5)
    elif n == 16:
        poly(ax, [(0, 0), (60, 0), (60, 60), (0, 60)], alpha=0.12)
        for ox, oy in [(15, 15), (30, 15), (15, 30), (30, 30)]:
            poly(
                ax,
                [(ox, oy), (ox + 15, oy), (ox + 15, oy + 15), (ox, oy + 15)],
                fill="#F0F0F0",
                edge=C_EDGE,
            )
        dim_h(ax, 0, 60, 0, "60", off=-2.5)
        dim_v(ax, 60, 0, 60, "60", off=2.5)
        dim_h(ax, 15, 30, 15, "15", off=0.55)
        dim_v(ax, 30, 15, 30, "15", off=0.55)
        ax.text(7.5, 7.5, "15", ha="center", fontsize=7, color="#666666")
        plain_text(ax, 30, 30, "חלונות", ha="center", fontsize=8, color="#666666")
        ax.set_xlim(-6, 66)
        ax.set_ylim(-6, 66)
    elif n == 17:
        _factory_plan(ax, show_values=False)
        ax.set_xlim(-3.5, 25)
        ax.set_ylim(-2, 13)
    elif n == 20:
        _factory_plan(ax, show_values=True)
        ax.set_xlim(-3.5, 25)
        ax.set_ylim(-2, 13)
    elif n == 18:
        poly(ax, [(0, 0), (12, 0), (12, 8), (0, 8)], alpha=0.15)
        theta = np.linspace(0, np.pi, 80)
        ax.plot(6 + 2 * np.cos(theta), 2 * np.sin(theta), "k-", lw=1.5)
        poly(ax, [(0, 5), (3, 5), (3, 8), (0, 8)], fill="#F0F0F0", edge=C_EDGE, lw=1.2)
        dim_h(ax, 0, 12, 0, "12", off=-1.05)
        dim_v(ax, 12, 0, 8, "8", off=0.85)
        dim_h(ax, 0, 3, 8, "3", off=0.55)
        dim_v(ax, 3, 5, 8, "3", off=0.65)
        ax.text(6, 2.3, r"$r=2$", ha="center", fontsize=9)
        dim_h(ax, 4, 8, 0, "4", off=-0.45, fs=7)
        plain_text(ax, 6, -1.45, "חזית", ha="center", fontsize=8)
        plain_text(ax, 6, 8.55, "אחור", ha="center", fontsize=8)
        plain_text(ax, 1.5, 6.5, "מטבח\n3×3", ha="center", fontsize=7, color="#555555")
        right_angle(ax, 3, 5, 0.3, quadrant=1)
        right_angle(ax, 0, 8, 0.3, quadrant=4)
        ax.set_xlim(-1.5, 14)
        ax.set_ylim(-2.0, 10)
    elif n == 19:
        plt.close(fig)
        fig, ax = coord_plane((-1, 11), (-1, 9), figsize=(7.2, 6.0))
        poly(ax, [(0, 0), (10, 0), (10, 8), (0, 8)], alpha=0.15)
        poly(ax, [(2, 2), (6, 2), (6, 6), (2, 6)], fill="#B8D4E8", alpha=0.7, edge=C_EDGE, lw=1.5)
        for x, y, lb, dx, dy in [
            (0, 0, "A(0,0)", -0.1, -0.55),
            (10, 0, "B(10,0)", -0.35, -0.55),
            (10, 8, "C(10,8)", -0.45, 0.15),
            (0, 8, "D(0,8)", -0.15, 0.15),
            (2, 2, "P(2,2)", -0.15, -0.55),
            (6, 2, "Q(6,2)", 0.1, -0.55),
            (6, 6, "R(6,6)", 0.1, 0.12),
            (2, 6, "S(2,6)", -0.15, 0.12),
        ]:
            mark_pt(ax, x, y, lb, dx=dx, dy=dy)
        plain_text(ax, 1, 4.2, "א'\n2×8", ha="center", fontsize=7)
        plain_text(ax, 8, 4.2, "ב'\n4×8", ha="center", fontsize=7)
        plain_text(ax, 4, 7.2, "ג'", ha="center", fontsize=8)
        plain_text(ax, 4, 1.2, "ג'", ha="center", fontsize=8)
        plain_text(ax, 4, 4, "בריכה\n4×4", ha="center", fontsize=7, color="#333333")
        dim_h(ax, 0, 10, -0.8, "10", off=0, fs=7)
        dim_v(ax, -0.8, 0, 8, "8", off=0, fs=7)
        dim_h(ax, 0, 2, 4.2, "2", off=0, fs=7)
        dim_h(ax, 6, 10, 4.2, "4", off=0, fs=7)
    else:
        poly(ax, [(0, 0), (10, 0), (10, 6), (3, 6), (3, 3), (0, 3)], alpha=0.3)
        ax.set_xlim(-1, 12)
        ax.set_ylim(-1, 8)
    save_fig(fig, stem, n)


def gen_16(stem: str, n: int) -> None:
    fig, ax = fig_axes_plain()
    poly(ax, [(0, 0), (18, 0), (18, 10), (0, 10)], alpha=0.12)
    if n in (9, 10, 17):
        poly(ax, [(0, 0), (6, 0), (6, 10), (0, 10)], fill=C_GRAY, alpha=0.45)
        ax.plot([6, 18], [10, 0], "k-", lw=1)
    elif n == 11:
        poly(ax, [(30, 15), (48, 15), (48, 35), (33, 35), (33, 25), (30, 25)], fill=C_GRAY, alpha=0.4)
    elif n == 12:
        circle(ax, (0, 0), 10, fill=None)
        circle(ax, (0, 0), 6, fill="#F0F0F0")
    elif n in (13, 14, 15):
        poly(ax, [(0, 0), (25, 0), (25, 48), (0, 48)], alpha=0.08)
        poly(ax, [(0, 0), (10, 0), (10, 48), (0, 48)], fill=C_GRAY, alpha=0.35)
    elif n == 16:
        poly(ax, [(0, 0), (10, 0), (10, 10), (0, 10)], alpha=0.1)
        poly(ax, [(3, 3), (7, 3), (7, 7), (3, 7)], fill="#555555", alpha=0.5)
    elif n == 18:
        poly(ax, [(0, 0), (10, 5), (20, 0), (10, -5)], alpha=0.15)
        poly(ax, [(4, -3), (16, -3), (16, 3), (4, 3)], alpha=0.12)
    elif n == 19:
        poly(ax, [(0, 0), (12, 0), (12, 12), (0, 12)], alpha=0.1)
        poly(ax, [(0, 12), (12, 12), (6, 20)], alpha=0.25)
        circle(ax, (6, 6), 6, fill="#CCCCCC")
    elif n == 20:
        poly(ax, [(0, 0), (16, 0), (16, 16), (0, 16)], alpha=0.08)
        poly(ax, [(4, 4), (12, 4), (12, 12), (4, 12)], fill=C_GRAY, alpha=0.35)
    ax.set_xlim(-5, 52)
    ax.set_ylim(-6, 52)
    save_fig(fig, stem, n)


def _coord_poly(ax, pts, labels, shade_idx=None):
    poly(ax, pts, alpha=0.25)
    for i, (x, y) in enumerate(pts):
        mark_pt(ax, x, y, labels[i])
    if shade_idx is not None:
        # shade triangle or region — first three vertices as example
        sub = [pts[i] for i in shade_idx]
        poly(ax, sub, fill=C_GRAY, alpha=0.45)


def gen_17(stem: str, n: int) -> None:
    if n <= 8:
        fig, ax = coord_plane((-5, 5), (-5, 5))
        if n == 1:
            ax.text(1, 4, r"$x$", fontsize=10)
            ax.text(4, 1, r"$y$", fontsize=10)
        elif n == 2:
            poly(ax, [(0, 0), (3, 0), (3, 3), (0, 3)], fill="#E3F2FD", alpha=0.5)
        elif n == 3:
            poly(ax, [(-3, 0), (0, 0), (0, 3), (-3, 3)], fill="#E3F2FD", alpha=0.4)
        elif n == 4:
            poly(ax, [(-3, -3), (0, -3), (0, 0), (-3, 0)], fill="#E3F2FD", alpha=0.4)
        elif n == 5:
            poly(ax, [(0, -3), (3, -3), (3, 0), (0, 0)], fill="#E3F2FD", alpha=0.4)
        elif n == 6:
            mark_pt(ax, 4, 0, r"$y=0$")
        elif n == 7:
            mark_pt(ax, 0, 5, r"$x=0$")
        elif n == 8:
            mark_pt(ax, 0, 0, "O")
    elif n == 9:
        fig, ax = coord_plane((-5, 6), (-6, 7))
        mark_pt(ax, 3, 4, "A")
        mark_pt(ax, -2, 5, "B")
        mark_pt(ax, -3, -1, "C")
        mark_pt(ax, 4, -6, "D")
    elif n == 10:
        fig, ax = coord_plane((-6, 2), (-6, 2))
        poly(ax, [(-4, -4), (0, -4), (0, 0), (-4, 0)], fill="#FFEBEE", alpha=0.4)
    elif n == 11:
        fig, ax = coord_plane((-2, 8), (-6, 2))
        mark_pt(ax, 5, -3, "Q")
    elif n == 12:
        fig, ax = coord_plane((-1, 5), (-1, 5))
        for x, y in [(2, 2), (-2, 2), (-2, -2), (2, -2)]:
            poly(ax, [(0, 0), (x, 0), (x, y), (0, y)], fill="#E3F2FD", alpha=0.15)
    elif n == 13:
        fig, ax = coord_plane((-7, 2), (-2, 2))
        mark_pt(ax, -5, 0, "R")
    elif n == 14:
        fig, ax = coord_plane((-2, 6), (-5, 2))
        mark_pt(ax, 0, 7, "S")
    elif n == 15:
        fig, ax = coord_plane((-1, 10), (-1, 2))
        mark_pt(ax, 2, 0, "A")
        mark_pt(ax, 8, 0, "B")
    elif n == 16:
        fig, ax = coord_plane((-2, 2), (-4, 8))
        mark_pt(ax, 0, -3, "C")
        mark_pt(ax, 0, 5, "D")
    elif n == 17:
        fig, ax = coord_plane((-1, 5), (-2, 4))
        pts = [(0, -1), (4, -1), (4, 2), (0, 2)]
        _coord_poly(ax, pts, ["A", "B", "C", "D"])
    elif n == 18:
        fig, ax = coord_plane((-6, 5), (-6, 4))
        for x, y, lb in [(3, -2, "P"), (-4, 1, "Q"), (0, -5, "R"), (-2, 0, "S")]:
            mark_pt(ax, x, y, lb)
    elif n == 19:
        fig, ax = coord_plane((-2, 8), (-5, 2))
        mark_pt(ax, 5, 0, "A")
        mark_pt(ax, 0, -3, "B")
        ax.plot([5, 0], [0, -3], "k-", lw=1.2)
    elif n == 20:
        fig, ax = coord_plane((-5, 5), (-4, 4))
        pts = [(-3, 2), (3, 2), (3, -2), (-3, -2)]
        _coord_poly(ax, pts, ["A", "B", "C", "D"])
    save_fig(fig, stem, n)


def gen_18(stem: str, n: int) -> None:
    if n <= 8:
        fig, ax = coord_plane((-4, 6), (-4, 6))
        if n == 1:
            mark_pt(ax, 3, 4, "A")
            mark_pt(ax, -2, 5, "B")
        elif n == 3:
            mark_pt(ax, 3, 4, "A(3,4)")
        elif n in (4, 5, 6, 7, 8):
            mark_pt(ax, -2, 0, "B") if n == 4 else None
            if n == 5:
                mark_pt(ax, 0, -5, "C")
            if n == 6:
                mark_pt(ax, 3, 4, "P")
                mark_pt(ax, 4, 3, "Q")
            if n == 7:
                mark_pt(ax, -3, 7, "D")
            if n == 8:
                mark_pt(ax, 0, 6, "(0,6)")
    else:
        fig, ax = coord_plane((-2, 10), (-4, 8))
        if n == 9:
            for x, y, lb in [(1, 3, "A"), (7, 3, "B"), (4, -1, "C")]:
                mark_pt(ax, x, y, lb)
            ax.plot([1, 7], [3, 3], "k--", lw=0.8)
        elif n == 10:
            mark_pt(ax, 2, 4, "A")
            mark_pt(ax, 8, 4, "B")
            mark_pt(ax, 5, 4, "M", dx=0, dy=0.25)
        elif n == 11:
            mark_pt(ax, -3, 4, "A")
            mark_pt(ax, 5, 4, "B")
            mark_pt(ax, 1, 4, "M", dx=0, dy=0.25)
        elif n == 12:
            mark_pt(ax, 0, 6, "P")
            mark_pt(ax, 8, 0, "Q")
            mark_pt(ax, 4, 3, "mid")
        elif n == 13:
            mark_pt(ax, 4, -2, "N")
            mark_pt(ax, -1, -2, "T")
        elif n == 14:
            mark_pt(ax, 4, -3, "K")
        elif n == 15:
            ax.axhline(5, color="gray", lw=0.8, ls=":")
        elif n == 16:
            ax.axvline(-2, color="gray", lw=0.8, ls=":")
        elif n == 17:
            pts = [(0, -1), (4, -1), (4, 2), (0, 2)]
            _coord_poly(ax, pts, ["A", "B", "C", "D"])
        elif n == 18:
            _coord_poly(ax, [(0, 0), (5, 0), (5, 12), (0, 12)], ["A", "B", "C", "D"])
        elif n == 19:
            _coord_poly(ax, [(0, 0), (8, 0), (8, 6), (0, 6)], ["A", "B", "C", "D"])
            mark_pt(ax, 3, 0, "E")
            ax.plot([3, 8], [0, 6], "k-", lw=1)
        elif n == 20:
            fig2, ax2 = coord_plane((-1, 12), (-1, 10))
            poly(
                ax2,
                [(0, 0), (10, 0), (10, 8), (6, 8), (6, 6), (2, 6), (2, 2), (0, 2)],
                alpha=0.25,
            )
            plt.close(fig)
            fig = fig2
            ax = ax2
    save_fig(fig, stem, n)


def gen_19(stem: str, n: int) -> None:
    if n <= 8:
        fig, ax = coord_plane((-2, 10), (-4, 8))
        pts_data = [
            ([(1, 3), (7, 3)], "horizontal"),
            ([(4, -2), (4, 5)], "vertical"),
            ([(-3, 2), (5, 2)], None),
            ([(2, -4), (2, 3)], None),
            ([(0, 0), (6, 0)], None),
            ([(-5, 4), (3, 4)], None),
            ([(0, 7), (0, -2)], None),
        ]
        if 1 <= n <= 7:
            p = pts_data[n - 1][0]
            ax.plot([p[0][0], p[1][0]], [p[0][1], p[1][1]], "o-", lw=2)
        else:
            ax.text(2, 5, r"$|AB| = b-a$", fontsize=9)
    elif n == 9:
        fig, ax = coord_plane((-1, 5), (-1, 4))
        _coord_poly(ax, [(0, -1), (4, -1), (4, 2), (0, 2)], ["A", "B", "C", "D"])
    elif n == 10:
        fig, ax = coord_plane((-2, 8), (-5, 2))
        mark_pt(ax, 5, 0, "P")
        mark_pt(ax, 0, -3, "Q")
        ax.plot([5, 0], [0, -3], "k-", lw=1.2)
    elif n == 11:
        fig, ax = coord_plane((-1, 8), (-1, 6))
        _coord_poly(ax, [(0, 0), (6, 0), (6, 4), (0, 4)], ["A", "B", "C", "D"])
    elif n == 12:
        fig, ax = coord_plane((-1, 8), (-1, 8))
        _coord_poly(ax, [(1, 1), (5, 1), (5, 5), (1, 5)], ["P", "Q", "R", "S"])
    elif n == 13:
        fig, ax = coord_plane((-6, 4), (-3, 5))
        _coord_poly(ax, [(-4, 3), (2, 3), (2, -1)], ["A", "B", "C"])
    elif n == 14:
        fig, ax = coord_plane((-2, 10), (-2, 8))
        _coord_poly(ax, [(0, 0), (8, 0), (8, 6)], ["A", "B", "C"])
    elif n == 15:
        fig, ax = coord_plane((-2, 12), (-2, 12))
        poly(ax, [(1, 2), (9, 8), (9, 2), (1, 8)], alpha=0.15)
        mark_pt(ax, 1, 2, "A")
        mark_pt(ax, 9, 8, "C")
    elif n == 16:
        fig, ax = coord_plane((-2, 12), (-2, 10))
        mark_pt(ax, 2, 0, "A")
        mark_pt(ax, 9, 0, "B")
        mark_pt(ax, 0, 1, "C")
        mark_pt(ax, 0, 7, "D")
    elif n >= 17:
        fig, ax = coord_plane((-4, 10), (-4, 10))
        _coord_poly(ax, [(0, 0), (6, 0), (6, 4), (0, 4)], ["A", "B", "C", "D"])
    save_fig(fig, stem, n)


def gen_20(stem: str, n: int) -> None:
    fig, ax = coord_plane((-2, 28), (-2, 52))
    if n == 1:
        _coord_poly(ax, [(0, 0), (5, 0), (5, 3), (0, 3)], ["A", "B", "C", "D"])
    elif n == 2:
        _coord_poly(ax, [(1, 1), (5, 1), (5, 5), (1, 5)], ["P", "Q", "R", "S"])
    elif n == 3:
        _coord_poly(ax, [(0, 0), (6, 0), (6, 4)], ["A", "B", "C"])
    elif n == 4:
        _coord_poly(ax, [(0, 0), (8, 0), (0, 5)], ["D", "E", "F"])
    elif n == 5:
        _coord_poly(ax, [(2, 1), (7, 1), (7, 4), (2, 4)], ["A", "B", "C", "D"])
    elif n == 6:
        _coord_poly(ax, [(3, 2), (9, 2), (9, 6)], ["A", "B", "C"])
    elif n == 7:
        poly(ax, [(1, 2), (7, 6), (7, 2), (1, 8)], alpha=0.12)
        mark_pt(ax, 1, 2, "A")
        mark_pt(ax, 7, 6, "C")
    elif n == 8:
        mark_pt(ax, 0, 0, "A")
        mark_pt(ax, 4, 0, "B")
    elif n == 9:
        _coord_poly(ax, [(0, -1), (4, -1), (4, 2), (0, 2)], ["A", "B", "C", "D"])
        mark_pt(ax, 2, -0.5, "M")
    elif n == 10:
        _coord_poly(ax, [(0, 0), (10, 0), (4, 6)], ["A", "B", "C"])
    elif n == 11:
        _coord_poly(ax, [(0, 0), (10, 0), (8, 4), (2, 4)], ["A", "B", "C", "D"])
    elif n == 12:
        _coord_poly(ax, [(0, 0), (6, 0), (6, 5), (0, 5)], ["A", "B", "C", "D"])
        mark_pt(ax, 2, 0, "E")
        ax.plot([2, 6], [0, 5], "k-", lw=1)
    elif n == 13:
        _coord_poly(ax, [(0, 0), (9, 0), (9, 12)], ["P", "Q", "R"])
    elif n == 14:
        _coord_poly(ax, [(0, 0), (12, 0), (10, 5), (2, 5)], ["A", "B", "C", "D"])
    elif n == 15:
        _coord_poly(ax, [(1, 1), (9, 1), (9, 6), (1, 6)], ["A", "B", "C", "D"])
        mark_pt(ax, 9, 3.5, "E")
        ax.plot([1, 9], [1, 3.5], "k-", lw=1)
    elif n == 16:
        _coord_poly(ax, [(0, 2), (4, 0), (6, 4), (2, 6)], ["A", "B", "C", "D"])
    elif n == 17:
        _coord_poly(ax, [(0, -1), (4, -1), (4, 2), (0, 2)], ["A", "B", "C", "D"])
    elif n == 18:
        _coord_poly(ax, [(0, 0), (25, 0), (25, 48), (0, 48)], ["A", "B", "C", "D"])
        mark_pt(ax, 25, 32, "E")
    elif n == 19:
        _coord_poly(ax, [(0, 0), (10, 0), (10, 8), (0, 8)], ["A", "B", "C", "D"])
        _coord_poly(ax, [(2, 2), (6, 2), (6, 6), (2, 6)], ["P", "Q", "R", "S"], shade_idx=None)
        poly(ax, [(2, 2), (6, 2), (6, 6), (2, 6)], fill="#B0BEC5", alpha=0.5)
    elif n == 20:
        _coord_poly(ax, [(0, 0), (15, 0), (15, 8), (0, 8)], ["A", "B", "C", "D"])
        mark_pt(ax, 5, 8, "E")
        mark_pt(ax, 15, 4, "F")
        poly(ax, [(0, 8), (5, 8), (15, 4)], fill=C_GRAY, alpha=0.35)
    save_fig(fig, stem, n)


GENERATORS = {
    "1_מהי_נקודה_קטע_ישר_וקרן": gen_1,
    "2_מושגי_יסוד_בזוויות": gen_2,
    "3_ההבדל_בין_היקף_לשטח": gen_3,
    "4_תכונות_המלבן_והריבוע": gen_4,
    "5_חישובי_היקף_ושטח_מלבן_וריבוע": gen_5,
    "6_שילוב_אלגברה_בסיסית": gen_6,
    "7_היכרות_עם_סוגי_משולשים": gen_7,
    "8_גובה_במשולש_וחישובי_שטח_והיקף": gen_8,
    "9_חיבור_וחיסור_שטחים": gen_9,
    "10_תכונות_המקבילית_והמעוין": gen_10,
    "11_חישובי_היקף_ושטח_מקבילית_ומעוין": gen_11,
    "12_תכונות_הטרפז_והדלתון": gen_12,
    "13_תכונות_המעגל": gen_13,
    "14_חישובי_היקף_ושטח_טרפז_דלתון_ומעגל": gen_14,
    "15_פירוק_צורות_מורכבות_לצורות_פשוטות": gen_15,
    "16_שטחים_צבועים_באפור_ויחסי_צלעות": gen_16,
    "17_היכרות_עם_מערכת_הצירים_הקרטזית": gen_17,
    "18_סימון_וקריאת_נקודות_במישור": gen_18,
    "19_חישוב_אורכי_קטעים_מקבילים_לצירים": gen_19,
    "20_חישוב_שטחים_והיקפים_במערכת_צירים": gen_20,
}


def inject_markdown() -> tuple[int, list[str]]:
    """Insert ![תרגיל N](images/6_<stem>_exNN.png) after each scoped exercise block."""
    md_files = sorted(
        f
        for f in os.listdir(CHAPTER_DIR)
        if f.endswith(".md") and not f.startswith(".")
    )
    inserted_total = 0
    touched: list[str] = []
    img_line_re = re.compile(r"!\[[^\]]*\]\(images/6_[^)]+\)")

    for fname in md_files:
        stem = fname[:-3]
        if stem not in SCOPE:
            continue
        path = os.path.join(CHAPTER_DIR, fname)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        if "<details>" in text:
            main, details = text.split("<details>", 1)
            details_block = "<details>" + details
        else:
            main, details_block = text, ""

        matches = list(re.finditer(r"(?m)^(?P<num>\d+)\.\s", main))
        if not matches:
            continue

        def span(num: int) -> tuple[int, int] | None:
            for i, m in enumerate(matches):
                if int(m.group("num")) != num:
                    continue
                start = m.start()
                end = matches[i + 1].start() if i + 1 < len(matches) else len(main)
                return start, end
            return None

        new_main = main
        offset = 0
        file_touched = False
        for ex in SCOPE[stem]:
            sp = span(ex)
            if not sp:
                SKIPPED.append((stem, ex, "exercise block not found"))
                continue
            s, e = sp
            s += offset
            e += offset
            block = new_main[s:e]
            if img_line_re.search(block):
                continue
            rel = f"images/6_{stem}_ex{ex:02d}.png"
            insert = f"\n\n![תרגיל {ex}]({rel})\n"
            new_main = new_main[:e] + insert + new_main[e:]
            offset += len(insert)
            inserted_total += 1
            file_touched = True
        if file_touched:
            touched.append(fname)
            out = new_main + details_block
            with open(path, "w", encoding="utf-8") as f:
                f.write(out)

    return inserted_total, touched


def main() -> int:
    count = 0
    for stem, exercises in SCOPE.items():
        gen = GENERATORS.get(stem)
        if not gen:
            for n in exercises:
                SKIPPED.append((stem, n, "no generator registered"))
            continue
        for n in exercises:
            try:
                gen(stem, n)
                count += 1
            except Exception as e:  # noqa: BLE001
                SKIPPED.append((stem, n, str(e)))
    print(f"Generated {count} PNG files in:\n  {IMAGES_DIR}")
    ins, touched = inject_markdown()
    print(f"Inserted {ins} image references in {len(touched)} markdown files.")
    if SKIPPED:
        print("\nSkipped / errors:")
        for s, n, msg in SKIPPED:
            print(f"  {s} ex{n:02d}: {msg}")
    return 0 if count > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
