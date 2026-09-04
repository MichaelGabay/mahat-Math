#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
מבחן מה״ט — פרקים 1–2 (ייחוס זהב).

להפקה:
  python3 מבחנים/generate_exam.py --legacy-ch12
  # או:
  python3 מבחנים/generate_exam_ch1_ch2.py

למבחנים חדשים מפרקים אחרים — ראה:
  מבחנים/README_EXAM_GENERATOR.md
  מבחנים/generate_exam.py --scaffold N M
"""

from __future__ import annotations

import io
import os
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
MPLDIR = Path(__file__).resolve().parent / ".mplconfig"
MPLDIR.mkdir(exist_ok=True)
os.environ["MPLCONFIGDIR"] = str(MPLDIR)

import matplotlib.pyplot as plt
from matplotlib import rcParams
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

import arabic_reshaper
from bidi.algorithm import get_display

OUT_DIR = Path(__file__).resolve().parent
PAGE_W, PAGE_H = A4

# Arial Unicode — עברית + לטינית + ספרות באותו גופן (קריאות RTL טובה)
HEB_REG_PATH = "/Library/Fonts/Arial Unicode.ttf"
HEB_BOLD_PATH = "/Library/Fonts/Arial Unicode.ttf"
if not Path(HEB_REG_PATH).exists():
    HEB_REG_PATH = HEB_BOLD_PATH = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"

FONT_REG = "ExamHeb"
FONT_BOLD = "ExamHebBold"
pdfmetrics.registerFont(TTFont(FONT_REG, HEB_REG_PATH))
pdfmetrics.registerFont(TTFont(FONT_BOLD, HEB_BOLD_PATH))

NAVY = HexColor("#1a365d")
LINE = HexColor("#2c5282")
LIGHT = HexColor("#edf2f7")
GRAY = HexColor("#4a5568")

RLM = "\u200F"
LRM = "\u200E"


def he(text: str) -> str:
    """עיבוד RTL לעברית בלבד (בלי סימנים מתמטיים)."""
    return get_display(arabic_reshaper.reshape(text))


def draw_he(c: canvas.Canvas, text: str, x_right: float, y: float, font=FONT_REG, size=11, color=black):
    """שורת עברית מיושרת לימין."""
    c.setFont(font, size)
    c.setFillColor(color)
    rendered = he(text)
    c.drawRightString(x_right, y, rendered)
    return c.stringWidth(rendered, font, size)


def draw_he_ltr_mix(c, x_right, y, segments, size=11, font=FONT_REG, color=black, gap=3):
    """
    ציור מימין לשמאל של מקטעים.
    segments: רשימת מחרוזות עבריות, או ('ltr', '...') למספרים/סימנים.
    """
    c.setFont(font, size)
    c.setFillColor(color)
    x = x_right
    for seg in segments:
        if isinstance(seg, tuple) and seg[0] == "ltr":
            s = seg[1]
        else:
            s = he(seg if isinstance(seg, str) else seg[1])
        c.drawRightString(x, y, s)
        x -= c.stringWidth(s, font, size) + gap
    return x


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


def formula_size(img: ImageReader, max_width: float, scale_px: float = 0.42):
    iw, ih = img.getSize()
    scale = min(1.0, max_width / max(iw * scale_px, 1))
    return iw * scale_px * scale, ih * scale_px * scale


def draw_formula(c: canvas.Canvas, latex: str, y: float, max_width: float = 16 * cm, fontsize: int = 15) -> float:
    img = formula_image(latex, fontsize=fontsize)
    w, h = formula_size(img, max_width)
    c.drawImage(img, (PAGE_W - w) / 2, y - h, width=w, height=h, mask="auto")
    return y - h - 6


def draw_formula_right(c, latex, x_right, y, fontsize=12, max_width=12 * cm):
    img = formula_image(latex, fontsize=fontsize)
    w, h = formula_size(img, max_width)
    c.drawImage(img, x_right - w, y - h * 0.75, width=w, height=h, mask="auto")
    return w


def draw_answer(c, latex, x_right, y, fontsize=12) -> float:
    """תשובה בשורה נפרדת מתחת לתווית — בלי חפיפה עם הנוסחה."""
    label = he("תשובה:")
    c.setFont(FONT_BOLD, 10.5)
    c.setFillColor(NAVY)
    c.drawRightString(x_right, y, label)
    y -= 0.28 * cm
    img = formula_image(latex, fontsize=fontsize)
    w, h = formula_size(img, 14 * cm)
    c.drawImage(img, x_right - w, y - h, width=w, height=h, mask="auto")
    return y - h - 0.4 * cm


def he_text_segments(text: str) -> list:
    """
    מפרק טקסט עברי שמכיל משתנים/מספרים לטיניים למקטעים,
    כדי ש־x/y לא יקפצו לסוף/תחילת השורה.
    """
    if not text:
        return []
    parts = re.split(r"([A-Za-z]+(?:_[A-Za-z0-9]+)?|\d+(?:\.\d+)?)", text)
    segs = []
    for p in parts:
        if p is None or p == "":
            continue
        if re.fullmatch(r"[A-Za-z]+(?:_[A-Za-z0-9]+)?|\d+(?:\.\d+)?", p):
            # רווחים סביב משתנה לטיני — מונע הידבקות למילה העברית
            segs.append(("ltr", f" {p} "))
        else:
            segs.append(("he", p))
    return segs


def draw_section_head(c, letter: str, points: str, text: str, x_right: float, y: float, size=10.5, font=FONT_REG, color=black):
    """
    א. 8 נק' — טקסט...
    בלי סוגריים (ב־RTL הן מתהפכות ב־PDF).
    """
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
    draw_rtl_flow(c, x_right, y, segs, font=font, size=size, color=color, gap=0)


def draw_q_heading(c, x_right, y, qnum: int, points: int, subtitle: str, size=12):
    """שאלה 1 — 25 נקודות — כותרת משנה"""
    c.setFillColor(NAVY)
    draw_rtl_flow(
        c,
        x_right,
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
        font=FONT_BOLD,
        size=size,
        color=NAVY,
        gap=0,
    )
    y -= 0.35 * cm
    c.setStrokeColor(LINE)
    c.setLineWidth(0.7)
    c.line(1.8 * cm, y, x_right, y)
    return y - 0.5 * cm


def draw_sol_heading(c, x_right, y, qnum: int, points: int):
    """שאלה 1 — פתרון — 25 נק'"""
    c.setFillColor(NAVY)
    draw_rtl_flow(
        c,
        x_right,
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
        font=FONT_BOLD,
        size=12,
        color=NAVY,
        gap=0,
    )


