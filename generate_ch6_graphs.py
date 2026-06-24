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
    "12_תכונות_הטרפז_והדלתון": _rng(9, 17),
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


def angle_arc(ax, Ox, Oy, start_deg, end_deg, r=0.55, label=None, label_r=0.82, fs=8):
    """Arc marking the angle from start_deg to end_deg (CCW from +x)."""
    arc = mpatches.Arc(
        (Ox, Oy),
        2 * r,
        2 * r,
        angle=0,
        theta1=start_deg,
        theta2=end_deg,
        color="#444444",
        lw=0.9,
    )
    ax.add_patch(arc)
    if label:
        mid = math.radians((start_deg + end_deg) / 2)
        _orig_text(
            ax,
            Ox + label_r * math.cos(mid),
            Oy + label_r * math.sin(mid),
            label,
            ha="center",
            va="center",
            fontsize=fs,
            bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.85),
        )


# ═══════════════════════════════════════════════════════════════════════════
# Per-subtopic generators (schematic; matches exercise numerics where stated)

def gen_1(stem: str, n: int) -> None:
    # Exercise 13 is an angle fan — keep the equal-aspect canvas.
    if n == 13:
        fig, ax = fig_axes_plain()
        angle_fan(ax, 0, 0, [0, 35, 90], ["OA", "OC", "OB"])
        _orig_text(ax, -0.3, 1.3, r"$\angle AOB=90°$", fontsize=9)
        _orig_text(ax, 1.1, 0.5, r"$\angle AOC=35°$", fontsize=9)
        right_angle(ax, 0, 0, 0.45, quadrant=1)
        ax.set_xlim(-0.8, 3)
        ax.set_ylim(-0.5, 2.5)
        save_fig(fig, stem, n)
        return

    # Number-line exercises (14–20): a WIDE canvas with a NON-equal aspect.
    # An equal aspect would squeeze a ~40-unit line into a ~60px-tall sliver
    # where the letters collide with the dimensions. Here the point letters sit
    # ABOVE the line and every dimension sits BELOW it, so nothing overlaps.
    fig, ax = plt.subplots(figsize=(9.2, 2.6), facecolor="white")

    def _nl(pts, labels, xlim=None):
        if xlim is None:
            xlim = (min(pts) - 3, max(pts) + 3)
        ax.set_xlim(xlim)
        ax.set_ylim(-1.9, 1.5)
        ax.axhline(0, color="black", lw=1.6, zorder=1)
        for x, lb in zip(pts, labels):
            ax.plot(x, 0, "o", color="#C41E3A", ms=8, zorder=5)
            if lb:
                ax.text(
                    x, 0.30, lb, ha="center", va="bottom",
                    fontsize=13, fontweight="bold", zorder=6,
                )
        ax.axis("off")

    if n == 14:
        # AB=30, AC:CB=2:3 → A=0, C=12, B=30, D midpoint of CB=21
        _nl([0, 12, 21, 30], ["A", "C", "D", "B"], xlim=(-3, 33))
        dim_h(ax, 0, 12, 0, "12", off=-0.6, fs=9)
        dim_h(ax, 12, 30, 0, "18", off=-0.6, fs=9)
        dim_h(ax, 0, 30, 0, "30", off=-1.35, fs=9)
        plain_text(ax, 15, 1.12, "AC:CB = 2:3", ha="center", fontsize=9)
    elif n == 15:
        # a=6 → PQ=12, QR=9, RS=17, PS=38
        _nl([0, 12, 21, 38], ["P", "Q", "R", "S"], xlim=(-3, 41))
        dim_h(ax, 0, 12, 0, r"$2a$", off=-0.6, fs=10)
        dim_h(ax, 12, 21, 0, r"$a+3$", off=-0.6, fs=10)
        dim_h(ax, 21, 38, 0, r"$3a-1$", off=-0.6, fs=10)
        dim_h(ax, 0, 38, 0, r"$5a+8$", off=-1.35, fs=10)
    elif n == 16:
        # XY=40, XZ=15, W midpoint of ZY
        _nl([0, 15, 27.5, 40], ["X", "Z", "W", "Y"], xlim=(-3, 43))
        dim_h(ax, 0, 15, 0, "15", off=-0.6, fs=9)
        dim_h(ax, 15, 40, 0, "25", off=-0.6, fs=9)
        dim_h(ax, 0, 40, 0, "40", off=-1.35, fs=9)
        plain_text(ax, 21.25, 1.12, r"$ZW = WY$", ha="center", fontsize=10)
    elif n == 17:
        # AB=12, BC=18, AC=30, M midpoint of AB=6
        _nl([0, 6, 12, 30], ["A", "M", "B", "C"], xlim=(-3, 33))
        dim_h(ax, 0, 12, 0, "12", off=-0.6, fs=9)
        dim_h(ax, 12, 30, 0, "18", off=-0.6, fs=9)
        dim_h(ax, 0, 30, 0, "30", off=-1.35, fs=9)
        _orig_text(ax, 15, 1.12, r"$AB=\frac{2}{5}AC$", ha="center", fontsize=10)
    elif n == 18:
        # AB=BC=CD=DE=5, F midpoint of BD=C at 10
        _nl([0, 5, 10, 15, 20], ["A", "B", "C", "D", "E"], xlim=(-3, 23))
        dim_h(ax, 0, 5, 0, "5", off=-0.6, fs=9)
        dim_h(ax, 5, 10, 0, "5", off=-0.6, fs=9)
        dim_h(ax, 10, 15, 0, "5", off=-0.6, fs=9)
        dim_h(ax, 15, 20, 0, "5", off=-0.6, fs=9)
        plain_text(ax, 10, 1.12, r"$BF = FD$", ha="center", fontsize=10)
    elif n == 19:
        # AC=32, AB:BC=3:5 → A=0, B=12, C=32; D=6, E=22
        _nl([0, 6, 12, 22, 32], ["A", "D", "B", "E", "C"], xlim=(-3, 35))
        dim_h(ax, 0, 12, 0, "12", off=-0.6, fs=9)
        dim_h(ax, 12, 32, 0, "20", off=-0.6, fs=9)
        dim_h(ax, 0, 32, 0, "32", off=-1.35, fs=9)
        plain_text(ax, 16, 1.12, "AB:BC = 3:5", ha="center", fontsize=9)
    elif n == 20:
        # BC=10, AB=CD=10, AD=30
        _nl([0, 10, 20, 30], ["A", "B", "C", "D"], xlim=(-3, 33))
        dim_h(ax, 0, 10, 0, "10", off=-0.6, fs=9)
        dim_h(ax, 10, 20, 0, "10", off=-0.6, fs=9)
        dim_h(ax, 20, 30, 0, "10", off=-0.6, fs=9)
        dim_h(ax, 0, 30, 0, "30", off=-1.35, fs=9)
        plain_text(ax, 15, 1.12, r"$AB=CD$", ha="center", fontsize=10)
    save_fig(fig, stem, n)


def gen_2(stem: str, n: int) -> None:
    fig, ax = fig_axes_plain()
    if n == 13:
        # זווית α ומשלימתה על ישר — (180°−α) גדולה מ-α ב-40°
        ax.plot([-2.2, 2.2], [0, 0], "k-", lw=1.5)
        ax.plot([0, 1.6], [0, 1.1], "k-", lw=1.3)
        mark_pt(ax, 0, 0, "O", dx=-0.22, dy=-0.28)
        angle_arc(ax, 0, 0, 0, 33, r=0.65, label=r"$\alpha$", label_r=0.95)
        angle_arc(ax, 0, 0, 33, 180, r=0.95, label=r"$180°-\alpha$", label_r=1.35, fs=7)
        ax.set_xlim(-2.6, 2.6)
        ax.set_ylim(-0.55, 1.85)
    elif n == 14:
        # זווית ומשלמתה ביחס 2:3 (סכום 90°)
        ax.plot([0, 2.4], [0, 0], "k-", lw=1.3)
        ax.plot([0, 0], [0, 2.4], "k-", lw=1.3)
        ax.plot([0, 1.95], [0, 1.95 * math.tan(math.radians(36))], "k-", lw=1.3)
        mark_pt(ax, 0, 0, "O", dx=-0.22, dy=-0.28)
        right_angle(ax, 0, 0, 0.38, quadrant=1)
        angle_arc(ax, 0, 0, 0, 36, r=0.55, label=r"$2k$", label_r=0.82)
        angle_arc(ax, 0, 0, 36, 90, r=0.85, label=r"$3k$", label_r=1.05)
        ax.set_xlim(-0.55, 2.85)
        ax.set_ylim(-0.55, 2.85)
    elif n == 15:
        # ∠AOC=90°, ∠AOB=(3x−5)°, ∠BOC=(x+15)°  →  x=20
        angle_fan(ax, 0, 0, [0, 55, 90], ["OA", "OB", "OC"])
        right_angle(ax, 0, 0, 0.42, quadrant=1)
        angle_arc(ax, 0, 0, 0, 55, r=0.55, label=r"$(3x-5)°$", label_r=0.88, fs=7)
        angle_arc(ax, 0, 0, 55, 90, r=0.75, label=r"$(x+15)°$", label_r=1.0, fs=7)
        _orig_text(ax, 1.55, 0.35, r"$\angle AOC=90°$", fontsize=8)
        ax.set_xlim(-0.6, 3.1)
        ax.set_ylim(-0.55, 2.6)
    elif n == 16:
        # ישר AB, נקודה O, קרן OC — ∠AOC = ∠COB
        ax.plot([-2.0, 2.0], [0, 0], "k-", lw=1.5)
        ax.plot([0, 0], [0, 1.8], "k-", lw=1.3)
        mark_pt(ax, -1.5, 0, "A", dx=-0.1, dy=-0.28)
        mark_pt(ax, 0, 0, "O", dx=-0.1, dy=-0.28)
        mark_pt(ax, 1.5, 0, "B", dx=-0.05, dy=-0.28)
        mark_pt(ax, 0, 1.8, "C", dx=0.12, dy=0.05)
        angle_arc(ax, 0, 0, 90, 180, r=0.55, label=r"$(4x+10)°$", label_r=0.88, fs=7)
        angle_arc(ax, 0, 0, 0, 90, r=0.55, label=r"$\angle COB$", label_r=0.95, fs=7)
        ax.set_xlim(-2.4, 2.4)
        ax.set_ylim(-0.55, 2.35)
    elif n == 17:
        # ישרים מקבילים וחותך — זוויות חד-צדדיות (4x+10)° ו-(2x+20)°
        y1, y2 = 0.0, 2.6
        t_deg = 110.0
        tr = math.radians(t_deg)
        x0, y0 = 0.9, y1
        x1 = x0 + (y2 - y0) / math.tan(tr)
        ax.plot([0, 4.2], [y1, y1], "k-", lw=1.5)
        ax.plot([0, 4.2], [y2, y2], "k-", lw=1.5)
        ax.plot([x0, x1], [y0, y2], "k-", lw=1.3)
        plain_text(ax, 2.1, y1 - 0.42, "ישר 1", ha="center", fontsize=7)
        plain_text(ax, 2.1, y2 + 0.18, "ישר 2", ha="center", fontsize=7)
        angle_arc(ax, x0, y0, 0, t_deg, r=0.55, label=r"$(4x+10)°$", label_r=0.9, fs=7)
        angle_arc(ax, x1, y2, 360 - (180 - t_deg), 360, r=0.55, label=r"$(2x+20)°$", label_r=0.92, fs=7)
        ax.set_xlim(-0.4, 4.6)
        ax.set_ylim(-0.75, 3.35)
    elif n == 18:
        # ∠AOC=135°, ∠AOB=(5x−10)°, ∠BOC=(2x+5)°  →  x=20
        angle_fan(ax, 0, 0, [0, 90, 135], ["OA", "OB", "OC"])
        angle_arc(ax, 0, 0, 0, 90, r=0.55, label=r"$(5x-10)°$", label_r=0.88, fs=7)
        angle_arc(ax, 0, 0, 90, 135, r=0.75, label=r"$(2x+5)°$", label_r=1.0, fs=7)
        _orig_text(ax, -0.95, 0.55, r"$\angle AOC=135°$", fontsize=8)
        ax.set_xlim(-1.2, 3.2)
        ax.set_ylim(-0.6, 2.8)
    elif n == 19:
        poly(ax, [(0, 0), (3.2, 0), (1.6, 2.2)], alpha=0.22)
        mark_pt(ax, 0, 0, "A", dx=-0.28, dy=-0.22)
        mark_pt(ax, 3.2, 0, "B", dx=0.08, dy=-0.22)
        mark_pt(ax, 1.6, 2.2, "C", dx=-0.05, dy=0.08)
        _orig_text(ax, 0.15, 0.35, r"$(2x+5)°$", fontsize=8)
        _orig_text(ax, 2.45, 0.35, r"$(3x-15)°$", fontsize=8)
        _orig_text(ax, 1.35, 1.55, r"$(x+40)°$", fontsize=8)
        ax.set_xlim(-0.55, 3.75)
        ax.set_ylim(-0.55, 2.75)
    elif n == 20:
        # מלבן ABCD, אלכסון BD, ∠ABD=63°
        w = 3.2
        h = w * math.tan(math.radians(63))
        poly(ax, [(0, 0), (w, 0), (w, h), (0, h)], alpha=0.18)
        ax.plot([w, 0], [0, h], "k-", lw=1.2)
        mark_pt(ax, 0, 0, "A", dx=-0.28, dy=-0.22)
        mark_pt(ax, w, 0, "B", dx=0.08, dy=-0.22)
        mark_pt(ax, w, h, "C", dx=0.08, dy=0.05)
        mark_pt(ax, 0, h, "D", dx=-0.28, dy=0.05)
        angle_arc(ax, w, 0, 180 - 63, 180, r=0.55, label=r"$63°$", label_r=0.88, fs=8)
        ax.set_xlim(-0.55, w + 0.55)
        ax.set_ylim(-0.55, h + 0.55)
    save_fig(fig, stem, n)


def gen_3(stem: str, n: int) -> None:
    fig, ax = fig_axes_plain()
    if n == 13:
        poly(ax, [(0, 0), (8, 0), (8, 6), (0, 6)], alpha=0.35)
        dim_h(ax, 0, 8, 0, "8", off=-0.75)
        dim_v(ax, 8, 0, 6, "?", off=0.75)
        plain_text(ax, 4, 3, "ריצוף", ha="center", fontsize=9)
        ax.set_xlim(-1.5, 10)
        ax.set_ylim(-1.5, 8)
    elif n == 14:
        # תמונה 40×30, שוליים 5 מכל צד → מסגרת חיצונית 50×40
        poly(ax, [(0, 0), (50, 0), (50, 40), (0, 40)], fill="#F5E6CC", alpha=0.45, edge=C_EDGE, lw=2)
        poly(ax, [(5, 5), (45, 5), (45, 35), (5, 35)], fill="white", alpha=0.9, edge=C_EDGE, lw=1.2)
        dim_h(ax, 0, 50, 0, "50", off=-1.0)
        dim_v(ax, 50, 0, 40, "40", off=1.0)
        dim_h(ax, 5, 45, 5, "40", off=0.55)
        dim_v(ax, 45, 5, 35, "30", off=0.75)
        dim_h(ax, 0, 5, 40, "5", off=0.55)
        plain_text(ax, 25, 20, "תמונה", ha="center", fontsize=8)
        ax.set_xlim(-3, 55)
        ax.set_ylim(-2.5, 44)
    elif n == 15:
        poly(ax, [(0, 0), (5, 0), (5, 5), (0, 5)], alpha=0.35)
        poly(ax, [(7, 0), (10, 0), (10, 3), (7, 3)], alpha=0.35)
        dim_h(ax, 0, 5, 0, r"$a$", off=-0.75)
        dim_v(ax, 5, 0, 5, r"$a$", off=0.75)
        dim_h(ax, 7, 10, 0, r"$b$", off=-0.75)
        dim_v(ax, 10, 0, 3, r"$b$", off=0.75)
        plain_text(ax, 2.5, 2.5, "גדול", ha="center", fontsize=7)
        plain_text(ax, 8.5, 1.5, "קטן", ha="center", fontsize=7)
        ax.set_xlim(-1.5, 12)
        ax.set_ylim(-1.5, 7)
    elif n == 16:
        # L: מלבן 10×4 + מלבן 6×3 מחובר לצד שמאל למעלה
        poly(ax, [(0, 0), (10, 0), (10, 4), (6, 4), (6, 7), (0, 7)], alpha=0.38)
        ax.plot([0, 6], [4, 4], "k--", lw=0.7)
        dim_h(ax, 0, 10, 0, "10", off=-0.85)
        dim_v(ax, 10, 0, 4, "4", off=0.85)
        dim_h(ax, 0, 6, 7, "6", off=0.65)
        dim_v(ax, 6, 4, 7, "3", off=-0.85)
        ax.set_xlim(-2.5, 12.5)
        ax.set_ylim(-1.5, 9.5)
    elif n == 17:
        poly(ax, [(0, 0), (15, 0), (15, 8), (0, 8)], alpha=0.35)
        poly(ax, [(11, 4), (15, 4), (15, 8), (11, 8)], fill="#A8D5A2", alpha=0.65, edge=C_EDGE)
        dim_h(ax, 0, 15, 0, "15", off=-0.85)
        dim_v(ax, 15, 0, 8, "8", off=0.85)
        dim_h(ax, 11, 15, 8, "4", off=0.55)
        dim_v(ax, 15, 4, 8, "4", off=0.75)
        plain_text(ax, 13, 6, "דשא", ha="center", fontsize=8)
        ax.set_xlim(-2.5, 18)
        ax.set_ylim(-1.5, 10.5)
    elif n == 18:
        poly(ax, [(0, 0), (20, 0), (20, 12), (0, 12)], alpha=0.35)
        ax.plot([0, 0], [0, 12], color="#8B4513", lw=3.5)
        plain_text(ax, -1.2, 6, "קיר", ha="center", fontsize=8, color="#8B4513")
        dim_h(ax, 0, 20, 0, "20", off=-0.85)
        dim_v(ax, 20, 0, 12, "12", off=0.85)
        ax.set_xlim(-3, 23)
        ax.set_ylim(-1.5, 14.5)
    elif n == 19:
        # חיתוך פינתי 3×3 מפינה ימנית עליונה
        poly(ax, [(0, 0), (12, 0), (12, 9), (9, 9), (9, 12), (0, 12)], alpha=0.32)
        dim_h(ax, 0, 12, 0, "12", off=-0.85)
        dim_v(ax, 0, 0, 12, "12", off=-0.85)
        dim_v(ax, 12, 0, 9, "9", off=0.85)
        dim_h(ax, 0, 9, 12, "9", off=0.55)
        dim_h(ax, 9, 12, 9, "3", off=-0.55)
        dim_v(ax, 9, 9, 12, "3", off=-0.85)
        ax.set_xlim(-2.5, 15)
        ax.set_ylim(-1.5, 14.5)
    elif n == 20:
        poly(ax, [(0, 0), (30, 0), (30, 20), (0, 20)], alpha=0.32)
        poly(ax, [(4, 4), (12, 4), (12, 9), (4, 9)], fill="#B3E5FC", alpha=0.7, edge=C_EDGE)
        dim_h(ax, 0, 30, 0, "30", off=-1.0)
        dim_v(ax, 30, 0, 20, "20", off=1.0)
        dim_h(ax, 4, 12, 9, "8", off=0.55)
        dim_v(ax, 12, 4, 9, "5", off=0.75)
        plain_text(ax, 8, 6.5, "בריכה", ha="center", fontsize=8)
        ax.set_xlim(-3.5, 35)
        ax.set_ylim(-2.5, 23)
    save_fig(fig, stem, n)


