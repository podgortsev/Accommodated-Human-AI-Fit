#!/usr/bin/env python3
"""
analyse_e1.py - the read of e1, from the CSVs alone. No GPU, no model.

    python analyse_e1.py e1_qwen.csv [e1_llama.csv e1_mistral.csv]

Instrument: p4_checks version 2 (line-aware plain_language), every answer read
through its first 250 words. Registered in PREREGISTRATION.md before any run.

Item sets, per need N:
    screen_reader, no_vision, wheelchair   the 60 questions of N's own pool
    deaf, plain_language                   every collected question (up to 180)

Per model and need, paired within question, as in e0:
    need benefit, label benefit, specificity, over-application, floors

Registered hypotheses beyond e0:
    H2 add-not-remove   deaf:       d(offers_text_route) - d(no_phone_instruction)
                        wheelchair: d(offers_step_free)  - d(no_walking_assumption)
                        each d = need form minus neutral_long mean. Claimed
                        positive means the need buys an addition more than it
                        removes the barrier.
    H3 need-over-label  plain_language: D(need) - D(label)

Gate 2 counts only the ceiling (none above 0.90): a benefit is a rise, and a
base rate of zero leaves all the room there is. e0's floor rule threw that away.

Verdicts: PASS (need benefit claimed, positive); NULL (not claimed, upper 95%
bound below the margin: 0.25 on a 60-question pool, 0.20 on 180 questions);
INCONCLUSIVE otherwise; UNMEASURABLE at the ceiling.
A need is a finding of the paper if it PASSES on at least two models; H2 and H3
are confirmed if claimed positive on at least two models.
"""

