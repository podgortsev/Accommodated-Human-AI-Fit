#!/usr/bin/env python3
"""
validate_e0.py - e0 checked offline, before any Colab hour is spent on it.

    python validate_e0.py

No torch, no transformers, no GPU. The model is replaced by a stub whose
answers carry violations of each need at rates set per cell, so every read has
a known right answer. Checked:

  stimuli     word counts, 2,040 prompts, lead-in placement, none = question
  collection  run_e0.collect on the stub: schema, no duplicates, resumes after
              a session dies mid-run, truncation flag
  scoring     the stub's violation sentences break exactly the need they target
  effect      need-form lowers violations of that need only: every need PASSES,
              specificity is claimed, floors do not move, decision CONTINUE
  null        nothing depends on the lead-in: every need FAILS, decision STOP
  any person  every lead-in, neutral included, lowers violations equally: the
              floor MOVES, the benefit is NOT claimed, decision STOP
  over-apply  any need-form lowers every need: benefit claimed, specificity
              NOT claimed, over-application claimed
  headroom    a need delivered always in `none` is UNMEASURABLE, not FAIL
  margin      a real +0.25 is never NULL; a real +0.15 never leads to STOP
  smoke       the GPU self-check stops on template leakage and empty answers
  power       the gate's power at n=120, printed for the preregistration
"""

import contextlib
import hashlib
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "scripts")))

import build_e0_stimuli as B      # noqa: E402
import run_e0 as R                # noqa: E402
import analyse_e0 as A            # noqa: E402
from p4_checks import check_all   # noqa: E402

RESULTS = []


def ok(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f"  ({detail})" if detail else ""))


# -------------------------------------------------------------- the stub model

BASE = ["Start by gathering your documents.", "Then open the service page.",
        "Fill in the form with your details.", "Keep a copy for your records."]
VIOLATE = {
    "screen_reader": ("| Step | Action |\n| 1 | Apply |", ""),
    "no_vision": ("Press the green button.", "Press the Submit button."),
    "deaf": ("Call the helpline to confirm.", "Send them a message by email to confirm."),
    "plain_language": ("It is a piece of cake.", "It is quick."),
    "wheelchair": ("Walk to the branch to finish.", "Use the step-free entrance at the branch."),
}


def u(*key):
    h = hashlib.sha256("|".join(map(str, key)).encode()).hexdigest()
    return int(h[:12], 16) / float(16 ** 12)


def stub(rate_fn, seed="s"):
    """rate_fn(cell_id, need) -> probability that the answer VIOLATES need."""
    lookup = {}
    stim = B.build()
    for q in stim["questions"]:
        for c in stim["cells"]:
            lookup[B.prompt(c["lead_in"], q["question"])] = (q["item_id"], c["cell_id"])

    def generate(prompts, max_new_tokens):
        out = []
        for p in prompts:
            item, cell = lookup[p]
            parts = list(BASE)
            for n, (bad, good) in VIOLATE.items():
                v = u(seed, item, cell, n) < rate_fn(cell, n)
                s = bad if v else good
                if s:
                    parts.insert(2, s)
            text = "\n".join(parts)
            out.append((text, min(len(text.split()), max_new_tokens)))
        return out
    return generate


def run_scenario(rate_fn, models=("qwen", "llama", "mistral")):
    stim = B.build()
    d = tempfile.mkdtemp()
    paths = []
    for m in models:
        p = os.path.join(d, f"e0_{m}.csv")
        with contextlib.redirect_stdout(io.StringIO()):
            R.collect(m, stub(rate_fn, seed=m), p, stim, batch=64)
        paths.append(p)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        v = A.main(paths)
    return v, buf.getvalue()


def decision(text):
    for line in text.splitlines():
        s = line.strip()
        if s.startswith(("CONTINUE", "STOP", "EXTEND")):
            return s.split(":")[0]
    return None


def rows_of(text, need, contrast):
    return [l for l in text.splitlines()
            if l.strip().startswith(need) and contrast in l]


# ---------------------------------------------------------------------- checks

def check_stimuli():
    print("stimuli")
    s = B.build()
    ok("120 questions x 17 cells", len(s["questions"]) == 120 and len(s["cells"]) == 17)
    ok("2,040 prompts in the plan", len(R.plan(s)) == 2040)
    for c in s["cells"]:
        want = {"none": 0, "need": 16, "label": 5,
                "neutral_long": 16, "neutral_short": 5}[c["family"]]
        if B.word_count(c["lead_in"]) != want:
            ok(f"word count {c['cell_id']}", False)
    ok("every lead-in has its registered word count", True)
    q = s["questions"][0]["question"]
    ok("none is the question alone", B.prompt("", q) == q)
    ok("lead-in comes first, one space", B.prompt("X y.", q) == "X y. " + q)
    ok("need form never names a checked property",
       not any(w in s_.lower() for s_ in B.NEED_FORM.values()
               for w in ("table", "emoji", "colour", "color", "phone", "email",
                         "lift", "ramp", "step-free", "sentence")))