def draw_rtl_flow(c, x_right, y, segments, font=FONT_REG, size=10, color=black, gap=0):
    """
    ציור מימין לשמאל לפי סדר קריאה עברי.
    segments: [('he','...'), ('ltr','...'), ...] — הראשון הוא הימני ביותר.
    מחזיר את רוחב השורה הכולל.
    """
    c.setFont(font, size)
    c.setFillColor(color)
    prepared = []
    for kind, text in segments:
        s = he(text) if kind == "he" else text
        prepared.append((s, c.stringWidth(s, font, size)))
    total = sum(w for _, w in prepared) + gap * max(0, len(prepared) - 1)
    x = x_right
    for i, (s, w) in enumerate(prepared):
        c.drawRightString(x, y, s)
        x -= w + (gap if i < len(prepared) - 1 else 0)
    return total


def draw_centered_rtl_flow(c, y, segments, font=FONT_REG, size=10, color=black, gap=0):
    """ממורכז: מחשב רוחב ואז מצייר מימין למרכז+חצי־רוחב."""
    c.setFont(font, size)
    widths = []
    for kind, text in segments:
        s = he(text) if kind == "he" else text
        widths.append(c.stringWidth(s, font, size))
    total = sum(widths) + gap * max(0, len(segments) - 1)
    draw_rtl_flow(c, (PAGE_W + total) / 2.0, y, segments, font=font, size=size, color=color, gap=gap)


def draw_page_footer(c, page_no: int, hint: str = "מבחן"):
    """כותרת תחתונה אחידה: עמוד N | מבחן (קריאה מימין)."""
    c.setStrokeColor(LINE)
    c.setLineWidth(0.6)
    c.line(1.5 * cm, 1.45 * cm, PAGE_W - 1.5 * cm, 1.45 * cm)
    draw_centered_rtl_flow(
        c,
        1.0 * cm,
        [
            ("he", "עמוד"),
            ("ltr", f" {page_no} "),
            ("ltr", "|"),
            ("he", f" {hint}"),
        ],
        font=FONT_REG,
        size=8,
        color=GRAY,
        gap=0,
    )


def new_page_header(c, title: str, page_no: int, total_hint: str = ""):
    c.setFillColor(NAVY)
    c.rect(0, PAGE_H - 1.35 * cm, PAGE_W, 1.35 * cm, fill=1, stroke=0)
    c.setFillColor(white)
    # כותרות עם מספרים — מקטעים נפרדים כדי שלא יתהפכו ב־RTL
    if "פרקים" in title and "1" in title:
        draw_centered_rtl_flow(
            c,
            PAGE_H - 0.85 * cm,
            [
                ("he", "פתרונות מלאים — מבחן פרקים"),
                ("ltr", " 1"),
                ("ltr", "–"),
                ("ltr", "2"),
            ],
            font=FONT_BOLD,
            size=11,
            color=white,
            gap=0,
        )
    else:
        c.setFont(FONT_BOLD, 11)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 0.85 * cm, he(title))


def ensure_space(c, y, need, title, page_no_ref, total_hint="מבחן"):
    if y < need:
        draw_page_footer(c, page_no_ref[0], total_hint)
        c.showPage()
        page_no_ref[0] += 1
        new_page_header(c, title, page_no_ref[0], total_hint)
        return PAGE_H - 2.0 * cm
    return y


def draw_compare_choice_line(c, y):
    """< או = או > — סימנים LTR, 'או' בעברית, בסדר קריאה מימין."""
    draw_centered_rtl_flow(
        c,
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
        font=FONT_REG,
        size=12,
        color=black,
    )


def write_lines(c, left, right, y, n=3, gap=0.85 * cm):
    c.setStrokeColor(HexColor("#cbd5e0"))
    c.setDash(2, 2)
    for _ in range(n):
        c.line(left, y, right, y)
        y -= gap
    c.setDash()
    return y


