#!/usr/bin/env python3
"""
Chapter 10 Trigonometry – Generate 160 PNG diagrams for MAHAT 99913 exam prep.
8 subtopics × 20 exercises each.
"""

import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, FancyArrow
import numpy as np, os, sys

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "10 - \u05d8\u05e8\u05d9\u05d2\u05d5\u05e0\u05d5\u05de\u05d8\u05e8\u05d9\u05d4")
IMG = os.path.join(DIR, "images")
os.makedirs(IMG, exist_ok=True)

plt.rcParams.update({
    'font.family': ['Arial Hebrew', 'Arial Unicode MS', 'Arial', 'DejaVu Sans'],
    'axes.unicode_minus': False,
})

# ══════════════════════════════════════════════════════
#  DRAWING PRIMITIVES
# ══════════════════════════════════════════════════════

def nax():
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_aspect('equal'); ax.axis('off')
    fig.patch.set_facecolor('white')
    return fig, ax

def sv(fig, nm):
    fig.savefig(os.path.join(IMG, nm), dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  \u2713 {nm}")

def ln(ax, p1, p2, lw=2, c='k', ls='-'):
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=c, lw=lw, ls=ls)

def pg(ax, pts, lw=2, c='k', ls='-'):
    n = len(pts)
    for i in range(n):
        ln(ax, pts[i], pts[(i+1) % n], lw=lw, c=c, ls=ls)

def rm(ax, corner, t1, t2, sz=None):
    """Right-angle square marker."""
    C = np.array(corner, float)
    d1, d2 = np.array(t1, float) - C, np.array(t2, float) - C
    n1, n2 = np.linalg.norm(d1), np.linalg.norm(d2)
    if n1 < 1e-9 or n2 < 1e-9: return
    if sz is None: sz = min(n1, n2) * 0.14
    u1, u2 = d1 / n1 * sz, d2 / n2 * sz
    ax.plot([C[0]+u1[0], C[0]+u1[0]+u2[0]], [C[1]+u1[1], C[1]+u1[1]+u2[1]], 'k-', lw=1.4)
    ax.plot([C[0]+u1[0]+u2[0], C[0]+u2[0]], [C[1]+u1[1]+u2[1], C[1]+u2[1]], 'k-', lw=1.4)

def aoa(ax, vtx, p1, p2, r=0.30, col='royalblue', lbl=None, lfs=10):
    """Angle arc (shorter arc) between rays to p1 and p2."""
    v = np.array(vtx, float)
    a1 = np.degrees(np.arctan2(float(p1[1])-v[1], float(p1[0])-v[0])) % 360
    a2 = np.degrees(np.arctan2(float(p2[1])-v[1], float(p2[0])-v[0])) % 360
    diff = (a2 - a1) % 360
    if diff > 180: a1, a2 = a2, a1; diff = 360 - diff
    ax.add_patch(Arc(tuple(v), 2*r, 2*r, angle=0, theta1=a1, theta2=a1+diff, color=col, lw=1.5))
    if lbl:
        m = np.radians(a1 + diff/2)
        ax.text(v[0]+r*2.1*np.cos(m), v[1]+r*2.1*np.sin(m), lbl,
                fontsize=lfs, ha='center', va='center', color=col)

def vl(ax, pt, txt, nbs, d=0.27, fs=13):
    """Vertex label offset away from centroid of neighbors."""
    pt = np.array(pt, float)
    ctr = np.mean([np.array(n, float) for n in nbs], axis=0)
    off = pt - ctr; nm = np.linalg.norm(off)
    off = off / nm * d if nm > 1e-9 else np.array([0.0, d])
    ax.text(pt[0]+off[0], pt[1]+off[1], txt, fontsize=fs,
            ha='center', va='center', fontweight='bold')

def ml(ax, p1, p2, txt, k=0.21, s=1, fs=11, c='k'):
    """Mid-segment label, offset perpendicular."""
    a, b = np.array(p1, float), np.array(p2, float)
    mid = (a+b)/2; d = b-a; nm = np.linalg.norm(d)
    perp = np.array([-d[1], d[0]])/nm*s if nm > 1e-9 else np.array([0.0, 1.0])
    ax.text(*(mid + perp*k), txt, fontsize=fs, ha='center', va='center', color=c)

def al(ax, pts, pad=0.55):
    pts = np.array(pts, float)
    ax.set_xlim(pts[:,0].min()-pad, pts[:,0].max()+pad)
    ax.set_ylim(pts[:,1].min()-pad, pts[:,1].max()+pad)

def s4(a, b=0):
    """Scale factor so max(|a|,|b|) <= 4."""
    m = max(abs(a), abs(b) if isinstance(b, (int, float)) else 0)
    return (4/m if m > 4 else 1.0)

def rtp(a, b):
    """Standard right-triangle points: C=(0,0), B=(a,0), A=(0,b) scaled to <=4."""
    sc = s4(a, b)
    return np.array([0,0]), np.array([a*sc, 0]), np.array([0, b*sc])

def iso_pts(half_b, h):
    """Isosceles: A=(0,h), B=(-hb,0), C=(hb,0), D=(0,0) altitude foot."""
    sc = s4(half_b, h)
    return (np.array([0, h*sc]), np.array([-half_b*sc, 0]),
            np.array([half_b*sc, 0]), np.array([0, 0]))

def rect_pts(w, h):
    """Rectangle A=(0,0), B=(w,0), C=(w,h), D=(0,h) scaled."""
    sc = s4(w, h)
    return (np.array([0,0]), np.array([w*sc,0]),
            np.array([w*sc,h*sc]), np.array([0,h*sc]))

def rhombus_pts(d1, d2):
    """Rhombus with diagonals d1 (horizontal) & d2 (vertical), centered at origin."""
    sc = s4(d1/2, d2/2)
    return (np.array([0, d2/2*sc]), np.array([d1/2*sc, 0]),
            np.array([0, -d2/2*sc]), np.array([-d1/2*sc, 0]))

def trap_pts(long_b, short_b, h):
    """Isosceles trapezoid: B=(0,0), C=(long,0), D=(off+short,h), A=(off,h)."""
    sc = s4(long_b, h)
    off = (long_b - short_b) / 2
    return (np.array([off*sc, h*sc]), np.array([0, 0]),
            np.array([long_b*sc, 0]), np.array([(off+short_b)*sc, h*sc]))

# ══════════════════════════════════════════════════════
#  1.2 – RIGHT TRIANGLE: HYPOTENUSE/LEGS IDENTIFICATION
# ══════════════════════════════════════════════════════
def ch12():
    pr = "10_1.2_ex"

    # 01: Triangle ABC, right angle at C → which side is hypotenuse (AB)?
    fig, ax = nax()
    C, B, A = np.array([0,0]), np.array([3,0]), np.array([0,4])
    pg(ax, [A,B,C]); rm(ax, C, A, B)
    vl(ax, A, 'A', [B,C]); vl(ax, B, 'B', [A,C]); vl(ax, C, 'C', [A,B])
    ml(ax, A, B, '?', k=0.28, c='red')
    al(ax, [A,B,C]); sv(fig, pr+"01.png")

    # 02: Sides 3, 4, 5 → hypotenuse is 5
    fig, ax = nax()
    C, B, A = np.array([0,0]), np.array([4,0]), np.array([0,3])
    pg(ax, [A,B,C]); rm(ax, C, A, B)
    ml(ax, A, C, '3'); ml(ax, C, B, '4', s=-1); ml(ax, A, B, '5', k=0.27, c='darkred')
    al(ax, [A,B,C]); sv(fig, pr+"02.png")

    # 03: Triangle DEF, right angle at E → hypotenuse is DF
    fig, ax = nax()
    E, F, D = np.array([0,0]), np.array([3,0]), np.array([0,4])
    pg(ax, [D,E,F]); rm(ax, E, D, F)
    vl(ax, D, 'D', [E,F]); vl(ax, E, 'E', [D,F]); vl(ax, F, 'F', [D,E])
    ml(ax, D, F, '?', k=0.28, c='red')
    al(ax, [D,E,F]); sv(fig, pr+"03.png")

    # 04: Sides 5, 12, 13 → hypotenuse is 13
    fig, ax = nax()
    sc = s4(12, 5)
    C, B, A = np.array([0,0]), np.array([12*sc,0]), np.array([0,5*sc])
    pg(ax, [A,B,C]); rm(ax, C, A, B)
    ml(ax, A, C, '5'); ml(ax, C, B, '12', s=-1); ml(ax, A, B, '13', k=0.27, c='darkred')
    al(ax, [A,B,C]); sv(fig, pr+"04.png")

    # 05: Triangle PQR, right angle at Q → hypotenuse is PR
    fig, ax = nax()
    Q, R, P = np.array([0,0]), np.array([3,0]), np.array([0,4])
    pg(ax, [P,Q,R]); rm(ax, Q, P, R)
    vl(ax, P, 'P', [Q,R]); vl(ax, Q, 'Q', [P,R]); vl(ax, R, 'R', [P,Q])
    ml(ax, P, R, '?', k=0.28, c='red')
    al(ax, [P,Q,R]); sv(fig, pr+"05.png")

    # 06: Hypotenuse is always the longest side
    fig, ax = nax()
    C, B, A = np.array([0,0]), np.array([4,0]), np.array([0,3])
    pg(ax, [A,B,C]); rm(ax, C, A, B)
    ml(ax, A, C, 'leg', c='steelblue'); ml(ax, C, B, 'leg', s=-1, c='steelblue')
    ml(ax, A, B, 'Hyp. (longest)', k=0.27, c='darkgreen')
    al(ax, [A,B,C]); sv(fig, pr+"06.png")

    # 07: Sides 8, 15, 17 → hypotenuse is 17
    fig, ax = nax()
    sc = s4(15, 8)
    C, B, A = np.array([0,0]), np.array([15*sc,0]), np.array([0,8*sc])
    pg(ax, [A,B,C]); rm(ax, C, A, B)
    ml(ax, A, C, '8'); ml(ax, C, B, '15', s=-1); ml(ax, A, B, '17', k=0.27, c='darkred')
    al(ax, [A,B,C]); sv(fig, pr+"07.png")

    # 08: Hypotenuse is opposite the right angle
    fig, ax = nax()
    C, B, A = np.array([0,0]), np.array([4,0]), np.array([0,3])
    pg(ax, [A,B,C]); rm(ax, C, A, B)
    vl(ax, A, 'A', [B,C]); vl(ax, B, 'B', [A,C]); vl(ax, C, 'C', [A,B])
    ml(ax, A, B, 'Hyp.', k=0.27, c='darkgreen')
    ax.annotate('', xy=(0.25, 0.25), xytext=(1.8, 2.2),
                arrowprops=dict(arrowstyle='->', color='royalblue', lw=1.6))
    ax.text(1.85, 2.4, '90°', fontsize=11, color='royalblue', ha='center', va='bottom')
    al(ax, [A,B,C]); sv(fig, pr+"08.png")

    # 09: ABC right at C, AB=10, BC=6 → find AC=8
    fig, ax = nax()
    C, B, A = np.array([0,0]), np.array([6,0]), np.array([0,8])
    pg(ax, [A,B,C]); rm(ax, C, A, B)
    vl(ax, A, 'A', [B,C]); vl(ax, B, 'B', [A,C]); vl(ax, C, 'C', [A,B])
    ml(ax, C, B, '6', s=-1); ml(ax, A, B, 'AB=10', k=0.27); ml(ax, A, C, '?', c='red')
    al(ax, [A,B,C]); sv(fig, pr+"09.png")

    # 10: Sides 9, 12, 15 → is it a right triangle? (Yes, 9-12-15 = 3×(3-4-5))
    fig, ax = nax()
    sc = s4(12, 9)
    C, B, A = np.array([0,0]), np.array([12*sc,0]), np.array([0,9*sc])
    pg(ax, [A,B,C]); rm(ax, C, A, B)
    ml(ax, A, C, '9'); ml(ax, C, B, '12', s=-1); ml(ax, A, B, '15', k=0.27)
    ax.text(2.0, 2.2, '?', fontsize=22, ha='center', va='center', color='royalblue')
    al(ax, [A,B,C]); sv(fig, pr+"10.png")

    # 11: MNP right at N, MN=7, NP=24 → find MP=25
    fig, ax = nax()
    sc = s4(24, 7)
    N, P, M = np.array([0,0]), np.array([24*sc,0]), np.array([0,7*sc])
    pg(ax, [M,N,P]); rm(ax, N, M, P)
    vl(ax, M, 'M', [N,P]); vl(ax, N, 'N', [M,P]); vl(ax, P, 'P', [M,N])
    ml(ax, N, M, '7'); ml(ax, N, P, '24', s=-1); ml(ax, M, P, '?', k=0.27, c='red')
    al(ax, [M,N,P]); sv(fig, pr+"11.png")

    # 12: Legs a=10, b=10√3 → find hypotenuse c=20
    fig, ax = nax()
    sc = s4(10*1.732, 10)
    C, B, A = np.array([0,0]), np.array([10*1.732*sc,0]), np.array([0,10*sc])
    pg(ax, [A,B,C]); rm(ax, C, A, B)
    ml(ax, A, C, 'a=10'); ml(ax, C, B, 'b=10\u221a3', s=-1); ml(ax, A, B, 'c=?', k=0.27, c='red')
    al(ax, [A,B,C]); sv(fig, pr+"12.png")

    # 13: XZ²=XY²+YZ² → right angle at Y, hypotenuse is XZ
    fig, ax = nax()
    Y, Z, X = np.array([0,0]), np.array([4,0]), np.array([0,3])
    pg(ax, [X,Y,Z]); rm(ax, Y, X, Z)
    vl(ax, X, 'X', [Y,Z]); vl(ax, Y, 'Y', [X,Z]); vl(ax, Z, 'Z', [X,Y])
    ml(ax, X, Z, 'XZ', k=0.27, c='darkred')
    ax.text(2.2, 2.2, 'XZ\u00b2=XY\u00b2+YZ\u00b2', fontsize=9, ha='center', va='center', color='royalblue')
    al(ax, [X,Y,Z]); sv(fig, pr+"13.png")

    # 14: c=25, a=15, find b=20
    fig, ax = nax()
    sc = s4(20, 15)
    C, B, A = np.array([0,0]), np.array([20*sc,0]), np.array([0,15*sc])
    pg(ax, [A,B,C]); rm(ax, C, A, B)
    ml(ax, A, C, 'a=15'); ml(ax, A, B, 'c=25', k=0.27); ml(ax, C, B, 'b=?', s=-1, c='red')
    al(ax, [A,B,C]); sv(fig, pr+"14.png")

    # 15: ABC right at B → AB and BC are legs
    fig, ax = nax()
    B, C, A = np.array([0,0]), np.array([4,0]), np.array([0,3])
    pg(ax, [A,B,C]); rm(ax, B, A, C)
    vl(ax, A, 'A', [B,C]); vl(ax, B, 'B', [A,C]); vl(ax, C, 'C', [A,B])
    ml(ax, A, B, 'leg', c='steelblue'); ml(ax, B, C, 'leg', s=-1, c='steelblue')
    ml(ax, A, C, 'Hyp.', k=0.27)
    al(ax, [A,B,C]); sv(fig, pr+"15.png")

    # 16: Legs a=20, b=21 → find hyp c=29
    fig, ax = nax()
    sc = s4(21, 20)
    C, B, A = np.array([0,0]), np.array([21*sc,0]), np.array([0,20*sc])
    pg(ax, [A,B,C]); rm(ax, C, A, B)
    ml(ax, A, C, 'a=20'); ml(ax, C, B, 'b=21', s=-1); ml(ax, A, B, 'c=?', k=0.27, c='red')
    al(ax, [A,B,C]); sv(fig, pr+"16.png")

    # 17: Rectangle ABCD 10×24, diagonal BD
    fig, ax = nax()
    sc = s4(24, 10)
    A, B, C, D = (np.array([0,0]), np.array([24*sc,0]),
                  np.array([24*sc,10*sc]), np.array([0,10*sc]))
    pg(ax, [A,B,C,D]); ln(ax, B, D, lw=2, c='royalblue', ls='--')
    vl(ax, A, 'A', [B,D]); vl(ax, B, 'B', [A,C])
    vl(ax, C, 'C', [B,D]); vl(ax, D, 'D', [A,C])
    ml(ax, A, B, '24', s=-1); ml(ax, A, D, '10')
    ml(ax, B, D, 'BD=?', k=0.27, c='royalblue')
    rm(ax, A, B, D)
    al(ax, [A,B,C,D]); sv(fig, pr+"17.png")

    # 18: Pole (h=12m) with rope (15m), ground distance=9m
    fig, ax = nax()
    sc = s4(9, 12)
    base = np.array([0,0]); top = np.array([0, 12*sc]); gnd = np.array([9*sc, 0])
    ln(ax, base, top, lw=3, c='saddlebrown')
    ln(ax, base, gnd, lw=2, c='dimgray')
    ln(ax, top, gnd, lw=2, c='royalblue', ls='--')
    rm(ax, base, top, gnd)
    ml(ax, base, gnd, '9m', s=-1); ml(ax, top, gnd, '15m', k=0.27, c='royalblue')
    ml(ax, base, top, 'h=?', c='red')
    ax.text(-0.2, 0, '\u25bc', fontsize=8, ha='center'); ax.text(0, -0.15, '\u25b2', fontsize=8, ha='center')
    al(ax, [base, top, gnd]); sv(fig, pr+"18.png")

    # 19: XYZ with XY=41, XZ=40, YZ=9 → right angle at Z
    fig, ax = nax()
    sc = s4(40, 9)
    Z, X, Y = np.array([0,0]), np.array([40*sc, 0]), np.array([0, 9*sc])
    pg(ax, [X,Y,Z]); rm(ax, Z, X, Y)
    vl(ax, X, 'X', [Y,Z]); vl(ax, Y, 'Y', [X,Z]); vl(ax, Z, 'Z', [X,Y])
    ml(ax, Z, X, 'XZ=40', s=-1); ml(ax, Z, Y, 'YZ=9'); ml(ax, X, Y, 'XY=41', k=0.27)
    al(ax, [X,Y,Z]); sv(fig, pr+"19.png")

    # 20: Hyp=3×short leg (=8), find long leg b=16√2
    fig, ax = nax()
    short, hyp = 8, 24
    long_ = np.sqrt(hyp**2 - short**2)  # ≈22.63
    sc = s4(long_, short)
    C, B, A = np.array([0,0]), np.array([long_*sc,0]), np.array([0,short*sc])
    pg(ax, [A,B,C]); rm(ax, C, A, B)
    ml(ax, A, C, '8'); ml(ax, A, B, 'c=3\xd78=24', k=0.27); ml(ax, C, B, 'b=?', s=-1, c='red')
    al(ax, [A,B,C]); sv(fig, pr+"20.png")

    print("  \u2713\u2713 1.2 complete (20 images)")

