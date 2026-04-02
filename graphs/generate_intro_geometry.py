# -*- coding: utf-8 -*-
"""Generate PNG diagrams for מבוא להנדסה practice. Run from repo root:
   py graphs/generate_intro_geometry.py
Figure labels: English and numerals only (no Hebrew on canvas)."""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Polygon, Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "intro_geometry")
os.makedirs(OUT, exist_ok=True)

plt.rcParams["font.sans-serif"] = ["Segoe UI", "Arial", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def _save(fig, fname):
    fig.savefig(os.path.join(OUT, fname), dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def off(ax):
    ax.set_aspect("equal")
    ax.axis("off")


# --- 6.1 ---
def s61_ex01():
    fig, ax = plt.subplots(figsize=(5, 3.8), dpi=150)
    verts = np.array([[0.0, 0.0], [4.2, 0.0], [0.55, 2.6]])
    ax.add_patch(Polygon(verts, closed=True, fill=False, lw=2, edgecolor="#1565C0"))
    ax.text(-0.25, -0.15, r"$40^\circ$", fontsize=12)
    ax.text(3.85, -0.15, r"$95^\circ$", fontsize=12)
    ax.text(0.45, 2.75, r"$?$", fontsize=13)
    ax.set_xlim(-0.6, 4.8)
    ax.set_ylim(-0.5, 3.2)
    off(ax)
    _save(fig, "s61_ex01.png")


def s61_ex05():
    fig, ax = plt.subplots(figsize=(4.5, 4.5), dpi=150)
    ax.add_patch(Circle((0, 0), 1.0, fill=False, lw=2, edgecolor="#1565C0"))
    ax.plot([-1, 1], [0, 0], "k-", lw=1.5)
    ax.text(0, 0.12, r"$d = 18$ cm", ha="center", fontsize=11)
    ax.set_xlim(-1.35, 1.35)
    ax.set_ylim(-1.35, 1.35)
    off(ax)
    _save(fig, "s61_ex05.png")


def s61_ex06():
    fig, ax = plt.subplots(figsize=(6, 3.8), dpi=150)
    ang = np.radians(63)
    base, side = 4.0, 2.2
    p0 = np.array([0.0, 0.0])
    p1 = p0 + np.array([base, 0.0])
    p2 = p1 + np.array([side * np.cos(ang), side * np.sin(ang)])
    p3 = p0 + np.array([side * np.cos(ang), side * np.sin(ang)])
    ax.add_patch(Polygon(np.vstack([p0, p1, p2, p3]), closed=True, fill=False, lw=2, edgecolor="#1565C0"))
    ax.text(0.35, 0.08, r"$63^\circ$", fontsize=12)
    ax.set_xlim(-0.3, 5.2)
    ax.set_ylim(-0.3, 2.4)
    off(ax)
    _save(fig, "s61_ex06.png")


def s61_ex10():
    fig, ax = plt.subplots(figsize=(4.5, 4), dpi=150)
    verts = np.array([[0.0, 0.0], [3.5, 0.0], [3.5, 2.45]])
    ax.add_patch(Polygon(verts, closed=True, fill=False, lw=2, edgecolor="#1565C0"))
    ax.plot([3.35, 3.35, 3.5], [0.0, 0.15, 0.15], "k-", lw=1)
    ax.text(3.05, 0.25, r"$35^\circ$", fontsize=12)
    ax.text(2.0, -0.2, r"$90^\circ$", fontsize=11, ha="center")
    ax.set_xlim(-0.2, 4.0)
    ax.set_ylim(-0.45, 2.9)
    off(ax)
    _save(fig, "s61_ex10.png")


def s61_ex15():
    fig, ax = plt.subplots(figsize=(5, 4.2), dpi=150)
    verts = np.array([[0.0, 0.0], [4.0, 0.0], [2.0, 3.2]])
    ax.add_patch(Polygon(verts, closed=True, fill=False, lw=2, edgecolor="#1565C0"))
    ax.text(-0.35, -0.12, r"$48^\circ$", fontsize=11)
    ax.text(3.55, -0.12, r"$48^\circ$", fontsize=11)
    ax.text(1.85, 3.35, r"$?$", fontsize=13)
    ax.set_xlim(-0.7, 4.6)
    ax.set_ylim(-0.4, 3.8)
    off(ax)
    _save(fig, "s61_ex15.png")


def s61_ex19():
    fig, ax = plt.subplots(figsize=(6, 3.8), dpi=150)
    p0, p1 = np.array([0.0, 0.0]), np.array([4.0, 0.0])
    p3 = np.array([0.8, 2.2])
    p2 = p1 + (p3 - p0)
    poly = np.vstack([p0, p1, p2, p3])
    ax.add_patch(Polygon(poly, closed=True, fill=False, lw=2, edgecolor="#1565C0"))
    ax.plot([p0[0], p2[0]], [p0[1], p2[1]], "k--", lw=1.5, alpha=0.85)
    ax.text(1.9, 1.05, "diagonal", fontsize=9, ha="center", rotation=28)
    ax.set_xlim(-0.3, 5.0)
    ax.set_ylim(-0.3, 2.6)
    off(ax)
    _save(fig, "s61_ex19.png")


# --- 6.2 ---
def s62_ex01():
    fig, ax = plt.subplots(figsize=(5.5, 3.2), dpi=150)
    ax.add_patch(Rectangle((0, 0), 9, 4, fill=False, lw=2, edgecolor="#1565C0"))
    ax.text(4.5, -0.35, "9 cm", ha="center", fontsize=11)
    ax.text(-0.45, 2, "4 cm", ha="center", va="center", fontsize=11, rotation=90)
    ax.set_xlim(-0.8, 9.8)
    ax.set_ylim(-0.7, 4.6)
    off(ax)
    _save(fig, "s62_ex01.png")


def s62_ex02():
    fig, ax = plt.subplots(figsize=(4.2, 4.2), dpi=150)
    ax.add_patch(Rectangle((0, 0), 11, 11, fill=False, lw=2, edgecolor="#1565C0"))
    ax.text(5.5, -0.55, "11 m", ha="center", fontsize=11)
    ax.set_xlim(-0.8, 12)
    ax.set_ylim(-1, 12)
    off(ax)
    _save(fig, "s62_ex02.png")


def s62_ex03():
    fig, ax = plt.subplots(figsize=(5.5, 3.4), dpi=150)
    ax.plot([0, 8, 4, 0], [0, 0, 3, 0], "-", color="#1565C0", lw=2)
    ax.plot([4, 4], [0, 3], "k--", lw=1, alpha=0.7)
    ax.text(4, -0.35, "8 cm", ha="center", fontsize=11)
    ax.text(4.25, 1.4, "3 cm", fontsize=10)
    ax.set_xlim(-0.5, 8.6)
    ax.set_ylim(-0.7, 3.6)
    off(ax)
    _save(fig, "s62_ex03.png")


def s62_ex04():
    fig, ax = plt.subplots(figsize=(6, 3.6), dpi=150)
    p0, p1 = np.array([0, 0]), np.array([12, 0])
    p3 = np.array([1.8, 5])
    p2 = p1 + (p3 - p0)
    ax.add_patch(Polygon(np.vstack([p0, p1, p2, p3]), closed=True, fill=False, lw=2, edgecolor="#1565C0"))
    ax.plot([p3[0], p3[0]], [0, p3[1]], "k--", lw=1, alpha=0.7)
    ax.text(6, -0.4, "12 dm", ha="center", fontsize=11)
    ax.text(2.1, 2.3, "5 dm", fontsize=10, rotation=90)
    ax.set_xlim(-0.5, 13.5)
    ax.set_ylim(-0.7, 5.8)
    off(ax)
    _save(fig, "s62_ex04.png")


def s62_ex05():
    fig, ax = plt.subplots(figsize=(4.2, 4.2), dpi=150)
    ax.add_patch(Circle((0, 0), 7, fill=False, lw=2, edgecolor="#1565C0"))
    ax.plot([0, 7], [0, 0], "k-", lw=1.2)
    ax.text(3.2, 0.25, r"$r = 7$ cm", fontsize=11)
    ax.set_xlim(-8.5, 8.5)
    ax.set_ylim(-8.5, 8.5)
    off(ax)
    _save(fig, "s62_ex05.png")


def s62_ex06():
    fig, ax = plt.subplots(figsize=(6, 3.8), dpi=150)
    b1, b2, h = 10, 6, 4
    offx = (b1 - b2) / 2
    xs = [0, b1, b1 - offx, offx, 0]
    ys = [0, 0, h, h, 0]
    ax.plot(xs, ys, "-", color="#1565C0", lw=2)
    ax.text(b1 / 2, -0.35, "10 m", ha="center", fontsize=10)
    ax.text(offx + b2 / 2, h + 0.15, "6 m", ha="center", fontsize=10)
    ax.text(-0.35, h / 2, "4 m", va="center", fontsize=10, rotation=90)
    ax.set_xlim(-0.8, 11)
    ax.set_ylim(-0.7, 4.8)
    off(ax)
    _save(fig, "s62_ex06.png")


def s62_ex07():
    fig, ax = plt.subplots(figsize=(5, 5), dpi=150)
    d1, d2 = 6, 8
    pts = np.array([[0, d2 / 2], [d1 / 2, 0], [0, -d2 / 2], [-d1 / 2, 0]])
    ax.add_patch(Polygon(pts, closed=True, fill=False, lw=2, edgecolor="#1565C0"))
    ax.plot([-d1 / 2, d1 / 2], [0, 0], "k--", lw=1, alpha=0.6)
    ax.plot([0, 0], [-d2 / 2, d2 / 2], "k--", lw=1, alpha=0.6)
    ax.text(0, d2 / 2 + 0.35, "6 cm", ha="center", fontsize=10)
    ax.text(d1 / 2 + 0.35, 0, "8 cm", va="center", fontsize=10)
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    off(ax)
    _save(fig, "s62_ex07.png")


def s62_ex08():
    fig, ax = plt.subplots(figsize=(6.5, 3.6), dpi=150)
    ax.add_patch(Rectangle((0, 0), 15, 8, fill=False, lw=2, edgecolor="#1565C0"))
    ax.text(7.5, -0.45, "15 cm", ha="center", fontsize=11)
    ax.text(-0.5, 4, "8 cm", ha="center", va="center", fontsize=11, rotation=90)
    ax.set_xlim(-1, 16)
    ax.set_ylim(-0.8, 9)
    off(ax)
    _save(fig, "s62_ex08.png")


def s62_ex11():
    fig, ax = plt.subplots(figsize=(6.5, 3.2), dpi=150)
    ax.add_patch(Rectangle((0, 0), 3, 3, fill=False, lw=2, edgecolor="#1565C0"))
    ax.add_patch(Rectangle((3, 0), 3, 3, fill=False, lw=2, edgecolor="#1565C0"))
    ax.text(1.5, -0.35, "3 cm", ha="center", fontsize=10)
    ax.text(4.5, -0.35, "3 cm", ha="center", fontsize=10)
    ax.set_xlim(-0.3, 6.6)
    ax.set_ylim(-0.7, 3.5)
    off(ax)
    _save(fig, "s62_ex11.png")


def s62_ex12():
    fig, ax = plt.subplots(figsize=(7.5, 3.8), dpi=150)
    ax.add_patch(Rectangle((0, 0), 20, 9, fill=False, lw=2, edgecolor="#1565C0"))
    ax.axhline(4.5, color="#E65100", lw=1.8, linestyle="--")
    ax.text(10, -0.55, "20 m", ha="center", fontsize=11)
    ax.text(-0.55, 4.5, "9 m", ha="center", va="center", fontsize=11, rotation=90)
    ax.text(10, 4.7, "cut // to length 20", ha="center", fontsize=9, color="#E65100")
    ax.set_xlim(-1, 21)
    ax.set_ylim(-0.9, 10)
    off(ax)
    _save(fig, "s62_ex12.png")


def s62_ex13():
    fig, ax = plt.subplots(figsize=(4.8, 3.6), dpi=150)
    ax.plot([0, 12, 12, 0], [0, 0, 5, 0], "-", color="#1565C0", lw=2)
    ax.plot([12, 12], [0, 0.2], "k-", lw=1)
    ax.plot([11.8, 12], [0, 0], "k-", lw=1)
    ax.text(6, -0.35, "12 cm", ha="center", fontsize=11)
    ax.text(12.35, 2.3, "5 cm", fontsize=11, rotation=90)
    ax.set_xlim(-0.5, 13.2)
    ax.set_ylim(-0.6, 5.6)
    off(ax)
    _save(fig, "s62_ex13.png")


def s62_ex14():
    fig, ax = plt.subplots(figsize=(6.5, 3.2), dpi=150)
    ax.add_patch(Rectangle((0, 0), 14, 5, fill=False, lw=2, edgecolor="#1565C0"))
    ax.add_patch(Rectangle((5, 1.5), 2, 2, fill=True, facecolor="#E3F2FD", edgecolor="#0D47A1", lw=1.5))
    ax.text(7, -0.4, "14 cm", ha="center", fontsize=10)
    ax.text(-0.45, 2.5, "5 cm", ha="center", va="center", fontsize=10, rotation=90)
    ax.set_xlim(-0.8, 15)
    ax.set_ylim(-0.7, 5.8)
    off(ax)
    _save(fig, "s62_ex14.png")


def s62_ex15():
    fig, ax = plt.subplots(figsize=(6, 3.6), dpi=150)
    p0, p1 = np.array([0, 0]), np.array([10, 0])
    p3 = np.array([1.5, 4.5])
    p2 = p1 + (p3 - p0)
    ax.add_patch(Polygon(np.vstack([p0, p1, p2, p3]), closed=True, fill=False, lw=2, edgecolor="#1565C0"))
    ax.plot([p3[0], p3[0]], [0, p3[1]], "k--", lw=1, alpha=0.7)
    ax.text(5, -0.4, "10 cm", ha="center", fontsize=11)
    ax.text(1.75, 2.1, "h = ?", fontsize=10, rotation=90)
    ax.text(8, 2.5, r"$A = 70$ cm$^2$", fontsize=10)
    ax.set_xlim(-0.5, 11.5)
    ax.set_ylim(-0.7, 5.2)
    off(ax)
    _save(fig, "s62_ex15.png")


def s62_ex16():
    fig, ax = plt.subplots(figsize=(7.5, 5), dpi=150)
    ax.add_patch(Rectangle((0, 0), 30, 18, fill=False, lw=2, edgecolor="#1565C0"))
    ax.add_patch(Circle((15, 9), 3, fill=True, facecolor="#BBDEFB", edgecolor="#1565C0", lw=1.5))
    ax.text(15, -0.9, "30 m", ha="center", fontsize=11)
    ax.text(-0.9, 9, "18 m", ha="center", va="center", fontsize=11, rotation=90)
    ax.text(15, 9, r"$r = 3$ m", ha="center", va="center", fontsize=10)
    ax.set_xlim(-2, 32)
    ax.set_ylim(-1.5, 20)
    off(ax)
    _save(fig, "s62_ex16.png")


def s62_ex17():
    fig, ax = plt.subplots(figsize=(7, 3.6), dpi=150)
    xs = [0, 12, 12, 10, 10, 0, 0]
    ys = [0, 0, 5, 5, 3, 3, 0]
    ax.plot(xs, ys, "-", color="#1565C0", lw=2)
    ax.text(6, -0.4, "12 cm", ha="center", fontsize=10)
    ax.text(-0.4, 2.5, "5 cm", ha="center", va="center", fontsize=10, rotation=90)
    ax.text(11.25, 4.1, "2 cm", fontsize=9, rotation=90)
    ax.set_xlim(-0.8, 13)
    ax.set_ylim(-0.7, 5.6)
    off(ax)
    _save(fig, "s62_ex17.png")


def s62_ex18():
    fig, ax = plt.subplots(figsize=(5.5, 5.5), dpi=150)
    ax.add_patch(Rectangle((0, 0), 10, 10, fill=False, lw=2.5, edgecolor="#1565C0"))
    ax.add_patch(Rectangle((1, 1), 8, 8, fill=False, lw=1.8, edgecolor="#E65100", linestyle="--"))
    ax.text(5, -0.45, r"$a = 10$ m", ha="center", fontsize=11)
    ax.text(0.5, 5, r"$w = 1$ m", fontsize=9, rotation=90, va="center")
    ax.set_xlim(-0.8, 10.8)
    ax.set_ylim(-0.8, 10.8)
    off(ax)
    _save(fig, "s62_ex18.png")


def s62_ex19():
    fig, ax = plt.subplots(figsize=(8, 3.6), dpi=150)
    ax.add_patch(Rectangle((0, 0), 20, 7, fill=False, lw=2, edgecolor="#1565C0"))
    ax.add_patch(Rectangle((-7, 0), 7, 7, fill=False, lw=2, edgecolor="#2E7D32"))
    ax.plot([0, 0], [0, 7], "k:", lw=1.2, alpha=0.7)
    ax.text(10, -0.45, "13 cm total", ha="center", fontsize=9)
    ax.text(-3.5, -0.45, "7 cm", ha="center", fontsize=10)
    ax.text(10, 3.5, "7 cm", ha="center", fontsize=10)
    ax.set_xlim(-8, 21)
    ax.set_ylim(-0.8, 8)
    off(ax)
    _save(fig, "s62_ex19.png")


def s62_ex20():
    fig, ax = plt.subplots(figsize=(5.5, 4.2), dpi=150)
    ax.plot([0, 10, 5, 0], [0, 0, 7.2, 0], "-", color="#1565C0", lw=2)
    ax.plot([5, 5], [0, 7.2], "k--", lw=1.2, alpha=0.8)
    ax.text(5, -0.35, "10 cm", ha="center", fontsize=11)
    ax.text(2.3, 4.2, "13 cm", fontsize=10, rotation=72)
    ax.text(6.0, 4.2, "13 cm", fontsize=10, rotation=-72)
    ax.text(5.35, 3.4, "h", fontsize=11)
    ax.set_xlim(-0.8, 10.8)
    ax.set_ylim(-0.6, 8.2)
    off(ax)
    _save(fig, "s62_ex20.png")


def coord(fname, points=None, polygon=None, segments=None, xlim=None, ylim=None, ann=None):
    fig, ax = plt.subplots(figsize=(5.2, 5.2), dpi=150)
    ax.axhline(0, color="gray", lw=0.8)
    ax.axvline(0, color="gray", lw=0.8)
    ax.grid(True, alpha=0.35)
    ax.set_aspect("equal")
    if polygon is not None:
        ax.add_patch(Polygon(np.array(polygon), closed=True, fill=False, lw=2, edgecolor="#1565C0"))
    if segments:
        for a, b in segments:
            ax.plot([a[0], b[0]], [a[1], b[1]], "o-", color="#1565C0", ms=7, lw=1.8)
    if points:
        for p in points:
            ax.plot(p[0], p[1], "o", color="#1565C0", ms=8)
    if ann:
        for (x, y), lab in ann:
            ax.annotate(lab, (x, y), textcoords="offset points", xytext=(6, 6), fontsize=10)
    if xlim:
        ax.set_xlim(xlim)
    if ylim:
        ax.set_ylim(ylim)
    ax.set_xlabel("x", fontsize=11)
    ax.set_ylabel("y", fontsize=11)
    _save(fig, fname)


def gen_s63():
    coord("s63_ex01.png", points=[(4, -3)], xlim=(-1, 6), ylim=(-5, 2), ann=[((4, -3), "(4, -3)")])
    coord("s63_ex02.png", segments=[((-2, 5), (7, 5))], xlim=(-4, 9), ylim=(2, 8), ann=[((-2, 5), "(-2, 5)"), ((7, 5), "(7, 5)")])
    coord("s63_ex03.png", segments=[((1, 6), (1, -2))], xlim=(-2, 4), ylim=(-4, 8), ann=[((1, 6), "(1, 6)"), ((1, -2), "(1, -2)")])
    coord("s63_ex04.png", polygon=[(0, 0), (5, 0), (5, 3), (0, 3)], xlim=(-1, 6), ylim=(-1, 4))
    coord("s63_ex05.png", points=[(3, 8)], xlim=(-1, 5), ylim=(0, 10), ann=[((3, 8), "A")])
    coord("s63_ex06.png", polygon=[(2, 1), (10, 1), (10, 6), (2, 6)], xlim=(0, 12), ylim=(0, 8))
    coord("s63_ex07.png", segments=[((4, 2), (4, 9))], xlim=(1, 6), ylim=(0, 11), ann=[((4, 2), "(4, 2)"), ((4, 9), "(4, 9)")])
    coord("s63_ex08.png", points=[(1, 1), (4, 5)], xlim=(-1, 6), ylim=(-1, 7), ann=[((1, 1), "(1, 1)"), ((4, 5), "(4, 5)")])
    coord("s63_ex09.png", polygon=[(-1, 2), (3, 2), (3, 9), (-1, 9)], xlim=(-3, 5), ylim=(0, 11))
    coord("s63_ex10.png", polygon=[(0, 0), (8, 0), (0, 6)], xlim=(-1, 9), ylim=(-1, 7))
    coord("s63_ex11.png", polygon=[(2, 1), (10, 1), (10, 6), (2, 6)], xlim=(0, 12), ylim=(0, 8))
    fig, ax = plt.subplots(figsize=(5.2, 5.2), dpi=150)
    ax.axhline(0, color="gray", lw=0.8)
    ax.axvline(0, color="gray", lw=0.8)
    ax.grid(True, alpha=0.35)
    ax.set_aspect("equal")
    ax.add_patch(Rectangle((1, 1), 6, 4, fill=False, lw=2, edgecolor="#1565C0"))
    ax.text(4, 0.3, "6", ha="center", fontsize=10)
    ax.text(0.3, 3, "4", ha="center", fontsize=10, rotation=90)
    ax.set_xlim(0, 9)
    ax.set_ylim(0, 7)
    ax.set_xlabel("x", fontsize=11)
    ax.set_ylabel("y", fontsize=11)
    _save(fig, "s63_ex12.png")
    coord("s63_ex13.png", points=[(7, 1), (-3, 1)], xlim=(-5, 9), ylim=(-1, 4), ann=[((7, 1), "(7, 1)"), ((-3, 1), "(-3, 1)")])
    coord("s63_ex14.png", polygon=[(1, 2), (9, 2), (9, 7), (1, 7)], xlim=(0, 11), ylim=(0, 9))
    coord("s63_ex15.png", polygon=[(0, 0), (4, 0), (0, 3)], xlim=(-1, 5), ylim=(-1, 4))
    coord("s63_ex16.png", polygon=[(0, 0), (6, 0), (6, 8), (0, 8)], xlim=(-1, 8), ylim=(-1, 10))
    coord("s63_ex17.png", points=[(5, 3), (5, -5)], xlim=(2, 8), ylim=(-7, 6), ann=[((5, -1), "(5,-1)")])
    coord(
        "s63_ex18.png",
        points=[(2, 3), (8, 9), (-4, 9), (2, -3)],
        xlim=(-6, 10),
        ylim=(-5, 11),
        ann=[((2, 3), "(2, 3)")],
    )
    coord("s63_ex19.png", polygon=[(0, 0), (6, 0), (6, 4), (0, 4)], xlim=(-1, 8), ylim=(-1, 6))
    coord("s63_ex20.png", polygon=[(1, 1), (5, 1), (5, 4), (1, 4)], xlim=(0, 6.5), ylim=(0, 5))
    fig, ax = plt.subplots(figsize=(5.2, 4), dpi=150)
    ax.axhline(0, color="gray", lw=0.8)
    ax.axvline(0, color="gray", lw=0.8)
    ax.grid(True, alpha=0.35)
    ax.set_aspect("equal")
    ax.plot([1, 5], [1, 1], "o-", color="#1565C0", lw=2, ms=8)
    ax.plot(11 / 3, 1, "s", color="#E65100", ms=10)
    ax.annotate("Q", (11 / 3, 1), textcoords="offset points", xytext=(0, -16), ha="center", fontsize=11)
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 3)
    ax.set_xlabel("x", fontsize=11)
    ax.set_ylabel("y", fontsize=11)
    _save(fig, "s63_ex20_detail.png")


def main():
    for f in (
        s61_ex01,
        s61_ex05,
        s61_ex06,
        s61_ex10,
        s61_ex15,
        s61_ex19,
        s62_ex01,
        s62_ex02,
        s62_ex03,
        s62_ex04,
        s62_ex05,
        s62_ex06,
        s62_ex07,
        s62_ex08,
        s62_ex11,
        s62_ex12,
        s62_ex13,
        s62_ex14,
        s62_ex15,
        s62_ex16,
        s62_ex17,
        s62_ex18,
        s62_ex19,
        s62_ex20,
    ):
        f()
    gen_s63()
    print("OK ->", OUT)


if __name__ == "__main__":
    main()