def draw_relevant_formulas(c, left, right, y) -> float:
    """
    נוסחאות רלוונטיות מהדף הרשמי לתרגילי המבחן:
    חוקי חזקות ושורשים + חוק הפילוג + המרת אורך (ק״מ↔מטר).
    מחזיר את ה־y מתחת לתיבה.
    """
    power_formulas = [
        r"a^{0} = 1",
        r"a^{1} = a",
        r"a^{-n} = \frac{1}{a^{n}}",
        r"a^{m} \cdot a^{n} = a^{m+n}",
        r"\frac{a^{m}}{a^{n}} = a^{m-n}",
        r"(a^{m})^{n} = (a^{n})^{m} = a^{m \cdot n}",
        r"a^{m} \cdot b^{m} = (ab)^{m}",
        r"\frac{a^{m}}{b^{m}} = \left(\frac{a}{b}\right)^{m} = \left(\frac{b}{a}\right)^{-m}",
        r"a^{\frac{m}{n}} = \sqrt[n]{a^{m}} = (\sqrt[n]{a})^{m}",
    ]
    extra_formulas = [
        r"a(b + c) = ab + ac",
        r"1\,\mathrm{km} = 1000\,\mathrm{m}",
        r"1\,\mathrm{m} = 0.001\,\mathrm{km}",
    ]

    box_top = y
    box_h = 5.85 * cm
    box_bottom = box_top - box_h

    c.setStrokeColor(LINE)
    c.setFillColor(HexColor("#f7fafc"))
    c.setLineWidth(1)
    c.roundRect(left, box_bottom, right - left, box_h, 6, fill=1, stroke=1)

    # כותרת התיבה
    c.setFillColor(NAVY)
    c.setFont(FONT_BOLD, 10)
    c.drawRightString(right - 0.35 * cm, box_top - 0.4 * cm, he("נוסחאות רלוונטיות למבחן — מתוך דף הנוסחאות של מה״ט"))
    c.setFont(FONT_REG, 7.5)
    c.setFillColor(GRAY)
    c.drawRightString(
        right - 0.35 * cm,
        box_top - 0.75 * cm,
        he("חוקי חזקות ושורשים  |  חוק הפילוג  |  המרת אורך  |  אין צורך בכפל מקוצר"),
    )

    # רשת 3×3 — חוקי חזקות ושורשים
    cols, rows = 3, 3
    margin_x = 0.3 * cm
    grid_top = box_top - 1.0 * cm
    grid_bottom = box_bottom + 1.55 * cm
    grid_left = left + margin_x
    grid_right = right - margin_x
    cell_w = (grid_right - grid_left) / cols
    cell_h = (grid_top - grid_bottom) / rows

    for idx, latex in enumerate(power_formulas):
        r = idx // cols
        col = idx % cols
        col_from_right = cols - 1 - col
        cx = grid_left + (col_from_right + 0.5) * cell_w
        cy = grid_top - (r + 0.55) * cell_h
        # נוסחאות ארוכות יותר בשורה התחתונה — גופן קטן יותר
        fs = 9 if idx >= 5 else 10.5
        img = formula_image(latex, fontsize=fs)
        max_w = cell_w - 0.2 * cm
        w, h = formula_size(img, max_w, scale_px=0.36)
        c.drawImage(img, cx - w / 2, cy - h / 2, width=w, height=h, mask="auto")

    # קו מפריד + שורת נוסחאות נוספות (פילוג + המרות)
    sep_y = box_bottom + 1.35 * cm
    c.setStrokeColor(LINE)
    c.setLineWidth(0.6)
    c.line(left + 0.35 * cm, sep_y, right - 0.35 * cm, sep_y)

    c.setFillColor(NAVY)
    c.setFont(FONT_BOLD, 8)
    c.drawRightString(right - 0.35 * cm, sep_y - 0.32 * cm, he("חוק הפילוג והמרת אורך (רלוונטי לתרגילים במבחן)"))

    extra_top = sep_y - 0.55 * cm
    extra_bottom = box_bottom + 0.2 * cm
    extra_h = extra_top - extra_bottom
    for idx, latex in enumerate(extra_formulas):
        col_from_right = cols - 1 - idx
        cx = grid_left + (col_from_right + 0.5) * cell_w
        cy = extra_bottom + extra_h * 0.45
        img = formula_image(latex, fontsize=11)
        max_w = cell_w - 0.2 * cm
        w, h = formula_size(img, max_w, scale_px=0.36)
        c.drawImage(img, cx - w / 2, cy - h / 2, width=w, height=h, mask="auto")

    return box_bottom - 0.4 * cm



def q_title(c, right, y, text_he: str):
    c.setFillColor(NAVY)
    c.setFont(FONT_BOLD, 12)
    c.drawRightString(right, y, he(text_he))
    y -= 0.35 * cm
    c.setStrokeColor(LINE)
    c.setLineWidth(0.7)
    c.line(1.8 * cm, y, right, y)
    return y - 0.5 * cm


