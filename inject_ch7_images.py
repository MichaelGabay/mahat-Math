#!/usr/bin/env python3
"""
Insert image references into Chapter 7 markdown exercise files.

For MUST files  (subtopics 1,4,5,12,13,17,18,20,21): exercises 1-20
For SHOULD files (subtopics 3,6,10,14,16):           exercises 9-20
"""
import re, os

BASE = "/Users/mq/Desktop/\u05de\u05ea\u05de\u05d8\u05d9\u05e7\u05d4 - \u05d0\u05d5\u05e8\u05d8/mahat-Math/7 - \u05d4\u05e0\u05d3\u05e1\u05d4 \u05d0\u05e0\u05dc\u05d9\u05d8\u05d9\u05ea"

FILES = {
    # subtopic_num: (filename, first_ex, last_ex)
    1:  ("1_\u05d7\u05d6\u05e8\u05d4_\u05e7\u05e6\u05e8\u05d4_\u05d5\u05d9\u05d9\u05e9\u05d5\u05e8_\u05e7\u05d5_\u05de\u05e2\u05e8\u05db\u05ea_\u05d4\u05e6\u05d9\u05e8\u05d9\u05dd_\u05d5\u05e1\u05d9\u05de\u05d5\u05df_\u05e0\u05e7\u05d5\u05d3\u05d5\u05ea_\u05d1\u05de\u05d9\u05e9\u05d5\u05e8.md", 1, 20),
    3:  ("3_\u05d6\u05d9\u05d4\u05d5\u05d9_\u05e9\u05e0\u05d9_\u05d4\u05e4\u05e8\u05de\u05d8\u05e8\u05d9\u05dd_\u05d4\u05de\u05e1\u05e4\u05e8\u05d9\u05dd_\u05d4\u05e7\u05d1\u05d5\u05e2\u05d9\u05dd_\u05d4\u05de\u05e8\u05db\u05d9\u05d1\u05d9\u05dd_\u05db\u05dc_\u05e4\u05d5\u05e0\u05e7\u05e6\u05d9\u05d4.md", 9, 20),
    4:  ("4_\u05ea\u05d9\u05d0\u05d5\u05e8_\u05d2\u05e8\u05e4\u05d9_\u05d5\u05d0\u05dc\u05d2\u05d1\u05e8\u05d9_\u05e9\u05dc_\u05e7\u05d5_\u05d9\u05e9\u05e8_\u05d5\u05d6\u05d9\u05d4\u05d5\u05d9_\u05e0\u05e7\u05d5\u05d3\u05d5\u05ea_\u05e9\u05e2\u05dc\u05d9\u05d5.md", 1, 20),
    5:  ("5_\u05e9\u05e8\u05d8\u05d5\u05d8_\u05e7\u05d5_\u05d9\u05e9\u05e8_\u05d1\u05e2\u05d6\u05e8\u05ea_\u05d8\u05d1\u05dc\u05ea_\u05e0\u05ea\u05d5\u05e0\u05d9\u05dd.md", 1, 20),
    6:  ("6_\u05de\u05e6\u05d9\u05d0\u05ea_\u05e0\u05e7\u05d5\u05d3\u05d5\u05ea_\u05d7\u05d9\u05ea\u05d5\u05da_\u05e9\u05dc_\u05d4\u05d9\u05e9\u05e8_\u05e2\u05dd_\u05d4\u05e6\u05d9\u05e8\u05d9\u05dd.md", 9, 20),
    10: ("10_\u05d7\u05d9\u05e9\u05d5\u05d1_\u05d5\u05de\u05e6\u05d9\u05d0\u05ea_\u05e9\u05d9\u05e4\u05d5\u05e2_\u05e9\u05dc_\u05e7\u05d5_\u05d9\u05e9\u05e8_\u05e2\u05dc_\u05e4\u05d9_\u05e9\u05ea\u05d9_\u05e0\u05e7\u05d5\u05d3\u05d5\u05ea.md", 9, 20),
    12: ("12_\u05d9\u05e9\u05e8\u05d9\u05dd_\u05de\u05e7\u05d1\u05d9\u05dc\u05d9\u05dd_\u05d5\u05d9\u05d9\u05e9\u05d5\u05de\u05df_\u05d1\u05d7\u05d9\u05e9\u05d5\u05d1\u05d9\u05dd.md", 1, 20),
    13: ("13_\u05d9\u05e9\u05e8\u05d9\u05dd_\u05e0\u05d9\u05e6\u05d1\u05d9\u05dd_\u05d5\u05d9\u05d9\u05e9\u05d5\u05de\u05df_\u05d1\u05d7\u05d9\u05e9\u05d5\u05d1\u05d9\u05dd.md", 1, 20),
    14: ("14_\u05de\u05e6\u05d9\u05d0\u05ea_\u05d0\u05de\u05e6\u05e2_\u05e7\u05d8\u05e2_\u05e0\u05ea\u05d5\u05df.md", 9, 20),
    16: ("16_\u05d7\u05d9\u05e9\u05d5\u05d1_\u05de\u05e8\u05d7\u05e7_\u05d1\u05d9\u05df_\u05e9\u05ea\u05d9_\u05e0\u05e7\u05d5\u05d3\u05d5\u05ea.md", 9, 20),
    17: ("17_\u05d4\u05ea\u05e8\u05ea_\u05de\u05e2\u05e8\u05db\u05d5\u05ea_\u05de\u05e9\u05d5\u05d0\u05d5\u05ea_\u05de\u05de\u05e2\u05dc\u05d4_\u05e8\u05d0\u05e9\u05d5\u05e0\u05d4_\u05d2\u05e8\u05e4\u05d9\u05ea.md", 1, 20),
    18: ("18_\u05d4\u05de\u05e9\u05de\u05e2\u05d5\u05ea_\u05d4\u05d2\u05d9\u05d0\u05d5\u05de\u05d8\u05e8\u05d9\u05ea_\u05e9\u05dc_\u05de\u05e1\u05e4\u05e8_\u05e9\u05d5\u05e8\u05e9\u05d9_\u05d4\u05de\u05e2\u05e8\u05db\u05ea.md", 1, 20),
    20: ("20_\u05d6\u05d9\u05d4\u05d5\u05d9_\u05de\u05e7\u05d1\u05d9\u05dc\u05d9\u05ea_\u05d1\u05de\u05e2\u05e8\u05db\u05ea_\u05e6\u05d9\u05e8\u05d9\u05dd.md", 1, 20),
    21: ("21_\u05d9\u05d9\u05e9\u05d5\u05dd_\u05d2\u05d9\u05d0\u05d5\u05de\u05d8\u05e8\u05d9\u05d4_\u05d0\u05e0\u05dc\u05d9\u05d8\u05d9\u05ea_\u05d1\u05e6\u05d5\u05e8\u05d5\u05ea_\u05d4\u05e0\u05d3\u05e1\u05d9\u05d5\u05ea.md", 1, 20),
}