# ══════════════════════════════════════════════════════
#  1.3 – OPPOSITE / ADJACENT LABELING
# ══════════════════════════════════════════════════════
def ch13():
    pr = "10_1.3_ex"

    # Helper: draw right triangle ABC (right at C) and highlight reference angle
    def rt_opp_adj(fig, ax, A, B, C, ref='A',
                   vnames=('A','B','C'), slbls=None, angle_lbl=None):
        pg(ax, [A,B,C]); rm(ax, C, A, B)
        vl(ax, A, vnames[0], [B,C])
        vl(ax, B, vnames[1], [A,C])
        vl(ax, C, vnames[2], [A,B])
        # Reference angle arc
        pts_map = {vnames[0]: A, vnames[1]: B, vnames[2]: C}
        ref_pt = pts_map[ref]
        others = [k for k in vnames if k != ref]
        aoa(ax, ref_pt, pts_map[others[0]], pts_map[others[1]],
            r=0.3, col='crimson', lbl=angle_lbl)
        if slbls:
            for (p1, p2), lbl in slbls:
                ml(ax, p1, p2, lbl)

    # 01–08: Triangle ABC right at C, then PQR right at R
    # 01: ABC right at C, angle at A → opp = BC
    fig, ax = nax()
    C, B, A = np.array([0,0]), np.array([4,0]), np.array([0,3])
    rt_opp_adj(fig, ax, A, B, C, ref='A', vnames=('A','B','C'))
    ml(ax, C, B, 'opp', s=-1, c='crimson'); ml(ax, A, C, 'adj', c='steelblue')
    ml(ax, A, B, 'Hyp.', k=0.28)
    al(ax, [A,B,C]); sv(fig, pr+"01.png")

    # 02: ABC right at C, angle at A → adj = AC
    fig, ax = nax()
    C, B, A = np.array([0,0]), np.array([4,0]), np.array([0,3])
    rt_opp_adj(fig, ax, A, B, C, ref='A', vnames=('A','B','C'))
    ml(ax, C, B, 'opp', s=-1, c='gray'); ml(ax, A, C, 'adj', c='crimson')
    ml(ax, A, B, 'Hyp.', k=0.28)
    al(ax, [A,B,C]); sv(fig, pr+"02.png")

    # 03: ABC right at C, angle at B → opp = AC
    fig, ax = nax()
    C, B, A = np.array([0,0]), np.array([4,0]), np.array([0,3])
    rt_opp_adj(fig, ax, A, B, C, ref='B', vnames=('A','B','C'))
    ml(ax, A, C, 'opp', c='crimson'); ml(ax, C, B, 'adj', s=-1, c='steelblue')
    ml(ax, A, B, 'Hyp.', k=0.28)
    al(ax, [A,B,C]); sv(fig, pr+"03.png")

    # 04: ABC right at C, angle at B → adj = BC
    fig, ax = nax()
    C, B, A = np.array([0,0]), np.array([4,0]), np.array([0,3])
    rt_opp_adj(fig, ax, A, B, C, ref='B', vnames=('A','B','C'))
    ml(ax, A, C, 'opp', c='gray'); ml(ax, C, B, 'adj', s=-1, c='crimson')
    ml(ax, A, B, 'Hyp.', k=0.28)
    al(ax, [A,B,C]); sv(fig, pr+"04.png")

    # 05: PQR right at R, angle at P → opp = QR
    fig, ax = nax()
    R, Q, P = np.array([0,0]), np.array([4,0]), np.array([0,3])
    rt_opp_adj(fig, ax, P, Q, R, ref='P', vnames=('P','Q','R'))
    ml(ax, R, Q, 'opp (QR)', s=-1, c='crimson'); ml(ax, P, R, 'adj (PR)', c='steelblue')
    ml(ax, P, Q, 'Hyp. (PQ)', k=0.28)
    al(ax, [P,Q,R]); sv(fig, pr+"05.png")

    # 06: PQR right at R, angle at P → adj = PR
    fig, ax = nax()
    R, Q, P = np.array([0,0]), np.array([4,0]), np.array([0,3])
    rt_opp_adj(fig, ax, P, Q, R, ref='P', vnames=('P','Q','R'))
    ml(ax, R, Q, 'opp (QR)', s=-1, c='gray'); ml(ax, P, R, 'adj (PR)', c='crimson')
    ml(ax, P, Q, 'Hyp.', k=0.28)
    al(ax, [P,Q,R]); sv(fig, pr+"06.png")

    # 07: PQR right at R, angle at Q → opp = PR
    fig, ax = nax()
    R, Q, P = np.array([0,0]), np.array([4,0]), np.array([0,3])
    rt_opp_adj(fig, ax, P, Q, R, ref='Q', vnames=('P','Q','R'))
    ml(ax, P, R, 'opp (PR)', c='crimson'); ml(ax, R, Q, 'adj (QR)', s=-1, c='steelblue')
    ml(ax, P, Q, 'Hyp.', k=0.28)
    al(ax, [P,Q,R]); sv(fig, pr+"07.png")

    # 08: PQR right at R, angle at Q → adj = QR
    fig, ax = nax()
    R, Q, P = np.array([0,0]), np.array([4,0]), np.array([0,3])
    rt_opp_adj(fig, ax, P, Q, R, ref='Q', vnames=('P','Q','R'))
    ml(ax, P, R, 'opp (PR)', c='gray'); ml(ax, R, Q, 'adj (QR)', s=-1, c='crimson')
    ml(ax, P, Q, 'Hyp.', k=0.28)
    al(ax, [P,Q,R]); sv(fig, pr+"08.png")

    # 09: ABC right at B, AB=6, BC=8, AC=10, angle A
    fig, ax = nax()
    B, C, A = np.array([0,0]), np.array([8,0]), np.array([0,6])
    pg(ax, [A,B,C]); rm(ax, B, A, C)
    vl(ax, A, 'A', [B,C]); vl(ax, B, 'B', [A,C]); vl(ax, C, 'C', [A,B])
    aoa(ax, A, B, C, r=0.3, col='crimson', lbl='\u03b1')
    ml(ax, A, B, '6'); ml(ax, B, C, '8', s=-1); ml(ax, A, C, 'AC=10 (Hyp.)', k=0.28)
    al(ax, [A,B,C]); sv(fig, pr+"09.png")

    # 10: Same triangle, angle at C
    fig, ax = nax()
    B, C, A = np.array([0,0]), np.array([8,0]), np.array([0,6])
    pg(ax, [A,B,C]); rm(ax, B, A, C)
    vl(ax, A, 'A', [B,C]); vl(ax, B, 'B', [A,C]); vl(ax, C, 'C', [A,B])
    aoa(ax, C, A, B, r=0.3, col='crimson', lbl='\u03b1')
    ml(ax, A, B, '6'); ml(ax, B, C, '8', s=-1); ml(ax, A, C, 'AC=10 (Hyp.)', k=0.28)
    al(ax, [A,B,C]); sv(fig, pr+"10.png")

    # 11: DEF right at F, DF=3, EF=4, DE=5, angle D
    fig, ax = nax()
    F, E, D = np.array([0,0]), np.array([4,0]), np.array([0,3])
    pg(ax, [D,E,F]); rm(ax, F, D, E)
    vl(ax, D, 'D', [E,F]); vl(ax, E, 'E', [D,F]); vl(ax, F, 'F', [D,E])
    aoa(ax, D, E, F, r=0.3, col='crimson', lbl='\u03b1')
    ml(ax, D, F, 'DF=3'); ml(ax, F, E, 'EF=4', s=-1); ml(ax, D, E, 'DE=5', k=0.28)
    al(ax, [D,E,F]); sv(fig, pr+"11.png")

    # 12: Same DEF, angle at E
    fig, ax = nax()
    F, E, D = np.array([0,0]), np.array([4,0]), np.array([0,3])
    pg(ax, [D,E,F]); rm(ax, F, D, E)
    vl(ax, D, 'D', [E,F]); vl(ax, E, 'E', [D,F]); vl(ax, F, 'F', [D,E])
    aoa(ax, E, D, F, r=0.3, col='crimson', lbl='\u03b1')
    ml(ax, D, F, 'DF=3'); ml(ax, F, E, 'EF=4', s=-1); ml(ax, D, E, 'DE=5', k=0.28)
    al(ax, [D,E,F]); sv(fig, pr+"12.png")

    # 13: opp=7, adj=24 → find hyp=25
    fig, ax = nax()
    sc = s4(24, 7)
    C, B, A = np.array([0,0]), np.array([24*sc,0]), np.array([0,7*sc])
    pg(ax, [A,B,C]); rm(ax, C, A, B)
    aoa(ax, B, A, C, r=0.3, col='crimson', lbl='\u03b1')
    ml(ax, A, C, 'opp=7', c='crimson'); ml(ax, C, B, 'adj=24', s=-1, c='steelblue')
    ml(ax, A, B, 'c=?', k=0.27, c='red')
    al(ax, [A,B,C]); sv(fig, pr+"13.png")

    # 14: PQR right at Q, PQ=15, PR=17 → find QR=8, angle P
    fig, ax = nax()
    sc = s4(8, 15)
    Q, R, P = np.array([0,0]), np.array([8*sc,0]), np.array([0,15*sc])
    pg(ax, [P,Q,R]); rm(ax, Q, P, R)
    vl(ax, P, 'P', [Q,R]); vl(ax, Q, 'Q', [P,R]); vl(ax, R, 'R', [P,Q])
    aoa(ax, P, Q, R, r=0.3, col='crimson', lbl='\u03b1')
    ml(ax, P, Q, 'PQ=15 (adj)'); ml(ax, Q, R, 'QR=? (opp)', s=-1, c='red')
    ml(ax, P, R, 'PR=17 (Hyp.)', k=0.28)
    al(ax, [P,Q,R]); sv(fig, pr+"14.png")

    # 15: opp=3×adj, adj=4, find hyp
    fig, ax = nax()
    adj, opp = 4, 12
    sc = s4(adj, opp)
    C, B, A = np.array([0,0]), np.array([adj*sc,0]), np.array([0,opp*sc])
    pg(ax, [A,B,C]); rm(ax, C, A, B)
    aoa(ax, B, A, C, r=0.3, col='crimson', lbl='\u03b1')
    ml(ax, A, C, 'opp=3\xd7adj=12', c='crimson'); ml(ax, C, B, 'adj=4', s=-1, c='steelblue')
    ml(ax, A, B, 'c=?', k=0.27, c='red')
    al(ax, [A,B,C]); sv(fig, pr+"15.png")

    # 16: ABC right at C, AC=5, AB=13, angle A → find BC=12
    fig, ax = nax()
    sc = s4(12, 5)
    C, B, A = np.array([0,0]), np.array([12*sc,0]), np.array([0,5*sc])
    pg(ax, [A,B,C]); rm(ax, C, A, B)
    vl(ax, A, 'A', [B,C]); vl(ax, B, 'B', [A,C]); vl(ax, C, 'C', [A,B])
    aoa(ax, A, B, C, r=0.3, col='crimson', lbl='\u03b1')
    ml(ax, A, C, 'AC=5 (adj)'); ml(ax, A, B, 'AB=13 (Hyp.)', k=0.27)
    ml(ax, C, B, 'BC=? (opp)', s=-1, c='red')
    al(ax, [A,B,C]); sv(fig, pr+"16.png")

    # 17: Ramp 5m, horizontal 3m, height=4m → angle with floor
    fig, ax = nax()
    base, hyp = np.array([3,0]), np.array([0,4])
    O = np.array([0,0])
    pg(ax, [O, base, np.array([3,4])], c='none')  # invisible guide
    ln(ax, O, base, lw=2, c='dimgray')  # ground
    ln(ax, O, hyp, lw=3, c='saddlebrown')  # wall/platform
    ln(ax, base, hyp, lw=2.5, c='royalblue')  # ramp
    rm(ax, O, base, hyp)
    aoa(ax, base, O, hyp, r=0.4, col='crimson', lbl='\u03b1')
    ml(ax, O, base, '3m', s=-1); ml(ax, O, hyp, 'h=4m (opp)')
    ml(ax, base, hyp, '5m (Hyp.)', k=0.28, c='royalblue')
    al(ax, [O, base, hyp]); sv(fig, pr+"17.png")

    # 18: XYZ right at Z, XY=25, XZ=20, angle X → find YZ=15
    fig, ax = nax()
    sc = s4(20, 15)
    Z, Y, X = np.array([0,0]), np.array([15*sc,0]), np.array([0,20*sc])
    pg(ax, [X,Y,Z]); rm(ax, Z, X, Y)
    vl(ax, X, 'X', [Y,Z]); vl(ax, Y, 'Y', [X,Z]); vl(ax, Z, 'Z', [X,Y])
    aoa(ax, X, Y, Z, r=0.3, col='crimson', lbl='\u03b1')
    ml(ax, X, Z, 'XZ=20 (adj)'); ml(ax, Z, Y, 'YZ=? (opp)', s=-1, c='red')
    ml(ax, X, Y, 'XY=25 (Hyp.)', k=0.28)
    al(ax, [X,Y,Z]); sv(fig, pr+"18.png")

    # 19: Wire 10m, ground 6m, pole height=8m → angle with ground
    fig, ax = nax()
    base = np.array([6,0]); top = np.array([0,8]); O = np.array([0,0])
    ln(ax, O, top, lw=3, c='saddlebrown')
    ln(ax, O, base, lw=2, c='dimgray')
    ln(ax, top, base, lw=2.5, c='royalblue')
    rm(ax, O, top, base)
    aoa(ax, base, O, top, r=0.5, col='crimson', lbl='\u03b1')
    ml(ax, O, base, '6m (adj)', s=-1); ml(ax, O, top, 'h=8m (opp)')
    ml(ax, base, top, '10m (Hyp.)', k=0.28, c='royalblue')
    al(ax, [O, top, base]); sv(fig, pr+"19.png")

    # 20: ABC right at C, AB=20, BC=10 → find AC=10√3, angle A
    fig, ax = nax()
    sc = s4(10*1.732, 10)
    C, B, A = np.array([0,0]), np.array([10*sc,0]), np.array([0,10*1.732*sc])
    pg(ax, [A,B,C]); rm(ax, C, A, B)
    vl(ax, A, 'A', [B,C]); vl(ax, B, 'B', [A,C]); vl(ax, C, 'C', [A,B])
    aoa(ax, A, B, C, r=0.3, col='crimson', lbl='\u03b1')
    ml(ax, C, B, 'BC=10 (opp)', s=-1, c='crimson')
    ml(ax, A, C, 'AC=? (adj)', c='red')
    ml(ax, A, B, 'AB=20 (Hyp.)', k=0.28)
    al(ax, [A,B,C]); sv(fig, pr+"20.png")

    print("  \u2713\u2713 1.3 complete (20 images)")

