# -*- coding: utf-8 -*-
"""Generate PNG charts for קריאת גרפים materials. Run from repo: py graphs/generate_reading_graphs.py"""
import os
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from bidi.algorithm import get_display

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "reading_graphs")
os.makedirs(OUT, exist_ok=True)

plt.rcParams["font.sans-serif"] = ["Segoe UI", "Arial", "David", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def heb(text):
    """Matplotlib מצייר ב־LTR; get_display הופך טקסט עברי לסדר תצוגה נכון."""
    if text is None:
        return None
    return get_display(text)


def line_plot(x, y, fname, xlabel, ylabel, title=None):
    fig, ax = plt.subplots(figsize=(7, 4.2), dpi=150)
    ax.plot(x, y, "o-", color="#1565C0", lw=2.2, ms=8)
    ax.set_xlabel(heb(xlabel), fontsize=11, labelpad=8)
    ax.set_ylabel(heb(ylabel), fontsize=11, labelpad=8)
    if title:
        ax.set_title(heb(title), fontsize=12, pad=10)
    ax.grid(True, alpha=0.35)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, fname), bbox_inches="tight")
    plt.close(fig)


def multi_line(xs, ys, labels, fname, xlabel, ylabel, title=None):
    fig, ax = plt.subplots(figsize=(7.5, 4.3), dpi=150)
    colors = ("#1565C0", "#E65100", "#2E7D32")
    for i, (x, y) in enumerate(zip(xs, ys)):
        ax.plot(
            x,
            y,
            "o-",
            lw=2.2,
            ms=7,
            color=colors[i % len(colors)],
            label=heb(labels[i]),
        )
    ax.set_xlabel(heb(xlabel), fontsize=11, labelpad=8)
    ax.set_ylabel(heb(ylabel), fontsize=11, labelpad=8)
    if title:
        ax.set_title(heb(title), fontsize=12, pad=10)
    ax.legend(loc="best", fontsize=10)
    ax.grid(True, alpha=0.35)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, fname), bbox_inches="tight")
    plt.close(fig)


def bar_two(cats, vals, fname, xlabel, ylabel, title=None):
    fig, ax = plt.subplots(figsize=(5.5, 4), dpi=150)
    ax.bar([heb(c) for c in cats], vals, color=("#1565C0", "#E65100"), width=0.55)
    ax.set_xlabel(heb(xlabel), fontsize=11, labelpad=8)
    ax.set_ylabel(heb(ylabel), fontsize=11, labelpad=8)
    if title:
        ax.set_title(heb(title), fontsize=12, pad=10)
    ax.grid(True, axis="y", alpha=0.35)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, fname), bbox_inches="tight")
    plt.close(fig)


# --- מערך שיעור ---
line_plot(
    [8, 10, 12, 14],
    [5, 12, 20, 9],
    "lesson_01_coffee.png",
    "שעה ביום",
    "מספר כוסות קפה שנמכרו",
    "מכירות כוסות קפה לפי שעה",
)

line_plot(
    [7, 9, 13, 15],
    [2.0, 5.0, 5.0, 2.0],
    "lesson_02_pool.png",
    "שעה",
    "גובה מי הבריכה (יחידות יחסיות)",
    "גובה מים בבריכה לפי זמן (תרשים לדוגמה)",
)

t_a = np.linspace(8, 16, 40)
# חנות א׳ (מרכז), חנות ב׳ (שכונה): עד תשע ב׳ מעל; ב־תשע מפגש; אחר כך א׳ מעל
line_a = np.piecewise(
    t_a,
    [t_a < 9, t_a >= 9],
    [lambda t: 20 + (55 - 20) * (t - 8) / (9 - 8), lambda t: 55 + (95 - 55) * (t - 9) / (16 - 9)],
)
line_b = np.piecewise(
    t_a,
    [t_a < 9, t_a >= 9],
    [lambda t: 50 + (55 - 50) * (t - 8) / (9 - 8), lambda t: 55 + (40 - 55) * (t - 9) / (16 - 9)],
)
multi_line(
    [t_a, t_a],
    [line_a, line_b],
    ["חנות א׳ (מרכז קניות)", "חנות ב׳ (שכונה)"],
    "lesson_03_stores.png",
    "שעה ביום",
    "מספר לקוחות",
    "השוואת לקוחות בין שתי חנויות (תרשים לדוגמה)",
)

# --- תרגול ---
line_plot(
    [8, 11, 14],
    [19, 24, 21],
    "ex01.png",
    "שעה",
    "טמפרטורה (°C)",
    "טמפרטורה בחוץ לפי שעה",
)

line_plot(
    [9, 12, 15],
    [3, 5, 6],
    "ex02.png",
    "שעה",
    "צעדים (באלפים)",
    "צעדים שנרשמו לפי שעה",
)

line_plot(
    [10, 11, 12],
    [48, 47, 50],
    "ex03.png",
    "שעה",
    "מחיר המניה (₪)",
    "מחיר מניה לפי שעה",
)

line_plot(
    [6, 10],
    [2, 8],
    "ex04.png",
    "שעה מהחצות",
    "גובה מי גשם (מ״מ)",
    "גובה מי גשם שנאספו",
)

bar_two(
    ["מכשיר ראשון", "מכשיר שני"],
    [120, 95],
    "ex05.png",
    "מכשיר",
    "ערך המדידה (יחידות אחידות)",
    "השוואת שני מכשירי מדידה באותו רגע",
)