def gen_4(stem: str, n: int) -> None:
    fig, ax = fig_axes_plain()

    def _rect_abcd(ax, w, h, alpha=0.22):
        poly(ax, [(0, 0), (w, 0), (w, h), (0, h)], alpha=alpha)
        mark_pt(ax, 0, 0, "A", dx=-0.35, dy=-0.28)
        mark_pt(ax, w, 0, "B", dx=0.1, dy=-0.28)
        mark_pt(ax, w, h, "C", dx=0.1, dy=0.08)
        mark_pt(ax, 0, h, "D", dx=-0.35, dy=0.08)
        right_angle(ax, 0, 0, min(0.35, w * 0.08, h * 0.08), quadrant=1)
        return w, h

    if n == 13:
        w, h = 6.5, 4.0
        _rect_abcd(ax, w, h, alpha=0.28)
        ax.plot([0, w], [0, h], "k-", lw=1.0)
        ax.plot([w, 0], [0, h], "k-", lw=1.0)
        mx, my = w / 2, h / 2
        mark_pt(ax, mx, my, "M", dx=0.1, dy=0.1)
        seg_label(ax, 0, 0, mx, my, r"$AM=6.5$", frac=0.45, dx=-0.45, dy=0.15, fs=8)
        ax.set_xlim(-1.5, w + 1.8)
        ax.set_ylim(-1.5, h + 1.5)
    elif n == 14:
        w, h = 7.5, 4.5
        _rect_abcd(ax, w, h, alpha=0.28)
        ax.plot([0, w], [0, h], "k--", lw=0.7)
        dim_h(ax, 0, w, 0, r"$AB=15$", off=-0.8)
        dim_v(ax, w, 0, h, r"$BC=9$", off=0.8)
        seg_label(ax, 0, 0, w, h, r"$AC$", frac=0.45, dx=0.4, dy=0.2, fs=8)
        ax.set_xlim(-1.8, w + 2.2)
        ax.set_ylim(-1.5, h + 1.8)
    elif n == 15:
        s = 5.0
        _rect_abcd(ax, s, s, alpha=0.28)
        ax.plot([0, s], [0, s], "k-", lw=1.0)
        ax.plot([s, 0], [0, s], "k-", lw=1.0)
        mx, my = s / 2, s / 2
        mark_pt(ax, mx, my, "M", dx=0.1, dy=0.1)
        seg_label(ax, 0, 0, mx, my, r"$AM=5\sqrt{2}$", frac=0.45, dx=-0.55, dy=0.15, fs=8)
        ax.set_xlim(-1.5, s + 1.8)
        ax.set_ylim(-1.5, s + 1.8)
    elif n == 16:
        w, h = 6.8, 4.0
        _rect_abcd(ax, w, h, alpha=0.28)
        dim_h(ax, 0, w, 0, r"$AB=3x+2$", off=-0.85)
        dim_h(ax, 0, w, h, r"$CD=5x-8$", off=0.65)
        ax.set_xlim(-1.8, w + 2.0)
        ax.set_ylim(-1.5, h + 1.8)
    elif n == 17:
        w, h = 12.5, 24.0
        _rect_abcd(ax, w, h, alpha=0.18)
        e_y = 16.0
        mark_pt(ax, w, e_y, "E", dx=0.12, dy=0.05)
        ax.plot([0, w], [0, e_y], "k-", lw=1.0)
        ax.plot([0, w], [0, h], "k--", lw=0.7)
        dim_h(ax, 0, w, 0, r"$AB=25$", off=-1.0)
        dim_v(ax, w, 0, h, r"$BC=48$", off=1.0)
        plain_text(ax, w + 0.15, h * 0.55, r"$BE=2\cdot EC$", fontsize=7)
        ax.set_xlim(-2.5, w + 3.5)
        ax.set_ylim(-1.8, h + 2.0)
    elif n == 18:
        plt.close(fig)
        pts = [(0, -1), (4, -1), (4, 2), (0, 2)]
        xlim, ylim = _plane_for_pts(pts, pad=1.2)
        fig, ax = coord_plane(xlim, ylim)
        _coord_poly_pts(ax, pts, ["A", "B", "C", "D"])
        ax.plot([0, 4], [-1, 2], "k--", lw=0.7)
        ax.plot([4, 0], [-1, 2], "k--", lw=0.7)
        mx, my = 2, 0.5
        mark_pt(ax, mx, my, "M", dx=0.1, dy=0.12)
    elif n == 19:
        w, h = 7.08, 13.9
        _rect_abcd(ax, w, h, alpha=0.22)
        mx, my = w / 2, h / 2
        mark_pt(ax, mx, my, "M", dx=0.1, dy=0.1)
        mark_pt(ax, mx, h, "E", dx=0.1, dy=0.1)
        ax.plot([0, w], [0, h], "k--", lw=0.6)
        ax.plot([w, 0], [0, h], "k--", lw=0.8)
        ax.plot([mx, mx], [my, h], "k-", lw=1.0)
        angle_arc(ax, w, 0, 117, 180, r=0.65, label=r"$63°$", label_r=0.95, fs=8)
        seg_label(ax, w, h, mx, my, r"$CM=7.8$", frac=0.36, dx=0.55, dy=0.45, fs=7)
        plain_text(ax, w / 2, -0.55, r"$\angle ABD=63°$", ha="center", fontsize=7)
        plain_text(
            ax,
            mx - 0.3,
            my + 1.9,
            r"$ME \parallel AD$",
            ha="right",
            fontsize=7,
            bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.9),
        )
        ax.set_xlim(-1.8, w + 2.5)
        ax.set_ylim(-1.5, h + 1.8)
    elif n == 20:
        sq, rw, rh = 4.0, 5.5, 3.5
        gap = 1.2
        poly(ax, [(0, 0), (sq, 0), (sq, sq), (0, sq)], alpha=0.28)
        mark_pt(ax, 0, 0, "A", dx=-0.35, dy=-0.28)
        mark_pt(ax, sq, 0, "B", dx=0.1, dy=-0.28)
        mark_pt(ax, sq, sq, "C", dx=0.1, dy=0.08)
        mark_pt(ax, 0, sq, "D", dx=-0.35, dy=0.08)
        ox = sq + gap
        poly(ax, [(ox, 0), (ox + rw, 0), (ox + rw, rh), (ox, rh)], alpha=0.28, fill="#E8F4E8")
        mark_pt(ax, ox, 0, "E", dx=-0.35, dy=-0.28)
        mark_pt(ax, ox + rw, 0, "F", dx=0.1, dy=-0.28)
        mark_pt(ax, ox + rw, rh, "G", dx=0.1, dy=0.08)
        mark_pt(ax, ox, rh, "H", dx=-0.35, dy=0.08)
        dim_h(ax, 0, sq, 0, r"$x+3$", off=-0.75)
        dim_h(ax, ox, ox + rw, 0, r"$x+7$", off=-0.75)
        dim_v(ax, ox + rw, 0, rh, r"$x+1$", off=0.75)
        plain_text(ax, sq / 2, sq + 0.35, "ריבוע", ha="center", fontsize=8)
        plain_text(ax, ox + rw / 2, rh + 0.35, "מלבן", ha="center", fontsize=8)
        ax.set_xlim(-1.2, ox + rw + 1.8)
        ax.set_ylim(-1.2, max(sq, rh) + 1.2)
    else:
        ax.set_xlim(-0.5, 7)
        ax.set_ylim(-0.5, 5)
    save_fig(fig, stem, n)


def gen_5(stem: str, n: int) -> None:
    fig, ax = fig_axes_plain()

    def _rect_abcd(ax, w, h, alpha=0.22):
        poly(ax, [(0, 0), (w, 0), (w, h), (0, h)], alpha=alpha)
        mark_pt(ax, 0, 0, "A", dx=-0.35, dy=-0.28)
        mark_pt(ax, w, 0, "B", dx=0.1, dy=-0.28)
        mark_pt(ax, w, h, "C", dx=0.1, dy=0.08)
        mark_pt(ax, 0, h, "D", dx=-0.35, dy=0.08)
        right_angle(ax, 0, 0, min(0.35, w * 0.08, h * 0.08), quadrant=1)
        return w, h

    if n == 13:
        w, h = 7, 4
        poly(ax, [(0, 0), (w, 0), (w, h), (0, h)], alpha=0.32)
        dim_h(ax, 0, w, 0, "7 מ'", off=-0.75)
        dim_v(ax, w, 0, h, "4 מ'", off=0.75)
        plain_text(ax, w / 2, h / 2, "גינה", ha="center", fontsize=9)
        ax.set_xlim(-1.5, w + 2)
        ax.set_ylim(-1.5, h + 1.5)
    elif n == 14:
        w, h = 5, 3
        poly(ax, [(0, 0), (w, 0), (w, h), (0, h)], alpha=0.32, fill="#F5E6CC")
        dim_h(ax, 0, w, 0, "5 מ'", off=-0.7)
        dim_v(ax, w, 0, h, "3 מ'", off=0.7)
        plain_text(ax, w / 2, h / 2, "חדר", ha="center", fontsize=9)
        ax.set_xlim(-1.2, w + 1.8)
        ax.set_ylim(-1.2, h + 1.2)
    elif n == 15:
        s_outer, s_inner = 10, 5
        poly(ax, [(0, 0), (s_outer, 0), (s_outer, s_outer), (0, s_outer)], alpha=0.18)
        off = (s_outer - s_inner) / 2
        poly(
            ax,
            [
                (off, off),
                (off + s_inner, off),
                (off + s_inner, off + s_inner),
                (off, off + s_inner),
            ],
            fill=C_SHADE,
            alpha=0.45,
        )
        mark_pt(ax, 0, 0, "A", dx=-0.4, dy=-0.3)
        mark_pt(ax, s_outer, 0, "B", dx=0.12, dy=-0.3)
        mark_pt(ax, s_outer, s_outer, "C", dx=0.12, dy=0.1)
        mark_pt(ax, 0, s_outer, "D", dx=-0.4, dy=0.1)
        mark_pt(ax, off, off, "E", dx=-0.35, dy=-0.3)
        mark_pt(ax, off + s_inner, off, "F", dx=0.1, dy=-0.3)
        mark_pt(ax, off + s_inner, off + s_inner, "G", dx=0.1, dy=0.1)
        mark_pt(ax, off, off + s_inner, "H", dx=-0.35, dy=0.1)
        dim_h(ax, 0, s_outer, 0, "10 ס\"מ", off=-0.85)
        dim_h(ax, off, off + s_inner, off, "5 ס\"מ", off=0.55, fs=7)
        ax.set_xlim(-1.5, s_outer + 1.5)
        ax.set_ylim(-1.5, s_outer + 1.5)
    elif n == 16:
        w, h = 6, 18
        poly(ax, [(0, 0), (w, 0), (w, h), (0, h)], alpha=0.2)
        poly(ax, [(-0.3, -0.3), (w + 2, -0.3), (w + 2, h + 2), (-0.3, h + 2)], alpha=0.12, fill="#E8F4E8")
        dim_h(ax, 0, w, 0, r"$w$", off=-0.7)
        dim_v(ax, w, 0, h, r"$3w$", off=0.8)
        dim_h(ax, -0.3, w + 2, -0.3, r"$w+2$", off=-0.55, fs=7)
        dim_v(ax, w + 2, -0.3, h + 2, r"$3w+2$", off=0.75, fs=7)
        plain_text(ax, w / 2, h + 1.2, "+2 ס\"מ לכל ממד", ha="center", fontsize=7)
        ax.set_xlim(-1.5, w + 3.5)
        ax.set_ylim(-1.5, h + 2.5)
    elif n == 17:
        w, h = 7.5, 4.5
        _rect_abcd(ax, w, h)
        e_x = w * 2 / 3
        mark_pt(ax, e_x, h, "E", dx=0.1, dy=0.1)
        ax.plot([e_x, 0], [h, 0], "k-", lw=1.0)
        ax.plot([e_x, w], [h, 0], "k-", lw=0.7, ls="--")
        dim_h(ax, 0, w, 0, "7.5 מ'", off=-0.85)
        dim_v(ax, w, 0, h, "4.5 מ'", off=0.85)
        dim_h(ax, 0, e_x, h, r"$DE$", off=0.55, fs=7)
        dim_h(ax, e_x, w, h, r"$EC$", off=0.55, fs=7)
        seg_label(ax, 0, h / 2, e_x, h, r"$2 \cdot EC$", frac=0.5, dx=-0.5, dy=0.2, fs=7)
        ax.set_xlim(-1.8, w + 2.2)
        ax.set_ylim(-1.5, h + 1.8)
    elif n == 18:
        w, h = 12, 26
        _rect_abcd(ax, w, h)
        e_y = 12
        mark_pt(ax, w, e_y, "E", dx=0.12, dy=0.05)
        ax.plot([0, w], [0, e_y], "k-", lw=1.0)
        ax.plot([0, w], [0, h], "k-", lw=1.0)
        dim_h(ax, 0, w, 0, "12 ס\"מ", off=-0.9)
        dim_v(ax, w, 0, h, "26 ס\"מ", off=0.95)
        dim_v(ax, w, 0, e_y, r"$BE$", off=1.35, fs=7)
        dim_v(ax, w, e_y, h, r"$EC$", off=1.35, fs=7)
        seg_label(ax, 0, 0, w, h, r"$AC$", frac=0.45, dx=0.5, dy=0.3, fs=7)
        plain_text(ax, w / 2, h + 0.85, r"$AB=BE$", ha="center", fontsize=8)
        ax.set_xlim(-2, w + 3)
        ax.set_ylim(-1.5, h + 2)
    elif n == 19:
        l_vis, w_vis = 14, 7
        poly(ax, [(0, 0), (l_vis, 0), (l_vis, w_vis), (0, w_vis)], alpha=0.28)
        dim_h(ax, 0, l_vis, 0, r"$2w$", off=-1.1)
        dim_v(ax, l_vis, 0, w_vis, r"$w$", off=1.1)
        plain_text(ax, l_vis / 2, w_vis / 2, "מגרש", ha="center", fontsize=9)
        plain_text(ax, l_vis / 2, -2.0, r"אורך $= 2 \times$ רוחב", ha="center", fontsize=7)
        plain_text(ax, l_vis / 2, w_vis + 0.75, r"היקף $= 84$ מ'", ha="center", fontsize=8)
        ax.set_xlim(-3, l_vis + 4)
        ax.set_ylim(-2.8, w_vis + 2.5)
    elif n == 20:
        w, h = 8, 15
        _rect_abcd(ax, w, h)
        e_y = 10
        mark_pt(ax, w, e_y, "E", dx=0.12, dy=0.05)
        ax.plot([0, w], [0, e_y], color="#C41E3A", lw=1.0)
        ax.plot([0, w], [0, h], color="#1565C0", lw=0.8)
        dim_h(ax, 0, w, 0, "8 ס\"מ", off=-0.85)
        dim_v(ax, w, 0, h, "15 ס\"מ", off=1.0)
        dim_v(ax, w, 0, e_y, r"$BE$", off=1.45, fs=7)
        dim_v(ax, w, e_y, h, r"$EC$", off=1.45, fs=7)
        plain_text(ax, w / 2, h + 0.85, r"$BE=2 \cdot EC$", ha="center", fontsize=8)
        seg_label(ax, 0, 0, w, e_y, r"$\triangle ABE$", frac=0.35, dx=-0.6, dy=0.2, fs=7)
        seg_label(ax, 0, 0, w, h, r"$\triangle AEC$", frac=0.55, dx=0.6, dy=0.2, fs=7)
        ax.set_xlim(-2.2, w + 3)
        ax.set_ylim(-1.5, h + 2)
    save_fig(fig, stem, n)


def gen_6(stem: str, n: int) -> None:
    fig, ax = fig_axes_plain()

    def _rect_abcd(w, h, alpha=0.18):
        poly(ax, [(0, 0), (w, 0), (w, h), (0, h)], alpha=alpha)
        mark_pt(ax, 0, 0, "A", dx=-0.35, dy=-0.28)
        mark_pt(ax, w, 0, "B", dx=0.1, dy=-0.28)
        mark_pt(ax, w, h, "C", dx=0.1, dy=0.08)
        mark_pt(ax, 0, h, "D", dx=-0.35, dy=0.08)
        right_angle(ax, 0, 0, min(0.35, w * 0.07, h * 0.07), quadrant=1)

    if n == 13:
        s_a = 4.0
        w_b, h_b = 8.0, 2.0
        gap = 1.2
        poly(ax, [(0, 0), (s_a, 0), (s_a, s_a), (0, s_a)], alpha=0.32, fill="#E3F2FD")
        mark_pt(ax, s_a / 2, s_a + 0.15, "A", dx=-0.05, dy=0.05)
        seg_label(ax, 0, 0, s_a, 0, r"$x+3$", frac=0.5, dy=-0.35, fs=8)
        x0 = s_a + gap
        poly(ax, [(x0, 0), (x0 + w_b, 0), (x0 + w_b, h_b), (x0, h_b)], alpha=0.32, fill="#FFF3E0")
        mark_pt(ax, x0 + w_b / 2, h_b + 0.15, "B", dx=-0.05, dy=0.05)
        dim_h(ax, x0, x0 + w_b, 0, r"$x+7$", off=-0.7)
        dim_v(ax, x0 + w_b, 0, h_b, r"$x+1$", off=0.7)
        plain_text(ax, (s_a + x0 + w_b) / 2, -0.95, r"שטחים שווים", ha="center", fontsize=8)
        ax.set_xlim(-1.2, x0 + w_b + 1.5)
        ax.set_ylim(-1.5, s_a + 1.2)
    elif n == 14:
        w, h = 9.0, 5.0
        _rect_abcd(w, h)
        e_x = 6.0
        mark_pt(ax, e_x, h, "E", dx=0.1, dy=0.08)
        dim_h(ax, 0, w, h, "9", off=0.55)
        plain_text(ax, w / 2, -0.85, r"$DE=2 \cdot EC$", ha="center", fontsize=7)
        ax.set_xlim(-1.5, w + 2)
        ax.set_ylim(-1.5, h + 1.5)
    elif n == 15:
        w, l_rect = 8.0, 15.0
        poly(ax, [(0, 0), (w, 0), (w, l_rect), (0, l_rect)], alpha=0.2)
        poly(ax, [(w, 0), (2 * w, 0), (2 * w, w), (w, w)], alpha=0.32, fill="#E8F5E9")
        mark_pt(ax, 0, 0, "A", dx=-0.35, dy=-0.28)
        mark_pt(ax, w, 0, "B", dx=0.1, dy=-0.28)
        mark_pt(ax, w, l_rect, "C", dx=0.1, dy=0.08)
        mark_pt(ax, 0, l_rect, "D", dx=-0.35, dy=0.08)
        dim_v(ax, 0, 0, l_rect, r"$w+7$", off=-1.05, fs=8)
        dim_v(ax, w, 0, w, r"$w$", off=0.75, fs=8)
        dim_h(ax, w, 2 * w, w, r"$w$", off=0.55, fs=8)
        plain_text(ax, w / 2, l_rect + 0.55, r"שטח מלבן $-$ שטח ריבוע $=56$", ha="center", fontsize=7)
        ax.set_xlim(-2.5, 2 * w + 1.5)
        ax.set_ylim(-1.5, l_rect + 1.5)
    elif n == 16:
        w, l0 = 8.0, 10.0
        poly(ax, [(0, 0), (w, 0), (w, l0), (0, l0)], alpha=0.28)
        poly(ax, [(0, 0), (w, 0), (w, l0 + 1), (0, l0 + 1)], alpha=0.12, fill="#E8F4E8")
        dim_v(ax, w, 0, l0, r"$l$", off=0.75)
        dim_v(ax, w, 0, l0 + 1, r"$l+1$", off=1.35, fs=7)
        dim_h(ax, 0, w, 0, r"$w$", off=-0.75)
        plain_text(ax, w / 2, l0 / 2 + 0.2, "שטח", ha="center", fontsize=8)
        _orig_text(ax, w / 2, l0 / 2 - 0.15, r"$+8$", ha="center", fontsize=8)
        plain_text(ax, w / 2, l0 / 2 - 0.5, 'מ"ר', ha="center", fontsize=8)
        plain_text(ax, w / 2, -1.05, "הגדלת אורך ב-", ha="center", fontsize=7)
        _orig_text(ax, w / 2 + 1.05, -1.05, r"$1$", ha="left", fontsize=7)
        plain_text(ax, w / 2 + 1.25, -1.05, "מ'", ha="left", fontsize=7)
        ax.set_xlim(-1.5, w + 2.5)
        ax.set_ylim(-1.8, l0 + 2.2)
    elif n == 17:
        w, h, be, bf = 50.0, 20.0, 10.0, 5.0
        _rect_abcd(w, h)
        poly(ax, [(w, 0), (w - bf, 0), (w, be)], fill=C_GRAY, alpha=0.45)
        ax.plot([w, w - bf, w], [0, 0, be], "k-", lw=1.1)
        mark_pt(ax, w, be, "E", dx=0.1, dy=0.05)
        mark_pt(ax, w - bf, 0, "F", dx=0.1, dy=-0.28)
        right_angle(ax, w, 0, 0.9, quadrant=3)
        dim_h(ax, 0, w, 0, "50", off=-0.9)
        dim_v(ax, 0, 0, h, "20", off=-1.1)
        dim_v(ax, w, 0, be, "10", off=0.85)
        dim_h(ax, w - bf, w, 0, "5", off=-1.35, fs=7)
        ax.set_xlim(-4, w + 4)
        ax.set_ylim(-2.5, h + 2)
    elif n == 18:
        w, h, ae = 25.0, 10.0, 5.0
        _rect_abcd(w, h)
        mark_pt(ax, ae, 0, "E", dx=0.1, dy=-0.28)
        poly(ax, [(0, 0), (ae, 0), (0, h)], fill="#E3F2FD", alpha=0.45)
        poly(ax, [(ae, 0), (w, 0), (w, h), (0, h)], fill="#FFF8E1", alpha=0.35)
        ax.plot([0, ae, w, w, 0], [0, 0, 0, h, h], "k-", lw=0.9)
        dim_h(ax, 0, w, 0, "25", off=-0.85)
        dim_v(ax, 0, 0, h, "10", off=-1.0)
        plain_text(ax, w / 2, -1.55, r"$AE:EB=1:4$", ha="center", fontsize=7)
        seg_label(ax, ae / 2, 0, ae / 2, h / 2, r"$\triangle ADE$", frac=0.55, dx=0.45, dy=0.0, fs=7)
        plain_text(ax, w * 0.62, h * 0.55, r"טרפז $EBCD$", fontsize=7)
        ax.set_xlim(-2.5, w + 2.5)
        ax.set_ylim(-2.2, h + 1.5)
    elif n == 19:
        w, h = 8.0, 19.0
        ef = 38.0
        _rect_abcd(w, h)
        e_x = w / 2
        mark_pt(ax, e_x, 0, "E", dx=0.1, dy=-0.28)
        mark_pt(ax, e_x, -ef, "F", dx=0.1, dy=-0.28)
        poly(ax, [(0, 0), (w, 0), (e_x, -ef)], fill="#FFEBEE", alpha=0.5)
        ax.plot([0, w, e_x, e_x], [0, 0, -ef, 0], "k-", lw=1.1)
        right_angle(ax, e_x, 0, 0.45, quadrant=4)
        dim_h(ax, 0, w, 0, "8", off=-0.85)
        dim_h(ax, 0, w, h, "8", off=0.55)
        dim_v(ax, w, 0, h, "19", off=0.85)
        dim_v(ax, e_x, 0, -ef, "38", off=1.05)
        seg_label(ax, 0, 0, e_x, -ef, r"$\triangle ABF$", frac=0.42, dx=-0.55, dy=0.0, fs=7)
        plain_text(ax, w / 2, -ef - 1.1, r"$EF \perp AB$, $EF=2 \times BC$", ha="center", fontsize=7)
        ax.set_xlim(-2, w + 2.5)
        ax.set_ylim(-ef - 2, h + 1.5)
    elif n == 20:
        w, h, be = 12.0, 26.0, 12.0
        _rect_abcd(w, h)
        mark_pt(ax, w, be, "E", dx=0.12, dy=0.05)
        ax.plot([0, w], [0, be], color="#C41E3A", lw=1.0)
        ax.plot([0, w], [0, h], color="#1565C0", lw=0.9)
        dim_h(ax, 0, w, 0, "12", off=-0.85)
        dim_v(ax, w, 0, h, "26", off=0.95)
        dim_v(ax, w, 0, be, "12", off=1.35, fs=7)
        plain_text(ax, w + 0.2, 6, r"$AB=BE$", fontsize=7)
        seg_label(ax, 0, 0, w, be, r"$\triangle ABE$", frac=0.35, dx=-0.55, dy=0.15, fs=7)
        seg_label(ax, 0, 0, w, h, r"$\triangle AEC$", frac=0.55, dx=0.55, dy=0.15, fs=7)
        ax.set_xlim(-2.2, w + 3)
        ax.set_ylim(-1.5, h + 1.5)
    save_fig(fig, stem, n)


