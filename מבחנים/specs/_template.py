#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
תבנית מפרט מבחן — העתק לקובץ חדש (למשל ch4_ch5.py) ומלא תוכן.

שימוש:
  python3 מבחנים/generate_exam.py --scaffold 4 5
  # נוצר specs/ch4_ch5.py על בסיס התבנית + סיכום נושאים
  # אחר כך ממלאים שאלות ומריצים:
  python3 מבחנים/generate_exam.py --spec ch4_ch5
"""

from __future__ import annotations

from reportlab.lib.units import cm

from lib.models import AnswerRow, ExamSpec, FormulaBox, Question, Section


def _body_formula(latex: str, lines: int = 1, fontsize: int = 15):
    def draw(pdf, y):
        y = pdf.draw_formula(latex, y, fontsize=fontsize)
        return pdf.write_lines(y - 0.2 * cm, n=lines, gap=0.55 * cm)

    return draw


def _sol_steps(*latex_lines: str, answer: str):
    def draw(pdf, y):
        for L in latex_lines:
            y = pdf.draw_formula(L, y, fontsize=12)
            y -= 0.05 * cm
        return pdf.draw_answer(answer, y)

    return draw


def build_spec() -> ExamSpec:
    """
    !!! זהו דוגמה מינימלית — החלף בתוכן אמיתי ברמת מה״ט.
    ודא: סכום נקודות סעיפים = ניקוד שאלה; סכום שאלות = 100.
    """

    q1 = Question(
        number=1,
        points=25,
        subtitle_he="כותרת נושא השאלה",
        intro_he="נתון הביטוי / המשוואה:",
        sections=[
            Section(
                letter="א",
                points=8,
                prompt_he="כתבו את תחום ההגדרה של x.",
                draw_body=lambda pdf, y: pdf.write_lines(y - 0.9 * cm, n=1),
                answer_latex=r"x \neq 0",
                solution_title_he="תחום ההגדרה:",
                draw_solution=_sol_steps(r"x \neq 0", answer=r"x \neq 0"),
            ),
            Section(
                letter="ב",
                points=12,
                prompt_he="פשטו / פתרו.",
                draw_body=_body_formula(r"\frac{1}{x} + \frac{1}{x+1}", lines=2),
                answer_latex=r"\frac{2x+1}{x(x+1)}",
                solution_title_he="מכנה משותף:",
                draw_solution=_sol_steps(
                    r"\frac{1}{x}+\frac{1}{x+1}=\frac{x+1+x}{x(x+1)}=\frac{2x+1}{x(x+1)}",
                    answer=r"\frac{2x+1}{x(x+1)}",
                ),
            ),
            Section(
                letter="ג",
                points=5,
                prompt_he="הציבו וחשבו כאשר:",
                draw_body=_body_formula(r"x = 2", lines=1, fontsize=13),
                answer_latex=r"\frac{5}{6}",
                solution_title_he="הצבה:",
                draw_solution=_sol_steps(
                    r"\frac{2\cdot2+1}{2\cdot3}=\frac{5}{6}",
                    answer=r"\frac{5}{6}",
                ),
            ),
        ],
    )

    # שאלות 2–4: השלם לפי חומר הפרקים (סה״כ 75 נק׳ נוספות)
    q2 = Question(number=2, points=25, subtitle_he="TODO — נושא", sections=[
        Section("א", 25, "TODO — החלף בסעיפים מפורטים עם ניקוד", answer_latex=r"TODO"),
    ])
    q3 = Question(number=3, points=25, subtitle_he="TODO — נושא", sections=[
        Section("א", 25, "TODO", answer_latex=r"TODO"),
    ])
    q4 = Question(number=4, points=25, subtitle_he="TODO — נושא", sections=[
        Section("א", 25, "TODO", answer_latex=r"TODO"),
    ])

    return ExamSpec(
        exam_filename="מבחן_TODO.pdf",
        solutions_filename="פתרונות_TODO.pdf",
        chapter_nums=[0],
        chapter_dirs=[],
        topics_he="נושאים: TODO",
        page_title_he="מבחן מה״ט — TODO",
        cover_notes=["הערה: התאם לפי הצורך (למשל נושאים מוחרגים)."],
        formula_box=FormulaBox(
            formulas=[
                r"a^{-n}=\frac{1}{a^{n}}",
                r"a^{m}\cdot a^{n}=a^{m+n}",
                r"(a^{m})^{n}=a^{m\cdot n}",
            ],
            extras=[],
        ),
        questions=[q1, q2, q3, q4],
        summary_rows=[
            AnswerRow("שאלה 1:", r"x\neq0;\ \frac{2x+1}{x(x+1)};\ \frac{5}{6}"),
            AnswerRow("שאלה 2:", r"TODO"),
            AnswerRow("שאלה 3:", r"TODO"),
            AnswerRow("שאלה 4:", r"TODO"),
        ],
    )
