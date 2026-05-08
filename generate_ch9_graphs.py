#!/usr/bin/env python3
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.patches import Polygon, Rectangle
from bidi.algorithm import get_display


ROOT = Path("/Users/mq/Desktop/מתמטיקה - אורט/mahat-Math")
CHAPTER_DIR = ROOT / "9 - שאלות מילוליות"
IMAGES_DIR = CHAPTER_DIR / "images"

MUST_SUBTOPICS = {"5.1", "5.2", "5.4", "7.3"}
SHOULD_SUBTOPICS = {"2.2", "5.3", "6.2", "7.2"}
HEBREW_RE = re.compile(r"[\u0590-\u05FF]")


def rtl_text(value):
    if isinstance(value, str) and HEBREW_RE.search(value):
        return get_display(value)
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
    if "שלושה צדדים" in text or "שלוש צלעות" in text:
        return "three_sides"
    if "ריבוע" in text:
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
