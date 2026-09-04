# מחולל מבחני מה״ט — מדריך שימוש

מערכת ליצירת מבחן PDF + פתרונות באותה רמה, היקף ודיוק כמו מבחן פרקים 1–2.

## התקנה חד־פעמית

```bash
cd "/Users/amitay/Desktop/ort - math/mahat-Math"
python3 -m venv .venv_exam
source .venv_exam/bin/activate
pip install reportlab arabic-reshaper python-bidi matplotlib
```

## זרימת עבודה למבחן חדש (למשל פרקים 4+5)

### 1. סקירת חומר
```bash
source .venv_exam/bin/activate
python3 מבחנים/generate_exam.py --list
python3 מבחנים/generate_exam.py --brief 4 5
```

### 2. יצירת קובץ מפרט
```bash
python3 מבחנים/generate_exam.py --scaffold 4 5
# → מבחנים/specs/ch4_ch5.py
```

### 3. מילוי שאלות במפרט
ערוך `מבחנים/specs/ch4_ch5.py`:
- 4 שאלות, **100 נקודות**
- ניקוד מדויק לכל סעיף (סכום סעיפים = ניקוד שאלה)
- סגנון מה״ט 99913, רמה גבוהה
- תיבת נוסחאות — רק מה שרלוונטי לדף מה״ט ולתרגילים
- פתרונות מלאים + סיכום תשובות

### 4. הפקה
```bash
python3 מבחנים/generate_exam.py --spec ch4_ch5
```

### מבחן פרקים 1–2 הקיים
```bash
python3 מבחנים/generate_exam.py --legacy-ch12
# או ישירות:
python3 מבחנים/generate_exam_ch1_ch2.py
```

## מבנה קבצים

```
מבחנים/
  generate_exam.py          # CLI
  generate_exam_ch1_ch2.py   # מבחן 1–2 המלא (ייחוס זהב)
  lib/
    pdf_engine.py           # RTL, נוסחאות, כותרות, תיבות
    models.py               # ExamSpec / Question / Section
    builder.py              # בניית PDF ממפרט
    discover.py             # גילוי תיקיות פרקים + עצי נושאים
  specs/
    _template.py            # תבנית
    ch4_ch5.py              # (אחרי scaffold)
  README_EXAM_GENERATOR.md
  mahat-exam-skill/SKILL.md # הנחיות מלאות לסוכן Cursor
```

## כללי איכות חובה (מהצ׳אט)

1. **מתמטיקה** — אימות ידני/sympy לכל תשובה לפני הפקה
2. **ניקוד** — סכום סעיפים = שאלה; סכום שאלות = 100
3. **RTL** — מספרים/משתנים לטיניים במקטע `ltr`; בלי `()` סביב ניקוד
4. **תשובות בפתרונות** — תווית «תשובה:» ואז נוסחה בשורה נפרדת
5. **כיסוי** — מכסה ליבת הפרקים ברמת בחינה (לא חובה 100% מתתי־נושאים בסיסיים)
6. **נוסחאות** — רק רלוונטיות מדף מה״ט לתרגילים שבמבחן
7. **החרגות** — לציין במפורש (כפל מקוצר וכו׳) אם רלוונטי
