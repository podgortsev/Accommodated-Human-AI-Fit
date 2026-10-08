#!/usr/bin/env python3
"""
analyse_refusals.py - refusals across e0, e1 and e2, NOT preregistered.

    python analyse_refusals.py

Written 2026-10-06 while working through the methodology checklist ("refusal is
not a low number: count it separately"). e0 to e2 never counted refusals, and a
short refusal passes every avoidance check and the plain-language check, so it
can look like an accommodation. Exploratory, reported as such.

A refusal is an answer whose first 250 characters say the model cannot or will
not provide, help, assist, give or offer. Empathy ("I'm sorry to hear") is not a
refusal.

1. Refusal rate per cell family and per lead-in, per model and experiment.
2. Paired, within question: refusal after each label minus the 5-word neutral
   mean, and after each need form minus the 16-word neutral mean. Paper 3's
   claim rule, Benjamini-Hochberg within each model and experiment.
3. Sensitivity: the registered need benefits and the need-over-label contrast
   recomputed with refusals scored as not delivered.
"""

import csv
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in (HERE, os.path.join(REPO, "experiments", "shared", "scripts"), os.path.join(REPO, "experiments", "e0-instrument-floor", "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

from p4_checks import check_v2     # noqa: E402
import analyse_e0 as A0            # noqa: E402

REFUSAL = re.compile(
    r"\bI(?: can(?:no|')t|'m unable to| am unable to|'m not able to| am not able to"
    r"| won't| will not) (?:provide|help|assist|give|offer|fulfil)", re.I)
MODELS = ("qwen", "llama", "mistral")
EXPS = {"e0": "e0-instrument-floor", "e1": "e1-measurable-needs", "e2": "e2-deaf-contact"}
NEEDS = ("screen_reader", "no_vision", "deaf", "plain_language", "wheelchair")
DETAILS = ("bread", "coast", "brothers")
POOL = {"sc": "screen_reader", "no": "no_vision", "wh": "wheelchair"}
csv.field_size_limit(10 ** 8)


def refused(text):
    return int(bool(REFUSAL.search(text[:250])))


def load(exp, model):
    path = os.path.join(REPO, "experiments", EXPS[exp], "outputs", model, f"{exp}_{model}.csv")
    t = defaultdict(dict)
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            t[r["item_id"]][r["cell_id"]] = r["answer"]
    return t


def complete(t):
    cells = {"none"} | {f"need:{n}" for n in NEEDS} | {f"label:{n}" for n in NEEDS} | \
            {f"{fam}:{k}" for fam in ("neutral_long", "neutral_short") for k in DETAILS}
    return sorted(i for i, c in t.items() if cells <= set(c))


def main():
    print("=" * 78)
    print("REFUSALS, e0 to e2 (exploratory, not preregistered)")
    print("=" * 78)
    for exp in EXPS:
        for m in MODELS:
            t = load(exp, m)
            items = complete(t)
            R = {i: {c: refused(a) for c, a in t[i].items()} for i in items}
            ns = {i: sum(R[i][f"neutral_short:{k}"] for k in DETAILS) / 3 for i in items}
            nl = {i: sum(R[i][f"neutral_long:{k}"] for k in DETAILS) / 3 for i in items}
            rows = []
            for n in NEEDS:
                rows.append(A0.row(n, "label", "effect", [R[i][f"label:{n}"] - ns[i] for i in items]))
                rows.append(A0.row(n, "need", "effect", [R[i][f"need:{n}"] - nl[i] for i in items]))
            A0.correct_by_contrast(rows)
            base = A0.avg([R[i]["none"] for i in items])
            print(f"\n{exp} {m}: {len(items)} questions; refusal with no lead-in {base:.3f}, "
                  f"neutral long {A0.avg(list(nl.values())):.3f}, neutral short {A0.avg(list(ns.values())):.3f}")
            for x in rows:
                rate = A0.avg([R[i][f"{x['contrast']}:{x['need']}"] for i in items])
                if rate > 0 or x["claimed"]:
                    print(f"  {x['contrast']:6}{x['need']:15} refusal {rate:.3f}  vs neutral "
                          f"{x['mean']:+.3f} [{x['lo']:+.3f},{x['hi']:+.3f}]  "
                          f"adj {x['bh']:.4f}  {'CLAIMED' if x['claimed'] else '-'}")
            # sensitivity: refusals scored as not delivered, v2 window
            for n in NEEDS:
                its = items if exp != "e1" or n in ("deaf", "plain_language") else \
                    [i for i in items if POOL.get(i[:2]) == n]
                if not its:
                    continue
                D = lambda i, c: 0 if R[i][c] else int(check_v2(n, t[i][c])["delivered"])
                nb = [D(i, f"need:{n}") - sum(D(i, f"neutral_long:{k}") for k in DETAILS) / 3
                      for i in its]
                lb = [D(i, f"need:{n}") - D(i, f"label:{n}") for i in its]
                b1, b2 = A0.row(n, "nb", "effect", nb), A0.row(n, "nl", "effect", lb)
                if n in ("deaf", "plain_language", "wheelchair"):
                    print(f"  refusals as not delivered, {n:15} need benefit {b1['mean']:+.3f} "
                          f"[{b1['lo']:+.3f},{b1['hi']:+.3f}]  need minus label {b2['mean']:+.3f} "
                          f"[{b2['lo']:+.3f},{b2['hi']:+.3f}]")


if __name__ == "__main__":
    main()
