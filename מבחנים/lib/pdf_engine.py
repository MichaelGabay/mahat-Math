#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
מנוע PDF למבחני מה״ט — עברית RTL, נוסחאות LaTeX, כותרות/תחתית.
כללי ברזל (מתוך ניסיון המבחנים הקודמים):
- לעולם לא לערבב עברית עם () . ' מספרים דרך he() בלבד
- מספרים/משתנים לטיניים כמקטע ('ltr', ...)
- תשובות בשורה נפרדת מתחת לתווית «תשובה:»
- בלי סוגריים סביב ניקוד (מתהפכים ב־RTL)
"""

from __future__ import annotations

import io
import os
import re
from pathlib import Path

import matplotlib

MPLDIR = Path(__file__).resolve().parent.parent / ".mplconfig"
MPLDIR.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPLDIR))
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib import rcParams
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

import arabic_reshaper
from bidi.algorithm import get_display

PAGE_W, PAGE_H = A4
NAVY = HexColor("#1a365d")
LINE = HexColor("#2c5282")
LIGHT = HexColor("#edf2f7")
GRAY = HexColor("#4a5568")

_FONT_REG = "ExamHeb"
_FONT_BOLD = "ExamHebBold"
_fonts_ready = False


def _ensure_fonts() -> None:
    global _fonts_ready
    if _fonts_ready:
        return
    reg = Path("/Library/Fonts/Arial Unicode.ttf")
    if not reg.exists():
        reg = Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf")
    pdfmetrics.registerFont(TTFont(_FONT_REG, str(reg)))
    pdfmetrics.registerFont(TTFont(_FONT_BOLD, str(reg)))
    _fonts_ready = True


def he(text: str) -> str:
    return get_display(arabic_reshaper.reshape(text))


def he_text_segments(text: str) -> list:
    if not text:
        return []
    parts = re.split(r"([A-Za-z]+(?:_[A-Za-z0-9]+)?|\d+(?:\.\d+)?)", text)
    segs = []
    for p in parts:
        if p is None or p == "":
            continue
        if re.fullmatch(r"[A-Za-z]+(?:_[A-Za-z0-9]+)?|\d+(?:\.\d+)?", p):
            segs.append(("ltr", f" {p} "))
        else:
            segs.append(("he", p))
    return segs


class ExamPDF:
    """עטיפה נוחה לכל פעולות הציור של מבחן/פתרונות."""

    def __init__(self, path: Path, doc_hint: str = "מבחן"):
        _ensure_fonts()
        self.path = Path(path)
        self.doc_hint = doc_hint
        self.c = canvas.Canvas(str(self.path), pagesize=A4)
        self.page = [1]
        self.right = PAGE_W - 1.8 * cm
        self.left = 1.8 * cm
        self.FONT_REG = _FONT_REG
        self.FONT_BOLD = _FONT_BOLD
        self.NAVY = NAVY
        self.LINE = LINE
        self.LIGHT = LIGHT
        self.GRAY = GRAY
        self.PAGE_W = PAGE_W
        self.PAGE_H = PAGE_H
        self.cm = cm

    # ----- RTL / text -----
    def draw_he(self, text, x_right=None, y=None, font=None, size=11, color=black):
        x_right = self.right if x_right is None else x_right
        font = font or self.FONT_REG
        self.c.setFont(font, size)
        self.c.setFillColor(color)
        rendered = he(text)
        self.c.drawRightString(x_right, y, rendered)
        return self.c.stringWidth(rendered, font, size)

    def draw_rtl_flow(self, x_right, y, segments, font=None, size=10, color=black, gap=0):
        font = font or self.FONT_REG
        self.c.setFont(font, size)
        self.c.setFillColor(color)
        prepared = []
        for kind, text in segments:
            s = he(text) if kind == "he" else text
            prepared.append((s, self.c.stringWidth(s, font, size)))
        total = sum(w for _, w in prepared) + gap * max(0, len(prepared) - 1)
        x = x_right
        for i, (s, w) in enumerate(prepared):
            self.c.drawRightString(x, y, s)
            x -= w + (gap if i < len(prepared) - 1 else 0)
        return total

    def draw_centered_rtl_flow(self, y, segments, font=None, size=10, color=black, gap=0):
        font = font or self.FONT_REG
        self.c.setFont(font, size)
        widths = []
        for kind, text in segments:
            s = he(text) if kind == "he" else text
            widths.append(self.c.stringWidth(s, font, size))
        total = sum(widths) + gap * max(0, len(segments) - 1)
        self.draw_rtl_flow((PAGE_W + total) / 2.0, y, segments, font=font, size=size, color=color, gap=gap)

    # ----- formulas -----
    @staticmethod
    def formula_image(latex: str, fontsize: int = 16, dpi: int = 200) -> ImageReader:
        rcParams["mathtext.fontset"] = "cm"
        fig = plt.figure(figsize=(0.01, 0.01))
        fig.patch.set_alpha(0)
        text = fig.text(0, 0, f"${latex}$", fontsize=fontsize, color="black")
        fig.canvas.draw()
        bbox = text.get_window_extent(renderer=fig.canvas.get_renderer())
        fig.set_size_inches((bbox.width + 8) / dpi, (bbox.height + 8) / dpi)
        text.set_position((4 / dpi, 4 / dpi))
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=dpi, transparent=True, bbox_inches="tight", pad_inches=0.08)
        plt.close(fig)
        buf.seek(0)
        return ImageReader(buf)

    @staticmethod
    def formula_size(img: ImageReader, max_width: float, scale_px: float = 0.42):
        iw, ih = img.getSize()
        scale = min(1.0, max_width / max(iw * scale_px, 1))
        return iw * scale_px * scale, ih * scale_px * scale

    def draw_formula(self, latex: str, y: float, max_width: float = 16 * cm, fontsize: int = 15) -> float:
        img = self.formula_image(latex, fontsize=fontsize)
        w, h = self.formula_size(img, max_width)
        self.c.drawImage(img, (PAGE_W - w) / 2, y - h, width=w, height=h, mask="auto")
        return y - h - 6

    def draw_formula_right(self, latex, x_right, y, fontsize=12, max_width=12 * cm):
        img = self.formula_image(latex, fontsize=fontsize)
        w, h = self.formula_size(img, max_width)
        self.c.drawImage(img, x_right - w, y - h * 0.75, width=w, height=h, mask="auto")
        return w

    def draw_answer(self, latex, y, x_right=None, fontsize=12) -> float:
        x_right = self.right if x_right is None else x_right
        label = he("תשובה:")
        self.c.setFont(self.FONT_BOLD, 10.5)
        self.c.setFillColor(NAVY)
        self.c.drawRightString(x_right, y, label)
        y -= 0.28 * cm
        img = self.formula_image(latex, fontsize=fontsize)
        w, h = self.formula_size(img, 14 * cm)
        self.c.drawImage(img, x_right - w, y - h, width=w, height=h, mask="auto")
        return y - h - 0.4 * cm

    # ----- structure -----
    def draw_section_head(self, letter: str, points: str, text: str, y: float, size=10.5, font=None, color=black):
        font = font or self.FONT_REG
        if letter and letter[-1].isdigit():
            letter_segs = [("he", letter[:-1]), ("ltr", letter[-1] + ".")]
        else:
            letter_segs = [("he", letter), ("ltr", ".")]
        segs = [
            *letter_segs,
            ("ltr", "  "),
            ("ltr", str(points)),
            ("ltr", " "),
            ("he", "נק"),
            ("ltr", "'"),
        ]
        if text.strip():
            segs.append(("ltr", "  —  "))
            segs.extend(he_text_segments(text))
        self.draw_rtl_flow(self.right, y, segs, font=font, size=size, color=color, gap=0)

    def draw_q_heading(self, y, qnum: int, points: int, subtitle: str, size=12) -> float:
        self.c.setFillColor(NAVY)
        self.draw_rtl_flow(
            self.right,
            y,
            [
                ("he", "שאלה"),
                ("ltr", f" {qnum} "),
                ("ltr", "— "),
                ("ltr", str(points)),
                ("ltr", " "),
                ("he", "נקודות"),
                ("ltr", " — "),
                ("he", subtitle),
            ],
            font=self.FONT_BOLD,
            size=size,
            color=NAVY,
            gap=0,
        )
        y -= 0.35 * cm
        self.c.setStrokeColor(LINE)
        self.c.setLineWidth(0.7)
        self.c.line(self.left, y, self.right, y)
        return y - 0.5 * cm

    def draw_sol_heading(self, y, qnum: int, points: int):
        self.c.setFillColor(NAVY)
        self.draw_rtl_flow(
            self.right,
            y,
            [
                ("he", "שאלה"),
                ("ltr", f" {qnum} "),
                ("ltr", "— "),
                ("he", "פתרון"),
                ("ltr", " — "),
                ("ltr", f"{points} "),
                ("he", "נק"),
                ("ltr", "'"),
            ],
            font=self.FONT_BOLD,
            size=12,
            color=NAVY,
            gap=0,
        )

    def write_lines(self, y, n=1, gap=0.55 * cm) -> float:
        self.c.setStrokeColor(LINE)
        self.c.setDash(1, 2)
        self.c.setLineWidth(0.5)
        for _ in range(n):
            self.c.line(self.left, y, self.right, y)
            y -= gap
        self.c.setDash()
        return y

    def draw_page_footer(self, hint: str | None = None):
        hint = hint or self.doc_hint
        self.c.setStrokeColor(LINE)
        self.c.setLineWidth(0.6)
        self.c.line(1.5 * cm, 1.45 * cm, PAGE_W - 1.5 * cm, 1.45 * cm)
        self.draw_centered_rtl_flow(
            1.0 * cm,
            [
                ("he", "עמוד"),
                ("ltr", f" {self.page[0]} "),
                ("ltr", "|"),
                ("he", f" {hint}"),
            ],
            font=self.FONT_REG,
            size=8,
            color=GRAY,
            gap=0,
        )

    def new_page_header(self, title_segments: list | None = None, title_he: str = ""):
        self.c.setFillColor(NAVY)
        self.c.rect(0, PAGE_H - 1.35 * cm, PAGE_W, 1.35 * cm, fill=1, stroke=0)
        self.c.setFillColor(white)
        if title_segments:
            self.draw_centered_rtl_flow(
                PAGE_H - 0.85 * cm,
                title_segments,
                font=self.FONT_BOLD,
                size=11,
                color=white,
                gap=0,
            )
        else:
            self.c.setFont(self.FONT_BOLD, 11)
            self.c.drawCentredString(PAGE_W / 2, PAGE_H - 0.85 * cm, he(title_he))

    def ensure_space(self, y, need, title_segments=None, title_he="", hint=None) -> float:
        if y < need:
            self.draw_page_footer(hint)
            self.c.showPage()
            self.page[0] += 1
            self.new_page_header(title_segments=title_segments, title_he=title_he)
            return PAGE_H - 2.0 * cm
        return y

    def draw_compare_choice_line(self, y):
        self.draw_centered_rtl_flow(
            y,
            [
                ("ltr", "<"),
                ("ltr", "      "),
                ("he", "או"),
                ("ltr", "      "),
                ("ltr", "="),
                ("ltr", "      "),
                ("he", "או"),
                ("ltr", "      "),
                ("ltr", ">"),
            ],
            size=12,
            color=black,
            gap=0,
        )

    def draw_formula_box(self, y, title_he: str, subtitle_he: str, formulas: list[str], extras: list[str] | None = None) -> float:
        """תיבת נוסחאות: רשת 3×N + שורת extras אופציונלית."""
        extras = extras or []
        n = len(formulas)
        rows = (n + 2) // 3
        box_h = (1.15 + rows * 1.05 + (1.45 if extras else 0.35)) * cm
        box_top = y
        box_bottom = box_top - box_h

        self.c.setStrokeColor(LINE)
        self.c.setFillColor(HexColor("#f7fafc"))
        self.c.setLineWidth(1)
        self.c.roundRect(self.left, box_bottom, self.right - self.left, box_h, 6, fill=1, stroke=1)

        self.c.setFillColor(NAVY)
        self.c.setFont(self.FONT_BOLD, 10)
        self.c.drawRightString(self.right - 0.35 * cm, box_top - 0.4 * cm, he(title_he))
        self.c.setFont(self.FONT_REG, 7.5)
        self.c.setFillColor(GRAY)
        self.c.drawRightString(self.right - 0.35 * cm, box_top - 0.75 * cm, he(subtitle_he))

        cols = 3
        margin_x = 0.3 * cm
        grid_top = box_top - 1.0 * cm
        grid_bottom = box_bottom + (1.55 * cm if extras else 0.25 * cm)
        grid_left = self.left + margin_x
        grid_right = self.right - margin_x
        cell_w = (grid_right - grid_left) / cols
        cell_h = (grid_top - grid_bottom) / max(rows, 1)

        for idx, latex in enumerate(formulas):
            r = idx // cols
            col = idx % cols
            col_from_right = cols - 1 - col
            cx = grid_left + (col_from_right + 0.5) * cell_w
            cy = grid_top - (r + 0.55) * cell_h
            fs = 9 if len(latex) > 40 else 10.5
            img = self.formula_image(latex, fontsize=fs)
            max_w = cell_w - 0.2 * cm
            w, h = self.formula_size(img, max_w, scale_px=0.36)
            self.c.drawImage(img, cx - w / 2, cy - h / 2, width=w, height=h, mask="auto")

        if extras:
            sep_y = box_bottom + 1.35 * cm
            self.c.setStrokeColor(LINE)
            self.c.setLineWidth(0.6)
            self.c.line(self.left + 0.35 * cm, sep_y, self.right - 0.35 * cm, sep_y)
            extra_top = sep_y - 0.35 * cm
            extra_bottom = box_bottom + 0.2 * cm
            extra_h = extra_top - extra_bottom
            for idx, latex in enumerate(extras[:3]):
                col_from_right = cols - 1 - idx
                cx = grid_left + (col_from_right + 0.5) * cell_w
                cy = extra_bottom + extra_h * 0.45
                img = self.formula_image(latex, fontsize=11)
                w, h = self.formula_size(img, cell_w - 0.2 * cm, scale_px=0.36)
                self.c.drawImage(img, cx - w / 2, cy - h / 2, width=w, height=h, mask="auto")

        return box_bottom - 0.4 * cm

    def draw_cover(
        self,
        main_title_segments: list,
        topics_he: str,
        difficulty_he: str = "רמת קושי: שאלות בסגנון בחינות מה״ט — הרמה הגבוהה ביותר",
        duration_min: int = 120,
        total_points: int = 100,
        notes: list[str] | None = None,
    ) -> float:
        """כותרת עליונה + פרטי תלמיד + הוראות. מחזיר y להמשך."""
        notes = notes or []
        c = self.c
        c.setFillColor(NAVY)
        c.rect(0, PAGE_H - 3.2 * cm, PAGE_W, 3.2 * cm, fill=1, stroke=0)
        self.draw_centered_rtl_flow(PAGE_H - 1.15 * cm, main_title_segments, font=self.FONT_BOLD, size=16, color=white, gap=0)
        c.setFont(self.FONT_REG, 11)
        c.setFillColor(white)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 1.85 * cm, he(topics_he))
        c.setFont(self.FONT_REG, 10)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 2.55 * cm, he(difficulty_he))

        y = PAGE_H - 3.9 * cm
        c.setStrokeColor(LINE)
        c.setFillColor(LIGHT)
        c.roundRect(self.left, y - 2.35 * cm, PAGE_W - 3.6 * cm, 2.5 * cm, 6, fill=1, stroke=1)
        c.setFillColor(black)
        self.draw_he("שם התלמיד/ה: ________________________________", self.right - 0.3 * cm, y - 0.55 * cm, self.FONT_BOLD, 12)
        self.draw_he("תעודת זהות: ______________________     כיתה/קבוצה: ______________", self.right - 0.3 * cm, y - 1.25 * cm, size=11)
        self.draw_he("תאריך: ____ / ____ / ________", self.right - 0.3 * cm, y - 1.95 * cm, size=11)

        y -= 3.0 * cm
        self.draw_rtl_flow(
            self.right,
            y,
            [
                ("he", "משך המבחן: שעתיים —"),
                ("ltr", f" {duration_min} "),
                ("he", "דקות"),
            ],
            font=self.FONT_BOLD,
            size=11,
            color=NAVY,
            gap=0,
        )
        self.draw_rtl_flow(
            self.left + 4.2 * cm,
            y,
            [("he", "סה״כ:"), ("ltr", f" {total_points} "), ("he", "נקודות")],
            font=self.FONT_BOLD,
            size=11,
            color=NAVY,
            gap=0,
        )

        y -= 0.55 * cm
        default_notes = [
            "הוראות: ענו על כל השאלות. יש להציג דרך פתרון מלאה ומסודרת.",
            'בסעיפים שבהם מצוין "ללא מחשבון" — אין להשתמש במחשבון. בשאר הסעיפים מותר מחשבון מדעי.',
            "שימו לב לניקוד המדויק של כל סעיף. אין קשר בין שאלות, אלא אם צוין במפורש.",
        ]
        for note in default_notes + notes:
            self.draw_he(note, self.right, y, size=9, color=GRAY if note in default_notes else NAVY)
            y -= 0.4 * cm

        y -= 0.05 * cm
        c.setStrokeColor(LINE)
        c.setLineWidth(1.2)
        c.line(self.left, y, self.right, y)
        return y - 0.45 * cm

    def draw_total_box(self, point_breakdown: str, total: int = 100):
        box_y = 1.75 * cm
        self.c.setStrokeColor(NAVY)
        self.c.setLineWidth(1)
        self.c.roundRect(self.left, box_y, PAGE_W - 3.6 * cm, 1.25 * cm, 5, fill=0, stroke=1)
        self.draw_centered_rtl_flow(
            box_y + 0.72 * cm,
            [
                ("he", "סה״כ המבחן:"),
                ("ltr", f" {total} "),
                ("he", "נקודות"),
                ("ltr", "  |  "),
                ("he", "בהצלחה"),
                ("ltr", "!"),
            ],
            font=self.FONT_BOLD,
            size=10,
            color=NAVY,
        )
        self.c.setFont(self.FONT_REG, 9)
        self.c.setFillColor(GRAY)
        self.c.drawCentredString(PAGE_W / 2, box_y + 0.28 * cm, point_breakdown)

    def save(self):
        self.c.save()
        return self.path
