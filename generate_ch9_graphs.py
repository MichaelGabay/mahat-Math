#!/usr/bin/env python3
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.patches import Polygon, Rectangle


ROOT = Path(__file__).resolve().parent
CHAPTER_DIR = ROOT / "9 - שאלות מילוליות"
IMAGES_DIR = CHAPTER_DIR / "images"

MUST_SUBTOPICS = {"5.1", "5.2", "5.4", "7.3"}
SHOULD_SUBTOPICS = {"2.2", "5.3", "6.2", "7.2"}
HEBREW_RE = re.compile(r"[\u0590-\u05FF]")


def rtl_text(value):
    # matplotlib in this environment already renders Hebrew RTL correctly
    # on its own (built-in text shaping). Running get_display()/python-bidi
    # on top of that double-flips the string and garbles it
    # (e.g. "גינה" -> "הניג", "ס"מ" -> "מ"ס"). Keep this as an identity
    # function - see quality-check prompt's critical warning about this
    # exact bug in generate_ch6_graphs.py.
    return value


_orig_set_title = Axes.set_title
_orig_set_xlabel = Axes.set_xlabel
_orig_set_ylabel = Axes.set_ylabel
_orig_annotate = Axes.annotate
_orig_text = Axes.text


def _patched_set_title(self, label, *args, **kwargs):
    return _orig_set_title(self, rtl_text(label), *args, **kwargs)


def _patched_set_xlabel(self, xlabel, *args, **kwargs):
    return _orig_set_xlabel(self, rtl_text(xlabel), *args, **kwargs)


def _patched_set_ylabel(self, ylabel, *args, **kwargs):
    return _orig_set_ylabel(self, rtl_text(ylabel), *args, **kwargs)


def _patched_annotate(self, text, *args, **kwargs):
    return _orig_annotate(self, rtl_text(text), *args, **kwargs)


def _patched_text(self, x, y, s, *args, **kwargs):
    return _orig_text(self, x, y, rtl_text(s), *args, **kwargs)


Axes.set_title = _patched_set_title
Axes.set_xlabel = _patched_set_xlabel
Axes.set_ylabel = _patched_set_ylabel
Axes.annotate = _patched_annotate
Axes.text = _patched_text

GEOMETRY_KEYWORDS = [
    "מלבן",
    "ריבוע",
    "משולש",
    "פיתגורס",
    "חצר",
    "מגרש",
    "חדר",
    "גינה",
    "גדר",
    "היקף",
    "שטח",
    "שביל",
    "שוליים",
    "צלע",
    "מסגרת",
    "בד ציור",
    "בריכה",
    "גג",
    "אריח",
]


@dataclass
class Exercise:
    number: int
    start: int
    end: int
    block: str


def parse_subtopic(file_path: Path) -> str:
    return file_path.name.split("_", 1)[0]


def parse_exercises(lines: list[str]) -> list[Exercise]:
    starts: list[tuple[int, int]] = []
    details_start = None
    for idx, line in enumerate(lines):
        if line.strip().startswith("<details>"):
            details_start = idx
            break
    limit = details_start if details_start is not None else len(lines)

    for idx, line in enumerate(lines[:limit]):
        m = re.match(r"^\s*(?:\*\*)?(\d{1,2})\.\**\s", line)
        if m:
            starts.append((idx, int(m.group(1))))

    exercises: list[Exercise] = []
    for i, (start_idx, number) in enumerate(starts):
        next_idx = limit
        if i + 1 < len(starts):
            next_idx = starts[i + 1][0]

        for j in range(start_idx + 1, next_idx):
            stripped = lines[j].strip()
            if stripped.startswith("---") or stripped.startswith("## ") or stripped.startswith("<details>"):
                next_idx = j
                break

        block = "".join(lines[start_idx:next_idx])
        exercises.append(Exercise(number=number, start=start_idx, end=next_idx, block=block))
    return exercises


def is_geometry_heavy(text: str) -> bool:
    text_l = text.lower()
    return any(keyword in text_l for keyword in GEOMETRY_KEYWORDS)


