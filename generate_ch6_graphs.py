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

# DejaVu first so Latin labels render cleanly; fall back to Hebrew-capable fonts.
plt.rcParams["font.family"] = ["DejaVu Sans", "Arial Hebrew", "Arial Unicode MS", "Arial"]
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
        ax.plot([2, 3], [0, 2], "k--", lw=1)
        ax.text(1, -0.25, "parallel lines + transversal", fontsize=8)
        ax.set_xlim(-0.5, 4.5)
        ax.set_ylim(-0.5, 2.5)
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
    if n == 13:
        poly(ax, [(0, 0), (8, 0), (8, 6), (0, 6)], alpha=0.25)
        ax.text(0.5, 3, "ריצוף", fontsize=10)
    elif n == 14:
        poly(ax, [(0, 0), (5, 0), (5, 4), (0, 4)], fill="#F5E6CC", alpha=0.5)
        ax.plot([0, 5, 5, 0, 0], [0, 0, 4, 4, 0], "k-", lw=2)
        ax.text(2, 2, "מסגרת", fontsize=10)
    elif n == 15:
        poly(ax, [(0, 0), (3, 0), (3, 3), (0, 3)], alpha=0.2)
        poly(ax, [(5, 0), (8, 0), (8, 2), (5, 2)], alpha=0.2)
    elif n == 16:
        poly(ax, [(0, 0), (8, 0), (8, 3), (5, 3), (5, 6), (0, 6)], alpha=0.3)
    elif n == 17:
        poly(ax, [(0, 0), (15, 0), (15, 8), (0, 8)], alpha=0.2)
    elif n == 18:
        poly(ax, [(0, 0), (20, 0), (20, 12), (0, 12)], alpha=0.2)
    elif n == 19:
        poly(ax, [(0, 0), (12, 0), (12, 12), (0, 12)], alpha=0.15)
        poly(ax, [(3, 3), (9, 3), (9, 9), (3, 9)], fill=C_GRAY, alpha=0.45)
    elif n == 20:
        poly(ax, [(0, 0), (30, 0), (30, 20), (0, 20)], alpha=0.15)
    ax.set_xlim(-0.5, 10)
    ax.set_ylim(-0.5, 8)
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


def gen_15(stem: str, n: int) -> None:
    fig, ax = fig_axes_plain()
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
