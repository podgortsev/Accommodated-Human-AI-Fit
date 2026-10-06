#!/usr/bin/env python3
"""
build_e5_jobs.py - e5, the headline under other wrappers, written once.

The methodology checklist requires several neutral wrappers, because in Paper 2
six arbitrary openings moved baselines by 2 to 5 points. e0 to e4 used one
wrapper: lead-in, one space, question. e5 re-asks e2's 90 contact questions, in
the four cells the deafness headline rests on (the need form and the three
16-word neutral details), under two further wrappers:

    opener   "Quick question for you." before the lead-in, as in Paper 2's
             method 3c (a neutral opening, no content)
    after    the question first, the lead-in after it: position, the
             checklist's counterbalancing item

The original wrapper's answers are e2's, already collected.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (HERE, os.path.join(EXP, "e0-instrument-floor", "scripts"),
          os.path.join(EXP, "e1-measurable-needs", "scripts"),
          os.path.join(EXP, "e2-deaf-contact", "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

import build_e0_stimuli as E0B     # noqa: E402
import build_e2_stimuli as E2B     # noqa: E402

OUT = os.path.join(HERE, "e5_stimuli.json")
OPENER = "Quick question for you."
CELLS = ["need:deaf"] + [f"neutral_long:{k}" for k in E0B.NEUTRAL_LONG]
WRAPPERS = ("opener", "after")


def lead_in(cell):
    fam, key = cell.split(":")
    return E0B.NEED_FORM[key] if fam == "need" else E0B.NEUTRAL_LONG[key]


def prompt(wrapper, lead, question):
    if wrapper == "opener":
        return f"{OPENER} {lead} {question}"
    if wrapper == "after":
        return f"{question} {lead}"
    raise KeyError(wrapper)


def build():
    return {"items": [{"item_id": f"de{i:02d}", "question": q}
                      for i, q in enumerate(E2B.QUESTIONS, 1)],
            "cells": CELLS, "wrappers": list(WRAPPERS),
            "lead_ins": {c: lead_in(c) for c in CELLS}}


def jobs(d):
    out = []
    for it in d["items"]:
        for w in d["wrappers"]:
            for c in d["cells"]:
                out.append({"job_id": f"{w}:{it['item_id']}:{c}", "wrapper": w,
                            "item_id": it["item_id"], "cell_id": c,
                            "messages": [{"role": "user", "content":
                                          prompt(w, d["lead_ins"][c], it["question"])}]})
    return out


META = ("wrapper", "item_id", "cell_id")


if __name__ == "__main__":
    d = build()
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1, ensure_ascii=False)
    j = jobs(d)
    print(f"{OUT}: {len(j)} jobs per model")
    print(j[0]["messages"][0]["content"])
    print(j[4]["messages"][0]["content"])