def gen_7(stem: str, n: int) -> None:
    fig, ax = fig_axes_plain()
    if n == 9:
        # שווה-שוקיים, זווית בסיס 65°
        b, h = 4.0, 3.2
        poly(ax, [(0, 0), (b, 0), (b / 2, h)], alpha=0.28)
        mark_pt(ax, b / 2, h, "A", dx=-0.05, dy=0.08)
        mark_pt(ax, 0, 0, "B", dx=-0.28, dy=-0.22)
        mark_pt(ax, b, 0, "C", dx=0.08, dy=-0.22)
        angle_arc(ax, 0, 0, 0, 65, r=0.65, label=r"$65°$", label_r=0.95)
        angle_arc(ax, b, 0, 115, 180, r=0.65, label=r"$65°$", label_r=0.95)
        ax.set_xlim(-1.2, 5.5)
        ax.set_ylim(-1.0, 4.5)
    elif n == 10:
        # שווה-צלעות
        s = 4.0
        h = s * math.sqrt(3) / 2
        poly(ax, [(0, 0), (s, 0), (s / 2, h)], alpha=0.28)
        mark_pt(ax, 0, 0, "A", dx=-0.28, dy=-0.22)
        mark_pt(ax, s, 0, "B", dx=0.08, dy=-0.22)
        mark_pt(ax, s / 2, h, "C", dx=-0.05, dy=0.08)
        angle_arc(ax, 0, 0, 0, 60, r=0.55, label=r"$60°$", label_r=0.82)
        angle_arc(ax, s, 0, 120, 180, r=0.55, label=r"$60°$", label_r=0.82)
        angle_arc(ax, s / 2, h, 240, 300, r=0.55, label=r"$60°$", label_r=0.82)
        ax.set_xlim(-1.2, 5.5)
        ax.set_ylim(-1.0, 4.5)
    elif n == 11:
        # ישר-זווית, זווית 30° ב-A (זווית ישרה ב-B)
        poly(ax, [(0, 0), (4, 0), (4, 2.31)], alpha=0.28)
        mark_pt(ax, 0, 0, "A", dx=-0.28, dy=-0.22)
        mark_pt(ax, 4, 0, "B", dx=0.08, dy=-0.22)
        mark_pt(ax, 4, 2.31, "C", dx=0.08, dy=0.05)
        right_angle(ax, 4, 0, 0.38, quadrant=2)
        angle_arc(ax, 0, 0, 0, 30, r=0.55, label=r"$30°$", label_r=0.88)
        ax.set_xlim(-1.0, 5.5)
        ax.set_ylim(-1.0, 3.5)
    elif n == 12:
        # בדיקת פיתגורס 8, 15, 17
        poly(ax, [(0, 0), (8, 0), (8, 15)], alpha=0.25)
        mark_pt(ax, 0, 0, "A", dx=-0.28, dy=-0.22)
        mark_pt(ax, 8, 0, "B", dx=0.08, dy=-0.22)
        mark_pt(ax, 8, 15, "C", dx=0.08, dy=0.05)
        right_angle(ax, 8, 0, 0.45, quadrant=2)
        dim_h(ax, 0, 8, 0, "8", off=-0.75)
        dim_v(ax, 8, 0, 15, "15", off=0.75)
        seg_label(ax, 0, 0, 8, 15, "17", frac=0.45, dx=-0.35, dy=0.15)
        ax.set_xlim(-1.5, 11)
        ax.set_ylim(-1.5, 17)
    elif n == 13:
        # זוויות (x+10)°, (2x-5)°, (4x+35)°
        poly(ax, [(0, 0), (4.2, 0), (1.4, 2.4)], alpha=0.25)
        mark_pt(ax, 0, 0, "A", dx=-0.28, dy=-0.22)
        mark_pt(ax, 4.2, 0, "B", dx=0.08, dy=-0.22)
        mark_pt(ax, 1.4, 2.4, "C", dx=-0.05, dy=0.08)
        _orig_text(ax, 0.35, 0.35, r"$(x+10)°$", fontsize=8)
        _orig_text(ax, 2.85, 0.35, r"$(2x-5)°$", fontsize=8)
        _orig_text(ax, 1.15, 1.65, r"$(4x+35)°$", fontsize=8)
        ax.set_xlim(-0.8, 5.0)
        ax.set_ylim(-0.8, 3.2)
    elif n == 14:
        # ABC שווה-שוקיים: AB=AC=13, BC=10
        b, h = 10.0, 12.0
        poly(ax, [(0, 0), (b, 0), (b / 2, h)], alpha=0.25)
        mark_pt(ax, b / 2, h, "A", dx=-0.05, dy=0.08)
        mark_pt(ax, 0, 0, "B", dx=-0.28, dy=-0.22)
        mark_pt(ax, b, 0, "C", dx=0.08, dy=-0.22)
        seg_label(ax, 0, 0, b / 2, h, "13", frac=0.5, dx=-0.35, dy=0.0)
        seg_label(ax, b, 0, b / 2, h, "13", frac=0.5, dx=0.35, dy=0.0)
        dim_h(ax, 0, b, 0, "10", off=-0.85)
        ax.set_xlim(-1.5, 12)
        ax.set_ylim(-1.5, 14)
    elif n == 15:
        # משולש 45°-45°-90°, יתר 10
        leg = 10 / math.sqrt(2)
        poly(ax, [(0, 0), (leg, 0), (0, leg)], alpha=0.28)
        mark_pt(ax, 0, 0, "A", dx=-0.28, dy=-0.22)
        mark_pt(ax, leg, 0, "B", dx=0.08, dy=-0.22)
        mark_pt(ax, 0, leg, "C", dx=-0.28, dy=0.05)
        right_angle(ax, 0, 0, 0.45, quadrant=1)
        angle_arc(ax, leg, 0, 90, 135, r=0.55, label=r"$45°$", label_r=0.85)
        angle_arc(ax, 0, leg, 270, 315, r=0.55, label=r"$45°$", label_r=0.85)
        seg_label(ax, leg, 0, 0, leg, "10", frac=0.5, dx=0.25, dy=0.0)
        ax.set_xlim(-1.2, 9.5)
        ax.set_ylim(-1.2, 9.5)
    elif n == 16:
        # תרגיל 17 במרקדאון: ABC שווה-שוקיים, BC=10, ∠A=100°
        b, h = 10.0, 3.5
        poly(ax, [(0, 0), (b, 0), (b / 2, h)], alpha=0.28)
        mark_pt(ax, b / 2, h, "A", dx=-0.05, dy=0.08)
        mark_pt(ax, 0, 0, "B", dx=-0.28, dy=-0.22)
        mark_pt(ax, b, 0, "C", dx=0.08, dy=-0.22)
        angle_arc(ax, b / 2, h, 240, 300, r=0.55, label=r"$100°$", label_r=0.88)
        dim_h(ax, 0, b, 0, "10", off=-0.75)
        ax.set_xlim(-1.5, 12)
        ax.set_ylim(-1.5, 5.5)
    elif n == 17:
        # תרגיל 17: ABC שווה-שוקיים, BC=10, ∠A=100°
        b, h = 10.0, 3.5
        poly(ax, [(0, 0), (b, 0), (b / 2, h)], alpha=0.28)
        mark_pt(ax, b / 2, h, "A", dx=-0.05, dy=0.08)
        mark_pt(ax, 0, 0, "B", dx=-0.28, dy=-0.22)
        mark_pt(ax, b, 0, "C", dx=0.08, dy=-0.22)
        angle_arc(ax, b / 2, h, 240, 300, r=0.55, label=r"$100°$", label_r=0.88)
        dim_h(ax, 0, b, 0, "10", off=-0.75)
        ax.set_xlim(-1.5, 12)
        ax.set_ylim(-1.5, 5.5)
    elif n == 18:
        # תרגיל 18: מלבן ABCD 6×5 + משולש ECD, גובה 4
        w, h_rect, h_tri = 6.0, 5.0, 4.0
        poly(ax, [(0, 0), (w, 0), (w, h_rect), (0, h_rect)], alpha=0.15)
        poly(ax, [(0, h_rect), (w, h_rect), (w / 2, h_rect + h_tri)], alpha=0.35, fill="#C8E6C9")
        mark_pt(ax, 0, 0, "A", dx=-0.28, dy=-0.22)
        mark_pt(ax, w, 0, "B", dx=0.08, dy=-0.22)
        mark_pt(ax, w, h_rect, "C", dx=0.08, dy=-0.05)
        mark_pt(ax, 0, h_rect, "D", dx=-0.28, dy=-0.05)
        mark_pt(ax, w / 2, h_rect + h_tri, "E", dx=-0.05, dy=0.08)
        dim_h(ax, 0, w, 0, "6", off=-0.75)
        dim_v(ax, w, 0, h_rect, "5", off=0.75)
        dim_v(ax, w / 2, h_rect, h_rect + h_tri, "4", off=0.75)
        ax.set_xlim(-1.5, 9)
        ax.set_ylim(-1.5, 11)
    elif n == 19:
        # תרגיל 19: ריבוע 10, E על BC, BE=4
        s = 10.0
        poly(ax, [(0, 0), (s, 0), (s, s), (0, s)], alpha=0.15)
        ax.plot([0, s], [0, 4], "k-", lw=1.2)
        mark_pt(ax, 0, 0, "A", dx=-0.28, dy=-0.22)
        mark_pt(ax, s, 0, "B", dx=0.08, dy=-0.22)
        mark_pt(ax, s, s, "C", dx=0.08, dy=0.05)
        mark_pt(ax, 0, s, "D", dx=-0.28, dy=0.05)
        mark_pt(ax, s, 4, "E", dx=0.08, dy=-0.05)
        right_angle(ax, s, 0, 0.45, quadrant=1)
        dim_h(ax, 0, s, 0, "10", off=-0.85)
        dim_v(ax, s, 0, s, "10", off=0.85)
        dim_v(ax, s, 0, 4, "4", off=0.55)
        ax.set_xlim(-1.5, 13)
        ax.set_ylim(-1.5, 13)
    elif n == 20:
        # תרגיל 20: צורה שנותרה — צלעות חיצוניות 2, 3, 4, 5, 8 (היקף 22)
        pts = [(0, 0), (8, 0), (8, 4), (5, 4), (2, 0)]
        poly(ax, pts, alpha=0.3)
        dim_h(ax, 0, 8, 0, "8", off=-0.75)
        dim_h(ax, 0, 2, 0, "2", off=-0.4)
        dim_v(ax, 8, 0, 4, "4", off=0.75)
        dim_h(ax, 5, 8, 4, "3", off=0.55)
        seg_label(ax, 5, 4, 2, 0, "5", frac=0.5, dx=0.0, dy=0.35)
        ax.set_xlim(-1.5, 10)
        ax.set_ylim(-1.5, 6)
    save_fig(fig, stem, n)


def gen_8(stem: str, n: int) -> None:
    fig, ax = fig_axes_plain()

    def _rect(w, h, alpha=0.15):
        poly(ax, [(0, 0), (w, 0), (w, h), (0, h)], alpha=alpha)
        mark_pt(ax, 0, 0, "A", dx=-0.28, dy=-0.22)
        mark_pt(ax, w, 0, "B", dx=0.08, dy=-0.22)
        mark_pt(ax, w, h, "C", dx=0.08, dy=0.05)
        mark_pt(ax, 0, h, "D", dx=-0.28, dy=0.05)

    if n == 9:
        poly(ax, [(0, 0), (9, 0), (9, 12)], alpha=0.28)
        mark_pt(ax, 0, 0, "A", dx=-0.28, dy=-0.22)
        mark_pt(ax, 9, 0, "B", dx=0.08, dy=-0.22)
        mark_pt(ax, 9, 12, "C", dx=0.08, dy=0.05)
        right_angle(ax, 9, 0, 0.45, quadrant=2)
        dim_h(ax, 0, 9, 0, "9", off=-0.75)
        seg_label(ax, 0, 0, 9, 12, "15", frac=0.45, dx=-0.35, dy=0.15)
        ax.set_xlim(-1.5, 12)
        ax.set_ylim(-1.5, 14)
    elif n == 10:
        b, h = 12.0, 8.0
        poly(ax, [(0, 0), (b, 0), (b / 2, h)], alpha=0.28)
        mark_pt(ax, b / 2, h, "A", dx=-0.05, dy=0.08)
        mark_pt(ax, 0, 0, "B", dx=-0.28, dy=-0.22)
        mark_pt(ax, b, 0, "C", dx=0.08, dy=-0.22)
        ax.plot([b / 2, b / 2], [0, h], "k--", lw=0.8)
        dim_h(ax, 0, b, 0, "12", off=-0.85)
        seg_label(ax, 0, 0, b / 2, h, "10", frac=0.5, dx=-0.35, dy=0.0)
        seg_label(ax, b, 0, b / 2, h, "10", frac=0.5, dx=0.35, dy=0.0)
        dim_v(ax, b / 2, 0, h, "8", off=0.75)
        ax.set_xlim(-1.5, 14)
        ax.set_ylim(-1.5, 10)
    elif n == 11:
        s = 10.0
        h = 5 * math.sqrt(3)
        poly(ax, [(0, 0), (s, 0), (s / 2, h)], alpha=0.25)
        mark_pt(ax, s / 2, h, "A", dx=-0.05, dy=0.08)
        mark_pt(ax, 0, 0, "B", dx=-0.28, dy=-0.22)
        mark_pt(ax, s, 0, "C", dx=0.08, dy=-0.22)
        dim_h(ax, 0, s, 0, "10", off=-0.85)
        dim_v(ax, s / 2, 0, h, r"$5\sqrt{3}$", off=0.75)
        ax.set_xlim(-1.5, 12)
        ax.set_ylim(-1.5, 10)
    elif n == 12:
        poly(ax, [(0, 0), (7, 0), (7, 24)], alpha=0.25)
        mark_pt(ax, 0, 0, "A", dx=-0.28, dy=-0.22)
        mark_pt(ax, 7, 0, "B", dx=0.08, dy=-0.22)
        mark_pt(ax, 7, 24, "C", dx=0.08, dy=0.05)
        right_angle(ax, 7, 0, 0.45, quadrant=2)
        dim_h(ax, 0, 7, 0, "7", off=-0.75)
        dim_v(ax, 7, 0, 24, "24", off=0.75)
        seg_label(ax, 0, 0, 7, 24, "25", frac=0.45, dx=-0.35, dy=0.15)
        ax.set_xlim(-1.5, 10)
        ax.set_ylim(-1.5, 27)
    elif n == 13:
        poly(ax, [(0, 0), (12, 0), (6, 6)], alpha=0.25)
        mark_pt(ax, 0, 0, "A", dx=-0.28, dy=-0.22)
        mark_pt(ax, 12, 0, "B", dx=0.08, dy=-0.22)
        mark_pt(ax, 6, 6, "C", dx=-0.05, dy=0.08)
        ax.plot([6, 6], [0, 6], "k--", lw=0.8)
        dim_h(ax, 0, 12, 0, r"$3x$", off=-0.85)
        dim_v(ax, 6, 0, 6, r"$x+2$", off=0.75)
        plain_text(ax, 4, 2.5, r"שטח $=36$", ha="center", fontsize=8)
        ax.set_xlim(-1.5, 14)
        ax.set_ylim(-1.5, 8)
    elif n == 14:
        h = 8.0
        poly(ax, [(0, 0), (14, 0), (7, h)], alpha=0.22)
        poly(ax, [(0, 0), (7, 0), (3.5, h)], alpha=0.22, fill="#D8E8F5")
        ax.plot([7, 7], [0, h], "k--", lw=0.8)
        mark_pt(ax, 0, 0, "A", dx=-0.28, dy=-0.22)
        mark_pt(ax, 14, 0, "B", dx=0.08, dy=-0.22)
        mark_pt(ax, 7, 0, "C", dx=0.08, dy=-0.22)
        mark_pt(ax, 3.5, h, "D", dx=-0.05, dy=0.08)
        dim_h(ax, 0, 14, 0, "14", off=-0.85)
        dim_h(ax, 0, 7, 0, "7", off=-0.45, fs=7)
        dim_v(ax, 7, 0, h, "8", off=0.75)
        ax.set_xlim(-1.5, 16)
        ax.set_ylim(-1.5, 10)
    elif n == 15:
        poly(ax, [(0, 0), (5, 0), (5, 12)], alpha=0.28)
        mark_pt(ax, 0, 0, "A", dx=-0.28, dy=-0.22)
        mark_pt(ax, 5, 0, "B", dx=0.08, dy=-0.22)
        mark_pt(ax, 5, 12, "C", dx=0.08, dy=0.05)
        right_angle(ax, 5, 0, 0.45, quadrant=2)
        mark_pt(ax, 2.5, 6, "D", dx=0.08, dy=0.05)
        ax.plot([5, 2.5], [0, 6], "k-", lw=1.0)
        dim_h(ax, 0, 5, 0, "5", off=-0.75)
        dim_v(ax, 5, 0, 12, "12", off=0.75)
        seg_label(ax, 0, 0, 5, 12, r"$AC$", frac=0.45, dx=-0.35, dy=0.15)
        ax.set_xlim(-1.5, 8)
        ax.set_ylim(-1.5, 14)
    elif n == 16:
        s = 10.0
        _rect(s, s)
        poly(ax, [(0, 0), (s, 0), (s, 4)], fill=C_SHADE, alpha=0.4)
        ax.plot([0, s, s], [0, 0, 4], "k-", lw=1.2)
        mark_pt(ax, s, 4, "E", dx=0.08, dy=-0.05)
        right_angle(ax, s, 0, 0.45, quadrant=1)
        dim_h(ax, 0, s, 0, "10", off=-0.85)
        dim_v(ax, s, 0, s, "10", off=0.85)
        dim_v(ax, s, 0, 4, "4", off=0.55)
        ax.set_xlim(-1.5, 13)
        ax.set_ylim(-1.5, 13)
    elif n == 17:
        w, h = 25.0, 48.0
        _rect(w, h, alpha=0.12)
        poly(ax, [(0, 0), (w, 0), (w, 32)], fill=C_SHADE, alpha=0.3)
        ax.plot([0, w], [0, 32], "k-", lw=1.0)
        mark_pt(ax, w, 32, "E", dx=0.08, dy=-0.05)
        dim_h(ax, 0, w, 0, "25", off=-1.1)
        dim_v(ax, w, 0, h, "48", off=1.1)
        dim_v(ax, w, 0, 32, "32", off=1.55, fs=7)
        dim_v(ax, w, 32, h, "16", off=1.55, fs=7)
        plain_text(ax, w + 0.2, 16, r"$BE=2\cdot EC$", fontsize=7)
        ax.set_xlim(-3, w + 5)
        ax.set_ylim(-2, h + 2)
    elif n == 18:
        w, h_rect, h_tri = 6.0, 5.0, 4.0
        _rect(w, h_rect, alpha=0.15)
        poly(ax, [(0, h_rect), (w, h_rect), (w / 2, h_rect + h_tri)], alpha=0.35, fill="#C8E6C9")
        mark_pt(ax, w / 2, h_rect + h_tri, "E", dx=-0.05, dy=0.08)
        dim_h(ax, 0, w, 0, "6", off=-0.75)
        dim_v(ax, w, 0, h_rect, "5", off=0.75)
        dim_v(ax, w / 2, h_rect, h_rect + h_tri, "4", off=0.75)
        ax.set_xlim(-1.5, 9)
        ax.set_ylim(-1.5, 11)
    elif n == 19:
        w, h = 7.5, 4.5
        _rect(w, h)
        e_x = w * 2 / 3
        mark_pt(ax, e_x, h, "E", dx=0.08, dy=0.05)
        ax.plot([0, e_x], [0, h], "k-", lw=0.9)
        ax.plot([e_x, w], [h, 0], "k-", lw=0.9)
        ax.plot([0, w], [0, h], "k--", lw=0.7)
        dim_h(ax, 0, w, 0, "7.5 מ'", off=-0.85)
        dim_v(ax, w, 0, h, "4.5 מ'", off=0.85)
        dim_h(ax, 0, e_x, h, r"$DE$", off=0.55, fs=7)
        dim_h(ax, e_x, w, h, r"$EC$", off=0.55, fs=7)
        plain_text(ax, e_x / 2, h + 0.35, r"$DE=2\cdot EC$", ha="center", fontsize=7)
        ax.set_xlim(-1.8, w + 2.2)
        ax.set_ylim(-1.5, h + 1.8)
    elif n == 20:
        w, h = 50.0, 20.0
        _rect(w, h, alpha=0.12)
        poly(ax, [(w, 0), (w - 5, 0), (w, 10)], fill=C_SHADE, alpha=0.45)
        ax.plot([w, w - 5, w], [0, 0, 10], "k-", lw=1.2)
        mark_pt(ax, w - 5, 0, "F", dx=0.08, dy=-0.22)
        mark_pt(ax, w, 10, "E", dx=0.08, dy=-0.05)
        right_angle(ax, w, 0, 0.9, quadrant=3)
        dim_h(ax, w - 5, w, 0, "5", off=-0.85)
        dim_v(ax, w, 0, 10, "10", off=0.85)
        dim_h(ax, 0, w, h, "50", off=0.55)
        dim_v(ax, 0, 0, h, "20", off=-1.1)
        ax.set_xlim(-4, w + 4)
        ax.set_ylim(-2, h + 2)
    save_fig(fig, stem, n)


