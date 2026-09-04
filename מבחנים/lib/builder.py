#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""בניית PDF מבחן + פתרונות מתוך ExamSpec."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import black
from reportlab.lib.units import cm

from .models import ExamSpec
from .pdf_engine import ExamPDF, LIGHT, LINE, NAVY, PAGE_W, he


def build_exam_pdf(spec: ExamSpec, out_dir: Path) -> Path:
    spec.validate()
    path = out_dir / spec.exam_filename
    pdf = ExamPDF(path, doc_hint="מבחן")

    y = pdf.draw_cover(
        main_title_segments=spec.main_title_segments,
        topics_he=spec.topics_he,
        duration_min=spec.duration_min,
        total_points=spec.total_points,
        notes=spec.cover_notes,
    )

    if spec.formula_box and (spec.formula_box.formulas or spec.formula_box.extras):
        y = pdf.draw_formula_box(
            y,
            spec.formula_box.title_he,
            spec.formula_box.subtitle_he,
            spec.formula_box.formulas,
            spec.formula_box.extras,
        )

    header_segs = spec.exam_header_segments()
    for q in spec.questions:
        y = pdf.ensure_space(y, 10 * cm, title_segments=header_segs, hint="מבחן")
        y = pdf.draw_q_heading(y, q.number, q.points, q.subtitle_he)
        pdf.c.setFillColor(black)
        if q.intro_he:
            pdf.draw_he(q.intro_he, pdf.right, y, size=10)
            y -= 0.38 * cm

        for sec in q.sections:
            y = pdf.ensure_space(y, 5 * cm, title_segments=header_segs, hint="מבחן")
            pdf.draw_section_head(sec.letter, str(sec.points), sec.prompt_he, y)
            y -= 0.35 * cm
            if sec.draw_body:
                y = sec.draw_body(pdf, y)
            else:
                y = pdf.write_lines(y - 0.15 * cm, n=sec.lines, gap=sec.line_gap * cm)
            y -= 0.25 * cm

    pdf.draw_total_box(spec.point_breakdown(), spec.total_points)
    pdf.draw_page_footer("מבחן")
    return pdf.save()


def build_solutions_pdf(spec: ExamSpec, out_dir: Path) -> Path:
    spec.validate()
    path = out_dir / spec.solutions_filename
    pdf = ExamPDF(path, doc_hint="פתרונות")
    c = pdf.c

    # כותרת
    c.setFillColor(NAVY)
    c.rect(0, pdf.PAGE_H - 2.6 * cm, PAGE_W, 2.6 * cm, fill=1, stroke=0)
    from reportlab.lib.colors import white

    c.setFillColor(white)
    c.setFont(pdf.FONT_BOLD, 15)
    c.drawCentredString(PAGE_W / 2, pdf.PAGE_H - 1.1 * cm, he("קובץ פתרונות — מבחן מה״ט"))
    pdf.draw_centered_rtl_flow(
        pdf.PAGE_H - 1.8 * cm,
        [
            ("he", spec.topics_he.replace("נושאים: ", "")),
            ("ltr", "  |  "),
            ("he", "סה״כ"),
            ("ltr", f" {spec.total_points} "),
            ("he", "נקודות"),
        ],
        font=pdf.FONT_REG,
        size=10,
        color=white,
    )

    y = pdf.PAGE_H - 3.3 * cm
    header_segs = spec.solutions_header_segments()

    for q in spec.questions:
        y = pdf.ensure_space(y, 8 * cm, title_segments=header_segs, hint="פתרונות")
        pdf.draw_sol_heading(y, q.number, q.points)
        y -= 0.5 * cm
        c.setFillColor(black)

        for sec in q.sections:
            y = pdf.ensure_space(y, 4.5 * cm, title_segments=header_segs, hint="פתרונות")
            title = sec.solution_title_he or sec.prompt_he
            pdf.draw_section_head(sec.letter, str(sec.points), title, y)
            y -= 0.2 * cm
            if sec.draw_solution:
                y = sec.draw_solution(pdf, y)
            elif sec.answer_latex:
                y = pdf.draw_answer(sec.answer_latex, y)
            y -= 0.15 * cm

    # סיכום תשובות
    from .models import AnswerRow

    if not spec.summary_rows:
        summary = []
        for q in spec.questions:
            joined = r";\ ".join(s.answer_latex for s in q.sections if s.answer_latex)
            if joined:
                summary.append(AnswerRow(f"שאלה {q.number}:", joined))
        spec.summary_rows = summary

    y = pdf.ensure_space(y, 7 * cm, title_segments=header_segs, hint="פתרונות")
    box_h = max(4.5 * cm, 0.7 * cm * (len(spec.summary_rows) + 2))
    c.setFillColor(LIGHT)
    c.setStrokeColor(LINE)
    c.roundRect(pdf.left, y - box_h, PAGE_W - 3.6 * cm, box_h + 0.2 * cm, 6, fill=1, stroke=1)
    c.setFillColor(NAVY)
    c.setFont(pdf.FONT_BOLD, 11)
    c.drawRightString(pdf.right - 0.3 * cm, y - 0.4 * cm, he("סיכום תשובות סופיות"))
    c.setFillColor(black)

    yy = y - 1.0 * cm
    for row in spec.summary_rows:
        pdf.draw_he(row.label_he, pdf.right - 0.3 * cm, yy, size=9)
        lw = c.stringWidth(he(row.label_he), pdf.FONT_REG, 9)
        pdf.draw_formula_right(row.latex, pdf.right - 0.3 * cm - lw - 8, yy, fontsize=9.5, max_width=11 * cm)
        yy -= 0.58 * cm

    pdf.draw_centered_rtl_flow(
        y - box_h + 0.35 * cm,
        [("he", "ניקוד:"), ("ltr", f"  {spec.point_breakdown()}")],
        font=pdf.FONT_BOLD,
        size=10,
        color=NAVY,
    )
    pdf.draw_page_footer("פתרונות")
    return pdf.save()