# ══════════════════════════════════════════════════════
#  4.2 – MIXED: FIND SIDE OR FIND ANGLE
# ══════════════════════════════════════════════════════
def ch42():
    pr = "10_4.2_ex"

    # 01: angle=37°, hyp=10 → find opp (sin)
    fig, ax = nax()
    C, B, A = np.array([0,0]), np.array([4,0]), np.array([0,3])
    pg(ax, [A,B,C]); rm(ax, C, A, B)
    aoa(ax, B, A, C, r=0.4, col='royalblue', lbl='37°')
    ml(ax, A, B, 'hyp=10'); ml(ax, A, C, 'x=?', c='red')
    al(ax, [A,B,C]); sv(fig, pr+"01.png")

    # 02: opp=6, hyp=10 → find angle (arcsin)
    fig, ax = nax()
    C, B, A = np.array([0,0]), np.array([4,0]), np.array([0,3])
    pg(ax, [A,B,C]); rm(ax, C, A, B)
    aoa(ax, B, A, C, r=0.4, col='red', lbl='?°')
    ml(ax, A, C, 'opp=6', c='crimson'); ml(ax, A, B, 'hyp=10')
    al(ax, [A,B,C]); sv(fig, pr+"02.png")

    # 03: angle=60°, hyp=8 → find adj (cos)
    fig, ax = nax()
    sc = s4(4, 3.46)
    C, B, A = np.array([0,0]), np.array([4*sc,0]), np.array([0,3.46*sc])
    pg(ax, [A,B,C]); rm(ax, C, A, B)
    aoa(ax, B, A, C, r=0.4, col='royalblue', lbl='60°')
    ml(ax, A, B, 'hyp=8'); ml(ax, C, B, 'adj=?', s=-1, c='red')
    al(ax, [A,B,C]); sv(fig, pr+"03.png")

    # 04: adj=5, hyp=10 → find angle (arccos) = 60°
    fig, ax = nax()
    C, B, A = np.array([0,0]), np.array([4,0]), np.array([0,3.46])
    pg(ax, [A,B,C]); rm(ax, C, A, B)
    aoa(ax, B, A, C, r=0.4, col='red', lbl='?°')
    ml(ax, C, B, 'adj=5', s=-1); ml(ax, A, B, 'hyp=10')
    al(ax, [A,B,C]); sv(fig, pr+"04.png")

    # 05: angle=45°, hyp=12 → find opp (sin45)
    fig, ax = nax()
    C, B, A = np.array([0,0]), np.array([3,0]), np.array([0,3])
    pg(ax, [A,B,C]); rm(ax, C, A, B)
    aoa(ax, B, A, C, r=0.4, col='royalblue', lbl='45°')
    ml(ax, A, B, 'hyp=12'); ml(ax, A, C, 'x=?', c='red')
    al(ax, [A,B,C]); sv(fig, pr+"05.png")

    # 06: opp=5, adj=5 → find angle=45° (arctan)
    fig, ax = nax()
    C, B, A = np.array([0,0]), np.array([3,0]), np.array([0,3])
    pg(ax, [A,B,C]); rm(ax, C, A, B)
    aoa(ax, B, A, C, r=0.4, col='red', lbl='?°')
    ml(ax, A, C, 'opp=5', c='crimson'); ml(ax, C, B, 'adj=5', s=-1, c='steelblue')
    al(ax, [A,B,C]); sv(fig, pr+"06.png")

    # 07: angle=53°, opp=8 → find hyp (sin)
    fig, ax = nax()
    sc = s4(6, 8)
    C, B, A = np.array([0,0]), np.array([6*sc,0]), np.array([0,8*sc])
    pg(ax, [A,B,C]); rm(ax, C, A, B)
    aoa(ax, B, A, C, r=0.4, col='royalblue', lbl='53°')
    ml(ax, A, C, 'opp=8', c='crimson'); ml(ax, A, B, 'c=?', k=0.27, c='red')
    al(ax, [A,B,C]); sv(fig, pr+"07.png")

    # 08: opp=8, adj=6 → find angle (arctan)
    fig, ax = nax()
    C, B, A = np.array([0,0]), np.array([3,0]), np.array([0,4])
    pg(ax, [A,B,C]); rm(ax, C, A, B)
    aoa(ax, B, A, C, r=0.4, col='red', lbl='?°')
    ml(ax, A, C, 'opp=8', c='crimson'); ml(ax, C, B, 'adj=6', s=-1, c='steelblue')
    al(ax, [A,B,C]); sv(fig, pr+"08.png")

    # 09: Ladder 13m, base 5m from wall → angle & height
    fig, ax = nax()
    sc = s4(5, 12)
    W = np.array([0,12*sc]); G = np.array([5*sc,0]); O = np.array([0,0])
    ln(ax, O, W, lw=3, c='saddlebrown'); ln(ax, O, G, lw=2, c='dimgray')
    ln(ax, W, G, lw=2.5, c='royalblue')
    rm(ax, O, W, G)
    aoa(ax, G, O, W, r=0.5, col='royalblue', lbl='\u03b1')
    ml(ax, O, G, '5m', s=-1); ml(ax, W, G, '13m', k=0.28, c='royalblue')
    ml(ax, O, W, 'h=?', c='red')
    al(ax, [O, W, G]); sv(fig, pr+"09.png")

    # 10: Building 24m, observer 18m away → elevation angle & direct distance
    fig, ax = nax()
    sc = s4(18, 24)
    B_top = np.array([0,24*sc]); B_bot = np.array([0,0]); Obs = np.array([18*sc,0])
    ln(ax, B_bot, B_top, lw=3, c='steelblue')
    ln(ax, B_bot, Obs, lw=2, c='dimgray')
    ln(ax, Obs, B_top, lw=2, c='royalblue', ls='--')
    rm(ax, B_bot, B_top, Obs)
    aoa(ax, Obs, B_bot, B_top, r=0.5, col='royalblue', lbl='\u03b1=?')
    ml(ax, B_bot, Obs, '18m', s=-1); ml(ax, B_bot, B_top, '24m')
    ml(ax, Obs, B_top, 'd=?', k=0.28, c='red')
    al(ax, [B_bot, B_top, Obs]); sv(fig, pr+"10.png")

    # 11: Triangle PQR, R=90°, PQ=20, angle P=37°
    fig, ax = nax()
    sc = s4(16, 12)
    R, Q, P = np.array([0,0]), np.array([16*sc,0]), np.array([0,12*sc])
    pg(ax, [P,Q,R]); rm(ax, R, P, Q)
    vl(ax, P, 'P', [Q,R]); vl(ax, Q, 'Q', [P,R]); vl(ax, R, 'R', [P,Q])
    aoa(ax, P, Q, R, r=0.35, col='royalblue', lbl='37°')
    ml(ax, P, Q, 'PQ=20 (Hyp.)'); ml(ax, R, Q, 'QR=?', s=-1, c='red')
    ml(ax, P, R, 'PR=?', c='red')
    al(ax, [P,Q,R]); sv(fig, pr+"11.png")

    # 12: opp=15, adj=20 → find angle (arctan) & hyp
    fig, ax = nax()
    sc = s4(20, 15)
    C, B, A = np.array([0,0]), np.array([20*sc,0]), np.array([0,15*sc])
    pg(ax, [A,B,C]); rm(ax, C, A, B)
    aoa(ax, B, A, C, r=0.4, col='red', lbl='?°')
    ml(ax, A, C, 'opp=15', c='crimson'); ml(ax, C, B, 'adj=20', s=-1, c='steelblue')
    ml(ax, A, B, 'c=?', k=0.27, c='red')
    al(ax, [A,B,C]); sv(fig, pr+"12.png")

    # 13: Ramp 5m long, angle=30°, find height and horizontal
    fig, ax = nax()
    sc = s4(4.33, 2.5)
    O = np.array([0,0]); T = np.array([0,2.5*sc]); G = np.array([4.33*sc,0])
    ln(ax, O, T, lw=2, c='saddlebrown')
    ln(ax, O, G, lw=2, c='dimgray')
    ln(ax, G, T, lw=2.5, c='royalblue')
    rm(ax, O, T, G)
    aoa(ax, G, O, T, r=0.5, col='royalblue', lbl='30°')
    ml(ax, G, T, '5m', k=0.28, c='royalblue'); ml(ax, O, T, 'h=?', c='red')
    ml(ax, O, G, 'horiz=?', s=-1, c='red')
    al(ax, [O, T, G]); sv(fig, pr+"13.png")

    # 14: Tower (15m) on hill (10m), observer 20m from base
    fig, ax = nax()
    base = np.array([0,0]); hill_top = np.array([0,2.0]); tower_top = np.array([0,3.5])
    obs = np.array([3,0])
    ln(ax, base, tower_top, lw=3, c='steelblue')
    ln(ax, base, obs, lw=2, c='dimgray')
    ln(ax, obs, hill_top, lw=1.5, c='royalblue', ls='--')
    ln(ax, obs, tower_top, lw=1.5, c='crimson', ls='--')
    rm(ax, base, tower_top, obs)
    aoa(ax, obs, base, hill_top, r=0.5, col='royalblue', lbl='\u03b11')
    aoa(ax, obs, base, tower_top, r=0.7, col='crimson', lbl='\u03b12')
    ml(ax, base, hill_top, '10m'); ml(ax, hill_top, tower_top, '15m', c='crimson')
    ml(ax, base, obs, '20m', s=-1)
    al(ax, [base, tower_top, obs]); sv(fig, pr+"14.png")

    # 15: ABC, C=90°, AC=9, BC=12 → find AB, angles
    fig, ax = nax()
    C, B, A = np.array([0,0]), np.array([12,0]), np.array([0,9])
    sc = s4(12, 9)
    C, B, A = np.array([0,0]), np.array([12*sc,0]), np.array([0,9*sc])
    pg(ax, [A,B,C]); rm(ax, C, A, B)
    vl(ax, A, 'A', [B,C]); vl(ax, B, 'B', [A,C]); vl(ax, C, 'C', [A,B])
    aoa(ax, A, B, C, r=0.35, col='royalblue', lbl='\u03b1=?')
    aoa(ax, B, A, C, r=0.35, col='crimson', lbl='\u03b2=?')
    ml(ax, A, C, 'AC=9'); ml(ax, C, B, 'BC=12', s=-1); ml(ax, A, B, 'AB=?', k=0.27, c='red')
    al(ax, [A,B,C]); sv(fig, pr+"15.png")

    # 16: Pendulum 4m from ceiling height 5m, horizontal offset=2m → angle of deviation
    fig, ax = nax()
    # Ground y=0; suspension at height 5; rope 4m; offset 2m → child height ≈1.54
    O = np.array([0.0, 5.0])
    hang = np.array([0.0, 1.0])          # vertical free-hang end
    child = np.array([2.0, 5.0 - 4.0 * np.cos(np.radians(30))])  # ≈(2, 1.536)
    ground_l, ground_r = np.array([-1.2, 0.0]), np.array([3.2, 0.0])
    ln(ax, ground_l, ground_r, lw=2, c='dimgray')             # ground
    ln(ax, O, hang, lw=1, c='dimgray', ls='--')               # vertical reference
    ln(ax, O, child, lw=2.5, c='royalblue')                   # actual rope
    ln(ax, hang, child, lw=1.5, c='dimgray', ls=':')
    rm(ax, hang, O, child)
    aoa(ax, O, hang, child, r=0.55, col='crimson', lbl='\u03b1=?')
    ml(ax, O, child, '4m', k=0.28, c='royalblue')
    ml(ax, hang, child, 'x=2m', s=-1)
    ml(ax, np.array([-0.9, 0]), np.array([-0.9, 5]), '5m', s=1, c='saddlebrown')
    ln(ax, np.array([-0.55, 0]), np.array([-0.55, 5]), lw=1, c='saddlebrown', ls=':')
    ax.plot(*O, 'ko', ms=6); ax.plot(*child, 'ro', ms=8)
    al(ax, [O, hang, child, ground_l, ground_r]); sv(fig, pr+"16.png")

    # 17: Slide+ladder: A top, B slide-foot, C ladder-foot, D foot of height
    # AC=2.5m (ladder), ∠ACD=46°, ∠ABD=63° → AD≈1.80, BD≈0.92, CD≈1.74, AB≈2.02
    fig, ax = nax()
    AD, BD, CD = 1.80, 0.92, 1.74
    D = np.array([0.0, 0.0]); A = np.array([0.0, AD])
    B = np.array([-BD, 0.0]); C = np.array([CD, 0.0])
    ln(ax, B, C, lw=2, c='dimgray')                # ground BC
    ln(ax, A, C, lw=2.5, c='saddlebrown')          # ladder AC
    ln(ax, A, B, lw=2.5, c='royalblue')            # slide AB
    ln(ax, A, D, lw=1.5, c='dimgray', ls='--')     # height AD
    rm(ax, D, A, B); rm(ax, D, A, C)
    aoa(ax, C, A, D, r=0.35, col='saddlebrown', lbl='46°')
    aoa(ax, B, A, D, r=0.40, col='royalblue', lbl='63°')
    ml(ax, A, C, 'AC=2.5m', k=0.28, c='saddlebrown')
    ml(ax, A, B, 'AB=?', k=0.28, c='royalblue')
    ml(ax, A, D, 'AD=?', k=0.22, c='red')
    ml(ax, B, D, 'BD=?', s=-1, c='red')
    vl(ax, A, 'A', [B, C]); vl(ax, B, 'B', [A, D])
    vl(ax, C, 'C', [A, D]); vl(ax, D, 'D', [A, B])
    al(ax, [A, B, C, D]); sv(fig, pr+"17.png")

    # 18: Right △ABC, ∠C=90°, median BD to AC; BD=14.3, ∠CDB=68°
    # CD≈5.36, BC≈13.26, AC≈10.72
    fig, ax = nax()
    sc = s4(13.26, 10.72)
    C = np.array([0.0, 0.0]); B = np.array([13.26*sc, 0.0])
    A = np.array([0.0, 10.72*sc]); D = np.array([0.0, 5.36*sc])
    pg(ax, [A, B, C])
    ln(ax, B, D, lw=2, c='royalblue', ls='--')
    rm(ax, C, A, B)
    vl(ax, A, 'A', [B, C]); vl(ax, B, 'B', [A, C])
    vl(ax, C, 'C', [A, B]); vl(ax, D, 'D', [B, C])
    aoa(ax, D, C, B, r=0.40, col='royalblue', lbl='68°')
    ml(ax, B, D, 'BD=14.3', k=0.30, c='royalblue')
    ml(ax, C, D, 'CD=?', k=0.22, c='red')
    ml(ax, C, B, 'BC=?', s=-1, c='red')
    al(ax, [A, B, C, D]); sv(fig, pr+"18.png")

    # 19: Bridge at 37°, length=15m; wall 7m at the NEAR (low) end
    # Bridge rises to h≈9.03 over horiz≈12; red line wall-top → bridge-top (for part ד)
    fig, ax = nax()
    sc = s4(12, 9.03)
    O = np.array([0.0, 0.0]); far = np.array([12*sc, 0.0])
    bridge_top = np.array([12*sc, 9.03*sc]); wall_top = np.array([0.0, 7*sc])
    ln(ax, O, far, lw=1.5, c='dimgray', ls='--')           # ground / horiz
    ln(ax, far, bridge_top, lw=1.5, c='dimgray', ls='--')  # height h
    ln(ax, O, bridge_top, lw=2.5, c='royalblue')           # bridge
    ln(ax, O, wall_top, lw=2.5, c='saddlebrown')           # wall at near end
    ln(ax, wall_top, bridge_top, lw=1.5, c='crimson', ls=':')
    rm(ax, far, O, bridge_top)
    aoa(ax, O, far, bridge_top, r=0.55, col='royalblue', lbl='37°')
    ml(ax, O, bridge_top, '15m', k=0.28, c='royalblue')
    ml(ax, O, wall_top, '7m', k=0.22, c='saddlebrown')
    ml(ax, O, far, 'horiz=?', s=-1)
    ml(ax, far, bridge_top, 'h=?', k=0.22, c='red')
    al(ax, [O, far, bridge_top, wall_top]); sv(fig, pr+"19.png")

    # 20: Lighthouse: two ships A and B, angles 12° and 20°
    fig, ax = nax()
    h, d = 3.0, 2.0  # representative
    O = np.array([0, 0]); tower_top = np.array([0, h])
    B_pt = np.array([d, 0]); A_pt = np.array([d + 2, 0])
    ln(ax, O, tower_top, lw=3, c='saddlebrown')
    ln(ax, O, A_pt, lw=2, c='dimgray')
    ln(ax, tower_top, B_pt, lw=1.5, c='royalblue', ls='--')
    ln(ax, tower_top, A_pt, lw=1.5, c='crimson', ls='--')
    aoa(ax, B_pt, O, tower_top, r=0.4, col='royalblue', lbl='20°')
    aoa(ax, A_pt, O, tower_top, r=0.3, col='crimson', lbl='12°')
    ax.text(d, -0.25, 'B', fontsize=12, ha='center', fontweight='bold')
    ax.text(d+2, -0.25, 'A', fontsize=12, ha='center', fontweight='bold')
    ml(ax, B_pt, A_pt, '300m', s=-1)
    ml(ax, O, tower_top, 'h=?', c='red')
    al(ax, [O, tower_top, A_pt]); sv(fig, pr+"20.png")

    print("  \u2713\u2713 4.2 complete (20 images)")

