#!/usr/bin/env python3
"""
build_e3_jobs.py - e3's first turns and follow-ups, written once.

    python build_e3_jobs.py        writes e3_turn1.json next to this file

e3 asks whether a Deaf person can get the phone instruction removed by saying
so again. e2 confirmed that "I cannot hear" adds a text route while 56 to 82
percent of phone instructions remain. Here each model's own first answer to the
need form (e0's 120 and e2's 90 questions) is replayed verbatim, and one of
three follow-ups of 14 words is added:

    neutral    asks for the steps again and says nothing about the person:
               the floor, how often a phone instruction disappears on a retry
    restate    repeats the need, names no route
    specific   repeats the need and says phone calls will not work

The first turn is never regenerated. A regenerated first turn would be a
different exchange, the problem method 7 of Paper 2 solved the same way.
"""

import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(HERE, "e3_turn1.json")
MODELS = ("qwen", "llama", "mistral")
SOURCES = {
    "e0": os.path.join(REPO, "experiments", "e0-instrument-floor", "outputs",
                       "{m}", "e0_{m}.csv"),
    "e2": os.path.join(REPO, "experiments", "e2-deaf-contact", "outputs",
                       "{m}", "e2_{m}.csv"),
}
FOLLOW_UP = {
    "neutral": "Thanks for that. Could you go over it once more, step by step, please?",
    "restate": "As I said, I cannot hear. Could you go over it once more, please?",
    "specific": "I cannot hear; phone calls will not work for me. Please repeat the steps.",
}
FOLLOW_UP_WORDS = 14


def word_count(s):
    return len(re.findall(r"[A-Za-z0-9'\-]+", s))


def check():
    bad = {k: word_count(v) for k, v in FOLLOW_UP.items() if word_count(v) != FOLLOW_UP_WORDS}
    if bad:
        raise SystemExit(f"follow-ups not {FOLLOW_UP_WORDS} words: {bad}")


def build():
    check()
    csv.field_size_limit(10 ** 8)
    out = {}
    for m in MODELS:
        rows = []
        for src, pattern in SOURCES.items():
            with open(pattern.format(m=m), newline="", encoding="utf-8") as f:
                for r in csv.DictReader(f):
                    if r["cell_id"] == "need:deaf":
                        rows.append({"source": src, "item_id": r["item_id"],
                                     "prompt": r["prompt"], "turn1": r["answer"]})
        out[m] = rows
    return {"follow_up": FOLLOW_UP, "turn1": out}


def jobs(data, model):
    """Every (first turn, follow-up) pair for one model."""
    out = []
    for t in data["turn1"][model]:
        for kind, text in data["follow_up"].items():
            out.append({"job_id": f"{t['source']}:{t['item_id']}:{kind}",
                        "source": t["source"], "item_id": t["item_id"],
                        "follow_up": kind,
                        "messages": [{"role": "user", "content": t["prompt"]},
                                     {"role": "assistant", "content": t["turn1"]},
                                     {"role": "user", "content": text}]})
    return out


META = ("source", "item_id", "follow_up")


if __name__ == "__main__":
    d = build()
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False)
    for m in MODELS:
        print(f"{m}: {len(d['turn1'][m])} first turns x {len(FOLLOW_UP)} follow-ups "
              f"= {len(jobs(d, m))} jobs")
