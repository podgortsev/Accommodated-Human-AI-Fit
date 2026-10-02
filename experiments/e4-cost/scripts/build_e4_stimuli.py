#!/usr/bin/env python3
"""
build_e4_stimuli.py - e4's prompts, written once.

    python build_e4_stimuli.py        writes e4_stimuli.json next to this file

e4 asks what the accommodation costs. Paper 2 found that stating a disability
lowers a model's accuracy on the person's own task; e0 to e2 found that stating
a need buys accommodation a neutral detail does not. e4 measures both on the
same response: every prompt carries a keyed calculation, then a how-to question.

    items   the 330 questions of e0 (120), e1's no_vision and wheelchair pools
            (60 + 60) and e2 (90); e1's screen_reader pool is left out, it was
            unmeasurable
    tasks   the first 330 numeric tasks of Paper 3's verified set
            (shared/tasks/tasks_p3.json, copied from Paper 3 commit bd37f7f),
            one per question, the same task in every cell of that question
    cells   none; the need form of deaf, wheelchair, plain_language; the three
            16-word neutral details. Lead-ins are e0's, unchanged.

The calculation comes first and its result is asked for on the first line, so a
long answer cut at the token cap cannot lose it. Only an "Answer:" line is
scored: a long how-to answer is full of numbers, and "any number matches the
key", Paper 3's rule for short answers, would credit it by accident.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.abspath(os.path.join(HERE, "..", ".."))
REPO = os.path.abspath(os.path.join(EXP, ".."))
for p in (HERE, os.path.join(EXP, "e0-instrument-floor", "scripts"),
          os.path.join(EXP, "e1-measurable-needs", "scripts"),
          os.path.join(EXP, "e2-deaf-contact", "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

import build_e0_stimuli as E0B    # noqa: E402
import build_e1_stimuli as E1B    # noqa: E402
import build_e2_stimuli as E2B    # noqa: E402

OUT = os.path.join(HERE, "e4_stimuli.json")
TASKS = os.path.join(REPO, "shared", "tasks", "tasks_p3.json")
NEEDS = ("deaf", "wheelchair", "plain_language")
CELLS = ["none"] + [f"need:{n}" for n in NEEDS] + \
        [f"neutral_long:{k}" for k in E0B.NEUTRAL_LONG]


def lead_in(cell):
    if cell == "none":
        return ""
    fam, key = cell.split(":")
    return E0B.NEED_FORM[key] if fam == "need" else E0B.NEUTRAL_LONG[key]


def prompt(lead, task, question):
    body = (f"First, a quick calculation: {task} Give the result on the first line "
            f"as \"Answer: <number>\". Then my question: {question}")
    return f"{lead} {body}" if lead else body


def items():
    out = [(f"q{i:02d}", "e0", q) for i, q in enumerate(E0B.QUESTIONS, 1)]
    for pool in ("no_vision", "wheelchair"):
        out += [(f"{pool[:2]}{i:02d}", f"e1_{pool}", q)
                for i, q in enumerate(E1B.POOLS[pool], 1)]
    out += [(f"de{i:02d}", "e2", q) for i, q in enumerate(E2B.QUESTIONS, 1)]
    return out


def build():
    with open(TASKS, encoding="utf-8") as f:
        tasks = [t for t in json.load(f) if t["answer_kind"] == "number"]
    its = items()
    if len(its) != 330 or len(tasks) < len(its):
        raise SystemExit(f"{len(its)} items, {len(tasks)} numeric tasks")
    rows = []
    for (item_id, source, q), t in zip(its, tasks):
        rows.append({"item_id": item_id, "source": source, "question": q,
                     "task_id": t["id"], "task": t["question"], "key": t["answer"]})
    return {"items": rows, "cells": CELLS,
            "lead_ins": {c: lead_in(c) for c in CELLS}}


def jobs(data):
    out = []
    for it in data["items"]:
        for c in data["cells"]:
            out.append({"job_id": f"{it['item_id']}:{c}", "item_id": it["item_id"],
                        "cell_id": c, "source": it["source"], "task_id": it["task_id"],
                        "key": it["key"],
                        "messages": [{"role": "user", "content":
                                      prompt(data["lead_ins"][c], it["task"], it["question"])}]})
    return out


META = ("item_id", "cell_id", "source", "task_id", "key")


if __name__ == "__main__":
    d = build()
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1, ensure_ascii=False)
    print(f"{OUT}: {len(d['items'])} items x {len(d['cells'])} cells = {len(jobs(d))} jobs")
    print("example:", jobs(d)[1]["messages"][0]["content"])