def check_scoring():
    print("scoring: each stub violation breaks exactly its own need")
    for n, (bad, good) in VIOLATE.items():
        clean = "\n".join(BASE[:2] + [g for _, g in VIOLATE.values() if g] + BASE[2:])
        dirty = clean.replace(good, bad) if good else clean + "\n" + bad
        c, dd = check_all(clean), check_all(dirty)
        ok(f"clean answer delivers {n}", c[n]["delivered"])
        others = [m for m in VIOLATE if m != n and not dd[m]["delivered"]]
        ok(f"violation breaks {n} and nothing else",
           not dd[n]["delivered"] and not others, f"also broke {others}" if others else "")


def check_collection():
    print("collection")
    stim = B.build()
    d = tempfile.mkdtemp()
    p = os.path.join(d, "e0_qwen.csv")
    gen = stub(lambda c, n: 0.5)
    calls = {"n": 0}

    def dying(prompts, mnt):
        calls["n"] += 1
        if calls["n"] == 4:
            raise RuntimeError("session died")
        return gen(prompts, mnt)
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            R.collect("qwen", dying, p, stim, batch=50)
        except RuntimeError:
            pass
        partial = len(R.done_keys(p))
        R.collect("qwen", gen, p, stim, batch=50)
    import csv
    with open(p, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    keys = [(r["item_id"], r["cell_id"]) for r in rows]
    ok("the dead session kept its finished batches", partial == 150, f"{partial}")
    ok("resume completes to 2,040 rows", len(rows) == 2040, f"{len(rows)}")
    ok("no (item, cell) twice", len(set(keys)) == len(keys))
    ok("schema", list(rows[0]) == R.FIELDS)
    with contextlib.redirect_stdout(io.StringIO()):
        R.collect("qwen", lambda ps, m: [("x " * m, m) for _ in ps],
                  os.path.join(d, "t.csv"), stim, batch=10, limit=10,
                  max_new_tokens=7)
    with open(os.path.join(d, "t.csv"), newline="", encoding="utf-8") as f:
        t = list(csv.DictReader(f))
    ok("truncation flag set at max_new_tokens", all(r["truncated"] == "1" for r in t))


def check_smoke():
    print("smoke self-check on the stub")
    stim = B.build()
    good = stub(lambda c, n: 0.5)
    leak = "<|im_start|>assistant Hi"
    with contextlib.redirect_stdout(io.StringIO()):
        a = R.smoke(good, stim)
        b = R.smoke(lambda ps, m: [(leak, 3) for _ in ps], stim)
        c = R.smoke(lambda ps, m: [("", 0) for _ in ps], stim)
    ok("smoke passes a clean generator", a)
    ok("smoke stops on template leakage", not b)
    ok("smoke stops on empty answers", not c)


def check_effect():
    print("effect: need form lowers that need's violations only")

    def rate(cell, n):
        if cell == f"need:{n}":
            return 0.05
        if cell == f"label:{n}":
            return 0.25
        return 0.6
    v, out = run_scenario(rate)
    ok("every need PASSES on every model",
       all(x == "PASS" for m in v.values() for x in m.values()))
    ok("specificity claimed for every need",
       all("CLAIMED" in l for n in VIOLATE for l in rows_of(out, n, "specificity")))
    lab = sum("CLAIMED" in l for n in VIOLATE for l in rows_of(out, n, "label_benefit"))
    ok("label benefit (+0.35 injected) claimed in at least 14 of 15 cells",
       lab >= 14, f"{lab} of 15; ")
    ok("over-application NOT claimed",
       not any("CLAIMED" in l for n in VIOLATE for l in rows_of(out, n, "over_application")))
    moves = out.count("MOVES:")
    ok("floors do not move", moves == 0, f"{moves} of 15 moved")
    ok("decision CONTINUE", decision(out) == "CONTINUE")
    line = [l for l in out.splitlines() if l.strip().startswith("deaf ")][0]
    none_rate, need_rate = float(line.split()[1]), float(line.split()[4])
    ok("rates near the injected truth (none 0.40, need 0.95)",
       abs(none_rate - 0.40) < 0.15 and abs(need_rate - 0.95) < 0.1,
       f"none {none_rate}, need {need_rate}")


def check_null():
    print("null: nothing depends on the lead-in")
    v, out = run_scenario(lambda c, n: 0.6)
    ok("no need passes on any model",
       not any(x == "PASS" for m in v.values() for x in m.values()))
    nulls = sum(x == "NULL" for m in v.values() for x in m.values())
    ok("at least 13 of 15 cells read as NULL, not merely unclaimed", nulls >= 13,
       f"{nulls} of 15")
    claims = sum("CLAIMED" in l for l in out.splitlines())
    ok("at most one false claim across 60 contrasts", claims <= 1, f"{claims}")
    ok("decision STOP", decision(out) == "STOP")


def check_any_person():
    print("any person: every lead-in lowers violations equally")
    v, out = run_scenario(lambda c, n: 0.6 if c == "none" else 0.15)
    ok("benefit not claimed anywhere",
       not any(x == "PASS" for m in v.values() for x in m.values()))
    ok("floor MOVES for every need on every model", out.count("MOVES:") == 15,
       f"{out.count('MOVES:')} of 15")
    ok("decision STOP", decision(out) == "STOP")


def check_over_application():
    print("over-application: any need form lowers every need")

    def rate(cell, n):
        return 0.08 if cell.startswith("need:") else 0.6
    v, out = run_scenario(rate)
    ok("need benefit claimed (it is real against neutral)",
       all(x == "PASS" for m in v.values() for x in m.values()))
    ok("specificity NOT claimed",
       not any("CLAIMED" in l for n in VIOLATE for l in rows_of(out, n, "specificity")))
    ok("over-application claimed for every need",
       all("CLAIMED" in l for n in VIOLATE for l in rows_of(out, n, "over_application")))


def check_headroom():
    print("headroom: a need always delivered in none")

    def rate(cell, n):
        if n == "deaf":
            return 0.0
        return 0.05 if cell == f"need:{n}" else 0.6
    v, out = run_scenario(rate)
    ok("deaf is UNMEASURABLE on every model",
       all(m["deaf"] == "UNMEASURABLE" for m in v.values()))
    ok("the other needs still PASS",
       all(m[n] == "PASS" for m in v.values() for n in m if n != "deaf"))


def check_power(sims=200):
    """Power of the registered gate at n=120, by simulation on the claim rule.

    Delivery in the neutral cells is Bernoulli(p0) three times per item and
    averaged, as in the analysis; the need cell is Bernoulli(p0 + delta). The
    rule is applied at alpha 0.05 / 5, the Bonferroni bound on a BH family of
    five, so this is a lower bound on power. It is printed for the
    preregistration, and checked only at the size the design must detect."""
    import random
    import p4_stats as st
    print("power of the gate at n=120 (p0 = 0.40, claim rule at 0.01)")
    rng = random.Random(7)
    res = {}
    for delta in (0.10, 0.15, 0.20, 0.25, 0.30):
        hits = 0
        for _ in range(sims):
            d = []
            for _ in range(120):
                nl = sum(rng.random() < 0.40 for _ in range(3)) / 3
                d.append(int(rng.random() < 0.40 + delta) - nl)
            t = st.two_tests(d)
            m = sum(d) / len(d)
            hits += st.claimed(m, t["rank_dir"], t["p"], alpha=0.01)
        res[delta] = hits / sims
        print(f"    delta {delta:.2f}: power {res[delta]:.2f}")
    ok("power at least 0.80 for a 0.20 difference in delivery", res[0.20] >= 0.80,
       f"{res[0.20]:.2f}")
    return res


def check_small_effect():
    print("near the margin: NULL means a benefit of 0.20 or more is excluded")

    def at(delta):
        return lambda cell, n: 0.6 - delta if cell == f"need:{n}" else 0.6
    v, out = run_scenario(at(0.25))
    cells = [x for m in v.values() for x in m.values()]
    ok("a real +0.25, above the margin, is never called NULL",
       "NULL" not in cells, f"{cells.count('PASS')} pass, "
       f"{cells.count('INCONCLUSIVE')} inconclusive")
    v, out = run_scenario(at(0.15))
    cells = [x for m in v.values() for x in m.values()]
    print(f"    real +0.15, below the margin: {cells.count('PASS')} pass, "
          f"{cells.count('INCONCLUSIVE')} inconclusive, {cells.count('NULL')} null "
          f"(any of these is a correct read at this size)")
    ok("a real +0.15 does not lead to STOP", decision(out) != "STOP", decision(out))


if __name__ == "__main__":
    for f in (check_stimuli, check_scoring, check_collection, check_smoke, check_effect,
              check_null, check_any_person, check_over_application, check_headroom,
              check_small_effect, check_power):
        f()
    bad = [n for n, c in RESULTS if not c]
    print("=" * 78)
    print(f"{len(RESULTS) - len(bad)} passed, {len(bad)} failed")
    sys.exit(1 if bad else 0)
