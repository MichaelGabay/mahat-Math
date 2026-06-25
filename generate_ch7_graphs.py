#!/usr/bin/env python3
"""Generate coordinate-plane graphs for Chapter 7 (Analytical Geometry) MAHAT Math exercises."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

CHAPTER_DIR = "/Users/amitay/Desktop/ort - math/mahat-Math/7 - \u05d4\u05e0\u05d3\u05e1\u05d4 \u05d0\u05e0\u05dc\u05d9\u05d8\u05d9\u05ea"
IMAGES_DIR = os.path.join(CHAPTER_DIR, "images")
os.makedirs(IMAGES_DIR, exist_ok=True)

plt.rcParams['font.family'] = ['Arial Hebrew', 'Arial Unicode MS', 'Arial', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

C1 = '#2166AC'   # Line 1: blue
C2 = '#D6604D'   # Line 2: orange-red
C3 = '#4DAC26'   # Line 3: green
C4 = '#6A0DAD'   # Line 4: purple
CP = '#E31A1C'   # Points: red
CI = '#33A02C'   # Intersection / midpoint: green
CF = '#AED6F1'   # Shape fill: light blue


# ── Helpers ────────────────────────────────────────────────────────────────

def make_fig(xlim=(-8, 8), ylim=(-8, 8)):
    """Coordinate plane with axes through origin.

    When 0 is not inside a limit (real-world graphs that start far from the
    origin) the corresponding spine is kept at the panel edge instead of being
    placed at zero, so the data is not squeezed into a thin strip.
    """
    fig, ax = plt.subplots(figsize=(6, 6), facecolor='white')
    ax.set_facecolor('white')
    x_axis_at_zero = ylim[0] <= 0 <= ylim[1]   # horizontal axis y=0 visible
    y_axis_at_zero = xlim[0] <= 0 <= xlim[1]    # vertical axis x=0 visible
    if x_axis_at_zero:
        ax.spines['bottom'].set_position('zero')
    if y_axis_at_zero:
        ax.spines['left'].set_position('zero')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_linewidth(1.5)
    ax.spines['bottom'].set_linewidth(1.5)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.grid(True, alpha=0.25, linestyle='--', color='gray')
    xr = xlim[1] - xlim[0]
    yr = ylim[1] - ylim[0]
    sx = max(1, round(xr / 12))
    sy = max(1, round(yr / 12))
    xt = [i for i in range(int(np.ceil(xlim[0])), int(np.floor(xlim[1])) + 1, sx) if i != 0]
    yt = [i for i in range(int(np.ceil(ylim[0])), int(np.floor(ylim[1])) + 1, sy) if i != 0]
    ax.set_xticks(xt)
    ax.set_yticks(yt)
    ax.tick_params(labelsize=7)
    y_lbl = 0 if x_axis_at_zero else ylim[0]
    x_lbl = 0 if y_axis_at_zero else xlim[0]
    ax.text(xlim[1] + xr * 0.025, y_lbl, 'x', fontsize=10, ha='left', va='center')
    ax.text(x_lbl + xr * 0.015, ylim[1], 'y', fontsize=10, ha='left', va='top')
    return fig, ax


def save(fig, name):
    path = os.path.join(IMAGES_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)


def dline(ax, m, b, xlim, color=C1, lw=2, label=None):
    """Draw y = mx + b."""
    x = np.linspace(xlim[0] - 0.5, xlim[1] + 0.5, 500)
    y = m * x + b
    ax.plot(x, y, color=color, linewidth=lw, zorder=2)
    if label:
        ylim_c = ax.get_ylim()
        yr = ylim_c[1] - ylim_c[0]
        for frac in [0.65, 0.80, 0.45, 0.25]:
            lx = xlim[0] + frac * (xlim[1] - xlim[0])
            ly = m * lx + b
            if ylim_c[0] + yr * 0.05 < ly < ylim_c[1] - yr * 0.1:
                ax.text(lx, ly + yr * 0.035, label, color=color, fontsize=7, zorder=6,
                        bbox=dict(facecolor='white', alpha=0.6, edgecolor='none', pad=1))
                break


def dpt(ax, x, y, lbl='', color=CP, size=7, dx=0.15, dy=0.15):
    """Draw a labeled point."""
    ax.plot(x, y, 'o', color=color, markersize=size, zorder=5)
    if lbl:
        ax.text(x + dx, y + dy, lbl, fontsize=8, color='black', fontweight='bold', zorder=6)


def dpoly(ax, pts, fcolor=CF, ecolor='black', alpha=0.15, lw=2):
    """Draw filled polygon."""
    poly = mpatches.Polygon(pts, closed=True, facecolor=fcolor, edgecolor=ecolor,
                            alpha=alpha, linewidth=lw, zorder=2)
    ax.add_patch(poly)
    xs = [p[0] for p in pts] + [pts[0][0]]
    ys = [p[1] for p in pts] + [pts[0][1]]
    ax.plot(xs, ys, color=ecolor, linewidth=lw, zorder=3)


def right_angle(ax, corner, d1, d2, size=0.3):
    """Draw right-angle square marker."""
    c = np.array(corner, dtype=float)
    v1 = np.array(d1, dtype=float); v1 = v1 / np.linalg.norm(v1) * size
    v2 = np.array(d2, dtype=float); v2 = v2 / np.linalg.norm(v2) * size
    sq = mpatches.Polygon([c, c + v1, c + v1 + v2, c + v2], closed=True,
                          fill=False, edgecolor='black', linewidth=1.2, zorder=4)
    ax.add_patch(sq)


def triangle_shape(ax, pts, fcolor=CF, labels=None, label_off=None):
    """Draw triangle with optional vertex labels."""
    dpoly(ax, pts, fcolor=fcolor, alpha=0.15)
    if labels:
        offs = label_off or [(0.15, 0.15)] * len(pts)
        for (x, y), lbl, (dx, dy) in zip(pts, labels, offs):
            dpt(ax, x, y, lbl, dx=dx, dy=dy)


# ════════════════════════════════════════════════════════════════════════════
#  FILE 1 — Point plotting  (exercises 1–20)
# ════════════════════════════════════════════════════════════════════════════

def _f1_simple(n, pts_data, xlim=(-7, 7), ylim=(-6, 8),
               extra_lines=None, shape=None, connect=False):
    fig, ax = make_fig(xlim, ylim)
    if extra_lines:
        for (m, b) in extra_lines:
            dline(ax, m, b, xlim, color=C1, lw=1.2)
    if shape:
        dpoly(ax, shape)
    for (x, y, lbl, dx, dy) in pts_data:
        dpt(ax, x, y, lbl, dx=dx, dy=dy)
    if connect:
        xs = [p[0] for p in pts_data] + [pts_data[0][0]]
        ys = [p[1] for p in pts_data] + [pts_data[0][1]]
        ax.plot(xs, ys, 'b-', lw=1.5, zorder=2)
    save(fig, f'7_1_ex{n:02d}.png')

_f1_simple(1,  [(3, 5, 'A(3,5)', .15, .15)])
_f1_simple(2,  [(-2, 4, 'B(-2,4)', .15, .15)])
_f1_simple(3,  [(-3, -1, 'C(-3,-1)', .15, .15)])
_f1_simple(4,  [(4, -2, 'D(4,-2)', .15, .15)])
_f1_simple(5,  [(0, 6, 'E(0,6)', .15, .15)])
_f1_simple(6,  [(3, 4, 'F(3,4)', .15, .15)])
_f1_simple(7,  [(5, 0, 'F(5,0)', .15, -.4)])
_f1_simple(8,  [(0, 0, 'O(0,0)', .15, .15)])
_f1_simple(9,  [(-0.5, 3, 'P(-0.5,3)', .15, .15), (1.5, -1, 'Q(1.5,-1)', .15, .15)],
           xlim=(-4, 4), ylim=(-3, 5))
_f1_simple(10, [(2, 5, 'A(2,5)', .15, .15), (2, -3, 'B(2,-3)', .15, .15)],
           xlim=(-3, 6), ylim=(-5, 7))
_f1_simple(11, [(-4, 1, 'C(-4,1)', .15, .15), (3, 1, 'D(3,1)', .15, .15)],
           xlim=(-6, 5), ylim=(-2, 4))
_f1_simple(12, [(-2, -5, 'G(-2,-5) ← Q3', .15, .15)],
           xlim=(-6, 4), ylim=(-7, 3))
_f1_simple(13, [(0, 3, 'H(0,3)', .15, .15)],
           xlim=(-4, 4), ylim=(-2, 6))
_f1_simple(14, [(5, 0, 'K(5,0)', .15, -.4)],
           xlim=(-2, 8), ylim=(-3, 4))
_f1_simple(15, [(-2.5, -3.5, 'M(-2.5,-3.5)', .15, .15)],
           xlim=(-6, 4), ylim=(-6, 2))
_f1_simple(16, [(-3, 0, 'A(-3,0)', .15, .15), (0, -3, 'B(0,-3)', .15, .15)],
           xlim=(-6, 4), ylim=(-6, 3))

# Ex 17: Rectangle A(-2,-1),B(4,-1),C(4,3),D(-2,3)
def _f1_17():
    fig, ax = make_fig((-4, 6), (-3, 5))
    pts = [(-2, -1), (4, -1), (4, 3), (-2, 3)]
    dpoly(ax, pts)
    for (x, y), lbl, (dx, dy) in zip(pts,
            ['A(-2,-1)', 'B(4,-1)', 'C(4,3)', 'D(-2,3)'],
            [(.1, -.4), (.1, -.4), (.1, .15), (-1.5, .15)]):
        dpt(ax, x, y, lbl, dx=dx, dy=dy)
    save(fig, '7_1_ex17.png')
_f1_17()

# Ex 18: Stations A(0,6), B(8,6), C(8,0)
def _f1_18():
    fig, ax = make_fig((-1, 11), (-1, 9))
    pts_d = [(0, 6, 'A(0,6)', .15, .15), (8, 6, 'B(8,6)', .15, .15), (8, 0, 'C(8,0)', .15, -.4)]
    for (x, y, lbl, dx, dy) in pts_d:
        dpt(ax, x, y, lbl, dx=dx, dy=dy)
    ax.plot([0, 8, 8], [6, 6, 0], 'b-', lw=2, zorder=2)
    save(fig, '7_1_ex18.png')
_f1_18()

# Ex 19: Rectangle PQRS
def _f1_19():
    fig, ax = make_fig((-5, 7), (-6, 4))
    pts = [(-3, 2), (5, 2), (5, -4), (-3, -4)]
    dpoly(ax, pts)
    for (x, y), lbl, (dx, dy) in zip(pts,
            ['P(-3,2)', 'Q(5,2)', 'R(5,-4)', 'S(-3,-4)'],
            [(-.4, .15), (.15, .15), (.15, -.45), (-.4, -.45)]):
        dpt(ax, x, y, lbl, dx=dx, dy=dy)
    save(fig, '7_1_ex19.png')
_f1_19()

# Ex 20: Rectangle ABCD A(1,1)..D(1,5)
def _f1_20():
    fig, ax = make_fig((-1, 10), (-1, 7))
    pts = [(1, 1), (7, 1), (7, 5), (1, 5)]
    dpoly(ax, pts)
    for (x, y), lbl, (dx, dy) in zip(pts,
            ['A(1,1)', 'B(7,1)', 'C(7,5)', 'D(1,5)'],
            [(.1, -.4), (.1, -.4), (.1, .15), (-1.5, .15)]):
        dpt(ax, x, y, lbl, dx=dx, dy=dy)
    ax.plot([1, 7], [1, 5], 'g--', lw=1.2)
    dpt(ax, 4, 1, 'E(4,1)', color='blue', size=6, dy=-.4)
    save(fig, '7_1_ex20.png')
_f1_20()
print("File 1: 20 images done")


# ════════════════════════════════════════════════════════════════════════════
#  FILE 4 — Line identification  (exercises 1–20)
# ════════════════════════════════════════════════════════════════════════════

def _f4(n, lines, pts=None, xlim=(-7, 7), ylim=(-7, 9)):
    fig, ax = make_fig(xlim, ylim)
    for i, (m, b, lbl) in enumerate(lines):
        dline(ax, m, b, xlim, color=[C1, C2, C3][i % 3], lw=2, label=lbl)
    if pts:
        for (x, y, lbl, dx, dy) in pts:
            dpt(ax, x, y, lbl, dx=dx, dy=dy)
    save(fig, f'7_4_ex{n:02d}.png')

_f4(1,  [(2, 1, 'y=2x+1')], [(0,1,'(0,1)',.15,.15),(2,5,'(2,5)',.15,.15)])
_f4(2,  [(-1, 5, 'y=-x+5')], [(0,5,'(0,5)',.15,.15),(4,1,'(4,1)',.15,.15)])
_f4(3,  [(3, -2, 'y=3x-2')], [(2,4,'A(2,4)\u2713',.15,.15)],
    xlim=(-2, 5), ylim=(-5, 13))
_f4(4,  [(-2, 6, 'y=-2x+6')], [(3,0,'A(3,0)\u2713',.15,.15)])
_f4(5,  [(4, 0, 'y=4x')], [(0,0,'O(0,0)',.15,.15),(1,4,'(1,4)',.15,.15)])
_f4(6,  [(1, 3, 'y=x+3')], [(-2,1,'x=-2 \u2192 y=1',.15,.15)])
_f4(7,  [(5, -10, 'y=5x-10')], [(2,0,'(2,0)\u2713',.15,-.4)],
    xlim=(-1, 5), ylim=(-12, 8))
_f4(8,  [(0.5, 4, 'y=0.5x+4')], [(6,7,'x=6\u2192y=7',.15,.15)])
_f4(9,  [(-3, 7, 'y=-3x+7')], [(-2,13,'(-2,13)\u2713',.15,.15)],
    xlim=(-4, 4), ylim=(-2, 16))
_f4(10, [(2/3, -1, 'y=(2/3)x-1')], [(-3,-3,'x=-3\u2192y=-3',.15,.15)])
_f4(11, [(2, -4, 'y=2x-4')], [(5,6,'(5,6)',.15,.15)],
    xlim=(-2, 7), ylim=(-6, 8))
_f4(12, [(-4, 12, 'y=-4x+12')], [(5,-8,'(5,-8)',.15,.15)],
    xlim=(-1, 7), ylim=(-10, 14))
_f4(13, [(1/3, 2, 'y=(1/3)x+2')], [(-6,0,'(-6,0)\u2713',.15,.15)],
    xlim=(-8, 4), ylim=(-2, 6))
_f4(14, [(3, -1, 'y=3x-1')], [(2,5,'(2,5), k=2',.15,.15)])
_f4(15, [(-0.5, 3, 'y=-0.5x+3')], [(4,1,'(4,1), m=1',.15,.15)])
_f4(16, [(2, -5, 'y=2x-5')],
    [(1,-3,'A\u2713',-.3,-.4),(3,1,'B\u2713',.15,.15),
     (-1,-7,'C\u2713',.15,.15),(0,-4,'D\u2717',.15,-.4)])
# Ex 17: two parallel lines
def _f4_17():
    fig, ax = make_fig((-3, 7), (-3, 16))
    dline(ax, 2, 1, (-3, 7), color=C1, label='\u2113\u2081: y=2x+1')
    dline(ax, 2, 5, (-3, 7), color=C2, label='\u2113\u2082: y=2x+5')
    save(fig, '7_4_ex17.png')
_f4_17()
# Ex 18: two intersecting lines at (1.75, 7.5)
def _f4_18():
    fig, ax = make_fig((-1, 5), (0, 13))
    dline(ax, 2, 4, (-1, 5), color=C1, label='\u2113_a: y=2x+4')
    dline(ax, -2, 11, (-1, 5), color=C2, label='\u2113_b: y=-2x+11')
    dpt(ax, 1.75, 7.5, 'P(1.75,7.5)', color=CI)
    save(fig, '7_4_ex18.png')
_f4_18()
_f4(19, [(3, -1, 'y=3x-1')], [(2,8,'P(2,8)',.15,.15),(2,5,'Q(2,5)',.15,-.5)],
    xlim=(-2, 5), ylim=(-5, 12))
def _f4_20():
    fig, ax = make_fig((-4, 6), (-7, 9))
    dline(ax, -2, 3, (-4, 6), color=C1, label='y=-2x+3')
    dpt(ax, -2, 7, 'E(-2,7)', dx=.15, dy=.15)
    dpt(ax, 4, -5, 'F(4,-5)', dx=.15, dy=.15)
    dpt(ax, 0, 3, '(0,3)', color='purple', dx=.15, dy=.15)
    dpt(ax, 1.5, 0, '(1.5,0)', color='purple', dx=.15, dy=-.4)
    save(fig, '7_4_ex20.png')
_f4_20()
print("File 4: 20 images done")


# ════════════════════════════════════════════════════════════════════════════
#  FILE 5 — Line from table  (exercises 1–20)
# ════════════════════════════════════════════════════════════════════════════

def _f5(n, m, b, table_x, xlim=(-5, 6), ylim=(-7, 8),
        extra=None, lbl=None):
    fig, ax = make_fig(xlim, ylim)
    l = lbl or (f'y={m}x+{b}' if b >= 0 else f'y={m}x{b}')
    dline(ax, m, b, xlim, color=C1, label=l)
    if extra:
        for em, eb, el in extra:
            dline(ax, em, eb, xlim, color=C2, label=el)
    for x in table_x:
        y = m * x + b
        dpt(ax, x, y, f'({x:.4g},{y:.4g})', size=5)
    save(fig, f'7_5_ex{n:02d}.png')

_f5(1, 2, 1, [-2,-1,0,1,2])
_f5(2, 1, -3, [0,1,2,3,4])
_f5(3, -1, 4, [-1,0,1,2,3])
_f5(4, 3, 0, [-2,-1,0,1,2], ylim=(-7,8))
_f5(5, -2, 5, [0,1,2,3,4])
def _f5_6():
    fig, ax = make_fig((-4, 4), (-2, 7))
    dline(ax, 0, 4, (-4, 4), color=C1, label='y=4')
    for x in [-2,-1,0,1,2]:
        dpt(ax, x, 4, f'({x},4)', size=5)
    save(fig, '7_5_ex06.png')
_f5_6()
_f5(7, 1, 1, [-3,-1,0,2,5], xlim=(-5,7), ylim=(-3,8))
_f5(8, -3, 6, [-1,0,1,2,3], ylim=(-4,11))
_f5(9, 0.5, -3, [-4,-2,0,2,4], xlim=(-6,6), ylim=(-6,2))
_f5(10, -2/3, 2, [-3,0,3,6,9], xlim=(-4,11), ylim=(-5,6))
_f5(11, 1.5, -4.5, [-2,0,1,3,5], xlim=(-3,7), ylim=(-8,4))
_f5(12, 2, -6, [0,3,5], xlim=(-2,7), ylim=(-7,6))
def _f5_13():
    fig, ax = make_fig((-3, 4), (-5, 9))
    dline(ax, 3, -1, (-3, 4), color=C1, label='f(x)=3x-1')
    dline(ax, -3, 5, (-3, 4), color=C2, label='g(x)=-3x+5')
    for x in [-1,0,1,2]:
        dpt(ax, x, 3*x-1, f'f({x})={3*x-1}', color=C1, size=5, dy=-.4)
        dpt(ax, x, -3*x+5, f'g({x})={-3*x+5}', color=C2, size=5, dy=.2)
    dpt(ax, 1, 2, 'x=1, y=2', color=CI, size=8)
    save(fig, '7_5_ex13.png')
_f5_13()
_f5(14, -2, 4, [0,1,2,3,4], lbl='y=-2x+4 (k=4)')
_f5(15, 0.75, 1, [-4,0,4,8], xlim=(-6,10), ylim=(-3,8))
_f5(16, 2, -2, [-2,0,2,4,6], xlim=(-3,8), ylim=(-7,11))
def _f5_17():
    fig, ax = make_fig((-1, 6), (-5, 7))
    dline(ax, 2, -4, (-1, 6), color=C1, label='\u2113\u2081: y=2x-4')
    dline(ax, -1, 5, (-1, 6), color=C2, label='\u2113\u2082: y=-x+5')
    for x in [0,1,2,3,4]:
        dpt(ax, x, 2*x-4, f'({x},{2*x-4})', color=C1, size=5, dy=-.4)
        dpt(ax, x, -x+5,  f'({x},{-x+5})',  color=C2, size=5, dy=.2)
    dpt(ax, 3, 2, 'P(3,2)', color=CI, size=8)
    save(fig, '7_5_ex17.png')
_f5_17()
def _f5_18():
    fig, ax = make_fig((-1, 10), (0, 32))
    ax.text(10.5, 0, 't', fontsize=10, ha='left', va='center')
    ax.text(.3, 32, 'V', fontsize=10, ha='left', va='top')
    dline(ax, 3, 6, (-1, 10), color=C1, label='V\u2081=3t+6')
    dline(ax, -1, 18, (-1, 10), color=C2, label='V\u2082=-t+18')
    for t in [0,2,4,6,8]:
        dpt(ax, t, 3*t+6, '', color=C1, size=4)
        dpt(ax, t, -t+18, '', color=C2, size=4)
    dpt(ax, 3, 15, 'P(3,15)', color=CI, size=8)
    save(fig, '7_5_ex18.png')
_f5_18()
_f5(19, 1, 3, [-4,-2,0,2,4], xlim=(-6,6), ylim=(-2,9))
def _f5_20():
    m20, b20 = -4/11, 2/11
    fig, ax = make_fig((-2, 10), (-4, 3))
    dline(ax, m20, b20, (-2, 10), color=C1, label='y=-4x/11+2/11')
    for x in [0,2,4,6,8]:
        dpt(ax, x, m20*x+b20, f'({x},{m20*x+b20:.2f})', size=5)
    save(fig, '7_5_ex20.png')
_f5_20()
print("File 5: 20 images done")


# ════════════════════════════════════════════════════════════════════════════
#  FILE 12 — Parallel lines  (exercises 1–20)
# ════════════════════════════════════════════════════════════════════════════

def _f12(n, lines, pts=None, xlim=(-7, 7), ylim=(-7, 9), poly=None):
    fig, ax = make_fig(xlim, ylim)
    clrs = [C1, C2, C3, C4]
    for i, (m, b, lbl) in enumerate(lines):
        dline(ax, m, b, xlim, color=clrs[i % 4], lw=2, label=lbl)
    if poly:
        dpoly(ax, poly)
    if pts:
        for (x, y, lbl, dx, dy, c) in pts:
            dpt(ax, x, y, lbl, color=c, dx=dx, dy=dy)
    save(fig, f'7_12_ex{n:02d}.png')

_f12(1,  [(3, 2, '\u2113\u2081:y=3x+2'), (3,-5,'\u2113\u2082:y=3x-5')])
_f12(2,  [(2, 1, 'y=2x+1'), (4, 1, 'y=4x+1')], xlim=(-4,4))
_f12(3,  [(5,-3,'y=5x-3'), (5,4,'y=5x+4 \u2225')])
_f12(4,  [(-2,7,'y=-2x+7'), (-2,0,'y=-2x \u2225')])
_f12(5,  [(0.5,3,'\u2113\u2081:y=0.5x+3'), (0.5,-1,'\u2113\u2082:y=0.5x-1')])
_f12(6,  [(4,-1,'y=4x-1'), (4,3,'y=4x+3 (k=4)')], xlim=(-3,3))
def _f12_7():
    fig, ax = make_fig((-5, 6), (3, 7))
    dline(ax, 0, 5, (-5, 6), color=C1, label='y=5')
    dpt(ax, 3, 5, '(3,5)')
    save(fig, '7_12_ex07.png')
_f12_7()
_f12(8,  [(1,0,'y=x'), (1,5,'y=x+5 \u2225')],
     pts=[(2,7,'(2,7)',.15,.15,CP)])
_f12(9,  [(2,3,'\u2113\u2081:y=2x+3'), (2,0.5,'\u2113\u2082:y=2x+0.5')], ylim=(-5,12))
_f12(10, [(-3,5,'\u2113\u2081:y=-3x+5'), (-2,-1/3,'\u2113\u2082:y=-2x-1/3')])
_f12(11, [(-3,2,'y=-3x+2'), (-3,5,'y=-3x+5 \u2225')],
     pts=[(2,-1,'A(2,-1)',.15,.15,CP)])
_f12(12, [(2/3,-4,'y=(2/3)x-4'), (2/3,3,'y=(2/3)x+3 \u2225')],
     pts=[(-3,1,'B(-3,1)',.15,.15,CP)])
def _f12_13():
    fig, ax = make_fig((-2, 7), (-1, 11))
    dline(ax, 1, 2, (-2,7), color=C1, label='AB: y=x+2')
    dline(ax, 1, 4, (-2,7), color=C2, label='CD: y=x+4')
    for (x,y,lbl,c) in [(0,2,'A',C1),(4,6,'B',C1),(1,5,'C',C2),(5,9,'D',C2)]:
        dpt(ax,x,y,lbl,color=c)
    save(fig, '7_12_ex13.png')
_f12_13()
def _f12_14():
    fig, ax = make_fig((-2, 6), (-2, 5))
    pts = [(0,0),(4,0),(4,3),(0,3)]
    dpoly(ax, pts)
    for (x,y),lbl,off in zip(pts,['A(0,0)','B(4,0)','C(4,3)','D(0,3)'],
                             [(.1,-.4),(.1,-.4),(.1,.15),(-1.5,.15)]):
        dpt(ax,x,y,lbl,dx=off[0],dy=off[1])
    ax.annotate('', xy=(2,.25), xytext=(2,-.05),
                arrowprops=dict(arrowstyle='->', color=C1, lw=1.5))
    ax.annotate('', xy=(2,3.25), xytext=(2,2.95),
                arrowprops=dict(arrowstyle='->', color=C1, lw=1.5))
    ax.text(2.2, .5, 'AB \u2225 DC', fontsize=8, color=C1)
    save(fig, '7_12_ex14.png')
_f12_14()
_f12(15, [(-1/3,1,'\u2113\u2081:y=-x/3+1'), (-1/3,3,'\u2113\u2082:y=-x/3+3')])
_f12(16, [(2,3,'\u2113\u2081:y=2x+3'), (2,5,'\u2113\u2082:y=2x+5')],
     pts=[(1,7,'(1,7)',.15,.15,CP)])
def _f12_17():
    fig, ax = make_fig((-2, 8), (-2, 7))
    pts = [(0,0),(4,2),(6,5),(2,3)]
    dpoly(ax, pts)
    dline(ax, 0.5, 0, (-2,8), color=C1, lw=1.2, label='AB: y=0.5x')
    dline(ax, 0.5, 2, (-2,8), color=C2, lw=1.2, label='DC: y=0.5x+2')
    for (x,y),lbl in zip(pts,['A(0,0)','B(4,2)','C(6,5)','D(2,3)']):
        dpt(ax,x,y,lbl,dx=.15,dy=.15)
    save(fig, '7_12_ex17.png')
_f12_17()
def _f12_18():
    fig, ax = make_fig((-2, 5), (-3, 13))
    dline(ax, 3,-1,(-2,5), color=C1, label='\u2113\u2081:y=3x-1')
    dline(ax, 3, 5,(-2,5), color=C1, lw=1.2, label='\u2113\u2082:y=3x+5')
    dline(ax, 2,-1,(-2,5), color=C2, label='\u2113\u2083:y=2x-1')
    dline(ax, 2, 5,(-2,5), color=C2, lw=1.2, label='\u2113\u2084:y=2x+5')
    for (x,y,lbl) in [(0,-1,'A(0,-1)'),(2,3,'B(2,3)'),(0,5,'(0,5)')]:
        dpt(ax,x,y,lbl)
    save(fig, '7_12_ex18.png')
_f12_18()
_f12(19, [(0.5,4,'\u05db\u05d1\u05d9\u05e9 \u05d0: y=0.5x+4'), (0.5,-2,'\u05db\u05d1\u05d9\u05e9 \u05d1: y=0.5x-2')])
def _f12_20():
    fig, ax = make_fig((-2, 6), (-6, 10))
    dline(ax, 2, 1, (-2,6), color=C1, label='\u2113\u2081:y=2x+1')
    dline(ax, 2,-2, (-2,6), color=C2, label='\u2113\u2082:y=2x-2')
    for (x,y,lbl,c) in [(1,3,'A(1,3)',C1),(3,7,'B(3,7)',C1),
                         (0,-2,'C(0,-2)',C2),(2,2,'D(2,k=2)',C2)]:
        dpt(ax,x,y,lbl,color=c)
    save(fig, '7_12_ex20.png')
_f12_20()
print("File 12: 20 images done")


# ════════════════════════════════════════════════════════════════════════════
#  FILE 13 — Perpendicular lines  (exercises 1–20)
# ════════════════════════════════════════════════════════════════════════════

def _f13(n, lines, pts=None, xlim=(-7,7), ylim=(-7,9), ra=None):
    fig, ax = make_fig(xlim, ylim)
    for i,(m,b,lbl) in enumerate(lines):
        dline(ax,m,b,xlim,color=[C1,C2,C3][i%3],lw=2,label=lbl)
    if pts:
        for (x,y,lbl,dx,dy,c) in pts:
            dpt(ax,x,y,lbl,color=c,dx=dx,dy=dy)
    if ra:
        right_angle(ax, ra[0], ra[1], ra[2],
                    size=ra[3] if len(ra) > 3 else 0.3)
    save(fig, f'7_13_ex{n:02d}.png')

_f13(1, [(2,3,'y=2x+3'),(-0.5,4,'y=-0.5x+4 (\u22a5)')],
     pts=[(0.4,3.8,'P',.15,.15,CI)], ra=((0.4,3.8),(1,2),(-2,1)))
_f13(2, [(3,1,'y=3x+1'),(3,-2,'y=3x-2 (\u2225, not \u22a5)')])
_f13(3, [(4,5,'y=4x+5'),(-0.25,6.5,'y=-x/4+6.5 (\u22a5)')], ylim=(-3,15))
_f13(4, [(-1/3,2,'y=-x/3+2'),(3,2,'y=3x+2 (\u22a5)')])
_f13(5, [(5,-1,'y=5x-1'),(-0.2,3,'y=-0.2x+3 (\u22a5)')],
     xlim=(-3,5), ylim=(-5,12))
_f13(6, [(-7,4,'y=-7x+4'),(1/7,3,'y=x/7+3 (\u22a5)')],
     xlim=(-2,3), ylim=(-10,12))
def _f13_7():
    fig, ax = make_fig((-6, 6), (-4, 6))
    dline(ax, 0, 2, (-6,6), color=C1, label='y=2 (horizontal)')
    ax.axvline(x=3, color=C2, linewidth=2, zorder=2)
    ax.text(3.1, 4.5, 'x=3 (vertical)', color=C2, fontsize=7)
    dpt(ax,3,2,'P(3,2)',color=CI)
    right_angle(ax,(3,2),(1,0),(0,1),size=0.3)
    save(fig, '7_13_ex07.png')
_f13_7()
# Ex 8: y=(2/3)x and y=-(3/2)x+5; intersection at x=30/13
xi8 = 30/13; yi8 = (2/3)*xi8
_f13(8, [(2/3,0,'y=(2/3)x'),(-1.5,5,'y=-(3/2)x+5')],
     pts=[(xi8,yi8,'P',.15,.15,CI)], ra=((xi8,yi8),(3,2),(-2,3)))
# Ex 9: y=3x-2 ⊥ y=-(1/3)x+2, A(3,1)
# Intersection: x=6/5=1.2, y=1.6
_f13(9, [(3,-2,'y=3x-2'),(-1/3,2,'y=-(1/3)x+2 (\u22a5)')],
     pts=[(3,1,'A(3,1)',.15,.15,CP),(1.2,1.6,'Int.',.15,.15,CI)],
     ra=((1.2,1.6),(3,1),(-1,3)))
# Ex 10: y=-2x+5 ⊥ y=0.5x+5, B(-2,4); intersection at (0,5)
_f13(10,[(-2,5,'y=-2x+5'),(0.5,5,'y=0.5x+5 (\u22a5)')],
     pts=[(-2,4,'B(-2,4)',.15,.15,CP),(0,5,'(0,5)',.15,.15,CI)],
     ra=((0,5),(1,-2),(2,1)))
# Ex 11: k=-1/4; intersection ≈(0.94, 2.76)
_f13(11,[(-0.25,3,'y=(-1/4)x+3, k=-1/4'),(4,-1,'y=4x-1')],
     xlim=(-4,4), ylim=(-5,10))
# Ex 12: right angle at B(4,2); AB slope=0.5, BC slope=-2
def _f13_12():
    fig, ax = make_fig((-2,6),(-2,6))
    pts = [(0,0),(4,2),(3,4)]
    triangle_shape(ax,pts,labels=['A(0,0)','B(4,2)','C(3,4)'])
    right_angle(ax,(4,2),(2,1),(1,-2),size=0.25)
    save(fig,'7_13_ex12.png')
_f13_12()
# Ex 13: y=0.5x+4 ⊥ y=-2x+1 through C(2,-3); intersection≈(-1.2,3.4)
_f13(13,[(0.5,4,'y=0.5x+4'),(-2,1,'y=-2x+1 (\u22a5)')],
     pts=[(2,-3,'C(2,-3)',.15,.15,CP),(-1.2,3.4,'Int.',.15,.15,CI)])
# Ex 14: y=x+2 ⊥ y=-x+4, D(3,1); intersection at (1,3)
_f13(14,[(1,2,'y=x+2'),(-1,4,'y=-x+4 (\u22a5)')],
     pts=[(3,1,'D(3,1)',.15,.15,CP),(1,3,'(1,3)',.15,.15,CI)],
     ra=((1,3),(1,1),(-1,1)))
_f13(15,[(0.75,-2,'y=(3/4)x-2'),(-4/3,5,'y=-(4/3)x+5')])
_f13(16,[(2,3,'\u2113\u2081:y=2x+3'),(-0.5,2,'\u2113\u2082:y=-0.5x+2')],
     pts=[(-0.4,2.2,'Int.',.15,.15,CI)],
     ra=((-0.4,2.2),(1,2),(-2,1)))
# Ex 17: Triangle A(-5,12),C(7,0),B(3,-4); right angle at C
def _f13_17():
    fig, ax = make_fig((-7,10),(-6,14))
    pts_t = [(-5,12),(7,0),(3,-4)]
    triangle_shape(ax,pts_t,labels=['A(-5,12)','C(7,0)','B(3,-4)'])
    dline(ax,-1,7,(-7,10),color=C1,lw=1.2,label='CA: slope=-1')
    dline(ax, 1,-7,(-7,10),color=C2,lw=1.2,label='CB: slope=1')
    right_angle(ax,(7,0),(-1,1),(-1,-1),size=0.45)
    save(fig,'7_13_ex17.png')
_f13_17()
# Ex 18: intersection of y=3x-1 and y=x+3 at (2,5); ⊥ to -0.5x+6: y=2x+1
def _f13_18():
    fig, ax = make_fig((-2,6),(-4,12))
    dline(ax,3,-1,(-2,6),color=C1,label='y=3x-1')
    dline(ax,1, 3,(-2,6),color=C2,label='y=x+3')
    dline(ax,2, 1,(-2,6),color=C3,lw=2,label='y=2x+1 (\u22a5)')
    dpt(ax,2,5,'(2,5)',color=CI)
    save(fig,'7_13_ex18.png')
_f13_18()
# Ex 19: Triangle A(0,5),B(-2,-1),C(4,2); altitude from A; foot H(2,1)
def _f13_19():
    fig, ax = make_fig((-4,6),(-4,8))
    pts_t = [(0,5),(-2,-1),(4,2)]
    triangle_shape(ax,pts_t,labels=['A(0,5)','B(-2,-1)','C(4,2)'])
    dline(ax,0.5,0,(-4,6),color=C1,lw=1.2,label='BC: y=0.5x')
    dline(ax,-2,5,(-4,6),color=C2,lw=1.5,label='\u05d2\u05d5\u05d1\u05d4: y=-2x+5')
    dpt(ax,2,1,'H(2,1)',color=CI)
    right_angle(ax,(2,1),(1,0.5),(-2,1),size=0.3)
    save(fig,'7_13_ex19.png')
_f13_19()
# Ex 20: Triangle A(-7,-7),B(2,6),C(17,1); altitude from B: y=-3x+12
def _f13_20():
    fig, ax = make_fig((-9,19),(-10,9))
    pts_t = [(-7,-7),(2,6),(17,1)]
    triangle_shape(ax,pts_t,labels=['A(-7,-7)','B(2,6)','C(17,1)'],
                   label_off=[(.2,.2),(.2,.2),(.2,.2)])
    dline(ax,-3,12,(-9,19),color=C2,lw=1.5,label='\u05d2\u05d5\u05d1\u05d4 B: y=-3x+12')
    dpt(ax,5,-3,'H(5,-3)',color=CI)
    dpt(ax,7,-9,'(7,-9)\u2713',color='purple')
    save(fig,'7_13_ex20.png')
_f13_20()
print("File 13: 20 images done")


# ════════════════════════════════════════════════════════════════════════════
#  FILE 17 — Systems of equations graphically  (exercises 1–20)
# ════════════════════════════════════════════════════════════════════════════

def _f17(n, m1, b1, m2, b2, ix, iy, xlim=(-3,7), ylim=(-5,13)):
    fig, ax = make_fig(xlim, ylim)
    lbl1 = f'y={m1}x{b1:+g}' if b1 != 0 else f'y={m1}x'
    lbl2 = f'y={m2}x{b2:+g}' if b2 != 0 else f'y={m2}x'
    dline(ax,m1,b1,xlim,color=C1,lw=2,label=lbl1)
    dline(ax,m2,b2,xlim,color=C2,lw=2,label=lbl2)
    dpt(ax,ix,iy,f'P({ix:.4g},{iy:.4g})',color=CI,size=8)
    save(fig, f'7_17_ex{n:02d}.png')

_f17(1,  2,1,  1,3,  2,5)
_f17(2,  3,-2, 1,2,  2,4,  ylim=(-4,10))
_f17(3,  1,4, -1,8,  2,6)
_f17(4,  2,-3,-1,6,  3,3)
_f17(5,  4,1,  2,5,  2,9,  xlim=(-1,4), ylim=(-1,12))
_f17(6, -2,7,  1,1,  2,3,  ylim=(-2,9))
_f17(7,  3,2, -1,6,  1,5,  xlim=(-2,4))
_f17(8,  5,-3, 2,6,  3,12, xlim=(-1,5), ylim=(-4,15))
_f17(9,  2,3,  3,-1, 4,11, xlim=(-1,6), ylim=(-4,14))
_f17(10, 3,1,  1,5,  2,7,  xlim=(-1,5))
_f17(11, 2,-3,-1,6,  3,3,  xlim=(-1,6))
_f17(12, 0.5,-1,-1/3,4, 6,2, xlim=(-2,9), ylim=(-4,7))
# Ex 13: y=2x+1 and y=1.5x+2 (from 3x-2y=-4); intersection (2,5)
_f17(13, 2,1, 1.5,2, 2,5, xlim=(-1,5), ylim=(-2,8))
_f17(14,-3,10, 0.5,-4, 4,-2, xlim=(-1,6), ylim=(-5,12))
# Ex 15: y=x-1 and y=-2x/3+4; intersection (3,2)
_f17(15, 1,-1,-2/3,4, 3,2, xlim=(-1,6), ylim=(-3,8))
_f17(16,-2/3,4, 1/3,-2, 6,0, xlim=(-2,9), ylim=(-4,6))
_f17(17, 3,9, -2,4, -1,6, xlim=(-4,4), ylim=(-4,12))
_f17(18,-2,11, 1,-1, 4,3, xlim=(-1,7), ylim=(-3,13))
_f17(19,-1,8,  2,-1, 3,5, xlim=(-1,6), ylim=(-3,10))
_f17(20, 0.5,4,-2,9,  2,5, xlim=(-1,6), ylim=(-1,12))
print("File 17: 20 images done")


# ════════════════════════════════════════════════════════════════════════════
#  FILE 18 — Geometric meaning of solution count  (exercises 1–20)
# ════════════════════════════════════════════════════════════════════════════

def _f18(n, m1, b1, m2, b2, gtype, xlim=(-5,6), ylim=(-6,8)):
    fig, ax = make_fig(xlim, ylim)
    if gtype == 'coincident':
        dline(ax,m1,b1,xlim,color=C1,lw=4)
        dline(ax,m2,b2,xlim,color=C2,lw=1.5)
        mid_x = (xlim[0]+xlim[1])/2
        mid_y = m1*mid_x+b1
        ylim_c = ax.get_ylim()
        if ylim_c[0] < mid_y < ylim_c[1]:
            ax.text(mid_x, mid_y+(ylim_c[1]-ylim_c[0])*0.08,
                    '\u05d7\u05d5\u05e4\u05e4\u05d9\u05dd (\u221e \u05e4\u05ea\u05e8\u05d5\u05e0\u05d5\u05ea)',
                    fontsize=8, ha='center', color=C1)
    elif gtype == 'parallel':
        dline(ax,m1,b1,xlim,color=C1,lw=2)
        dline(ax,m2,b2,xlim,color=C2,lw=2)
        mid_x = (xlim[0]+xlim[1])/2
        avg_y = (m1*mid_x+b1 + m2*mid_x+b2)/2
        ylim_c = ax.get_ylim()
        if ylim_c[0] < avg_y < ylim_c[1]:
            ax.text(mid_x, avg_y,
                    '\u05de\u05e7\u05d1\u05d9\u05dc\u05d9\u05dd\n(\u05d0\u05d9\u05df \u05e4\u05ea\u05e8\u05d5\u05df)',
                    fontsize=8, ha='center', color='gray',
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
    else:
        dline(ax,m1,b1,xlim,color=C1,lw=2)
        dline(ax,m2,b2,xlim,color=C2,lw=2)
        if m1 != m2:
            xi = (b2-b1)/(m1-m2); yi = m1*xi+b1
            ylim_c = ax.get_ylim()
            if ylim_c[0] < yi < ylim_c[1]:
                dpt(ax,xi,yi,f'P({xi:.3g},{yi:.3g})',color=CI)
    save(fig, f'7_18_ex{n:02d}.png')

_f18(1,  2,3,  1,1,   'intersect')
_f18(2,  3,-1, 3,2,   'parallel')
_f18(3,  4,2,  4,2,   'coincident')
_f18(4, -1,5,  2,-1,  'intersect', xlim=(-2,6), ylim=(-4,8))
_f18(5,  0.5,3, 0.5,-1,'parallel')
_f18(6,  1,4,  1,4,   'coincident')
_f18(7, -3,7,  2,-3,  'intersect', xlim=(-1,5), ylim=(-4,10))
_f18(8,  2,1,  2,1,   'coincident')
_f18(9,  2,3,  2,5,   'parallel')          # k=2 → parallel
_f18(10, 3,7,  3,7,   'coincident')        # m=7 → coincident
_f18(11, 5,4,  5,-2,  'parallel', xlim=(-3,3))
_f18(12, 2,3,  2,3,   'coincident')        # k=6 → y=2x+3 coincident
_f18(13, 4,1,  4,4,   'parallel', xlim=(-2,3), ylim=(-5,14))
_f18(14, 3,-5, 3,-3,  'parallel')
_f18(15, 3,2,  3,5,   'parallel')
_f18(16,-2,3, -2,4,   'parallel')
_f18(17,-2,10,-2,5,   'parallel')
_f18(18, 3,-4, 3,-6,  'parallel')
_f18(19, 2,-5, 2,-5,  'coincident')        # k=5 → coincident
_f18(20, 1,4,  1,7,   'parallel')
print("File 18: 20 images done")


# ════════════════════════════════════════════════════════════════════════════
#  FILE 20 — Parallelogram identification  (exercises 1–20)
# ════════════════════════════════════════════════════════════════════════════

def _f20(n, A, B, C, D, is_para=True, xlim=(-3,10), ylim=(-2,10)):
    fig, ax = make_fig(xlim, ylim)
    pts = [A,B,C,D]
    fc = CF if is_para else '#FADBD8'
    dpoly(ax, pts, fcolor=fc)
    offs = [(.1,-.4),(.15,-.4),(.15,.15),(-.6,.15)]
    for (x,y),lbl,off in zip(pts,['A','B','C','D'],offs):
        dpt(ax,x,y,f'{lbl}({x},{y})',dx=off[0],dy=off[1])
    save(fig, f'7_20_ex{n:02d}.png')

_f20(1,  (0,0),(4,0),(5,3),(1,3), True,  (-1,7),(-1,5))
_f20(2,  (1,1),(5,1),(6,4),(2,4), True,  (-1,8),(-1,6))
_f20(3,  (0,0),(3,0),(4,2),(2,2), False, (-1,6),(-1,4))
_f20(4,  (2,1),(6,1),(8,4),(4,4), True,  (0,10),(-1,6))
_f20(5,  (0,2),(4,0),(6,4),(2,6), True,  (-1,8),(-1,8))
_f20(6,  (1,0),(5,0),(7,3),(3,3), True,  (-1,9),(-1,5))
_f20(7,  (0,0),(5,0),(6,3),(2,3), False, (-1,8),(-1,5))
_f20(8,  (-1,1),(3,1),(4,4),(0,4),True,  (-3,6),(-1,6))
_f20(9,  (0,0),(4,0),(6,3),(2,3), True,  (-1,8),(-1,5))
_f20(10, (1,2),(5,2),(4,5),(0,5), True,  (-2,7),(-1,7))
_f20(11, (-2,1),(3,1),(4,4),(-1,4),True, (-4,6),(-1,6))
_f20(12, (0,0),(6,0),(8,4),(2,4), True,  (-1,10),(-1,6))
_f20(13, (1,3),(4,3),(6,7),(3,7), True,  (-1,8),(1,9))
_f20(14, (2,1),(5,-1),(7,3),(4,5),True,  (0,9),(-3,7))
_f20(15, (0,0),(4,0),(6,3),(2,3), True,  (-1,8),(-1,5))
_f20(16, (-3,1),(1,1),(3,5),(-1,5),True, (-5,5),(-1,7))
def _f20_17():
    fig, ax = make_fig((0,8),(0,7))
    pts = [(2,2),(2,5),(6,5),(6,2)]
    dpoly(ax, pts)
    for (x,y),lbl,off in zip(pts,['A(2,2)','B(2,5)','C(6,5)','D(6,2)'],
                             [(-.6,-.4),(-.6,.15),(.15,.15),(.15,-.4)]):
        dpt(ax,x,y,lbl,dx=off[0],dy=off[1])
    ax.plot([2,6],[2,5],'g--',lw=1.2)
    ax.plot([2,6],[5,2],'m--',lw=1.2)
    dpt(ax,4,3.5,'M(4,3.5)',color=CI,size=8)
    save(fig,'7_20_ex17.png')
_f20_17()
_f20(18,(0,-1),(4,-1),(4,2),(0,2), True, (-2,6),(-3,4))
_f20(19,(1,2),(5,2),(6,5),(2,5),   True, (-1,8),(0,7))
_f20(20,(0,0),(4,1),(5,4),(1,3),   True, (-2,7),(-2,6))
print("File 20: 20 images done")


# ════════════════════════════════════════════════════════════════════════════
#  FILE 21 — Geometric shapes  (exercises 1–20)
# ════════════════════════════════════════════════════════════════════════════

def _f21_01():
    fig, ax = make_fig((-2,6),(-2,5))
    pts = [(0,0),(4,0),(0,3)]
    triangle_shape(ax,pts,labels=['A(0,0)','B(4,0)','C(0,3)'],
                   label_off=[(.1,-.4),(.1,-.4),(-.7,.1)])
    save(fig,'7_21_ex01.png')
_f21_01()

def _f21_02():
    fig, ax = make_fig((-1,7),(-1,6))
    pts = [(1,1),(5,1),(5,4),(1,4)]
    dpoly(ax, pts)
    for (x,y),lbl,off in zip(pts,['A(1,1)','B(5,1)','C(5,4)','D(1,4)'],
                             [(.1,-.4),(.1,-.4),(.1,.15),(-1.5,.15)]):
        dpt(ax,x,y,lbl,dx=off[0],dy=off[1])
    ax.plot([1,5],[1,4],'g--',lw=1.2)
    ax.text(3.2,2.7,'|diag|=5',fontsize=8,color='green')
    save(fig,'7_21_ex02.png')
_f21_02()

def _f21_03():
    fig, ax = make_fig((-2,8),(-2,6))
    pts = [(0,0),(6,0),(3,4)]
    triangle_shape(ax,pts,labels=['A(0,0)','B(6,0)','C(3,4)'],
                   label_off=[(.1,-.4),(.1,-.4),(-.3,.15)])
    save(fig,'7_21_ex03.png')
_f21_03()

def _f21_04():
    fig, ax = make_fig((-1,9),(-1,13))
    dline(ax,4/3,5/3,(-1,9),color=C1)
    for (x,y,lbl) in [(1,3,'A(1,3)'),(4,7,'B(4,7)'),(7,11,'C(7,11)\u2713')]:
        dpt(ax,x,y,lbl)
    save(fig,'7_21_ex04.png')
_f21_04()

def _f21_05():
    fig, ax = make_fig((-2,6),(-2,5))
    dline(ax,3/4,0,(-2,6),color=C1,label='y=(3/4)x')
    dpt(ax,0,0,'A(0,0)')
    dpt(ax,4,3,'B(4,3)')
    save(fig,'7_21_ex05.png')
_f21_05()

def _f21_06():
    fig, ax = make_fig((-2,6),(-2,8))
    dline(ax,2,1,(-2,6),color=C1,label='y=2x+1')
    dline(ax,-0.5,6,(-2,6),color=C2,label='y=-0.5x+6')
    dpt(ax,2,5,'P(2,5)',color=CI)
    right_angle(ax,(2,5),(1,2),(-2,1),size=0.35)
    save(fig,'7_21_ex06.png')
_f21_06()

def _f21_07():
    fig, ax = make_fig((0,10),(2,12))
    ax.plot([2,8],[4,10],'b-',lw=2)
    dpt(ax,2,4,'A(2,4)')
    dpt(ax,8,10,'B(8,10)')
    dpt(ax,5,7,'M(5,7)',color=CI,size=8)
    save(fig,'7_21_ex07.png')
_f21_07()

def _f21_08():
    fig, ax = make_fig((-1,7),(-1,7))
    pts = [(0,0),(5,0),(5,5)]
    triangle_shape(ax,pts,labels=['A(0,0)','B(5,0)','C(5,5)'],
                   label_off=[(.1,-.4),(.1,-.4),(.1,.15)])
    ax.plot([0,5],[0,2.5],'g--',lw=1.5)
    dpt(ax,5,2.5,'M(5,2.5)',color=CI)
    save(fig,'7_21_ex08.png')
_f21_08()

def _f21_09():
    fig, ax = make_fig((-5,7),(-2,6))
    pts = [(-3,0),(5,0),(1,4)]
    triangle_shape(ax,pts,labels=['A(-3,0)','B(5,0)','C(1,4)'],
                   label_off=[(.1,-.4),(.1,-.4),(-.3,.15)])
    dpt(ax,1,0,'M(1,0)',color=CI)
    ax.plot([1,1],[0,4],'g--',lw=1.5)
    save(fig,'7_21_ex09.png')
_f21_09()

def _f21_10():
    fig, ax = make_fig((-1,7),(0,7))
    pts = [(1,2),(5,2),(5,5),(1,5)]
    dpoly(ax,pts)
    for (x,y),lbl,off in zip(pts,['A(1,2)','B(5,2)','C(5,5)','D(1,5)'],
                             [(.1,-.4),(.1,-.4),(.1,.15),(-1.5,.15)]):
        dpt(ax,x,y,lbl,dx=off[0],dy=off[1])
    save(fig,'7_21_ex10.png')
_f21_10()

def _f21_11():
    h = 2*np.sqrt(3)
    fig, ax = make_fig((-2,6),(-2,6))
    pts = [(0,0),(4,0),(2,h)]
    triangle_shape(ax,pts,labels=[f'A(0,0)',f'B(4,0)',f'C(2,{h:.2f})'],
                   label_off=[(.1,-.4),(.1,-.4),(-.4,.1)])
    save(fig,'7_21_ex11.png')
_f21_11()

def _f21_12():
    fig, ax = make_fig((-1,8),(-1,7))
    pts = [(2,1),(6,1),(4,5)]
    triangle_shape(ax,pts,labels=['A(2,1)','B(6,1)','C(4,5)'],
                   label_off=[(.1,-.4),(.1,-.4),(-.3,.15)])
    ax.axvline(x=4,color=C2,lw=1.5,linestyle='--')
    ax.text(4.1,4,'\u05d2\u05d5\u05d1\u05d4: x=4',fontsize=8,color=C2)
    dpt(ax,4,1,'H(4,1)',color=CI)
    save(fig,'7_21_ex12.png')
_f21_12()

def _f21_13():
    fig, ax = make_fig((-1,8),(-1,5))
    ax.plot([0,6],[0,3],'b-',lw=2)
    dpt(ax,0,0,'A(0,0)')
    dpt(ax,6,3,'B(6,3)')
    dpt(ax,2,1,'D(2,1)',color=CI)
    save(fig,'7_21_ex13.png')
_f21_13()

def _f21_14():
    fig, ax = make_fig((-1,11),(1,9))
    pts = [(1,3),(7,3),(9,7),(3,7)]
    dpoly(ax,pts)
    for (x,y),lbl,off in zip(pts,['A(1,3)','B(7,3)','C(9,7)','D(3,7)'],
                             [(.1,-.4),(.1,-.4),(.1,.15),(-1.5,.15)]):
        dpt(ax,x,y,lbl,dx=off[0],dy=off[1])
    ax.annotate('',xy=(1,7),xytext=(1,3),
                arrowprops=dict(arrowstyle='<->',color='green',lw=1.5))
    ax.text(1.2,5,'h=4',fontsize=8,color='green')
    save(fig,'7_21_ex14.png')
_f21_14()

def _f21_15():
    fig, ax = make_fig((-6,6),(-2,5))
    pts = [(-4,0),(4,0),(0,3)]
    triangle_shape(ax,pts,labels=['A(-4,0)','B(4,0)','C(0,3)'],
                   label_off=[(.1,-.4),(.1,-.4),(-.3,.15)])
    ax.plot([0,0],[0,3],'g--',lw=1.2)
    ax.text(.2,1.5,'h=3',fontsize=8,color='green')
    save(fig,'7_21_ex15.png')
_f21_15()

def _f21_16():
    fig, ax = make_fig((-3,6),(-4,10))
    dline(ax,3,-1,(-3,6),color=C1,label='y=3x-1')
    dline(ax,-1/3,17/3,(-3,6),color=C2,label='y=-x/3+17/3 (\u22a5)')
    dpt(ax,2,5,'P(2,5)',color=CI)
    right_angle(ax,(2,5),(3,1),(-1,3),size=0.3)
    save(fig,'7_21_ex16.png')
_f21_16()

def _f21_17():
    fig, ax = make_fig((-10,7),(-2,9))
    dline(ax,3/4,6,(-10,7),color=C1,label='\u05e7\u05d9\u05e8 \u05d0: y=(3/4)x+6')
    dline(ax,-4/3,6,(-10,7),color=C2,label='\u05e7\u05d9\u05e8 \u05d1: y=(-4/3)x+6')
    dpt(ax,-8,0,'A(-8,0)')
    dpt(ax,0,6,'B(0,6)')
    dpt(ax,4.5,0,'C(4.5,0)')
    right_angle(ax,(0,6),(3,4),(-4,3),size=0.4)
    save(fig,'7_21_ex17.png')
_f21_17()

def _f21_18():
    fig, ax = make_fig((-7,10),(-6,14))
    pts = [(-5,12),(7,0),(3,-4)]
    triangle_shape(ax,pts,labels=['A(-5,12)','C(7,0)','B(3,-4)'],
                   label_off=[(.2,.2),(.2,.2),(.2,-.4)])
    right_angle(ax,(7,0),(-1,1),(-1,-1),size=0.45)
    save(fig,'7_21_ex18.png')
_f21_18()

def _f21_19():
    fig, ax = make_fig((-9,19),(-10,9))
    pts = [(-7,-7),(2,6),(17,1)]
    triangle_shape(ax,pts,labels=['A(-7,-7)','B(2,6)','C(17,1)'],
                   label_off=[(.2,.2),(.2,.2),(.2,.2)])
    dpt(ax,5,-3,'M(5,-3)',color=CI)
    dline(ax,-3,12,(-9,19),color=C2,lw=1.5,label='\u05ea\u05d9\u05db\u05d5\u05df=\u05d2\u05d5\u05d1\u05d4')
    save(fig,'7_21_ex19.png')
_f21_19()

def _f21_20():
    fig, ax = make_fig((-2,8),(-2,6))
    pts = [(0,4),(6,0),(0,0)]
    triangle_shape(ax,pts,labels=['A(0,4)','B(6,0)','C(0,0)'],
                   label_off=[(-.7,.1),(.1,-.4),(-.7,-.4)])
    right_angle(ax,(0,0),(0,1),(1,0),size=0.3)
    dpt(ax,3,2,'M(3,2)',color=CI)
    ax.plot([0,3],[0,2],'g--',lw=1.5)
    ax.text(1.2,1.3,'CM=\u00bd|AB|',fontsize=8,color='green')
    save(fig,'7_21_ex20.png')
_f21_20()
print("File 21: 20 images done")


# ════════════════════════════════════════════════════════════════════════════
#  FILE 3 — Parameters  (exercises 9–20 only)
# ════════════════════════════════════════════════════════════════════════════

def _f3(n, lines, pts=None, xlim=(-6,8), ylim=(-8,12)):
    fig, ax = make_fig(xlim, ylim)
    for i,(m,b,lbl) in enumerate(lines):
        dline(ax,m,b,xlim,color=[C1,C2][i%2],lw=2,label=lbl)
    if pts:
        for (x,y,lbl,dx,dy) in pts:
            dpt(ax,x,y,lbl,dx=dx,dy=dy)
    save(fig, f'7_3_ex{n:02d}.png')

_f3(9,  [(-4,10,'y=-4x+10, a=-4, b=10')])
_f3(10, [(2,5,'f(x)=2x+5'),(2,-3,'g(x)=2x-3')],
    pts=[(0,5,'(0,5)',.15,.15),(0,-3,'(0,-3)',.15,.15)])
_f3(11, [(4,1,'f(x)=4x+1'),(-4,1,'g(x)=-4x+1')],
    pts=[(0,1,'(0,1)',.15,.15)])
_f3(12, [(4,3,'y=4x+3, a=4')])
_f3(13, [(-2,5,'y=-2x+5, b=5')])
_f3(14, [(3,2,'y=3x+2')],
    pts=[(1,5,'(1,5)',.15,.15),(3,11,'(3,11)',.15,.15)])
_f3(15, [(2,-3,'y=2x-3')],
    pts=[(0,-3,'(0,-3)',.15,.15),(4,5,'(4,5)',.15,.15)])
_f3(16, [(1.5,20,'y=1.5x+20')], xlim=(-2,14), ylim=(15,42))
_f3(17, [(2.5,50,'y=2.5x+50')], xlim=(-5,80), ylim=(40,260))
def _f3_18():
    fig, ax = make_fig((-2,35),(-10,360))
    dline(ax,8,60,(-2,35),color=C1,lw=2)
    dline(ax,10,20,(-2,35),color=C2,lw=2)
    ax.text(2,94,'\u05e1\u05e4\u05e7 \u05d0: y=8x+60',color=C1,fontsize=7,
            bbox=dict(facecolor='white',alpha=0.6,edgecolor='none',pad=1))
    ax.text(6,52,'\u05e1\u05e4\u05e7 \u05d1: y=10x+20',color=C2,fontsize=7,
            bbox=dict(facecolor='white',alpha=0.6,edgecolor='none',pad=1))
    dpt(ax,20,220,'x=20',color=CP,dx=.5,dy=.5)
    save(fig,'7_3_ex18.png')
_f3_18()
_f3(19, [(2,-6,'y=2x-6')],
    pts=[(0,-6,'(0,-6)',.15,.15),(3,0,'(3,0)',.15,.15)])
_f3(20, [(2,110,'y=2x+110')], xlim=(-2,55), ylim=(100,225))
print("File 3: 12 images done (ex 9-20)")


# ════════════════════════════════════════════════════════════════════════════
#  FILE 6 — Intercepts  (exercises 9–20 only)
# ════════════════════════════════════════════════════════════════════════════

def _f6(n, m, b, xi, yi, xlim=(-6,8), ylim=(-10,12), lbl=None):
    fig, ax = make_fig(xlim, ylim)
    line_lbl = lbl or (f'y={m}x{b:+g}' if b != 0 else f'y={m}x')
    dline(ax,m,b,xlim,color=C1,lw=2,label=line_lbl)
    dpt(ax,xi,0,f'({xi:.4g},0)',color='purple',dy=-.5)
    dpt(ax,0,yi,f'(0,{yi:.4g})',color='purple',dx=.15)
    save(fig, f'7_6_ex{n:02d}.png')

_f6(9,  -1.5,6,  4,6,  lbl='3x+2y=12')
_f6(10, 4,-8,    2,-8, xlim=(-2,6), ylim=(-10,5), lbl='-4x+y+8=0')
_f6(11, 2/3,2,  -3,2,  xlim=(-6,6), ylim=(-3,7), lbl='2x-3y+6=0')
_f6(12,-1.25,5,  4,5,  xlim=(-2,6), ylim=(-3,8), lbl='5x+4y=20')
_f6(13, 3,-6,    2,-6)
_f6(14, 3,-9,    3,-9, xlim=(-2,6), ylim=(-11,6))
_f6(15,-0.75,6,  8,6,  xlim=(-2,10), ylim=(-2,8))
def _f6_16():
    fig, ax = make_fig((-2,8),(-8,8))
    dline(ax,2,-6,(-2,8),color=C1,label='\u2113\u2081:y=2x-6')
    dline(ax,-1,6,(-2,8),color=C2,label='\u2113\u2082:y=-x+6')
    dpt(ax,3,0,'(3,0)',color=C1,dy=-.5)
    dpt(ax,0,-6,'(0,-6)',color=C1,dx=.15)
    dpt(ax,6,0,'(6,0)',color=C2,dy=-.5)
    dpt(ax,0,6,'(0,6)',color=C2,dx=.15)
    save(fig,'7_6_ex16.png')
_f6_16()
def _f6_17():
    fig, ax = make_fig((-5,5),(0,12))
    dline(ax,2,8,(-5,5),color=C1,label='y=2x+8')
    dline(ax,-2,5,(-5,5),color=C2,label='y=-2x+5')
    dpt(ax,0,8,'(0,8)',color=C1,dx=.15)
    dpt(ax,0,5,'(0,5)',color=C2,dx=.15)
    dpt(ax,-0.75,6.5,'P(-0.75,6.5)',color=CI)
    save(fig,'7_6_ex17.png')
_f6_17()
def _f6_18():
    fig, ax = make_fig((-5,6),(-2,12))
    dline(ax,-3,9,(-5,6),color=C1)
    dline(ax,0.5,2,(-5,6),color=C2)
    ax.text(-1.4,10.4,'\u05db\u05d1\u05d9\u05e9 \u05d0: y=-3x+9',color=C1,fontsize=7,
            bbox=dict(facecolor='white',alpha=0.6,edgecolor='none',pad=1))
    ax.text(3.3,4.4,'\u05db\u05d1\u05d9\u05e9 \u05d1: y=0.5x+2',color=C2,fontsize=7,
            bbox=dict(facecolor='white',alpha=0.6,edgecolor='none',pad=1))
    dpt(ax,3,0,'(3,0)',color=C1,dy=-.5)
    dpt(ax,0,9,'(0,9)',color=C1,dx=.15)
    dpt(ax,-4,0,'(-4,0)',color=C2,dy=-.5)
    dpt(ax,0,2,'(0,2)',color=C2,dx=.15)
    dpt(ax,2,3,'(2,3)',color=CI)
    save(fig,'7_6_ex18.png')
_f6_18()
def _f6_19():
    fig, ax = make_fig((-2,7),(-3,5))
    pts = [(0,3),(5,3),(5,-1),(0,-1)]
    dpoly(ax,pts)
    for (x,y),lbl,off in zip(pts,['A(0,3)','B(5,3)','C(5,-1)','D(0,-1)'],
                             [(-.6,.15),(.15,.15),(.15,-.4),(-.6,-.4)]):
        dpt(ax,x,y,lbl,dx=off[0],dy=off[1])
    dline(ax,-4/5,3,(-2,7),color=C2,lw=1.5,label='\u05d0\u05dc\u05db\u05e1\u05d5\u05df AC')
    dpt(ax,3.75,0,'(3.75,0)',color='purple',dy=-.4)
    dpt(ax,2.5,1,'M(2.5,1)',color=CI)
    save(fig,'7_6_ex19.png')
_f6_19()
def _f6_20():
    fig, ax = make_fig((-100,1100),(-50,600))
    dline(ax,-0.5,500,(-100,1100),color=C1,label='y=-0.5x+500')
    dpt(ax,1000,0,'A(1000,0)',dx=10,dy=-30)
    dpt(ax,0,500,'B(0,500)',dx=10,dy=10)
    dpt(ax,500,250,'(500,250)\u2713',color=CI)
    save(fig,'7_6_ex20.png')
_f6_20()
print("File 6: 12 images done (ex 9-20)")


# ════════════════════════════════════════════════════════════════════════════
#  FILE 10 — Slopes  (exercises 9–20 only)
# ════════════════════════════════════════════════════════════════════════════

def _f10_seg(n, p1, p2, slope, xlim=(-6,6), ylim=(-8,10)):
    fig, ax = make_fig(xlim, ylim)
    b = p1[1] - slope*p1[0]
    dline(ax,slope,b,xlim,color=C1,lw=2)
    dpt(ax,p1[0],p1[1],f'A({p1[0]},{p1[1]})')
    dpt(ax,p2[0],p2[1],f'B({p2[0]},{p2[1]})')
    ylim_c = ax.get_ylim()
    ax.text(xlim[0]+.3, ylim_c[0]+(ylim_c[1]-ylim_c[0])*.1,
            f'a = {slope:.4g}', fontsize=9, color=C1)
    save(fig, f'7_10_ex{n:02d}.png')

_f10_seg(9,  (-2,5),(3,-5),  -2)
_f10_seg(10, (-3,-4),(-1,2), 3,  xlim=(-5,3),  ylim=(-7,7))
_f10_seg(11, (0,-5),(4,-5),  0,  ylim=(-8,4))
_f10_seg(12, (.5,3),(1.5,7), 4,  xlim=(-1,4),  ylim=(0,10))
def _f10_13():
    fig, ax = make_fig((-4,4),(-2,10))
    dline(ax,2,5,(-4,4),color=C1,label='y=2x+5')
    dpt(ax,-1,3,'A(-1,3)')
    dpt(ax,0,5,'B(0,5)')
    ax.text(-3.5,.5,'a=2',fontsize=9,color=C1)
    save(fig,'7_10_ex13.png')
_f10_13()
_f10_seg(14, (-4,.5),(0,-1.5), -0.5, xlim=(-6,3), ylim=(-4,4))
def _f10_15():
    fig, ax = make_fig((-1,7),(-1,13))
    dline(ax,2,1,(-1,7),color=C1,label='y=2x+1')
    for (x,y,lbl) in [(1,3,'A(1,3)'),(3,7,'B(3,7)'),(5,11,'C(5,11)')]:
        dpt(ax,x,y,lbl)
    save(fig,'7_10_ex15.png')
_f10_15()
def _f10_16():
    fig, ax = make_fig((-2,7),(-4,10))
    dline(ax,2,-2,(-2,7),color=C1,label='y=2x-2 (a=2, k=2)')
    dpt(ax,2,2,'A(k=2, 2)')
    dpt(ax,4,6,'B(4,6)')
    save(fig,'7_10_ex16.png')
_f10_16()
def _f10_17():
    fig, ax = make_fig((-20,350),(-30,200))
    dline(ax,0.5,0,(-20,350),color=C1)
    dpt(ax,100,50,'A(100,50)')
    dpt(ax,300,150,'B(300,150)')
    ax.text(50,25,'a=0.5',fontsize=9,color=C1)
    save(fig,'7_10_ex17.png')
_f10_17()
def _f10_18():
    fig, ax = make_fig((-1,7),(-1,20))
    dline(ax,3,1,(-1,7),color=C1,label='y=3x+1')
    for (x,y,lbl) in [(1,4,'P(1,4)'),(3,10,'Q(3,10)'),(5,16,'R(5,k=16)')]:
        dpt(ax,x,y,lbl)
    save(fig,'7_10_ex18.png')
_f10_18()
def _f10_19():
    fig, ax = make_fig((-1,6),(-1,22))
    ax.text(6.3,0,'t',fontsize=10,ha='left',va='center')
    ax.text(.3,22,'\u05de\u05d9\u05e7\u05d5\u05dd',fontsize=9,ha='left',va='top')
    dline(ax,4,3,(-1,6),color=C1,label='\u05de\u05d9\u05e7\u05d5\u05dd=4t+3')
    for (t,s,lbl) in [(0,3,'(0,3)'),(2,11,'(2,11)'),(4,19,'(4,19)')]:
        dpt(ax,t,s,lbl)
    save(fig,'7_10_ex19.png')
_f10_19()
def _f10_20():
    fig, ax = make_fig((-5,5),(-4,6))
    pts = [(-3,1),(1,3),(3,-1)]
    triangle_shape(ax,pts,labels=['A(-3,1)','B(1,3)','C(3,-1)'])
    ax.text(-1.5,3,'a_AB=0.5',fontsize=8,color=C1)
    ax.text(1.5,1.5,'a_BC=-2',fontsize=8,color=C2)
    save(fig,'7_10_ex20.png')
_f10_20()
print("File 10: 12 images done (ex 9-20)")


# ════════════════════════════════════════════════════════════════════════════
#  FILE 14 — Midpoints  (exercises 9–20 only)
# ════════════════════════════════════════════════════════════════════════════

def _f14_seg(n, A, B, M, xlim=(-6,10), ylim=(-8,10)):
    fig, ax = make_fig(xlim, ylim)
    ax.plot([A[0],B[0]],[A[1],B[1]],'b-',lw=2)
    dpt(ax,A[0],A[1],f'A({A[0]},{A[1]})')
    dpt(ax,B[0],B[1],f'B({B[0]},{B[1]})')
    dpt(ax,M[0],M[1],f'M({M[0]},{M[1]})',color=CI,size=8)
    save(fig, f'7_14_ex{n:02d}.png')

_f14_seg(9,  (-3,5),(7,-1),(2,2))
_f14_seg(10, (-4,-2),(0,6),(-2,2), xlim=(-6,4))
_f14_seg(11, (-5,3),(-1,-7),(-3,-2), xlim=(-8,3), ylim=(-10,6))
def _f14_12():
    fig, ax = make_fig((-1,8),(-1,9))
    ax.plot([1,5],[2,6],'b-',lw=2)
    dpt(ax,1,2,'A(1,2)')
    dpt(ax,5,6,'B(5,6)')
    dpt(ax,3,4,'M(3,4)',color=CI,size=8)
    save(fig,'7_14_ex12.png')
_f14_12()
def _f14_13():
    fig, ax = make_fig((-6,6),(0,9))
    ax.plot([-4,4],[3,7],'b-',lw=2)
    dpt(ax,-4,3,'P(-4,3)')
    dpt(ax,4,7,'Q(4,7)')
    dpt(ax,0,5,'M(0,5)',color=CI,size=8)
    save(fig,'7_14_ex13.png')
_f14_13()
_f14_seg(14, (.5,3),(1.5,-1),(1,1), xlim=(-1,4), ylim=(-3,5))
_f14_seg(15, (-.5,1.5),(2.5,.5),(1,1), xlim=(-2,4), ylim=(-1,3))
_f14_seg(16, (2,3),(8,7),(5,5))
def _f14_17():
    fig, ax = make_fig((0,8),(0,7))
    pts = [(2,2),(2,5),(6,5),(6,2)]
    dpoly(ax,pts)
    for (x,y),lbl,off in zip(pts,['A(2,2)','B(2,5)','C(6,5)','D(6,2)'],
                             [(-.6,-.4),(-.6,.15),(.15,.15),(.15,-.4)]):
        dpt(ax,x,y,lbl,dx=off[0],dy=off[1])
    ax.plot([2,6],[2,5],'g--',lw=1.5)
    ax.plot([2,6],[5,2],'m--',lw=1.5)
    dpt(ax,4,3.5,'M(4,3.5)',color=CI,size=8)
    save(fig,'7_14_ex17.png')
_f14_17()
def _f14_18():
    fig, ax = make_fig((-2,6),(-3,4))
    pts = [(0,-1),(4,-1),(4,2),(0,2)]
    dpoly(ax,pts)
    for (x,y),lbl,off in zip(pts,['A(0,-1)','B(4,-1)','C(4,2)','D(0,2)'],
                             [(-.6,-.4),(.15,-.4),(.15,.15),(-.6,.15)]):
        dpt(ax,x,y,lbl,dx=off[0],dy=off[1])
    ax.plot([0,4],[-1,2],'g--',lw=1.5)
    ax.plot([4,0],[-1,2],'m--',lw=1.5)
    dpt(ax,2,.5,'M(2,0.5)',color=CI,size=8)
    save(fig,'7_14_ex18.png')
_f14_18()
def _f14_19():
    fig, ax = make_fig((-1,5),(-5,2))
    pts = [(2,-3),(1,-3),(1,-1),(2,-1)]
    dpoly(ax,pts)
    for (x,y),lbl in zip(pts,['A(2,-3)','B(1,-3)','C(1,-1)','D(2,-1)']):
        dpt(ax,x,y,lbl,dx=.1,dy=.1)
    dpt(ax,1.5,-2,'M(1.5,-2)',color=CI,size=8)
    save(fig,'7_14_ex19.png')
_f14_19()
def _f14_20():
    fig, ax = make_fig((0,8),(0,7))
    pts = [(2,2),(2,5),(6,5),(6,2)]
    dpoly(ax,pts)
    for (x,y),lbl,off in zip(pts,['A(2,2)','B(2,5)','C(6,5)','D(6,2)'],
                             [(-.6,-.4),(-.6,.15),(.15,.15),(.15,-.4)]):
        dpt(ax,x,y,lbl,dx=off[0],dy=off[1])
    ax.plot([2,6],[2,5],'g--',lw=1.5)
    ax.plot([2,6],[5,2],'m--',lw=1.5)
    dpt(ax,4,3.5,'M(4,3.5)',color=CI,size=8)
    ax.text(3.5,5.5,'|AC|=|BD|=5',fontsize=8,color='green')
    save(fig,'7_14_ex20.png')
_f14_20()
print("File 14: 12 images done (ex 9-20)")


# ════════════════════════════════════════════════════════════════════════════
#  FILE 16 — Distances  (exercises 9–20 only)
# ════════════════════════════════════════════════════════════════════════════

def _f16_seg(n, A, B, dist, xlim=(-6,8), ylim=(-8,10)):
    fig, ax = make_fig(xlim, ylim)
    ax.plot([A[0],B[0]],[A[1],B[1]],'b-',lw=2)
    dpt(ax,A[0],A[1],f'A({A[0]},{A[1]})')
    dpt(ax,B[0],B[1],f'B({B[0]},{B[1]})')
    mid = ((A[0]+B[0])/2, (A[1]+B[1])/2)
    ylim_c = ax.get_ylim()
    dy_label = (ylim_c[1]-ylim_c[0])*0.04
    ax.text(mid[0]+.2, mid[1]+dy_label, f'd={dist}', fontsize=9, color='gray')
    save(fig, f'7_16_ex{n:02d}.png')

_f16_seg(9,  (-3,2),(5,-4),  10)
_f16_seg(10, (-4,-3),(0,0),  5, xlim=(-6,3), ylim=(-6,4))
_f16_seg(11, (1,7),(-2,3),   5, xlim=(-4,4), ylim=(0,10))
_f16_seg(12, (-2,3),(3,-9),  13, xlim=(-4,6), ylim=(-11,6))
_f16_seg(13, (0,-6),(8,0),   10, xlim=(-2,10), ylim=(-8,3))
_f16_seg(14, (-5,2),(7,7),   13, xlim=(-7,9), ylim=(-1,10))
_f16_seg(15, (-6,1),(6,6),   13, xlim=(-8,8), ylim=(-1,9))
_f16_seg(16, (.5,1),(2.5,4), '\u221a13', xlim=(-1,4), ylim=(-1,6))
def _f16_17():
    fig, ax = make_fig((-2,8),(-2,10))
    ax.plot([0,6],[0,8],'b-',lw=2)
    dpt(ax,0,0,'A(0,0)')
    dpt(ax,6,8,'B(6,8)')
    dpt(ax,3,4,'M(3,4)',color=CI,size=8)
    ax.text(3.2,4.5,'d=10',fontsize=9,color='gray')
    save(fig,'7_16_ex17.png')
_f16_17()
def _f16_18():
    fig, ax = make_fig((-100,1100),(-50,250))
    ax.plot([1000,0],[0,200],'b-',lw=2)
    dpt(ax,1000,0,'A(1000,0)',dx=10,dy=-20)
    dpt(ax,0,200,'B(0,200)',dx=10,dy=10)
    dpt(ax,500,100,'M(500,100)',color=CI,size=8)
    ax.text(600,140,'d\u22481020m',fontsize=9,color='gray')
    save(fig,'7_16_ex18.png')
_f16_18()
def _f16_19():
    fig, ax = make_fig((0,9),(-5,3))
    pts = [(2,-3),(7,-3),(7,1),(2,1)]
    dpoly(ax,pts)
    for (x,y),lbl,off in zip(pts,['A(2,-3)','B(7,-3)','C(7,1)','D(2,1)'],
                             [(.1,-.5),(.1,-.5),(.1,.15),(-1.5,.15)]):
        dpt(ax,x,y,lbl,dx=off[0],dy=off[1])
    ax.plot([2,7],[-3,1],'g--',lw=1.5)
    ax.text(5,0,'|AC|=\u221a41',fontsize=8,color='green')
    save(fig,'7_16_ex19.png')
_f16_19()
def _f16_20():
    fig, ax = make_fig((-6,6),(-2,5))
    pts = [(-4,0),(4,0),(0,3)]
    triangle_shape(ax,pts,labels=['A(-4,0)','B(4,0)','C(0,3)'],
                   label_off=[(.1,-.4),(.1,-.4),(-.4,.1)])
    ax.text(-2.5,2,'|AC|=5',fontsize=8,color=C1)
    ax.text(1.5,2,'|BC|=5',fontsize=8,color=C1)
    ax.text(-.5,-.6,'|AB|=8',fontsize=8,color=C1)
    save(fig,'7_16_ex20.png')
_f16_20()
print("File 16: 12 images done (ex 9-20)")

# Count total
import glob
all_imgs = glob.glob(os.path.join(IMAGES_DIR, '7_*.png'))
print(f"\nAll done! Total images in directory: {len(all_imgs)}")
