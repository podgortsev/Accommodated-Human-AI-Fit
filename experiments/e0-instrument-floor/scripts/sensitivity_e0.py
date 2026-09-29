#!/usr/bin/env python3
"""
sensitivity_e0.py - two post hoc checks on e0, NOT preregistered.

    python sensitivity_e0.py e0_qwen.csv e0_llama.csv e0_mistral.csv

Written 2026-09-29 after the registered analysis was run and read. Reported as
exploratory, beside the registered result, never in place of it.

1. WINDOW. Truncation at 400 new tokens differs by cell (Llama: 40 percent of
   need-form answers against 81 percent of label-form answers). A presence check
   such as "offers a text route" is more likely to be seen in an answer that
   ends inside the window. Every answer is cut to its first 200 words before
   scoring, so every cell is read through the same window.

2. LINES. The registered sentence splitter ends a sentence at . ! or ? only.
   Markdown list items without a full stop merge into one long "sentence", so
   the plain_language check partly measures list punctuation. Here every
   non-empty line is also a sentence boundary, and markdown markers (#, *, -,
   numbering) are dropped before counting. Same thresholds.

Everything else, the contrasts, tests and corrections, is analyse_e0.py unchanged.
"""

import contextlib
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "scripts")))
sys.path.insert(0, HERE)

import p4_checks as C          # noqa: E402
import analyse_e0 as A         # noqa: E402

WINDOW = 200
MD = re.compile(r"^\s*(#{1,6}\s*|[-*•]\s+|\d+[.)]\s+)")


def window(text, n=WINDOW):
    return " ".join(text.split()[:n]) if False else _first_words(text, n)


def _first_words(text, n):
    """First n words, keeping line breaks so list structure survives."""
    out, count = [], 0
    for line in text.splitlines():
        w = line.split()
        if count + len(w) >= n:
            out.append(" ".join(w[:n - count]))
            break
        out.append(line)
        count += len(w)
    return "\n".join(out)


def line_sentences(text):
    parts = []
    for line in text.splitlines():
        line = MD.sub("", line).replace("**", "").strip()
        if not line:
            continue
        parts += [p.strip() for p in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", line)
                  if p.strip()]
    return parts


def plain_lines(text):
    ss = line_sentences(text)
    ws = C.words(text)
    if not ss or not ws:
        return {"short_sentences": True, "low_grade": True,
                "no_idiom": not C._has(text, C.IDIOMS)}
    msw = sum(len(C.words(s)) for s in ss) / len(ss)
    syl = sum(C.syllables(w) for w in ws)
    grade = 0.39 * (len(ws) / len(ss)) + 11.8 * (syl / len(ws)) - 15.59
    return {"short_sentences": msw <= C.MAX_SENTENCE_WORDS,
            "low_grade": grade <= C.MAX_GRADE,
            "no_idiom": not C._has(text, C.IDIOMS)}


def run(paths, label, transform=None, plain=None):
    orig_needs = dict(C.NEEDS)
    orig_check_all = A.check_all
    if plain:
        C.NEEDS["plain_language"] = plain

    def scored(text):
        return C.check_all(transform(text) if transform else text)
    A.check_all = scored
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            A.main(paths)
    finally:
        C.NEEDS.clear()
        C.NEEDS.update(orig_needs)
        A.check_all = orig_check_all
    keep = []
    model = None
    for line in buf.getvalue().splitlines():
        if line.startswith("e0 |"):
            model = line.split("|")[1].strip()
            keep.append(f"-- {model}")
        s = line.strip()
        if ("need_benefit" in s or "label_benefit" in s) and \
                s.split()[0] in ("deaf", "plain_language", "wheelchair"):
            keep.append("  " + s)
        if s.startswith(("deaf ", "plain_language ", "wheelchair ")) and \
                len(s.split()) == 7:
            keep.append("  rates " + s)
        if s.startswith(("CONTINUE", "EXTEND", "STOP")):
            keep.append("  DECISION " + s)
    print("=" * 78)
    print(label)
    print("=" * 78)
    print("\n".join(keep))


def truncation_by_cell(paths):
    import csv
    csv.field_size_limit(10 ** 8)
    print("=" * 78)
    print("Truncation share by cell family, per model (context for check 1)")
    print("=" * 78)
    for p in paths:
        rows = list(csv.DictReader(open(p, newline="", encoding="utf-8")))
        fam = {}
        for r in rows:
            f = r["cell_id"].split(":")[0]
            fam.setdefault(f, []).append(r["truncated"] == "1")
        print(f"  {rows[0]['model']:8}" + "  ".join(
            f"{f}={sum(v) / len(v):.2f}" for f, v in sorted(fam.items())))


if __name__ == "__main__":
    paths = sys.argv[1:]
    truncation_by_cell(paths)
    run(paths, f"CHECK 1, WINDOW: every answer scored on its first {WINDOW} words",
        transform=lambda t: _first_words(t, WINDOW))
    run(paths, "CHECK 2, LINES: plain_language with line-aware sentences",
        plain=plain_lines)
    run(paths, "CHECKS 1 AND 2 TOGETHER",
        transform=lambda t: _first_words(t, WINDOW), plain=plain_lines)
