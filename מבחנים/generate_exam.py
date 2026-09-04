#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI ליצירת מבחני מה״ט.

דוגמאות:
  # הצגת נושאים מתיקיות פרקים
  python3 מבחנים/generate_exam.py --brief 4 5

  # יצירת קובץ מפרט חדש (scaffold) לפרקים שנבחרו
  python3 מבחנים/generate_exam.py --scaffold 4 5

  # הפקת PDF ממפרט קיים
  python3 מבחנים/generate_exam.py --spec ch1_ch2
  python3 מבחנים/generate_exam.py --spec ch4_ch5

  # הפקת המבחן הקיים (פרקים 1–2) דרך הסקריפט המקורי
  python3 מבחנים/generate_exam.py --legacy-ch12
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SPECS = HERE / "specs"
sys.path.insert(0, str(HERE))

from lib.discover import find_chapters, load_topic_tree, print_chapter_brief
from lib.builder import build_exam_pdf, build_solutions_pdf


def _load_spec_module(name: str):
    path = SPECS / f"{name}.py"
    if not path.exists():
        raise FileNotFoundError(f"לא נמצא מפרט: {path}")
    spec = importlib.util.spec_from_file_location(f"exam_spec_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    if not hasattr(mod, "build_spec"):
        raise AttributeError(f"{path.name} חייב להגדיר build_spec() -> ExamSpec")
    return mod


def cmd_brief(nums: list[int]) -> None:
    print_chapter_brief(nums)


def _strip_template_header(src: str) -> str:
    """מסיר shebang + encoding + docstring ראשוני מהתבנית."""
    lines = src.splitlines(keepends=True)
    i = 0
    while i < len(lines) and (
        lines[i].startswith("#!")
        or lines[i].startswith("# -*-")
        or lines[i].startswith("# coding")
        or lines[i].strip() == ""
    ):
        i += 1
    rest = "".join(lines[i:]).lstrip()
    if rest.startswith('"""') or rest.startswith("'''"):
        q = rest[:3]
        end = rest.find(q, 3)
        if end != -1:
            rest = rest[end + 3 :].lstrip("\n")
    return rest


def cmd_scaffold(nums: list[int]) -> Path:
    chapters = find_chapters(nums)
    tag = "_".join(f"ch{n}" for n in nums)
    out = SPECS / f"{tag}.py"
    if out.exists():
        raise FileExistsError(f"כבר קיים: {out} — מחק/שנה שם לפני scaffold חדש")

    template = (SPECS / "_template.py").read_text(encoding="utf-8")
    names = " | ".join(c["name"] for c in chapters)
    topics = "נושאים: " + "  •  ".join(c["name"] for c in chapters)
    dirs = ", ".join(repr(c["rel"]) for c in chapters)
    nums_lit = ", ".join(str(n) for n in nums)
    nums_dash = "-".join(map(str, nums))
    nums_en = "–".join(map(str, nums))

    trees = []
    for c in chapters:
        tree = load_topic_tree(c["num"])
        trees.append(f"# --- פרק {c['num']}: {c['name']} ---\n# " + "\n# ".join(tree.splitlines()[:40]))

    header = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
מפרט מבחן מה״ט — פרקים {nums_en}
נושאים: {names}

נוצר אוטומטית ע״י: python3 מבחנים/generate_exam.py --scaffold {" ".join(map(str, nums))}
מלא את השאלות ברמת מה״ט (ראה מבחנים/README_EXAM_GENERATOR.md ו־mahat-exam-skill).
לאחר מכן:
  python3 מבחנים/generate_exam.py --spec {tag}
"""

'''
    body = _strip_template_header(template)
    body = body.replace(
        'exam_filename="מבחן_TODO.pdf"',
        f'exam_filename="מבחן_פרקים_{nums_dash}.pdf"',
    )
    body = body.replace(
        'solutions_filename="פתרונות_TODO.pdf"',
        f'solutions_filename="פתרונות_מבחן_פרקים_{nums_dash}.pdf"',
    )
    body = body.replace("chapter_nums=[0]", f"chapter_nums=[{nums_lit}]")
    body = body.replace("chapter_dirs=[]", f"chapter_dirs=[{dirs}]")
    body = body.replace('topics_he="נושאים: TODO"', f'topics_he="{topics}"')
    body = body.replace(
        'page_title_he="מבחן מה״ט — TODO"',
        f'page_title_he="מבחן מה״ט — פרקים {nums_en}"',
    )

    context = "\n".join(trees) + "\n\n"
    out.write_text(header + context + body, encoding="utf-8")
    print(f"נוצר מפרט: {out}")
    print("כעת מלא שאלות (4 שאלות, 100 נק׳, סגנון מה״ט) והרץ --spec")
    return out


def cmd_build(name: str) -> None:
    mod = _load_spec_module(name)
    spec = mod.build_spec()
    spec.validate()
    exam = build_exam_pdf(spec, HERE)
    sols = build_solutions_pdf(spec, HERE)
    print("EXAM:", exam)
    print("SOLS:", sols)


def cmd_legacy_ch12() -> None:
    import runpy

    runpy.run_path(str(HERE / "generate_exam_ch1_ch2.py"), run_name="__main__")


def main():
    p = argparse.ArgumentParser(description="מחולל מבחני מה״ט")
    p.add_argument("--brief", nargs="+", type=int, metavar="N", help="הצג עץ נושאים + קבצים לפרקים")
    p.add_argument("--scaffold", nargs="+", type=int, metavar="N", help="צור קובץ מפרט חדש לפרקים")
    p.add_argument("--spec", type=str, help="שם מפרט ב־specs/ (בלי .py)")
    p.add_argument("--legacy-ch12", action="store_true", help="הפק את מבחן פרקים 1–2 המלא")
    p.add_argument("--list", action="store_true", help="הצג פרקים זמינים")
    args = p.parse_args()

    if args.list:
        from lib.discover import discover_chapters

        for c in discover_chapters():
            print(f"{c['num']:2d}  {c['rel']}  ({len(c['md_files'])} md)")
        return

    if args.brief:
        cmd_brief(args.brief)
        return
    if args.scaffold:
        cmd_scaffold(args.scaffold)
        return
    if args.spec:
        cmd_build(args.spec)
        return
    if args.legacy_ch12:
        cmd_legacy_ch12()
        return

    p.print_help()


if __name__ == "__main__":
    main()