def should_generate(subtopic: str, ex_number: int, block: str) -> bool:
    if subtopic in MUST_SUBTOPICS:
        return 1 <= ex_number <= 20
    if subtopic in SHOULD_SUBTOPICS:
        heavy = is_geometry_heavy(block)
        return heavy and (ex_number >= 10 or "משולש" in block or "פיתגורס" in block)
    return False


def add_labels(ax, points: Iterable[tuple[float, float]], labels: Iterable[str]) -> None:
    for (x, y), lbl in zip(points, labels):
        ax.text(x, y, lbl, fontsize=12, weight="bold", ha="center", va="center")


_DIM_ARROW = dict(arrowstyle="<->", color="#333333", lw=0.9, mutation_scale=9)


def dim_h(ax, x1, x2, y, label, off=-0.7, fs=10):
    ya = y + off
    ax.annotate("", xy=(x1, ya), xytext=(x2, ya), arrowprops=_DIM_ARROW)
    ax.plot([x1, x1], [y, ya], color="#777777", lw=0.6)
    ax.plot([x2, x2], [y, ya], color="#777777", lw=0.6)
    ax.text(
        (x1 + x2) / 2,
        ya + (0.32 if off < 0 else -0.42),
        label,
        ha="center",
        fontsize=fs,
        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.9),
    )


def dim_v(ax, x, y1, y2, label, off=-0.7, fs=10):
    xa = x + off
    ax.annotate("", xy=(xa, y1), xytext=(xa, y2), arrowprops=_DIM_ARROW)
    ax.plot([x, xa], [y1, y1], color="#777777", lw=0.6)
    ax.plot([x, xa], [y2, y2], color="#777777", lw=0.6)
    ax.text(
        xa + (-0.55 if off < 0 else 0.55),
        (y1 + y2) / 2,
        label,
        va="center",
        ha="center",
        fontsize=fs,
        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.9),
    )