# ---------------------------------------------------------------------------
# מבחן
# ---------------------------------------------------------------------------
def write_exam():
    path = OUT_DIR / "מבחן_פרקים_1-2_טכניקה_חזקות.pdf"
    c = canvas.Canvas(str(path), pagesize=A4)
    page = [1]
    title = "מבחן מה״ט — טכניקה אלגברית | חזקות ושורשים"
    right = PAGE_W - 1.8 * cm
    left = 1.8 * cm

    # כותרת
    c.setFillColor(NAVY)
    c.rect(0, PAGE_H - 3.2 * cm, PAGE_W, 3.2 * cm, fill=1, stroke=0)
    c.setFillColor(white)
    draw_centered_rtl_flow(
        c,
        PAGE_H - 1.15 * cm,
        [
            ("he", "מבחן במתמטיקה — שאלון"),
            ("ltr", " 99913"),
        ],
        font=FONT_BOLD,
        size=16,
        color=white,
        gap=0,
    )
    c.setFont(FONT_REG, 11)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 1.85 * cm, he("נושאים: טכניקה אלגברית  •  חזקות, שורשים, מידות וכתיבה מדעית"))
    c.setFont(FONT_REG, 10)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 2.55 * cm, he("רמת קושי: שאלות בסגנון בחינות מה״ט — הרמה הגבוהה ביותר"))

    y = PAGE_H - 3.9 * cm

    # פרטי תלמיד
    c.setStrokeColor(LINE)
    c.setFillColor(LIGHT)
    c.roundRect(left, y - 2.35 * cm, PAGE_W - 3.6 * cm, 2.5 * cm, 6, fill=1, stroke=1)
    c.setFillColor(black)
    draw_he(c, "שם התלמיד/ה: ________________________________", right - 0.3 * cm, y - 0.55 * cm, FONT_BOLD, 12)
    draw_he(c, "תעודת זהות: ______________________     כיתה/קבוצה: ______________", right - 0.3 * cm, y - 1.25 * cm, FONT_REG, 11)
    draw_he(c, "תאריך: ____ / ____ / ________", right - 0.3 * cm, y - 1.95 * cm, FONT_REG, 11)

    y -= 3.0 * cm
    c.setFillColor(NAVY)
    draw_rtl_flow(
        c,
        right,
        y,
        [
            ("he", "משך המבחן: שעתיים —"),
            ("ltr", " 120 "),
            ("he", "דקות"),
        ],
        font=FONT_BOLD,
        size=11,
        color=NAVY,
        gap=0,
    )
    c.setFont(FONT_BOLD, 11)
    c.setFillColor(NAVY)
    # סה״כ בצד שמאל — מספר ב־LTR
    draw_rtl_flow(
        c,
        left + 4.2 * cm,
        y,
        [("he", "סה״כ:"), ("ltr", " 100 "), ("he", "נקודות")],
        font=FONT_BOLD,
        size=11,
        color=NAVY,
        gap=0,
    )

    y -= 0.55 * cm
    c.setFillColor(GRAY)
    draw_he(c, "הוראות: ענו על כל ארבע השאלות. יש להציג דרך פתרון מלאה ומסודרת.", right, y, size=9)
    y -= 0.4 * cm
    draw_he(c, "בסעיפים שבהם מצוין \"ללא מחשבון\" — אין להשתמש במחשבון. בשאר הסעיפים מותר מחשבון מדעי.", right, y, size=9)
    y -= 0.4 * cm
    draw_he(c, "שימו לב לניקוד המדויק של כל סעיף. אין קשר בין שאלות, אלא אם צוין במפורש.", right, y, size=9)
    y -= 0.4 * cm
    draw_he(c, "הערה: במבחן זה אין צורך בנוסחאות הכפל המקוצר או בפירוק טרינום.", right, y, size=9, color=NAVY)

    y -= 0.45 * cm
    c.setStrokeColor(LINE)
    c.setLineWidth(1.2)
    c.line(left, y, right, y)
    y -= 0.45 * cm

    # נוסחאות רלוונטיות מדף מה״ט
    y = draw_relevant_formulas(c, left, right, y)

    # ===== שאלה 1 — מכנה משותף אמיתי (לא צמצום נפרד של כל שבר) =====
    y = draw_q_heading(c, right, y, 1, 25, "טכניקה אלגברית: שברים אלגבריים")
    c.setFillColor(black)
    draw_he(c, "נתון הביטוי:", right, y)
    y -= 0.2 * cm
    y = draw_formula(c, r"\frac{5}{x + 2} - \frac{3}{x - 2}", y, fontsize=15)
    y -= 0.2 * cm

    draw_section_head(c, "א", "8", "כתבו את תחום ההגדרה של x.", right, y)
    y = write_lines(c, left, right, y - 1.25 * cm, n=1, gap=0.45 * cm)
    y -= 0.3 * cm

    draw_section_head(c, "ב", "12", "פשטו את הביטוי לצורה המצומצמת ביותר — בעזרת מכנה משותף.", right, y)
    y = write_lines(c, left, right, y - 1.55 * cm, n=1, gap=0.45 * cm)
    y -= 0.3 * cm

    draw_section_head(c, "ג", "5", "מה יהיה ערך הביטוי כאשר:", right, y)
    y -= 0.15 * cm
    y = draw_formula(c, r"x = 4", y, fontsize=13)
    y = write_lines(c, left, right, y - 0.85 * cm, n=1, gap=0.45 * cm)
    y -= 0.5 * cm

    # ===== שאלה 2 — גורם משותף, פילוג+כינוס, חילוק שברים =====
    # הוסרה הצבה כפולה (הייתה גם בש1ג); א3 הוחלף מגורם משותף נוסף לפילוג+כינוס
    y = ensure_space(c, y, 13 * cm, title, page, "מבחן")
    y = draw_q_heading(c, right, y, 2, 20, "גורם משותף, חוק הפילוג וחילוק שברים")
    c.setFillColor(black)

    draw_section_head(c, "א", "9", "שלוש נקודות לכל סעיף:", right, y)
    y -= 0.4 * cm
    draw_he(c, "א1–א2: פרקו לגורמים על ידי הוצאת גורם משותף בלבד.", right, y, size=10)
    y -= 0.35 * cm
    for lab, latex in [
        ("א1.", r"6xy^{2} - 18x^{2}y ="),
        ("א2.", r"10m^{2}n - 15mn^{2} ="),
    ]:
        draw_he(c, lab, right, y, FONT_BOLD, 10)
        y -= 0.08 * cm
        y = draw_formula(c, latex, y, fontsize=14)
        y -= 0.7 * cm

    draw_he(c, "א3: פתחו סוגריים וכנסו איברים דומים:", right, y, size=10)
    y -= 0.2 * cm
    draw_he(c, "א3.", right, y, FONT_BOLD, 10)
    y -= 0.08 * cm
    y = draw_formula(c, r"3x(2x - 4) + 5x =", y, fontsize=14)
    y -= 0.55 * cm

    y = ensure_space(c, y, 8 * cm, title, page, "מבחן")
    draw_he(c, "ב. נתון הביטוי:", right, y)
    y -= 0.15 * cm
    y = draw_formula(c, r"\frac{4x}{x - 6} : \frac{1}{2x - 12}", y, fontsize=15)
    y -= 0.25 * cm

    draw_section_head(c, "ב1", "8", "פשטו את הביטוי ככל האפשר.", right, y)
    y = write_lines(c, left, right, y - 1.15 * cm, n=1, gap=0.45 * cm)
    y -= 0.28 * cm

    draw_section_head(c, "ב2", "3", "כתבו את תחום ההגדרה של x.", right, y)
    y = write_lines(c, left, right, y - 1.0 * cm, n=1, gap=0.45 * cm)
    y -= 0.45 * cm

    # ===== שאלה 3 — השוואה, פירוק שורשים, תחום שורש, פישוט חזקות =====
    y = ensure_space(c, y, 13 * cm, title, page, "מבחן")
    y = draw_q_heading(c, right, y, 3, 30, "חזקות, שורשים ופישוט")
    c.setFillColor(black)
    draw_he(c, "פתרו את הסעיפים הבאים. אין קשר בין הסעיפים.", right, y, size=10)
    y -= 0.38 * cm
    draw_he(c, "יש להציג חישובים מפורטים. בסעיפים א'–ד' — ללא מחשבון.", right, y, size=10)
    y -= 0.5 * cm

    draw_section_head(c, "א", "8", "השלימו במקום סימן השאלה אחד מהסימנים הבאים — בעזרת חוקי חזקות:", right, y)
    y -= 0.35 * cm
    draw_compare_choice_line(c, y)
    y -= 0.28 * cm
    y = draw_formula(c, r"32^{60}\ \ ?\ \ 16^{80}", y, fontsize=15)
    y = write_lines(c, left, right, y - 1.0 * cm, n=1, gap=0.45 * cm)
    y -= 0.3 * cm

    draw_section_head(c, "ב", "8", "פשטו את הביטוי ככל שניתן — פירוק שורשים וכינוס:", right, y)
    y -= 0.18 * cm
    y = draw_formula(c, r"\sqrt{48} + \sqrt{75} =", y, fontsize=15)
    y = write_lines(c, left, right, y - 1.0 * cm, n=1, gap=0.45 * cm)
    y -= 0.3 * cm

    draw_section_head(c, "ג", "4", "כתבו את תחום ההגדרה של x.", right, y)
    y -= 0.15 * cm
    y = draw_formula(c, r"\sqrt{2x - 8}", y, fontsize=14)
    y = write_lines(c, left, right, y - 0.95 * cm, n=1, gap=0.45 * cm)
    y -= 0.3 * cm

    y = ensure_space(c, y, 7 * cm, title, page, "מבחן")
    draw_section_head(c, "ד", "10", "פשטו את הביטוי ככל שניתן, בעזרת חוקי חזקות בלבד:", right, y)
    y -= 0.18 * cm
    y = draw_formula(c, r"\frac{72 \cdot 8^{72} - 8^{74}}{8^{71} - 4 \cdot 8^{70}}", y, fontsize=15)
    y = write_lines(c, left, right, y - 0.35 * cm, n=3)
    y -= 0.3 * cm

    # ===== שאלה 4 — פישוט משולב, הצגה מדעית, המרות, מעריך שבר =====
    y = ensure_space(c, y, 13 * cm, title, page, "מבחן")
    y = draw_q_heading(c, right, y, 4, 25, "חזקות, שורשים, המרות וכתיבה מדעית")
    c.setFillColor(black)

    draw_section_head(c, "א", "8", "פשטו את הביטוי בעזרת חוקי החזקות והשורשים — ללא מחשבון.", right, y)
    y -= 0.35 * cm
    draw_he(c, "הניחו שמספר M שונה מאפס.", right, y, size=9.5)
    y -= 0.22 * cm
    y = draw_formula(
        c,
        r"A = \frac{(8M^{5})^{2} \cdot \sqrt{81} \cdot (2M)^{-2}}{(4M^{2})^{3} \cdot \sqrt{16M^{8}}}",
        y,
        fontsize=14,
    )
    y = write_lines(c, left, right, y - 0.3 * cm, n=2, gap=0.7 * cm)
    y -= 0.3 * cm

    y = ensure_space(c, y, 10 * cm, title, page, "מבחן")
    draw_section_head(c, "ב", "5", "הציבו את הערך הבא בביטוי שקיבלתם בסעיף א' וחשבו את ערכו.", right, y)
    y -= 0.12 * cm
    y = draw_formula(c, r"M = -1.25", y, fontsize=13)
    draw_rtl_flow(
        c,
        right,
        y,
        [("he", "עגלו ל־"), ("ltr", "2 "), ("he", "ספרות אחרי הנקודה, והציגו גם בהצגה מדעית")],
        size=10,
        gap=0,
    )
    y -= 0.35 * cm
    draw_rtl_flow(
        c,
        right,
        y,
        [
            ("he", "כאשר המקדם בין"),
            ("ltr", " 1 "),
            ("he", "ל־"),
            ("ltr", "10 "),
            ("he", "בערך מוחלט, ובדיוק של"),
            ("ltr", " 2 "),
            ("he", "ספרות אחרי הנקודה."),
        ],
        size=10,
        gap=0,
    )
    y = write_lines(c, left, right, y - 1.0 * cm, n=1, gap=0.45 * cm)
    y -= 0.3 * cm

    draw_section_head(c, "ג", "6", "המרת מידות וכתיבה מדעית:", right, y)
    y -= 0.35 * cm
    draw_he(c, "כוכב נמצא במרחק:", right, y, size=10.5)
    y -= 0.15 * cm
    y = draw_formula(c, r"4.2 \times 10^{13}\ \mathrm{km}", y, fontsize=14)
    draw_he(c, "המירו את המרחק למטרים, וכתבו את התשובה בכתיבה מדעית", right, y, size=10)
    y -= 0.35 * cm
    draw_rtl_flow(
        c,
        right,
        y,
        [
            ("he", "כאשר המקדם בין"),
            ("ltr", " 1 "),
            ("he", "ל־"),
            ("ltr", "10 "),
            ("he", "בערך מוחלט, ובדיוק של"),
            ("ltr", " 2 "),
            ("he", "ספרות אחרי הנקודה."),
        ],
        size=10,
        gap=0,
    )
    y = write_lines(c, left, right, y - 1.0 * cm, n=1, gap=0.45 * cm)
    y -= 0.3 * cm

    y = ensure_space(c, y, 5.5 * cm, title, page, "מבחן")
    draw_section_head(c, "ד", "6", "פשטו את הביטוי בעזרת מעריך שבר — ללא מחשבון.", right, y)
    y -= 0.3 * cm
    draw_he(c, "הניחו ש־x גדול או שווה לאפס.", right, y, size=9.5)
    y -= 0.2 * cm
    y = draw_formula(c, r"\left(8x^{6}\right)^{\frac{2}{3}} =", y, fontsize=15)
    y = write_lines(c, left, right, y - 1.0 * cm, n=1, gap=0.45 * cm)

    # סה״כ
    box_y = 1.75 * cm
    c.setStrokeColor(NAVY)
    c.setLineWidth(1)
    c.roundRect(left, box_y, PAGE_W - 3.6 * cm, 1.25 * cm, 5, fill=0, stroke=1)
    draw_centered_rtl_flow(
        c,
        box_y + 0.72 * cm,
        [
            ("he", "סה״כ המבחן:"),
            ("ltr", " 100 "),
            ("he", "נקודות"),
            ("ltr", "  |  "),
            ("he", "בהצלחה"),
            ("ltr", "!"),
        ],
        font=FONT_BOLD,
        size=10,
        color=NAVY,
    )
    c.setFont(FONT_REG, 9)
    c.setFillColor(GRAY)
    c.drawCentredString(PAGE_W / 2, box_y + 0.28 * cm, "25 + 20 + 30 + 25 = 100")
    draw_page_footer(c, page[0], "מבחן")
    c.save()
    return path