# ══════════════════════════════════════════════════════
#  5.1 – ISOSCELES TRIANGLE & GENERAL TRIANGLE
# ══════════════════════════════════════════════════════
def ch51():
    pr = "10_5.1_ex"

    def draw_iso(ax, hb, h, lbl_leg=None, lbl_base=None, lbl_h=None,
                 lbl_angle=None, show_alt=True):
        """Isosceles triangle A=(0,h), B=(-hb,0), C=(hb,0), altitude from A."""
        sc = s4(hb, h)
        A = np.array([0, h*sc]); B = np.array([-hb*sc, 0]); C = np.array([hb*sc, 0])
        D = np.array([0, 0])
        pg(ax, [A, B, C])
        if show_alt:
            ln(ax, A, D, lw=1.5, c='royalblue', ls='--')
            rm(ax, D, A, B)
        vl(ax, A, 'A', [B, C]); vl(ax, B, 'B', [A, C]); vl(ax, C, 'C', [A, B])
        if show_alt: vl(ax, D, 'D', [A, B])
        if lbl_leg: ml(ax, A, B, lbl_leg)
        if lbl_base: ml(ax, B, C, lbl_base, s=-1)
        if lbl_h:
            ml(ax, A, D, lbl_h, s=-1, c='royalblue')
        if lbl_angle:
            aoa(ax, B, A, C, r=0.35, col='royalblue', lbl=lbl_angle)
        al(ax, [A, B, C, D] if show_alt else [A, B, C])
        return A, B, C, D

    # 01: Isosceles ABC, AB=AC=13, BC=10, altitude AD → find AD=12
    fig, ax = nax()
    draw_iso(ax, 5, 12, lbl_leg='13', lbl_base='10', lbl_h='AD=?')
    sv(fig, pr+"01.png")

    # 02: Isosceles, legs=5, base=6 → find height=4
    fig, ax = nax()
    draw_iso(ax, 3, 4, lbl_leg='5', lbl_base='6', lbl_h='h=?')
    sv(fig, pr+"02.png")

    # 03: Isosceles, legs=17, base=16 → find height=15
    fig, ax = nax()
    draw_iso(ax, 8, 15, lbl_leg='17', lbl_base='16', lbl_h='h=?')
    sv(fig, pr+"03.png")

    # 04: General triangle, base=14, height=9
    fig, ax = nax()
    sc = s4(14, 9)
    B = np.array([0, 0]); C_ = np.array([14*sc, 0]); A = np.array([5*sc, 9*sc])
    D = np.array([5*sc, 0])
    pg(ax, [A, B, C_])
    ln(ax, A, D, lw=1.5, c='royalblue', ls='--')
    rm(ax, D, A, B)
    vl(ax, A, 'A', [B, C_]); vl(ax, B, 'B', [A, C_]); vl(ax, C_, 'C', [A, B])
    ml(ax, B, C_, 'base=14', s=-1); ml(ax, A, D, 'h=9', c='royalblue')
    al(ax, [A, B, C_, D]); sv(fig, pr+"04.png")

    # 05: Isosceles, base angle=60°, leg=10, find height=10sin60°=5√3
    fig, ax = nax()
    h = 10 * np.sin(np.radians(60)); hb = 10 * np.cos(np.radians(60))
    A, B, C, D = draw_iso(ax, hb, h, lbl_leg='10', lbl_h='h=?')
    aoa(ax, B, A, C, r=0.35, col='crimson', lbl='60°')
    sv(fig, pr+"05.png")

    # 06: Isosceles, apex angle=90°, legs=8 → base=8√2
    fig, ax = nax()
    h = 8 * np.cos(np.radians(45)); hb = 8 * np.sin(np.radians(45))
    A, B, C, D = draw_iso(ax, hb, h, lbl_leg='8', lbl_base='?', lbl_h=None, show_alt=False)
    aoa(ax, A, B, C, r=0.35, col='royalblue', lbl='90°')
    sv(fig, pr+"06.png")

    # 07: Isosceles, height=12, base=10 → find leg=13
    fig, ax = nax()
    draw_iso(ax, 5, 12, lbl_leg='leg=?', lbl_base='10', lbl_h='h=12')
    sv(fig, pr+"07.png")

    # 08: General triangle ABC, BC=20, AB=15, angle B=35°, altitude from A
    fig, ax = nax()
    sc = s4(20, 15 * np.sin(np.radians(35)))
    B = np.array([0, 0]); C_ = np.array([20*sc, 0])
    A = np.array([15*sc*np.cos(np.radians(35)), 15*sc*np.sin(np.radians(35))])
    D = np.array([A[0], 0])
    pg(ax, [A, B, C_])
    ln(ax, A, D, lw=1.5, c='royalblue', ls='--'); rm(ax, D, A, B)
    vl(ax, A, 'A', [B, C_]); vl(ax, B, 'B', [A, C_]); vl(ax, C_, 'C', [A, B])
    aoa(ax, B, A, C_, r=0.4, col='royalblue', lbl='35°')
    ml(ax, A, B, 'AB=15'); ml(ax, B, C_, 'BC=20', s=-1); ml(ax, A, D, 'AD=?', c='red')
    al(ax, [A, B, C_, D]); sv(fig, pr+"08.png")

    # 09: Isosceles ABC, AB=AC=26, BC=20, altitude AD
    fig, ax = nax()
    draw_iso(ax, 10, 24, lbl_leg='26', lbl_base='20', lbl_h='AD=?')
    sv(fig, pr+"09.png")

    # 10: Isosceles, base=22, base angle=40°
    fig, ax = nax()
    leg = 11 / np.cos(np.radians(40)); h = 11 * np.tan(np.radians(40))
    A, B, C, D = draw_iso(ax, 11, h, lbl_base='22', lbl_h='h=?')
    aoa(ax, B, A, C, r=0.4, col='royalblue', lbl='40°')
    ml(ax, A, B, 'leg=?', c='red')
    sv(fig, pr+"10.png")

    # 11: Isosceles, apex angle=100°, legs=15
    fig, ax = nax()
    h = 15 * np.cos(np.radians(50)); hb = 15 * np.sin(np.radians(50))
    A, B, C, D = draw_iso(ax, hb, h, lbl_leg='15', lbl_h='h=?')
    aoa(ax, A, B, C, r=0.4, col='royalblue', lbl='100°')
    ml(ax, B, C, 'base=?', s=-1, c='red')
    sv(fig, pr+"11.png")

    # 12: Isosceles, perimeter=56, base=16 → legs=20
    fig, ax = nax()
    draw_iso(ax, 8, 18.33, lbl_leg='leg=?', lbl_base='16', lbl_h='h=?')
    ax.text(0, 4.5, 'Perimeter=56', fontsize=10, ha='center', va='center', color='royalblue')
    sv(fig, pr+"12.png")

    # 13: General triangle ABC, BC=25, AB=18, angle B=50°
    fig, ax = nax()
    sc = s4(25, 18 * np.sin(np.radians(50)))
    B = np.array([0, 0]); C_ = np.array([25*sc, 0])
    A = np.array([18*sc*np.cos(np.radians(50)), 18*sc*np.sin(np.radians(50))])
    D = np.array([A[0], 0])
    pg(ax, [A, B, C_]); ln(ax, A, D, lw=1.5, c='royalblue', ls='--'); rm(ax, D, A, B)
    vl(ax, A, 'A', [B, C_]); vl(ax, B, 'B', [A, C_]); vl(ax, C_, 'C', [A, B])
    aoa(ax, B, A, C_, r=0.4, col='royalblue', lbl='50°')
    ml(ax, A, B, '18'); ml(ax, B, C_, '25', s=-1); ml(ax, A, D, 'AD=?', c='red')
    al(ax, [A, B, C_, D]); sv(fig, pr+"13.png")

    # 14: Isosceles, AB=AC, area=108, base=18 → AD=12
    fig, ax = nax()
    draw_iso(ax, 9, 12, lbl_leg='AB=AC', lbl_base='BC=18', lbl_h='AD=?')
    ax.text(0, 6, 'Area=108 cm\u00b2', fontsize=10, ha='center', va='center', color='royalblue')
    sv(fig, pr+"14.png")

    # 15: Equilateral triangle, side=12
    fig, ax = nax()
    h = 12 * np.sqrt(3) / 2
    A, B, C, D = draw_iso(ax, 6, h, lbl_leg='12', lbl_base='12', lbl_h='h=?')
    aoa(ax, B, A, C, r=0.4, col='royalblue', lbl='60°')
    sv(fig, pr+"15.png")

    # 16: Isosceles ABC, AB=AC=20, AD=16 → find BC
    fig, ax = nax()
    draw_iso(ax, 12, 16, lbl_leg='20', lbl_base='BC=?', lbl_h='AD=16')
    sv(fig, pr+"16.png")

    # 17: Isosceles, BC=24, area=180 → AD=15, find DE (E midpoint of AB)
    fig, ax = nax()
    sc = s4(12, 15)
    A = np.array([0, 15*sc]); B = np.array([-12*sc, 0]); C = np.array([12*sc, 0])
    D = np.array([0, 0]); E = (A + B) / 2
    pg(ax, [A, B, C])
    ln(ax, A, D, lw=1.5, c='royalblue', ls='--')
    ln(ax, D, E, lw=1.5, c='crimson', ls='--')
    rm(ax, D, A, B)
    vl(ax, A, 'A', [B, C]); vl(ax, B, 'B', [A, C]); vl(ax, C, 'C', [A, B])
    vl(ax, D, 'D', [A, B]); vl(ax, E, 'E', [A, B])
    ml(ax, A, D, 'AD=?', c='royalblue'); ml(ax, B, C, 'BC=24', s=-1)
    ml(ax, D, E, 'DE=?', c='red', k=0.28)
    ax.text(0, 15*sc + 0.55, 'Area=180 cm\u00b2', fontsize=10, ha='center', va='bottom', color='royalblue')
    al(ax, [A, B, C, D, E], pad=0.75); sv(fig, pr+"17.png")

    # 18: Right triangle ABC, B=90°, AB=7, BC=24, altitude BD⊥AC
    fig, ax = nax()
    sc = s4(24, 7)
    B = np.array([0, 0]); C_ = np.array([24*sc, 0]); A = np.array([0, 7*sc])
    # AC hypotenuse, BD altitude to AC
    AC = C_ - A; ac_len = np.linalg.norm(AC)
    BD_len = 7*24/25  # area formula: BD = AB*BC/AC = 7*24/25
    BD_dir = np.array([-AC[1], AC[0]]) / ac_len
    D = A + np.dot(B - A, AC/ac_len) * (AC/ac_len)
    pg(ax, [A, B, C_])
    ln(ax, B, D, lw=1.5, c='royalblue', ls='--'); rm(ax, D, B, A)
    vl(ax, A, 'A', [B, C_]); vl(ax, B, 'B', [A, C_])
    vl(ax, C_, 'C', [A, B]); vl(ax, D, 'D', [B, A])
    ml(ax, A, B, 'AB=7'); ml(ax, B, C_, 'BC=24', s=-1)
    ml(ax, B, D, 'BD=?', k=0.3, c='red', s=-1)
    al(ax, [A, B, C_, D]); sv(fig, pr+"18.png")

    # 19: Isosceles ABC, AB=AC=25, BC=14, altitude AD, altitude BE⊥AC
    fig, ax = nax()
    sc = s4(7, 24)
    A = np.array([0, 24*sc]); B = np.array([-7*sc, 0]); C = np.array([7*sc, 0])
    D = np.array([0, 0])
    # E: foot of altitude from B to AC
    AC_vec = C - A; ac_n = np.linalg.norm(AC_vec)
    E = A + np.dot(B - A, AC_vec/ac_n) * (AC_vec/ac_n)
    pg(ax, [A, B, C])
    ln(ax, A, D, lw=1.5, c='royalblue', ls='--')
    ln(ax, B, E, lw=1.5, c='crimson', ls='--')
    rm(ax, D, A, B); rm(ax, E, B, A)
    vl(ax, A, 'A', [B, C]); vl(ax, B, 'B', [A, C]); vl(ax, C, 'C', [A, B])
    vl(ax, D, 'D', [A, B]); vl(ax, E, 'E', [B, C])
    ml(ax, A, B, '25'); ml(ax, B, C, '14', s=-1)
    ml(ax, A, D, 'AD=?', c='red'); ml(ax, B, E, 'BE=?', c='red', k=0.28)
    al(ax, [A, B, C, D, E]); sv(fig, pr+"19.png")

    # 20: Roof (isosceles), base=10m, slope angle=35°
    fig, ax = nax()
    h = 5 * np.tan(np.radians(35)); leg = 5 / np.cos(np.radians(35))
    sc = s4(5, h)
    A = np.array([0, h*sc]); B = np.array([-5*sc, 0]); C = np.array([5*sc, 0])
    D = np.array([0, 0])
    pg(ax, [A, B, C]); ln(ax, A, D, lw=1.5, c='royalblue', ls='--')
    rm(ax, D, A, B)
    aoa(ax, B, A, C, r=0.4, col='royalblue', lbl='35°')
    ml(ax, B, C, 'base=10m', s=-1); ml(ax, A, B, 'slope=?', c='red')
    ml(ax, A, D, 'h=?', c='red')
    vl(ax, A, 'A', [B, C]); vl(ax, B, 'B', [A, C]); vl(ax, C, 'C', [A, B])
    al(ax, [A, B, C, D]); sv(fig, pr+"20.png")

    print("  \u2713\u2713 5.1 complete (20 images)")

