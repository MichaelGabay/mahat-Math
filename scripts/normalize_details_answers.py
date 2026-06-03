#!/usr/bin/env python3
"""Normalize <details> answer blocks for GitHub RTL + LaTeX (chapter-agnostic)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

HEBREW_RE = re.compile(r"[\u0590-\u05FF]")
MATH_RE = re.compile(r"\$[^$]+\$")
NUM_LINE_RE = re.compile(r"^(\*{2})?\d+\.(\*{2})?\s*")
SUB_LINE_RE = re.compile(r"^[א-ד]\.\s*")
PUNCT_ONLY_RE = re.compile(r"^[,;.\s]+$")
EMBEDDED_NUM_RE = re.compile(
    r"(?<=\S)\s+((?:[2-9]|1[0-9]|20)\.)(?!\d)\s*"
)


def has_hebrew(s: str) -> bool:
    return bool(HEBREW_RE.search(s))


def has_math(s: str) -> bool:
    return bool(MATH_RE.search(s))


def is_table_line(s: str) -> bool:
    return "|" in s and "$" in s


THOUSANDS_RE = re.compile(r"\d{1,3}\{ \}\d{3}(?:\.\d+)?\$")


def repair_stray_dollars(line: str) -> str:
    shields: list[str] = []

    def shield_thousands(m: re.Match[str]) -> str:
        val = m.group(0)[:-1]
        shields.append(val)
        return f"__TH{len(shields) - 1}__"

    line = THOUSANDS_RE.sub(shield_thousands, line)
    line = re.sub(
        r"(?<!\$)(?<![\d+\-*/(=])(\d+(?:\.\d+)?)\$(?=\s*[\u0590-\u05FF%₪]|[;,\)]|\s+[א-ת])",
        r"$\1$",
        line,
    )  # (?<!\$) avoids breaking $22$בנות
    line = re.sub(r"(?<!\$)(?<![\d.])(\d+)\$✓", r"$\1$ ✓", line)
    line = re.sub(r"([א-ד]\.)\s*(\d+(?:\.\d+)?(?:\{ \}\d+)?)\$", r"\1\n$\2$", line)
    line = re.sub(r"(\$[\d{ }]+)\s+([א-ד]\.)", r"\1\n\2", line)
    for i, val in enumerate(shields):
        line = line.replace(f"__TH{i}__", f"${val}$")
    return line


def preprocess_glued_line(line: str) -> str:
    line = re.sub(r"^\*\*(\d+)\.\*\*\s*", r"\1. ", line)
    line = re.sub(r"^\*\*(\d+)\.\*\*$", r"\1.", line)
    line = re.sub(r"^(\d+\.)\s*(\\)", r"\1\n\\", line)
    line = re.sub(r"יהי\$([^$]+)\$\s*=", r"יהי\n$\1$\n=", line)
    line = re.sub(r"(\$[a-zA-Z][^$]*\$)\s*=\s*", r"\1\n=\n", line)
    for unit in ("₪", 'מ"ר', "מ'", 'ק"ג', 'ס"מ', "ממ'", "צמחים"):
        line = re.sub(rf"({re.escape(unit)})\s*([א-ד]\.)", r"\1\n\2", line)
    line = re.sub(r"([א-ת])\s+([א-ד]\.\s)", r"\1\n\2", line)
    line = re.sub(r"([%])\s+([א-ד]\.)", r"\1\n\2", line)
    line = re.sub(r"(\$[^$]+\$)\s*([א-ד]\.)", r"\1\n\2", line)
    line = re.sub(r"(\$[^$]+)([א-ד]\.)", r"\1$\n\2", line)
    line = re.sub(r"(\d+)([א-ד]\.)", r"\1\n\2", line)
    line = re.sub(r"\$(\d+)\n([א-ד]\.)", r"$\1$\n\2", line)
    line = re.sub(r"(\d+)\$([א-ד]\.)", r"$\1$\n\2", line)
    line = re.sub(r"([א-ד]\.)\s*([^$\n]{1,40})\s+([א-ד]\.)", r"\1\n\2\n\3", line)
    line = re.sub(
        r"([א-ד]\.)\s*((?:\d+\{ \}\d+|\d+\.?\d*))\s*₪",
        r"\1\n$\2$\n₪",
        line,
    )
    return repair_stray_dollars(line)


def unglue_single_line(line: str) -> list[str]:
    if is_table_line(line):
        return [line]
    line = re.sub(r"(\$[^$]+\$)\s*([\u0590-\u05FF])", r"\1\n\2", line)
    line = re.sub(r"([\u0590-\u05FF])\s*(\$)", r"\1\n\2", line)
    line = re.sub(r"(\$[^$]+\$)(;\s*)", r"\1\n\2", line)
    line = re.sub(r"(\$[^$]+\$)(\()", r"\1\n\2", line)
    parts = [repair_stray_dollars(p.strip()) for p in line.split("\n") if p.strip()]
    return parts if parts else [line]


def split_numbered_with_subitems(line: str) -> list[str]:
    m = re.match(r"^(\d+\.)\s*([א-ד]\.\s*)(.*)$", line)
    if m:
        return [m.group(1), (m.group(2) + m.group(3)).strip()]
    return [line]


def split_embedded_answer_numbers(line: str) -> list[str]:
    m = re.match(r"^(\d+\.)(.*)$", line)
    if not m:
        return [line]
    head, tail = m.group(1), m.group(2)
    if not EMBEDDED_NUM_RE.search(tail):
        return [line]
    parts = EMBEDDED_NUM_RE.split(tail)
    out = [head + parts[0].strip()] if parts[0].strip() else [head.rstrip()]
    i = 1
    while i < len(parts):
        if i + 1 < len(parts):
            out.append(parts[i] + parts[i + 1].strip())
            i += 2
        else:
            out.append(parts[i])
            i += 1
    return [p for p in out if p.strip()]


def split_subanswers_in_line(line: str) -> list[str]:
    if not re.search(r"[א-ד]\.", line):
        return [line]
    parts = re.split(r"(?<=[;])\s*(?=[א-ד]\.)", line)
    if len(parts) == 1:
        parts = re.split(r"(?<=[.)])\s*(?=[א-ד]\.)", line)
    if len(parts) == 1:
        return [line]
    out: list[str] = []
    for i, p in enumerate(parts):
        p = p.strip()
        if not p:
            continue
        if i > 0 and not SUB_LINE_RE.match(p):
            if out:
                out[-1] = out[-1].rstrip(";") + "; " + p
            else:
                out.append(p)
        else:
            out.append(p)
    return out


def split_hebrew_math(line: str) -> list[str]:
    line = line.strip()
    if not line or not (has_hebrew(line) and has_math(line)):
        return [line]

    m = re.match(r"^(\d+\.)\s*(.*)$", line)
    label = ""
    rest = line
    if m:
        label = m.group(1) + " "
        rest = m.group(2)
    else:
        sm = re.match(r"^([א-ד]\.)\s*(.*)$", line)
        if sm:
            label = sm.group(1) + " "
            rest = sm.group(2)

    segments = [s for s in re.split(r"(\$[^$]+\$)", rest) if s != ""]
    out: list[str] = []
    for seg in segments:
        if seg.startswith("$"):
            inner = seg[1:-1]
            if has_hebrew(inner):
                for part in re.split(r"([\u0590-\u05FF]+)", inner):
                    part = part.strip()
                    if not part:
                        continue
                    if has_hebrew(part):
                        if label and not out:
                            out.append((label + part).strip())
                            label = ""
                        elif out and has_hebrew(out[-1]) and not has_math(out[-1]):
                            out[-1] = out[-1] + part
                        else:
                            out.append(part)
                    elif part:
                        piece = f"${part}$"
                        if label and not out:
                            out.append((label + piece).strip())
                            label = ""
                        else:
                            out.append(piece)
            else:
                if label and not out:
                    out.append((label + seg).strip())
                    label = ""
                else:
                    out.append(seg.strip())
        else:
            t = seg.strip()
            if not t:
                continue
            if label and not out:
                out.append((label + t).strip())
                label = ""
            elif out and has_hebrew(out[-1]) and not has_math(out[-1]):
                sep = "" if out[-1].endswith((":", "—", "(", "（")) else " "
                out[-1] = out[-1] + sep + t
            else:
                out.append(t)
    if label and not out:
        out.append(label.strip())
    return out if out else [line]


def split_subitem_prefix(line: str) -> list[str] | None:
    m = re.match(r"^([א-ד]\.)\s*(.*)$", line)
    if not m:
        return None
    label, rest = m.group(1), m.group(2).strip()
    if not rest:
        return [label]
    parts = [label]
    if has_math(rest) or has_hebrew(rest):
        parts.extend(split_hebrew_math(rest))
    else:
        parts.append(rest)
    return parts


def process_line(line: str) -> list[str]:
    line = preprocess_glued_line(line)
    expanded: list[str] = []
    for glued in unglue_single_line(line):
        for part in split_embedded_answer_numbers(glued):
            for chunk in split_numbered_with_subitems(part):
                for sub in split_subanswers_in_line(chunk):
                    sub_parts = split_subitem_prefix(sub)
                    if sub_parts is not None:
                        expanded.extend(sub_parts)
                    else:
                        expanded.extend(split_hebrew_math(sub))
    return expanded


def merge_punctuation_lines(lines: list[str]) -> list[str]:
    out: list[str] = []
    for line in lines:
        if PUNCT_ONLY_RE.match(line) and out:
            out[-1] = out[-1] + line.strip()
        else:
            out.append(line)
    return out


def polish_block_text(block: str) -> str:
    block = re.sub(r"\$\(\(([^)]+)\)\)\$", r"$(\1)$", block)
    block = re.sub(r"\n\$\s*\n", "\n", block)
    block = re.sub(r"נקודות החיתוך:\$", "נקודות החיתוך:", block)
    block = re.sub(r"([\u0590-\u05FF]+):\$", r"\1:\n", block)
    block = re.sub(r"(\$[\d{ }]+)₪", r"\1\n₪", block)
    block = re.sub(r"ו-\$", "ו-", block)
    block = re.sub(
        r"\$\\left\$\s*\n\$\((.+?\\right)\)\$?\.?",
        r"$\\left(\1)$.",
        block,
    )
    block = re.sub(
        r"^(-?\d[^$\n]*[<>=][^$\n]*)\$\s*;?\s*$",
        r"$\1$",
        block,
        flags=re.MULTILINE,
    )
    block = re.sub(
        r"^(\d+\.\s+\$\d+\$);(\$[^$]+\$.*)$",
        r"\1\n\2",
        block,
        flags=re.MULTILINE,
    )
    block = re.sub(
        r"^(\d+)\$(\s*;)",
        r"$\1$\2",
        block,
        flags=re.MULTILINE,
    )
    for m in re.finditer(r"\$([\u0590-\u05FF][^\n$]+)\$", block):
        if not re.search(r"[=<>+\-*/^\\]|\\frac|\\sqrt", m.group(1)):
            block = block.replace(m.group(0), m.group(1))
    block = re.sub(
        r"(?<!\$)\((-?[^)]+,\s*-?[^)]+)\)\$",
        r"$(\1)$",
        block,
    )
    block = re.sub(
        r"^(\$)([\u0590-\u05FF][^\n$]+)$",
        lambda m: m.group(2),
        block,
        flags=re.MULTILINE,
    )
    block = re.sub(
        r"(\d+\.\s+)\$([A-Z])\$\s*\n\$\(([^)]+)\)\$",
        r"\1$\2(\3)$",
        block,
    )
    block = re.sub(
        r"\$([A-Z])\$\s*\n\$\(([^)]+)\)\$",
        r"$\1(\2)$",
        block,
    )
    block = re.sub(
        r"(ו-)\s*\n\$([A-Z])\$\s*\n\$\(([^)]+)\)\$",
        r"\1\n$\2(\3)$",
        block,
    )
    block = re.sub(r"\$\\left\$\s*\n\$\(", r"$\\left(", block)
    block = re.sub(r"\$\\left\$\(", r"$\\left(", block)
    return block


def merge_split_decimals(text: str) -> str:
    """Repair $6.$76$ / $249.$8$ artifacts from over-eager $ wrapping."""
    prev = None
    while prev != text:
        prev = text
        text = re.sub(r"\$(\d+)\.\$(\d+)\$", r"$\1.\2$", text)
        text = re.sub(
            r"\$(\d+)\.(\d+)(?=\$|\s|$|[\u0590-\u05FF%₪(])",
            r"$\1.\2",
            text,
        )
    return text


def finalize_block(text: str) -> str:
    text = merge_split_decimals(text)
    text = re.sub(r"^\*\*(\d+)\.\*\*$", r"\1.", text, flags=re.MULTILINE)
    text = re.sub(r"^\$\$([^$\n]+)\$\$$", r"$\1$", text, flags=re.MULTILINE)
    text = re.sub(
        r"(?<!\$)(?<!\{ )\$\s*(\d+(?:\.\d+)?)(?!\{ \})\$",
        r"$\1$",
        text,
    )
    text = merge_split_decimals(text)
    text = re.sub(r"(\d)\{\s*\}\s*(\d)", r"\1{ }\2", text)
    text = re.sub(
        r"^([\u0590-\u05FF][^\n$]*?)\.\$$",
        r"\1.",
        text,
        flags=re.MULTILINE,
    )
    text = re.sub(
        r"^=\s*([\u0590-\u05FF][^\n$]+)\.\$$",
        r"= \1.",
        text,
        flags=re.MULTILINE,
    )
    lines = text.split("\n")
    merged: list[str] = []
    for ln in lines:
        s = ln.strip()
        if s in {"$.", "$", "."} and merged:
            merged[-1] = merged[-1] + s.replace("$", "")
            continue
        if re.match(r"^\$[\u0590-\u05FF]", s) and merged:
            merged[-1] = merged[-1] + s[1:]
            continue
        merged.append(ln)
    text = "\n".join(merged)
    text = re.sub(
        r"([\u0590-\u05FF])(\$[\u0590-\u05FF])",
        lambda m: m.group(1) + " " + m.group(2)[1:],
        text,
    )
    text = re.sub(r"(\$[^$]+\$)\s*([א-ד]\.)", r"\1\n\2", text)
    text = re.sub(r"(\$[^$]+\$)\s*([\u0590-\u05FF])", r"\1\n\2", text)
    text = re.sub(r"([\u0590-\u05FF]+):\$", r"\1:\n", text)
    text = re.sub(r"(\$[\d{ }]+)₪", r"\1\n₪", text)
    text = re.sub(r"^([א-ד])$", r"\1.", text, flags=re.MULTILINE)
    text = re.sub(r"^([א-ד])\.\s+\$", r"\1.\n$", text, flags=re.MULTILINE)
    text = re.sub(r"\$(\d)\$(\d\{ \}\d+)\$", r"$\1\2$", text)
    text = re.sub(r"\$(\d\{ \}\d+)\$(?=[^\d{])", r"$\1$", text)
    text = re.sub(r"\n\$\.\$\n", "\n", text)
    text = re.sub(r"^([א-ד])\n\$\.\s*$", r"\1.", text, flags=re.MULTILINE)
    text = re.sub(r"\$\$+", "$", text)
    text = merge_split_decimals(text)
    text = re.sub(r"&nbsp;+", "", text)
    text = re.sub(r"°\$\(", "°\n(", text)
    text = re.sub(r"(\d+°)\$\(", r"\1\n(", text)
    text = re.sub(r"\$([^$=]+=\s*)\$([^$]+)\$", r"$\1\2$", text)
    text = re.sub(r"\^ \$ (\d+) \$", r"^{\1}", text)
    text = re.sub(r"\^ \$(\d+)\$", r"^{\1}", text)
    text = re.sub(
        r'(["״²°־\u0590-\u05FF]+)\s+([א-ד]\.\s*)',
        r"\1\n\2",
        text,
    )
    text = re.sub(
        r'^([A-Za-z]+ = )\$([^$]+)\$',
        r'$\1\2$',
        text,
        flags=re.MULTILINE,
    )
    text = re.sub(
        r'^([^\n$]*[\u0590-\u05FF][^\n$]*)\s+\$\s*$',
        r"\1",
        text,
        flags=re.MULTILINE,
    )
    text = re.sub(r"(\$[^$]+\$)\s+\$\s*$", r"\1", text, flags=re.MULTILINE)
    text = re.sub(r"^(.+?)\s{2,}\$\s*$", r"\1", text, flags=re.MULTILINE)
    return text


def normalize_inner(inner: str) -> str:
    raw_lines = [ln.rstrip() for ln in inner.split("\n") if ln.strip()]

    blocks: list[list[str]] = []
    current: list[str] = []

    for line in raw_lines:
        if NUM_LINE_RE.match(line):
            if current:
                blocks.append(current)
            current = []
        current.extend(process_line(line))
    if current:
        blocks.append(current)

    formatted_blocks: list[str] = []
    for block in blocks:
        block = merge_punctuation_lines(block)
        block = [ln for ln in block if ln.strip()]
        formatted_blocks.append(
            finalize_block(polish_block_text("\n".join(block)))
        )

    return "\n\n".join(formatted_blocks)


def patch_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if "<details>" not in text:
        return False
    start = text.index("<details>")
    end = text.index("</details>") + len("</details>")
    inner = text[start + len("<details>") : text.index("</details>")]
    inner = inner.replace("<summary>תשובות סופיות</summary>", "").strip()
    normalized = normalize_inner(inner)
    block = (
        "<details>\n<summary>תשובות סופיות</summary>\n\n"
        + normalized
        + "\n</details>"
    )
    new_text = text[:start] + block + text[end:]
    if new_text == text:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: normalize_details_answers.py <chapter-dir>")
        sys.exit(1)
    chapter = Path(sys.argv[1]).resolve()
    for path in sorted(chapter.glob("*.md")):
        if patch_file(path):
            print("patched", path.name)
        else:
            print("unchanged", path.name)


if __name__ == "__main__":
    main()
