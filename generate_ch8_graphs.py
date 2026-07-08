"""
Generate PNG graphs for Chapter 8 – Quadratic Functions & Parabola
One graph per exercise, 20 exercises × 12 subtopics = 240 images.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Polygon
from matplotlib.axes import Axes
import numpy as np
import os
import re
from bidi.algorithm import get_display

WORKSPACE = os.path.dirname(os.path.abspath(__file__))
CHAPTER_DIR = os.path.join(WORKSPACE, "8 - הפונקציה הריבועית והפרבולה")
IMAGES_DIR = os.path.join(CHAPTER_DIR, "images")
os.makedirs(IMAGES_DIR, exist_ok=True)

plt.rcParams['font.family'] = ['Arial', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

HEBREW_RE = re.compile(r'[\u0590-\u05FF]')

def rtl_text(value):
    return value

_orig_set_title = Axes.set_title
_orig_set_xlabel = Axes.set_xlabel
_orig_set_ylabel = Axes.set_ylabel
_orig_plot = Axes.plot
_orig_fill_between = Axes.fill_between
_orig_annotate = Axes.annotate
_orig_text = Axes.text

def _patched_set_title(self, label, *args, **kwargs):
    return _orig_set_title(self, rtl_text(label), *args, **kwargs)

def _patched_set_xlabel(self, xlabel, *args, **kwargs):
    return _orig_set_xlabel(self, rtl_text(xlabel), *args, **kwargs)

def _patched_set_ylabel(self, ylabel, *args, **kwargs):
    return _orig_set_ylabel(self, rtl_text(ylabel), *args, **kwargs)

def _patched_plot(self, *args, **kwargs):
    if 'label' in kwargs:
        kwargs['label'] = rtl_text(kwargs['label'])
    return _orig_plot(self, *args, **kwargs)

def _patched_fill_between(self, *args, **kwargs):
    if 'label' in kwargs:
        kwargs['label'] = rtl_text(kwargs['label'])
    return _orig_fill_between(self, *args, **kwargs)

def _patched_annotate(self, text, *args, **kwargs):
    return _orig_annotate(self, rtl_text(text), *args, **kwargs)

def _patched_text(self, x, y, s, *args, **kwargs):
    return _orig_text(self, x, y, rtl_text(s), *args, **kwargs)

Axes.set_title = _patched_set_title
Axes.set_xlabel = _patched_set_xlabel
Axes.set_ylabel = _patched_set_ylabel
Axes.plot = _patched_plot
Axes.fill_between = _patched_fill_between
Axes.annotate = _patched_annotate
Axes.text = _patched_text

# ── colours ──────────────────────────────────────────────────────────────────
PARA_COLOR  = '#2166AC'
LINE_COLOR  = '#D6604D'
PARA2_COLOR = '#762A83'
PARA3_COLOR = '#4DAC26'
VTX_COLOR   = 'red'
ROOT_COLOR  = 'green'
SYM_COLOR   = '#FF7F00'
POS_COLOR   = '#4DAC26'
NEG_COLOR   = '#D7191C'
INC_COLOR   = '#1A9641'
DEC_COLOR   = '#D7191C'
PT_COLOR    = '#0571B0'

# ── helpers ───────────────────────────────────────────────────────────────────

def make_fig():
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.set_facecolor('white')
    fig.patch.set_facecolor('white')
    return fig, ax


def setup_axes(ax):
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')
    ax.spines['left'].set_linewidth(1.2)
    ax.spines['bottom'].set_linewidth(1.2)
    ax.grid(True, alpha=0.25, linestyle='--')
    ax.tick_params(labelsize=8)


def py(a, b, c, x):
    return a * x**2 + b * x + c


def get_roots(a, b, c):
    disc = b**2 - 4 * a * c
    if disc < -1e-9:
        return []
    if abs(disc) < 1e-9:
        return [-b / (2 * a)]
    sq = np.sqrt(disc)
    return sorted([(-b + sq) / (2 * a), (-b - sq) / (2 * a)])


def vertex(a, b, c):
    xv = -b / (2 * a)
    return xv, py(a, b, c, xv)


def xlim_auto(a, b, c, extra=None, m2=None, n2=None, margin_factor=0.55):
    """Compute sensible x-limits given parabola and optional extra points/line."""
    xv, _ = vertex(a, b, c)
    roots = get_roots(a, b, c)
    pts = [xv] + roots
    if extra:
        pts.extend(extra)
    if m2 is not None:
        # intersection with line y = m2*x + n2
        disc2 = (b - m2)**2 - 4 * a * (c - n2)
        if disc2 >= 0:
            sq2 = np.sqrt(disc2)
            pts.append((-(b - m2) + sq2) / (2 * a))
            pts.append((-(b - m2) - sq2) / (2 * a))
    lo, hi = min(pts), max(pts)
    span = max(hi - lo, 1.0)
    mg = max(2.5, span * margin_factor)
    return lo - mg, hi + mg


def draw_para(ax, a, b, c, xlim, color=PARA_COLOR, lw=2, label=None, ls='-'):
    x = np.linspace(xlim[0], xlim[1], 700)
    y = py(a, b, c, x)
    ax.plot(x, y, color=color, linewidth=lw, label=label, linestyle=ls)
    return x, y


def draw_line(ax, m, n, xlim, color=LINE_COLOR, lw=2, label=None):
    x = np.linspace(xlim[0], xlim[1], 300)
    ax.plot(x, m * x + n, color=color, linewidth=lw, label=label)


def mark_vertex(ax, a, b, c, label='V', color=VTX_COLOR):
    xv, yv = vertex(a, b, c)
    ax.scatter([xv], [yv], color=color, zorder=6, s=80)
    dy = 7 if yv >= 0 else -14
    ax.annotate(label, (xv, yv), textcoords='offset points',
                xytext=(6, dy), fontsize=9, color=color, fontweight='bold')
    ax.axvline(xv, color='purple', linestyle='--', linewidth=1.0, alpha=0.55)
    return xv, yv


def mark_roots(ax, a, b, c, labels=None):
    roots = get_roots(a, b, c)
    default = ['A', 'B', 'C', 'D']
    for i, r in enumerate(roots):
        ax.scatter([r], [0], color=ROOT_COLOR, zorder=6, s=70)
        lbl = (labels[i] if labels and i < len(labels) else
               default[i] if i < len(default) else '')
        if lbl:
            ax.annotate(lbl, (r, 0), textcoords='offset points',
                        xytext=(0, 9), fontsize=9, color=ROOT_COLOR, fontweight='bold')
    return roots


def mark_pt(ax, x, y, label='', color=PT_COLOR, xytext=(6, 6)):
    ax.scatter([x], [y], color=color, zorder=6, s=70)
    if label:
        ax.annotate(label, (x, y), textcoords='offset points',
                    xytext=xytext, fontsize=9, color=color, fontweight='bold')


def intersections_para_line(a, b, c, m, n):
    """Return sorted list of (x, y) intersections of parabola and line."""
    # a*x^2 + (b-m)*x + (c-n) = 0
    A2, B2, C2 = a, b - m, c - n
    disc = B2**2 - 4 * A2 * C2
    if disc < -1e-9:
        return []
    if abs(disc) < 1e-9:
        x0 = -B2 / (2 * A2)
        return [(x0, m * x0 + n)]
    sq = np.sqrt(disc)
    xs = sorted([(-B2 + sq) / (2 * A2), (-B2 - sq) / (2 * A2)])
    return [(x, m * x + n) for x in xs]


def intersections_two_paras(a1, b1, c1, a2, b2, c2):
    return intersections_para_line(a1 - a2, b1 - b2, c1 - c2, 0, 0)


def save_fig(fig, sub, n):
    fname = f"8_{sub}_ex{n:02d}.png"
    path  = os.path.join(IMAGES_DIR, fname)
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  {fname}")


def shade_signs(ax, a, b, c, xlim):
    roots = get_roots(a, b, c)
    x = np.linspace(xlim[0], xlim[1], 700)
    y = py(a, b, c, x)
    if len(roots) == 2:
        r1, r2 = roots[0], roots[1]
        if a > 0:
            ax.fill_between(x, 0, y, where=(x <= r1) | (x >= r2),
                            alpha=0.18, color=POS_COLOR, label='חיובית')
            ax.fill_between(x, 0, y, where=(x >= r1) & (x <= r2),
                            alpha=0.18, color=NEG_COLOR, label='שלילית')
        else:
            ax.fill_between(x, 0, y, where=(x >= r1) & (x <= r2),
                            alpha=0.18, color=POS_COLOR, label='חיובית')
            ax.fill_between(x, 0, y, where=(x <= r1) | (x >= r2),
                            alpha=0.18, color=NEG_COLOR, label='שלילית')
    elif len(roots) == 0:
        color = POS_COLOR if (a > 0) else NEG_COLOR
        ax.fill_between(x, 0, y, alpha=0.18, color=color)


def shade_incr_decr(ax, a, b, c, xlim):
    xv, _ = vertex(a, b, c)
    x = np.linspace(xlim[0], xlim[1], 700)
    y = py(a, b, c, x)
    ybase = np.min(y) - abs(np.min(y)) * 0.05 - 0.5
    ytop  = np.max(y) + abs(np.max(y)) * 0.05 + 0.5
    if a > 0:
        ax.fill_between(x, ybase, y, where=(x <= xv),
                        alpha=0.15, color=DEC_COLOR, label='יורדת')
        ax.fill_between(x, ybase, y, where=(x >= xv),
                        alpha=0.15, color=INC_COLOR, label='עולה')
    else:
        ax.fill_between(x, y, ytop, where=(x <= xv),
                        alpha=0.15, color=INC_COLOR, label='עולה')
        ax.fill_between(x, y, ytop, where=(x >= xv),
                        alpha=0.15, color=DEC_COLOR, label='יורדת')


def draw_triangle(ax, pts, color='#4393C3', alpha=0.2, lw=1.5):
    tri = Polygon(pts, closed=True, facecolor=color, edgecolor='#2166AC',
                  alpha=alpha, linewidth=lw)
    ax.add_patch(tri)


def draw_trapezoid(ax, pts, color='#92C5DE', alpha=0.25, lw=1.5):
    trap = Polygon(pts, closed=True, facecolor=color, edgecolor='#2166AC',
                   alpha=alpha, linewidth=lw)
    ax.add_patch(trap)


# ═══════════════════════════════════════════════════════════════════════════════
#  SUBTOPIC 1.2  –  Role of parameter a (direction of parabola)
# ═══════════════════════════════════════════════════════════════════════════════

def gen_1_2():
    sub = '1.2'
    print(f"\n── Subtopic {sub} ──")

    # ex01: 4 parabolas showing a>0 (up) and a<0 (down)
    n = 1
    fig, ax = make_fig()
    setup_axes(ax)
    xl = (-4, 4)
    x = np.linspace(*xl, 500)
    ax.plot(x, 3*x**2,      color=PARA_COLOR,  lw=2, label='y=3x²  ▲')
    ax.plot(x, -2*x**2,     color=LINE_COLOR,  lw=2, label='y=−2x²  ▼')
    ax.plot(x, x**2 + 5,    color=PARA2_COLOR, lw=2, label='y=x²+5  ▲')
    ax.plot(x, -x**2 - 3,   color=PARA3_COLOR, lw=2, label='y=−x²−3 ▼')
    ax.set_xlim(*xl); ax.set_ylim(-20, 20)
    ax.legend(fontsize=7, loc='upper center')
    ax.set_title('פרמטר a: כיוון הפרבולה', fontsize=10)
    save_fig(fig, sub, n)

    # ex02: y=4x² vs y=−4x²
    n = 2
    fig, ax = make_fig(); setup_axes(ax)
    xl = (-3, 3); x = np.linspace(*xl, 500)
    ax.plot(x,  4*x**2, color=PARA_COLOR, lw=2, label='y=4x²  (a=4>0)')
    ax.plot(x, -4*x**2, color=LINE_COLOR, lw=2, label='y=−4x² (a=−4<0)')
    ax.scatter([2], [16],  color=PARA_COLOR, s=70, zorder=5)
    ax.scatter([2], [-16], color=LINE_COLOR, s=70, zorder=5)
    ax.annotate('(2,16)',  (2, 16),  textcoords='offset points', xytext=(5, 3),  fontsize=8)
    ax.annotate('(2,−16)', (2, -16), textcoords='offset points', xytext=(5, -10), fontsize=8)
    ax.set_xlim(*xl); ax.set_ylim(-40, 40)
    ax.legend(fontsize=8); ax.set_title('a=4 לעומת a=−4', fontsize=10)
    save_fig(fig, sub, n)

    # ex03: y=2x² with table points
    n = 3
    fig, ax = make_fig(); setup_axes(ax)
    xl = (-3, 3); x = np.linspace(*xl, 500)
    ax.plot(x, 2*x**2, color=PARA_COLOR, lw=2, label='y=2x²')
    for xi in [-2, -1, 0, 1, 2]:
        yi = 2*xi**2
        ax.scatter([xi], [yi], color=ROOT_COLOR, s=70, zorder=5)
        ax.annotate(f'({xi},{yi})', (xi, yi), textcoords='offset points',
                    xytext=(5, 4), fontsize=7)
    ax.set_xlim(*xl); ax.set_ylim(-2, 12)
    ax.legend(fontsize=8); ax.set_title('y=2x² – טבלת ערכים', fontsize=10)
    save_fig(fig, sub, n)

    # ex04: y=−2x² with table points
    n = 4
    fig, ax = make_fig(); setup_axes(ax)
    xl = (-3, 3); x = np.linspace(*xl, 500)
    ax.plot(x, -2*x**2, color=LINE_COLOR, lw=2, label='y=−2x²')
    for xi in [-2, -1, 0, 1, 2]:
        yi = -2*xi**2
        ax.scatter([xi], [yi], color=VTX_COLOR, s=70, zorder=5)
        ax.annotate(f'({xi},{yi})', (xi, yi), textcoords='offset points',
                    xytext=(5, -12), fontsize=7)
    ax.set_xlim(*xl); ax.set_ylim(-12, 2)
    ax.legend(fontsize=8); ax.set_title('y=−2x² – טבלת ערכים', fontsize=10)
    save_fig(fig, sub, n)

    # ex05: y=x², y=3x², y=½x²  – width comparison
    n = 5
    fig, ax = make_fig(); setup_axes(ax)
    xl = (-4, 4); x = np.linspace(*xl, 500)
    ax.plot(x, x**2,       color=PARA_COLOR,  lw=2, label='y=x²')
    ax.plot(x, 3*x**2,     color=LINE_COLOR,  lw=2, label='y=3x² (צרה)')
    ax.plot(x, 0.5*x**2,   color=PARA2_COLOR, lw=2, label='y=½x² (רחבה)')
    ax.scatter([2], [4],  color=PARA_COLOR,  s=50, zorder=5)
    ax.scatter([2], [12], color=LINE_COLOR,  s=50, zorder=5)
    ax.scatter([2], [2],  color=PARA2_COLOR, s=50, zorder=5)
    ax.set_xlim(*xl); ax.set_ylim(-1, 18)
    ax.legend(fontsize=8); ax.set_title('השוואת רוחב פרבולות (a שונה)', fontsize=10)
    save_fig(fig, sub, n)

    # ex06: y=−5x², max at (0,0)
    n = 6
    fig, ax = make_fig(); setup_axes(ax)
    xl = (-3, 3); x = np.linspace(*xl, 500)
    ax.plot(x, -5*x**2, color=LINE_COLOR, lw=2, label='y=−5x²')
    ax.scatter([0], [0], color=VTX_COLOR, s=90, zorder=6)
    ax.annotate('מקסימום (0,0)', (0, 0), textcoords='offset points',
                xytext=(8, 8), fontsize=9, color=VTX_COLOR, fontweight='bold')
    ax.set_xlim(*xl); ax.set_ylim(-50, 10)
    ax.legend(fontsize=8); ax.set_title('y=−5x²,  a<0 → מקסימום', fontsize=10)
    save_fig(fig, sub, n)

    # ex07: y=x² vs y=−x²
    n = 7
    fig, ax = make_fig(); setup_axes(ax)
    xl = (-4, 4); x = np.linspace(*xl, 500)
    ax.plot(x,  x**2, color=PARA_COLOR, lw=2, label='y=x²  (a>0, מינימום)')
    ax.plot(x, -x**2, color=LINE_COLOR, lw=2, label='y=−x² (a<0, מקסימום)')
    ax.axhline(0, color='black', lw=0.8)
    ax.set_xlim(*xl); ax.set_ylim(-16, 16)
    ax.legend(fontsize=8); ax.set_title('y=x² לעומת y=−x²', fontsize=10)
    save_fig(fig, sub, n)

    # ex08: 4 parabolas with a values labeled
    n = 8
    fig, ax = make_fig(); setup_axes(ax)
    xl = (-3, 3); x = np.linspace(*xl, 500)
    ax.plot(x, 7*x**2 - 3*x + 1,    color=PARA_COLOR,  lw=2, label='a=7')
    ax.plot(x, -(1/3)*x**2 + x,      color=LINE_COLOR,  lw=2, label='a=−⅓')
    ax.plot(x, x**2,                  color=PARA2_COLOR, lw=2, label='a=1')
    ax.plot(x, -x**2 - 2*x,          color=PARA3_COLOR, lw=2, label='a=−1')
    ax.set_xlim(*xl); ax.set_ylim(-8, 20)
    ax.legend(fontsize=8); ax.set_title('ערכי הפרמטר a', fontsize=10)
    save_fig(fig, sub, n)

    # ex09: y=2x², y=5x², y=⅓x² at x=3
    n = 9
    fig, ax = make_fig(); setup_axes(ax)
    xl = (-4, 4); x = np.linspace(*xl, 500)
    ax.plot(x, 2*x**2,      color=PARA_COLOR,  lw=2, label='y=2x²  (y=18 at x=3)')
    ax.plot(x, 5*x**2,      color=LINE_COLOR,  lw=2, label='y=5x²  (y=45 at x=3)')
    ax.plot(x, (1/3)*x**2,  color=PARA2_COLOR, lw=2, label='y=⅓x²  (y=3 at x=3)')
    ax.axvline(3, color='gray', lw=1, ls=':')
    ax.scatter([3, 3, 3], [18, 45, 3], color=['blue','red','green'], s=60, zorder=5)
    ax.set_xlim(*xl); ax.set_ylim(-2, 55)
    ax.legend(fontsize=7); ax.set_title('סדר לפי רוחב: a=5 צרה, a=⅓ רחבה', fontsize=9)
    save_fig(fig, sub, n)

    # ex10: y=−x² vs y=−3x²
    n = 10
    fig, ax = make_fig(); setup_axes(ax)
    xl = (-3, 3); x = np.linspace(*xl, 500)
    ax.plot(x, -x**2,  color=PARA_COLOR, lw=2, label='y=−x²  (a=−1)')
    ax.plot(x, -3*x**2, color=LINE_COLOR, lw=2, label='y=−3x² (a=−3, צרה יותר)')
    ax.scatter([2], [-4],  color=PARA_COLOR, s=60, zorder=5)
    ax.scatter([2], [-12], color=LINE_COLOR, s=60, zorder=5)
    ax.annotate('(2,−4)',  (2, -4),  textcoords='offset points', xytext=(5,  3), fontsize=8)
    ax.annotate('(2,−12)', (2, -12), textcoords='offset points', xytext=(5, -12), fontsize=8)
    ax.set_xlim(*xl); ax.set_ylim(-30, 5)
    ax.legend(fontsize=8); ax.set_title('a<0: −3x² צרה מ−x²', fontsize=10)
    save_fig(fig, sub, n)

    # ex11: y=3x² passes through (2,12)
    n = 11
    fig, ax = make_fig(); setup_axes(ax)
    xl = (-4, 4); x = np.linspace(*xl, 500)
    ax.plot(x, 3*x**2, color=PARA_COLOR, lw=2, label='y=3x²  (a=3)')
    ax.scatter([2], [12], color=ROOT_COLOR, s=90, zorder=6)
    ax.annotate('(2,12)', (2, 12), textcoords='offset points', xytext=(6, 3), fontsize=9,
                color=ROOT_COLOR, fontweight='bold')
    ax.axhline(12, color='gray', lw=0.8, ls=':')
    ax.axvline(2,  color='gray', lw=0.8, ls=':')
    ax.set_xlim(*xl); ax.set_ylim(-2, 50)
    ax.legend(fontsize=8); ax.set_title('y=3x² עוברת דרך (2,12)', fontsize=10)
    save_fig(fig, sub, n)

    # ex12: y=−3x² passes through (−3,−27)
    n = 12
    fig, ax = make_fig(); setup_axes(ax)
    xl = (-4, 4); x = np.linspace(*xl, 500)
    ax.plot(x, -3*x**2, color=LINE_COLOR, lw=2, label='y=−3x²  (a=−3)')
    ax.scatter([-3], [-27], color=VTX_COLOR, s=90, zorder=6)
    ax.annotate('(−3,−27)', (-3, -27), textcoords='offset points', xytext=(6, -4), fontsize=9,
                color=VTX_COLOR, fontweight='bold')
    ax.set_xlim(*xl); ax.set_ylim(-55, 5)
    ax.legend(fontsize=8); ax.set_title('y=−3x² עוברת דרך (−3,−27)', fontsize=10)
    save_fig(fig, sub, n)

    # ex13: y=2x² and y=−2x² as mirrors
    n = 13
    fig, ax = make_fig(); setup_axes(ax)
    xl = (-4, 4); x = np.linspace(*xl, 500)
    ax.plot(x,  2*x**2, color=PARA_COLOR, lw=2, label='y=2x²  (a=2)')
    ax.plot(x, -2*x**2, color=LINE_COLOR, lw=2, label='y=−2x² (a=−2)')
    ax.axhline(0, color='black', lw=1.0, ls='-')
    ax.fill_between(x, 2*x**2, -2*x**2, alpha=0.08, color='gray')
    ax.set_xlim(*xl); ax.set_ylim(-35, 35)
    ax.legend(fontsize=8); ax.set_title('מיראה ביחס לציר x: a ו−a', fontsize=10)
    save_fig(fig, sub, n)

    # ex14: downward parabola a<−1 (illustrative)
    n = 14
    fig, ax = make_fig(); setup_axes(ax)
    xl = (-3, 3); x = np.linspace(*xl, 500)
    for a_val, col in [(-2, PARA_COLOR), (-3, LINE_COLOR), (-5, PARA2_COLOR)]:
        ax.plot(x, a_val*x**2 - 3*x + 1, color=col, lw=2, label=f'a={a_val}')
    ax.set_xlim(*xl); ax.set_ylim(-50, 10)
    ax.legend(fontsize=8); ax.set_title('a < −1: פרבולה כלפי מטה', fontsize=10)
    save_fig(fig, sub, n)

    # ex15: y=−0.5x²+4x (projectile)
    n = 15
    fig, ax = make_fig(); setup_axes(ax)
    a, b, c = -0.5, 4, 0
    xl = xlim_auto(a, b, c)
    draw_para(ax, a, b, c, xl, PARA_COLOR)
    mark_vertex(ax, a, b, c, 'שיא')
    mark_roots(ax, a, b, c, ['יציאה', 'נחיתה'])
    setup_axes(ax)
    ax.set_xlim(*xl); ax.set_title('y=−0.5x²+4x – מסלול קשתי', fontsize=10)
    save_fig(fig, sub, n)

    # ex16: y=4x²−1 and y=¼x²−1
    n = 16
    fig, ax = make_fig(); setup_axes(ax)
    xl = (-3, 3); x = np.linspace(*xl, 500)
    ax.plot(x, 4*x**2   - 1, color=PARA_COLOR, lw=2, label='y=4x²−1  (a=4, צרה)')
    ax.plot(x, 0.25*x**2 - 1, color=LINE_COLOR, lw=2, label='y=¼x²−1  (a=¼, רחבה)')
    ax.scatter([0], [-1], color=ROOT_COLOR, s=80, zorder=6)
    ax.annotate('(0,−1)', (0, -1), textcoords='offset points', xytext=(6, -12), fontsize=8,
                color=ROOT_COLOR, fontweight='bold')
    ax.set_xlim(*xl); ax.set_ylim(-5, 35)
    ax.legend(fontsize=8); ax.set_title('השוואה: a=4 vs a=¼', fontsize=10)
    save_fig(fig, sub, n)

    # ex17: y=−2x² through (3,−18)
    n = 17
    fig, ax = make_fig(); setup_axes(ax)
    xl = (-5, 5); x = np.linspace(*xl, 500)
    ax.plot(x, -2*x**2, color=PARA_COLOR, lw=2, label='y=−2x²  (a=−2)')
    ax.scatter([3], [-18], color=VTX_COLOR, s=90, zorder=6)
    ax.annotate('(3,−18)', (3, -18), textcoords='offset points', xytext=(6, -4), fontsize=9,
                color=VTX_COLOR, fontweight='bold')
    ax.axhline(-18, color='gray', lw=0.8, ls=':')
    ax.axvline(3,   color='gray', lw=0.8, ls=':')
    ax.scatter([0], [0], color=ROOT_COLOR, s=80, zorder=5)
    ax.set_xlim(*xl); ax.set_ylim(-60, 5)
    ax.legend(fontsize=8); ax.set_title('y=−2x², a=−2 (מעבר דרך (3,−18))', fontsize=10)
    save_fig(fig, sub, n)

    # ex18: y=3x²−5 and y=−3x²+5 with intersections
    n = 18
    fig, ax = make_fig(); setup_axes(ax)
    xl = (-3, 3); x = np.linspace(*xl, 500)
    ax.plot(x, 3*x**2 - 5,  color=PARA_COLOR, lw=2, label='y=3x²−5  (a=3)')
    ax.plot(x, -3*x**2 + 5, color=LINE_COLOR, lw=2, label='y=−3x²+5 (a=−3)')
    xi = np.sqrt(5/3)
    yi = 3*(5/3) - 5  # = 0
    ax.scatter([xi, -xi], [yi, yi], color=ROOT_COLOR, s=80, zorder=6)
    ax.annotate(f'(√(5/3), 0)', (xi, 0), textcoords='offset points', xytext=(4, 8), fontsize=7,
                color=ROOT_COLOR)
    ax.annotate(f'(−√(5/3), 0)', (-xi, 0), textcoords='offset points', xytext=(-80, 8), fontsize=7,
                color=ROOT_COLOR)
    ax.set_xlim(*xl); ax.set_ylim(-20, 20)
    ax.legend(fontsize=8); ax.set_title('y=3x²−5 ו y=−3x²+5', fontsize=10)
    save_fig(fig, sub, n)

    # ex19: y=x²+3 vertex at (0,3)
    n = 19
    fig, ax = make_fig(); setup_axes(ax)
    xl = (-4, 4); x = np.linspace(*xl, 500)
    ax.plot(x, x**2 + 3, color=PARA_COLOR, lw=2, label='y=x²+3')
    ax.scatter([0], [3], color=VTX_COLOR, s=90, zorder=6)
    ax.annotate('קודקוד (0,3)', (0, 3), textcoords='offset points', xytext=(8, 4),
                fontsize=9, color=VTX_COLOR, fontweight='bold')
    ax.axvline(0, color='purple', ls='--', lw=1.0, alpha=0.6)
    ax.set_xlim(*xl); ax.set_ylim(-1, 22)
    ax.legend(fontsize=8); ax.set_title('y=x²+3, a=1 (מ-a=1, c=3)', fontsize=10)
    save_fig(fig, sub, n)

    # ex20: y=−2x²+8x (projectile max at (2,8))
    n = 20
    fig, ax = make_fig(); setup_axes(ax)
    a, b, c = -2, 8, 0
    xl = xlim_auto(a, b, c)
    draw_para(ax, a, b, c, xl, PARA_COLOR)
    xv, yv = mark_vertex(ax, a, b, c, 'שיא')
    mark_roots(ax, a, b, c, ['t=0', 't=4'])
    setup_axes(ax)
    ax.set_xlim(*xl); ax.set_title('y=−2x²+8x – גובה מקסימלי '+str(int(yv)), fontsize=10)
    save_fig(fig, sub, n)


# ═══════════════════════════════════════════════════════════════════════════════
#  SUBTOPIC 2.2  –  x-intercepts (roots)
# ═══════════════════════════════════════════════════════════════════════════════

def gen_2_2():
    sub = '2.2'
    print(f"\n── Subtopic {sub} ──")

    exercises = [
        # (a, b, c, line_m, line_n, title)
        ( 1, -5,  6,  None, None, 'y=x²−5x+6'),
        ( 1,  1,-12,  None, None, 'y=x²+x−12'),
        ( 1,  0, -9,  None, None, 'y=x²−9'),
        ( 1, -7, 10,  None, None, 'y=x²−7x+10'),
        ( 2, -5,  2,  None, None, 'y=2x²−5x+2'),
        ( 1, -6,  9,  None, None, 'y=x²−6x+9 (כפול)'),
        ( 1, -4,  0,  None, None, 'y=x²−4x'),
        ( 1,  2, -8,  None, None, 'y=x²+2x−8'),
        ( 1,  1,-12,  None, None, 'y=x²+x−12'),
        (-1,  8,-11,  None, None, 'y=−x²+8x−11'),
        ( 1, -2, -4,  None, None, 'y=x²−2x−4'),
        (-0.5, 5,-12.5, None, None,'y=−½x²+5x−12.5'),
        ( 1, -2,-35,  None, None, 'y=x²−2x−35'),
        ( 1, -5, -1,  None, None, 'y=x²−5x−1'),
        (-1,  4,  0,  None, None, 'y=−x²+4x'),
        (-1,  6,  0,  None, None, 'h=−t²+6t'),
        ( 1, -2, -4,   1,   6,   'y=x²−2x−4 ו y=x+6'),
        ( 1,  1,-12,  None, None, 'y=x²+x−12 (מה"ט)'),
        ( 1, -5, -1,  -3,   7,   'y=x²−5x−1 ו y=−3x+7'),
        (-1,  8, -9,   1,   1,   'y=−x²+8x−9 ו y=x+1'),
    ]

    for i, (a, b, c, lm, ln, title) in enumerate(exercises):
        n = i + 1
        fig, ax = make_fig()
        xl = xlim_auto(a, b, c, m2=lm, n2=ln if lm is not None else None)
        draw_para(ax, a, b, c, xl)
        if lm is not None:
            draw_line(ax, lm, ln, xl)
            pts = intersections_para_line(a, b, c, lm, ln)
            labels = ['A', 'B']
            for k, (px, py_) in enumerate(pts):
                mark_pt(ax, px, py_, labels[k] if k < 2 else '', ROOT_COLOR)
            if n in (19, 20):
                mark_vertex(ax, a, b, c, 'C')
        else:
            mark_roots(ax, a, b, c)
            mark_vertex(ax, a, b, c)
        setup_axes(ax)
        ax.set_xlim(*xl)
        ax.set_title(title, fontsize=10)
        save_fig(fig, sub, n)


# ═══════════════════════════════════════════════════════════════════════════════
#  SUBTOPIC 2.3  –  Number of solutions & distance between roots
# ═══════════════════════════════════════════════════════════════════════════════

def gen_2_3():
    sub = '2.3'
    print(f"\n── Subtopic {sub} ──")

    exercises = [
        # (a,b,c, lm, ln, disc_info, title)
        ( 1,-4, 3, None,None, 'Δ=4>0, שתי נקודות'),
        ( 1,-4, 4, None,None, 'Δ=0, נקודה אחת'),
        ( 1,-4, 5, None,None, 'Δ=−4<0, אין נקודות'),
        ( 1,-4, 3, None,None, 'שלושה מצבים (Δ>0)'),  # representative
        ( 1, 6, 9, None,None, 'y=x²+6x+9, Δ=0'),
        ( 1, 1, 5, None,None, 'y=x²+x+5, Δ<0'),
        ( 1,-2,-15,None,None, 'מרחק 8: נק׳ (−3,0) ו(5,0)'),
        ( 1, -6,-16,None,None,'מרחק 10: x₁=−2, x₂=8'),
        ( 1,-2, -8,None,None, 'y=x²−2x−8, מרחק 6'),
        (-1, 6, -4,None,None, 'y=−x²+6x−4, מרחק 2√5'),
        ( 1, 4,  3, None,None,'y=x²+4x+k: k<4 שתי נקודות'),
        ( 1,-6,  9, None,None,'y=x²−6x+k: k=9 נקודה אחת'),
        ( 1,-2,-35,None,None, 'y=x²−2x−35, מרחק 12'),
        (-1,11,-24,None,None, 'y=−x²+11x−24, מרחק 5'),
        ( 2,-8,  6, None,None,'y=2x²−8x+6, מרחק 2'),
        ( 1,-6,  5, None,None,'פרבולה 1: y=x²−6x+5'),
        ( 1,-2, -4,  1,  6,  'y=x²−2x−4 ו y=x+6 + קודקוד'),
        ( 1,-5, -1, -3,  7,  'y=x²−5x−1 ו y=−3x+7'),
        (-1, 8,-11,  None,None,'שתי פרבולות: y=−x²+8x−11 ו (x−5)²'),
        ( 1,-6, 13, None,None,'שתי פרבולות: y=x²−6x+13 ו −x²+8x−7'),
    ]

    for i, row in enumerate(exercises):
        n = i + 1
        a, b, c = row[0], row[1], row[2]
        lm, ln  = row[3], row[4]
        title   = row[6] if len(row) > 6 else row[5]

        fig, ax = make_fig()

        if n == 19:
            # two parabolas: y=−x²+8x−11 and y=(x−5)²
            a2,b2,c2 = 1,-10,25
            xl = (-1, 9)
            draw_para(ax, -1, 8,-11, xl, PARA_COLOR, label='y=−x²+8x−11')
            draw_para(ax,  1,-10, 25, xl, LINE_COLOR, label='y=(x−5)²')
            pts = intersections_two_paras(-1,8,-11, 1,-10,25)
            for k,(px,pyv) in enumerate(pts):
                mark_pt(ax, px, pyv, chr(65+k), ROOT_COLOR)
            setup_axes(ax); ax.set_xlim(*xl)
            ax.legend(fontsize=8)
        elif n == 20:
            # two parabolas
            xl = (-1, 9)
            draw_para(ax, 1,-6,13, xl, PARA_COLOR, label='y=x²−6x+13')
            draw_para(ax,-1, 8,-7, xl, LINE_COLOR,  label='y=−x²+8x−7')
            pts = intersections_two_paras(1,-6,13,-1,8,-7)
            for k,(px,pyv) in enumerate(pts):
                mark_pt(ax, px, pyv, chr(65+k), ROOT_COLOR)
            setup_axes(ax); ax.set_xlim(*xl)
            ax.legend(fontsize=8)
        elif n == 16:
            # two separate parabolas on same axes
            xl = (-2, 8)
            draw_para(ax, 1,-6, 5, xl, PARA_COLOR, label='y=x²−6x+5')
            draw_para(ax,-1, 4,-3, xl, LINE_COLOR, label='y=−x²+4x−3')
            for aa,bb,cc,col in [(1,-6,5,PARA_COLOR),(-1,4,-3,LINE_COLOR)]:
                for r in get_roots(aa,bb,cc):
                    ax.scatter([r],[0],color=col,s=60,zorder=5)
            setup_axes(ax); ax.set_xlim(*xl)
            ax.legend(fontsize=8)
        elif lm is not None:
            xl = xlim_auto(a, b, c, m2=lm, n2=ln)
            draw_para(ax, a, b, c, xl)
            draw_line(ax, lm, ln, xl)
            pts = intersections_para_line(a, b, c, lm, ln)
            for k,(px,pyv) in enumerate(pts):
                mark_pt(ax, px, pyv, chr(65+k), ROOT_COLOR)
            # vertex C
            xv,yv = mark_vertex(ax, a, b, c, 'C')
            setup_axes(ax); ax.set_xlim(*xl)
        else:
            xl = xlim_auto(a, b, c)
            draw_para(ax, a, b, c, xl)
            roots = mark_roots(ax, a, b, c)
            mark_vertex(ax, a, b, c)
            # annotate distance
            if len(roots) == 2:
                dist = abs(roots[1] - roots[0])
                mid  = (roots[0] + roots[1]) / 2
                ax.annotate(f'd={dist:.2g}', (mid, 0),
                            textcoords='offset points', xytext=(0, -16), fontsize=8,
                            ha='center', color='darkblue')
            setup_axes(ax); ax.set_xlim(*xl)

        ax.set_title(title, fontsize=9)
        save_fig(fig, sub, n)


# ═══════════════════════════════════════════════════════════════════════════════
#  SUBTOPIC 3.1  –  x-coordinate of vertex & axis of symmetry
# ═══════════════════════════════════════════════════════════════════════════════

def gen_3_1():
    sub = '3.1'
    print(f"\n── Subtopic {sub} ──")

    exercises = [
        (1,-4, 1, None,None, 'y=x²−4x+1'),
        (1, 6, 5, None,None, 'y=x²+6x+5'),
        (-1,8,-3, None,None, 'y=−x²+8x−3'),
        (2,-12,7, None,None, 'y=2x²−12x+7'),
        (1, 1,-12,None,None, 'y=x²+x−12'),
        (-1,2, 8, None,None, 'y=−x²+2x+8'),
        (4,-16,3, None,None, 'y=4x²−16x+3'),
        (1,-2,-35,None,None, 'y=x²−2x−35'),
        (2,-8, 3, None,None, 'y=2x²−8x+3'),
        (-1,6,-4, None,None, 'y=−x²+6x−4'),
        (1, 6, 0, None,None, 'y=x²+bx+c, ציר x=−3'),
        (1,-8, 7, None,None, 'שורשים (1,0) ו-(7,0)'),
        (1,-2,-15,None,None, 'שורשים (−3,0) ו-(5,0)'),
        (1,-2,-4, None,None, 'y=x²−2x−4'),
        (1,-4, 5, None,None, 'ציר x=2, עוברת דרך (0,5)'),
        (1, 4,-12,None,None, 'y=x²+4x−12'),
        (1, 1,-12,None,None, 'y=x²+x−12'),
        (1,-2,-4,  1,  6,   'y=x²−2x−4 ו-y=x+6'),
        (-1,4,  0, None,None,'y=−x²+4x'),
        (1,-6, 13, None,None,'y=x²−6x+13 ו-y=−x²+8x−7'),
    ]

    for i, (a, b, c, lm, ln, title) in enumerate(exercises):
        n = i + 1
        fig, ax = make_fig()

        if n == 20:
            xl = (-1, 9)
            draw_para(ax, 1,-6,13, xl, PARA_COLOR, label='y=x²−6x+13')
            draw_para(ax,-1, 8,-7, xl, LINE_COLOR,  label='y=−x²+8x−7')
            mark_vertex(ax,1,-6,13,'V₁')
            mark_vertex(ax,-1,8,-7,'V₂', color='orange')
            setup_axes(ax); ax.set_xlim(*xl); ax.legend(fontsize=8)
        elif lm is not None:
            xl = xlim_auto(a,b,c,m2=lm,n2=ln)
            draw_para(ax,a,b,c,xl)
            draw_line(ax,lm,ln,xl)
            pts = intersections_para_line(a,b,c,lm,ln)
            for k,(px,pyv) in enumerate(pts):
                mark_pt(ax,px,pyv,chr(65+k),ROOT_COLOR)
            mark_vertex(ax,a,b,c,'C')
            setup_axes(ax); ax.set_xlim(*xl)
        else:
            xl = xlim_auto(a,b,c)
            draw_para(ax,a,b,c,xl)
            mark_roots(ax,a,b,c)
            mark_vertex(ax,a,b,c)
            setup_axes(ax); ax.set_xlim(*xl)

        ax.set_title(title, fontsize=9)
        save_fig(fig, sub, n)


# ═══════════════════════════════════════════════════════════════════════════════
#  SUBTOPIC 3.2  –  y-coordinate of vertex (min/max)
# ═══════════════════════════════════════════════════════════════════════════════

def gen_3_2():
    sub = '3.2'
    print(f"\n── Subtopic {sub} ──")

    exercises = [
        (1,-6, 5, None,None, 'y=x²−6x+5, V=(3,−4) מינימום'),
        (1, 4,-3, None,None, 'y=x²+4x−3, V=(−2,−7) מינימום'),
        (-1,2, 3, None,None, 'y=−x²+2x+3, V=(1,4) מקסימום'),
        (2,-4, 1, None,None, 'y=2x²−4x+1, V=(1,−1) מינימום'),
        (1,-4, 5, None,None, 'y=x²−4x+5, V=(2,1) מינימום'),
        (-1,4, 0, None,None, 'y=−x²+4x, V=(2,4) מקסימום'),
        (1,-4, 3, None,None, 'a>0 → מינימום (כלל)'),
        (1,-2,-35,None,None, 'y=x²−2x−35, V=(1,−36)'),
        (2,-12,10,None,None, 'y=2x²−12x+10, V=(3,−8) מינימום'),
        (-2,8,-3, None,None, 'y=−2x²+8x−3, V=(2,5) מקסימום'),
        (-1,10,-16,None,None,'P(x)=−x²+10x−16, V=(5,9) מקס'),
        (1,-2,-4, None,None, 'y=x²−2x−4, V=(1,−5)'),
        (-1,3, 4, None,None, 'y=−x²+3x+4, V=(1.5,6.25) מקס'),
        (1, 6, 5, None,None, 'y=x²+6x+5 (b=6), V=(−3,−4)'),
        (-8,16,-6,None,None, 'y=−8x²+16x−6, V=(1,2) מקס'),
        (1,-6,13, None,None, 'y=x²−6x+13, V=(3,4) מינ'),
        (-1,4, 0, None,None, 'y=−x²+4x, V=(2,4), f(x)=3 ?'),
        (1,-1,-2, None,None, 'y=x²−x−2, V=(½,−9/4)'),
        (1,-4, 5, None,None, 'y=x²−4x+5, A(0,5) B(4,5) C'),
        (-8,16,-6,None,None, 'y=−8x²+16x−6, שורשים ½,3/2'),
    ]

    for i, (a, b, c, lm, ln, title) in enumerate(exercises):
        n = i + 1
        fig, ax = make_fig()
        xl = xlim_auto(a, b, c)
        draw_para(ax, a, b, c, xl)
        vlabel = 'C' if n == 19 else 'V'
        xv, yv = mark_vertex(ax, a, b, c, label=vlabel)
        mark_roots(ax, a, b, c)

        # Extra: annotate min/max value
        minmax = 'מינימום' if a > 0 else 'מקסימום'
        ax.annotate(f'{minmax}: y={yv:.3g}', (xv, yv),
                    textcoords='offset points', xytext=(-50, 18 if a > 0 else -22),
                    fontsize=8, color=VTX_COLOR,
                    arrowprops=dict(arrowstyle='->', color=VTX_COLOR, lw=0.8))

        # For ex17: mark y=3 line and intersections
        if n == 17:
            draw_line(ax, 0, 3, xl, color='orange', lw=1.5, label='y=3')
            pts17 = intersections_para_line(a, b, c, 0, 3)
            for px, pyv in pts17:
                mark_pt(ax, px, pyv, '', ROOT_COLOR)
            ax.legend(fontsize=8)

        # For ex19: mark A, B on y=5 level
        if n == 19:
            ax.axhline(5, color='orange', ls='--', lw=1.2)
            mark_pt(ax, 0, 5, 'A', SYM_COLOR)
            mark_pt(ax, 4, 5, 'B', SYM_COLOR)

        setup_axes(ax)
        ax.set_xlim(*xl)
        ax.set_title(title, fontsize=9)
        save_fig(fig, sub, n)


# ═══════════════════════════════════════════════════════════════════════════════
#  SUBTOPIC 3.3  –  Symmetric point on parabola
# ═══════════════════════════════════════════════════════════════════════════════

def gen_3_3():
    sub = '3.3'
    print(f"\n── Subtopic {sub} ──")

    def draw_sym_pair(ax, a, b, c, px, plabel='P', splabel="P'",
                      show_roots=True, show_vertex=True):
        xl = xlim_auto(a, b, c, extra=[px])
        draw_para(ax, a, b, c, xl)
        xv, _ = vertex(a, b, c)
        ppy = py(a, b, c, px)
        sym_x = 2 * xv - px
        spy = py(a, b, c, sym_x)
        mark_pt(ax, px, ppy, plabel, PT_COLOR)
        mark_pt(ax, sym_x, spy, splabel, SYM_COLOR, xytext=(6, 6))
        ax.axvline(xv, color='purple', ls='--', lw=1.2, alpha=0.7,
                   label=f'ציר x={xv:.2g}')
        if abs(ppy - spy) < 0.01:
            ax.annotate('', (sym_x, spy), (px, ppy),
                        arrowprops=dict(arrowstyle='<->', color='purple', lw=1.0))
        if show_roots:
            mark_roots(ax, a, b, c)
        if show_vertex:
            mark_vertex(ax, a, b, c)
        setup_axes(ax)
        ax.set_xlim(*xl)
        ax.legend(fontsize=8)
        return xl

    sym_specs = {
        1:  (1, -6,  5,   1, 'P', "P'", False, False, 'ציר x=3, P ב-x=1, סימטרית ב-x=5'),
        2:  (1, -10, 24,  2, 'P', "P'", False, False, 'ציר x=5, P ב-x=2, סימטרית ב-x=8'),
        3:  (-1, -2, 3,   4, 'P', "P'", False, False, 'ציר x=−1, P ב-x=4, סימטרית ב-x=−6'),
        5:  (1, -4,  3,   0, 'A', "A'", True,  True,  'y=x²−4x+3: A(0,3) ↔ A′(4,3)'),
        6:  (1, -6,  5,   1, 'P', "P'", True,  True,  'y=x²−6x+5: (1,0) ↔ (5,0)'),
        7:  (-1, 2,  8,  -1, 'P', "P'", True,  True,  'y=−x²+2x+8: (−1,5) ↔ (3,5)'),
        8:  (1, -2, -35, -5, 'A', "A'", True,  True,  'y=x²−2x−35: A(−5,0) ↔ (7,0)'),
        9:  (1, -8,  7,   1, 'P', "P'", True,  True,  'y=x²−8x+7: (1,0) ↔ (7,0)'),
        10: (1, -4,  5,   0, 'A', "A'", True,  True,  'y=x²−4x+5: A(0,5) ↔ A′(4,5)'),
        11: (-1, 6, -5,   1, 'P', "P'", True,  True,  'y=−x²+6x−5: (1,0) ↔ (5,0)'),
        12: (1,  2, -8,   2, 'P', "P'", True,  True,  'y=x²+2x−8: P(2,0) ↔ (−4,0)'),
        13: (1, -2, -4,   0, 'P', "P'", True,  True,  'y=x²−2x−4: (0,−4) ↔ (2,−4)'),
        14: (2, -8,  3,   0, 'B', "B'", True,  True,  'y=2x²−8x+3: B(0,3) ↔ B′(4,3)'),
        15: (1, -6,  8,   1, 'A', 'B',  True,  True,  'y=x²−6x+8: A(1,3) ↔ B(5,3)'),
        16: (-1, 8, -7,   1, 'C', "C'", True,  True,  'y=−x²+8x−7: C(1,0) ↔ (7,0)'),
    }

    for n in range(1, 21):
        fig, ax = make_fig()

        if n == 4:
            xl = (-4, 4)
            draw_para(ax, 1, 0, 0, xl)
            mark_pt(ax, -2, 4, 'P', PT_COLOR)
            mark_pt(ax, 2, 4, "P'", SYM_COLOR, xytext=(6, 6))
            ax.axvline(0, color='purple', ls='--', lw=1.2, alpha=0.7, label='ציר x=0')
            ax.annotate('', (2, 4), (-2, 4),
                        arrowprops=dict(arrowstyle='<->', color='purple', lw=1.0))
            setup_axes(ax)
            ax.set_xlim(*xl)
            ax.legend(fontsize=8)
            ax.set_title('נקודות סימטריות: אותו שיעור y', fontsize=9)

        elif n == 17:
            a, b, c = 1, -4, 5
            xl = xlim_auto(a, b, c)
            draw_para(ax, a, b, c, xl)
            xv, yv = vertex(a, b, c)
            mark_pt(ax, 0, 5, 'A', PT_COLOR)
            mark_pt(ax, 4, 5, 'B', SYM_COLOR, xytext=(6, 6))
            mark_pt(ax, xv, yv, 'C', VTX_COLOR)
            ax.axvline(xv, color='purple', ls='--', lw=1.2, alpha=0.7,
                       label=f'ציר x={xv:.2g}')
            ax.annotate('', (4, 5), (0, 5),
                        arrowprops=dict(arrowstyle='<->', color='purple', lw=1.0))
            setup_axes(ax)
            ax.set_xlim(*xl)
            ax.legend(fontsize=8)
            ax.set_title('y=x²−4x+5: A(0,5), B(4,5), C(2,1)', fontsize=9)

        elif n == 18:
            xl = (-5, 6)
            draw_para(ax, 1, 0, 0, xl, PARA_COLOR, label='y=x²')
            draw_line(ax, 3, 4, xl, LINE_COLOR, label='y=3x+4')
            mark_pt(ax, -1, 1,  'A', ROOT_COLOR)
            mark_pt(ax,  4, 16, 'B', ROOT_COLOR)
            mark_pt(ax, -4, 16, 'C', SYM_COLOR, xytext=(6, 4))
            mark_pt(ax,  0, 0,  'D', VTX_COLOR)
            ax.scatter([0], [0], color=VTX_COLOR, s=80, zorder=6)
            ax.legend(fontsize=8)
            setup_axes(ax)
            ax.set_xlim(*xl)
            ax.set_title('y=x² ו y=3x+4: A(−1,1), B(4,16), C(−4,16)', fontsize=9)

        elif n == 19:
            a, b, c = 1, -5, -1
            xl = xlim_auto(a, b, c, extra=[-2, 4, 7], m2=-3, n2=7)
            draw_para(ax, a, b, c, xl)
            draw_line(ax, -3, 7, xl, LINE_COLOR, label='y=−3x+7')
            mark_pt(ax, -2, 13, 'A', PT_COLOR)
            mark_pt(ax,  4, -5, 'B', ROOT_COLOR)
            mark_pt(ax,  7, 13, "A'", SYM_COLOR, xytext=(6, 6))
            mark_pt(ax, -2,  0, 'D', 'gray', xytext=(6, -12))
            ax.axvline(2.5, color='purple', ls='--', lw=1.2, alpha=0.7, label='ציר x=5/2')
            ax.annotate('', (7, 13), (-2, 13),
                        arrowprops=dict(arrowstyle='<->', color='purple', lw=1.0))
            setup_axes(ax)
            ax.set_xlim(*xl)
            ax.legend(fontsize=8)
            ax.set_title('y=x²−5x−1, חיתוך עם y=−3x+7', fontsize=9)

        elif n == 20:
            a, b, c = -1, 2, 8
            xl = xlim_auto(a, b, c)
            draw_para(ax, a, b, c, xl)
            mark_pt(ax, -2, 0, 'A', ROOT_COLOR)
            mark_pt(ax,  4, 0, 'D', ROOT_COLOR, xytext=(6, 9))
            mark_pt(ax,  0, 8, 'B', PT_COLOR)
            mark_pt(ax,  2, 8, 'C', SYM_COLOR, xytext=(6, 6))
            ax.axvline(1, color='purple', ls='--', lw=1.2, alpha=0.7, label='ציר x=1')
            ax.annotate('', (2, 8), (0, 8),
                        arrowprops=dict(arrowstyle='<->', color='purple', lw=1.0))
            setup_axes(ax)
            ax.set_xlim(*xl)
            ax.legend(fontsize=8)
            ax.set_title('y=−x²+2x+8: A(−2,0), B(0,8), C(2,8), D(4,0)', fontsize=9)

        elif n in sym_specs:
            a, b, c, px, pl, sl, roots, vtx, title = sym_specs[n]
            draw_sym_pair(ax, a, b, c, px, pl, sl, roots, vtx)
            ax.set_title(title, fontsize=9)

        save_fig(fig, sub, n)


# ═══════════════════════════════════════════════════════════════════════════════
#  SUBTOPIC 4.1  –  Positive / negative domains
# ═══════════════════════════════════════════════════════════════════════════════

def gen_4_1():
    sub = '4.1'
    print(f"\n── Subtopic {sub} ──")

    exercises = [
        ( 1,-6, 5, None,None, 'y=(x−1)(x−5): חיובי מחוץ לשורשים'),
        ( 1,-2,-8, None,None, 'y=(x+2)(x−4): שלילי בין השורשים'),
        ( 1, 0,-9, None,None, 'y=x²−9: חיובי ב|x|>3'),
        ( 1, 4, 5, None,None, 'y=x²+4x+5: Δ<0, a>0 → חיובי תמיד'),
        (-1,-2,-3, None,None, 'y=−x²−2x−3: Δ<0, a<0 → שלילי תמיד'),
        ( 1,-4, 3, None,None, 'y=x²−4x+3: טבלת סימנים'),
        (-1, 0, 4, None,None, 'y=−x²+4: שלילי ב|x|>2'),
        ( 1,-2,-8, None,None, 'y=x²−2x−8: תחום חיוביות'),
        ( 1, 1,-12,None,None, 'y=x²+x−12: חיוביות ושליליות'),
        (-1, 6,-5, None,None, 'y=−x²+6x−5: חיוביות ושליליות'),
        ( 1,-2,-4, None,None, 'y=x²−2x−4: שורשי δ'),
        ( 1,-7,10, None,None, 'x²−7x+10>0: x<2 או x>5'),
        (-1, 5,-6, None,None, '−x²+5x−6≥0: 2≤x≤3'),
        ( 1,-1,-2, None,None, 'y=x²−x−2: שורשים −1,2'),
        (-1, 4, 0, None,None, 'y=−x²+4x: חיובי ב(0,4)'),
        (-1, 4, 0, None,None, 'f(x)=−x²+4x: f≥3 → 1≤x≤3'),
        ( 1, 1,-12,None,None, 'y=x²+x−12 (מה"ט): y<0'),
        ( 1,-1,-2, None,None, 'y=x²−x−2 (מה"ט): y≤0 ב[−2,3]'),
        (-1, 4, 0, None,None, 'f(x)=−x²+4x (מה"ט): f>0'),
        (-1, 6,-4, None,None, 'שתי פרבולות (מה"ט): חיוביות'),
    ]

    for i, (a, b, c, lm, ln, title) in enumerate(exercises):
        n = i + 1
        fig, ax = make_fig()

        if n == 20:
            xl = (-1, 9)
            draw_para(ax,-1, 6,-4, xl, PARA_COLOR, label='y=−x²+6x−4')
            draw_para(ax,-1,11,-24,xl, LINE_COLOR,  label='y=−x²+11x−24')
            for aa,bb,cc,col in [(-1,6,-4,PARA_COLOR),(-1,11,-24,LINE_COLOR)]:
                shade_signs(ax,aa,bb,cc,xl)
            setup_axes(ax); ax.set_xlim(*xl); ax.legend(fontsize=8)
        elif n == 16:
            xl = xlim_auto(a,b,c)
            draw_para(ax,a,b,c,xl)
            shade_signs(ax,a,b,c,xl)
            # mark y=3 line and 1≤x≤3 region
            draw_line(ax,0,3,xl,color='orange',lw=1.5,label='y=3')
            pts = intersections_para_line(a,b,c,0,3)
            for px,pyv in pts:
                mark_pt(ax,px,pyv,'',ROOT_COLOR)
            ax.legend(fontsize=8); setup_axes(ax); ax.set_xlim(*xl)
        else:
            xl = xlim_auto(a,b,c)
            draw_para(ax,a,b,c,xl)
            shade_signs(ax,a,b,c,xl)
            mark_roots(ax,a,b,c)
            mark_vertex(ax,a,b,c)
            ax.legend(fontsize=7, loc='upper center'); setup_axes(ax); ax.set_xlim(*xl)

        ax.set_title(title, fontsize=9)
        save_fig(fig, sub, n)


# ═══════════════════════════════════════════════════════════════════════════════
#  SUBTOPIC 4.2  –  Increasing / decreasing domains
# ═══════════════════════════════════════════════════════════════════════════════

def gen_4_2():
    sub = '4.2'
    print(f"\n── Subtopic {sub} ──")

    exercises = [
        ( 1,-4, 3, None,None, 'y=x²−4x+3: יורדת x<2, עולה x>2'),
        (-1, 6,-5, None,None, 'y=−x²+6x−5: עולה x<3, יורדת x>3'),
        ( 1, 0, 0, None,None, 'y=x²: עולה x>0, יורדת x<0'),
        ( 1,-10,21,None,None, 'y=x²−10x+21: ציר x=5'),
        (-2, 8,-1, None,None, 'y=−2x²+8x−1: ציר x=2'),
        ( 3, 6, 1, None,None, 'y=3x²+6x+1: ציר x=−1'),
        (-1,-4, 5, None,None, 'y=−x²−4x+5: V=(−2,9)'),
        ( 1,-4, 3, None,None, 'עלייה אחרי קודקוד (כלל)'),
        ( 1,-2,-35,None,None, 'y=x²−2x−35: V=(1,−36)'),
        (-1, 3, 4, None,None, 'y=−x²+3x+4: V=(1.5,6.25)'),
        ( 1, 1,-12,None,None, 'y=x²+x−12: V=(−½,−49/4)'),
        (-1, 4, 0, None,None, 'y=−x²+4x: כרטיס מידע'),
        ( 1,-6, 8, None,None, 'y=x²−6x+8: כרטיס מידע'),
        (-1, 4, 0, None,None, 'f(x)=−x²+4x: גם עולה וגם חיובית'),
        ( 1,-2,-8, None,None, 'y=x²−2x−8: גם יורדת וגם שלילית'),
        ( 1,-6, 5, None,None, 'שתי פרבולות: עליות שונות'),
        ( 1, 1,-12,None,None, 'y=x²+x−12 (מה"ט): תחום עלייה'),
        (-1, 4, 0, None,None, 'f(x)=−x²+4x (מה"ט): עולה'),
        ( 1,-6,13, None,None, 'שתי פרבולות (מה"ט)'),
        ( 1,-1,-2, None,None, 'y=x²−x−2: עולה ויורדת ב[−2,3]'),
    ]

    for i, (a, b, c, lm, ln, title) in enumerate(exercises):
        n = i + 1
        fig, ax = make_fig()

        if n == 16:
            xl = (-1, 8)
            draw_para(ax, 1,-6, 5, xl, PARA_COLOR, label='y=x²−6x+5')
            draw_para(ax,-1, 4,-3, xl, LINE_COLOR,  label='y=−x²+4x−3')
            shade_incr_decr(ax,1,-6,5,xl)
            setup_axes(ax); ax.set_xlim(*xl); ax.legend(fontsize=8)
        elif n == 19:
            xl = (-1, 9)
            draw_para(ax, 1,-6,13, xl, PARA_COLOR, label='y=x²−6x+13')
            draw_para(ax,-1, 8,-7, xl, LINE_COLOR,  label='y=−x²+8x−7')
            mark_vertex(ax,1,-6,13,'V₁')
            mark_vertex(ax,-1,8,-7,'V₂',color='orange')
            setup_axes(ax); ax.set_xlim(*xl); ax.legend(fontsize=8)
        else:
            xl = xlim_auto(a,b,c)
            draw_para(ax,a,b,c,xl)
            shade_incr_decr(ax,a,b,c,xl)
            mark_roots(ax,a,b,c)
            mark_vertex(ax,a,b,c)
            ax.legend(fontsize=7, loc='upper center'); setup_axes(ax); ax.set_xlim(*xl)

        ax.set_title(title, fontsize=9)
        save_fig(fig, sub, n)


# ═══════════════════════════════════════════════════════════════════════════════
#  SUBTOPIC 5.1  –  Intersection of parabola and line
# ═══════════════════════════════════════════════════════════════════════════════

def gen_5_1():
    sub = '5.1'
    print(f"\n── Subtopic {sub} ──")

    exercises = [
        (1, 0, 0,  0,  4,  'y=x² ו y=4: נקודות (±2,4)'),
        (1, 0, 0,  2,  0,  'y=x² ו y=2x: נקודות (0,0),(2,4)'),
        (1, 0,-1,  0,  3,  'y=x²−1 ו y=3: נקודות (±2,3)'),
        (1, 2, 0,  0,  0,  'y=x²+2x ו y=0: שורשים'),
        (1, 0,-4,  1,  2,  'y=x²−4 ו y=x+2'),
        (1, 0, 0,  1,  6,  'y=x² ו y=x+6'),
        (-1,0, 4, -1,  2,  'y=−x²+4 ו y=−x+2'),
        (1, 0, 3,  0,  4,  'y=x²+3 ו y=4: נקודות (±1,4)'),
        (1,-2,-4,  1,  6,  'y=x²−2x−4 ו y=x+6'),
        (1,-5,-1, -3,  7,  'y=x²−5x−1 ו y=−3x+7'),
        (-1,8,-9,  1,  1,  'y=−x²+8x−9 ו y=x+1'),
        (1, 0, 0,  3,  4,  'y=x² ו y=3x+4 + V(0,0)'),
        (-1,6,-4,  0,  0,  'שתי פרבולות: נקודת חיתוך אחת'),
        (1,-4, 3,  0, -1,  'y=x²−4x+3 ו y=k: מיקום k'),
        (1,-2,-8,  1, -2,  'y=x²−2x−8 ו y=x−2'),
        (-1,2, 8,  1,  4,  'y=−x²+2x+8 ו y=x+4'),
        (1,-2,-4,  1,  6,  'y=x²−2x−4 ו y=x+6 (מה"ט)'),
        (1, 0, 0,  3,  4,  'y=x² ו y=3x+4 (מה"ט)'),
        (1,-5,-1, -3,  7,  'y=x²−5x−1 ו y=−3x+7 (מה"ט)'),
        (-1,8,-9,  1,  1,  'y=−x²+8x−9 ו y=x+1 (מה"ט)'),
    ]

    for i, (a, b, c, lm, ln, title) in enumerate(exercises):
        n = i + 1
        fig, ax = make_fig()

        if n == 13:
            # two parabolas intersecting at (4,4)
            xl = (-1, 8)
            draw_para(ax,-1, 6,-4, xl, PARA_COLOR, label='y=−x²+6x−4')
            draw_para(ax,-1,11,-24,xl, LINE_COLOR,  label='y=−x²+11x−24')
            mark_pt(ax, 4, 4, 'A=(4,4)', ROOT_COLOR)
            setup_axes(ax); ax.set_xlim(*xl); ax.legend(fontsize=8)
        else:
            xl = xlim_auto(a, b, c, m2=lm, n2=ln)
            draw_para(ax, a, b, c, xl)
            draw_line(ax, lm, ln, xl)
            pts = intersections_para_line(a, b, c, lm, ln)
            labels = ['A', 'B', 'C']
            for k, (px, pyv) in enumerate(pts):
                mark_pt(ax, px, pyv, labels[k], ROOT_COLOR)

            if n in [12, 17, 18, 19, 20]:
                mark_vertex(ax, a, b, c, 'V' if n==12 else 'C')

            setup_axes(ax); ax.set_xlim(*xl)

        ax.set_title(title, fontsize=9)
        save_fig(fig, sub, n)


# ═══════════════════════════════════════════════════════════════════════════════
#  SUBTOPIC 5.2  –  Basic shifts of parabolas
# ═══════════════════════════════════════════════════════════════════════════════

def gen_5_2():
    sub = '5.2'
    print(f"\n── Subtopic {sub} ──")

    # Each entry: original y=x² (or other) + shifted version + title
    exercises = [
        # (orig_a,orig_b,orig_c, new_a,new_b,new_c, title)
        (1,0,0,  1,0, 3, 'y=x² → y=x²+3 (3 למעלה)'),
        (1,0,0,  1,-4, 4,'y=x² → y=(x−2)² (2 ימינה)'),
        (1,0,0,  1,-6,13,'y=x² → y=(x−3)²+4'),
        (1,0,0,  1, 2,-1,'y=x² → y=(x+1)²−2'),
        (1,0,0,  1,-6,11,'y=(x−3)²+2: V=(3,2)'),
        (1,0,0,  1, 4,-1,'y=(x+2)²−5: V=(−2,−5)'),
        (1,0,0,  1,-2, 1,'y=(x−1)²: V=(1,0)'),
        (1,0,0,  1,-6,11,'y=x²−6x+11=(x−3)²+2'),
        (1,0,0,  1,-6, 5,'y=(x−3)²−4: V=(3,−4)'),
        (1,0,0,  1,-10,25,'y=(x−5)²: V=(5,0)'),
        (1,0,0,  1,-4, 7,'y=(x−2)²+3 ← x²−4x+7'),
        (1,0,0,  1, 6, 5,'y=(x+3)²−4 ← x²+6x+5'),
        (1,0,0,  1,-6, 7,'y=(x−3)²−2: V=(3,−2)'),
        (1,-10,25,-1,8,-11,'שתי פרבולות: (x−5)² ו −x²+8x−11'),
        (1,0,0,  1,-8,12,'y=(x−4)²−4 ← x²−8x+12'),
        (1,0,0,  1,-6,13,'y=(x−3)²+4 ו y=−(x−4)²+9'),
        (1,0,0,  1,-6,13,'y=(x−3)²+4 (הזזה 3 ימינה, 4 למעלה)'),
        (-1,8,-11,1,-10,25,'y=−(x−4)²+5 ו y=(x−5)²'),
        (1,-6,13,-1,8,-7, 'שתי פרבולות הזזה: V=(3,4) ו V=(4,9)'),
        (1,-10,25,0, 3, 4,'y=(x−5)² ו y=3x+4'),
    ]

    for i, (oa,ob,oc, na,nb,nc, title) in enumerate(exercises):
        n = i + 1
        fig, ax = make_fig()

        if n == 20:
            # shifted parabola + line: y=(x-5)^2 and y=3x+4
            xl = xlim_auto(1, -10, 25, m2=3, n2=4)
            x = np.linspace(*xl, 500)
            ax.plot(x, (x-5)**2,  color=PARA_COLOR, lw=2, label='y=(x−5)²')
            draw_line(ax, 3, 4, xl, LINE_COLOR, label='y=3x+4')
            pts = intersections_para_line(1,-10,25,3,4)
            for k,(px,pyv) in enumerate(pts):
                mark_pt(ax,px,pyv,chr(65+k),ROOT_COLOR)
            ax.scatter([5],[0],color=VTX_COLOR,s=80,zorder=6)
            ax.annotate('V=(5,0)',(5,0),textcoords='offset points',xytext=(6,6),fontsize=8,color=VTX_COLOR)
            setup_axes(ax); ax.set_xlim(*xl); ax.legend(fontsize=8)
        elif n == 14:
            xl = (-1, 9)
            draw_para(ax,  1,-10,25, xl, PARA_COLOR, label='y=(x−5)²')
            draw_para(ax, -1,  8,-11,xl, LINE_COLOR,  label='y=−x²+8x−11')
            for aa,bb,cc in [(1,-10,25),(-1,8,-11)]:
                xvv,yvv = vertex(aa,bb,cc)
                ax.scatter([xvv],[yvv],color=VTX_COLOR,s=70,zorder=6)
            pts = intersections_two_paras(1,-10,25,-1,8,-11)
            for k,(px,pyv) in enumerate(pts):
                mark_pt(ax,px,pyv,chr(65+k),ROOT_COLOR)
            setup_axes(ax); ax.set_xlim(*xl); ax.legend(fontsize=8)
        elif n == 16:
            xl = (-1, 9)
            draw_para(ax,1,-6,13,xl,PARA_COLOR,label='y=(x−3)²+4')
            draw_para(ax,-1,8,-7,xl,LINE_COLOR,label='y=−(x−4)²+9')
            pts = intersections_two_paras(1,-6,13,-1,8,-7)
            for k,(px,pyv) in enumerate(pts):
                mark_pt(ax,px,pyv,chr(65+k),ROOT_COLOR)
            mark_vertex(ax,1,-6,13,'V₁'); mark_vertex(ax,-1,8,-7,'V₂',color='orange')
            setup_axes(ax); ax.set_xlim(*xl); ax.legend(fontsize=8)
        elif n == 18:
            xl = (0, 8)
            draw_para(ax,-1, 8,-11,xl,PARA_COLOR,label='y=−(x−4)²+5')
            draw_para(ax, 1,-10, 25,xl,LINE_COLOR, label='y=(x−5)²')
            pts = intersections_two_paras(-1,8,-11,1,-10,25)
            for k,(px,pyv) in enumerate(pts):
                mark_pt(ax,px,pyv,chr(65+k),ROOT_COLOR)
            setup_axes(ax); ax.set_xlim(*xl); ax.legend(fontsize=8)
        elif n == 19:
            xl = (-1, 9)
            draw_para(ax,1,-6,13,xl,PARA_COLOR,label='y=(x−3)²+4')
            draw_para(ax,-1,8,-7,xl,LINE_COLOR, label='y=−(x−4)²+9')
            pts = intersections_two_paras(1,-6,13,-1,8,-7)
            for k,(px,pyv) in enumerate(pts):
                mark_pt(ax,px,pyv,chr(65+k),ROOT_COLOR)
            setup_axes(ax); ax.set_xlim(*xl); ax.legend(fontsize=8)
        else:
            # draw original (dashed) and shifted
            all_x = [oa,ob,oc, na,nb,nc]
            xl_n = xlim_auto(na, nb, nc)
            xl_o = (-5, 5)
            xl_both = (min(xl_n[0], xl_o[0]), max(xl_n[1], xl_o[1]))

            x = np.linspace(*xl_both, 500)
            ax.plot(x, py(oa,ob,oc,x), color='gray', lw=1.5, ls='--', label='y=x² (מקורית)', alpha=0.6)
            draw_para(ax, na, nb, nc, xl_both, PARA_COLOR, label='פרבולה מוזזת')
            xvn, yvn = vertex(na, nb, nc)
            ax.scatter([xvn],[yvn], color=VTX_COLOR, s=80, zorder=6)
            ax.annotate(f'V=({xvn:.2g},{yvn:.2g})',(xvn,yvn),
                        textcoords='offset points', xytext=(6,4), fontsize=8, color=VTX_COLOR)

            setup_axes(ax); ax.set_xlim(*xl_both); ax.legend(fontsize=8)

        ax.set_title(title, fontsize=9)
        save_fig(fig, sub, n)


# ═══════════════════════════════════════════════════════════════════════════════
#  SUBTOPIC 5.3  –  Areas and perimeters with parabola
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_and_fill_triangle(ax, pts, label_pts=None, colors=None):
    tri_pts = np.array(pts)
    draw_triangle(ax, tri_pts)
    if label_pts:
        for j, (px, pyv) in enumerate(pts):
            lbl = label_pts[j] if j < len(label_pts) else ''
            col = colors[j] if colors and j < len(colors) else PT_COLOR
            mark_pt(ax, px, pyv, lbl, col, xytext=(6 if px >= 0 else -20, 6))


def gen_5_3():
    sub = '5.3'
    print(f"\n── Subtopic {sub} ──")

    for n in range(1, 21):
        fig, ax = make_fig()

        if n == 1:
            # A(-3,0), B(5,0), C(1,4)
            pts = [(-3,0),(5,0),(1,4)]
            xl = (-5, 7); ax.set_xlim(*xl); ax.set_ylim(-1, 7)
            _draw_and_fill_triangle(ax, pts, ['A','B','C'])
            setup_axes(ax)
            ax.set_title('|AB|=8, שטח=½·8·4=16', fontsize=10)

        elif n == 2:
            pts = [(0,0),(6,0),(3,8)]
            xl = (-1, 8); ax.set_xlim(*xl); ax.set_ylim(-1, 10)
            _draw_and_fill_triangle(ax, pts, ['A','B','C'])
            setup_axes(ax)
            ax.set_title('A(0,0) B(6,0) C(3,8): שטח=24', fontsize=10)

        elif n == 3:
            pts = [(-2,0),(4,0),(1,5)]
            xl = (-4, 6); ax.set_xlim(*xl); ax.set_ylim(-1, 7)
            _draw_and_fill_triangle(ax, pts, ['A','B','C'])
            setup_axes(ax)
            ax.set_title('A(−2,0) B(4,0) C(1,5): שטח=15', fontsize=10)

        elif n == 4:
            pts_trap = [(-3,0),(5,0),(3,4),(-1,4)]
            xl = (-5, 7); ax.set_xlim(*xl); ax.set_ylim(-1, 6)
            draw_trapezoid(ax, np.array(pts_trap))
            for j,(px,pyv) in enumerate(pts_trap):
                mark_pt(ax,px,pyv,'ABCD'[j],PT_COLOR)
            setup_axes(ax)
            ax.set_title('טרפז: b₁=8, b₂=4, h=4 → S=24', fontsize=10)

        elif n == 5:
            xl = (-1, 9); ax.set_xlim(*xl); ax.set_ylim(-1, 6)
            mark_pt(ax,1,3,'P',PT_COLOR); mark_pt(ax,7,3,"Q",SYM_COLOR)
            ax.annotate('',xy=(7,3),xytext=(1,3),
                        arrowprops=dict(arrowstyle='<->',color='darkblue',lw=1.5))
            ax.annotate('|PQ|=6',(4,3.5),ha='center',fontsize=9)
            setup_axes(ax)
            ax.set_title('P(1,3) Q(7,3): |PQ|=6, גובה מציר x=3', fontsize=10)

        elif n == 6:
            pts_sq = [(0,0),(4,0),(4,4),(0,4)]
            draw_trapezoid(ax, np.array(pts_sq), color='#F4A582')
            for j,(px,pyv) in enumerate(pts_sq):
                mark_pt(ax,px,pyv,'ABCD'[j],PT_COLOR)
            ax.set_xlim(-1,6); ax.set_ylim(-1,6)
            setup_axes(ax)
            ax.set_title('ריבוע 4×4: שטח=16, היקף=16', fontsize=10)

        elif n == 7:
            pts = [(0,0),(8,0),(4,6)]
            xl = (-1,10); ax.set_xlim(*xl); ax.set_ylim(-1,8)
            _draw_and_fill_triangle(ax, pts, ['','',''])
            ax.annotate('b=8',(4,-0.4),ha='center',fontsize=9)
            ax.annotate('h=6',(8.2,3),fontsize=9,color='blue')
            ax.plot([4,4],[0,6],color='blue',lw=1.2,ls=':')
            setup_axes(ax)
            ax.set_title('שטח משולש: ½·8·6=24', fontsize=10)

        elif n == 8:
            pts_trap = [(0,0),(10,0),(8,5),(2,5)]
            xl = (-1,12); ax.set_xlim(*xl); ax.set_ylim(-1,7)
            draw_trapezoid(ax, np.array(pts_trap))
            ax.annotate('b₁=10',(5,-0.5),ha='center',fontsize=9)
            ax.annotate('b₂=6',(5,5.3),ha='center',fontsize=9)
            ax.annotate('h=5',(10.2,2.5),fontsize=9,color='blue')
            setup_axes(ax)
            ax.set_title('טרפז: ½(4+10)·5=35', fontsize=10)

        elif n == 9:
            a,b,c = 1,0,-4
            xl = xlim_auto(a,b,c); draw_para(ax,a,b,c,xl)
            roots = get_roots(a,b,c); xv,yv = vertex(a,b,c)
            Ax,Bx = roots[0],roots[1]
            tri = [(Ax,0),(Bx,0),(xv,yv)]
            draw_triangle(ax, np.array(tri))
            mark_pt(ax,Ax,0,'A',ROOT_COLOR); mark_pt(ax,Bx,0,'B',ROOT_COLOR); mark_pt(ax,xv,yv,'C',VTX_COLOR)
            setup_axes(ax); ax.set_xlim(*xl)
            ax.set_title('y=x²−4: שטח=½·4·4=8', fontsize=10)

        elif n == 10:
            a,b,c = 1,-2,-8
            xl = xlim_auto(a,b,c); draw_para(ax,a,b,c,xl)
            roots = get_roots(a,b,c); xv,yv = vertex(a,b,c)
            tri = [(roots[0],0),(roots[1],0),(xv,yv)]
            draw_triangle(ax, np.array(tri))
            mark_pt(ax,roots[0],0,'A',ROOT_COLOR); mark_pt(ax,roots[1],0,'B',ROOT_COLOR)
            mark_pt(ax,xv,yv,'C',VTX_COLOR)
            setup_axes(ax); ax.set_xlim(*xl)
            ax.set_title('y=x²−2x−8: שטח=½·6·9=27', fontsize=10)

        elif n == 11:
            a,b,c = -1,2,8
            xl = xlim_auto(a,b,c); draw_para(ax,a,b,c,xl)
            trap = [(-2,0),(4,0),(2,8),(0,8)]
            draw_trapezoid(ax, np.array(trap))
            for lbl,px,pyv in [('A',-2,0),('D',4,0),('B',0,8),('C',2,8)]:
                mark_pt(ax,px,pyv,lbl,ROOT_COLOR if pyv==0 else PT_COLOR)
            setup_axes(ax); ax.set_xlim(*xl)
            ax.set_title('y=−x²+2x+8: טרפז ABDC, S=32', fontsize=10)

        elif n == 12:
            a,b,c = 1,-4,5
            xl = xlim_auto(a,b,c); draw_para(ax,a,b,c,xl)
            tri = [(0,5),(4,5),(2,1)]
            draw_triangle(ax, np.array(tri))
            mark_pt(ax,0,5,'A',PT_COLOR); mark_pt(ax,4,5,'B',SYM_COLOR); mark_pt(ax,2,1,'C',VTX_COLOR)
            ax.axhline(5,color='orange',ls='--',lw=1)
            setup_axes(ax); ax.set_xlim(*xl)
            ax.set_title('y=x²−4x+5: שטח=½·4·4=8', fontsize=10)

        elif n == 13:
            a,b,c = 1,-2,-4
            lm,ln = 1,6
            xl = xlim_auto(a,b,c,m2=lm,n2=ln)
            draw_para(ax,a,b,c,xl); draw_line(ax,lm,ln,xl)
            pts_i = intersections_para_line(a,b,c,lm,ln)
            xv,yv = vertex(a,b,c)
            Ax,Ay = pts_i[0]; Bx,By = pts_i[1]
            tri = [(Ax,Ay),(Bx,By),(xv,yv)]
            draw_triangle(ax, np.array(tri))
            mark_pt(ax,Ax,Ay,'A',ROOT_COLOR); mark_pt(ax,Bx,By,'B',ROOT_COLOR)
            mark_pt(ax,xv,yv,'C',VTX_COLOR)
            setup_axes(ax); ax.set_xlim(*xl)
            ax.set_title('y=x²−2x−4 ו y=x+6: שטח=42', fontsize=10)

        elif n == 14:
            a,b,c = -1,3,4
            xl = xlim_auto(a,b,c); draw_para(ax,a,b,c,xl)
            roots = get_roots(a,b,c); xv,yv = vertex(a,b,c)
            tri = [(roots[0],0),(roots[1],0),(xv,yv)]
            draw_triangle(ax, np.array(tri))
            mark_pt(ax,roots[0],0,'A',ROOT_COLOR); mark_pt(ax,roots[1],0,'B',ROOT_COLOR)
            mark_pt(ax,xv,yv,'C',VTX_COLOR)
            setup_axes(ax); ax.set_xlim(*xl)
            ax.set_title('y=−x²+3x+4: שטח≈15.6', fontsize=10)

        elif n == 15:
            a,b,c = 1,0,0
            lm,ln = 1,6
            xl = xlim_auto(a,b,c,m2=lm,n2=ln)
            draw_para(ax,a,b,c,xl); draw_line(ax,lm,ln,xl)
            pts_i = intersections_para_line(a,b,c,lm,ln)
            Ax,Ay = pts_i[0]; Bx,By = pts_i[1]
            tri = [(Ax,Ay),(Bx,By),(0,0)]
            draw_triangle(ax, np.array(tri))
            mark_pt(ax,Ax,Ay,'A',ROOT_COLOR); mark_pt(ax,Bx,By,'B',ROOT_COLOR)
            mark_pt(ax,0,0,'D',VTX_COLOR)
            setup_axes(ax); ax.set_xlim(*xl)
            ax.set_title('y=x² ו y=x+6: שטח=15', fontsize=10)

        elif n == 16:
            a,b,c = -1,8,-7
            xl = xlim_auto(a,b,c); draw_para(ax,a,b,c,xl)
            roots = get_roots(a,b,c)
            tri = [(roots[0],0),(roots[1],0),(0,py(a,b,c,0))]
            draw_triangle(ax, np.array(tri))
            mark_pt(ax,roots[0],0,'A',ROOT_COLOR); mark_pt(ax,roots[1],0,'B',ROOT_COLOR)
            mark_pt(ax,0,py(a,b,c,0),'C',PT_COLOR)
            setup_axes(ax); ax.set_xlim(*xl)
            ax.set_title('y=−x²+8x−7: שטח=21', fontsize=10)

        elif n == 17:
            a,b,c = 1,-2,-4
            lm,ln = 1,6
            xl = xlim_auto(a,b,c,m2=lm,n2=ln)
            draw_para(ax,a,b,c,xl); draw_line(ax,lm,ln,xl)
            pts_i = intersections_para_line(a,b,c,lm,ln)
            Ax,Ay = pts_i[0]; Bx,By = pts_i[1]
            Ex = (Ax+Bx)/2
            mark_pt(ax,Ax,Ay,'A',ROOT_COLOR); mark_pt(ax,Bx,By,'B',ROOT_COLOR)
            mark_pt(ax,Ax,0,'D',PT_COLOR)
            mark_pt(ax,Ex,0,'E',SYM_COLOR)
            xv,yv = vertex(a,b,c); mark_pt(ax,xv,yv,'C',VTX_COLOR)
            # draw ADE triangle
            draw_triangle(ax, np.array([(Ax,Ay),(Ax,0),(Ex,0)]))
            setup_axes(ax); ax.set_xlim(*xl)
            ax.set_title('y=x²−2x−4 ו y=x+6: שטח ADE=7', fontsize=10)

        elif n == 18:
            a,b,c = 1,-5,-1
            lm,ln = -3,7
            xl = xlim_auto(a,b,c,m2=lm,n2=ln)
            draw_para(ax,a,b,c,xl); draw_line(ax,lm,ln,xl)
            pts_i = intersections_para_line(a,b,c,lm,ln)
            Ax,Ay = pts_i[0]; Bx,By = pts_i[1]
            xv,yv = vertex(a,b,c)
            draw_triangle(ax, np.array([(Ax,Ay),(Bx,By),(xv,yv)]))
            mark_pt(ax,Ax,Ay,'A',ROOT_COLOR); mark_pt(ax,Bx,By,'B',ROOT_COLOR)
            mark_pt(ax,xv,yv,'C',VTX_COLOR)
            setup_axes(ax); ax.set_xlim(*xl)
            ax.set_title('y=x²−5x−1 ו y=−3x+7', fontsize=10)

        elif n == 19:
            a,b,c = 1,-4,5
            xl = xlim_auto(a,b,c); draw_para(ax,a,b,c,xl)
            xv,yv = vertex(a,b,c)
            draw_triangle(ax, np.array([(0,5),(4,5),(xv,yv)]))
            mark_pt(ax,0,5,'A',PT_COLOR); mark_pt(ax,4,5,'B',SYM_COLOR); mark_pt(ax,xv,yv,'C',VTX_COLOR)
            ax.axhline(5, color='orange', ls='--', lw=1)
            setup_axes(ax); ax.set_xlim(*xl)
            ax.set_title('y=x²−4x+5: שטח=8, היקף=4+4√5', fontsize=10)

        elif n == 20:
            a,b,c = -1,2,8
            xl = xlim_auto(a,b,c); draw_para(ax,a,b,c,xl)
            trap = [(-2,0),(4,0),(2,8),(0,8)]
            draw_trapezoid(ax, np.array(trap))
            for lbl,px,pyv in [('A',-2,0),('D',4,0),('B',0,8),('C',2,8)]:
                mark_pt(ax,px,pyv,lbl,ROOT_COLOR if pyv==0 else PT_COLOR)
            setup_axes(ax); ax.set_xlim(*xl)
            ax.set_title('y=−x²+2x+8: טרפז S=32, היקף=8+4√17', fontsize=10)

        save_fig(fig, sub, n)


# ═══════════════════════════════════════════════════════════════════════════════
#  SUBTOPIC 6.2  –  Full MAHAT questions
# ═══════════════════════════════════════════════════════════════════════════════

def gen_6_2():
    sub = '6.2'
    print(f"\n── Subtopic {sub} ──")

    exercises = [
        ( 1,-4, 3, None,None, 'y=x²−4x+3: מלא'),
        (-1, 4, 0, None,None, 'y=−x²+4x: מלא'),
        ( 1,-4, 5, None,None, 'y=x²−4x+5: מלא'),
        ( 1,-2,-4,  2,  3,   'y=x²−1 ו y=2x+3'),
        (-1, 6,-8, None,None, 'y=−x²+6x−8: מלא'),
        ( 1,-4, 4, -2,  4,   'y=x²−4x+4 ו y=−2x+4'),
        ( 2,-8, 6, None,None, 'y=2x²−8x+6: מלא'),
        ( 1, 2,-3, None,None, 'y=x²+2x−3: מלא'),
        ( 1,-2,-4,  1,  6,   'y=x²−2x−4 ו y=x+6 (מה"ט)'),
        ( 1, 1,-12,None,None, 'y=x²+x−12: מלא (מה"ט)'),
        (-1, 6,-4, None,None, 'שתי פרבולות (מה"ט)'),
        (-1, 8,-11,None,None, 'y=−x²+8x−11 ו (x−5)² (מה"ט)'),
        ( 1,-4, 5, None,None, 'y=x²−4x+5: שטח ABC (מה"ט)'),
        (-1, 2, 8, None,None, 'y=−x²+2x+8: טרפז (מה"ט)'),
        (-1, 4, 0, None,None, 'f(x)=−x²+4x: מלא (מה"ט)'),
        ( 1,-6,13, None,None, 'שתי פרבולות (מה"ט 2025)'),
        ( 1, 0, 0,  3,  4,   'y=x² ו y=3x+4 (מה"ט 2025)'),
        (-1, 3, 4, None,None, 'y=−x²+3x+4: מסלול (מה"ט)'),
        (-1, 8,-11,None,None, 'שתי פרבולות (מה"ט 2025)'),
        (-1, 8,-9,  1,  1,   'y=−x²+8x−9 ו y=x+1 (מה"ט 2025)'),
    ]

    for i, (a, b, c, lm, ln, title) in enumerate(exercises):
        n = i + 1
        fig, ax = make_fig()

        if n == 11:
            xl = (-1, 9)
            draw_para(ax,-1,6,-4, xl, PARA_COLOR, label='y=−x²+6x−4')
            draw_para(ax,-1,11,-24,xl, LINE_COLOR, label='y=−x²+11x−24')
            for aa,bb,cc,col in [(-1,6,-4,PARA_COLOR),(-1,11,-24,LINE_COLOR)]:
                for r in get_roots(aa,bb,cc):
                    ax.scatter([r],[0],color=col,s=60,zorder=5)
            mark_pt(ax,4,4,'(4,4)',ROOT_COLOR)
            setup_axes(ax); ax.set_xlim(*xl); ax.legend(fontsize=8)

        elif n == 12:
            xl = (0, 8)
            draw_para(ax,-1, 8,-11,xl, PARA_COLOR, label='y=−x²+8x−11')
            draw_para(ax, 1,-10, 25,xl, LINE_COLOR,  label='y=(x−5)²')
            pts = intersections_two_paras(-1,8,-11,1,-10,25)
            for k,(px,pyv) in enumerate(pts):
                mark_pt(ax,px,pyv,chr(65+k),ROOT_COLOR)
            setup_axes(ax); ax.set_xlim(*xl); ax.legend(fontsize=8)

        elif n == 13:
            a2,b2,c2 = 1,-4,5
            xl = xlim_auto(a2,b2,c2); draw_para(ax,a2,b2,c2,xl)
            tri = [(0,5),(4,5),(2,1)]
            draw_triangle(ax, np.array(tri))
            mark_pt(ax,0,5,'A',PT_COLOR); mark_pt(ax,4,5,'B',SYM_COLOR); mark_pt(ax,2,1,'C',VTX_COLOR)
            ax.axhline(5,color='orange',ls='--',lw=1)
            setup_axes(ax); ax.set_xlim(*xl)

        elif n == 14:
            a2,b2,c2 = -1,2,8
            xl = xlim_auto(a2,b2,c2); draw_para(ax,a2,b2,c2,xl)
            trap = [(-2,0),(4,0),(2,8),(0,8)]
            draw_trapezoid(ax, np.array(trap))
            for lbl,px,pyv in [('A',-2,0),('D',4,0),('B',0,8),('C',2,8)]:
                mark_pt(ax,px,pyv,lbl,ROOT_COLOR if pyv==0 else PT_COLOR)
            setup_axes(ax); ax.set_xlim(*xl)

        elif n == 16:
            xl = (-1,9)
            draw_para(ax,1,-6,13, xl, PARA_COLOR, label='y=x²−6x+13')
            draw_para(ax,-1,8,-7, xl, LINE_COLOR,  label='y=−x²+8x−7')
            for aa,bb,cc in [(1,-6,13),(-1,8,-7)]:
                xvv,yvv = vertex(aa,bb,cc)
                ax.scatter([xvv],[yvv],color=VTX_COLOR,s=70,zorder=6)
            pts = intersections_two_paras(1,-6,13,-1,8,-7)
            for k,(px,pyv) in enumerate(pts):
                mark_pt(ax,px,pyv,chr(65+k),ROOT_COLOR)
            setup_axes(ax); ax.set_xlim(*xl); ax.legend(fontsize=8)

        elif n == 17:
            xl = xlim_auto(1,0,0,m2=3,n2=4)
            draw_para(ax,1,0,0,xl, PARA_COLOR, label='y=x²')
            draw_line(ax,3,4,xl, LINE_COLOR, label='y=3x+4')
            pts = intersections_para_line(1,0,0,3,4)
            Ax,Ay = pts[0]; Bx,By = pts[1]
            mark_pt(ax,Ax,Ay,'A',ROOT_COLOR); mark_pt(ax,Bx,By,'B',ROOT_COLOR)
            mark_pt(ax,Bx,0,'C',PT_COLOR); mark_pt(ax,0,0,'D',VTX_COLOR)
            draw_triangle(ax, np.array([(Bx,By),(Bx,0),(0,0)]))
            setup_axes(ax); ax.set_xlim(*xl); ax.legend(fontsize=8)

        elif n == 18:
            a2,b2,c2 = -1,3,4
            xl = xlim_auto(a2,b2,c2); draw_para(ax,a2,b2,c2,xl)
            xv2,yv2 = vertex(a2,b2,c2)
            roots2 = get_roots(a2,b2,c2)
            tri = [(roots2[0],0),(roots2[1],0),(xv2,yv2)]
            draw_triangle(ax, np.array(tri))
            mark_pt(ax,roots2[0],0,'A',ROOT_COLOR); mark_pt(ax,roots2[1],0,'C',ROOT_COLOR)
            mark_pt(ax,xv2,yv2,'B',VTX_COLOR)
            setup_axes(ax); ax.set_xlim(*xl)

        elif n == 19:
            xl = (0,8)
            draw_para(ax,-1, 8,-11,xl, PARA_COLOR, label='y=−x²+8x−11')
            draw_para(ax, 1,-10, 25,xl, LINE_COLOR,  label='y=(x−5)²')
            pts = intersections_two_paras(-1,8,-11,1,-10,25)
            for k,(px,pyv) in enumerate(pts):
                mark_pt(ax,px,pyv,chr(65+k),ROOT_COLOR)
            setup_axes(ax); ax.set_xlim(*xl); ax.legend(fontsize=8)

        elif lm is not None:
            xl = xlim_auto(a,b,c,m2=lm,n2=ln)
            draw_para(ax,a,b,c,xl)
            draw_line(ax,lm,ln,xl)
            pts = intersections_para_line(a,b,c,lm,ln)
            for k,(px,pyv) in enumerate(pts):
                mark_pt(ax,px,pyv,chr(65+k),ROOT_COLOR)
            mark_vertex(ax,a,b,c,'V')
            shade_signs(ax,a,b,c,xl)
            setup_axes(ax); ax.set_xlim(*xl)

        else:
            xl = xlim_auto(a,b,c)
            draw_para(ax,a,b,c,xl)
            mark_roots(ax,a,b,c)
            mark_vertex(ax,a,b,c)
            shade_signs(ax,a,b,c,xl)
            shade_incr_decr(ax,a,b,c,xl)
            setup_axes(ax); ax.set_xlim(*xl)

        ax.set_title(title, fontsize=9)
        save_fig(fig, sub, n)


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("Generating Chapter 8 graphs …")
    gen_1_2()
    gen_2_2()
    gen_2_3()
    gen_3_1()
    gen_3_2()
    gen_3_3()
    gen_4_1()
    gen_4_2()
    gen_5_1()
    gen_5_2()
    gen_5_3()
    gen_6_2()
    print(f"\nDone! All images saved to:\n  {IMAGES_DIR}")
