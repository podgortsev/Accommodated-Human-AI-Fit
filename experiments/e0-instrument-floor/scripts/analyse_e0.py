#!/usr/bin/env python3
"""
analyse_e0.py - the read of e0, from the CSVs alone. No GPU, no model.

    python analyse_e0.py e0_qwen.csv [e0_llama.csv e0_mistral.csv]

Every answer is scored on all five needs by scripts/p4_checks.py, whatever was
disclosed, so one generation serves the matched, mismatched, neutral and none
reads at once.

Per model, per need N, paired within question:

    need benefit      D(need:N)  - mean D(neutral_long:*)     THE GATE
    label benefit     D(label:N) - mean D(neutral_short:*)
    specificity       D(need:N)  - mean D(need:M), M != N
    over-application  mean D(need:M), M != N  - mean D(neutral_long:*)
    floor, x6         D(neutral_*:k) - D(none)                 reported

D is 1 if the answer delivered N, else 0. Contrasts use the Paper 3 claim rule
(p4_stats): an effect is claimed only if the signed-rank test AND the sign-flip
permutation test both reject after Benjamini-Hochberg, and both lean the same
way. One BH family per contrast type per model (five needs each), so the gate,
need benefit, is corrected only among its own five tests. Floors are their own family per model, Holm on either
test, and "moves" means either test rejects.

The floor is reported, not used as a kill switch: the benefit is read against
the neutral arm, so a neutral detail that moves delivery by itself is already
subtracted. Whether it moves is a finding in its own right (the "any person"
effect).

Registered decision (PREREGISTRATION.md):
    gate 2  a need is UNMEASURABLE on a model if its `none` delivery rate is
            above 0.90 or below 0.02
    gate 1  a need PASSES on a model if its need benefit is claimed and positive;
            is NULL if not claimed and the upper 95% bound of the benefit is
            below 0.20 (a benefit worth a paper is excluded); is INCONCLUSIVE
            otherwise. At n=120 the gate has power of about 0.8 for a difference
            of 0.20 (validate_e0.py); a non-claim alone is not a null.
    CONTINUE if at least two needs PASS on at least two of the three models.
    EXTEND   if not, but counting INCONCLUSIVE as PASS would reach CONTINUE:
             collect e0b, 120 further questions, and decide on all 240.
    STOP     otherwise, and report e0 as the result.
"""

import csv
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "shared", "scripts")))
sys.path.insert(0, HERE)

from p4_checks import NEEDS, check_all          # noqa: E402
import p4_stats as st                            # noqa: E402

HEADROOM_HI = 0.90
HEADROOM_LO = 0.02
PASS_NEEDS = 2
PASS_MODELS = 2
NULL_MARGIN = 0.20
csv.field_size_limit(10 ** 8)


def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def delivery_table(rows):
    """{item_id: {cell_id: {need: 0/1}}} plus per-part rates for printing."""
    table = defaultdict(dict)
    parts = defaultdict(lambda: defaultdict(list))
    for r in rows:
        scored = check_all(r["answer"])
        table[r["item_id"]][r["cell_id"]] = {n: int(scored[n]["delivered"])
                                             for n in NEEDS}
        fam = r["cell_id"].split(":")[0]
        for n, res in scored.items():
            for k, v in res.items():
                if k != "delivered":
                    parts[(fam, n)][k].append(int(v))
    return table, parts


def cell_ids(table):
    return sorted({c for cells in table.values() for c in cells})


def complete_items(table, needed):
    """Only questions with every cell present enter a paired test."""
    return sorted(i for i, cells in table.items() if needed <= set(cells))


def contrasts(table, needs, details):
    needed = ({"none"} | {f"need:{n}" for n in needs} | {f"label:{n}" for n in needs}
              | {f"neutral_long:{k}" for k in details}
              | {f"neutral_short:{k}" for k in details})
    items = complete_items(table, needed)
    rows, rates = [], {}
    for n in needs:
        D = lambda i, c: table[i][c][n]
        nl = {i: sum(D(i, f"neutral_long:{k}") for k in details) / len(details)
              for i in items}
        ns = {i: sum(D(i, f"neutral_short:{k}") for k in details) / len(details)
              for i in items}
        mm = {i: sum(D(i, f"need:{m}") for m in needs if m != n) / (len(needs) - 1)
              for i in items}
        series = {
            "need_benefit": [D(i, f"need:{n}") - nl[i] for i in items],
            "label_benefit": [D(i, f"label:{n}") - ns[i] for i in items],
            "specificity": [D(i, f"need:{n}") - mm[i] for i in items],
            "over_application": [mm[i] - nl[i] for i in items],
        }
        for name, d in series.items():
            rows.append(row(n, name, "effect", d))
        for k in details:
            for fam in ("neutral_long", "neutral_short"):
                d = [D(i, f"{fam}:{k}") - D(i, "none") for i in items]
                rows.append(row(n, f"floor {fam}:{k}", "floor", d))
        rates[n] = {
            "none": avg([D(i, "none") for i in items]),
            "need": avg([D(i, f"need:{n}") for i in items]),
            "label": avg([D(i, f"label:{n}") for i in items]),
            "neutral_long": avg(list(nl.values())),
            "neutral_short": avg(list(ns.values())),
            "mismatched": avg(list(mm.values())),
        }
    return rows, rates, len(items)


def avg(x):
    return sum(x) / len(x) if x else float("nan")


def row(need, contrast, kind, d):
    t = st.two_tests(d)
    mean, lo, hi = st.boot_ci(d)
    return {"need": need, "contrast": contrast, "type": kind, "n": len(d),
            "mean": mean, "lo": lo, "hi": hi, "mde": st.mde(d), **t}