# ══════════════════════════════════════════════════════
#  5.2 – RECTANGLE AND RHOMBUS
# ══════════════════════════════════════════════════════
def ch52():
    pr = "10_5.2_ex"

    def draw_rect_diag(ax, w, h, diag='AC', lbl_w=None, lbl_h=None,
                       lbl_d=None, lbl_ang=None):
        sc = s4(w, h)
        A = np.array([0,0]); B = np.array([w*sc,0])
        C = np.array([w*sc,h*sc]); D = np.array([0,h*sc])
        pg(ax, [A,B,C,D]); rm(ax, A, B, D)
        if diag == 'AC':
            ln(ax, A, C, lw=2, c='royalblue', ls='--')
            if lbl_d: ml(ax, A, C, lbl_d, k=0.28, c='royalblue')
            if lbl_ang: aoa(ax, A, B, C, r=0.4, col='crimson', lbl=lbl_ang)
        elif diag == 'BD':
            ln(ax, B, D, lw=2, c='royalblue', ls='--')
            if lbl_d: ml(ax, B, D, lbl_d, k=0.28, c='royalblue')
            if lbl_ang: aoa(ax, A, B, D, r=0.4, col='crimson', lbl=lbl_ang)
        vl(ax, A, 'A', [B,D]); vl(ax, B, 'B', [A,C])
        vl(ax, C, 'C', [B,D]); vl(ax, D, 'D', [A,C])
        if lbl_w: ml(ax, A, B, lbl_w, s=-1)
        if lbl_h: ml(ax, A, D, lbl_h)
        al(ax, [A,B,C,D])
        return A, B, C, D

    def draw_rhombus_diag(ax, d1, d2, lbl_d1=None, lbl_d2=None,
                          lbl_side=None, lbl_ang=None, ang_vertex='D'):
        sc = s4(d1/2, d2/2)
        A = np.array([0, d2/2*sc]); B = np.array([d1/2*sc, 0])
        C = np.array([0, -d2/2*sc]); D = np.array([-d1/2*sc, 0])
        O = np.array([0, 0])
        pg(ax, [A,B,C,D])
        ln(ax, A, C, lw=1.5, c='royalblue', ls='--')
        ln(ax, B, D, lw=1.5, c='crimson', ls='--')
        rm(ax, O, A, B)
        vl(ax, A, 'A', [B,D]); vl(ax, B, 'B', [A,C])
        vl(ax, C, 'C', [B,D]); vl(ax, D, 'D', [A,C])
        # Labels on half-diagonals (away from O) to avoid overlap at the center
        if lbl_d1: ml(ax, O, B, lbl_d1, k=0.28, s=-1)
        if lbl_d2: ml(ax, O, A, lbl_d2, k=0.28)
        if lbl_side: ml(ax, A, B, lbl_side)
        if lbl_ang:
            # Full vertex angle between the two sides (not side+diagonal)
            if ang_vertex == 'A':
                aoa(ax, A, D, B, r=0.3, col='royalblue', lbl=lbl_ang)
            elif ang_vertex == 'B':
                aoa(ax, B, A, C, r=0.3, col='royalblue', lbl=lbl_ang)
            else:
                aoa(ax, D, A, C, r=0.3, col='royalblue', lbl=lbl_ang)
        al(ax, [A,B,C,D])
        return A, B, C, D, O

    # 01: Rectangle, diagonal=10, angle=30° → find long side (cos)
    fig, ax = nax()
    w = 10*np.cos(np.radians(30)); h = 10*np.sin(np.radians(30))
    draw_rect_diag(ax, w, h, lbl_w='?', lbl_d='d=10', lbl_ang='30°')
    sv(fig, pr+"01.png")

    # 02: Rectangle, diagonal=13, angle=22° → find short side (sin)
    fig, ax = nax()
    w = 13*np.cos(np.radians(22)); h = 13*np.sin(np.radians(22))
    draw_rect_diag(ax, w, h, lbl_h='?', lbl_d='d=13', lbl_ang='22°')
    sv(fig, pr+"02.png")

    # 03: Rectangle, sides=6, 8 → find diagonal=10
    fig, ax = nax()
    draw_rect_diag(ax, 8, 6, lbl_w='8', lbl_h='6', lbl_d='d=?')
    sv(fig, pr+"03.png")

    # 04: Rhombus, side=10, acute angle=60° → find diagonals
    fig, ax = nax()
    d1 = 2*10*np.cos(np.radians(30)); d2 = 2*10*np.sin(np.radians(30))
    draw_rhombus_diag(ax, d1, d2, lbl_d1='d1=?', lbl_d2='d2=?', lbl_side='10', lbl_ang='60°')
    sv(fig, pr+"04.png")

    # 05: Square (rhombus 90°), side=6 → diagonal=6√2
    fig, ax = nax()
    draw_rhombus_diag(ax, 6*np.sqrt(2), 6*np.sqrt(2), lbl_d1='d=?', lbl_side='6')
    sv(fig, pr+"05.png")

    # 06: Rectangle, diagonal=20, angle=35° → find area
    fig, ax = nax()
    w = 20*np.cos(np.radians(35)); h = 20*np.sin(np.radians(35))
    draw_rect_diag(ax, w, h, lbl_d='d=20', lbl_ang='35°')
    ax.text(w*s4(w,h)/2, h*s4(w,h)/2, 'Area=?',
            fontsize=11, ha='center', va='center', color='red')
    sv(fig, pr+"06.png")

    # 07: Square, side=8 → diagonal=8√2
    fig, ax = nax()
    draw_rhombus_diag(ax, 8*np.sqrt(2), 8*np.sqrt(2), lbl_d1='d=?', lbl_side='8')
    sv(fig, pr+"07.png")

    # 08: Rectangle, sides=15, 8 → find diagonal=17 and angle
    fig, ax = nax()
    draw_rect_diag(ax, 15, 8, lbl_w='15', lbl_h='8', lbl_d='d=?', lbl_ang='?°')
    sv(fig, pr+"08.png")

    # 09: Rectangle ABCD, diagonal AC=16, angle BAC=38°
    fig, ax = nax()
    w = 16*np.cos(np.radians(38)); h = 16*np.sin(np.radians(38))
    draw_rect_diag(ax, w, h, lbl_w='AB=?', lbl_h='AD=?', lbl_d='AC=16', lbl_ang='38°')
    sv(fig, pr+"09.png")

    # 10: Rhombus, side=12, acute angle=72° → find diagonals
    fig, ax = nax()
    d1 = 2*12*np.cos(np.radians(36)); d2 = 2*12*np.sin(np.radians(36))
    draw_rhombus_diag(ax, d1, d2, lbl_d1='d1=?', lbl_d2='d2=?', lbl_side='12', lbl_ang='72°')
    sv(fig, pr+"10.png")

    # 11: Rectangle, perimeter=34, diagonal=13 → sides 12,5
    fig, ax = nax()
    draw_rect_diag(ax, 12, 5, lbl_w='?', lbl_h='?', lbl_d='d=13')
    ax.text(3, 4.5, 'P=34', fontsize=10, ha='center', color='royalblue')
    sv(fig, pr+"11.png")

    # 12: Rhombus, diagonals=24, 10 → find side and angle
    fig, ax = nax()
    draw_rhombus_diag(ax, 24, 10, lbl_d1='d1=24', lbl_d2='d2=10',
                      lbl_side='a=?', lbl_ang='?°')
    sv(fig, pr+"12.png")

    # 13: Rectangle, short side=9, diagonal=15 → long side=12
    # Part ג asks angle between diagonal and SHORT side → mark ∠CAD, not ∠BAC
    fig, ax = nax()
    sc = s4(12, 9)
    A = np.array([0.0, 0.0]); B = np.array([12*sc, 0.0])
    C = np.array([12*sc, 9*sc]); D = np.array([0.0, 9*sc])
    pg(ax, [A, B, C, D]); rm(ax, A, B, D)
    ln(ax, A, C, lw=2, c='royalblue', ls='--')
    vl(ax, A, 'A', [B, D]); vl(ax, B, 'B', [A, C])
    vl(ax, C, 'C', [B, D]); vl(ax, D, 'D', [A, C])
    ml(ax, A, B, 'long=?', s=-1)
    ml(ax, A, D, '9')
    ml(ax, A, C, 'd=15', k=0.28, c='royalblue')
    aoa(ax, A, D, C, r=0.45, col='crimson', lbl='?°')  # angle with short side AD
    al(ax, [A, B, C, D])
    sv(fig, pr+"13.png")

    # 14: Rhombus, side=7, obtuse angle=120° → acute=60°, find diagonals
    fig, ax = nax()
    d1 = 2*7*np.cos(np.radians(30)); d2 = 7  # d2 = 2*7*sin(30)
    # With d1>d2 the obtuse angles sit at A and C
    draw_rhombus_diag(ax, d1, d2, lbl_d1='d1=?', lbl_d2='d2=?',
                      lbl_side='7', lbl_ang='120°', ang_vertex='A')
    sv(fig, pr+"14.png")

    # 15: Rectangle, area=60, diagonal=13 → sides 5,12
    fig, ax = nax()
    draw_rect_diag(ax, 12, 5, lbl_w='?', lbl_h='?', lbl_d='d=13')
    ax.text(3, 4, 'Area=60', fontsize=10, ha='center', color='royalblue')
    sv(fig, pr+"15.png")

    # 16: Rhombus, area=120, one diagonal=20 → other diagonal=12
    fig, ax = nax()
    draw_rhombus_diag(ax, 20, 12, lbl_d1='d1=20', lbl_d2='d2=?', lbl_side='a=?', lbl_ang='?°')
    ax.text(0, 0.5, 'Area=120', fontsize=10, ha='center', color='royalblue')
    sv(fig, pr+"16.png")

    # 17: Rectangle ABCD, CM=7.8, angle ABD=63°
    fig, ax = nax()
    d = 2*7.8; w = d*np.cos(np.radians(63)); h = d*np.sin(np.radians(63))
    sc = s4(w, h)
    A = np.array([0.0, 0.0]); B = np.array([w*sc, 0.0])
    C = np.array([w*sc, h*sc]); D = np.array([0.0, h*sc])
    M = (A + C) / 2
    E = np.array([M[0], C[1]])  # on CD, ME || AD
    pg(ax, [A, B, C, D])
    ln(ax, A, C, lw=1.5, c='dimgray', ls='--')
    ln(ax, B, D, lw=1.5, c='dimgray', ls='--')
    ln(ax, M, E, lw=2, c='royalblue')
    rm(ax, A, B, D)
    vl(ax, A, 'A', [B, D]); vl(ax, B, 'B', [A, C])
    vl(ax, C, 'C', [B, D]); vl(ax, D, 'D', [A, C])
    vl(ax, M, 'M', [A, C]); vl(ax, E, 'E', [C, D, M])
    aoa(ax, B, A, D, r=0.45, col='crimson', lbl='63°')  # ∠ABD
    ml(ax, C, M, 'CM=7.8', k=0.28, c='royalblue')
    ml(ax, M, E, 'ME', k=0.22, c='royalblue')
    al(ax, [A, B, C, D, E], pad=0.7)
    sv(fig, pr+"17.png")

    # 18: Rectangle ABCD, AB=BE, AE=11.32, EC=4 (do not spoil AB/BC)
    fig, ax = nax()
    ab, ec = 8.0, 4.0
    bc = ab + ec
    sc = s4(ab, bc)
    A = np.array([0.0, 0.0]); B = np.array([ab*sc, 0.0])
    C = np.array([ab*sc, bc*sc]); D = np.array([0.0, bc*sc])
    E = np.array([ab*sc, ab*sc])  # on BC with BE = AB
    pg(ax, [A, B, C, D])
    ln(ax, A, E, lw=2, c='royalblue')
    ln(ax, A, C, lw=1.5, c='dimgray', ls='--')
    rm(ax, A, B, D)
    vl(ax, A, 'A', [B, D]); vl(ax, B, 'B', [A, C])
    vl(ax, C, 'C', [B, D]); vl(ax, D, 'D', [A, C])
    vl(ax, E, 'E', [B, C, A])
    ml(ax, A, E, 'AE=11.32', k=0.28, c='royalblue')
    ml(ax, E, C, 'EC=4', k=0.28, c='crimson')
    ml(ax, A, B, 'AB=BE=?', s=-1)
    ml(ax, B, C, 'BC=?')
    al(ax, [A, B, C, D, E], pad=0.75)
    sv(fig, pr+"18.png")

    # 19: Rhombus ABCD, AB=10.3, ∠ABC=128° (+ E,F for part ג)
    fig, ax = nax()
    a_side, ang = 10.3, 128.0
    acute = 180.0 - ang  # 52°
    sc = s4(a_side * (1 + abs(np.cos(np.radians(acute)))),
            a_side * np.sin(np.radians(acute)))
    A = np.array([0.0, 0.0])
    B = np.array([a_side*sc, 0.0])
    D = np.array([a_side*np.cos(np.radians(acute))*sc,
                  a_side*np.sin(np.radians(acute))*sc])
    C = B + (D - A)
    O = (A + C) / 2  # diagonals' midpoint
    F = np.array([D[0], 0.0])
    E = np.array([C[0], 0.0])
    pg(ax, [A, B, C, D])
    ln(ax, C, E, lw=1.3, c='steelblue', ls=':')
    ln(ax, E, F, lw=1.3, c='steelblue', ls=':')
    ln(ax, F, D, lw=1.3, c='steelblue', ls=':')
    ln(ax, A, C, lw=1.5, c='royalblue', ls='--')
    ln(ax, B, D, lw=1.5, c='crimson', ls='--')
    rm(ax, O, A, B)  # diagonals are perpendicular (not a vertex right-angle)
    vl(ax, A, 'A', [B, D]); vl(ax, B, 'B', [A, C])
    vl(ax, C, 'C', [B, D]); vl(ax, D, 'D', [A, C])
    vl(ax, E, 'E', [C, B]); vl(ax, F, 'F', [D, A])
    # ∠ABC=128° — arc at B; label placed outside to the right of B
    aoa(ax, B, A, C, r=0.5, col='royalblue', lbl=None)
    ax.text(B[0] + 0.55, B[1] + 0.35, '128°', fontsize=11, ha='left', va='center', color='royalblue')
    ax.text((A[0]+B[0])/2, -0.55, 'AB=10.3', fontsize=11, ha='center', va='top')
    ml(ax, A, C, 'AC=?', k=0.22, c='royalblue')
    ml(ax, B, D, 'BD=?', k=0.22, c='crimson')
    al(ax, [A, B, C, D, E, F], pad=0.85)
    sv(fig, pr+"19.png")

    # 20: Rectangle ABCD 12×9 and Rhombus PQRS side=10, ∠PQR=110°
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.5, 4.4))
    for _ax in (ax1, ax2):
        _ax.set_aspect('equal'); _ax.axis('off')
    fig.patch.set_facecolor('white')

    sc = s4(12, 9)
    A = np.array([0.0, 0.0]); B = np.array([12*sc, 0.0])
    C = np.array([12*sc, 9*sc]); D = np.array([0.0, 9*sc])
    pg(ax1, [A, B, C, D])
    ln(ax1, A, C, lw=2, c='royalblue', ls='--')
    vl(ax1, A, 'A', [B, D]); vl(ax1, B, 'B', [A, C])
    vl(ax1, C, 'C', [B, D]); vl(ax1, D, 'D', [A, C])
    ml(ax1, A, B, '12', s=-1); ml(ax1, A, D, '9')
    ml(ax1, A, C, 'd=?', k=0.28, c='royalblue')
    ax1.text(6*sc, -1.0, 'Rectangle ABCD', fontsize=10, ha='center', color='steelblue')
    al(ax1, [A, B, C, D], pad=0.9)

    half = np.radians(55)
    Qp = np.array([0.0, 0.0])
    Pp = np.array([10*np.cos(half), 10*np.sin(half)])
    Rp = np.array([10*np.cos(half), -10*np.sin(half)])
    Sp = Pp + Rp - Qp
    scr = s4(max(Pp[0], Sp[0]), Pp[1])
    Pp, Qp, Rp, Sp = Pp*scr, Qp*scr, Rp*scr, Sp*scr
    Op = (Pp + Rp) / 2
    pg(ax2, [Pp, Qp, Rp, Sp])
    ln(ax2, Pp, Rp, lw=1.5, c='royalblue', ls='--')
    ln(ax2, Qp, Sp, lw=1.5, c='crimson', ls='--')
    rm(ax2, Op, Pp, Qp)
    vl(ax2, Pp, 'P', [Qp, Sp]); vl(ax2, Qp, 'Q', [Pp, Rp])
    vl(ax2, Rp, 'R', [Qp, Sp]); vl(ax2, Sp, 'S', [Pp, Rp])
    ml(ax2, Pp, Qp, '10')
    aoa(ax2, Qp, Pp, Rp, r=0.3, col='royalblue', lbl='110°')
    ml(ax2, Op, Pp, 'd1=?', k=0.26)
    ml(ax2, Op, Qp, 'd2=?', k=0.26, s=-1)
    ax2.text(Op[0], Rp[1]-0.9, 'Rhombus PQRS', fontsize=10, ha='center', color='steelblue')
    al(ax2, [Pp, Qp, Rp, Sp], pad=0.9)

    sv(fig, pr+"20.png")

    print("  \u2713\u2713 5.2 complete (20 images)")

