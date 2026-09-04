#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""גילוי תיקיות פרקים, עצי נושאים וקבצי תרגול."""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMS_DIR = Path(__file__).resolve().parents[1]
TOPIC_TREES_DIR = REPO_ROOT / "עצי נושאים מעודכנים"


def discover_chapters() -> list[dict]:
    """מחזיר רשימת פרקים לפי תיקיות בשורש הפרויקט: 'N - שם'."""
    out = []
    for p in sorted(REPO_ROOT.iterdir()):
        if not p.is_dir():
            continue
        m = re.match(r"^(\d+)\s*-\s*(.+)$", p.name)
        if not m:
            continue
        out.append(
            {
                "num": int(m.group(1)),
                "name": m.group(2).strip(),
                "dir": p,
                "rel": p.name,
                "md_files": sorted(p.glob("*.md")),
                "topic_tree": TOPIC_TREES_DIR / f"עץ נושאים מעודכן פרק {m.group(1)}.txt",
            }
        )
    return out


def find_chapters(nums: list[int]) -> list[dict]:
    all_ch = {c["num"]: c for c in discover_chapters()}
    missing = [n for n in nums if n not in all_ch]
    if missing:
        raise FileNotFoundError(f"לא נמצאו תיקיות לפרקים: {missing}")
    return [all_ch[n] for n in nums]


def load_topic_tree(chapter_num: int) -> str:
    path = TOPIC_TREES_DIR / f"עץ נושאים מעודכן פרק {chapter_num}.txt"
    if not path.exists():
        # נסיון חלופי
        alt = REPO_ROOT / "עצי נושאים" / f"עץ נושאים פרק {chapter_num}.txt"
        path = alt if alt.exists() else path
    if not path.exists():
        return f"(לא נמצא עץ נושאים לפרק {chapter_num})"
    return path.read_text(encoding="utf-8")


def list_practice_files(chapter_num: int) -> list[Path]:
    ch = find_chapters([chapter_num])[0]
    return list(ch["md_files"])


def print_chapter_brief(nums: list[int]) -> None:
    """הדפסת סיכום לסוכן/משתמש לפני בניית מפרט."""
    for ch in find_chapters(nums):
        print("=" * 72)
        print(f"פרק {ch['num']}: {ch['name']}")
        print(f"תיקייה: {ch['rel']}")
        print(f"קבצי תרגול ({len(ch['md_files'])}):")
        for f in ch["md_files"]:
            print(f"  - {f.name}")
        tree = load_topic_tree(ch["num"])
        print("- עץ נושאים (תחילה):")
        print("\n".join(tree.splitlines()[:25]))
        if tree.count("\n") > 25:
            print("  ...")
    print("=" * 72)