def exercise_pattern(n):
    """Return regex that matches an exercise header line for exercise n.
    Supports both:
      '1. ' / '1.\n'    (regular numbered list)
      '**1.**' / '**1.** '  (bold numbered)
    """
    # Bold style  **N.**
    bold = rf'\*\*{n}\.\*\*'
    # Plain style  N.  (at start of line or after some whitespace/dash)
    plain = rf'(?:^|\n){n}\.'
    return rf'({bold}|{plain})'


def insert_image_after_exercise(text, subtopic, ex_num, ex_start, ex_end):
    """Insert `![תרגיל N](images/7_S_exNN.png)` after exercise ex_num block."""
    img_tag = f"\n\n![תרגיל {ex_num}](images/7_{subtopic}_ex{ex_num:02d}.png)\n"

    # Pattern: line that starts the exercise (bold **N.** or plain N.)
    # followed eventually by the start of next exercise or end of section
    patterns_this = [
        rf'\*\*{ex_num}\.\*\*',
        rf'^{ex_num}\.',
        rf'\n{ex_num}\.',
    ]
    # Find where this exercise starts
    start_pos = None
    for pat in patterns_this:
        m = re.search(pat, text, re.MULTILINE)
        if m:
            start_pos = m.start()
            break
    if start_pos is None:
        print(f"  WARNING: could not find exercise {ex_num} in subtopic {subtopic}")
        return text

    # Find where the NEXT exercise starts (or end-of-section / <details>)
    next_ex = ex_num + 1
    end_pos = len(text)
    # Possible next-exercise patterns
    if next_ex <= ex_end:
        next_patterns = [
            rf'\*\*{next_ex}\.\*\*',
            rf'^{next_ex}\.',
            rf'\n{next_ex}\.',
        ]
        for pat in next_patterns:
            m = re.search(pat, text[start_pos + 1:], re.MULTILINE)
            if m:
                end_pos = start_pos + 1 + m.start()
                break
    else:
        # Last exercise of section — stop before <details> or ---
        for stopper in [r'\n---', r'<details']:
            m = re.search(stopper, text[start_pos:])
            if m:
                candidate = start_pos + m.start()
                if candidate < end_pos:
                    end_pos = candidate
                break

    # The block for this exercise is text[start_pos:end_pos]
    block = text[start_pos:end_pos]

    # Check if image already injected
    if f'7_{subtopic}_ex{ex_num:02d}.png' in block:
        return text  # already there

    # Insert image tag at the end of the block (before end_pos)
    # Find a good insertion point: after the last non-blank line in the block
    # Strip trailing newlines from block, append image, re-add separator
    stripped_block = block.rstrip('\n')
    new_block = stripped_block + img_tag

    return text[:start_pos] + new_block + text[end_pos:]


def process_file(subtopic, filename, first_ex, last_ex):
    path = os.path.join(BASE, filename)
    if not os.path.exists(path):
        print(f"FILE NOT FOUND: {path}")
        return

    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    original = text
    for ex_num in range(first_ex, last_ex + 1):
        text = insert_image_after_exercise(text, subtopic, ex_num, first_ex, last_ex)

    if text != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Updated: {filename}  (ex {first_ex}-{last_ex})")
    else:
        print(f"No changes: {filename}")


if __name__ == '__main__':
    for subtopic, (filename, first_ex, last_ex) in sorted(FILES.items()):
        process_file(subtopic, filename, first_ex, last_ex)
    print("\nAll markdown files processed.")