# ══════════════════════════════════════════════════════
#  5.3 – TRAPEZOID
# ══════════════════════════════════════════════════════
def ch53():
    pr = "10_5.3_ex"

    def draw_iso_trap(ax, long_b, short_b, h, lbl_long=None, lbl_short=None,
                      lbl_leg=None, lbl_h=None, lbl_ang=None, show_heights=True):
        """Isosceles trapezoid with optional heights and labels."""
        sc = s4(long_b, h)
        off = (long_b - short_b) / 2
        B = np.array([0, 0]); C_ = np.array([long_b*sc, 0])
        A = np.array([off*sc, h*sc]); D = np.array([(off+short_b)*sc, h*sc])
        pg(ax, [A, B, C_, D])
        E = np.array([off*sc, 0]); F = np.array([(off+short_b)*sc, 0])
        if show_heights:
            ln(ax, A, E, lw=1.5, c='royalblue', ls='--')
            ln(ax, D, F, lw=1.5, c='royalblue', ls='--')
            rm(ax, E, A, B); rm(ax, F, D, C_)
        vl(ax, A, 'A', [B, D]); vl(ax, B, 'B', [A, C_])
        vl(ax, C_, 'C', [B, D]); vl(ax, D, 'D', [A, C_])
        if lbl_long: ml(ax, B, C_, lbl_long, s=-1)
        if lbl_short: ml(ax, A, D, lbl_short)
        if lbl_leg: ml(ax, A, B, lbl_leg)
        if lbl_h and show_heights:
            ml(ax, A, E, lbl_h, s=-1, c='royalblue')
        if lbl_ang: aoa(ax, B, A, C_, r=0.4, col='crimson', lbl=lbl_ang)
        al(ax, [A, B, C_, D, E, F])
        return A, B, C_, D, E, F

    # 01: Isosceles trap, long=30, short=10, angle=30° → h=10tan30°≈5.77
    fig, ax = nax()
    h = 10 * np.tan(np.radians(30))
    draw_iso_trap(ax, 30, 10, h, lbl_long='30', lbl_short='10', lbl_h='h=?', lbl_ang='30°')
    sv(fig, pr+"01.png")

    # 02: Isosceles trap, long=20, short=8, h=6 → find area
    fig, ax = nax()
    draw_iso_trap(ax, 20, 8, 6, lbl_long='20', lbl_short='8', lbl_h='h=6')
    ax.text(10*s4(20,6), 3*s4(20,6), 'Area=?', fontsize=11, ha='center', color='red')
    sv(fig, pr+"02.png")

    # 03: Isosceles trap, long=26, short=10, angle=45° → h=8, leg=8√2
    fig, ax = nax()
    h = 8 * np.tan(np.radians(45))
    draw_iso_trap(ax, 26, 10, h, lbl_long='26', lbl_short='10',
                  lbl_leg='leg=?', lbl_h='h=?', lbl_ang='45°')
    sv(fig, pr+"03.png")

    # 04: Isosceles trap, leg=10, long=22, angle=60° → short=12
    fig, ax = nax()
    h = 10*np.sin(np.radians(60)); ex = 10*np.cos(np.radians(60))
    short = 22 - 2*ex
    draw_iso_trap(ax, 22, max(short,1), h, lbl_long='22', lbl_short='short=?',
                  lbl_leg='10', lbl_h='h', lbl_ang='60°')
    sv(fig, pr+"04.png")

    # 05: Isosceles trap, h=12, long=28, leg=13 → short=18
    fig, ax = nax()
    draw_iso_trap(ax, 28, 18, 12, lbl_long='28', lbl_short='short=?',
                  lbl_leg='13', lbl_h='h=12')
    sv(fig, pr+"05.png")

    # 06: General trap, bases=10,18, h=7 → area
    fig, ax = nax()
    sc = s4(18, 7)
    B = np.array([0,0]); C_ = np.array([18*sc,0])
    A = np.array([2*sc, 7*sc]); D = np.array([12*sc, 7*sc])
    E = np.array([2*sc, 0]); F = np.array([12*sc, 0])
    pg(ax, [A,B,C_,D])
    ln(ax, A, E, lw=1.5, c='royalblue', ls='--'); rm(ax, E, A, B)
    vl(ax, A, 'A', [B,D]); vl(ax, B, 'B', [A,C_])
    vl(ax, C_, 'C', [B,D]); vl(ax, D, 'D', [A,C_])
    ml(ax, B, C_, '18', s=-1); ml(ax, A, D, '10')
    ml(ax, A, E, 'h=7', s=-1, c='royalblue')
    ax.text(9*sc, 3.5*sc, 'Area=?', fontsize=11, ha='center', color='red')
    al(ax, [A,B,C_,D,E]); sv(fig, pr+"06.png")

    # 07: Isosceles trap, bases=14,30, h=8 → area & leg
    fig, ax = nax()
    draw_iso_trap(ax, 30, 14, 8, lbl_long='30', lbl_short='14',
                  lbl_leg='leg=?', lbl_h='h=8')
    ax.text(15*s4(30,8), 4*s4(30,8), 'Area=?', fontsize=11, ha='center', color='red')
    sv(fig, pr+"07.png")

    # 08: Isosceles trap, angle=50°, leg=15 → h=15sin50°
    fig, ax = nax()
    h = 15*np.sin(np.radians(50)); ex = 15*np.cos(np.radians(50))
    draw_iso_trap(ax, 10+2*ex, 10, h, lbl_leg='15', lbl_h='h=?', lbl_ang='50°')
    sv(fig, pr+"08.png")

    # 09: ABCD, AD=12, BC=30, angle ABC=55°
    fig, ax = nax()
    ex = 9; h = ex*np.tan(np.radians(55))
    draw_iso_trap(ax, 30, 12, h, lbl_long='BC=30', lbl_short='AD=12',
                  lbl_leg='AB=?', lbl_h='h=?', lbl_ang='55°')
    sv(fig, pr+"09.png")

    # 10: Isosceles trap, bases=18,42, legs=15 → h=9
    fig, ax = nax()
    draw_iso_trap(ax, 42, 18, 9, lbl_long='42', lbl_short='18',
                  lbl_leg='15', lbl_h='h=?')
    sv(fig, pr+"10.png")

    # 11: Isosceles trap, area=150, h=10, long=22 → short=8
    fig, ax = nax()
    draw_iso_trap(ax, 22, 8, 10, lbl_long='22', lbl_short='?', lbl_h='h=10')
    ax.text(11*s4(22,10), 5*s4(22,10), 'Area=150', fontsize=10, ha='center', color='royalblue')
    sv(fig, pr+"11.png")

    # 12: Isosceles trap, perimeter=72, bases=16,24 → legs=16, h≈15.49
    fig, ax = nax()
    draw_iso_trap(ax, 24, 16, 15.49, lbl_long='24', lbl_short='16',
                  lbl_leg='leg=?', lbl_h='h=?')
    ax.text(12*s4(24,15.49), 7.5*s4(24,15.49), 'P=72', fontsize=10, ha='center', color='royalblue')
    sv(fig, pr+"12.png")

    # 13: General trapezoid ABCD, AB=20, AD=13, angle ADC=67.4°
    fig, ax = nax()
    h = 13*np.sin(np.radians(67.4)); DE = 13*np.cos(np.radians(67.4))
    FC = 15*np.cos(np.radians(53)); BF = 15*np.sin(np.radians(53))
    DC_len = DE + 20 + FC
    sc = s4(DC_len, h)
    D = np.array([0,0]); C_ = np.array([DC_len*sc,0])
    A = np.array([DE*sc, h*sc]); B = np.array([(DE+20)*sc, h*sc])
    E_pt = np.array([DE*sc,0]); F_pt = np.array([(DE+20)*sc, 0])
    pg(ax, [A,B,C_,D])
    ln(ax, A, E_pt, lw=1.5, c='royalblue', ls='--')
    ln(ax, B, F_pt, lw=1.5, c='crimson', ls='--')
    rm(ax, E_pt, A, D); rm(ax, F_pt, B, C_)
    vl(ax, A, 'A', [B,D]); vl(ax, B, 'B', [A,C_])
    vl(ax, C_, 'C', [B,D]); vl(ax, D, 'D', [A,C_])
    vl(ax, E_pt, 'E', [A,D]); vl(ax, F_pt, 'F', [B,C_])
    aoa(ax, D, A, C_, r=0.4, col='royalblue', lbl='67.4°')
    ml(ax, A, B, 'AB=20'); ml(ax, A, D, 'AD=13', s=-1)
    ml(ax, A, E_pt, 'h=?', c='red'); ml(ax, B, C_, 'BC=15')
    al(ax, [A,B,C_,D,E_pt,F_pt]); sv(fig, pr+"13.png")

    # 14: Isosceles trap ABCD, diagonal AC=25, BC=31, angle ABC=45° → h=7, AD=17
    fig, ax = nax()
    A, B, C_, D, E, F = draw_iso_trap(ax, 31, 17, 7,
                  lbl_long='BC=31', lbl_short='AD=?', lbl_h='h=?', lbl_ang='45°')
    ln(ax, A, C_, lw=1.5, c='crimson', ls='--')
    ml(ax, A, C_, 'AC=25', k=0.32, c='crimson')
    sv(fig, pr+"14.png")

    # 15: Isosceles trap, h=6, long=30, angle=45° → leg=6√2, short=18
    fig, ax = nax()
    draw_iso_trap(ax, 30, 18, 6, lbl_long='30', lbl_short='short=?',
                  lbl_leg='leg=?', lbl_h='h=6', lbl_ang='45°')
    sv(fig, pr+"15.png")

    # 16: Isosceles trap, long=50, leg=17, h=15 → short=34
    fig, ax = nax()
    draw_iso_trap(ax, 50, 34, 15, lbl_long='50', lbl_short='?',
                  lbl_leg='17', lbl_h='h=15', lbl_ang='?°')
    ax.text(25*s4(50,15), 7.5*s4(50,15), 'Area=?', fontsize=10, ha='center', color='red')
    sv(fig, pr+"16.png")

    # 17: Isosceles trap, AD=12, BC=48, angle DCB=40° — feet G,H labeled
    fig, ax = nax()
    h = 18*np.tan(np.radians(40))
    A, B, C_, D, G, H = draw_iso_trap(ax, 48, 12, h, lbl_long='BC=48', lbl_short='AD=12',
                  lbl_h='h=?', lbl_ang=None)
    vl(ax, G, 'G', [A, B]); vl(ax, H, 'H', [D, C_])
    aoa(ax, C_, D, B, r=0.4, col='crimson', lbl='40°')
    sv(fig, pr+"17.png")

    # 18: General trapezoid ABCD, AB=17, AD=13, BC=15, angle BCD=53° — E,F labeled
    fig, ax = nax()
    h_val = 12.0; DE = 5.0; FC = 9.0
    DC_len = DE + 17 + FC
    sc = s4(DC_len, h_val)
    D = np.array([0,0]); C_ = np.array([DC_len*sc,0])
    A = np.array([DE*sc, h_val*sc]); B = np.array([(DE+17)*sc, h_val*sc])
    E_pt = np.array([DE*sc, 0]); F_pt = np.array([(DE+17)*sc, 0])
    pg(ax, [A,B,C_,D])
    ln(ax, A, E_pt, lw=1.5, c='royalblue', ls='--')
    ln(ax, B, F_pt, lw=1.5, c='crimson', ls='--')
    rm(ax, E_pt, A, D); rm(ax, F_pt, B, C_)
    vl(ax, A, 'A', [B,D]); vl(ax, B, 'B', [A,C_])
    vl(ax, C_, 'C', [B,D]); vl(ax, D, 'D', [A,C_])
    vl(ax, E_pt, 'E', [A,D]); vl(ax, F_pt, 'F', [B,C_])
    aoa(ax, C_, B, D, r=0.4, col='crimson', lbl='53°')
    ml(ax, A, B, 'AB=17'); ml(ax, A, D, 'AD=13'); ml(ax, B, C_, 'BC=15', s=-1)
    ml(ax, A, E_pt, 'h=?', c='red')
    al(ax, [A,B,C_,D,E_pt,F_pt]); sv(fig, pr+"18.png")

    # 19: Isosceles trap AB∥DC, AB=10 (top), DC=34 (bottom), ∠BCD=35°
    fig, ax = nax()
    ex = 12; h = ex * np.tan(np.radians(35)); short_b = 10; long_b = 34
    sc = s4(long_b, h)
    D = np.array([0.0, 0.0]); C_ = np.array([long_b * sc, 0.0])
    A = np.array([ex * sc, h * sc]); B = np.array([(ex + short_b) * sc, h * sc])
    E = np.array([ex * sc, 0.0]); F = np.array([(ex + short_b) * sc, 0.0])
    pg(ax, [A, B, C_, D])
    ln(ax, A, E, lw=1.5, c='royalblue', ls='--')
    ln(ax, B, F, lw=1.5, c='royalblue', ls='--')
    rm(ax, E, A, D); rm(ax, F, B, C_)
    vl(ax, A, 'A', [B, D]); vl(ax, B, 'B', [A, C_])
    vl(ax, C_, 'C', [B, D]); vl(ax, D, 'D', [A, C_])
    aoa(ax, C_, B, D, r=0.4, col='crimson', lbl='35°')
    ml(ax, A, B, 'AB=10'); ml(ax, D, C_, 'DC=34', s=-1)
    ml(ax, A, E, 'h=?', s=-1, c='royalblue', k=0.21)
    ml(ax, B, C_, 'leg=?', k=0.25)
    al(ax, [A, B, C_, D, E, F]); sv(fig, pr+"19.png")

    # 20: Isosceles trap, AD=8, BC=24, leg AB=10 — midpoints M,N for part ד
    fig, ax = nax()
    h = np.sqrt(10**2 - 8**2)  # = 6
    A, B, C_, D, E, F = draw_iso_trap(ax, 24, 8, h, lbl_long='BC=24', lbl_short='AD=8',
                  lbl_leg='AB=10', lbl_h='h=?', lbl_ang='?°')
    M = (A + B) / 2; N = (D + C_) / 2
    ln(ax, M, N, lw=1.5, c='darkgreen', ls='--')
    vl(ax, M, 'M', [A, B]); vl(ax, N, 'N', [D, C_])
    sv(fig, pr+"20.png")

    print("  \u2713\u2713 5.3 complete (20 images)")

