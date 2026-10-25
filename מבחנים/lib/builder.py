#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""בניית PDF מבחן + פתרונות מתוך ExamSpec."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import black
from reportlab.lib.units import cm

from .models import ExamSpec
from .pdf_engine import ExamPDF, LIGHT, LINE, NAVY, PAGE_W, he, he_text_segments


def build_exam_pdf(spec: ExamSpec, out_dir: Path) -> Path:
    spec.validate()
    path = out_dir / spec.exam_filename
    pdf = ExamPDF(path, doc_hint="מבחן")
    pdf.c.setTitle(spec.page_title_he)

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
        if q.new_page:
            y = pdf.ensure_space(0, 1, title_segments=header_segs, hint="מבחן")
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
    pdf.c.setTitle("פתרונות - " + spec.page_title_he)
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
        if q.new_page and q.number != spec.questions[0].number:
            y = pdf.ensure_space(0, 1, title_segments=header_segs, hint="פתרונות")
        y = pdf.ensure_space(y, 8 * cm, title_segments=header_segs, hint="פתרונות")
        pdf.draw_sol_heading(y, q.number, q.points)
        y -= 0.5 * cm
        c.setFillColor(black)

        for sec in q.sections:
            needed = (sec.solution_height_cm + 2) * cm if sec.solution_height_cm else 4.5 * cm
            y = pdf.ensure_space(y, needed, title_segments=header_segs, hint="פתרונות")
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

    rendered_rows = []
    for row in spec.summary_rows:
        img = pdf.formula_image(row.latex, fontsize=11)
        w, h = pdf.formula_size(img, 11 * cm)
        rendered_rows.append((row, img, w, h, max(0.9 * cm, h + 0.25 * cm)))
    box_h = max(4.5 * cm, 1.8 * cm + sum(row[4] for row in rendered_rows))
    if spec.summary_new_page:
        y = 0
    y = pdf.ensure_space(y, max(7 * cm, box_h + 2 * cm), title_segments=header_segs, hint="פתרונות")
    c.setFillColor(LIGHT)
    c.setStrokeColor(LINE)
    c.roundRect(pdf.left, y - box_h, PAGE_W - 3.6 * cm, box_h + 0.2 * cm, 6, fill=1, stroke=1)
    c.setFillColor(NAVY)
    c.setFont(pdf.FONT_BOLD, 11)
    c.drawRightString(pdf.right - 0.3 * cm, y - 0.4 * cm, he("סיכום תשובות סופיות"))
    c.setFillColor(black)

    yy = y - 0.8 * cm
    for row, img, w, h, row_h in rendered_rows:
        center_y = yy - row_h / 2
        lw = pdf.draw_rtl_flow(pdf.right - 0.3 * cm, center_y - 3,
                               he_text_segments(row.label_he), size=9)
        c.drawImage(img, pdf.right - 0.3 * cm - lw - 12 - w,
                    center_y - h / 2, width=w, height=h, mask="auto")
        yy -= row_h

    pdf.draw_centered_rtl_flow(
        y - box_h + 0.35 * cm,
        [("he", "ניקוד:"), ("ltr", f"  {spec.point_breakdown()}")],
        font=pdf.FONT_BOLD,
        size=10,
        color=NAVY,
    )
    pdf.draw_page_footer("פתרונות")
    return pdf.save()