import csv
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in (HERE, os.path.join(REPO, "experiments", "e0-instrument-floor", "scripts"),
          os.path.join(REPO, "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

from p4_checks import NEEDS_V2, check_all_v2     # noqa: E402
import p4_stats as st                            # noqa: E402
import analyse_e0 as A0                          # noqa: E402

POOL_NEEDS = ("screen_reader", "no_vision", "wheelchair")
ALL_ITEM_NEEDS = ("deaf", "plain_language")
POOL_OF_PREFIX = {"sc": "screen_reader", "no": "no_vision", "wh": "wheelchair"}
CEILING = 0.90
MARGIN = {60: 0.25, 180: 0.20}
DETAILS = ("bread", "coast", "brothers")
ADD_REMOVE = {"deaf": ("offers_text_route", "no_phone_instruction"),
              "wheelchair": ("offers_step_free", "no_walking_assumption")}
csv.field_size_limit(10 ** 8)


def margin(n):
    return MARGIN[60] if n <= 90 else MARGIN[180]


def load_table(rows):
    """{item: {cell: {need: {part: 0/1, delivered: 0/1}}}}"""
    t = defaultdict(dict)
    for r in rows:
        scored = check_all_v2(r["answer"])
        t[r["item_id"]][r["cell_id"]] = {n: {k: int(v) for k, v in s.items()}
                                         for n, s in scored.items()}
    return t


def complete(t, items):
    needed = ({"none"} | {f"need:{n}" for n in NEEDS_V2}
              | {f"label:{n}" for n in NEEDS_V2}
              | {f"neutral_long:{k}" for k in DETAILS}
              | {f"neutral_short:{k}" for k in DETAILS})
    return sorted(i for i in items if needed <= set(t.get(i, {})))


def item_set(t, need):
    ids = sorted(t)
    if need in POOL_NEEDS:
        ids = [i for i in ids if POOL_OF_PREFIX.get(i[:2]) == need]
    return complete(t, ids)


def series(t, items, n, part="delivered"):
    D = lambda i, c: t[i][c][n][part]
    nl = {i: sum(D(i, f"neutral_long:{k}") for k in DETAILS) / 3 for i in items}
    ns = {i: sum(D(i, f"neutral_short:{k}") for k in DETAILS) / 3 for i in items}
    mm = {i: sum(D(i, f"need:{m}") for m in NEEDS_V2 if m != n) / (len(NEEDS_V2) - 1)
          for i in items}
    return D, nl, ns, mm


def analyse_model(model, rows):
    t = load_table(rows)
    res, rates, sets = [], {}, {}
    for n in NEEDS_V2:
        items = item_set(t, n)
        sets[n] = items
        if not items:
            rates[n] = None
            continue
        D, nl, ns, mm = series(t, items, n)
        for name, d in (
                ("need_benefit", [D(i, f"need:{n}") - nl[i] for i in items]),
                ("label_benefit", [D(i, f"label:{n}") - ns[i] for i in items]),
                ("specificity", [D(i, f"need:{n}") - mm[i] for i in items]),
                ("over_application", [mm[i] - nl[i] for i in items])):
            res.append(A0.row(n, name, "effect", d))
        for k in DETAILS:
            for fam in ("neutral_long", "neutral_short"):
                res.append(A0.row(n, f"floor {fam}:{k}", "floor",
                                  [D(i, f"{fam}:{k}") - D(i, "none") for i in items]))
        rates[n] = {c: A0.avg(v) for c, v in (
            ("none", [D(i, "none") for i in items]),
            ("neutral_long", list(nl.values())), ("neutral_short", list(ns.values())),
            ("need", [D(i, f"need:{n}") for i in items]),
            ("label", [D(i, f"label:{n}") for i in items]),
            ("mismatched", list(mm.values())))}
        if n == "plain_language":
            res.append(A0.row(n, "H3_need_over_label", "effect",
                              [D(i, f"need:{n}") - D(i, f"label:{n}") for i in items]))
        if n in ADD_REMOVE:
            add, rem = ADD_REMOVE[n]
            Da, nla, _, _ = series(t, items, n, add)
            Dr, nlr, _, _ = series(t, items, n, rem)
            da = [Da(i, f"need:{n}") - nla[i] for i in items]
            dr = [Dr(i, f"need:{n}") - nlr[i] for i in items]
            res.append(A0.row(n, f"part {add}", "part", da))
            res.append(A0.row(n, f"part {rem}", "part", dr))
            res.append(A0.row(n, "H2_add_not_remove", "effect",
                              [a - b for a, b in zip(da, dr)]))
    A0.correct_by_contrast([r for r in res if r["type"] != "part"])
    for r in res:
        if r["type"] == "part":
            r["claimed"], r["bh"] = None, float("nan")

    verdict = {}
    for n in NEEDS_V2:
        r = rates[n]
        if r is None:
            verdict[n] = "NOT COLLECTED"
        elif r["none"] > CEILING:
            verdict[n] = "UNMEASURABLE"
        else:
            b = [x for x in res if x["need"] == n and x["contrast"] == "need_benefit"][0]
            if b["claimed"] and b["mean"] > 0:
                verdict[n] = "PASS"
            elif b["hi"] < margin(b["n"]):
                verdict[n] = "NULL"
            else:
                verdict[n] = "INCONCLUSIVE"
    hyp = {}
    for n, name in (("deaf", "H2_add_not_remove"), ("wheelchair", "H2_add_not_remove"),
                    ("plain_language", "H3_need_over_label")):
        x = [r for r in res if r["need"] == n and r["contrast"] == name]
        hyp[f"{name} {n}"] = bool(x and x[0]["claimed"] and x[0]["mean"] > 0)

    print("=" * 78)
    print(f"e1 | {model} | {len(rows)} answers | instrument v2, first 250 words")
    print("=" * 78)
    print("\nDelivery rate by need and cell (on that need's item set)")
    print(f"  {'need':15}{'n':>4}{'none':>7}{'neutL':>7}{'neutS':>7}{'need':>7}"
          f"{'label':>7}{'mism':>7}")
    for n in NEEDS_V2:
        r = rates[n]
        if r is None:
            print(f"  {n:15}   0  not collected (pool dropped at gate 2)")
            continue
        print(f"  {n:15}{len(sets[n]):4}{r['none']:7.2f}{r['neutral_long']:7.2f}"
              f"{r['neutral_short']:7.2f}{r['need']:7.2f}{r['label']:7.2f}"
              f"{r['mismatched']:7.2f}")
    print("\nContrasts (mean [95% CI], MDE, p rank / p mean, adjusted, claimed)")
    for x in res:
        if x["type"] == "floor":
            continue
        tag = ("CLAIMED" if x["claimed"] else "-") if x["claimed"] is not None \
            else "(part, descriptive)"
        adj = f"adj {x['bh']:.4f}" if x["bh"] == x["bh"] else "          "
        print(f"  {x['need']:15}{x['contrast']:32}{x['mean']:+.3f} "
              f"[{x['lo']:+.3f},{x['hi']:+.3f}] mde {x['mde']:.3f}  "
              f"{x['p_rank']:.4f}/{x['p_mean']:.4f}  {adj}  {tag}")
    print("\nFloor: neutral detail against none (Holm, either test)")
    for n in NEEDS_V2:
        fl = [r for r in res if r["need"] == n and r["type"] == "floor"]
        if fl:
            moved = [r["contrast"].split(" ")[1] for r in fl if r["claimed"]]
            print(f"  {n:15} mean shift {A0.avg([r['mean'] for r in fl]):+.3f}  "
                  f"{'MOVES: ' + ', '.join(moved) if moved else 'no detail moves'}")
    print("\nVerdict per need")
    for n in NEEDS_V2:
        print(f"  {n:15}{verdict[n]}")
    print("\nHypotheses")
    for k, v in hyp.items():
        print(f"  {k:36}{'CLAIMED' if v else '-'}")
    return verdict, hyp


def main(paths):
    by_model = defaultdict(list)
    for p in paths:
        with open(p, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                by_model[r["model"]].append(r)
    out = {m: analyse_model(m, rows) for m, rows in sorted(by_model.items())}
    print("\n" + "=" * 78)
    print("REGISTERED READ ACROSS MODELS")
    print("=" * 78)
    if len(out) < 3:
        print(f"  only {len(out)} of 3 models present: per-model results only")
    for n in NEEDS_V2:
        passes = [m for m, (v, _) in out.items() if v[n] == "PASS"]
        tag = "FINDING" if len(passes) >= 2 else "not a finding"
        print(f"  {n:15}passes on {len(passes)}: {', '.join(passes) or '-':24} {tag}")
    for k in next(iter(out.values()))[1]:
        yes = [m for m, (_, h) in out.items() if h[k]]
        tag = "CONFIRMED" if len(yes) >= 2 else "not confirmed"
        print(f"  {k:36}claimed on {len(yes)}: {', '.join(yes) or '-':20} {tag}")
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