# ══════════════════════════════════════════════════════
#  6.1 – REAL-WORLD WORD PROBLEMS
# ══════════════════════════════════════════════════════
def ch61():
    pr = "10_6.1_ex"

    def ladder_scene(ax, ladder_len, ground_dist, height, angle_label=None, q='h',
                     show_ground=False):
        """Wall on left, ground at bottom, ladder leaning against wall."""
        O = np.array([0,0]); wall_top = np.array([0, height])
        gnd = np.array([ground_dist, 0])
        ln(ax, np.array([-0.1,0]), np.array([-0.1, height+0.3]), lw=4, c='dimgray')  # wall
        ln(ax, np.array([-0.3, 0]), np.array([ground_dist+0.3, 0]), lw=3, c='saddlebrown')  # ground
        ln(ax, gnd, wall_top, lw=2.5, c='royalblue')  # ladder
        rm(ax, O, gnd, wall_top)
        if angle_label:
            aoa(ax, gnd, O, wall_top, r=0.5, col='crimson', lbl=angle_label)
        q_color = 'red'
        if q == 'h': ml(ax, O, wall_top, 'h=?', c=q_color)
        elif q == 'ang': pass
        elif q == 'dist': ml(ax, O, gnd, 'd=?', s=-1, c=q_color)
        ml(ax, gnd, wall_top, f'{ladder_len}m', k=0.3, c='royalblue')
        # Do not label a computed ground distance — that spoils unknowns (ex01/ex09).
        if show_ground and q != 'dist':
            gtxt = f'{ground_dist:.2f}'.rstrip('0').rstrip('.') + 'm'
            ml(ax, O, gnd, gtxt, s=-1)
        al(ax, [O, wall_top, gnd, np.array([-0.3,0])])

    def pole_shadow(ax, height, shadow_len, sun_angle=None, q='h'):
        """Pole (vertical) with shadow on ground."""
        O = np.array([0,0]); top = np.array([0, height])
        tip = np.array([shadow_len, 0])
        ln(ax, np.array([0,-0.1]), np.array([shadow_len+0.3,-0.1]), lw=3, c='saddlebrown')  # ground
        ln(ax, O, top, lw=3, c='steelblue')  # pole
        ln(ax, O, tip, lw=2, c='goldenrod')  # shadow
        ln(ax, top, tip, lw=1.5, c='orange', ls='--')  # sun ray
        rm(ax, O, top, tip)
        if sun_angle: aoa(ax, tip, O, top, r=0.5, col='orange', lbl=sun_angle)
        if q == 'h': ml(ax, O, top, 'h=?', c='red')
        elif q == 'dist': ml(ax, O, tip, 'd=?', s=-1, c='red')
        if height and q != 'h': ml(ax, O, top, f'{height}m')
        if shadow_len and q != 'dist': ml(ax, O, tip, f'{shadow_len}m', s=-1)
        al(ax, [O, top, tip, np.array([0,-0.2])])

    # 01: Ladder 6m, angle=65° → find height
    fig, ax = nax()
    h = 6*np.sin(np.radians(65)); d = 6*np.cos(np.radians(65))
    ladder_scene(ax, 6, d, h, angle_label='65°', q='h')
    sv(fig, pr+"01.png")

    # 02: Ramp 8m, slope=12° → height difference
    fig, ax = nax()
    h = 8*np.sin(np.radians(12)); horiz = 8*np.cos(np.radians(12))
    O = np.array([0,0]); T = np.array([0, h]); G = np.array([horiz, 0])
    ln(ax, O, G, lw=3, c='saddlebrown'); ln(ax, G, T, lw=2.5, c='royalblue')
    ln(ax, O, T, lw=1.5, c='dimgray', ls='--')
    rm(ax, O, T, G)
    aoa(ax, G, O, T, r=0.5, col='crimson', lbl='12°')
    ml(ax, G, T, '8m (ramp)', k=0.28, c='royalblue')
    ml(ax, O, T, 'h=?', c='red'); ml(ax, O, G, 'horiz', s=-1)
    al(ax, [O, T, G]); sv(fig, pr+"02.png")

    # 03: TV screen diagonal=50", angle=28° → width and height
    fig, ax = nax()
    w = 50*np.cos(np.radians(28)); h = 50*np.sin(np.radians(28))
    sc = s4(w, h)
    A, B, C, D = (np.array([0,0]), np.array([w*sc,0]),
                  np.array([w*sc,h*sc]), np.array([0,h*sc]))
    pg(ax, [A,B,C,D])
    ln(ax, A, C, lw=2, c='royalblue', ls='--')
    aoa(ax, A, B, C, r=0.4, col='crimson', lbl='28°')
    ml(ax, A, C, '50"', k=0.28, c='royalblue')
    ml(ax, A, B, 'width=?', s=-1, c='red'); ml(ax, A, D, 'height=?', c='red')
    vl(ax, A, 'A', [B,D]); vl(ax, C, 'C', [B,D])
    al(ax, [A,B,C,D]); sv(fig, pr+"03.png")

    # 04: Pole shadow=5m, sun angle=40° → pole height
    fig, ax = nax()
    h = 5*np.tan(np.radians(40))
    pole_shadow(ax, h, 5, sun_angle='40°', q='h')
    sv(fig, pr+"04.png")

    # 05: Slide height=3m, angle=40° → slide length
    fig, ax = nax()
    slide_len = 3 / np.sin(np.radians(40)); horiz = 3 / np.tan(np.radians(40))
    O = np.array([0,0]); top = np.array([horiz, 3]); base = np.array([0,3])
    ln(ax, O, np.array([horiz+0.2, 0]), lw=3, c='saddlebrown')  # ground
    ln(ax, base, np.array([0,-0.1]), lw=2, c='dimgray')   # support
    ln(ax, O, top, lw=2.5, c='royalblue')                  # slide
    ln(ax, base, top, lw=1.5, c='dimgray', ls='--')        # platform
    rm(ax, O, top, np.array([0,0]))
    aoa(ax, O, np.array([horiz,0]), top, r=0.5, col='crimson', lbl='40°')
    ml(ax, O, top, 'slide=?', k=0.28, c='red')
    ml(ax, base, top, ''); ml(ax, O, base, '3m', c='darkgreen')
    al(ax, [O, top, base]); sv(fig, pr+"05.png")

    # 06: Sail (mast=3m, base angle=50°) → hypotenuse of sail
    fig, ax = nax()
    h = 3; hyp = h / np.sin(np.radians(50)); base_len = h / np.tan(np.radians(50))
    O = np.array([0,0]); top = np.array([0,h]); tip = np.array([base_len,0])
    ln(ax, O, top, lw=3, c='saddlebrown')    # mast
    ln(ax, O, tip, lw=2, c='dimgray')        # boom
    ln(ax, top, tip, lw=2.5, c='royalblue')  # sail hyp
    rm(ax, O, top, tip)
    aoa(ax, tip, O, top, r=0.5, col='crimson', lbl='50°')
    ml(ax, O, top, 'mast=3m'); ml(ax, top, tip, 'hyp=?', k=0.28, c='red')
    al(ax, [O, top, tip]); sv(fig, pr+"06.png")

    # 07: Stairs rise=20cm, run=28cm → slope angle
    fig, ax = nax()
    O = np.array([0,0]); run = np.array([2.8,0]); up = np.array([0,2.0])
    G = np.array([2.8, 2.0])
    ln(ax, O, run, lw=2, c='dimgray'); ln(ax, run, G, lw=2, c='dimgray')
    ln(ax, O, G, lw=2.5, c='royalblue', ls='--')
    rm(ax, run, O, G)
    aoa(ax, O, run, G, r=0.5, col='crimson', lbl='?°')
    ml(ax, O, run, '28cm', s=-1); ml(ax, run, G, '20cm', s=-1)
    ml(ax, O, G, 'slope', k=0.28, c='royalblue')
    al(ax, [O, run, G]); sv(fig, pr+"07.png")

    # 08: Car on hill, slope=8°, road=200m → vertical height
    fig, ax = nax()
    h = 200*np.sin(np.radians(8)); horiz = 200*np.cos(np.radians(8))
    sc = s4(horiz, h)
    O = np.array([0,0]); road_end = np.array([horiz*sc, h*sc])
    ln(ax, O, np.array([horiz*sc+0.3, 0]), lw=3, c='saddlebrown')
    ln(ax, O, road_end, lw=2.5, c='royalblue')
    ln(ax, road_end, np.array([horiz*sc, 0]), lw=1.5, c='dimgray', ls='--')
    aoa(ax, O, np.array([horiz*sc,0]), road_end, r=0.5, col='crimson', lbl='8°')
    ml(ax, O, road_end, '200m', k=0.27, c='royalblue')
    ml(ax, road_end, np.array([horiz*sc,0]), 'h=?', c='red')
    al(ax, [O, road_end, np.array([horiz*sc,0])]); sv(fig, pr+"08.png")

    # 09: Ladder 5m, reaches h=4m → angle and distance from wall
    fig, ax = nax()
    d = np.sqrt(25-16)
    ladder_scene(ax, 5, d, 4, angle_label='?°', q='ang')
    ml(ax, np.array([0,0]), np.array([0,4]), '4m')
    sv(fig, pr+"09.png")

    # 10: Building shadow, sun=35°, shadow=42m → height
    fig, ax = nax()
    h = 42*np.tan(np.radians(35))
    pole_shadow(ax, h, 42, sun_angle='35°', q='h')
    sv(fig, pr+"10.png")

    # 11: Ramp standard, max slope=5°, max height=0.75m
    fig, ax = nax()
    ramp_len = 0.75 / np.sin(np.radians(5))
    sc = s4(ramp_len, 0.75)
    O = np.array([0,0]); top = np.array([0, 0.75*sc]); end = np.array([ramp_len*sc, 0])
    ln(ax, O, end, lw=3, c='saddlebrown')
    ln(ax, end, top, lw=2.5, c='royalblue')
    ln(ax, O, top, lw=1.5, c='dimgray', ls='--')
    rm(ax, O, top, end)
    aoa(ax, end, O, top, r=0.5, col='crimson', lbl='5°')
    ml(ax, O, top, '0.75m')
    # Place ramp label near hypotenuse midpoint, clearly above the base
    mid = (end + top) / 2
    ax.text(mid[0] + 0.15, mid[1] + 0.25, 'ramp=?', fontsize=11,
            ha='center', va='center', color='red')
    al(ax, [O, top, end]); sv(fig, pr+"11.png")

    # 12: TV 16:9, diagonal=55" → width and height
    fig, ax = nax()
    k = 55 / np.sqrt(16**2 + 9**2)
    w, h = 16*k, 9*k
    sc = s4(w, h)
    A, B, C, D_ = (np.array([0,0]), np.array([w*sc,0]),
                   np.array([w*sc,h*sc]), np.array([0,h*sc]))
    pg(ax, [A,B,C,D_])
    ln(ax, A, C, lw=2, c='royalblue', ls='--')
    ml(ax, A, C, '55"', k=0.28, c='royalblue')
    ml(ax, A, B, f'16k=?', s=-1, c='red'); ml(ax, A, D_, f'9k=?', c='red')
    aoa(ax, A, B, C, r=0.4, col='crimson', lbl='?°')
    al(ax, [A,B,C,D_]); sv(fig, pr+"12.png")

    # 13: Sail isosceles, base=4m, apex=50° → leg and area
    fig, ax = nax()
    base_angle = (180-50)/2; leg = (4/2)/np.cos(np.radians(base_angle))
    h = (4/2)*np.tan(np.radians(base_angle))
    sc = s4(2, h)
    A = np.array([0,h*sc]); B = np.array([-2*sc,0]); C = np.array([2*sc,0])
    pg(ax, [A,B,C])
    vl(ax, A, 'A', [B,C]); vl(ax, B, 'B', [A,C]); vl(ax, C, 'C', [A,B])
    aoa(ax, A, B, C, r=0.4, col='royalblue', lbl='50°')
    ml(ax, B, C, 'base=4m', s=-1); ml(ax, A, B, 'leg=?', c='red')
    al(ax, [A,B,C]); sv(fig, pr+"13.png")

    # 14: Stairs h_diff=3m, rise=17cm, angle=34°
    fig, ax = nax()
    sc = s4(5, 3)
    O = np.array([0,0]); top = np.array([0,3*sc]); base = np.array([4.45*sc,0])
    ln(ax, O, base, lw=3, c='saddlebrown')
    ln(ax, base, top, lw=2.5, c='royalblue', ls='--')
    ln(ax, O, top, lw=2, c='dimgray', ls='--')
    rm(ax, O, top, base)
    aoa(ax, O, base, top, r=0.5, col='crimson', lbl='34°')
    ml(ax, O, top, '3m'); ml(ax, base, top, 'staircase', k=0.3, c='royalblue')
    ax.text(2.2*sc, 1.5*sc, '17cm per step', fontsize=9, ha='center', color='darkgreen')
    al(ax, [O, top, base]); sv(fig, pr+"14.png")

    # 15: Cliff 80m, depression angle=12° from horizontal → horizontal distance
    fig, ax = nax()
    horiz = 80/np.tan(np.radians(12))
    sc = s4(horiz, 80)
    O = np.array([0,0]); cliff = np.array([0,80*sc]); ship = np.array([horiz*sc,0])
    ln(ax, O, cliff, lw=3, c='gray')
    ln(ax, O, ship, lw=2, c='dimgray')
    ln(ax, cliff, ship, lw=2, c='royalblue', ls='--')
    # Horizontal reference at eye level — depression is measured from this, not from vertical
    horiz_ref = cliff + np.array([1.8, 0])
    ln(ax, cliff, horiz_ref, lw=1.2, c='gray', ls=':')
    rm(ax, O, cliff, ship)
    aoa(ax, cliff, horiz_ref, ship, r=0.55, col='crimson', lbl='12°')
    ml(ax, O, cliff, '80m'); ml(ax, O, ship, 'd=?', s=-1, c='red')
    hx = horiz*sc
    hull = np.array([[hx-0.22,0],[hx+0.22,0],[hx+0.12,-0.14],[hx-0.12,-0.14]])
    ax.fill(hull[:,0], hull[:,1], color='saddlebrown')
    ln(ax, np.array([hx,0]), np.array([hx,0.35]), lw=1.5, c='dimgray')
    al(ax, [O, cliff, ship, horiz_ref]); sv(fig, pr+"15.png")

    # 16: Two buildings, tall=48m, elevation angle=20° from horizontal, horiz dist=60m
    fig, ax = nax()
    diff_h = 60*np.tan(np.radians(20))
    short_h = 48 - diff_h
    sc = s4(60, 48)
    B1_top = np.array([0,48*sc]); B1_bot = np.array([0,0])
    B2_bot = np.array([60*sc,0]); B2_top = np.array([60*sc,short_h*sc])
    # Point on tall building at the height of the short building (horizontal sight line)
    meet = np.array([0.0, short_h*sc])
    ln(ax, B1_bot, B1_top, lw=3, c='steelblue')
    ln(ax, B2_bot, B2_top, lw=3, c='saddlebrown')
    ln(ax, B1_bot, B2_bot, lw=2, c='dimgray')
    ln(ax, B2_top, meet, lw=1.2, c='gray', ls=':')  # horizontal from short roof
    ln(ax, B2_top, B1_top, lw=1.5, c='crimson', ls='--')
    rm(ax, B1_bot, B1_top, B2_bot)
    aoa(ax, B2_top, meet, B1_top, r=0.5, col='crimson', lbl='20°')
    ml(ax, B1_bot, B1_top, '48m'); ml(ax, B1_bot, B2_bot, '60m', s=-1)
    ml(ax, B2_bot, B2_top, 'h=?', c='red')
    al(ax, [B1_bot,B1_top,B2_bot,B2_top,meet]); sv(fig, pr+"16.png")

    # 17: Slide, bottom angle=28°, height=2.4m
    fig, ax = nax()
    slide_len = 2.4/np.sin(np.radians(28)); horiz = 2.4/np.tan(np.radians(28))
    sc = s4(horiz, 2.4)
    O = np.array([0,0]); top = np.array([0, 2.4*sc]); base = np.array([horiz*sc, 0])
    ln(ax, O, base, lw=3, c='saddlebrown')
    ln(ax, base, top, lw=2.5, c='royalblue')
    ln(ax, O, top, lw=2, c='dimgray', ls='--')
    rm(ax, O, top, base)
    aoa(ax, base, O, top, r=0.5, col='crimson', lbl='28°')
    ml(ax, O, top, '2.4m'); ml(ax, base, top, 'slide=?', k=0.28, c='red')
    al(ax, [O, top, base]); sv(fig, pr+"17.png")

    # 18: Security bar, length=3.5m, horizontal=1.8m → angle
    fig, ax = nax()
    h = np.sqrt(3.5**2 - 1.8**2)  # ≈3.0m
    sc = s4(1.8, h)
    O = np.array([0,0]); top = np.array([0, h*sc]); gnd = np.array([1.8*sc, 0])
    ln(ax, O, top, lw=3, c='dimgray')
    ln(ax, O, gnd, lw=2, c='dimgray')
    ln(ax, top, gnd, lw=2.5, c='royalblue')
    rm(ax, O, top, gnd)
    aoa(ax, gnd, O, top, r=0.5, col='crimson', lbl='?°')
    ml(ax, O, gnd, '1.8m', s=-1); ml(ax, top, gnd, '3.5m', k=0.28, c='royalblue')
    ml(ax, O, top, 'h=?', c='red')
    al(ax, [O, top, gnd]); sv(fig, pr+"18.png")

    # 19: Bridge, horizontal=18m, height diff=4.5m → angle and length
    fig, ax = nax()
    bridge_len = np.sqrt(18**2 + 4.5**2)
    sc = s4(18, 4.5)
    O = np.array([0,0]); far = np.array([18*sc, 4.5*sc])
    ln(ax, O, np.array([18*sc, 0]), lw=3, c='saddlebrown')
    ln(ax, np.array([18*sc, 0]), far, lw=2, c='dimgray')
    ln(ax, O, far, lw=2.5, c='royalblue')
    rm(ax, O, np.array([18*sc, 0]), far)
    aoa(ax, O, np.array([18*sc,0]), far, r=0.5, col='crimson', lbl='?°')
    ml(ax, O, np.array([18*sc,0]), '18m', s=-1); ml(ax, np.array([18*sc,0]), far, '4.5m')
    ml(ax, O, far, 'bridge=?', k=0.28, c='red')
    al(ax, [O, far, np.array([18*sc,0])]); sv(fig, pr+"19.png")

    # 20: Sports field rectangle diagonal=52m, angle=38°
    fig, ax = nax()
    w = 52*np.cos(np.radians(38)); h = 52*np.sin(np.radians(38))
    sc = s4(w, h)
    A,B,C,D_ = (np.array([0,0]), np.array([w*sc,0]),
                 np.array([w*sc,h*sc]), np.array([0,h*sc]))
    pg(ax, [A,B,C,D_])
    ln(ax, A, C, lw=2, c='royalblue', ls='--')
    aoa(ax, A, B, C, r=0.4, col='crimson', lbl='38°')
    ml(ax, A, C, '52m', k=0.28, c='royalblue')
    ml(ax, A, B, 'length=?', s=-1, c='red'); ml(ax, A, D_, 'width=?', c='red')
    al(ax, [A,B,C,D_]); sv(fig, pr+"20.png")

    print("  \u2713\u2713 6.1 complete (20 images)")