def gen_9(stem: str, n: int) -> None:
    fig, ax = fig_axes_plain()
    if n == 9:
        poly(ax, [(0, 0), (10, 0), (10, 5), (6, 5), (6, 8), (0, 8)], alpha=0.35)
        dim_h(ax, 0, 10, 0, "10", off=-0.75)
        dim_v(ax, 0, 0, 8, "8", off=-0.75)
        dim_v(ax, 10, 0, 5, "5", off=0.75)
        dim_h(ax, 6, 10, 5, "4", off=0.55)
        dim_v(ax, 6, 5, 8, "3", off=0.55)
        dim_h(ax, 0, 6, 8, "6", off=0.55)
        ax.set_xlim(-2, 12.5)
        ax.set_ylim(-1.5, 10)
    elif n == 10:
        poly(ax, [(0, 0), (20, 0), (20, 12), (0, 12)], alpha=0.12)
        poly(ax, [(6, 0), (14, 0), (16, 5), (4, 5)], fill=C_GRAY, alpha=0.5)
        dim_h(ax, 0, 20, 0, "20", off=-0.85)
        dim_v(ax, 20, 0, 12, "12", off=0.85)
        dim_h(ax, 6, 14, 0, "8", off=-0.45, fs=7)
        dim_h(ax, 4, 16, 5, "12", off=0.55, fs=7)
        dim_v(ax, 16, 0, 5, "5", off=0.65, fs=7)
        plain_text(ax, 10, 2.5, "גינה", ha="center", fontsize=8, color="#555555")
        ax.set_xlim(-2.5, 22.5)
        ax.set_ylim(-1.5, 14)
    elif n == 11:
        poly(ax, [(0, 0), (16, 0), (16, 16), (0, 16)], alpha=0.1)
        for dx, dy in [(0, 0), (12, 0), (12, 12), (0, 12)]:
            poly(ax, [(dx, dy), (dx + 4, dy), (dx + 4, dy + 4), (dx, dy + 4)], fill=C_GRAY, alpha=0.35)
        dim_h(ax, 0, 16, 0, "16", off=-0.85)
        dim_v(ax, 16, 0, 16, "16", off=0.85)
        dim_h(ax, 0, 4, 0, "4", off=-1.45, fs=7)
        dim_v(ax, 4, 0, 4, "4", off=-1.45, fs=7)
        ax.set_xlim(-2.5, 18.5)
        ax.set_ylim(-2.5, 18.5)
    elif n == 12:
        s = 8.0
        leg = s / 4
        poly(ax, [(0, 0), (s, 0), (s, s), (0, s)], alpha=0.12)
        for tri in [
            [(0, 0), (leg, 0), (0, leg)],
            [(s, 0), (s - leg, 0), (s, leg)],
            [(s, s), (s, s - leg), (s - leg, s)],
            [(0, s), (leg, s), (0, s - leg)],
        ]:
            poly(ax, tri, fill=C_SHADE, alpha=0.45)
        dim_h(ax, 0, s, 0, r"$a$", off=-0.85)
        dim_v(ax, s, 0, s, r"$a$", off=0.85)
        dim_h(ax, 0, leg, 0, r"$\frac{a}{4}$", off=-0.45, fs=7)
        dim_v(ax, leg, 0, leg, r"$\frac{a}{4}$", off=0.55, fs=7)
        ax.set_xlim(-2, 10.5)
        ax.set_ylim(-2, 10.5)
    elif n == 13:
        w, h, ae = 18.0, 10.0, 6.0
        poly(ax, [(0, 0), (w, 0), (w, h), (0, h)], alpha=0.15)
        poly(ax, [(0, 0), (ae, 0), (w, h)], fill=C_SHADE, alpha=0.4)
        ax.plot([ae, w], [0, h], "k-", lw=1.1)
        mark_pt(ax, 0, 0, "A", dx=-0.35, dy=-0.28)
        mark_pt(ax, w, 0, "B", dx=0.1, dy=-0.28)
        mark_pt(ax, w, h, "C", dx=0.1, dy=0.08)
        mark_pt(ax, 0, h, "D", dx=-0.35, dy=0.08)
        mark_pt(ax, ae, 0, "E", dx=0.08, dy=-0.35)
        dim_h(ax, 0, w, 0, "18", off=-0.85)
        dim_v(ax, w, 0, h, "10", off=0.85)
        dim_h(ax, 0, ae, 0, "6", off=-0.45, fs=7)
        ax.set_xlim(-2.5, 21)
        ax.set_ylim(-1.5, 12.5)
    elif n == 14:
        poly(ax, [(0, 0), (14, 0), (10, 8), (4, 8)], alpha=0.25)
        circle(ax, (7, 4), 4, fill="#E8F4FF")
        dim_h(ax, 0, 14, 0, "14", off=-0.85)
        dim_h(ax, 4, 10, 8, "6", off=0.55, fs=7)
        dim_v(ax, 14, 0, 8, "8", off=0.85)
        ax.text(7, 4.3, r"$d=8$", ha="center", fontsize=8)
        ax.set_xlim(-2, 16.5)
        ax.set_ylim(-1.5, 10.5)
    elif n == 15:
        poly(ax, [(0, 0), (24, 0), (24, 10), (0, 10)], alpha=0.12)
        circle(ax, (5, 5), 5, fill="#E8F4FF")
        dim_h(ax, 0, 24, 0, "24", off=-0.85)
        dim_v(ax, 24, 0, 10, "10", off=0.85)
        dim_h(ax, 0, 10, 0, "10", off=-0.45, fs=7)
        ax.set_xlim(-2, 26.5)
        ax.set_ylim(-1.5, 12.5)
    elif n == 16:
        s = 8.0
        poly(ax, [(0, 0), (s, 0), (s, s), (0, s)], alpha=0.12)
        circle(ax, (s / 2, s / 2), s / 2, fill="#DDDDDD")
        dim_h(ax, 0, s, 0, r"$a$", off=-0.85)
        dim_v(ax, s, 0, s, r"$a$", off=0.85)
        ax.text(s / 2, s / 2, r"$r=\frac{a}{2}$", ha="center", fontsize=8)
        ax.set_xlim(-2, 10.5)
        ax.set_ylim(-2, 10.5)
    elif n == 17:
        w, h, be, bf = 50.0, 20.0, 10.0, 5.0
        poly(ax, [(0, 0), (w, 0), (w, h), (0, h)], alpha=0.08)
        poly(ax, [(w, 0), (w, be), (w - bf, 0)], fill=C_SHADE, alpha=0.45)
        mark_pt(ax, 0, 0, "A", dx=-0.35, dy=-0.28)
        mark_pt(ax, w, 0, "B", dx=0.1, dy=-0.28)
        mark_pt(ax, w, h, "C", dx=0.1, dy=0.08)
        mark_pt(ax, 0, h, "D", dx=-0.35, dy=0.08)
        mark_pt(ax, w, be, "E", dx=0.12, dy=0.05)
        mark_pt(ax, w - bf, 0, "F", dx=0.08, dy=-0.35)
        dim_h(ax, 0, w, 0, "50", off=-0.85)
        dim_v(ax, 0, 0, h, "20", off=-1.1)
        dim_v(ax, w, 0, be, "10", off=0.85, fs=7)
        dim_h(ax, w - bf, w, 0, "5", off=-0.45, fs=7)
        ax.set_xlim(-4, w + 4)
        ax.set_ylim(-2, h + 2)
    elif n == 18:
        ha, hb, inset = 35, 25, 15
        A, B, C, D = (0, ha), (hb, 0), (0, -ha), (-hb, 0)
        poly(ax, [A, B, C, D], alpha=0.22)
        ax.plot([A[0], C[0]], [A[1], C[1]], "k--", lw=0.7)
        ax.plot([B[0], D[0]], [B[1], D[1]], "k--", lw=0.7)
        K = (0, ha - inset)
        M = (0, -ha + inset)
        I = (hb - inset, 0)
        J = (-hb + inset, 0)
        E = (J[0], K[1])
        F = (I[0], K[1])
        H = (I[0], M[1])
        G = (J[0], M[1])
        poly(ax, [E, F, H, G], fill="#F8F8F8", edge=C_EDGE, lw=1.2, alpha=0.85)
        for p, lb, dx, dy in [
            (A, "A", -0.35, 0.1),
            (B, "B", 0.12, -0.3),
            (C, "C", -0.15, -0.4),
            (D, "D", -0.4, 0.05),
            (E, "E", -0.35, 0.1),
            (F, "F", 0.12, 0.1),
            (H, "H", 0.12, -0.35),
            (G, "G", -0.35, -0.35),
            (K, "K", 0.55, 0.05),
            (I, "I", 0.12, -0.1),
            (M, "M", 0.55, -0.35),
            (J, "J", -0.55, 0.05),
        ]:
            mark_pt(ax, p[0], p[1], lb, dx=dx, dy=dy)
        dim_v(ax, 0, -ha, ha, "70", off=1.15)
        dim_h(ax, -hb, hb, 0, "50", off=-1.05)
        seg_label(ax, A[0], A[1], K[0], K[1], "15", frac=0.45, dx=-0.55, dy=0.05, fs=7)
        seg_label(ax, C[0], C[1], M[0], M[1], "15", frac=0.45, dx=0.55, dy=-0.05, fs=7)
        seg_label(ax, B[0], B[1], I[0], I[1], "15", frac=0.45, dx=0.45, dy=-0.05, fs=7)
        seg_label(ax, D[0], D[1], J[0], J[1], "15", frac=0.45, dx=-0.55, dy=-0.05, fs=7)
        plain_text(ax, 0, ha + 2.5, r"$ABCD$ — מעוין", ha="center", fontsize=7)
        plain_text(ax, 0, 0, r"$EHGF$ — מלבן", ha="center", fontsize=7)
        ax.set_xlim(-38, 38)
        ax.set_ylim(-42, 42)
    elif n == 19:
        s, h_tri, r = 12.0, 8.0, 6.0
        poly(ax, [(0, 0), (s, 0), (s, s), (0, s)], alpha=0.12)
        poly(ax, [(0, s), (s, s), (s / 2, s + h_tri)], alpha=0.3)
        circle(ax, (s / 2, s / 2), r, fill="#E8E8E8")
        mark_pt(ax, 0, 0, "A", dx=-0.35, dy=-0.28)
        mark_pt(ax, s, 0, "B", dx=0.1, dy=-0.28)
        mark_pt(ax, s, s, "C", dx=0.1, dy=0.08)
        mark_pt(ax, 0, s, "D", dx=-0.35, dy=0.08)
        mark_pt(ax, s / 2, s + h_tri, "E", dx=-0.05, dy=0.08)
        dim_h(ax, 0, s, 0, "12", off=-0.85)
        dim_v(ax, s / 2, s, s + h_tri, "8", off=0.85)
        ax.text(s / 2, s / 2, r"$r=6$", ha="center", fontsize=8)
        ax.set_xlim(-2, 15)
        ax.set_ylim(-1.5, 22)
    elif n == 20:
        vx, vy = 18 / 41, 80 / 41
        pts = [(0, 0), (8, 0), (8, 4), (5, 4), (vx, vy)]
        poly(ax, pts, alpha=0.3)
        dim_h(ax, 0, 8, 0, "8", off=-0.75)
        dim_v(ax, 8, 0, 4, "4", off=0.75)
        dim_h(ax, 5, 8, 4, "3", off=0.55)
        seg_label(ax, 5, 4, vx, vy, "5", frac=0.5, dx=0.25, dy=0.12, fs=7)
        seg_label(ax, vx, vy, 0, 0, "2", frac=0.5, dx=-0.4, dy=0.0, fs=7)
        ax.set_xlim(-1.5, 10)
        ax.set_ylim(-1.5, 6.5)
    save_fig(fig, stem, n)


