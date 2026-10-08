#!/usr/bin/env python3
"""
analyse_e5.py - the deafness headline under three wrappers. No GPU.

    python analyse_e5.py e5_qwen.csv [e5_llama.csv e5_mistral.csv]

Per model and wrapper (original = e2's answers; opener; after), paired within
question, instrument v2, 250-word window:

    need benefit   D(need:deaf) - mean D(neutral_long:k)
    H2             d(offers_text_route) - d(no_phone_instruction)

Registered read: the headline holds under a wrapper if both are claimed
positive on at least two models under that wrapper. Reported beside it: the
spread of each estimate across the three wrappers, the checklist's error bar.
"""

import csv
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in (HERE, os.path.join(REPO, "experiments", "shared", "scripts"),
          os.path.join(REPO, "experiments", "e0-instrument-floor", "scripts")):
    if os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)

from p4_checks import check_v2    # noqa: E402
import analyse_e0 as A0           # noqa: E402

DETAILS = ("bread", "coast", "brothers")
CELLS = ["need:deaf"] + [f"neutral_long:{k}" for k in DETAILS]
E2_DIR = os.path.join(REPO, "experiments", "e2-deaf-contact", "outputs")
csv.field_size_limit(10 ** 8)


def score(text):
    c = check_v2("deaf", text)
    return int(c["delivered"]), int(c["offers_text_route"]), int(c["no_phone_instruction"])


def read(model, rows, e2_path=None):
    t = defaultdict(lambda: defaultdict(dict))
    for r in rows:
        t[r["wrapper"]][r["item_id"]][r["cell_id"]] = score(r["answer"])
    path = e2_path or os.path.join(E2_DIR, model, f"e2_{model}.csv")
    if os.path.exists(path):
        with open(path, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["cell_id"] in CELLS:
                    t["original"][r["item_id"]][r["cell_id"]] = score(r["answer"])
    return t


def contrasts(tw):
    items = sorted(i for i, c in tw.items() if set(CELLS) <= set(c))
    nl = lambda i, k: sum(tw[i][f"neutral_long:{d}"][k] for d in DETAILS) / 3
    nb = [tw[i]["need:deaf"][0] - nl(i, 0) for i in items]
    da = [tw[i]["need:deaf"][1] - nl(i, 1) for i in items]
    dr = [tw[i]["need:deaf"][2] - nl(i, 2) for i in items]
    return items, [A0.row("deaf", "need_benefit", "effect", nb),
                   A0.row("deaf", "H2_add_not_remove", "effect",
                          [a - b for a, b in zip(da, dr)])], (A0.avg(da), A0.avg(dr))


def main(paths, e2_paths=None):
    by_model = defaultdict(list)
    for p in paths:
        with open(p, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                by_model[r["model"]].append(r)
    hold = defaultdict(lambda: defaultdict(int))
    for m, rows in sorted(by_model.items()):
        t = read(m, rows, (e2_paths or {}).get(m))
        print("=" * 78)
        print(f"e5 | {m}")
        print("=" * 78)
        est = defaultdict(list)
        for w in ("original", "opener", "after"):
            if w not in t:
                print(f"  {w:9} not available")
                continue
            items, res, (da, dr) = contrasts(t[w])
            A0.correct_by_contrast(res)
            ok = all(x["claimed"] and x["mean"] > 0 for x in res)
            for x in res:
                est[x["contrast"]].append(x["mean"])
            hold[w]["n"] += 1
            hold[w]["yes"] += ok
            print(f"  {w:9} n={len(items):3}  text route {da:+.2f}  phone removed {dr:+.2f}")
            for x in res:
                print(f"      {x['contrast']:20}{x['mean']:+.3f} [{x['lo']:+.3f},{x['hi']:+.3f}]"
                      f"  adj {x['bh']:.4f}  {'CLAIMED' if x['claimed'] else '-'}")
        for k, v in est.items():
            print(f"  spread across wrappers, {k:20} {min(v):+.3f} to {max(v):+.3f}")
    print("\n" + "=" * 78)
    print("REGISTERED READ, e5")
    print("=" * 78)
    for w in ("original", "opener", "after"):
        y = hold[w]["yes"]
        print(f"  {w:9} headline holds on {y} of {hold[w]['n']} models: "
              f"{'HOLDS' if y >= 2 else 'does not hold'}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