def correct_by_contrast(rows):
    """One family per contrast type within a model: the five need benefits are
    the registered gate and are corrected only among themselves. Pooling all
    twenty contrasts let strong real effects make Benjamini-Hochberg lenient
    for the null ones; the offline validator caught a false specificity claim
    that way. Floors stay one Holm family per model, on either test."""
    kinds = {}
    for r in rows:
        kinds.setdefault("floor" if r["type"] == "floor" else r["contrast"],
                         []).append(r)
    for fam in kinds.values():
        st.correct(fam, group=("type",))


def verdicts(rows, rates):
    out = {}
    for n, r in rates.items():
        if not (HEADROOM_LO <= r["none"] <= HEADROOM_HI):
            out[n] = "UNMEASURABLE"
            continue
        b = [x for x in rows if x["need"] == n and x["contrast"] == "need_benefit"][0]
        if b["claimed"] and b["mean"] > 0:
            out[n] = "PASS"
        elif b["hi"] < NULL_MARGIN:
            out[n] = "NULL"
        else:
            out[n] = "INCONCLUSIVE"
    return out


def length_report(rows):
    by = defaultdict(list)
    trunc = defaultdict(list)
    for r in rows:
        fam = r["cell_id"].split(":")[0]
        by[fam].append(len(r["answer"].split()))
        trunc[fam].append(r.get("truncated", "0") in ("1", "True", "true"))
    return {f: (avg(by[f]), avg([int(x) for x in trunc[f]]), len(by[f])) for f in by}


def analyse_model(model, rows):
    table, parts = delivery_table(rows)
    needs = list(NEEDS)
    details = sorted({c.split(":")[1] for c in cell_ids(table)
                      if c.startswith("neutral_long:")})
    res, rates, n_items = contrasts(table, needs, details)
    correct_by_contrast(res)
    v = verdicts(res, rates)

    print("=" * 78)
    print(f"e0 | {model} | {n_items} complete questions, {len(rows)} answers")
    print("=" * 78)
    print("\nLength and truncation by cell family (words, share truncated, n)")
    for f, (w, t, k) in sorted(length_report(rows).items()):
        print(f"  {f:14} {w:7.1f}  {t:5.2f}  {k}")

    print("\nDelivery rate by need and cell")
    print(f"  {'need':15}{'none':>7}{'neutL':>7}{'neutS':>7}{'need':>7}"
          f"{'label':>7}{'mism':>7}")
    for n in needs:
        r = rates[n]
        print(f"  {n:15}{r['none']:7.2f}{r['neutral_long']:7.2f}"
              f"{r['neutral_short']:7.2f}{r['need']:7.2f}{r['label']:7.2f}"
              f"{r['mismatched']:7.2f}")

    print("\nParts in the none cell (share holding), to see which part binds")
    for n in needs:
        ps = parts[("none", n)]
        print(f"  {n:15}" + "  ".join(f"{k}={avg(v):.2f}" for k, v in ps.items()))

    print("\nContrasts (mean [95% CI], MDE, p rank / p mean, adjusted, claimed)")
    for n in needs:
        for x in [r for r in res if r["need"] == n and r["type"] == "effect"]:
            print(f"  {n:15}{x['contrast']:17}{x['mean']:+.3f} "
                  f"[{x['lo']:+.3f},{x['hi']:+.3f}] mde {x['mde']:.3f}  "
                  f"{x['p_rank']:.4f}/{x['p_mean']:.4f}  adj {x['bh']:.4f}  "
                  f"{'CLAIMED' if x['claimed'] else '-'}")

    print("\nFloor: neutral detail against none (Holm, either test)")
    for n in needs:
        fl = [r for r in res if r["need"] == n and r["type"] == "floor"]
        moved = [r["contrast"].split(" ")[1] for r in fl if r["claimed"]]
        mean = avg([r["mean"] for r in fl])
        print(f"  {n:15} mean shift {mean:+.3f}  "
              f"{'MOVES: ' + ', '.join(moved) if moved else 'no detail moves'}")

    print("\nVerdict per need (gate 2 headroom, then gate 1 need benefit)")
    for n in needs:
        print(f"  {n:15}{v[n]}")
    return v


def main(paths):
    by_model = defaultdict(list)
    for p in paths:
        for r in load(p):
            by_model[r["model"]].append(r)
    all_v = {m: analyse_model(m, rows) for m, rows in sorted(by_model.items())}

    print("\n" + "=" * 78)
    print("REGISTERED DECISION")
    print("=" * 78)
    passing = {m: [n for n, x in v.items() if x == "PASS"] for m, v in all_v.items()}
    for m, ns in passing.items():
        print(f"  {m:10} passes: {', '.join(ns) if ns else 'none'}")
    good = [m for m, ns in passing.items() if len(ns) >= PASS_NEEDS]
    maybe = [m for m, v in all_v.items()
             if sum(x in ("PASS", "INCONCLUSIVE") for x in v.values()) >= PASS_NEEDS]
    if len(all_v) < 3:
        print(f"  only {len(all_v)} of 3 models present: no decision yet")
    elif len(good) >= PASS_MODELS:
        print(f"  CONTINUE: {len(good)} models with >= {PASS_NEEDS} passing needs")
    elif len(maybe) >= PASS_MODELS:
        print(f"  EXTEND: {len(good)} models pass, {len(maybe)} would with the "
              f"inconclusive needs. Collect e0b (120 more questions), decide on 240.")
    else:
        print(f"  STOP: {len(good)} models with >= {PASS_NEEDS} passing needs, "
              f"{PASS_MODELS} required, and the rest are nulls. e0 is the result.")
    return all_v


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