def gen_10(stem: str, n: int) -> None:
    fig, ax = fig_axes_plain()

    def _pgram_pts(base, height, slant):
        return [(0, 0), (base, 0), (base + slant, height), (slant, height)]

    def _pgram_labeled(base, height, slant, labels=("A", "B", "C", "D"), alpha=0.28):
        pts = _pgram_pts(base, height, slant)
        poly(ax, pts, alpha=alpha)
        for p, lb, dx, dy in zip(
            pts,
            labels,
            [-0.35, 0.1, 0.1, -0.35],
            [-0.3, -0.3, 0.08, 0.08],
        ):
            mark_pt(ax, p[0], p[1], lb, dx=dx, dy=dy)
        return pts

    def _rhombus_diag(d_ac, d_bd, labels=("A", "B", "C", "D"), alpha=0.28):
        ha, hb = d_ac / 2, d_bd / 2
        pts = [(0, ha), (hb, 0), (0, -ha), (-hb, 0)]
        poly(ax, pts, alpha=alpha)
        ax.plot([0, 0], [-ha, ha], "k--", lw=0.7)
        ax.plot([-hb, hb], [0, 0], "k--", lw=0.7)
        mark_pt(ax, 0, 0, "O", dx=0.12, dy=0.1)
        for p, lb, dx, dy in zip(
            pts,
            labels,
            [-0.15, 0.12, -0.15, -0.35],
            [0.12, -0.28, -0.35, 0.05],
        ):
            mark_pt(ax, p[0], p[1], lb, dx=dx, dy=dy)
        return pts, ha, hb

    def _pgram_angle_arcs(pts, angle_labels):
        """angle_labels: dict vertex index -> (start_deg, end_deg, label)."""
        for idx, (start, end, label) in angle_labels.items():
            x, y = pts[idx]
            angle_arc(ax, x, y, start, end, r=0.75, label=label, label_r=1.05, fs=7)

    if n == 9:
        pts = _pgram_labeled(10, 4, 3)
        _pgram_angle_arcs(
            pts,
            {
                0: (0, 38, r"$(3x+10)°$"),
                1: (142, 180, r"$(5x-10)°$"),
            },
        )
        ax.set_xlim(-2, 15)
        ax.set_ylim(-1.5, 6.5)
    elif n == 10:
        _rhombus_diag(10, 24)
        seg_label(ax, 0, 5, 5, 0, "13", frac=0.5, dx=0.35, dy=0.15)
        dim_v(ax, 0, -5, 5, "10", off=0.75)
        ax.set_xlim(-14.5, 14.5)
        ax.set_ylim(-7, 7.5)
    elif n == 11:
        by = math.sqrt(40)
        pts = [(-9, 0), (3, by), (9, 0), (-3, -by)]
        poly(ax, pts, alpha=0.28)
        for p, lb, dx, dy in zip(
            pts,
            ("A", "B", "C", "D"),
            [-0.35, 0.1, 0.1, -0.35],
            [-0.3, -0.3, 0.08, 0.08],
        ):
            mark_pt(ax, p[0], p[1], lb, dx=dx, dy=dy)
        ax.plot([-9, 9], [0, 0], "k--", lw=0.7)
        ax.plot([3, -3], [by, -by], "k--", lw=0.7)
        mark_pt(ax, 0, 0, "O", dx=0.12, dy=0.1)
        dim_h(ax, -9, 9, 0, "18", off=-0.95)
        seg_label(ax, 3, by, -3, -by, "14", frac=0.5, dx=0.55, dy=0.0, fs=7)
        ax.set_xlim(-12, 12)
        ax.set_ylim(-9, 9)
    elif n == 12:
        pts = _pgram_labeled(9, 4, 2.5)
        _pgram_angle_arcs(
            pts,
            {
                0: (0, 42, r"$(2x+10)°$"),
                2: (180, 222, r"$(4x-30)°$"),
            },
        )
        ax.set_xlim(-2, 13.5)
        ax.set_ylim(-1.5, 6.5)
    elif n == 13:
        _rhombus_diag(30, 16)
        dim_v(ax, 0, -15, 15, "30", off=0.95)
        dim_h(ax, -8, 8, 0, "16", off=-0.85)
        ax.set_xlim(-11, 11)
        ax.set_ylim(-18.5, 18.5)
    elif n == 14:
        _rhombus_diag(8, 6)
        seg_label(ax, 0, 3, 3, 0, "5", frac=0.5, dx=0.3, dy=0.12)
        dim_v(ax, 0, -3, 3, "8", off=0.75)
        ax.set_xlim(-5.5, 5.5)
        ax.set_ylim(-5, 5.5)
    elif n == 15:
        poly(ax, [(0, 0), (9, 0), (9, 6), (0, 6)], alpha=0.18, fill="#E8F4E8")
        plain_text(ax, 4.5, 3, "מקבילית", ha="center", fontsize=8)
        cx = 16
        rh = [(cx, 3), (cx + 6, 0), (cx, -3), (cx - 6, 0)]
        poly(ax, rh, alpha=0.32)
        ax.plot([cx, cx], [-3, 3], "k--", lw=0.7)
        ax.plot([cx - 6, cx + 6], [0, 0], "k--", lw=0.7)
        plain_text(ax, cx, 0, "מעוין", ha="center", fontsize=8)
        ax.set_xlim(-1.5, 24)
        ax.set_ylim(-5, 8)
    elif n == 16:
        pts = _pgram_labeled(10, 4, 3)
        _pgram_angle_arcs(pts, {0: (0, 38, r"$70°$")})
        ax.set_xlim(-2, 15)
        ax.set_ylim(-1.5, 6.5)
    elif n == 17:
        _rhombus_diag(30, 16)
        dim_v(ax, 0, -15, 15, "30", off=0.95)
        dim_h(ax, -8, 8, 0, "16", off=-0.85)
        ax.set_xlim(-11, 11)
        ax.set_ylim(-18.5, 18.5)
    elif n == 18:
        pts = _pgram_labeled(15, 12, 5)
        _pgram_angle_arcs(
            pts,
            {
                0: (0, 67, r"$(2x+10)°$"),
                1: (113, 180, r"$(4x-10)°$"),
            },
        )
        ax.plot([pts[2][0], pts[2][0]], [0, 12], "k--", lw=0.8)
        dim_h(ax, 0, 15, 0, "15", off=-0.85)
        seg_label(ax, pts[1][0], pts[1][1], pts[2][0], pts[2][1], "13", frac=0.45, dx=0.45, dy=0.1)
        dim_v(ax, pts[2][0], 0, 12, r"$h=12$", off=0.85)
        ax.set_xlim(-2.5, 23)
        ax.set_ylim(-1.8, 14.5)
    elif n == 19:
        w, h, eb = 14.62, 6.82, 8.9
        A, B, C, D = (0, h), (w, h), (w, 0), (0, 0)
        E, F = (w - eb, h), (eb, 0)
        poly(ax, [A, B, C, D], alpha=0.12, fill="#F5F5F5")
        poly(ax, [E, B, F, D], alpha=0.38, fill="#D8E8F5")
        for p, lb, dx, dy in [
            (A, "A", -0.35, 0.08),
            (B, "B", 0.1, 0.08),
            (C, "C", 0.1, -0.35),
            (D, "D", -0.35, -0.35),
            (E, "E", -0.35, 0.08),
            (F, "F", 0.1, -0.35),
        ]:
            mark_pt(ax, p[0], p[1], lb, dx=dx, dy=dy)
        dim_h(ax, 0, w, h, r"$AB$", off=0.65)
        dim_v(ax, w, 0, h, r"$AD$", off=0.85)
        seg_label(ax, E[0], E[1], B[0], B[1], "8.9", frac=0.5, dx=0, dy=0.2)
        angle_arc(ax, F[0], F[1], 50, 180, r=1.0, label=r"$130°$", label_r=1.45, fs=7)
        right_angle(ax, 0, h, 0.35, quadrant=4)
        right_angle(ax, w, h, 0.35, quadrant=3)
        right_angle(ax, w, 0, 0.35, quadrant=2)
        right_angle(ax, 0, 0, 0.35, quadrant=1)
        ax.set_xlim(-2, w + 3)
        ax.set_ylim(-2, h + 2)
    elif n == 20:
        _rhombus_diag(16, 12)
        seg_label(ax, 0, 8, 6, 0, "10", frac=0.5, dx=0.35, dy=0.12)
        dim_h(ax, -6, 6, 0, "12", off=-0.75)
        ax.set_xlim(-9, 9)
        ax.set_ylim(-11, 11)
    else:
        poly(ax, [(0, 0), (6, 0), (7, 3), (1, 3)], alpha=0.22)
        ax.set_xlim(-2, 9)
        ax.set_ylim(-1, 5)

    save_fig(fig, stem, n)


def gen_11(stem: str, n: int) -> None:
    fig, ax = fig_axes_plain()

    def _pgram_pts(base, height, slant):
        return [(0, 0), (base, 0), (base + slant, height), (slant, height)]

    def _pgram_labeled(base, height, slant, labels=("A", "B", "C", "D"), alpha=0.28):
        pts = _pgram_pts(base, height, slant)
        poly(ax, pts, alpha=alpha)
        for p, lb, dx, dy in zip(
            pts,
            labels,
            [-0.35, 0.1, 0.1, -0.35],
            [-0.3, -0.3, 0.08, 0.08],
        ):
            mark_pt(ax, p[0], p[1], lb, dx=dx, dy=dy)
        return pts

    def _rhombus_diag(d_ac, d_bd, labels=("A", "B", "C", "D"), alpha=0.28):
        ha, hb = d_ac / 2, d_bd / 2
        pts = [(0, ha), (hb, 0), (0, -ha), (-hb, 0)]
        poly(ax, pts, alpha=alpha)
        ax.plot([0, 0], [-ha, ha], "k--", lw=0.7)
        ax.plot([-hb, hb], [0, 0], "k--", lw=0.7)
        for p, lb, dx, dy in zip(
            pts,
            labels,
            [-0.15, 0.12, -0.15, -0.35],
            [0.12, -0.28, -0.35, 0.05],
        ):
            mark_pt(ax, p[0], p[1], lb, dx=dx, dy=dy)
        return pts, ha, hb

    if n == 9:
        _rhombus_diag(8, 12)
        dim_v(ax, 0, -4, 4, "8", off=0.75)
        plain_text(ax, 0, -6.2, 'שטח $=48$ ס"מ$^2$', ha="center", fontsize=7)
        ax.set_xlim(-8.5, 8.5)
        ax.set_ylim(-7.5, 6.5)
    elif n == 10:
        _pgram_labeled(8, 5, 2)
        dim_h(ax, 0, 8, 0, r"$x+3$", off=-0.75)
        dim_v(ax, 10, 0, 5, r"$x$", off=0.75)
        plain_text(ax, 5, 2.5, 'שטח $=40$ ס"מ$^2$', ha="center", fontsize=7)
        ax.set_xlim(-2, 12.5)
        ax.set_ylim(-1.5, 7)
    elif n == 11:
        _rhombus_diag(10, 24)
        seg_label(ax, 0, 5, 5, 0, "13", frac=0.5, dx=0.35, dy=0.15)
        dim_v(ax, 0, -5, 5, "10", off=0.75)
        ax.set_xlim(-14.5, 14.5)
        ax.set_ylim(-7, 7.5)
    elif n == 12:
        poly(ax, [(0, 0), (10, 0), (10, 6), (0, 6)], alpha=0.18, fill="#E8F4E8")
        poly(ax, [(12, 0), (22, 0), (24, 6), (14, 6)], alpha=0.32)
        dim_h(ax, 0, 10, 0, "10", off=-0.65)
        dim_h(ax, 12, 22, 0, "10", off=-0.65)
        dim_v(ax, 10, 0, 6, "6", off=0.7)
        dim_v(ax, 24, 0, 6, "6", off=0.7)
        plain_text(ax, 5, 3, "מלבן", ha="center", fontsize=8)
        plain_text(ax, 18, 3, "מקבילית", ha="center", fontsize=8)
        ax.set_xlim(-1.5, 26.5)
        ax.set_ylim(-1.5, 8)
    elif n == 13:
        _rhombus_diag(10, 16)
        dim_v(ax, 0, -5, 5, r"$x$", off=0.75)
        dim_h(ax, -8, 8, 0, r"$x+6$", off=-0.75)
        plain_text(ax, 0, -7.2, 'שטח $=80$ ס"מ$^2$', ha="center", fontsize=7)
        ax.set_xlim(-10.5, 10.5)
        ax.set_ylim(-8.5, 7.5)
    elif n == 14:
        _rhombus_diag(8, 6)
        seg_label(ax, 0, 3, 3, 0, "5", frac=0.5, dx=0.3, dy=0.12)
        dim_v(ax, 0, -3, 3, "8", off=0.75)
        ax.set_xlim(-5.5, 5.5)
        ax.set_ylim(-5, 5.5)
    elif n == 15:
        pts = _pgram_labeled(15, 12, 5)
        ax.plot([pts[2][0], pts[2][0]], [0, 12], "k--", lw=0.8)
        dim_h(ax, 0, 15, 0, "15", off=-0.85)
        seg_label(ax, pts[1][0], pts[1][1], pts[2][0], pts[2][1], "13", frac=0.45, dx=0.45, dy=0.1)
        dim_v(ax, pts[2][0], 0, 12, r"$h=12$", off=0.85)
        ax.set_xlim(-2.5, 23)
        ax.set_ylim(-1.8, 14.5)
    elif n == 16:
        poly(ax, [(0, 0), (9, 0), (9, 6), (0, 6)], alpha=0.18, fill="#E8F4E8")
        dim_h(ax, 0, 9, 0, "9", off=-0.65)
        dim_v(ax, 9, 0, 6, "6", off=0.7)
        plain_text(ax, 4.5, 3, "מקבילית", ha="center", fontsize=8)
        cx = 16
        rh = [(cx, 3), (cx + 6, 0), (cx, -3), (cx - 6, 0)]
        poly(ax, rh, alpha=0.32)
        ax.plot([cx, cx], [-3, 3], "k--", lw=0.7)
        ax.plot([cx - 6, cx + 6], [0, 0], "k--", lw=0.7)
        dim_v(ax, cx, -3, 3, r"$d_2$", off=0.75)
        dim_h(ax, cx - 6, cx + 6, 0, r"$2d_2$", off=-0.75)
        plain_text(ax, cx, 4.2, r"$d_1=2d_2$", ha="center", fontsize=7)
        plain_text(ax, cx, -4.5, r"$\frac{2}{3}$ שטח", ha="center", fontsize=7)
        ax.set_xlim(-1.5, 24)
        ax.set_ylim(-6, 8)
    elif n == 17:
        _rhombus_diag(30, 16)
        dim_v(ax, 0, -15, 15, "30", off=0.95)
        dim_h(ax, -8, 8, 0, "16", off=-0.85)
        ax.set_xlim(-11, 11)
        ax.set_ylim(-18.5, 18.5)
    elif n == 18:
        pts = _pgram_labeled(14, 9, 12)
        foot_x = pts[1][0] + 12
        ax.plot([foot_x, foot_x], [0, 9], "k--", lw=0.8)
        mark_pt(ax, foot_x, 0, "H", dx=0.1, dy=-0.35)
        dim_h(ax, 0, 14, 0, "14", off=-0.85)
        dim_v(ax, pts[2][0], 0, 9, r"$h=9$", off=0.9)
        seg_label(ax, pts[1][0], pts[1][1], pts[2][0], pts[2][1], "15", frac=0.45, dx=0.5, dy=0.1)
        dim_h(ax, pts[1][0], foot_x, 0, "12", off=-1.35, fs=7)
        plain_text(ax, (pts[1][0] + foot_x) / 2, -1.85, r"מ-$B$ ל-$H$", ha="center", fontsize=7)
        ax.set_xlim(-2.5, 28)
        ax.set_ylim(-2.5, 11.5)
    elif n == 19:
        w, h, eb = 14.62, 6.82, 8.9
        A, B, C, D = (0, h), (w, h), (w, 0), (0, 0)
        E, F = (w - eb, h), (eb, 0)
        poly(ax, [A, B, C, D], alpha=0.12, fill="#F5F5F5")
        poly(ax, [E, B, F, D], alpha=0.38, fill="#D8E8F5")
        for p, lb, dx, dy in [
            (A, "A", -0.35, 0.08),
            (B, "B", 0.1, 0.08),
            (C, "C", 0.1, -0.35),
            (D, "D", -0.35, -0.35),
            (E, "E", -0.35, 0.08),
            (F, "F", 0.1, -0.35),
        ]:
            mark_pt(ax, p[0], p[1], lb, dx=dx, dy=dy)
        dim_h(ax, 0, w, h, r"$AB$", off=0.65)
        dim_v(ax, w, 0, h, r"$AD$", off=0.85)
        seg_label(ax, E[0], E[1], B[0], B[1], "8.9", frac=0.5, dx=0, dy=0.2)
        angle_arc(ax, F[0], F[1], 50, 180, r=1.0, label=r"$130°$", label_r=1.45, fs=7)
        right_angle(ax, 0, h, 0.35, quadrant=4)
        right_angle(ax, w, h, 0.35, quadrant=3)
        right_angle(ax, w, 0, 0.35, quadrant=2)
        right_angle(ax, 0, 0, 0.35, quadrant=1)
        ax.set_xlim(-2, w + 3)
        ax.set_ylim(-2, h + 2)
    elif n == 20:
        ha, hb, inset = 35, 25, 15
        A, B, C, D = (0, ha), (hb, 0), (0, -ha), (-hb, 0)
        poly(ax, [A, B, C, D], alpha=0.22)
        ax.plot([A[0], C[0]], [A[1], C[1]], "k--", lw=0.7)
        ax.plot([B[0], D[0]], [B[1], D[1]], "k--", lw=0.7)
        K = (0, ha - inset)
        M = (0, -ha + inset)
        I = (hb - inset, 0)
        J = (-hb + inset, 0)
        E = (J[0], K[1])
        F = (I[0], K[1])
        H = (I[0], M[1])
        G = (J[0], M[1])
        poly(ax, [E, F, H, G], fill="#F8F8F8", edge=C_EDGE, lw=1.2, alpha=0.85)
        for p, lb, dx, dy in [
            (A, "A", -0.35, 0.1),
            (B, "B", 0.12, -0.3),
            (C, "C", -0.15, -0.4),
            (D, "D", -0.4, 0.05),
            (E, "E", -0.35, 0.1),
            (F, "F", 0.12, 0.1),
            (H, "H", 0.12, -0.35),
            (G, "G", -0.35, -0.35),
            (K, "K", 0.55, 0.05),
            (I, "I", 0.12, -0.1),
            (M, "M", 0.55, -0.35),
            (J, "J", -0.55, 0.05),
        ]:
            mark_pt(ax, p[0], p[1], lb, dx=dx, dy=dy)
        dim_v(ax, 0, -ha, ha, "70", off=1.15)
        dim_h(ax, -hb, hb, 0, "50", off=-1.05)
        seg_label(ax, A[0], A[1], K[0], K[1], "15", frac=0.45, dx=-0.55, dy=0.05, fs=7)
        seg_label(ax, C[0], C[1], M[0], M[1], "15", frac=0.45, dx=0.55, dy=-0.05, fs=7)
        seg_label(ax, B[0], B[1], I[0], I[1], "15", frac=0.45, dx=0.45, dy=-0.05, fs=7)
        seg_label(ax, D[0], D[1], J[0], J[1], "15", frac=0.45, dx=-0.55, dy=0.05, fs=7)
        plain_text(ax, 0, ha + 2.5, r"$ABCD$ — מעוין", ha="center", fontsize=7)
        plain_text(ax, 0, 0, r"$EHGF$ — מלבן", ha="center", fontsize=7)
        ax.set_xlim(-38, 38)
        ax.set_ylim(-42, 42)
    else:
        poly(ax, [(0, 0), (6, 0), (7, 3), (1, 3)], alpha=0.22)
        ax.set_xlim(-2, 9)
        ax.set_ylim(-1, 5)

    save_fig(fig, stem, n)


def _draw_kite_ac(
    ax,
    ac: float,
    ab: float,
    cb: float,
    *,
    show_diag_bd: bool = True,
    mark_o: bool = True,
    alpha: float = 0.28,
) -> tuple[float, float, float, float]:
    """Convex kite: AB=AD=ab, CB=CD=cb, diagonal AC=ac (vertical). Returns (half_w, h_top, h_bot, bo)."""
    c_len = (cb * cb - ab * ab + ac * ac) / (2 * ac)
    a_len = ac - c_len
    half_w = math.sqrt(max(ab * ab - a_len * a_len, 0.01))
    bo = half_w
    pts = [(0, a_len), (half_w, 0), (0, -c_len), (-half_w, 0)]
    poly(ax, pts, alpha=alpha)
    if show_diag_bd:
        ax.plot([-half_w, half_w], [0, 0], "k--", lw=0.75)
    ax.plot([0, 0], [a_len, -c_len], "k--", lw=0.75)
    if mark_o:
        mark_pt(ax, 0, 0, "O", dx=0.12, dy=0.1)
    for p, lb, dx, dy in zip(
        pts,
        ("A", "B", "C", "D"),
        [-0.15, 0.12, -0.15, -0.35],
        [0.12, -0.28, -0.35, 0.05],
    ):
        mark_pt(ax, p[0], p[1], lb, dx=dx, dy=dy)
    return half_w, a_len, c_len, bo


def _draw_gen_trap_ab_dc(
    ax,
    ab: float,
    ad: float,
    bc: float,
    angle_bcd_deg: float,
    *,
    labels: dict[str, str] | None = None,
    alpha: float = 0.28,
) -> tuple[float, float, float]:
    """General trapezoid AB || DC; returns (h, de, dc)."""
    ang = math.radians(angle_bcd_deg)
    h = bc * math.sin(ang)
    de = math.sqrt(max(ad * ad - h * h, 0.01))
    fc = bc * math.cos(ang)
    dc = de + ab + fc
    sc = 1.0
    if dc > 28:
        sc = 24.0 / dc
    D = (0.0, 0.0)
    C_ = (dc * sc, 0.0)
    A = (de * sc, h * sc)
    B = ((de + ab) * sc, h * sc)
    E = (de * sc, 0.0)
    F = ((de + ab) * sc, 0.0)
    poly(ax, [A, B, C_, D], alpha=alpha)
    ax.plot([A[0], E[0]], [A[1], E[1]], "k--", lw=0.75)
    ax.plot([B[0], F[0]], [B[1], F[1]], "k--", lw=0.75)
    right_angle(ax, E[0], E[1], 0.35 * sc, quadrant=2)
    right_angle(ax, F[0], F[1], 0.35 * sc, quadrant=3)
    for p, lb, dx, dy in [
        (A, "A", -0.35, 0.1),
        (B, "B", 0.12, 0.1),
        (C_, "C", 0.12, -0.35),
        (D, "D", -0.35, -0.35),
        (E, "E", -0.35, -0.35),
        (F, "F", 0.12, -0.35),
    ]:
        mark_pt(ax, p[0], p[1], lb, dx=dx, dy=dy)
    angle_arc(
        ax,
        C_[0],
        C_[1],
        180 - angle_bcd_deg,
        180,
        r=0.55 * sc,
        label=rf"${angle_bcd_deg}°$",
        label_r=0.95 * sc,
        fs=7,
    )
    if labels:
        if "ab" in labels:
            dim_h(ax, A[0], B[0], A[1], labels["ab"], off=0.65)
        if "ad" in labels:
            seg_label(ax, D[0], D[1], A[0], A[1], labels["ad"], frac=0.45, dx=-0.55, dy=0.0)
        if "bc" in labels:
            seg_label(ax, B[0], B[1], C_[0], C_[1], labels["bc"], frac=0.45, dx=0.45, dy=0.0)
    return h, de, dc