# ══════════════════════════════════════════════════════
#  6.2 – FULL MAHAT QUESTIONS (MIXED)
# ══════════════════════════════════════════════════════
def ch62():
    pr = "10_6.2_ex"

    # 01: Right triangle ABC, C=90°, AB=20, angle A=32°
    # Adjacent to A is AC=20*cos32°, opposite is BC=20*sin32°
    fig, ax = nax()
    sc = s4(20*np.sin(np.radians(32)), 20*np.cos(np.radians(32)))
    C = np.array([0.0, 0.0])
    B = np.array([20*np.sin(np.radians(32))*sc, 0.0])
    A = np.array([0.0, 20*np.cos(np.radians(32))*sc])
    pg(ax, [A,B,C]); rm(ax, C, A, B)
    vl(ax, A, 'A', [B,C]); vl(ax, B, 'B', [A,C]); vl(ax, C, 'C', [A,B])
    aoa(ax, A, B, C, r=0.35, col='royalblue', lbl='32°')
    ml(ax, A, B, 'AB=20'); ml(ax, C, B, 'BC=?', s=-1, c='red')
    ml(ax, A, C, 'AC=?', c='red')
    al(ax, [A,B,C]); sv(fig, pr+"01.png")

    # 02: Rectangle ABCD, AB=9, BC=12 → diagonal, angle, perimeter
    fig, ax = nax()
    sc = s4(9, 12)
    A,B,C,D_ = (np.array([0.0, 0.0]), np.array([9*sc, 0.0]),
                 np.array([9*sc, 12*sc]), np.array([0.0, 12*sc]))
    pg(ax, [A,B,C,D_]); ln(ax, A, C, lw=2, c='royalblue', ls='--')
    rm(ax, A, B, D_)
    vl(ax, A,'A',[B,D_]); vl(ax,B,'B',[A,C]); vl(ax,C,'C',[B,D_]); vl(ax,D_,'D',[A,C])
    ml(ax, A, B, 'AB=9', s=-1); ml(ax, B, C, 'BC=12')
    ml(ax, A, C, 'AC=?', k=0.28, c='red')
    aoa(ax, A, B, C, r=0.4, col='crimson', lbl='?°')
    al(ax, [A,B,C,D_]); sv(fig, pr+"02.png")

    # 03: Rhombus ABCD, side=8, acute angle=50°
    fig, ax = nax()
    d1 = 2*8*np.cos(np.radians(25)); d2 = 2*8*np.sin(np.radians(25))
    sc = s4(d1/2, d2/2)
    A = np.array([0,d2/2*sc]); B = np.array([d1/2*sc,0])
    C = np.array([0,-d2/2*sc]); D_ = np.array([-d1/2*sc,0])
    O = np.array([0,0])
    pg(ax,[A,B,C,D_])
    ln(ax,A,C,lw=1.5,c='royalblue',ls='--'); ln(ax,B,D_,lw=1.5,c='crimson',ls='--')
    rm(ax,O,A,B)
    vl(ax,A,'A',[B,D_]); vl(ax,B,'B',[A,C]); vl(ax,C,'C',[B,D_]); vl(ax,D_,'D',[A,C])
    aoa(ax,D_,A,B,r=0.35,col='royalblue',lbl='50°')
    ml(ax,A,B,'8'); ml(ax,A,C,'d1=?',c='red'); ml(ax,B,D_,'d2=?',c='red',s=-1)
    al(ax,[A,B,C,D_]); sv(fig,pr+"03.png")

    # 04: Isosceles trapezoid, long=32, short=18, angle=55°
    fig, ax = nax()
    ex = 7; h = ex*np.tan(np.radians(55))
    sc = s4(32, h)
    off = (32-18)/2
    B = np.array([0,0]); C_ = np.array([32*sc,0])
    A = np.array([off*sc,h*sc]); D = np.array([(off+18)*sc,h*sc])
    E = np.array([off*sc,0]); F = np.array([(off+18)*sc,0])
    pg(ax,[A,B,C_,D])
    ln(ax,A,E,lw=1.5,c='royalblue',ls='--'); ln(ax,D,F,lw=1.5,c='royalblue',ls='--')
    rm(ax,E,A,B); rm(ax,F,D,C_)
    vl(ax,A,'A',[B,D]); vl(ax,B,'B',[A,C_]); vl(ax,C_,'C',[B,D]); vl(ax,D,'D',[A,C_])
    ml(ax,B,C_,'32',s=-1); ml(ax,A,D,'18'); ml(ax,A,B,'leg=?',c='red')
    ml(ax,A,E,'h=?',s=-1,c='red')
    aoa(ax,B,A,C_,r=0.4,col='crimson',lbl='55°')
    al(ax,[A,B,C_,D,E,F]); sv(fig,pr+"04.png")

    # 05: Ladder 10m, height=8m → angle and distance from wall
    fig, ax = nax()
    d = np.sqrt(100-64)  # = 6
    O = np.array([0,0]); W = np.array([0,8]); G = np.array([6,0])
    ln(ax,np.array([-0.1,0]),np.array([-0.1,8.3]),lw=4,c='dimgray')
    ln(ax,np.array([-0.3,0]),np.array([6.3,0]),lw=3,c='saddlebrown')
    ln(ax,G,W,lw=2.5,c='royalblue')
    rm(ax,O,W,G)
    aoa(ax,G,O,W,r=0.5,col='crimson',lbl='?°')
    ml(ax,O,W,'8m'); ml(ax,G,W,'10m',k=0.28,c='royalblue')
    ml(ax,O,G,'d=?',s=-1,c='red')
    al(ax,[O,W,G,np.array([-0.3,0])]); sv(fig,pr+"05.png")

    # 06: Isosceles triangle ABC, AB=AC=15, BC=18
    fig, ax = nax()
    sc = s4(9, 12)
    A = np.array([0,12*sc]); B = np.array([-9*sc,0]); C = np.array([9*sc,0])
    D = np.array([0,0])
    pg(ax,[A,B,C]); ln(ax,A,D,lw=1.5,c='royalblue',ls='--'); rm(ax,D,A,B)
    vl(ax,A,'A',[B,C]); vl(ax,B,'B',[A,C]); vl(ax,C,'C',[A,B]); vl(ax,D,'D',[A,B])
    aoa(ax,B,A,C,r=0.4,col='royalblue',lbl='?°')
    ml(ax,A,B,'15'); ml(ax,B,C,'18',s=-1); ml(ax,A,D,'h=?',c='red')
    al(ax,[A,B,C,D]); sv(fig,pr+"06.png")

    # 07: Rectangle diagonal=26, angle BAC=42°
    fig, ax = nax()
    w = 26*np.cos(np.radians(42)); h = 26*np.sin(np.radians(42))
    sc = s4(w,h)
    A,B,C,D_ = (np.array([0,0]),np.array([w*sc,0]),
                 np.array([w*sc,h*sc]),np.array([0,h*sc]))
    M = (A+C)/2
    pg(ax,[A,B,C,D_])
    ln(ax,A,C,lw=2,c='royalblue',ls='--'); ln(ax,B,D_,lw=1.5,c='dimgray',ls=':')
    ax.plot(*M,'ko',ms=5)
    vl(ax,A,'A',[B,D_]); vl(ax,B,'B',[A,C]); vl(ax,C,'C',[B,D_]); vl(ax,D_,'D',[A,C])
    vl(ax,M,'M',[A,C])
    aoa(ax,A,B,C,r=0.4,col='crimson',lbl='42°')
    ml(ax,A,C,'26',k=0.28,c='royalblue'); ml(ax,A,B,'AB=?',s=-1,c='red')
    al(ax,[A,B,C,D_]); sv(fig,pr+"07.png")

    # 08: Isosceles trapezoid, area=220, h=11, long=26 → short=14
    fig, ax = nax()
    sc = s4(26, 11)
    off = 6
    B=np.array([0,0]); C_=np.array([26*sc,0])
    A=np.array([off*sc,11*sc]); D=np.array([(off+14)*sc,11*sc])
    E=np.array([off*sc,0]); F=np.array([(off+14)*sc,0])
    pg(ax,[A,B,C_,D])
    ln(ax,A,E,lw=1.5,c='royalblue',ls='--'); ln(ax,D,F,lw=1.5,c='royalblue',ls='--')
    rm(ax,E,A,B); rm(ax,F,D,C_)
    vl(ax,A,'A',[B,D]); vl(ax,B,'B',[A,C_]); vl(ax,C_,'C',[B,D]); vl(ax,D,'D',[A,C_])
    ml(ax,B,C_,'26',s=-1); ml(ax,A,D,'?'); ml(ax,A,E,'h=11',s=-1,c='royalblue')
    ml(ax,A,B,'leg=?',c='red')
    ax.text(13*sc,5.5*sc,'Area=220',fontsize=10,ha='center',color='royalblue')
    al(ax,[A,B,C_,D,E,F]); sv(fig,pr+"08.png")

    # 09: Right triangle ABC, C=90°, AB=17, BC=8; D on AB with CD⊥AB
    fig, ax = nax()
    sc = s4(8, 15)
    C = np.array([0.0, 0.0]); B = np.array([8*sc, 0.0]); A = np.array([0.0, 15*sc])
    AB = B - A
    t = np.dot(C - A, AB) / np.dot(AB, AB)
    D = A + t * AB
    pg(ax, [A, B, C]); rm(ax, C, A, B)
    ln(ax, C, D, lw=1.5, c='royalblue', ls='--'); rm(ax, D, C, A)
    vl(ax, A, 'A', [B, C]); vl(ax, B, 'B', [A, C]); vl(ax, C, 'C', [A, B])
    vl(ax, D, 'D', [A, B, C])
    ml(ax, A, B, 'AB=17'); ml(ax, C, B, 'BC=8', s=-1); ml(ax, A, C, 'AC=?', c='red')
    ml(ax, C, D, 'CD=?', k=0.28, c='red')
    al(ax, [A, B, C, D]); sv(fig, pr+"09.png")

    # 10: Rectangle ABCD, angle ABD=55°, BD=18
    fig, ax = nax()
    w=18*np.cos(np.radians(55)); h=18*np.sin(np.radians(55))
    sc=s4(w,h)
    A,B,C,D_=(np.array([0,0]),np.array([w*sc,0]),
               np.array([w*sc,h*sc]),np.array([0,h*sc]))
    M=(A+C)/2
    pg(ax,[A,B,C,D_])
    ln(ax,B,D_,lw=2,c='royalblue',ls='--'); ln(ax,A,C,lw=1.5,c='dimgray',ls=':')
    ax.plot(*M,'ko',ms=5)
    rm(ax,A,B,D_)
    vl(ax,A,'A',[B,D_]); vl(ax,B,'B',[A,C]); vl(ax,C,'C',[B,D_]); vl(ax,D_,'D',[A,C])
    vl(ax,M,'M',[A,C])
    aoa(ax,A,B,D_,r=0.4,col='royalblue',lbl='55°')
    ml(ax,B,D_,'BD=18',k=0.28,c='royalblue')
    ml(ax,A,B,'AB=?',s=-1,c='red'); ml(ax,A,D_,'AD=?',c='red')
    al(ax,[A,B,C,D_]); sv(fig,pr+"10.png")

    # 11: Rhombus ABCD, AB=13, diagonal AC=24
    fig, ax = nax()
    half_AC=12; half_BD=5
    sc=s4(half_AC,half_BD)
    A=np.array([0,half_BD*sc]); B=np.array([half_AC*sc,0])
    C=np.array([0,-half_BD*sc]); D_=np.array([-half_AC*sc,0])
    O=np.array([0,0])
    pg(ax,[A,B,C,D_])
    ln(ax,A,C,lw=2,c='royalblue',ls='--'); ln(ax,B,D_,lw=2,c='crimson',ls='--')
    rm(ax,O,A,B)
    vl(ax,A,'A',[B,D_]); vl(ax,B,'B',[A,C]); vl(ax,C,'C',[B,D_]); vl(ax,D_,'D',[A,C])
    ml(ax,A,B,'AB=13'); ml(ax,A,C,'AC=24',c='royalblue'); ml(ax,B,D_,'BD=?',c='red',s=-1)
    al(ax,[A,B,C,D_]); sv(fig,pr+"11.png")

    # 12: Isosceles trap ABCD, AD=10, AB=13, angle ABC=67.4°
    fig, ax = nax()
    h=13*np.sin(np.radians(67.4)); extra=13*np.cos(np.radians(67.4))
    BC_len=10+2*extra
    sc=s4(BC_len,h)
    off=extra
    B=np.array([0,0]); C_=np.array([BC_len*sc,0])
    A=np.array([off*sc,h*sc]); D=np.array([(off+10)*sc,h*sc])
    E=np.array([off*sc,0]); F=np.array([(off+10)*sc,0])
    pg(ax,[A,B,C_,D])
    ln(ax,A,E,lw=1.5,c='royalblue',ls='--'); ln(ax,D,F,lw=1.5,c='royalblue',ls='--')
    rm(ax,E,A,B); rm(ax,F,D,C_)
    vl(ax,A,'A',[B,D]); vl(ax,B,'B',[A,C_]); vl(ax,C_,'C',[B,D]); vl(ax,D,'D',[A,C_])
    aoa(ax,B,A,C_,r=0.4,col='royalblue',lbl='67.4°')
    ml(ax,A,D,'AD=10'); ml(ax,A,B,'AB=13',s=-1); ml(ax,A,E,'h=?',c='red')
    ml(ax,B,C_,'BC=?',s=-1,c='red')
    al(ax,[A,B,C_,D,E,F]); sv(fig,pr+"12.png")

    # 13: Building shadow, sun=28°, shadow=63.2m, tree h=8m
    fig, ax = nax()
    h=63.2*np.tan(np.radians(28))
    sc=s4(63.2,h)
    B_bot=np.array([0,0]); B_top=np.array([0,h*sc]); shadow_tip=np.array([63.2*sc,0])
    tree_base=np.array([63.2*sc+1,0]); tree_top=np.array([63.2*sc+1,8*sc])
    ln(ax,B_bot,B_top,lw=3,c='steelblue'); ln(ax,B_bot,shadow_tip,lw=2,c='dimgray')
    ln(ax,B_top,shadow_tip,lw=1.5,c='orange',ls='--')
    ln(ax,tree_base,tree_top,lw=2,c='darkgreen')
    rm(ax,B_bot,B_top,shadow_tip)
    aoa(ax,shadow_tip,B_bot,B_top,r=0.4,col='orange',lbl='28°')
    ml(ax,B_bot,B_top,'h=?',c='red'); ml(ax,B_bot,shadow_tip,'63.2m',s=-1)
    ml(ax,tree_base,tree_top,'8m',c='darkgreen')
    al(ax,[B_bot,B_top,shadow_tip,tree_top]); sv(fig,pr+"13.png")

    # 14: Isosceles ABC, AB=AC=25, apex angle=50°
    fig, ax = nax()
    hb = 25*np.sin(np.radians(25)); h = 25*np.cos(np.radians(25))
    sc = s4(hb, h)
    A = np.array([0.0, h*sc]); B = np.array([-hb*sc, 0.0]); C = np.array([hb*sc, 0.0])
    D = np.array([0.0, 0.0])
    # E on AB such that DE⊥AB
    AB = B - A
    t = np.dot(D - A, AB) / np.dot(AB, AB)
    E = A + t * AB
    pg(ax, [A, B, C]); ln(ax, A, D, lw=1.5, c='royalblue', ls='--'); rm(ax, D, A, B)
    ln(ax, D, E, lw=1.5, c='crimson', ls='--'); rm(ax, E, D, A)
    vl(ax, A, 'A', [B, C]); vl(ax, B, 'B', [A, C]); vl(ax, C, 'C', [A, B])
    vl(ax, D, 'D', [A, B]); vl(ax, E, 'E', [A, B, D])
    aoa(ax, A, B, C, r=0.35, col='royalblue', lbl='50°')
    ml(ax, A, B, '25'); ml(ax, B, C, 'BC=?', s=-1, c='red'); ml(ax, A, D, 'h=?', c='red')
    ml(ax, D, E, 'DE=?', k=0.25, c='crimson')
    al(ax, [A, B, C, D, E], pad=0.7); sv(fig, pr+"14.png")

    # 15: Rectangle ABCD, diagonal AC=20, angle BAC=36°; distance A→CD
    fig, ax = nax()
    w = 20*np.cos(np.radians(36)); h = 20*np.sin(np.radians(36))
    sc = s4(w, h)
    A,B,C,D_ = (np.array([0.0, 0.0]), np.array([w*sc, 0.0]),
                 np.array([w*sc, h*sc]), np.array([0.0, h*sc]))
    pg(ax, [A, B, C, D_])
    ln(ax, A, C, lw=2, c='royalblue', ls='--')
    ln(ax, A, D_, lw=2, c='crimson', ls='--')  # distance A to CD equals AD
    vl(ax, A, 'A', [B, D_]); vl(ax, B, 'B', [A, C]); vl(ax, C, 'C', [B, D_]); vl(ax, D_, 'D', [A, C])
    aoa(ax, A, B, C, r=0.4, col='crimson', lbl='36°')
    ml(ax, A, C, 'AC=20', k=0.28, c='royalblue')
    ml(ax, A, B, 'AB=?', s=-1, c='red'); ml(ax, A, D_, 'AD=?', c='red')
    al(ax, [A, B, C, D_]); sv(fig, pr+"15.png")

    # 16: General trapezoid ABCD, AB=20, AD=15, BC=25, angle ADC=60°
    fig, ax = nax()
    h=15*np.sin(np.radians(60)); DE=15*np.cos(np.radians(60))
    FC=np.sqrt(25**2-h**2) if 25**2>h**2 else 20
    DC_len=DE+20+FC
    sc=s4(DC_len,h)
    D=np.array([0,0]); C_=np.array([DC_len*sc,0])
    A=np.array([DE*sc,h*sc]); B=np.array([(DE+20)*sc,h*sc])
    E=np.array([DE*sc,0]); F=np.array([(DE+20)*sc,0])
    pg(ax,[A,B,C_,D])
    ln(ax,A,E,lw=1.5,c='royalblue',ls='--'); ln(ax,B,F,lw=1.5,c='crimson',ls='--')
    rm(ax,E,A,D); rm(ax,F,B,C_)
    vl(ax,A,'A',[B,D]); vl(ax,B,'B',[A,C_]); vl(ax,C_,'C',[B,D]); vl(ax,D,'D',[A,C_])
    aoa(ax,D,A,C_,r=0.45,col='royalblue',lbl=None)
    ax.text(D[0]+0.55, D[1]+0.35, '60°', fontsize=13, ha='center', va='center',
            color='royalblue', fontweight='bold')
    ml(ax,A,B,'AB=20'); ml(ax,A,D,'AD=15'); ml(ax,B,C_,'BC=25',s=-1)
    ml(ax,A,E,'h=?',c='red')
    al(ax,[A,B,C_,D,E,F]); sv(fig,pr+"16.png")

    # 17: Slide, angle=28°, height=2.4m (same as 6.1 ex17)
    fig, ax = nax()
    slide=2.4/np.sin(np.radians(28)); horiz=2.4/np.tan(np.radians(28))
    sc=s4(horiz,2.4)
    O=np.array([0,0]); top=np.array([0,2.4*sc]); base=np.array([horiz*sc,0])
    ln(ax,O,base,lw=3,c='saddlebrown'); ln(ax,base,top,lw=2.5,c='royalblue')
    ln(ax,O,top,lw=2,c='dimgray',ls='--'); rm(ax,O,top,base)
    aoa(ax,base,O,top,r=0.5,col='crimson',lbl='28°')
    ml(ax,O,top,'2.4m'); ml(ax,base,top,'slide=?',k=0.28,c='red')
    ml(ax,O,base,'horiz=?',s=-1,c='red')
    al(ax,[O,top,base]); sv(fig,pr+"17.png")

    # 18: Isosceles trap ABCD, AD=12, BC=48, angle DCB=40° (same as 5.3 ex17)
    fig, ax = nax()
    h_=18*np.tan(np.radians(40))
    sc=s4(48,h_)
    off=(48-12)/2
    B=np.array([0,0]); C_=np.array([48*sc,0])
    A=np.array([off*sc,h_*sc]); D=np.array([(off+12)*sc,h_*sc])
    E=np.array([off*sc,0]); F=np.array([(off+12)*sc,0])
    pg(ax,[A,B,C_,D])
    ln(ax,A,E,lw=1.5,c='royalblue',ls='--'); ln(ax,D,F,lw=1.5,c='royalblue',ls='--')
    rm(ax,E,A,B); rm(ax,F,D,C_)
    vl(ax,A,'A',[B,D]); vl(ax,B,'B',[A,C_]); vl(ax,C_,'C',[B,D]); vl(ax,D,'D',[A,C_])
    vl(ax,E,'G',[A,B]); vl(ax,F,'H',[D,C_])
    aoa(ax,C_,D,B,r=0.4,col='royalblue',lbl='40°')
    ml(ax,A,D,'AD=12'); ml(ax,B,C_,'BC=48',s=-1); ml(ax,A,E,'h=?',c='red')
    al(ax,[A,B,C_,D,E,F]); sv(fig,pr+"18.png")

    # 19: Sail = two triangles, CD=4.7, angle ACD=55°, angle ABD=38°
    fig, ax = nax()
    AD=4.7*np.tan(np.radians(55)); CD=4.7; BD=AD/np.tan(np.radians(38))
    BC=BD+CD
    sc=s4(BC,AD)
    D=np.array([0,0]); C_=np.array([CD*sc,0]); B=np.array([-BD*sc,0])
    A=np.array([0,AD*sc])
    pg(ax,[A,B,C_])
    ln(ax,A,D,lw=1.5,c='royalblue',ls='--')
    rm(ax,D,A,B); rm(ax,D,A,C_)
    vl(ax,A,'A',[B,C_]); vl(ax,B,'B',[A,C_])
    vl(ax,C_,'C',[A,B]); vl(ax,D,'D',[A,B])
    aoa(ax,C_,A,B,r=0.35,col='royalblue',lbl='55°')
    aoa(ax,B,A,C_,r=0.35,col='crimson',lbl='38°')
    ml(ax,D,C_,'CD=4.7',s=-1); ml(ax,A,D,'AD=?',c='red')
    al(ax,[A,B,C_,D]); sv(fig,pr+"19.png")

    # 20: Rhombus ABCD, AB=10.3, angle ABC=128°; rectangle CEDF via heights to line AB
    fig, ax = nax()
    a = 10.3
    ang = 52  # direction of sides AD, BC from AB
    sc = s4(a * (1 + np.cos(np.radians(ang))), a * np.sin(np.radians(ang)))
    A = np.array([0.0, 0.0])
    B = np.array([a*sc, 0.0])
    D_ = np.array([a*np.cos(np.radians(ang))*sc, a*np.sin(np.radians(ang))*sc])
    C = B + (D_ - A)
    F = np.array([D_[0], 0.0])
    E = np.array([C[0], 0.0])
    # line AB extended
    ln(ax, np.array([A[0]-0.4, 0.0]), np.array([E[0]+0.4, 0.0]), lw=1.2, c='dimgray', ls=':')
    pg(ax, [A, B, C, D_])
    # rectangle CEDF
    pg(ax, [C, E, F, D_], lw=1.8, c='seagreen', ls='-')
    ln(ax, D_, F, lw=1.5, c='seagreen', ls='--')
    ln(ax, C, E, lw=1.5, c='seagreen', ls='--')
    rm(ax, F, D_, E); rm(ax, E, C, F)
    ln(ax, A, C, lw=1.5, c='royalblue', ls='--')
    ln(ax, B, D_, lw=1.5, c='crimson', ls='--')
    aoa(ax, B, A, C, r=0.40, col='royalblue', lbl=None)
    # label near B (not along bisector — that lands on diagonal intersection)
    ax.text(B[0] - 0.15, B[1] + 0.55, '128°', fontsize=12,
            ha='center', va='center', color='royalblue', fontweight='bold')
    vl(ax, A, 'A', [B, D_]); vl(ax, B, 'B', [A, C])
    vl(ax, C, 'C', [B, D_, E]); vl(ax, D_, 'D', [A, C, F])
    vl(ax, E, 'E', [C, B]); vl(ax, F, 'F', [D_, A])
    ml(ax, A, B, 'AB=10.3', s=-1)
    ml(ax, A, C, 'AC=?', c='royalblue', k=0.3)
    ml(ax, B, D_, 'BD=?', c='crimson', k=0.28)
    ax.text((F[0]+E[0])/2, (D_[1])/2, 'מלבן CEDF', fontsize=9, ha='center',
            va='center', color='seagreen')
    al(ax, [A, B, C, D_, E, F], pad=0.85); sv(fig, pr+"20.png")

    print("  \u2713\u2713 6.2 complete (20 images)")

# ══════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════
if __name__ == '__main__':
    print("\n=== Generating Chapter 10 Trigonometry Diagrams ===\n")
    print(">> Subtopic 1.2"); ch12()
    print(">> Subtopic 1.3"); ch13()
    print(">> Subtopic 4.2"); ch42()
    print(">> Subtopic 5.1"); ch51()
    print(">> Subtopic 5.2"); ch52()
    print(">> Subtopic 5.3"); ch53()
    print(">> Subtopic 6.1"); ch61()
    print(">> Subtopic 6.2"); ch62()
    print(f"\n=== Done! All images saved to:\n    {IMG}\n")
