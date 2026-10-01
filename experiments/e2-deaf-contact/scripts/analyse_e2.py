#!/usr/bin/env python3
"""
analyse_e2.py - the read of e2, from the CSVs alone. No GPU, no model.

    python analyse_e2.py e2_qwen.csv [e2_llama.csv e2_mistral.csv]

Per model, e1's analysis unchanged (analyse_e1.analyse_model: instrument v2,
250-word window, the claim rule, the corrections), on e2's 90 questions.

Added before any e2 data, from e1's mistake: a RELEVANCE check. The deaf need is
only tested where the ordinary answer tells people to phone. If a phone
instruction appears in fewer than 0.10 of a model's `none` answers, that model's
deaf result is NOT A TEST and is excluded from the registered read, whatever it
says.

Registered read:
    deaf is a finding if it PASSES on at least two models that are tests;
    H2 for deaf is confirmed if claimed positive on at least two models that
    are tests. plain_language is reported as a secondary replication.
"""

import csv
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.abspath(os.path.join(HERE, "..", ".."))
REPO = os.path.abspath(os.path.join(EXP, ".."))
for p in (HERE, os.path.join(EXP, "e1-measurable-needs", "scripts"),
          os.path.join(EXP, "e0-instrument-floor", "scripts"),
          os.path.join(REPO, "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

import analyse_e1 as A1            # noqa: E402
from p4_checks import check_v2     # noqa: E402

RELEVANCE = 0.10
csv.field_size_limit(10 ** 8)


def phone_rate(rows):
    none = [r for r in rows if r["cell_id"] == "none"]
    if not none:
        return float("nan")
    return sum(not check_v2("deaf", r["answer"])["no_phone_instruction"]
               for r in none) / len(none)


def main(paths):
    by_model = defaultdict(list)
    for p in paths:
        with open(p, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                by_model[r["model"]].append(r)
    res = {}
    for m, rows in sorted(by_model.items()):
        v, h = A1.analyse_model(m, rows)
        rate = phone_rate(rows)
        test = rate >= RELEVANCE
        print(f"\nRelevance: phone instruction in {rate:.2f} of none answers "
              f"(threshold {RELEVANCE:.2f}): {'TEST' if test else 'NOT A TEST'}")
        res[m] = (v, h, test, rate)

    print("\n" + "=" * 78)
    print("REGISTERED READ, e2")
    print("=" * 78)
    if len(res) < 3:
        print(f"  only {len(res)} of 3 models present: per-model results only")
    tests = [m for m, (_, _, t, _) in res.items() if t]
    for m, (_, _, t, rate) in res.items():
        print(f"  {m:10} relevance {rate:.2f}  {'TEST' if t else 'NOT A TEST, excluded'}")
    deaf = [m for m in tests if res[m][0]["deaf"] == "PASS"]
    h2 = [m for m in tests if res[m][1]["H2_add_not_remove deaf"]]
    pl = [m for m, (v, _, _, _) in res.items() if v["plain_language"] == "PASS"]
    print(f"  deaf need benefit   passes on {len(deaf)} of {len(tests)} tests: "
          f"{', '.join(deaf) or '-':24} {'FINDING' if len(deaf) >= 2 else 'not a finding'}")
    print(f"  H2 deaf             claimed on {len(h2)} of {len(tests)} tests: "
          f"{', '.join(h2) or '-':24} {'CONFIRMED' if len(h2) >= 2 else 'not confirmed'}")
    print(f"  plain_language      passes on {len(pl)}: {', '.join(pl) or '-'} (secondary)")
    return res


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
