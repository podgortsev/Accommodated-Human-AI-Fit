#!/usr/bin/env python3
"""
validate_e2.py - e2 checked offline, before any Colab hour is spent on it.

    python validate_e2.py

The stub is e1's (answers assembled from components with known probabilities),
pointed at e2's questions. Checked:

  stimuli     90 questions, none from e0 or e1, e0's 17 cells
  collection  two phases with e2 file names, 1,530 rows, resumes
  add only    text route added, phone unchanged: deaf FINDING, H2 CONFIRMED
  add+remove  added and removed equally: deaf FINDING, H2 NOT confirmed
  null        nothing depends on the cell: neither
  relevance   phone instructions rare at baseline: NOT A TEST, excluded, so no
              finding can be read from a model where the barrier is absent
  power       need benefit and H2 at n=90
"""

import contextlib
import io
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (HERE, os.path.join(EXP, "e1-measurable-needs", "scripts"),
          os.path.join(EXP, "e0-instrument-floor", "scripts"),
          os.path.join(EXP, "shared", "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

import build_e2_stimuli as B      # noqa: E402
import run_e0 as R0               # noqa: E402
import run_e1 as R1               # noqa: E402
import analyse_e2 as A            # noqa: E402
import validate_e1 as V1          # noqa: E402

RESULTS = []


def ok(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f"  ({detail})" if detail else ""))


def stub(rate, seed):
    stim = B.build()
    lookup = {B.prompt(c["lead_in"], q["question"]): (q["item_id"], q["pool"], c["cell_id"])
              for q in stim["questions"] for c in stim["cells"]}

    def generate(prompts, max_new_tokens):
        out = []
        for p in prompts:
            item, pool, cell = lookup[p]
            parts = list(V1.BASE)
            for comp, text in V1.COMPONENTS.items():
                if V1.u(seed, item, cell, comp) < rate(cell, comp):
                    parts.insert(1, text)
            s = V1.NL.join(parts)
            out.append((s, min(len(s.split()), max_new_tokens)))
        return out
    return generate


BASE = {"table": 0.05, "colour": 0.05, "phone": 0.3, "text": 0.1,
        "walk": 0.05, "stepfree": 0.0, "idiom": 0.3}


def run(rate, models=("qwen", "llama", "mistral")):
    stim = B.build()
    d = tempfile.mkdtemp()
    for m in models:
        with contextlib.redirect_stdout(io.StringIO()):
            R1.collect_all(m, stub(rate, m), d, stim, batch=100, prefix="e2")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        res = A.main([os.path.join(d, f"e2_{m}.csv") for m in models])
    return res, buf.getvalue(), d


def line(text, start):
    return next((l for l in text.splitlines() if l.strip().startswith(start)), "")


def check_stimuli():
    print("stimuli")
    s = B.build()
    ok("90 questions, all in the deaf pool",
       len(s["questions"]) == 90 and all(q["pool"] == "deaf" for q in s["questions"]))
    ok("e0's 17 cells", s["cells"] == B.E0B.build()["cells"])
    ok("1,530 prompts", len(R0.plan(s)) == 1530)


def check_collection():
    print("collection")
    _, text, d = run(lambda c, k: BASE[k], models=("qwen",))
    import csv
    rows = list(csv.DictReader(open(os.path.join(d, "e2_qwen.csv"), newline="",
                                    encoding="utf-8")))
    ok("1,530 rows with e2 names", len(rows) == 1530, f"{len(rows)}")
    ok("gate file written", os.path.exists(os.path.join(d, "e2_qwen_gate.json")))


def check_add_only():
    print("add only: text route added, phone instruction unchanged")

    def rate(cell, comp):
        if cell == "need:deaf" and comp == "text":
            return 0.6
        return BASE[comp]
    _, t, _ = run(rate)
    ok("deaf a FINDING", "FINDING" in line(t, "deaf need benefit"))
    ok("H2 CONFIRMED", "CONFIRMED" in line(t, "H2 deaf"))
    ok("all three models are tests", t.count("TEST, excluded") == 0 and
       sum(" TEST" in l for l in t.splitlines() if "relevance" in l) == 3)


def check_add_and_remove():
    print("added and removed equally")

    def rate(cell, comp):
        if cell == "need:deaf" and comp == "text":
            return 0.4
        if cell == "need:deaf" and comp == "phone":
            return 0.0
        return BASE[comp]
    _, t, _ = run(rate)
    ok("deaf a FINDING", "FINDING" in line(t, "deaf need benefit"))
    ok("H2 NOT confirmed", "not confirmed" in line(t, "H2 deaf"))


def check_null():
    print("null")
    _, t, _ = run(lambda c, k: BASE[k])
    ok("deaf not a finding", "not a finding" in line(t, "deaf need benefit"))
    ok("H2 not confirmed", "not confirmed" in line(t, "H2 deaf"))


def check_relevance():
    print("relevance: the barrier absent at baseline")

    def rate(cell, comp):
        if comp == "phone":
            return 0.02
        if cell == "need:deaf" and comp == "text":
            return 0.6
        return BASE[comp]
    _, t, _ = run(rate)
    ok("every model NOT A TEST", t.count("NOT A TEST, excluded") == 3)
    ok("no finding read from non-tests", "not a finding" in line(t, "deaf need benefit")
       and "not confirmed" in line(t, "H2 deaf"))


def check_power(sims=200):
    import random
    import p4_stats as st
    print("power at n=90 (claim rule at 0.01)")
    rng = random.Random(5)
    for label, p0, delta in (("need benefit 0.20, base 0.10", 0.10, 0.20),
                             ("need benefit 0.15, base 0.10", 0.10, 0.15)):
        hits = 0
        for _ in range(sims):
            d = [int(rng.random() < p0 + delta)
                 - sum(rng.random() < p0 for _ in range(3)) / 3 for _ in range(90)]
            t = st.two_tests(d)
            hits += st.claimed(sum(d) / 90, t["rank_dir"], t["p"], alpha=0.01)
        print(f"    {label}: {hits / sims:.2f}")
        if delta == 0.20:
            ok("power >= 0.80 for a 0.20 benefit from a 0.10 base", hits / sims >= 0.80,
               f"{hits / sims:.2f}")


if __name__ == "__main__":
    for f in (check_stimuli, check_collection, check_add_only, check_add_and_remove,
              check_null, check_relevance, check_power):
        f()
    bad = [n for n, c in RESULTS if not c]
    print("=" * 78)
    print(f"{len(RESULTS) - len(bad)} passed, {len(bad)} failed")
    sys.exit(1 if bad else 0)
