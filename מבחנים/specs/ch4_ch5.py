#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""מבחן תרגול מקורי בסגנון מה״ט, פרקים 4 ו-5.

ללא כפל מקוצר ופירוק טרינום. תוצאות מקורבות: שתי ספרות אחרי הנקודה.

מקורות לסגנון ולכיסוי: תיקיות פרקים 4 ו-5, עצי הנושאים המעודכנים,
ומאגרי השאלות המקבילים בתיקיית תרגילי בחינות מהט.
תיבת הנוסחאות נבדקה מול עמוד 1 בדף הנוסחאות המקומי.
הפקה: python3 מבחנים/generate_exam.py --spec ch4_ch5
"""
from __future__ import annotations

from reportlab.lib.units import cm
from lib.models import AnswerRow, ExamSpec, FormulaBox, Question, Section


def body(*items, lines=3):
    """עברית בשורה נפרדת; מתמטיקה באמצעות מנוע הנוסחאות."""
    def draw(pdf, y):
        for kind, value in items:
            if kind == 'he':
                pdf.draw_he(value, pdf.right, y - 0.12 * cm, size=10)
                y -= 0.55 * cm
            else:
                y = pdf.draw_formula(value, y, fontsize=13)
        return pdf.write_lines(y - 0.22 * cm, n=lines, gap=0.58 * cm)
    return draw


def solution(*items, answer):
    def draw(pdf, y):
        y -= 0.1 * cm
        for kind, value in items:
            if kind == 'he':
                pdf.draw_he(value, pdf.right, y - 0.1 * cm, size=9.5)
                y -= 0.48 * cm
            else:
                y = pdf.draw_formula(value, y, fontsize=11)
        return pdf.draw_answer(answer, y - 0.15 * cm, fontsize=11)
    return draw


def build_spec() -> ExamSpec:
    q1 = Question(1, 25, 'משוואות, תחום הצבה ובדיקת פתרונות', new_page=True, sections=[
        Section('א', 7, 'פתרו את המשוואה ובדקו בהצבה.',
            draw_body=body(('math', r'\frac{3x-2}{4}-\frac{x+1}{6}=\frac{x-5}{3}+2'), lines=4),
            answer_latex=r'x=4', solution_title_he='כפל במכנה משותף ובדיקה',
            draw_solution=solution(
                ('math', r'3(3x-2)-2(x+1)=4(x-5)+24'),
                ('math', r'9x-6-2x-2=4x+4\quad\Rightarrow\quad 3x=12'),
                ('he', 'בדיקה: שני האגפים שווים לאחר ההצבה.'),
                ('math', r'\frac{12-2}{4}-\frac{4+1}{6}=\frac{5}{3}=\frac{4-5}{3}+2'),
                answer=r'x=4'), solution_height_cm=6),
        Section('ב', 10, 'קבעו תחום הצבה, פתרו ובדקו בהצבה.',
            draw_body=body(('math', r'\frac{2x+1}{x-2}=3+\frac{7}{2(x-2)}'), lines=5),
            answer_latex=r'x=3.50\quad (x\ne2)', solution_title_he='תחום הצבה ומכנה משותף',
            draw_solution=solution(
                ('math', r'x-2\ne0\quad\Rightarrow\quad x\ne2'),
                ('he', 'כופלים במכנה המשותף ומפעילים את חוק הפילוג:'),
                ('math', r'2(2x+1)=6(x-2)+7'),
                ('math', r'4x+2=6x-5\quad\Rightarrow\quad 2x=7\quad\Rightarrow\quad x=3.50'),
                ('he', 'הפתרון בתחום ההצבה. בדיקה במשוואה המקורית:'),
                ('math', r'\frac{2\cdot3.5+1}{3.5-2}=\frac{16}{3}=3+\frac{7}{2(3.5-2)}'),
                answer=r'x=3.50\quad (x\ne2)'), solution_height_cm=7),
        Section('ג', 8, 'פתרו באמצעות נוסחת השורשים ועגלו לשתי ספרות אחרי הנקודה.',
            draw_body=body(('math', r'3x^2-2(x+1)=12x-7'), lines=4),
            answer_latex=r'x_1\approx4.28,\quad x_2\approx0.39', solution_title_he='חוק הפילוג ונוסחת השורשים',
            draw_solution=solution(
                ('math', r'3x^2-2x-2=12x-7\quad\Rightarrow\quad 3x^2-14x+5=0'),
                ('math', r'a=3,\ b=-14,\ c=5,\quad \Delta=196-60=136'),
                ('math', r'x=\frac{14\pm\sqrt{136}}{6}=\frac{7\pm\sqrt{34}}{3}'),
                answer=r'x_1\approx4.28,\quad x_2\approx0.39'), solution_height_cm=5.5),
    ])
    q2 = Question(2, 25, 'מערכות משוואות ומספר הפתרונות', new_page=True, sections=[
        Section('א', 9, 'פתרו את המערכת ובדקו את הפתרון בשתי המשוואות.',
            draw_body=body(('math', r'6-2(4x-3y)=26'), ('math', r'\frac{x+2y}{3}=1'), lines=5),
            answer_latex=r'(x,y)=(-1,2)', solution_title_he='מערכת ממעלה ראשונה',
            draw_solution=solution(
                ('math', r'-8x+6y=20\quad\Rightarrow\quad -4x+3y=10'),
                ('math', r'x+2y=3\quad\Rightarrow\quad -4x-8y=-12'),
                ('he', 'מחסרים את המשוואות ומוצאים את שני הנעלמים.'),
                ('math', r'11y=22\quad\Rightarrow\quad y=2,\quad x=3-2\cdot2=-1'),
                ('math', r'6-2(-4-6)=26,\qquad \frac{-1+2\cdot2}{3}=1'),
                answer=r'(x,y)=(-1,2)'), solution_height_cm=6.5),
        Section('ב', 12, 'מצאו את כל פתרונות המערכת ובדקו כל זוג בהצבה.',
            draw_body=body(('math', r'y=x^2-3x-4'), ('math', r'2x-y=4'), lines=5),
            answer_latex=r'(x,y)=(0,-4),\ (5,6)', solution_title_he='מערכת מעורבת ומשוואה ריבועית חלקית',
            draw_solution=solution(
                ('math', r'y=2x-4\quad\Rightarrow\quad x^2-3x-4=2x-4'),
                ('math', r'x^2-5x=0\quad\Rightarrow\quad x(x-5)=0'),
                ('math', r'x=0\Rightarrow y=-4,\qquad x=5\Rightarrow y=6'),
                ('he', 'בדיקה בכל אחת משתי המשוואות:'),
                ('math', r'(0,-4):\quad -4=0^2-3\cdot0-4,\quad 2\cdot0-(-4)=4'),
                ('math', r'(5,6):\quad 6=25-15-4,\quad 2\cdot5-6=4'),
                answer=r'(x,y)=(0,-4),\ (5,6)'), solution_height_cm=7.5),
        Section('ג', 4, 'קבעו את קבוצת הפתרונות של כל משוואה ונמקו.',
            draw_body=body(('math', r'\mathrm{I}:\quad 2(3x-1)-4=6(x-1)'),
                           ('math', r'\mathrm{II}:\quad 2(3x-1)-4=6x-5'), lines=3),
            answer_latex=r'\mathrm{I}:\ x\in\mathbb{R};\qquad \mathrm{II}:\ \varnothing',
            solution_title_he='זהות לעומת סתירה',
            draw_solution=solution(
                ('math', r'\mathrm{I}:\quad 6x-6=6x-6\quad\Rightarrow\quad 0=0'),
                ('he', 'המשוואה הראשונה מתקיימת לכל מספר ממשי: אינסוף פתרונות.'),
                ('math', r'\mathrm{II}:\quad 6x-6=6x-5\quad\Rightarrow\quad -6=-5'),
                ('he', 'המשוואה השנייה מובילה לסתירה: אין פתרון.'),
                answer=r'\mathrm{I}:\ x\in\mathbb{R};\qquad \mathrm{II}:\ \varnothing'), solution_height_cm=5.5),
    ])
    q3 = Question(3, 25, 'שינוי נושא נוסחה ושברים', new_page=True, sections=[
        Section('א', 9, 'בטאו את גובה התיבה באמצעות שטח הפנים ושאר הממדים.',
            draw_body=body(('he', 'נתונה נוסחת שטח הפנים של תיבה. כל הממדים חיוביים.'),
                ('math', r'S=2(LW+LH+WH)'),
                ('he', 'האותיות מסמנות בהתאמה אורך, רוחב וגובה; שטח הפנים נמדד בסמ״ר.'),
                ('math', r'L\ [\mathrm{cm}],\quad W\ [\mathrm{cm}],\quad H\ [\mathrm{cm}]'), lines=4),
            answer_latex=r'H=\frac{S-2LW}{2(L+W)}', solution_title_he='הוצאת גורם משותף ובידוד הגובה',
            draw_solution=solution(
                ('math', r'\frac{S}{2}=LW+LH+WH'),
                ('math', r'\frac{S}{2}-LW=H(L+W)'),
                ('he', 'סכום האורך והרוחב חיובי ולכן מותר לחלק בו.'),
                ('he', 'לתיבה שגובהה חיובי נדרש גם ששטח הפנים גדול מפעמיים שטח הבסיס.'),
                ('math', r'S>2LW'),
                answer=r'H=\frac{S-2LW}{2(L+W)}'), solution_height_cm=6.5),
        Section('ב', 7, 'חשבו את גובה התיבה ועגלו לשתי ספרות אחרי הנקודה.',
            draw_body=body(('he', 'הציבו בנוסחה שבודדתם בסעיף הקודם את הנתונים הבאים:'),
                ('math', r'L=6.5\ \mathrm{cm},\quad W=4.5\ \mathrm{cm},\quad S=(58.5+22\sqrt{18})\ \mathrm{cm}^2'),
                ('he', 'ציינו יחידות בתשובתכם.'), lines=4),
            answer_latex=r'H\approx4.24\ \mathrm{cm}',
            solution_title_he='הצבת ביטוי המכיל שורש',
            draw_solution=solution(
                ('math', r'2LW=2\cdot6.5\cdot4.5=58.5,\quad 2(L+W)=22'),
                ('math', r'H=\frac{58.5+22\sqrt{18}-58.5}{22}=\sqrt{18}=3\sqrt{2}'),
                ('he', 'בדיקה: הצבת הגובה בנוסחת השטח מחזירה את הביטוי הנתון.'),
                ('math', r'S=58.5+22\cdot\sqrt{18}'),
                answer=r'H\approx4.24\ \mathrm{cm}'), solution_height_cm=5.5),
        Section('ג', 9, 'בטאו את מחיר היחידה כנושא הנוסחה, ואז חשבו אותו.',
            draw_body=body(('he', 'נתונה נוסחה לחישוב נקודת איזון. כל הגדלים חיוביים והמחיר גדול מהעלות.'),
                ('math', r'PQ=\frac{F}{1-\frac{V}{P}},\qquad P>V'),
                ('he', 'הסימונים להלן: מחיר ליחידה, עלות ליחידה, כמות והוצאות קבועות, בהתאמה.'),
                ('math', r'P,\quad V,\quad Q,\quad F'),
                ('he', 'הסכומים בש״ח והכמות ביחידות.'),
                ('he', 'לצורך החישוב המספרי נתון:'),
                ('math', r'Q=120,\quad V=18,\quad F=8640'), lines=4),
            answer_latex=r'P=V+\frac{F}{Q}=90', solution_title_he='פישוט שבר מורכב והצבה',
            draw_solution=solution(
                ('he', 'המחיר חיובי ושונה מהעלות, ולכן המכנים אינם מתאפסים.'),
                ('math', r'PQ\left(1-\frac{V}{P}\right)=F\quad\Rightarrow\quad PQ-QV=F'),
                ('math', r'Q(P-V)=F\quad\Rightarrow\quad P=V+\frac{F}{Q}'),
                ('math', r'P=18+\frac{8640}{120}=90'),
                ('he', 'המחיר הוא תשעים ש״ח ליחידה. בדיקה בנוסחה המקורית:'),
                ('math', r'90\cdot120=10800=\frac{8640}{1-18/90}'),
                answer=r'P=90\quad (P>18)'), solution_height_cm=7),
    ])
    q4 = Question(4, 25, 'שינוי נושא נוסחה עם חזקות ושורשים', new_page=True, sections=[
        Section('א', 9, 'בטאו את אורך המטוטלת וחשבו אותו לפי הנתונים.',
            draw_body=body(('he', 'תקופת תנודה של מטוטלת נתונה בנוסחה הבאה. כל הגדלים חיוביים.'),
                ('math', r'T=2\pi\sqrt{\frac{L}{g}}'),
                ('he', 'התקופה בשניות, האורך במטרים ותאוצת הכובד במטר לשנייה בריבוע.'),
                ('math', r'T=\sqrt{3}\ \mathrm{s},\quad g=9.8\ \mathrm{m/s^2}'),
                ('he', 'עגלו את האורך לשתי ספרות אחרי הנקודה.'), lines=3),
            answer_latex=r'L=\frac{gT^2}{4\pi^2}\approx0.74\ \mathrm{m}', solution_title_he='בידוד משתנה מתוך שורש',
            draw_solution=solution(
                ('math', r'\frac{T}{2\pi}=\sqrt{\frac{L}{g}}\quad\Rightarrow\quad\frac{T^2}{4\pi^2}=\frac{L}{g}'),
                ('math', r'L=\frac{gT^2}{4\pi^2}=\frac{9.8(\sqrt{3})^2}{4\pi^2}=\frac{29.4}{4\pi^2}'),
                ('he', 'משתמשים בערך פאי שבמחשבון ומעגלים רק בסוף.'),
                answer=r'L\approx0.74\ \mathrm{m}'), solution_height_cm=5.5),
        Section('ב', 8, 'בטאו את רדיוס הכדור וחשבו אותו לפי הנתון.',
            draw_body=body(('he', 'נפח כדור ורדיוסו החיובי מקיימים את הנוסחה:'),
                ('math', r'V=\frac{4}{3}\pi r^3,\qquad V=5000\ \mathrm{m}^3'),
                ('he', 'כתבו את הרדיוס במטרים ועגלו לשתי ספרות אחרי הנקודה.'), lines=3),
            answer_latex=r'r=\sqrt[3]{\frac{3V}{4\pi}}\approx10.61\ \mathrm{m}',
            solution_title_he='בידוד חזקה שלישית',
            draw_solution=solution(
                ('math', r'3V=4\pi r^3\quad\Rightarrow\quad r^3=\frac{3V}{4\pi}'),
                ('math', r'r=\sqrt[3]{\frac{3V}{4\pi}}=\sqrt[3]{\frac{15000}{4\pi}}'),
                ('he', 'מוציאים שורש שלישי. עבור נפח חיובי מתקבל רדיוס חיובי יחיד.'),
                answer=r'r\approx10.61\ \mathrm{m}'), solution_height_cm=5.5),
        Section('ג', 8, 'בטאו את רדיוס הגליל וחשבו אותו לפי הנתונים.',
            draw_body=body(('he', 'נפח גליל, רדיוסו וגובהו החיוביים מקיימים:'),
                ('math', r'V=\pi r^2h,\qquad h=3\ \mathrm{m},\quad V=\sqrt{360}\ \mathrm{m}^3'),
                ('he', 'כתבו את הרדיוס במטרים ועגלו לשתי ספרות אחרי הנקודה.'), lines=4),
            answer_latex=r'r=\sqrt{\frac{V}{\pi h}}\approx1.42\ \mathrm{m}',
            solution_title_he='בידוד ריבוע, הצבת שורש ועיגול',
            draw_solution=solution(
                ('math', r'r^2=\frac{V}{\pi h}\quad\Rightarrow\quad r=\sqrt{\frac{V}{\pi h}}'),
                ('he', 'בוחרים בשורש החיובי כי הרדיוס חיובי.'),
                ('math', r'r=\sqrt{\frac{\sqrt{360}}{3\pi}}\approx1.418861686\ \mathrm{m}'),
                ('he', 'הספרה השלישית אחרי הנקודה היא שמונה, ולכן מעגלים כלפי מעלה.'),
                answer=r'r\approx1.42\ \mathrm{m}'), solution_height_cm=6),
    ])
    questions = [q1,q2,q3,q4]
    return ExamSpec(
        exam_filename='מבחן_פרקים_4-5.pdf',
        solutions_filename='פתרונות_מבחן_פרקים_4-5.pdf',
        chapter_nums=[4,5],
        chapter_dirs=['4 - משוואות ממעלה ראשונה ושנייה, מערכת משוואות','5 - שינוי נושא הנוסחה'],
        topics_he='משוואות ומערכות משוואות  •  שינוי נושא הנוסחה',
        page_title_he='מבחן תרגול מה״ט - משוואות ושינוי נושא הנוסחה',
        main_title_segments=[('he','מבחן תרגול בסגנון מה״ט - שאלון'),('ltr',' 99913 ')],
        cover_notes=[
            'פרקים נכללים: משוואות ומערכות משוואות; שינוי נושא הנוסחה.',
            'המבחן אינו כולל כפל מקוצר או פירוק טרינום.',
            'המבחן כולל ארבע שאלות, כל אחת עשרים וחמש נקודות. יש לענות על כולן.',
            'פתרו במספרים ממשיים. יש לציין תחום הצבה כאשר נעלם מופיע במכנה.',
            'השתמשו בערך פאי שבמחשבון. אין לעגל תוצאות ביניים.',
            'בתשובות עשרוניות השאירו שתי ספרות אחרי הנקודה ועגלו לפי הספרה השלישית.',
            'אפשר להמשיך את הפתרון בדפים נוספים ולציין את מספר השאלה והסעיף.',
        ],
        formula_box=FormulaBox(
            formulas=[r'x_{1,2}=\frac{-b\pm\sqrt{b^2-4ac}}{2a}'],
            subtitle_he='נוסחת השורשים מיועדת למשוואה ריבועית שמקדם הריבוע בה אינו אפס'),
        questions=questions,
        summary_new_page=True,
        summary_rows=[AnswerRow(f'שאלה {q.number}, סעיף {s.letter}:',s.answer_latex)
                      for q in questions for s in q.sections],
    )
