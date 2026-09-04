#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""מודלים להגדרת מבחן מה״ט באופן דקלרטיבי."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class FormulaBox:
    title_he: str = "נוסחאות רלוונטיות למבחן — מתוך דף הנוסחאות של מה״ט"
    subtitle_he: str = "רק נוסחאות שנדרשות לתרגילים במבחן זה"
    formulas: list[str] = field(default_factory=list)
    extras: list[str] = field(default_factory=list)


@dataclass
class Section:
    """סעיף במבחן (א / ב1 / ג ...)."""

    letter: str
    points: int
    prompt_he: str
    # גוף הסעיף — ציור מותאם (נוסחאות, שורות כתיבה וכו')
    # חתימה: (pdf: ExamPDF, y: float) -> float
    draw_body: Optional[Callable] = None
    answer_latex: str = ""
    solution_title_he: str = ""
    # ציור פתרון מותאם; אם None — מציגים answer_latex בלבד
    draw_solution: Optional[Callable] = None
    lines: int = 1
    line_gap: float = 0.45


@dataclass
class Question:
    number: int
    points: int
    subtitle_he: str
    intro_he: str = ""
    sections: list[Section] = field(default_factory=list)

    def validate_points(self) -> None:
        s = sum(sec.points for sec in self.sections)
        if s != self.points:
            raise ValueError(
                f"שאלה {self.number}: סכום סעיפים={s} ≠ ניקוד שאלה={self.points}"
            )


@dataclass
class AnswerRow:
    label_he: str
    latex: str


@dataclass
class ExamSpec:
    """מפרט מלא של מבחן + פתרונות."""

    # מטא
    exam_filename: str
    solutions_filename: str
    chapter_nums: list[int]
    chapter_dirs: list[str]  # שמות תיקיות יחסיות לשורש הפרויקט
    topics_he: str  # שורת נושאים בכותרת
    page_title_he: str  # כותרת עמודים פנימיים (בלי מספרים מתהפכים)
    duration_min: int = 120
    total_points: int = 100
    cover_notes: list[str] = field(default_factory=list)

    formula_box: Optional[FormulaBox] = None
    questions: list[Question] = field(default_factory=list)
    summary_rows: list[AnswerRow] = field(default_factory=list)

    # מקטעי כותרת ראשית: [('he','...'), ('ltr',' 99913')]
    main_title_segments: list = field(
        default_factory=lambda: [
            ("he", "מבחן במתמטיקה — שאלון"),
            ("ltr", " 99913"),
        ]
    )

    # כותרת עמודי פתרונות עם מספרים
    def solutions_header_segments(self) -> list:
        nums = self.chapter_nums
        segs = [("he", "פתרונות מלאים — מבחן פרקים")]
        if len(nums) == 1:
            segs.append(("ltr", f" {nums[0]}"))
        elif len(nums) >= 2:
            segs.append(("ltr", f" {nums[0]}"))
            segs.append(("ltr", "–"))
            segs.append(("ltr", str(nums[1])))
        return segs

    def exam_header_segments(self) -> list:
        return [("he", self.page_title_he)]

    def point_breakdown(self) -> str:
        parts = [str(q.points) for q in self.questions]
        return " + ".join(parts) + f" = {self.total_points}"

    def validate(self) -> None:
        for q in self.questions:
            q.validate_points()
        total = sum(q.points for q in self.questions)
        if total != self.total_points:
            raise ValueError(f"סה״כ שאלות={total} ≠ total_points={self.total_points}")
        if len(self.questions) < 1:
            raise ValueError("חייב להיות לפחות שאלה אחת")