line_plot(
    [1, 2, 3],
    [40, 35, 28],
    "ex06.png",
    "יום (מספר סידורי)",
    "מלאי (יחידות)",
    "מלאי בחנות לפי יום",
)

line_plot(
    [0, 2],
    [60, 100],
    "ex07.png",
    "זמן (שעות)",
    "מהירות הרכבת (קמ״ש)",
    "מהירות רכבת לפי זמן",
)

line_plot(
    [0, 3, 5, 7],
    [1, 4, 4, 1.5],
    "ex08.png",
    "שעה",
    "ערך המדידה (יחידות יחסיות)",
    "דוגמה: עלייה, קטע קבוע, ירידה",
)

line_plot(
    [10, 12, 14, 16],
    [50, 90, 70, 40],
    "ex09.png",
    "שעה",
    "מספר מבקרים",
    "מבקרים במוזיאון לפי שעה",
)

multi_line(
    [[8, 10], [8, 10]],
    [[12, 30], [20, 25]],
    ["בית קפה א׳", "בית קפה ב׳"],
    "ex10.png",
    "שעה",
    "מספר לקוחות",
    "לקוחות בשני בתי קפה",
)

line_plot(
    [0, 5, 10],
    [20, 50, 60],
    "ex11.png",
    "זמן (דקות)",
    "טמפרטורת המנוע (°C)",
    "טמפרטורת מנוע לפי זמן",
)

line_plot(
    [1, 7],
    [80, 68],
    "ex12.png",
    "יום בשבוע (מספר)",
    "מחיר המוצר (₪)",
    "מחיר מוצר לאורך ימים",
)

multi_line(
    [[13, 14, 15, 16, 17, 18], [13, 14, 15, 16, 17, 18]],
    [[80, 75, 70, 68, 65, 62], [50, 55, 62, 68, 72, 78]],
    ["גרף א׳", "גרף ב׳"],
    "ex13.png",
    "שעה",
    "ערך המדידה",
    "שני גרפים עם נקודת מפגש (תרשים לדוגמה)",
)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 5.5), dpi=150)
x_b = [0, 1, 2]
y_b = [10, 15, 20]
ax1.plot(x_b, y_b, "o-", color="#1565C0", lw=2)
ax1.set_ylabel(heb("ערך בטבלה (מדרגות)"), fontsize=10)
ax1.set_title(heb("טבלה א׳: משבצת אחת = 10 יחידות אמיתיות"), fontsize=10)
ax1.grid(True, alpha=0.35)
ax1.set_xlabel(heb("נקודת זמן"), fontsize=10)

ax2.plot(x_b, y_b, "o-", color="#E65100", lw=2)
ax2.set_ylabel(heb("ערך בטבלה (מדרגות)"), fontsize=10)
ax2.set_title(heb("טבלה ב׳: משבצת אחת = יחידה אחת אמיתית"), fontsize=10)
ax2.grid(True, alpha=0.35)
ax2.set_xlabel(heb("נקודת זמן"), fontsize=10)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "ex14.png"), bbox_inches="tight")
plt.close(fig)

line_plot(
    [6, 8, 10, 12],
    [2, 5, 5, 2],
    "ex15.png",
    "שעה",
    "גובה מי הבריכה (יחידות יחסיות)",
    "גובה מים בבריכה (תרגיל)",
)

line_plot(
    [1, 2, 3],
    [40, 100, 120],
    "ex16.png",
    "זמן (שעות)",
    "מרחק מנקודת התחלה (ק״מ)",
    "מרחק לפי זמן",
)

line_plot(
    [100, 200, 300],
    [0.5, 0.6, 0.6],
    "ex17.png",
    "צריכה חודשית (קוט״ש)",
    "מחיר לקוט״ש (₪)",
    "מחיר חשמל לפי צריכה",
)

t_bus = np.linspace(6, 18, 60)
# קו א׳ מעל בין 6 ל־9; פגישה ב־9; קו ב׳ מעל אחר כך
bus_a = np.piecewise(
    t_bus,
    [t_bus < 9, t_bus >= 9],
    [lambda t: 100 + (60 - 100) * (t - 6) / 3, lambda t: 60 + (75 - 60) * (t - 9) / 9],
)
bus_b = np.piecewise(
    t_bus,
    [t_bus < 9, t_bus >= 9],
    [lambda t: 40 + (60 - 40) * (t - 6) / 3, lambda t: 60 + (110 - 60) * (t - 9) / 9],
)
multi_line(
    [t_bus, t_bus],
    [bus_a, bus_b],
    ["קו א׳", "קו ב׳"],
    "ex18.png",
    "שעה ביום",
    "מספר נוסעים",
    "נוסעים בשני קווי אוטובוס (תרשים לדוגמה)",
)

line_plot(
    [0, 2, 4, 6],
    [1.0, 4.0, 2.0, 4.0],
    "ex19.png",
    "שעה",
    "גובה המים במיכל (יחידות יחסיות)",
    "גובה מים במיכל לפי זמן (תרשים לדוגמה)",
)

line_plot(
    [0, 5, 15, 25],
    [70, 130, 130, 90],
    "ex20.png",
    "זמן מאז תחילת האימון (דקות)",
    "דופק (פעימות לדקה)",
    "דופק במהלך אימון",
)

print("Saved charts to:", OUT)
