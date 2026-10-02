#!/usr/bin/env python3
"""
analyse_e3.py - the read of e3, from the CSVs alone. No GPU, no model.

    python analyse_e3.py e3_qwen.csv [e3_llama.csv e3_mistral.csv]

Instrument version 2, 250-word window, on the follow-up answer. A first turn
"kept the barrier" if its own text carries a phone instruction (same check).

Primary set, per model: the first turns that kept the barrier. For each, the
three follow-ups are compared paired within the first turn. Removal is measured
where there was something to remove, as a share of those answers: the lesson of
e1, where an absolute-points comparison let a large addition outweigh the
near-total removal of a rare barrier.

    H4 restate over neutral    removed(restate)  - removed(neutral)
    H5 specific over restate   removed(specific) - removed(restate)

removed = 1 if the follow-up answer carries no phone instruction. The Paper 3
claim rule; one family per contrast per model. Confirmed if claimed positive on
at least two models. A model with fewer than 10 first turns that kept the
barrier is NOT A TEST.

Reported beside them: the phone instruction left after each follow-up, the
text route offered, and the same on all first turns.
"""

import csv
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in (HERE, os.path.join(REPO, "scripts"),
          os.path.join(REPO, "experiments", "e0-instrument-floor", "scripts")):
    if os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)

from p4_checks import check_v2    # noqa: E402
import p4_stats as st             # noqa: E402
import analyse_e0 as A0           # noqa: E402

MIN_SET = 10
KINDS = ("neutral", "restate", "specific")
csv.field_size_limit(10 ** 8)


def phone(text):
    return int(not check_v2("deaf", text)["no_phone_instruction"])


def text_route(text):
    return int(check_v2("deaf", text)["offers_text_route"])


def load_turn1(path=None):
    with open(path or os.path.join(HERE, "e3_turn1.json"), encoding="utf-8") as f:
        d = json.load(f)
    return {m: {f"{t['source']}:{t['item_id']}": phone(t["turn1"]) for t in rows}
            for m, rows in d["turn1"].items()}


def analyse_model(model, rows, turn1):
    by = defaultdict(dict)
    for r in rows:
        by[f"{r['source']}:{r['item_id']}"][r["follow_up"]] = r["answer"]
    full = [k for k, v in by.items() if set(KINDS) <= set(v)]
    kept = [k for k in full if turn1[model].get(k) == 1]
    test = len(kept) >= MIN_SET

    def rate(keys, kind, fn):
        return A0.avg([fn(by[k][kind]) for k in keys]) if keys else float("nan")

    res = []
    if kept:
        rem = {k: {f: 1 - phone(by[k][f]) for f in KINDS} for k in kept}
        for name, a, b in (("H4_restate_over_neutral", "restate", "neutral"),
                           ("H5_specific_over_restate", "specific", "restate"),
                           ("specific_over_neutral", "specific", "neutral")):
            res.append(A0.row("deaf", name, "effect", [rem[k][a] - rem[k][b] for k in kept]))
        A0.correct_by_contrast(res)

    print("=" * 78)
    print(f"e3 | {model} | {len(full)} first turns, {len(kept)} kept the phone "
          f"instruction | {'TEST' if test else 'NOT A TEST'}")
    print("=" * 78)
    print("\nOn first turns that kept the barrier: share of follow-ups that ...")
    print(f"  {'follow-up':10}{'still phone':>13}{'text route':>12}")
    for f in KINDS:
        print(f"  {f:10}{rate(kept, f, phone):13.2f}{rate(kept, f, text_route):12.2f}")
    print("\nOn all first turns (secondary)")
    print(f"  first turn  phone {A0.avg([turn1[model].get(k, 0) for k in full]):.2f}")
    for f in KINDS:
        print(f"  {f:10}  phone {rate(full, f, phone):.2f}  text route {rate(full, f, text_route):.2f}")
    print("\nContrasts on the barrier set (removed = no phone instruction)")
    for x in res:
        print(f"  {x['contrast']:28}{x['mean']:+.3f} [{x['lo']:+.3f},{x['hi']:+.3f}] "
              f"mde {x['mde']:.3f}  {x['p_rank']:.4f}/{x['p_mean']:.4f}  "
              f"adj {x['bh']:.4f}  {'CLAIMED' if x['claimed'] else '-'}")
    hyp = {x["contrast"]: bool(test and x["claimed"] and x["mean"] > 0)
           for x in res if x["contrast"].startswith("H")}
    return test, hyp


def main(paths, turn1_path=None):
    turn1 = load_turn1(turn1_path)
    by_model = defaultdict(list)
    for p in paths:
        with open(p, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                by_model[r["model"]].append(r)
    out = {m: analyse_model(m, rows, turn1) for m, rows in sorted(by_model.items())}
    print("\n" + "=" * 78)
    print("REGISTERED READ, e3")
    print("=" * 78)
    for h in ("H4_restate_over_neutral", "H5_specific_over_restate"):
        yes = [m for m, (t, hy) in out.items() if hy.get(h)]
        tests = [m for m, (t, _) in out.items() if t]
        print(f"  {h:28} claimed on {len(yes)} of {len(tests)} tests: "
              f"{', '.join(yes) or '-':24} {'CONFIRMED' if len(yes) >= 2 else 'not confirmed'}")
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