# ---------------------------------------------------------------------------
# פתרונות
# ---------------------------------------------------------------------------
def write_solutions():
    path = OUT_DIR / "פתרונות_מבחן_פרקים_1-2.pdf"
    c = canvas.Canvas(str(path), pagesize=A4)
    page = [1]
    title = "פתרונות מלאים — מבחן פרקים 1–2"
    right = PAGE_W - 1.8 * cm
    left = 1.8 * cm

    c.setFillColor(NAVY)
    c.rect(0, PAGE_H - 2.6 * cm, PAGE_W, 2.6 * cm, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont(FONT_BOLD, 15)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 1.1 * cm, he("קובץ פתרונות — מבחן מה״ט"))
    c.setFont(FONT_REG, 10)
    # כותרת משנה עם מספר — בלי ערבוב סוגריים
    draw_centered_rtl_flow(
        c,
        PAGE_H - 1.8 * cm,
        [
            ("he", "טכניקה אלגברית  •  חזקות, שורשים וכתיבה מדעית"),
            ("ltr", "  |  "),
            ("he", "סה״כ"),
            ("ltr", " 100 "),
            ("he", "נקודות"),
        ],
        font=FONT_REG,
        size=10,
        color=white,
    )

    y = PAGE_H - 3.3 * cm

    # --- ש1 ---
    draw_sol_heading(c, right, y, 1, 25)
    y -= 0.45 * cm
    c.setFillColor(black)

    draw_section_head(c, "א", "8", "המכנים אינם מתאפסים:", right, y)
    y -= 0.12 * cm
    y = draw_formula(c, r"x + 2 \neq 0 \quad \Rightarrow \quad x \neq -2", y, fontsize=12)
    y -= 0.05 * cm
    y = draw_formula(c, r"x - 2 \neq 0 \quad \Rightarrow \quad x \neq 2", y, fontsize=12)
    y = draw_answer(c, r"x \neq 2,\ x \neq -2", right, y)

    draw_section_head(c, "ב", "12", "מכנה משותף:", right, y)
    y -= 0.12 * cm
    y = draw_formula(
        c,
        r"\frac{5}{x+2}-\frac{3}{x-2}=\frac{5(x-2)-3(x+2)}{(x+2)(x-2)}=\frac{5x-10-3x-6}{x^{2}-4}=\frac{2x-16}{x^{2}-4}",
        y,
        fontsize=11,
    )
    y -= 0.05 * cm
    y = draw_formula(c, r"\frac{2(x-8)}{(x+2)(x-2)}", y, fontsize=12)
    y = draw_answer(c, r"\frac{2(x-8)}{(x+2)(x-2)}", right, y)

    draw_section_head(c, "ג", "5", "הצבה:", right, y)
    y -= 0.12 * cm
    y = draw_formula(c, r"\frac{2(4-8)}{(4+2)(4-2)}=\frac{2\cdot(-4)}{6\cdot 2}=\frac{-8}{12}=-\frac{2}{3}", y, fontsize=12)
    y = draw_answer(c, r"-\frac{2}{3}", right, y)
    y -= 0.15 * cm

    # --- ש2 ---
    y = ensure_space(c, y, 11 * cm, title, page, "פתרונות")
    draw_sol_heading(c, right, y, 2, 20)
    y -= 0.5 * cm
    c.setFillColor(black)

    draw_section_head(c, "א1", "3", "", right, y, size=10.5)
    y -= 0.1 * cm
    y = draw_formula(c, r"6xy^{2} - 18x^{2}y = 6xy(y - 3x)", y, fontsize=13)
    draw_section_head(c, "א2", "3", "", right, y, size=10.5)
    y -= 0.1 * cm
    y = draw_formula(c, r"10m^{2}n - 15mn^{2} = 5mn(2m - 3n)", y, fontsize=13)
    draw_section_head(c, "א3", "3", "פילוג וכינוס:", right, y, size=10.5)
    y -= 0.1 * cm
    y = draw_formula(c, r"3x(2x-4)+5x = 6x^{2}-12x+5x = 6x^{2}-7x", y, fontsize=12)
    y = draw_answer(c, r"6x^{2}-7x", right, y)

    draw_section_head(c, "ב1", "8", "חילוק שברים = כפל בהופכי, והוצאת גורם משותף:", right, y)
    y -= 0.12 * cm
    y = draw_formula(c, r"2x - 12 = 2(x - 6)", y, fontsize=12)
    y -= 0.05 * cm
    y = draw_formula(
        c,
        r"\frac{4x}{x - 6} : \frac{1}{2(x - 6)} = \frac{4x}{x - 6} \cdot \frac{2(x - 6)}{1} = 8x",
        y,
        fontsize=12,
    )
    y = draw_answer(c, r"8x", right, y)

    draw_section_head(c, "ב2", "3", "תחום ההגדרה — המכנים אינם מתאפסים:", right, y)
    y -= 0.12 * cm
    y = draw_formula(c, r"x - 6 \neq 0 \quad \Rightarrow \quad x \neq 6", y, fontsize=12)
    draw_he(c, "גם במכנה השני מתקבל אותו תנאי.", right, y, size=9.5)
    y -= 0.35 * cm
    y = draw_answer(c, r"x \neq 6", right, y)
    y -= 0.15 * cm

    # --- ש3 ---
    y = ensure_space(c, y, 13 * cm, title, page, "פתרונות")
    draw_sol_heading(c, right, y, 3, 30)
    y -= 0.5 * cm
    c.setFillColor(black)

    draw_section_head(c, "א", "8", "מעבר לבסיס זהה:", right, y)
    y -= 0.12 * cm
    y = draw_formula(c, r"32^{60} = (2^{5})^{60} = 2^{300}", y, fontsize=13)
    y -= 0.05 * cm
    y = draw_formula(c, r"16^{80} = (2^{4})^{80} = 2^{320}", y, fontsize=13)
    y -= 0.05 * cm
    y = draw_formula(c, r"2^{300} < 2^{320} \quad \Rightarrow \quad 32^{60} < 16^{80}", y, fontsize=13)
    y = draw_answer(c, r"<", right, y, fontsize=16)

    draw_section_head(c, "ב", "8", "פירוק שורשים וכינוס:", right, y)
    y -= 0.12 * cm
    y = draw_formula(c, r"\sqrt{48}=\sqrt{16\cdot 3}=4\sqrt{3},\quad \sqrt{75}=\sqrt{25\cdot 3}=5\sqrt{3}", y, fontsize=12)
    y -= 0.05 * cm
    y = draw_formula(c, r"4\sqrt{3}+5\sqrt{3}=9\sqrt{3}", y, fontsize=13)
    y = draw_answer(c, r"9\sqrt{3}", right, y)

    draw_section_head(c, "ג", "4", "תחום ההגדרה של x:", right, y)
    y -= 0.12 * cm
    y = draw_formula(c, r"2x-8\geq 0 \quad \Rightarrow \quad x\geq 4", y, fontsize=13)
    y = draw_answer(c, r"x\geq 4", right, y)

    y = ensure_space(c, y, 8 * cm, title, page, "פתרונות")
    draw_section_head(c, "ד", "10", "הוצאת חזקה משותפת:", right, y)
    y -= 0.12 * cm
    y = draw_formula(c, r"72\cdot 8^{72} - 8^{74} = 8^{72}(72 - 8^{2}) = 8^{72}(72-64) = 8^{73}", y, fontsize=11)
    y -= 0.08 * cm
    y = draw_formula(c, r"8^{71} - 4\cdot 8^{70} = 8^{70}(8 - 4) = 4\cdot 8^{70}", y, fontsize=12)
    y -= 0.08 * cm
    y = draw_formula(
        c,
        r"\frac{8^{73}}{4\cdot 8^{70}} = \frac{(2^{3})^{73}}{2^{2}\cdot (2^{3})^{70}} = \frac{2^{219}}{2^{212}} = 2^{7} = 128",
        y,
        fontsize=11,
    )
    y = draw_answer(c, r"128", right, y)
    y -= 0.15 * cm

    # --- ש4 ---
    y = ensure_space(c, y, 13 * cm, title, page, "פתרונות")
    draw_sol_heading(c, right, y, 4, 25)
    y -= 0.5 * cm
    c.setFillColor(black)

    draw_section_head(c, "א", "8", "פישוט שלב־אחר־שלב:", right, y)
    y -= 0.12 * cm
    y = draw_formula(c, r"(8M^{5})^{2} = 64M^{10},\quad \sqrt{81}=9,\quad (2M)^{-2}=\frac{1}{4M^{2}}", y, fontsize=11)
    y -= 0.05 * cm
    y = draw_formula(c, r"(4M^{2})^{3} = 64M^{6},\quad \sqrt{16M^{8}} = 4M^{4}", y, fontsize=11)
    y -= 0.05 * cm
    y = draw_formula(
        c,
        r"A = \frac{64M^{10}\cdot 9\cdot \frac{1}{4M^{2}}}{64M^{6}\cdot 4M^{4}} = \frac{144M^{8}}{256M^{10}} = \frac{9}{16M^{2}}",
        y,
        fontsize=12,
    )
    y = draw_answer(c, r"\frac{9}{16M^{2}}", right, y)

    draw_section_head(c, "ב", "5", "הצבה, עיגול והצגה מדעית:", right, y)
    y -= 0.12 * cm
    y = draw_formula(c, r"A = \frac{9}{16\cdot(-1.25)^{2}} = \frac{9}{16\cdot 1.5625} = \frac{9}{25} = 0.36", y, fontsize=12)
    y = draw_answer(c, r"0.36 = 3.60 \times 10^{-1}", right, y)

    draw_section_head(c, "ג", "6", "המרה מקילומטרים למטרים:", right, y)
    y -= 0.12 * cm
    y = draw_formula(
        c,
        r"4.2 \times 10^{13}\ \mathrm{km} = 4.2 \times 10^{13} \times 10^{3}\ \mathrm{m} = 4.20 \times 10^{16}\ \mathrm{m}",
        y,
        fontsize=11,
    )
    y = draw_answer(c, r"4.20 \times 10^{16}\ \mathrm{m}", right, y)

    draw_section_head(c, "ד", "6", "מעריך שבר:", right, y)
    y -= 0.12 * cm
    y = draw_formula(
        c,
        r"\left(8x^{6}\right)^{\frac{2}{3}} = 8^{\frac{2}{3}}\cdot (x^{6})^{\frac{2}{3}} = (2^{3})^{\frac{2}{3}}\cdot x^{4} = 2^{2}\cdot x^{4} = 4x^{4}",
        y,
        fontsize=11,
    )
    y = draw_answer(c, r"4x^{4}", right, y)
    y -= 0.25 * cm

    # סיכום
    y = ensure_space(c, y, 8.2 * cm, title, page, "פתרונות")
    c.setFillColor(LIGHT)
    c.setStrokeColor(LINE)
    box_h = 7.3 * cm
    c.roundRect(left, y - box_h, PAGE_W - 3.6 * cm, box_h + 0.2 * cm, 6, fill=1, stroke=1)
    c.setFillColor(NAVY)
    c.setFont(FONT_BOLD, 11)
    c.drawRightString(right - 0.3 * cm, y - 0.4 * cm, he("סיכום תשובות סופיות"))
    c.setFillColor(black)

    yy = y - 0.95 * cm

    def row(label, latex, yy):
        draw_he(c, label, right - 0.3 * cm, yy, size=9)
        lw = c.stringWidth(he(label), FONT_REG, 9)
        draw_formula_right(c, latex, right - 0.3 * cm - lw - 8, yy, fontsize=9.5, max_width=11 * cm)
        return yy - 0.58 * cm

    yy = row("שאלה 1א:", r"x\neq 2,\ x\neq -2", yy)
    yy = row("שאלה 1ב:", r"\frac{2(x-8)}{(x+2)(x-2)}", yy)
    yy = row("שאלה 1ג:", r"-\frac{2}{3}", yy)
    yy = row("שאלה 2א:", r"6xy(y-3x);\ 5mn(2m-3n);\ 6x^{2}-7x", yy)
    yy = row("שאלה 2ב:", r"8x;\ x\neq 6", yy)
    yy = row("שאלה 3:", r"<;\ 9\sqrt{3};\ x\geq 4;\ 128", yy)
    yy = row("שאלה 4:", r"\frac{9}{16M^{2}};\ 0.36=3.60\times10^{-1};\ 4.20\times10^{16}\,\mathrm{m};\ 4x^{4}", yy)

    c.setFont(FONT_BOLD, 10)
    c.setFillColor(NAVY)
    draw_centered_rtl_flow(
        c,
        y - box_h + 0.35 * cm,
        [
            ("he", "ניקוד:"),
            ("ltr", "  25 + 20 + 30 + 25 = 100"),
        ],
        font=FONT_BOLD,
        size=10,
        color=NAVY,
    )

    draw_page_footer(c, page[0], "פתרונות")
    c.save()
    return path


if __name__ == "__main__":
    exam = write_exam()
    sols = write_solutions()
    print("EXAM:", exam)
    print("SOLS:", sols)