def gen_12(stem: str, n: int) -> None:
    fig, ax = fig_axes_plain()

    if n == 9:
        _draw_iso_trap(ax, 20, 8, 8, labels={"bottom": "20", "top": "8", "leg": "10"})
        ax.set_xlim(-2.5, 23)
        ax.set_ylim(-2, 11)
    elif n == 10:
        # טרפז כללי AB||CD: AB בסיס תחתון, ∠A=80°, ∠B=60° (זוויות בסיס חדות)
        h = 4.0
        A, B = (0, 0), (10, 0)
        D = (h / math.tan(math.radians(80)), h)
        C = (10 - h / math.tan(math.radians(60)), h)
        poly(ax, [A, B, C, D], alpha=0.28)
        for p, lb, dx, dy in zip(
            [A, B, C, D],
            ("A", "B", "C", "D"),
            [-0.4, 0.15, 0.15, -0.45],
            [-0.45, -0.45, 0.12, 0.12],
        ):
            mark_pt(ax, p[0], p[1], lb, dx=dx, dy=dy)
        angle_arc(ax, A[0], A[1], 0, 80, r=0.9, label=r"$80°$", label_r=1.45, fs=7)
        angle_arc(ax, B[0], B[1], 120, 180, r=0.9, label=r"$60°$", label_r=1.45, fs=7)
        dim_h(ax, A[0], B[0], 0, r"$AB$", off=-0.6)
        ax.set_xlim(-2, 12)
        ax.set_ylim(-1.5, 6)
    elif n == 11:
        b_big, b_small = 48.0, 12.0
        h = 18.0 * math.tan(math.radians(40))
        off = _draw_iso_trap(
            ax,
            b_big,
            b_small,
            h,
            labels={"bottom": "48", "top": "12"},
            vertices={"A": 3, "B": 0, "C": 1, "D": 2},
        )
        ax.plot([off, off], [0, h], "k--", lw=0.75)
        ax.plot([b_big - off, b_big - off], [0, h], "k--", lw=0.75)
        mark_pt(ax, off, 0, "G", dx=-0.1, dy=-0.35)
        mark_pt(ax, b_big - off, 0, "H", dx=0.1, dy=-0.35)
        right_angle(ax, off, 0, 0.45, quadrant=2)
        right_angle(ax, b_big - off, 0, 0.45, quadrant=3)
        angle_arc(ax, b_big, 0, 140, 180, r=0.75, label=r"$40°$", label_r=1.05, fs=7)
        ax.set_xlim(-3, 52)
        ax.set_ylim(-2, h + 2.5)
    elif n == 12:
        half_w, a_len, c_len, _ = _draw_kite_ac(ax, 8, 5, 7)
        dim_v(ax, 0, -c_len, a_len, "8", off=0.85)
        seg_label(ax, 0, a_len, half_w, 0, "5", frac=0.45, dx=-0.45, dy=0.0)
        seg_label(ax, half_w, 0, 0, -c_len, "7", frac=0.45, dx=0.45, dy=0.0)
        ax.set_xlim(-half_w - 2.5, half_w + 2.5)
        ax.set_ylim(-c_len - 2, a_len + 2)
    elif n == 13:
        # דלתון: אלכסון ארוך 10 (אופקי), אלכסון קצר 6 (אנכי), אלכסונים מאונכים
        half_l, half_s = 5.0, 3.0
        pts = [(0, half_s), (half_l, 0), (0, -half_s), (-half_l, 0)]
        poly(ax, pts, alpha=0.28)
        ax.plot([-half_l, half_l], [0, 0], "k--", lw=0.75)
        ax.plot([0, 0], [half_s, -half_s], "k--", lw=0.75)
        dim_h(ax, -half_l, half_l, 0, "10", off=-0.75)
        dim_v(ax, 0, -half_s, half_s, "6", off=0.85)
        right_angle(ax, 0, 0, 0.45, quadrant=1)
        ax.set_xlim(-7, 7)
        ax.set_ylim(-5, 5)
    elif n == 14:
        # טרפז שווה-שוקיים סימבולי: בסיס גדול b1, בסיס קטן b2, שוק c
        b_big, b_small, h = 20.0, 8.0, 8.0
        _draw_iso_trap(
            ax,
            b_big,
            b_small,
            h,
            labels={"bottom": r"$b_1$", "top": r"$b_2$", "leg": r"$c$"},
        )
        ax.set_xlim(-2.5, 23)
        ax.set_ylim(-2, 11)
    elif n == 15:
        # טרפז שווה-שוקיים עם שני האלכסונים AC ו-BD (הוכחה ששווים)
        h, off = 6.0, 4.0
        _draw_iso_trap(ax, 16, 8, h, vertices={"A": 3, "B": 2, "C": 1, "D": 0}, alpha=0.22)
        ax.plot([off, 16], [h, 0], "k--", lw=0.8)        # AC
        ax.plot([16 - off, 0], [h, 0], "k--", lw=0.8)    # BD
        plain_text(ax, 8, 3.4, r"$AC=BD$", ha="center", fontsize=8, color="#444444",
                   bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
        ax.set_xlim(-2.5, 19)
        ax.set_ylim(-2, 9)
    elif n == 16:
        # טרפז שווה-שוקיים: AB=11.8 (עליון), CD=20.4 (תחתון), שוק 12.57, משולש ACD
        h, off = math.sqrt(12.57**2 - 4.3**2), 4.3
        _draw_iso_trap(
            ax,
            20.4,
            11.8,
            h,
            labels={"bottom": "20.4", "top": "11.8", "leg": "12.57"},
            vertices={"A": 3, "B": 2, "C": 1, "D": 0},
        )
        poly(ax, [(off, h), (20.4, 0), (0, 0)], fill=C_GRAY, alpha=0.32)
        ax.plot([off, 20.4], [h, 0], "k--", lw=0.8)      # AC
        plain_text(ax, 9.5, h / 2 - 0.8, r"$\triangle ACD$", ha="center", fontsize=8, color="#333333")
        ax.set_xlim(-2.5, 23.5)
        ax.set_ylim(-2, h + 2.5)
    elif n == 17:
        # טרפז שווה-שוקיים: AB=26 (בסיס גדול, תחתון), CD=10 (קטן, עליון), שוק 13
        h = math.sqrt(13**2 - 8**2)
        _draw_iso_trap(
            ax,
            26,
            10,
            h,
            labels={"bottom": "26", "top": "10", "leg": "13"},
            vertices={"A": 0, "B": 1, "C": 2, "D": 3},
        )
        ax.set_xlim(-2.5, 29)
        ax.set_ylim(-2, h + 2.5)
    else:
        poly(ax, [(0, 0), (8, 0), (6, 3), (2, 3)], alpha=0.28)
        ax.set_xlim(-1, 10)
        ax.set_ylim(-1, 5)

    save_fig(fig, stem, n)


def gen_13(stem: str, n: int) -> None:
    fig, ax = fig_axes_plain()
    if n == 13:
        # ריבוע 10×10 עם מעגל חסום
        s = 10.0
        poly(ax, [(0, 0), (s, 0), (s, s), (0, s)], alpha=0.12)
        circle(ax, (s / 2, s / 2), s / 2, fill="#DDDDDD")
        mark_pt(ax, 0, 0, "A", dx=-0.35, dy=-0.35)
        mark_pt(ax, s, 0, "B", dx=0.12, dy=-0.35)
        mark_pt(ax, s, s, "C", dx=0.12, dy=0.08)
        mark_pt(ax, 0, s, "D", dx=-0.35, dy=0.08)
        dim_h(ax, 0, s, 0, "10", off=-0.85)
        dim_v(ax, s, 0, s, "10", off=0.85)
        ax.set_xlim(-2, 13)
        ax.set_ylim(-2, 13)
    elif n == 14:
        # מיתר AB = רדיוס → משולש שווה-צלעות OAB
        r = 3.5
        Ox, Oy = 0.0, 0.0
        circle(ax, (Ox, Oy), r, fill="#E8F4FF")
        ax.plot([Ox, r], [Oy, Oy], "k-", lw=1.2)
        ax.plot([Ox, r / 2], [Oy, r * math.sqrt(3) / 2], "k-", lw=1.2)
        ax.plot([r, r / 2], [Oy, r * math.sqrt(3) / 2], "k-", lw=1.2)
        mark_pt(ax, Ox, Oy, "O", dx=-0.35, dy=-0.35)
        mark_pt(ax, r, Oy, "A", dx=0.12, dy=-0.35)
        mark_pt(ax, r / 2, r * math.sqrt(3) / 2, "B", dx=-0.05, dy=0.1)
        seg_label(ax, Ox, Oy, r, Oy, r"$r$", frac=0.55, dy=0.22)
        seg_label(ax, Ox, Oy, r / 2, r * math.sqrt(3) / 2, r"$r$", frac=0.55, dx=-0.3, dy=0.0)
        seg_label(ax, r, Oy, r / 2, r * math.sqrt(3) / 2, r"$r$", frac=0.5, dx=0.3, dy=0.0)
        ax.set_xlim(-2.5, 5)
        ax.set_ylim(-2.5, 5)
    elif n == 15:
        # שלושה מעגלים קונצנטריים: רדיוסים 3, 6, 9
        for rad, alpha in [(9, 0.08), (6, 0.14), (3, 0.22)]:
            circle(ax, (0, 0), rad, fill="#E8F4FF", ec=C_EDGE, lw=1.2)
        mark_pt(ax, 0, 0, "O", dx=-0.35, dy=-0.35)
        dim_h(ax, 0, 3, 0, "3", off=-0.75)
        dim_h(ax, 0, 6, 0, "6", off=-1.35)
        dim_h(ax, 0, 9, 0, "9", off=-1.95)
        ax.set_xlim(-11, 11)
        ax.set_ylim(-11, 11)
    elif n == 16:
        # תרגיל 17 במרקדאון: מעגלים קונצנטריים 30 ו-20
        R, r = 3.0, 2.0
        circle(ax, (0, 0), R, fill="#E8F4FF", ec=C_EDGE)
        circle(ax, (0, 0), r, fill="white", ec=C_EDGE)
        mark_pt(ax, 0, 0, "O", dx=-0.35, dy=-0.35)
        dim_h(ax, 0, R, 0, "30", off=-0.75)
        dim_h(ax, 0, r, 0, "20", off=0.65)
        plain_text(ax, 0, 0.5, "רצועה", ha="center", fontsize=8, color="#444444")
        ax.set_xlim(-4, 4)
        ax.set_ylim(-4, 4)
    elif n == 17:
        # תרגיל 18 במרקדאון: r=5, P על המעגל, Q על קוטר OQ=2
        r = 5.0
        circle(ax, (0, 0), r, fill="#E8F4FF")
        ax.plot([-r, r], [0, 0], "k--", lw=0.8)
        mark_pt(ax, 0, 0, "O", dx=-0.35, dy=-0.35)
        mark_pt(ax, r, 0, "P", dx=0.12, dy=-0.35)
        mark_pt(ax, 2, 0, "Q", dx=-0.05, dy=0.12)
        dim_h(ax, 0, r, 0, "5", off=-0.75)
        dim_h(ax, 0, 2, 0, "2", off=0.55)
        ax.set_xlim(-7, 7)
        ax.set_ylim(-7, 7)
    elif n == 18:
        # תרגיל 19 במרקדאון: r=8, OM=3, מיתר AB דרך M
        r, d = 8.0, 3.0
        half = math.sqrt(r * r - d * d)
        circle(ax, (0, 0), r, fill="#E8F4FF")
        ax.plot([d, d], [-half, half], "k-", lw=1.4)
        ax.plot([0, d], [0, 0], "k--", lw=0.8)
        mark_pt(ax, 0, 0, "O", dx=-0.35, dy=-0.35)
        mark_pt(ax, d, 0, "M", dx=0.12, dy=-0.35)
        mark_pt(ax, d, half, "A", dx=0.12, dy=0.05)
        mark_pt(ax, d, -half, "B", dx=0.12, dy=-0.35)
        dim_h(ax, 0, r, 0, "8", off=-0.85)
        dim_h(ax, 0, d, 0, "3", off=0.55)
        ax.set_xlim(-10, 10)
        ax.set_ylim(-10, 10)
    elif n == 19:
        # תרגיל 20 במרקדאון: ריבוע צלע 2r, מעגל חסום רדיוס r
        r = 5.0
        s = 2 * r
        poly(ax, [(0, 0), (s, 0), (s, s), (0, s)], alpha=0.12)
        circle(ax, (r, r), r, fill="#DDDDDD")
        mark_pt(ax, 0, 0, "A", dx=-0.35, dy=-0.35)
        mark_pt(ax, s, 0, "B", dx=0.12, dy=-0.35)
        mark_pt(ax, s, s, "C", dx=0.12, dy=0.08)
        mark_pt(ax, 0, s, "D", dx=-0.35, dy=0.08)
        dim_h(ax, 0, s, 0, r"$2r$", off=-0.85)
        seg_label(ax, r, r, s, r, r"$r$", frac=0.5, dy=0.22)
        ax.set_xlim(-2, 13)
        ax.set_ylim(-2, 13)
    elif n == 20:
        # תרגיל 20ד: r=7 — שטחים מספריים
        r = 7.0
        s = 2 * r
        poly(ax, [(0, 0), (s, 0), (s, s), (0, s)], alpha=0.12)
        circle(ax, (r, r), r, fill="#DDDDDD")
        mark_pt(ax, 0, 0, "A", dx=-0.35, dy=-0.35)
        mark_pt(ax, s, 0, "B", dx=0.12, dy=-0.35)
        mark_pt(ax, s, s, "C", dx=0.12, dy=0.08)
        mark_pt(ax, 0, s, "D", dx=-0.35, dy=0.08)
        dim_h(ax, 0, s, 0, "14", off=-0.85)
        seg_label(ax, r, r, s, r, "7", frac=0.5, dy=0.22)
        plain_text(ax, r, r, "מעגל", ha="center", fontsize=8, color="#333333")
        ax.set_xlim(-2, 17)
        ax.set_ylim(-2, 17)
    else:
        circle(ax, (0, 0), 3, fill="#E8F4FF", ec=C_EDGE)
        ax.plot([0], [0], "ko", ms=4)
        ax.set_xlim(-4, 4)
        ax.set_ylim(-4, 4)
    save_fig(fig, stem, n)


def _iso_trap_pts(b_big: float, b_small: float, h: float) -> tuple[list[tuple[float, float]], float]:
    """Isosceles trapezoid: large base on y=0, small base at y=h."""
    off = (b_big - b_small) / 2
    return [(0, 0), (b_big, 0), (b_big - off, h), (off, h)], off


def _draw_iso_trap(
    ax,
    b_big: float,
    b_small: float,
    h: float,
    *,
    labels: dict[str, str] | None = None,
    vertices: dict[str, int] | None = None,
    alpha: float = 0.28,
) -> float:
    pts, off = _iso_trap_pts(b_big, b_small, h)
    poly(ax, pts, alpha=alpha)
    if labels:
        if "bottom" in labels:
            dim_h(ax, 0, b_big, 0, labels["bottom"], off=-0.85)
        if "top" in labels:
            dim_h(ax, off, b_big - off, h, labels["top"], off=0.65)
        if "height" in labels:
            dim_v(ax, b_big, 0, h, labels["height"], off=0.9)
        if "leg" in labels:
            seg_label(ax, 0, 0, off, h, labels["leg"], frac=0.45, dx=-0.55, dy=0.0)
    if vertices:
        names = ["A", "B", "C", "D"]
        offsets = [(-0.35, -0.35), (0.12, -0.35), (0.12, 0.1), (-0.35, 0.1)]
        for name, idx in vertices.items():
            x, y = pts[idx]
            dx, dy = offsets[idx]
            mark_pt(ax, x, y, name, dx=dx, dy=dy)
    ax.plot([off, off], [0, h], "k--", lw=0.6, alpha=0.45)
    return off


def gen_14(stem: str, n: int) -> None:
    fig, ax = fig_axes_plain()
    if n == 9:
        _draw_iso_trap(
            ax,
            20,
            8,
            8,
            labels={"bottom": "20", "top": "8", "leg": "10"},
        )
        ax.set_xlim(-2.5, 23)
        ax.set_ylim(-2, 11)
    elif n == 10:
        r = 10.0
        circle(ax, (0, 0), r, fill="#E8F4FF")
        seg_label(ax, 0, 0, r, 0, r"$C=20\pi$", frac=0.55, dy=0.3, fs=8)
        ax.set_xlim(-13, 13)
        ax.set_ylim(-13, 13)
    elif n == 11:
        r = 8.0
        circle(ax, (0, 0), r, fill="#E8F4FF")
        dim_h(ax, 0, r, 0, "8", off=-0.75)
        plain_text(ax, 0, 0, r"$S=64\pi$", ha="center", fontsize=8, color="#333333")
        ax.set_xlim(-11, 11)
        ax.set_ylim(-11, 11)
    elif n == 12:
        _draw_iso_trap(
            ax,
            12,
            8,
            6,
            labels={"top": "8", "height": "6"},
        )
        plain_text(ax, 6, 3, r"$S=60$", ha="center", fontsize=8, color="#444444")
        ax.set_xlim(-2.5, 15)
        ax.set_ylim(-2, 9)
    elif n == 13:
        _draw_iso_trap(
            ax,
            16,
            8,
            4,
            labels={"bottom": r"$3x-2$", "top": r"$x+2$", "height": "4"},
        )
        plain_text(ax, 8, 2, r"$S=48$", ha="center", fontsize=8, color="#444444")
        ax.set_xlim(-2.5, 19)
        ax.set_ylim(-2, 7)
    elif n == 14:
        s = 10.0
        poly(ax, [(0, 0), (s, 0), (s, s), (0, s)], alpha=0.12)
        circle(ax, (s / 2, s / 2), s / 2, fill="#DDDDDD")
        dim_h(ax, 0, s, 0, "10", off=-0.85)
        dim_v(ax, s, 0, s, "10", off=0.85)
        seg_label(ax, s / 2, s / 2, s, s / 2, "5", frac=0.5, dy=0.22)
        ax.set_xlim(-2, 13)
        ax.set_ylim(-2, 13)
    elif n == 15:
        w, h_rect, r = 12.0, 5.0, 6.0
        poly(ax, [(0, 0), (w, 0), (w, h_rect), (0, h_rect)], alpha=0.12)
        theta = np.linspace(0, np.pi, 80)
        ax.fill(
            np.append(w / 2 + r * np.cos(theta), [0, w]),
            np.append(h_rect + r * np.sin(theta), [h_rect, h_rect]),
            color="#DDDDDD",
            edgecolor=C_EDGE,
            lw=1.2,
        )
        dim_h(ax, 0, w, 0, "12", off=-0.85)
        dim_v(ax, w, 0, h_rect, "5", off=0.85)
        seg_label(ax, w / 2, h_rect, w / 2 + r, h_rect, "6", frac=0.5, dy=0.25)
        ax.set_xlim(-2, 15)
        ax.set_ylim(-2, 13)
    elif n == 16:
        for cx, rad, lbl in [(0, 3, r"$r$"), (8, 6, r"$2r$")]:
            circle(ax, (cx, 0), rad, fill="#E8F4FF")
            dim_h(ax, cx, cx + rad, 0, lbl, off=-0.75)
        plain_text(ax, 4, 4.5, "הכפלת רדיוס פי 2", ha="center", fontsize=8)
        ax.set_xlim(-5, 16)
        ax.set_ylim(-5, 8)
    elif n == 17:
        R, r = 30.0, 20.0
        scale = 0.1
        Rs, rs = R * scale, r * scale
        circle(ax, (0, 0), Rs, fill="#C8C8C8", ec=C_EDGE)
        circle(ax, (0, 0), rs, fill="white", ec=C_EDGE)
        mark_pt(ax, 0, 0, "O", dx=-0.35, dy=-0.35)
        dim_h(ax, 0, Rs, 0, "30", off=-0.75)
        dim_h(ax, 0, rs, 0, "20", off=0.65)
        plain_text(ax, 0, 0.35, "אפור", ha="center", fontsize=8, color="#444444")
        ax.set_xlim(-4.5, 4.5)
        ax.set_ylim(-4.5, 4.5)
    elif n == 18:
        _draw_iso_trap(
            ax,
            20,
            8,
            8,
            labels={"bottom": "20", "top": "8", "leg": "10"},
            vertices={"A": 0, "B": 1, "C": 2, "D": 3},
        )
        ax.set_xlim(-2.5, 23)
        ax.set_ylim(-2, 11)
    elif n == 19:
        w, h_field, r_pool = 20.0, 10.0, 3.0
        poly(ax, [(0, 0), (w, 0), (w, h_field), (0, h_field)], alpha=0.1)
        circle(ax, (w / 2, h_field / 2), r_pool, fill="#E8E8E8")
        dim_h(ax, 0, w, 0, "20 מ'", off=-0.9)
        dim_v(ax, w, 0, h_field, "10 מ'", off=0.9)
        dim_h(ax, w / 2, w / 2 + r_pool, h_field / 2, "3 מ'", off=0.65, fs=7)
        plain_text(ax, w / 2, h_field / 2, "בריכה", ha="center", fontsize=8, color="#555555")
        ax.set_xlim(-3, 24)
        ax.set_ylim(-2, 14)
    elif n == 20:
        b_big, b_small, leg = 26.0, 10.0, 13.0
        off = (b_big - b_small) / 2
        h = math.sqrt(leg * leg - off * off)
        pts, _ = _iso_trap_pts(b_big, b_small, h)
        poly(ax, pts, alpha=0.2)
        cx, cy = b_big / 2, h / 2
        circle(ax, (cx, cy), h / 2, fill="#E8E8E8")
        mark_pt(ax, 0, 0, "A", dx=-0.35, dy=-0.35)
        mark_pt(ax, b_big, 0, "B", dx=0.12, dy=-0.35)
        mark_pt(ax, b_big - off, h, "C", dx=0.12, dy=0.1)
        mark_pt(ax, off, h, "D", dx=-0.35, dy=0.1)
        dim_h(ax, 0, b_big, 0, "26", off=-0.95)
        dim_h(ax, off, b_big - off, h, "10", off=0.7)
        seg_label(ax, 0, 0, off, h, "13", frac=0.45, dx=-0.55, dy=0.0)
        seg_label(ax, b_big, 0, b_big - off, h, "13", frac=0.45, dx=0.55, dy=0.0)
        ax.plot([off, off], [0, h], "k--", lw=0.6, alpha=0.45)
        plain_text(ax, cx, cy, "קוטר = גובה", ha="center", fontsize=7, color="#444444")
        ax.set_xlim(-3, 30)
        ax.set_ylim(-2, h + 3)
    else:
        poly(ax, [(0, 0), (10, 0), (8, 4), (2, 4)], alpha=0.25)
        ax.set_xlim(-1, 12)
        ax.set_ylim(-1, 6)
    save_fig(fig, stem, n)


def _factory_plan(ax, show_values: bool = False) -> None:
    """MAHAT factory: CDFG 22×5, extension ABCG 20×5, rooms ABCG / ADEF / rest."""
    C, D, G = (0, 0), (22, 0), (0, 5)
    D_top, F, J, A, B = (22, 5), (10, 5), (20, 5), (0, 10), (20, 10)
    # E: equidistant from D and F with DE = FE = 7 (35% of AB)
    mid_df = ((D[0] + F[0]) / 2, (D[1] + F[1]) / 2)
    half_df = math.dist(D, F) / 2
    h_alt = math.sqrt(49 - half_df**2)
    E = (mid_df[0] + h_alt * 5 / 13, mid_df[1] + h_alt * 12 / 13)

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
    seg_label(ax, D[0], D[1], E[0], E[1], "7" if show_values else "35%", frac=0.42, dx=0.6, dy=-0.15)
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
        dim_h(ax, 0, 8, 13, "8", off=0.55)
        dim_v(ax, 8, 8, 13, "5", off=-0.75)
        plain_text(ax, 7.5, 4, "חלק א'", ha="center", fontsize=8)
        plain_text(ax, 4, 10.5, "חלק ב'", ha="center", fontsize=8)
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
        c, s = 2, 16
        outer = [
            (c, 0),
            (s - c, 0),
            (s - c, c),
            (s, c),
            (s, s - c),
            (s - c, s - c),
            (s - c, s),
            (c, s),
            (c, s - c),
            (0, s - c),
            (0, c),
            (c, c),
        ]
        poly(ax, outer, alpha=0.35)
        for ox, oy in [(0, 0), (s - c, 0), (s - c, s - c), (0, s - c)]:
            ax.plot([ox, ox + c, ox + c, ox, ox], [oy, oy, oy + c, oy + c, oy], "r--", lw=0.8)
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

    def _abcd_rect(w, h, alpha=0.12):
        poly(ax, [(0, 0), (w, 0), (w, h), (0, h)], alpha=alpha)
        mark_pt(ax, 0, 0, "A", dx=-0.35, dy=-0.28)
        mark_pt(ax, w, 0, "B", dx=0.1, dy=-0.28)
        mark_pt(ax, w, h, "C", dx=0.1, dy=0.08)
        mark_pt(ax, 0, h, "D", dx=-0.35, dy=0.08)
        right_angle(ax, 0, 0, min(0.35, w * 0.06, h * 0.06), quadrant=1)

    def _square_abcd(s, alpha=0.12):
        _abcd_rect(s, s, alpha=alpha)

    def _rhombus_diagonal_rect(ha, hb, d, shade_all=False, shade_corner_a=False):
        A, B, C, D = (0, ha), (hb, 0), (0, -ha), (-hb, 0)
        K = (0, ha - d)
        M = (0, -ha + d)
        I = (hb - d, 0)
        J = (-hb + d, 0)
        TL = (-hb + d, ha - d)
        TR = (hb - d, ha - d)
        BR = (hb - d, -ha + d)
        BL = (-hb + d, -ha + d)
        R = [TL, TR, BR, BL]
        E = K
        F = I
        H = M
        G = J
        poly(ax, [A, B, C, D], alpha=0.15)
        if shade_all:
            poly(ax, [A, B, C, D], fill=C_GRAY, alpha=0.35)
            poly(ax, R, fill="#F8F8F8", edge=C_EDGE, lw=1.2, alpha=0.95)
        elif shade_corner_a:
            x_top = hb * d / ha
            p_r = (x_top, K[1])
            p_l = (-x_top, K[1])
            poly(ax, [A, p_r, TR, TL, p_l], fill=C_GRAY, alpha=0.45)
            poly(ax, R, fill="#F8F8F8", edge=C_EDGE, lw=1.2, alpha=0.95)
        else:
            poly(ax, R, fill="#F8F8F8", edge=C_EDGE, lw=1.2, alpha=0.9)
        ax.plot([A[0], C[0]], [A[1], C[1]], "k--", lw=0.7)
        ax.plot([B[0], D[0]], [B[1], D[1]], "k--", lw=0.7)
        for p, lb, dx, dy in [
            (A, "A", -0.35, 0.1),
            (B, "B", 0.12, -0.3),
            (C, "C", -0.15, -0.4),
            (D, "D", -0.4, 0.05),
            (TL, "E", -0.35, 0.08),
            (TR, "F", 0.12, 0.08),
            (BR, "H", 0.12, -0.35),
            (BL, "G", -0.35, -0.35),
            (K, "K", 0.45, 0.05),
            (I, "I", 0.45, -0.1),
            (M, "M", 0.45, 0.05),
            (J, "J", -0.55, 0.05),
        ]:
            mark_pt(ax, p[0], p[1], lb, dx=dx, dy=dy)
        dim_v(ax, 0, -ha, ha, "70", off=1.15)
        dim_h(ax, -hb, hb, 0, "50", off=-1.05)
        seg_label(ax, A[0], A[1], K[0], K[1], "15", frac=0.45, dx=-0.55, dy=0.05, fs=7)
        seg_label(ax, B[0], B[1], I[0], I[1], "15", frac=0.45, dx=0.45, dy=-0.05, fs=7)
        seg_label(ax, C[0], C[1], M[0], M[1], "15", frac=0.45, dx=0.45, dy=0.05, fs=7)
        seg_label(ax, D[0], D[1], J[0], J[1], "15", frac=0.45, dx=-0.55, dy=-0.05, fs=7)
        rw, rh = 2 * (hb - d), 2 * (ha - d)
        dim_h(ax, TL[0], TR[0], ha - d, str(int(rw)), off=0.55, fs=7)
        dim_v(ax, hb - d, BR[1], TR[1], str(int(rh)), off=1.05, fs=7)
        ax.set_xlim(-hb - 6, hb + 6)
        ax.set_ylim(-ha - 6, ha + 6)

    if n == 9:
        w, h, ae = 18.0, 10.0, 6.0
        _abcd_rect(w, h)
        poly(ax, [(0, 0), (ae, 0), (w, h)], fill=C_GRAY, alpha=0.42)
        ax.plot([0, ae, w], [0, 0, h], "k-", lw=1.1)
        mark_pt(ax, ae, 0, "E", dx=0.1, dy=-0.28)
        dim_h(ax, 0, w, 0, "18", off=-0.85)
        dim_v(ax, w, 0, h, "10", off=0.85)
        dim_h(ax, 0, ae, 0, r"$AE$", off=-1.35, fs=7)
        dim_h(ax, ae, w, 0, r"$EB$", off=-1.35, fs=7)
        plain_text(ax, w / 2, -1.55, r"$AE:EB=1:2$", ha="center", fontsize=7)
        ax.set_xlim(-2.5, w + 3)
        ax.set_ylim(-2.2, h + 2)
    elif n == 10:
        s, be = 12.0, 3.0
        _square_abcd(s)
        poly(ax, [(0, 0), (s, 0), (s, be)], fill=C_GRAY, alpha=0.42)
        ax.plot([0, s, s], [0, 0, be], "k-", lw=1.1)
        mark_pt(ax, s, be, "E", dx=0.1, dy=0.05)
        dim_h(ax, 0, s, 0, "12", off=-0.85)
        dim_v(ax, s, 0, be, r"$BE$", off=0.65, fs=7)
        dim_v(ax, s, be, s, r"$EC$", off=0.65, fs=7)
        plain_text(ax, s / 2, -1.45, r"$BE:EC=1:3$", ha="center", fontsize=7)
        ax.set_xlim(-1.8, s + 2.5)
        ax.set_ylim(-1.8, s + 2)
    elif n == 11:
        w, h, be, bf = 50.0, 20.0, 10.0, 5.0
        _abcd_rect(w, h)
        poly(ax, [(w, 0), (w - bf, 0), (w, be)], fill=C_GRAY, alpha=0.45)
        ax.plot([w, w - bf, w], [0, 0, be], "k-", lw=1.1)
        right_angle(ax, w, 0, 0.9, quadrant=3)
        dim_h(ax, w - bf, w, 0, "5", off=-0.85)
        dim_v(ax, w, 0, be, "10", off=0.85)
        dim_h(ax, 0, w, h, "50", off=0.55)
        dim_v(ax, 0, 0, h, "20", off=-1.1)
        for px, py, lb, dx, dy in [
            (0, 0, "A", -1.1, -0.55),
            (w, 0, "B", 0.12, -0.35),
            (w, h, "C", 0.12, 0.08),
            (0, h, "D", -0.55, 0.08),
            (w, be, "E", 0.1, 0.05),
            (w - bf, 0, "F", 0.1, -0.55),
        ]:
            mark_pt(ax, px, py, lb, dx=dx, dy=dy)
        ax.set_xlim(-5, w + 4)
        ax.set_ylim(-2, h + 2)
    elif n == 12:
        R, r = 10.0, 6.0
        circle(ax, (0, 0), R, fill=C_GRAY, ec=C_EDGE, lw=1.4)
        circle(ax, (0, 0), r, fill="white", ec=C_EDGE, lw=1.4)
        mark_pt(ax, 0, 0, "O", dx=-0.35, dy=-0.35)
        dim_h(ax, 0, R, 0, r"$R=10$", off=-0.85)
        dim_h(ax, 0, r, 0, r"$r=6$", off=0.65)
        ax.set_xlim(-12.5, 12.5)
        ax.set_ylim(-12.5, 12.5)
    elif n in (13, 19):
        w, h, be = 25.0, 48.0, 32.0
        _abcd_rect(w, h, alpha=0.1)
        poly(ax, [(0, 0), (w, 0), (w, be)], fill=C_GRAY, alpha=0.38)
        ax.plot([0, w], [0, be], "k-", lw=1.0)
        mark_pt(ax, w, be, "E", dx=0.1, dy=0.05)
        dim_h(ax, 0, w, 0, "25", off=-1.1)
        dim_v(ax, w, 0, h, "48", off=1.1)
        dim_v(ax, w, 0, be, r"$BE$", off=1.55, fs=7)
        dim_v(ax, w, be, h, r"$EC$", off=1.55, fs=7)
        plain_text(ax, w + 0.2, h / 2, r"$BE=2\cdot EC$", fontsize=7)
        ax.set_xlim(-3, w + 5)
        ax.set_ylim(-2, h + 2)
    elif n == 14:
        s, be = 12.0, 4.0
        _square_abcd(s)
        poly(ax, [(0, 0), (s, 0), (s, be)], fill=C_GRAY, alpha=0.42)
        ax.plot([0, s, s], [0, 0, be], "k-", lw=1.1)
        mark_pt(ax, s, be, "E", dx=0.1, dy=0.05)
        dim_h(ax, 0, s, 0, r"$a$", off=-0.85)
        dim_v(ax, s, 0, be, r"$\frac{a}{3}$", off=0.7)
        dim_v(ax, s, be, s, r"$\frac{2a}{3}$", off=0.7)
        ax.set_xlim(-1.8, s + 2.5)
        ax.set_ylim(-1.8, s + 2)
    elif n == 15:
        w, h, be = 8.0, 15.0, 10.0
        _abcd_rect(w, h)
        poly(ax, [(0, 0), (w, 0), (w, be)], fill=C_GRAY, alpha=0.35)
        ax.plot([0, w], [0, be], "k-", lw=1.0)
        mark_pt(ax, w, be, "E", dx=0.1, dy=0.05)
        dim_h(ax, 0, w, 0, "8", off=-0.85)
        dim_v(ax, w, 0, h, "15", off=0.85)
        dim_v(ax, w, 0, be, r"$BE$", off=1.35, fs=7)
        dim_v(ax, w, be, h, r"$EC$", off=1.35, fs=7)
        plain_text(ax, w + 0.15, h / 2, r"$BE=2\cdot EC$", fontsize=7)
        ax.set_xlim(-2.2, w + 3)
        ax.set_ylim(-1.5, h + 1.5)
    elif n == 16:
        _rhombus_diagonal_rect(35, 25, 15, shade_all=True)
    elif n == 17:
        w, h = 7.5, 4.5
        _abcd_rect(w, h)
        e_x = w * 2 / 3
        mark_pt(ax, e_x, h, "E", dx=0.08, dy=0.05)
        ax.plot([0, e_x], [0, h], "k-", lw=0.9)
        ax.plot([e_x, w], [h, 0], "k-", lw=0.9)
        ax.plot([0, w], [0, h], "k--", lw=0.7)
        dim_h(ax, 0, w, 0, "7.5 מ'", off=-0.85)
        dim_v(ax, w, 0, h, "4.5 מ'", off=0.85)
        dim_h(ax, 0, e_x, h, r"$DE$", off=0.55, fs=7)
        dim_h(ax, e_x, w, h, r"$EC$", off=0.55, fs=7)
        plain_text(ax, e_x / 2, h + 0.35, r"$DE=2\cdot EC$", ha="center", fontsize=7)
        ax.set_xlim(-1.8, w + 2.2)
        ax.set_ylim(-1.5, h + 1.8)
    elif n == 18:
        w, h, be, bf = 50.0, 20.0, 10.0, 5.0
        _abcd_rect(w, h, alpha=0.1)
        poly(ax, [(w, 0), (w - bf, 0), (w, be)], fill=C_GRAY, alpha=0.45)
        ax.plot([w, w - bf, w], [0, 0, be], "k-", lw=1.2)
        right_angle(ax, w, 0, 0.9, quadrant=3)
        dim_h(ax, w - bf, w, 0, "5", off=-0.85)
        dim_v(ax, w, 0, be, "10", off=0.85)
        dim_h(ax, 0, w, h, "50", off=0.55)
        dim_v(ax, 0, 0, h, "20", off=-1.1)
        for px, py, lb, dx, dy in [
            (0, 0, "A", -1.1, -0.55),
            (w, 0, "B", 0.12, -0.35),
            (w, h, "C", 0.12, 0.08),
            (0, h, "D", -0.55, 0.08),
            (w, be, "E", 0.1, 0.05),
            (w - bf, 0, "F", 0.1, -0.55),
        ]:
            mark_pt(ax, px, py, lb, dx=dx, dy=dy)
        ax.set_xlim(-5, w + 4)
        ax.set_ylim(-2, h + 2)
    elif n == 20:
        _rhombus_diagonal_rect(35, 25, 15, shade_corner_a=True)
    else:
        _abcd_rect(10, 6)
        ax.set_xlim(-2, 13)
        ax.set_ylim(-2, 9)

    save_fig(fig, stem, n)


def _coord_poly(ax, pts, labels, shade_idx=None):
    poly(ax, pts, alpha=0.25)
    for i, (x, y) in enumerate(pts):
        mark_pt(ax, x, y, labels[i])
    if shade_idx is not None:
        # shade triangle or region — first three vertices as example
        sub = [pts[i] for i in shade_idx]
        poly(ax, sub, fill=C_GRAY, alpha=0.45)


def _fmt_coord(v):
    return str(int(v)) if v == int(v) else str(v)


def _coord_poly_pts(ax, pts, letters, shade_idx=None, alpha=0.25):
    poly(ax, pts, alpha=alpha)
    for (x, y), lb in zip(pts, letters):
        mark_pt(ax, x, y, f"{lb}({_fmt_coord(x)},{_fmt_coord(y)})")
    if shade_idx is not None:
        sub = [pts[i] for i in shade_idx]
        poly(ax, sub, fill=C_GRAY, alpha=0.45)


def _plane_for_pts(pts, pad=1.5):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (min(xs) - pad, max(xs) + pad), (min(ys) - pad, max(ys) + pad)


def gen_17(stem: str, n: int) -> None:
    if n <= 8:
        fig, ax = coord_plane((-5, 5), (-5, 5))
        if n == 1:
            pass
        elif n == 2:
            poly(ax, [(0, 0), (3, 0), (3, 3), (0, 3)], fill="#E3F2FD", alpha=0.5)
        elif n == 3:
            poly(ax, [(-3, 0), (0, 0), (0, 3), (-3, 3)], fill="#E3F2FD", alpha=0.4)
        elif n == 4:
            poly(ax, [(-3, -3), (0, -3), (0, 0), (-3, 0)], fill="#E3F2FD", alpha=0.4)
        elif n == 5:
            poly(ax, [(0, -3), (3, -3), (3, 0), (0, 0)], fill="#E3F2FD", alpha=0.4)
        elif n == 6:
            mark_pt(ax, 4, 0)
        elif n == 7:
            mark_pt(ax, 0, 5)
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
        fig, ax = coord_plane((-3, 3), (-3, 3))
        for (cx, cy), lb in zip(
            [(2, 2), (-2, 2), (-2, -2), (2, -2)],
            ["A", "B", "C", "D"],
        ):
            poly(
                ax,
                [(cx - 1, cy - 1), (cx + 1, cy - 1), (cx + 1, cy + 1), (cx - 1, cy + 1)],
                fill="#E3F2FD",
                alpha=0.4,
            )
            plain_text(ax, cx, cy, lb, ha="center", va="center", fontsize=10)
    elif n == 13:
        fig, ax = coord_plane((-7, 2), (-2, 2))
        mark_pt(ax, -5, 0, "R")
    elif n == 14:
        fig, ax = coord_plane((-2, 6), (-2, 8))
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
        labels = [f"{lb}({x},{y})" for (x, y), lb in zip(pts, ["A", "B", "C", "D"])]
        _coord_poly(ax, pts, labels)
    elif n == 18:
        fig, ax = coord_plane((-6, 5), (-6, 4))
        for x, y, lb in [(3, -2, "P"), (-4, 1, "Q"), (0, -5, "R"), (-2, 0, "S")]:
            mark_pt(ax, x, y, lb)
    elif n == 19:
        fig, ax = coord_plane((-2, 8), (-5, 2))
        mark_pt(ax, 5, 0, "A(5,0)")
        mark_pt(ax, 0, -3, "B(0,-3)")
        ax.plot([5, 0], [0, -3], "k-", lw=1.2)
        dim_h(ax, 0, 5, 0, "5", off=-0.65)
        dim_v(ax, 0, 0, -3, "3", off=0.65)
    elif n == 20:
        fig, ax = coord_plane((-5, 5), (-4, 4))
        pts = [(-3, 2), (3, 2), (3, -2), (-3, -2)]
        labels = [f"{lb}({x},{y})" for (x, y), lb in zip(pts, ["A", "B", "C", "D"])]
        _coord_poly(ax, pts, labels)
    save_fig(fig, stem, n)


def gen_18(stem: str, n: int) -> None:
    if n <= 8:
        plane_limits = {
            1: ((-4, 6), (-4, 6)),
            2: ((-4, 6), (-4, 6)),
            3: ((-4, 6), (-4, 6)),
            4: ((-4, 6), (-4, 6)),
            5: ((-4, 6), (-6, 6)),
            6: ((-4, 6), (-4, 6)),
            7: ((-4, 6), (-4, 8)),
            8: ((-4, 6), (-4, 8)),
        }
        fig, ax = coord_plane(*plane_limits[n])
        if n == 1:
            mark_pt(ax, 3, 4, "A")
            mark_pt(ax, -2, 5, "B")
        elif n == 3:
            mark_pt(ax, 3, 4, "A(3,4)")
        elif n in (4, 5, 6, 7, 8):
            mark_pt(ax, -2, 0, "B") if n == 4 else None
            if n == 5:
                mark_pt(ax, 0, -5, "C(0,-5)")
            if n == 6:
                mark_pt(ax, 3, 4, "P")
                mark_pt(ax, 4, 3, "Q")
            if n == 7:
                pass
            if n == 8:
                pass
    elif n == 9:
        fig, ax = coord_plane((-2, 10), (-4, 8))
        for x, y, lb in [(1, 3, "A"), (7, 3, "B"), (4, -1, "C")]:
            mark_pt(ax, x, y, lb)
        ax.plot([1, 7], [3, 3], "k--", lw=0.8)
    elif n == 10:
        fig, ax = coord_plane((-2, 10), (-4, 8))
        mark_pt(ax, 2, 4, "A")
        mark_pt(ax, 8, 4, "B")
        ax.plot([2, 8], [4, 4], "k-", lw=1.0)
    elif n == 11:
        fig, ax = coord_plane((-4, 10), (-4, 8))
        mark_pt(ax, -3, 4, "A")
        mark_pt(ax, 5, 4, "B")
        ax.plot([-3, 5], [4, 4], "k-", lw=1.0)
    elif n == 12:
        fig, ax = coord_plane((-2, 10), (-4, 8))
        mark_pt(ax, 0, 6, "P")
        mark_pt(ax, 8, 0, "Q")
        ax.plot([0, 8], [6, 0], "k-", lw=1.0)
    elif n == 13:
        fig, ax = coord_plane((-2, 10), (-4, 8))
        ax.axhline(-2, color="gray", lw=0.8, ls=":")
        mark_pt(ax, -1, -2, "T(-1,-2)")
        plain_text(ax, 1.2, -1.55, "5 יח' ימינה", ha="left", fontsize=8)
    elif n == 14:
        fig, ax = coord_plane((-2, 10), (-4, 8))
        ax.axvline(4, color="gray", lw=0.8, ls=":")
        dim_v(ax, 4, 0, -3, "3", off=0.65)
        plain_text(ax, 4.8, -1.5, "K?", ha="left", fontsize=9)
    elif n == 15:
        fig, ax = coord_plane((-2, 10), (-4, 8))
        ax.axhline(5, color="gray", lw=0.8, ls=":")
    elif n == 16:
        fig, ax = coord_plane((-2, 10), (-4, 8))
        ax.axvline(-2, color="gray", lw=0.8, ls=":")
    elif n == 17:
        pts = [(0, -1), (4, -1), (4, 2), (0, 2)]
        xlim, ylim = _plane_for_pts(pts)
        fig, ax = coord_plane(xlim, ylim)
        _coord_poly_pts(ax, pts, ["A", "B", "C", "D"])
    elif n == 18:
        pts = [(0, 0), (5, 0), (5, 12), (0, 12)]
        xlim, ylim = _plane_for_pts(pts)
        fig, ax = coord_plane(xlim, ylim)
        _coord_poly_pts(ax, pts, ["A", "B", "C", "D"])
    elif n == 19:
        pts = [(0, 0), (8, 0), (8, 6), (0, 6)]
        xlim, ylim = _plane_for_pts(pts)
        fig, ax = coord_plane(xlim, ylim)
        _coord_poly_pts(ax, pts, ["A", "B", "C", "D"])
        mark_pt(ax, 3, 0, "E(3,0)")
        ax.plot([3, 8], [0, 6], "k-", lw=1)
    elif n == 20:
        boundary = [(0, 0), (10, 0), (10, 8), (0, 8)]
        pool = [(2, 2), (6, 2), (6, 6), (2, 6)]
        xlim, ylim = _plane_for_pts(boundary + pool, pad=1.5)
        fig, ax = coord_plane(xlim, ylim)
        poly(ax, boundary, alpha=0.2)
        poly(ax, pool, fill=C_GRAY, alpha=0.45)
        for (x, y), lb in zip(
            boundary + pool,
            ["A", "B", "C", "D", "P", "Q", "R", "S"],
        ):
            mark_pt(ax, x, y, f"{lb}({_fmt_coord(x)},{_fmt_coord(y)})")
    else:
        fig, ax = coord_plane((-2, 10), (-4, 8))
    save_fig(fig, stem, n)


def gen_19(stem: str, n: int) -> None:
    def _pt(ax, x, y, lb):
        mark_pt(ax, x, y, f"{lb}({_fmt_coord(x)},{_fmt_coord(y)})")

    if n == 1:
        fig, ax = coord_plane((-2, 10), (-4, 8))
        _pt(ax, 1, 3, "A")
        _pt(ax, 7, 3, "B")
        ax.plot([1, 7], [3, 3], "k-", lw=1.5)
    elif n == 2:
        fig, ax = coord_plane((-2, 10), (-4, 8))
        _pt(ax, 4, -2, "C")
        _pt(ax, 4, 5, "D")
        ax.plot([4, 4], [-2, 5], "k-", lw=1.5)
    elif n == 3:
        fig, ax = coord_plane((-5, 8), (-4, 6))
        _pt(ax, -3, 2, "E")
        _pt(ax, 5, 2, "F")
        ax.plot([-3, 5], [2, 2], "k-", lw=1.5)
    elif n == 4:
        fig, ax = coord_plane((-2, 8), (-6, 6))
        _pt(ax, 2, -4, "G")
        _pt(ax, 2, 3, "H")
        ax.plot([2, 2], [-4, 3], "k-", lw=1.5)
    elif n == 5:
        fig, ax = coord_plane((-2, 8), (-4, 6))
        _pt(ax, 0, 0, "P")
        _pt(ax, 6, 0, "Q")
        ax.plot([0, 6], [0, 0], "k-", lw=1.5)
    elif n == 6:
        fig, ax = coord_plane((-7, 6), (-4, 8))
        _pt(ax, -5, 4, "M")
        _pt(ax, 3, 4, "N")
        ax.plot([-5, 3], [4, 4], "k-", lw=1.5)
    elif n == 7:
        fig, ax = coord_plane((-2, 10), (-4, 8))
        _pt(ax, 0, 7, "A")
        _pt(ax, 0, -2, "B")
        ax.plot([0, 0], [7, -2], "k-", lw=1.5)
    elif n == 8:
        fig, ax = coord_plane((-2, 10), (-4, 8))
        _pt(ax, 2, 0, "A")
        _pt(ax, 7, 0, "B")
        ax.plot([2, 7], [0, 0], "k-", lw=1.5)
        dim_h(ax, 2, 7, 0, r"$b-a$", off=-0.65)
        ax.text(2, -0.35, r"$a$", fontsize=8, ha="center")
        ax.text(7, -0.35, r"$b$", fontsize=8, ha="center")
    elif n == 9:
        pts = [(0, -1), (4, -1), (4, 2), (0, 2)]
        fig, ax = coord_plane(*_plane_for_pts(pts))
        _coord_poly_pts(ax, pts, ["A", "B", "C", "D"])
    elif n == 10:
        fig, ax = coord_plane((-2, 8), (-5, 2))
        _pt(ax, 5, 0, "P")
        _pt(ax, 0, -3, "Q")
        ax.plot([5, 0], [0, -3], "k-", lw=1.2)
        dim_h(ax, 0, 5, 0, "5", off=-0.65)
        dim_v(ax, 0, 0, -3, "3", off=0.65)
    elif n == 11:
        pts = [(0, 0), (6, 0), (6, 4), (0, 4)]
        fig, ax = coord_plane(*_plane_for_pts(pts))
        _coord_poly_pts(ax, pts, ["A", "B", "C", "D"])
    elif n == 12:
        pts = [(1, 1), (5, 1), (5, 5), (1, 5)]
        fig, ax = coord_plane(*_plane_for_pts(pts))
        _coord_poly_pts(ax, pts, ["P", "Q", "R", "S"])
    elif n == 13:
        pts = [(-4, 3), (2, 3), (2, -1)]
        fig, ax = coord_plane(*_plane_for_pts(pts))
        _coord_poly_pts(ax, pts, ["A", "B", "C"])
        right_angle(ax, 2, 3, 0.35, quadrant=4)
    elif n == 14:
        pts = [(0, 0), (8, 0), (8, 6)]
        fig, ax = coord_plane(*_plane_for_pts(pts))
        _coord_poly_pts(ax, pts, ["A", "B", "C"])
        right_angle(ax, 8, 0, 0.35, quadrant=1)
    elif n == 15:
        pts = [(1, 2), (9, 2), (9, 8), (1, 8)]
        fig, ax = coord_plane(*_plane_for_pts(pts))
        _coord_poly_pts(ax, pts, ["A", "B", "C", "D"])
    elif n == 16:
        fig, ax = coord_plane((-2, 12), (-2, 10))
        _pt(ax, 2, 0, "A")
        _pt(ax, 9, 0, "B")
        _pt(ax, 0, 1, "C")
        _pt(ax, 0, 7, "D")
        dim_h(ax, 2, 9, 0, "7", off=-0.65)
        dim_v(ax, 0, 1, 7, "6", off=0.65)
    elif n == 17:
        pts = [(0, -1), (4, -1), (4, 2), (0, 2)]
        fig, ax = coord_plane(*_plane_for_pts(pts))
        _coord_poly_pts(ax, pts, ["A", "B", "C", "D"])
    elif n == 18:
        pts = [(0, 0), (5, 0), (5, 12), (0, 12)]
        fig, ax = coord_plane(*_plane_for_pts(pts))
        _coord_poly_pts(ax, pts, ["A", "B", "C", "D"])
        right_angle(ax, 5, 0, 0.35, quadrant=1)
    elif n == 19:
        pts = [(0, 0), (12, 0), (12, 9)]
        fig, ax = coord_plane(*_plane_for_pts(pts))
        _coord_poly_pts(ax, pts, ["X", "Y", "Z"])
        right_angle(ax, 12, 0, 0.35, quadrant=2)
        dim_h(ax, 0, 12, 0, "12", off=-0.75)
        dim_v(ax, 12, 0, 9, "9", off=0.75)
    elif n == 20:
        pts = [(0, 0), (8, 0), (8, 6), (0, 6)]
        fig, ax = coord_plane(*_plane_for_pts(pts))
        _coord_poly_pts(ax, pts, ["A", "B", "C", "D"])
        _pt(ax, 3, 0, "E")
        ax.plot([3, 8], [0, 6], "k-", lw=1.2)
    save_fig(fig, stem, n)


def gen_20(stem: str, n: int) -> None:
    if n == 1:
        pts = [(0, 0), (5, 0), (5, 3), (0, 3)]
        fig, ax = coord_plane(*_plane_for_pts(pts))
        _coord_poly_pts(ax, pts, ["A", "B", "C", "D"])
    elif n == 2:
        pts = [(1, 1), (5, 1), (5, 5), (1, 5)]
        fig, ax = coord_plane(*_plane_for_pts(pts))
        _coord_poly_pts(ax, pts, ["P", "Q", "R", "S"])
    elif n == 3:
        pts = [(0, 0), (6, 0), (6, 4)]
        fig, ax = coord_plane(*_plane_for_pts(pts))
        _coord_poly_pts(ax, pts, ["A", "B", "C"])
        right_angle(ax, 6, 0, 0.45, quadrant=2)
    elif n == 4:
        pts = [(0, 0), (8, 0), (0, 5)]
        fig, ax = coord_plane(*_plane_for_pts(pts))
        _coord_poly_pts(ax, pts, ["D", "E", "F"])
        right_angle(ax, 0, 0, 0.45, quadrant=1)
    elif n == 5:
        pts = [(2, 1), (7, 1), (7, 4), (2, 4)]
        fig, ax = coord_plane(*_plane_for_pts(pts))
        _coord_poly_pts(ax, pts, ["A", "B", "C", "D"])
    elif n == 6:
        pts = [(3, 2), (9, 2), (9, 6)]
        fig, ax = coord_plane(*_plane_for_pts(pts))
        _coord_poly_pts(ax, pts, ["A", "B", "C"])
        right_angle(ax, 9, 2, 0.45, quadrant=2)
    elif n == 7:
        pts = [(1, 2), (7, 2), (7, 6), (1, 6)]
        fig, ax = coord_plane(*_plane_for_pts(pts))
        _coord_poly_pts(ax, pts, ["A", "B", "C", "D"])
        dim_h(ax, 1, 7, 2, "6", off=-0.65)
        dim_v(ax, 7, 2, 6, "4", off=0.65)
    elif n == 8:
        fig, ax = coord_plane((-1, 5), (-1, 5))
        mark_pt(ax, 0, 0, "A(0,0)", dx=-0.1, dy=-0.35)
        mark_pt(ax, 4, 0, "B(4,0)", dx=-0.15, dy=-0.35)
        dim_h(ax, 0, 4, 0, "4", off=-0.65)
    elif n == 9:
        pts = [(0, -1), (4, -1), (4, 2), (0, 2)]
        fig, ax = coord_plane(*_plane_for_pts(pts, pad=2))
        _coord_poly_pts(ax, pts, ["A", "B", "C", "D"])
        mark_pt(ax, 2, 0.5, "M(2,0.5)", dx=0.12, dy=0.12)
        ax.plot([0, 4], [2, -1], "k--", lw=0.7)
        ax.plot([0, 4], [-1, 2], "k--", lw=0.7)
    elif n == 10:
        pts = [(0, 0), (10, 0), (4, 6)]
        fig, ax = coord_plane(*_plane_for_pts(pts))
        _coord_poly_pts(ax, pts, ["A", "B", "C"])
    elif n == 11:
        pts = [(0, 0), (10, 0), (8, 4), (2, 4)]
        fig, ax = coord_plane(*_plane_for_pts(pts))
        _coord_poly_pts(ax, pts, ["A", "B", "C", "D"])
        dim_h(ax, 0, 10, 0, "10", off=-0.75)
        dim_h(ax, 2, 8, 4, "6", off=0.55, fs=7)
        dim_v(ax, 0, 0, 4, "4", off=-0.75)
    elif n == 12:
        pts = [(0, 0), (6, 0), (6, 5), (0, 5)]
        fig, ax = coord_plane(*_plane_for_pts(pts))
        _coord_poly_pts(ax, pts, ["A", "B", "C", "D"])
        mark_pt(ax, 2, 0, "E(2,0)", dx=0.1, dy=-0.35)
        ax.plot([2, 6], [0, 5], "k-", lw=1)
    elif n == 13:
        pts = [(0, 0), (9, 0), (9, 12)]
        fig, ax = coord_plane(*_plane_for_pts(pts))
        _coord_poly_pts(ax, pts, ["P", "Q", "R"])
        right_angle(ax, 9, 0, 0.55, quadrant=2)
    elif n == 14:
        pts = [(0, 0), (12, 0), (10, 5), (2, 5)]
        fig, ax = coord_plane(*_plane_for_pts(pts))
        _coord_poly_pts(ax, pts, ["A", "B", "C", "D"])
        dim_h(ax, 0, 12, 0, "12", off=-0.85)
        dim_h(ax, 2, 10, 5, "8", off=0.55, fs=7)
        dim_v(ax, 0, 0, 5, "5", off=-0.85)
    elif n == 15:
        pts = [(1, 1), (9, 1), (9, 6), (1, 6)]
        fig, ax = coord_plane(*_plane_for_pts(pts))
        _coord_poly_pts(ax, pts, ["A", "B", "C", "D"])
        mark_pt(ax, 9, 3.5, "E(9,3.5)", dx=0.12, dy=0.05)
        ax.plot([1, 9], [1, 3.5], "k-", lw=1)
    elif n == 16:
        pts = [(0, 2), (4, 0), (6, 4), (2, 6)]
        fig, ax = coord_plane((-1, 7), (-1, 7))
        _coord_poly_pts(ax, pts, ["A", "B", "C", "D"])
    elif n == 17:
        pts = [(0, -1), (4, -1), (4, 2), (0, 2)]
        fig, ax = coord_plane(*_plane_for_pts(pts, pad=2))
        _coord_poly_pts(ax, pts, ["A", "B", "C", "D"])
        mark_pt(ax, 2, 0.5, "M(2,0.5)", dx=0.12, dy=0.12)
        ax.plot([0, 4], [2, -1], "k--", lw=0.7)
        ax.plot([0, 4], [-1, 2], "k--", lw=0.7)
    elif n == 18:
        pts = [(0, 0), (25, 0), (25, 48), (0, 48)]
        fig, ax = coord_plane((-3, 30), (-5, 55), grid_step_x=5, grid_step_y=5)
        _coord_poly_pts(ax, pts, ["A", "B", "C", "D"])
        mark_pt(ax, 25, 32, "E(25,32)", dx=0.15, dy=0.1)
        dim_h(ax, 0, 25, 0, "25", off=-2.5)
        dim_v(ax, 25, 0, 48, "48", off=2.5)
        dim_v(ax, 25, 0, 32, r"$BE$", off=3.2, fs=7)
        dim_v(ax, 25, 32, 48, r"$EC$", off=3.2, fs=7)
    elif n == 19:
        fig, ax = coord_plane((-1, 11), (-1, 9), figsize=(7.2, 6.0))
        poly(ax, [(0, 0), (10, 0), (10, 8), (0, 8)], alpha=0.15)
        poly(ax, [(2, 2), (6, 2), (6, 6), (2, 6)], fill="#B0BEC5", alpha=0.55, edge=C_EDGE, lw=1.5)
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
        plain_text(ax, 1, 1, "א'\n2×2", ha="center", fontsize=7)
        plain_text(ax, 8, 4, "ב'\n4×8", ha="center", fontsize=7)
        plain_text(ax, 4, 7, "ג'", ha="center", fontsize=8)
        plain_text(ax, 4, 1, "ג'", ha="center", fontsize=8)
        plain_text(ax, 4, 4, "בריכה\n4×4", ha="center", fontsize=7, color="#333333")
        dim_h(ax, 0, 10, -0.6, "10", off=0, fs=7)
        dim_v(ax, -0.6, 0, 8, "8", off=0, fs=7)
    elif n == 20:
        pts = [(0, 0), (15, 0), (15, 8), (0, 8)]
        fig, ax = coord_plane((-2, 18), (-2, 10))
        _coord_poly_pts(ax, pts, ["A", "B", "C", "D"])
        mark_pt(ax, 5, 8, "E(5,8)", dx=-0.15, dy=0.12)
        mark_pt(ax, 15, 4, "F(15,4)", dx=0.12, dy=0.05)
        poly(ax, [(0, 8), (5, 8), (15, 4)], fill=C_GRAY, alpha=0.35)
        ax.plot([0, 5, 15], [8, 8, 4], "k-", lw=1.1)
        dim_h(ax, 0, 15, 0, "15", off=-0.85)
        dim_v(ax, 15, 0, 8, "8", off=0.85)
        dim_h(ax, 0, 5, 8, r"$DE$", off=0.55, fs=7)
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