def setup_ax_for(w_ext: float, h_ext: float, pad_left=2.6, pad_right=1.0, pad_bottom=2.0, pad_top=1.6):
    xlim = w_ext + pad_left + pad_right
    ylim = h_ext + pad_bottom + pad_top
    base = 0.42
    fig_w = max(4.6, min(8.2, xlim * base))
    fig_h = max(3.2, min(6.8, ylim * base))
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), facecolor="white")
    ax.set_facecolor("white")
    ax.set_xlim(0, xlim)
    ax.set_ylim(0, ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax, pad_left, pad_bottom


def draw_dim_rect(ax, x0, y0, w, h, w_label, h_label, edgecolor="#1f2937", corner_labels=("A", "B", "C", "D")):
    rect = Rectangle((x0, y0), w, h, fill=False, linewidth=2, edgecolor=edgecolor)
    ax.add_patch(rect)
    if corner_labels:
        add_labels(
            ax,
            [(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)],
            corner_labels,
        )
    dim_h(ax, x0, x0 + w, y0, w_label, off=-1.0)
    dim_v(ax, x0, y0, y0 + h, h_label, off=-1.0)


def draw_three_sides_dim(ax, x0, y0, w, h, w_label, h_label, edgecolor="#1f2937", corner_labels=("A", "B", "C", "D")):
    """Rectangle fenced on the long (top) side + both short (vertical) sides;
    the bottom (open) side is drawn dashed, matching draw_three_sides()."""
    ax.plot([x0, x0 + w], [y0 + h, y0 + h], color=edgecolor, linewidth=2.2)
    ax.plot([x0, x0], [y0, y0 + h], color=edgecolor, linewidth=2.2)
    ax.plot([x0 + w, x0 + w], [y0, y0 + h], color=edgecolor, linewidth=2.2)
    ax.plot([x0, x0 + w], [y0, y0], color="#9ca3af", linewidth=1.8, linestyle="--")
    if corner_labels:
        add_labels(
            ax,
            [(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)],
            corner_labels,
        )
    dim_h(ax, x0, x0 + w, y0, w_label, off=-1.0)
    dim_v(ax, x0, y0, y0 + h, h_label, off=-1.0)


def top_caption(ax, xlim, ylim, text, fs=11, color="#111827"):
    if isinstance(text, (list, tuple)):
        for i, line in enumerate(text):
            ax.text(xlim / 2, ylim - 0.55 - i * 0.5, line, ha="center", fontsize=fs, color=color, weight="bold")
    else:
        ax.text(xlim / 2, ylim - 0.55, text, ha="center", fontsize=fs, color=color, weight="bold")


def setup_ax():
    fig, ax = plt.subplots(figsize=(6, 4), facecolor="white")
    ax.set_facecolor("white")
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def draw_rectangle(ax):
    rect = Rectangle((2, 1.5), 8, 5, fill=False, linewidth=2, edgecolor="#1f2937")
    ax.add_patch(rect)
    add_labels(ax, [(2, 1.5), (10, 1.5), (10, 6.5), (2, 6.5)], ["A", "B", "C", "D"])


def draw_square(ax):
    sq = Rectangle((3, 1.5), 5, 5, fill=False, linewidth=2, edgecolor="#1f2937")
    ax.add_patch(sq)
    add_labels(ax, [(3, 1.5), (8, 1.5), (8, 6.5), (3, 6.5)], ["A", "B", "C", "D"])


def draw_three_sides(ax):
    x, y, w, h = 2, 1.5, 8, 5
    ax.plot([x, x + w], [y + h, y + h], color="#1f2937", linewidth=3)
    ax.plot([x, x], [y, y + h], color="#1f2937", linewidth=3)
    ax.plot([x + w, x + w], [y, y + h], color="#1f2937", linewidth=3)
    ax.plot([x, x + w], [y, y], color="#9ca3af", linewidth=2, linestyle="--")
    add_labels(ax, [(x, y), (x + w, y), (x + w, y + h), (x, y + h)], ["A", "B", "C", "D"])


def draw_walkway(ax):
    outer = Rectangle((1.2, 0.8), 9.6, 6.4, fill=False, linewidth=2, edgecolor="#1f2937")
    inner = Rectangle((2.2, 1.8), 7.6, 4.4, fill=False, linewidth=2, edgecolor="#111827")
    frame = Rectangle((1.2, 0.8), 9.6, 6.4, fill=True, facecolor="#dbeafe", alpha=0.45, edgecolor="none")
    hole = Rectangle((2.2, 1.8), 7.6, 4.4, fill=True, facecolor="white", edgecolor="none")
    ax.add_patch(frame)
    ax.add_patch(hole)
    ax.add_patch(outer)
    ax.add_patch(inner)
    add_labels(ax, [(1.2, 0.8), (10.8, 0.8), (10.8, 7.2), (1.2, 7.2)], ["A", "B", "C", "D"])


def draw_inner_house(ax):
    outer = Rectangle((1.0, 0.8), 10.0, 6.4, fill=False, linewidth=2, edgecolor="#1f2937")
    inner = Rectangle((3.0, 2.2), 6.0, 3.6, fill=False, linewidth=2, edgecolor="#0f766e")
    ax.add_patch(outer)
    ax.add_patch(inner)
    ax.text(6, 4, "בית", fontsize=11, color="#0f766e", ha="center")
    add_labels(ax, [(1.0, 0.8), (11.0, 0.8), (11.0, 7.2), (1.0, 7.2)], ["A", "B", "C", "D"])


def draw_right_triangle(ax):
    points = [(2, 1.2), (9, 1.2), (9, 6.2)]
    tri = Polygon(points, closed=True, fill=False, linewidth=2, edgecolor="#1f2937")
    ax.add_patch(tri)
    ax.plot([8.3, 8.3, 9], [1.2, 1.9, 1.9], color="#1f2937", linewidth=1.5)
    add_labels(ax, points, ["A", "B", "C"])


def pick_diagram(text: str) -> str:
    if "משולש" in text or "פיתגורס" in text or "יתר" in text:
        return "triangle"
    if "שביל" in text:
        return "walkway"
    if "שוליים" in text or "בתוך המגרש" in text or "בית מלבני בתוך" in text:
        return "inner_house"
    if (
        "שלושה צדדים" in text
        or "שלוש צלעות" in text
        or "הצלע הארוכה ושתי" in text
    ):
        return "three_sides"
    is_square = ("ריבוע" in text or "מרובע" in text) and not (
        "משוואה ריבועית" in text or "פונקציה ריבועית" in text
    )
    if is_square:
        return "square"
    return "rectangle"


def create_image(out_path: Path, block: str) -> None:
    fig, ax = setup_ax()
    kind = pick_diagram(block)
    if kind == "triangle":
        draw_right_triangle(ax)
    elif kind == "walkway":
        draw_walkway(ax)
    elif kind == "inner_house":
        draw_inner_house(ax)
    elif kind == "three_sides":
        draw_three_sides(ax)
    elif kind == "square":
        draw_square(ax)
    else:
        draw_rectangle(ax)

    fig.savefig(out_path, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def create_image_5_2(out_path: Path, n: int) -> None:
    """Dedicated, per-exercise diagrams for 9/5.2 with real dimension labels."""

    if n == 1:
        w, h = 10, 6
        fig, ax, px, py = setup_ax_for(w, h)
        draw_dim_rect(ax, px, py, w, h, "10 מ'", "6 מ'")
    elif n == 2:
        s = 8
        fig, ax, px, py = setup_ax_for(s, s)
        draw_dim_rect(ax, px, py, s, s, "8 מ'", "8 מ'")
    elif n == 3:
        w, h = 15, 10
        fig, ax, px, py = setup_ax_for(w, h)
        draw_dim_rect(ax, px, py, w, h, "15 מ'", "10 מ'")
    elif n == 4:
        s = 9
        fig, ax, px, py = setup_ax_for(s, s)
        draw_dim_rect(ax, px, py, s, s, "9 מ'", "9 מ'")
    elif n == 5:
        w, h = 12, 5
        fig, ax, px, py = setup_ax_for(w, h)
        draw_dim_rect(ax, px, py, w, h, "12 מ'", "5 מ'")
    elif n == 6:
        w, h = 10, 7
        fig, ax, px, py = setup_ax_for(w, h)
        draw_dim_rect(ax, px, py, w, h, "10 מ'", "7 מ'")
    elif n == 7:
        w, h = 14, 6
        fig, ax, px, py = setup_ax_for(w, h)
        draw_dim_rect(ax, px, py, w, h, "14 מ'", "6 מ'")
    elif n == 8:
        s = 6
        fig, ax, px, py = setup_ax_for(s, s)
        draw_dim_rect(ax, px, py, s, s, "6 מ'", "6 מ'")
    elif n == 9:
        w, h = 20, 12
        fig, ax, px, py = setup_ax_for(w, h)
        draw_dim_rect(ax, px, py, w, h, "20 מ'", "12 מ'")
    elif n == 10:
        w, h = 9, 6
        fig, ax, px, py = setup_ax_for(w, h, pad_top=2.2)
        draw_dim_rect(ax, px, py, w, h, "$a$", "$b$")
        top_caption(ax, w + px + 1.0, h + py + 2.2, ["a - b = 4 מ'", "היקף = 28 מ'"], fs=10)
    elif n == 11:
        w, h, ext = 8, 6, 2
        fig, ax, px, py = setup_ax_for(w + ext, h)
        draw_dim_rect(ax, px, py, w, h, "8 מ'", "6 מ'")
        strip = Rectangle((px + w, py), ext, h, fill=True, facecolor="#dbeafe", alpha=0.5,
                           edgecolor="#1f2937", linewidth=1.5, linestyle="--")
        ax.add_patch(strip)
        dim_h(ax, px + w, px + w + ext, py, "2 מ'", off=-1.0)
        ax.text(px + w + ext / 2, py + h / 2, "רצועה", fontsize=9, ha="center", color="#1e3a8a")
    elif n == 12:
        w, h = 18, 10
        fig, ax, px, py = setup_ax_for(w, h)
        draw_dim_rect(ax, px, py, w, h, "18 מ'", "10 מ'")
    elif n == 13:
        s = 10
        fig, ax, px, py = setup_ax_for(s, s)
        draw_dim_rect(ax, px, py, s, s, "10 מ'", "10 מ'")
    elif n == 14:
        w, h = 10, 5.5
        fig, ax, px, py = setup_ax_for(w, h, pad_top=2.2)
        draw_dim_rect(ax, px, py, w, h, "$a$", "$b$")
        top_caption(ax, w + px + 1.0, h + py + 2.2, ["אורך − רוחב = 6 מ'", "היקף = 44 מ'"], fs=10)
    elif n == 15:
        s = 7
        fig, ax, px, py = setup_ax_for(s, s, pad_top=2.0)
        draw_dim_rect(ax, px, py, s, s, "$a$", "$a$")
        ax.text(px + s / 2, py + s / 2, 'שטח $= 64$ מ"ר', fontsize=10, ha="center", color="#0f766e")
    elif n == 16:
        w, h = 9, 4
        fig, ax, px, py = setup_ax_for(w, h, pad_top=2.0)
        draw_dim_rect(ax, px, py, w, h, "$3b$", "$b$")
        ax.text(px + w / 2, py + h / 2, 'שטח $= 75$ מ"ר', fontsize=10, ha="center", color="#0f766e")
    elif n == 17:
        w, h = 10, 6.5
        margin = 1.3
        fig, ax, px, py, = setup_ax_for(w, h, pad_top=2.2)
        draw_dim_rect(ax, px, py, w, h, "$a$", "$b$")
        inner = Rectangle((px + margin, py + margin), w - 2 * margin, h - 2 * margin,
                           fill=False, linewidth=2, edgecolor="#0f766e")
        ax.add_patch(inner)
        ax.text(px + w / 2, py + h / 2, "בית", fontsize=11, color="#0f766e", ha="center")
        dim_v(ax, px, py, py + margin, "3 מ'", off=0.55)
        ax.text(px + margin / 2, py + h - margin / 2, "3 מ'", fontsize=8, ha="center",
                bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.9))
        ax.text(px + w - margin / 2, py + margin / 2, "3 מ'", fontsize=8, ha="center",
                bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.9))
        top_caption(ax, w + px + 1.0, h + py + 2.2, ["היקף = 88 מ'", 'שטח = 480 מ"ר'], fs=10)
    elif n == 18:
        w, h = 9, 5
        fig, ax, px, py = setup_ax_for(w, h, pad_top=2.0)
        draw_dim_rect(ax, px, py, w, h, "$x+6$", "$x$")
        top_caption(ax, w + px + 1.0, h + py + 2.0, 'שטח לאחר השינוי $= 126$ מ"ר', fs=10)
    elif n == 19:
        w, h = 8, 5
        pad_out = 0.9
        fig, ax, px, py = setup_ax_for(w + 2 * pad_out, h + 2 * pad_out, pad_top=2.2)
        outer = Rectangle((px, py), w + 2 * pad_out, h + 2 * pad_out, fill=True,
                           facecolor="#dbeafe", alpha=0.45, edgecolor="#1f2937", linewidth=2)
        inner_x, inner_y = px + pad_out, py + pad_out
        hole = Rectangle((inner_x, inner_y), w, h, fill=True, facecolor="white", edgecolor="none")
        ax.add_patch(outer)
        ax.add_patch(hole)
        garden = Rectangle((inner_x, inner_y), w, h, fill=False, linewidth=2, edgecolor="#0f766e")
        ax.add_patch(garden)
        add_labels(
            ax,
            [(inner_x, inner_y), (inner_x + w, inner_y), (inner_x + w, inner_y + h), (inner_x, inner_y + h)],
            ["A", "B", "C", "D"],
        )
        dim_h(ax, inner_x, inner_x + w, inner_y, "$L$", off=-0.75)
        dim_v(ax, inner_x, inner_y, inner_y + h, "$L-4$", off=-0.75)
        dim_h(ax, px, inner_x, py, "1 מ'", off=-1.9)
        top_caption(ax, w + 2 * pad_out + px + 1.0, h + 2 * pad_out + py + 2.2,
                     ["רוחב = אורך − 4 מ'", "היקף מקורי = 32 מ'"], fs=10)
    elif n == 20:
        w, h = 9, 5
        fig, ax, px, py = setup_ax_for(w, h, pad_top=2.0)
        draw_dim_rect(ax, px, py, w, h, "$x$", "$14-x$")
        top_caption(ax, w + px + 1.0, h + py + 2.0, "היקף מקורי = 28 מ'", fs=10)
    else:
        fig, ax = setup_ax()
        draw_rectangle(ax)

    fig.savefig(out_path, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def create_image_5_4(out_path: Path, n: int) -> None:
    """Dedicated, per-exercise diagrams for 9/5.4 with real dimension labels."""

    if n == 1:
        w, h = 12, 8
        fig, ax, px, py = setup_ax_for(w, h)
        draw_dim_rect(ax, px, py, w, h, "12 מ'", "8 מ'")
    elif n == 2:
        w, h = 10, 6
        fig, ax, px, py = setup_ax_for(w, h)
        draw_dim_rect(ax, px, py, w, h, "10 מ'", "6 מ'")
    elif n == 3:
        w, h = 20, 12
        fig, ax, px, py = setup_ax_for(w, h)
        draw_three_sides_dim(ax, px, py, w, h, "20 מ'", "12 מ'")
    elif n == 4:
        s = 9
        fig, ax, px, py = setup_ax_for(s, s)
        draw_dim_rect(ax, px, py, s, s, "9 מ'", "9 מ'")
    elif n == 5:
        w, h = 16, 10
        fig, ax, px, py = setup_ax_for(w, h)
        draw_dim_rect(ax, px, py, w, h, "16 מ'", "10 מ'")
    elif n == 6:
        s = 9
        fig, ax, px, py = setup_ax_for(s, s)
        draw_dim_rect(ax, px, py, s, s, "9 מ'", "9 מ'")
    elif n == 7:
        w, h = 12, 4
        fig, ax, px, py = setup_ax_for(w, h, pad_top=2.0)
        draw_dim_rect(ax, px, py, w, h, "$3x$", "$x$")
        top_caption(ax, w + px + 1.0, h + py + 2.0, "היקף = 56 מ'", fs=10)
    elif n == 8:
        w, h = 14, 10
        fig, ax, px, py = setup_ax_for(w, h)
        draw_three_sides_dim(ax, px, py, w, h, "14 מ'", "10 מ'")
    elif n == 9:
        w, h = 11.5, 6.5
        fig, ax, px, py = setup_ax_for(w, h, pad_top=2.0)
        draw_dim_rect(ax, px, py, w, h, "$a$", "$b$")
        top_caption(ax, w + px + 1.0, h + py + 2.0, "היקף = 46 מ'", fs=10)
    elif n == 10:
        w, h = 8, 4
        fig, ax, px, py = setup_ax_for(w, h, pad_top=2.0)
        draw_three_sides_dim(ax, px, py, w, h, "$2b$", "$b$")
    elif n == 11:
        w, h = 15, 9
        fig, ax, px, py = setup_ax_for(w, h)
        draw_dim_rect(ax, px, py, w, h, "30 מ'", "18 מ'")
    elif n == 12:
        w, h = 9, 4.2
        fig, ax, px, py = setup_ax_for(w, h, pad_top=2.0)
        draw_three_sides_dim(ax, px, py, w, h, "$a$", "$b$")
        top_caption(ax, w + px + 1.0, h + py + 2.0, "$b < \\dfrac{a}{2}$", fs=11)
    elif n == 13:
        w, h = 8, 4
        fig, ax, px, py = setup_ax_for(w, h, pad_top=2.0)
        draw_dim_rect(ax, px, py, w, h, "$2w$", "$w$")
        top_caption(ax, w + px + 1.0, h + py + 2.0, "היקף = 60 מ'", fs=10)
    elif n == 14:
        w, h = 18, 12
        fig, ax, px, py = setup_ax_for(w, h)
        draw_dim_rect(ax, px, py, w, h, "18 מ'", "12 מ'")
    elif n == 15:
        w, h = 20, 14
        margin = 1.0
        fig, ax, px, py = setup_ax_for(w + 2 * margin, h + 2 * margin)
        outer = Rectangle((px, py), w + 2 * margin, h + 2 * margin, fill=True,
                           facecolor="#fde68a", alpha=0.45, edgecolor="#1f2937", linewidth=2)
        garden = Rectangle((px + margin, py + margin), w, h, fill=True,
                            facecolor="#dcfce7", edgecolor="#0f766e", linewidth=2)
        ax.add_patch(outer)
        ax.add_patch(garden)
        add_labels(
            ax,
            [(px + margin, py + margin), (px + margin + w, py + margin),
             (px + margin + w, py + margin + h), (px + margin, py + margin + h)],
            ["A", "B", "C", "D"],
        )
        dim_h(ax, px + margin, px + margin + w, py + margin, "20 מ'", off=-1.0)
        dim_v(ax, px + margin, py + margin, py + margin + h, "14 מ'", off=-1.0)
        dim_h(ax, px, px + margin, py, "1 מ'", off=-1.9)
        ax.text(px + margin + w / 2, py + margin + h / 2, "גינה (דשא)", fontsize=9, ha="center", color="#166534")
        ax.text(px + margin + w / 2, py + h + 1.6 * margin, "שביל", fontsize=9, ha="center", color="#92400e")
    elif n == 16:
        s = 9
        fig, ax, px, py = setup_ax_for(s, s)
        draw_dim_rect(ax, px, py, s, s, "$s$", "$s$")
    elif n == 17:
        w, h = 11.5, 6.5
        fig, ax, px, py = setup_ax_for(w, h, pad_top=2.0)
        draw_dim_rect(ax, px, py, w, h, "$a$", "$b$")
        top_caption(ax, w + px + 1.0, h + py + 2.0, "היקף = 46 מ'", fs=10)
    elif n == 18:
        w, h = 9, 4.2
        fig, ax, px, py = setup_ax_for(w, h, pad_top=2.0)
        draw_three_sides_dim(ax, px, py, w, h, "$a$", "$b$")
        top_caption(ax, w + px + 1.0, h + py + 2.0, "$b < \\dfrac{a}{2}$", fs=11)
    elif n == 19:
        w, h = 8, 5
        margin = 1.5
        fig, ax, px, py = setup_ax_for(w + 2 * margin, h + 2 * margin, pad_top=2.2)
        outer = Rectangle((px, py), w + 2 * margin, h + 2 * margin, fill=False,
                           linewidth=2, edgecolor="#1f2937")
        house = Rectangle((px + margin, py + margin), w, h, fill=False,
                           linewidth=2, edgecolor="#0f766e")
        ax.add_patch(outer)
        ax.add_patch(house)
        add_labels(
            ax,
            [(px, py), (px + w + 2 * margin, py), (px + w + 2 * margin, py + h + 2 * margin), (px, py + h + 2 * margin)],
            ["A", "B", "C", "D"],
        )
        ax.text(px + margin + w / 2, py + margin + h / 2, "בית", fontsize=11, color="#0f766e", ha="center")
        dim_v(ax, px, py, py + margin, "3 מ'", off=0.55)
        top_caption(ax, w + 2 * margin + px + 1.0, h + 2 * margin + py + 2.2,
                     ["היקף המגרש = 52 מ'", 'שטח המגרש = 160 מ"ר'], fs=10)
    elif n == 20:
        w, h = 8, 4
        margin = 1.3
        fig, ax, px, py = setup_ax_for(w + 2 * margin, h + 2 * margin, pad_top=2.2)
        outer = Rectangle((px, py), w + 2 * margin, h + 2 * margin, fill=False,
                           linewidth=2, edgecolor="#1f2937")
        house = Rectangle((px + margin, py + margin), w, h, fill=False,
                           linewidth=2, edgecolor="#0f766e")
        ax.add_patch(outer)
        ax.add_patch(house)
        add_labels(
            ax,
            [(px, py), (px + w + 2 * margin, py), (px + w + 2 * margin, py + h + 2 * margin), (px, py + h + 2 * margin)],
            ["A", "B", "C", "D"],
        )
        ax.text(px + margin + w / 2, py + margin + h / 2, "בית", fontsize=11, color="#0f766e", ha="center")
        dim_v(ax, px, py, py + margin, "2 מ'", off=0.55)
        top_caption(ax, w + 2 * margin + px + 1.0, h + 2 * margin + py + 2.2,
                     ["אורך המגרש − רוחב = 4 מ'", "היקף המגרש = 40 מ'"], fs=10)
    else:
        fig, ax = setup_ax()
        draw_rectangle(ax)

    fig.savefig(out_path, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def inject_links(file_path: Path, target_numbers: set[int], subtopic: str) -> tuple[bool, int]:
    raw_lines = file_path.read_text(encoding="utf-8").splitlines(keepends=True)
    link_line_re = re.compile(rf"^!\[תרגיל\s+\d+\]\(images/9_{re.escape(subtopic)}_ex\d{{2}}\.png\)\s*$")
    lines = [ln for ln in raw_lines if not link_line_re.match(ln.strip())]
    exercises = parse_exercises(lines)
    if not exercises:
        return False, 0

    out_lines: list[str] = []
    cursor = 0
    inserted = 0
    changed = False

    for ex in exercises:
        out_lines.extend(lines[cursor:ex.start])
        block_lines = lines[ex.start:ex.end]
        block_text = "".join(block_lines)

        if ex.number in target_numbers:
            link_line = f"![תרגיל {ex.number}](images/9_{subtopic}_ex{ex.number:02d}.png)\n"
            pattern = re.compile(rf"!\[תרגיל\s+{ex.number}\]\(images/9_{re.escape(subtopic)}_ex{ex.number:02d}\.png\)\n?")
            cleaned = re.sub(pattern, "", block_text)
            cleaned = cleaned.rstrip("\n")
            new_block = cleaned + "\n\n" + link_line + "\n"
            if new_block != block_text:
                changed = True
                inserted += 1
            out_lines.append(new_block)
        else:
            out_lines.extend(block_lines)

        cursor = ex.end

    out_lines.extend(lines[cursor:])
    if changed:
        file_path.write_text("".join(out_lines), encoding="utf-8")
    return changed, inserted


def validate_links(md_path: Path, expected_files: set[str]) -> tuple[int, int]:
    text = md_path.read_text(encoding="utf-8")
    links = set(re.findall(r"!\[תרגיל\s+\d+\]\((images/9_[^)]+\.png)\)", text))
    missing = sum(1 for rel in links if rel.replace("images/", "") not in expected_files)
    return len(links), missing


def main() -> None:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(CHAPTER_DIR.glob("*.md"))
    touched_files: list[Path] = []
    generated_images: set[Path] = set()
    skipped: list[str] = []

    for md in files:
        subtopic = parse_subtopic(md)
        if subtopic not in MUST_SUBTOPICS and subtopic not in SHOULD_SUBTOPICS:
            continue

        lines = md.read_text(encoding="utf-8").splitlines(keepends=True)
        exercises = parse_exercises(lines)
        targets: set[int] = set()

        for ex in exercises:
            if should_generate(subtopic, ex.number, ex.block):
                targets.add(ex.number)
            else:
                if subtopic in SHOULD_SUBTOPICS and ex.number >= 10:
                    skipped.append(f"{subtopic} ex{ex.number:02d}: non-visual")

        for ex in exercises:
            if ex.number in targets:
                image_name = f"9_{subtopic}_ex{ex.number:02d}.png"
                out_path = IMAGES_DIR / image_name
                if subtopic == "5.2":
                    create_image_5_2(out_path, ex.number)
                else:
                    create_image(out_path, ex.block)
                generated_images.add(out_path)

        changed, _ = inject_links(md, targets, subtopic)
        if changed:
            touched_files.append(md)

    expected = {p.name for p in generated_images}
    link_report = []
    total_links = 0
    total_missing = 0

    for md in sorted(touched_files):
        count, missing = validate_links(md, expected)
        total_links += count
        total_missing += missing
        link_report.append((md.name, count, missing))

    print("=== Chapter 9 Geometry Generation Report ===")
    print(f"Generated images: {len(generated_images)}")
    print(f"Markdown files touched: {len(touched_files)}")
    print(f"Total markdown links found in touched files: {total_links}")
    print(f"Missing linked images: {total_missing}")
    print("")
    print("Touched files:")
    for md in touched_files:
        print(f"- {md.relative_to(ROOT)}")
    print("")
    print("Per-file link check:")
    for name, count, missing in link_report:
        print(f"- {name}: links={count}, missing={missing}")
    print("")
    print("Skipped non-visual items:")
    if skipped:
        for s in sorted(set(skipped)):
            print(f"- {s}")
    else:
        print("- none")


if __name__ == "__main__":
    main()
