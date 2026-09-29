#!/usr/bin/env python3
"""
validate_e1.py - e1 checked offline, before any Colab hour is spent on it.

    python validate_e1.py

No torch, no GPU. The model is a stub whose answers are assembled from
components, each present with a probability set per pool and cell, so every
read has a known right answer. Components are separate for the parts H2 is
about: a phone instruction and a text route, a walking assumption and a
step-free route.

  stimuli     180 questions, three pools of 60, e0's 17 cells, no overlap with e0
  two phases  none first; a pool at the ceiling is dropped and its other cells
              are never generated; the gate decision survives a restart
  resume      a session dying in phase 2 loses at most one batch
  effect      each need's form lowers its violations: all five PASS, floors quiet
  null        nothing depends on the cell: no PASS, H2 and H3 not claimed
  H2          text route added, phone unchanged: claimed; added AND removed
              equally: not claimed
  H3          plain language served for the need form, not the label: claimed
  window      a violation after word 250 is not seen
  power       the pool gate at n=60 and the replication at n=180
"""

import contextlib
import hashlib
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in (HERE, os.path.join(REPO, "experiments", "e0-instrument-floor", "scripts"),
          os.path.join(REPO, "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

import build_e1_stimuli as B     # noqa: E402
import run_e1 as R               # noqa: E402
import analyse_e1 as A           # noqa: E402
import run_e0 as R0              # noqa: E402

RESULTS = []
NL = chr(10)


def ok(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f"  ({detail})" if detail else ""))


BASE = ["Start by checking the details.", "Then follow the steps.",
        "Keep a note of what you did."]
COMPONENTS = {
    "table": "| Option | Cost |" + NL + "| A | 10 |",
    "colour": "Press the green button.",
    "phone": "Call the helpline to confirm.",
    "text": "You can also contact them by email.",
    "walk": "Walk to the entrance.",
    "stepfree": "Use the step-free entrance.",
    "idiom": "It is a piece of cake.",
}
# probability each component is present, before any cell effect
BASE_RATE = {"table": 0.6, "colour": 0.6, "phone": 0.3, "text": 0.1,
             "walk": 0.6, "stepfree": 0.0, "idiom": 0.6}
POOL_ONLY = {"table": "screen_reader", "colour": "no_vision", "walk": "wheelchair"}


def u(*key):
    h = hashlib.sha256("|".join(map(str, key)).encode()).hexdigest()
    return int(h[:12], 16) / float(16 ** 12)


def stub(rate, seed):
    """rate(pool, cell, component) -> probability the component is present."""
    stim = B.build()
    lookup = {B.prompt(c["lead_in"], q["question"]): (q["item_id"], q["pool"], c["cell_id"])
              for q in stim["questions"] for c in stim["cells"]}
    e0 = R.stimuli_for_smoke()
    for q in e0["questions"][:1]:
        for c in e0["cells"]:
            lookup[B.prompt(c["lead_in"], q["question"])] = ("q01", "screen_reader", c["cell_id"])

    def generate(prompts, max_new_tokens):
        out = []
        for p in prompts:
            item, pool, cell = lookup[p]
            parts = list(BASE)
            for comp, text in COMPONENTS.items():
                if u(seed, item, cell, comp) < rate(pool, cell, comp):
                    parts.insert(1, text)
            s = NL.join(parts)
            out.append((s, min(len(s.split()), max_new_tokens)))
        return out
    return generate


def base(pool, cell, comp):
    if comp in POOL_ONLY and POOL_ONLY[comp] != pool:
        return 0.05
    return BASE_RATE[comp]


def run(rate, models=("qwen", "llama", "mistral"), dying_at=None):
    stim = B.build()
    d = tempfile.mkdtemp()
    for m in models:
        gen = stub(rate, m)
        with contextlib.redirect_stdout(io.StringIO()):
            R.collect_all(m, gen, d, stim, batch=120)
    paths = [os.path.join(d, f"e1_{m}.csv") for m in models]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        out = A.main(paths)
    return out, buf.getvalue(), d


def verdicts(out):
    return [v[n] for v, _ in out.values() for n in v]


# ------------------------------------------------------------------- checks

def check_stimuli():
    print("stimuli")
    s = B.build()
    ok("180 questions in three pools of 60",
       len(s["questions"]) == 180 and
       all(sum(q["pool"] == p for q in s["questions"]) == 60 for p in B.POOLS))
    ok("e0's 17 cells, unchanged", len(s["cells"]) == 17 and
       s["cells"] == B.E0B.build()["cells"])
    ok("3,060 prompts", len(R0.plan(s)) == 3060)
    ok("item ids carry their pool", all(A.POOL_OF_PREFIX[q["item_id"][:2]] == q["pool"]
                                        for q in s["questions"]))


def check_two_phases():
    print("two phases and the pool gate")

    def rate(pool, cell, comp):
        if comp == "table":                  # screen_reader pool at the ceiling
            return 0.02 if pool == "screen_reader" else 0.05
        return base(pool, cell, comp)
    out, text, d = run(rate, models=("qwen",))
    import csv
    rows = list(csv.DictReader(open(os.path.join(d, "e1_qwen.csv"), newline="",
                                    encoding="utf-8")))
    g = json.load(open(os.path.join(d, "e1_qwen_gate.json"), encoding="utf-8"))
    ok("screen_reader pool dropped at the ceiling", "screen_reader" not in g["kept"],
       f"none rate {g['none_rate']['screen_reader']:.2f}")
    ok("other pools kept", {"no_vision", "wheelchair"} <= set(g["kept"]))
    ok("rows = 180 none + 120 x 16", len(rows) == 180 + 120 * 16, f"{len(rows)}")
    ok("screen_reader reported as not collected", "screen_reader" in text and
       out["qwen"][0]["screen_reader"] == "NOT COLLECTED")
    calls = {"n": 0}
    gen = stub(lambda p, c, k: base(p, c, k), "llama")

    def dying(ps, m):
        calls["n"] += 1
        if calls["n"] == 5:
            raise RuntimeError("session died")
        return gen(ps, m)
    stim = B.build()
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            R.collect_all("llama", dying, d, stim, batch=100)
        except RuntimeError:
            pass
        g1 = open(os.path.join(d, "e1_llama_gate.json"), encoding="utf-8").read()
        R.collect_all("llama", gen, d, stim, batch=100)
    rows = list(csv.DictReader(open(os.path.join(d, "e1_llama.csv"), newline="",
                                    encoding="utf-8")))
    keys = [(r["item_id"], r["cell_id"]) for r in rows]
    ok("resume in phase 2 completes to 3,060", len(rows) == 3060, f"{len(rows)}")
    ok("no (item, cell) twice", len(set(keys)) == len(keys))
    ok("gate decision not revisited on restart",
       g1 == open(os.path.join(d, "e1_llama_gate.json"), encoding="utf-8").read())


def effect_rate(pool, cell, comp):
    r = base(pool, cell, comp)
    target = {"table": "screen_reader", "colour": "no_vision", "phone": "deaf",
              "text": "deaf", "walk": "wheelchair", "stepfree": "wheelchair",
              "idiom": "plain_language"}[comp]
    if cell == f"need:{target}":
        return {"table": 0.05, "colour": 0.05, "phone": 0.05, "text": 0.8,
                "walk": 0.05, "stepfree": 0.7, "idiom": 0.05}[comp]
    return r


def check_effect():
    print("effect: each need form serves its need")
    out, text, _ = run(effect_rate)
    v = verdicts(out)
    ok("all five needs PASS on all three models", v.count("PASS") == 15,
       f"{v.count('PASS')} of 15")
    ok("every need a FINDING", text.count("FINDING") == 5)
    moved = text.count("MOVES:")
    ok("floors quiet", moved <= 1, f"{moved} moved")


def check_null():
    print("null: nothing depends on the cell")
    out, text, _ = run(lambda p, c, k: base(p, c, k))
    v = verdicts(out)
    ok("no need passes", "PASS" not in v)
    ok("most read as NULL, not merely unclaimed", v.count("NULL") >= 12,
       f"{v.count('NULL')} null, {v.count('INCONCLUSIVE')} inconclusive, "
       f"{v.count('UNMEASURABLE')} unmeasurable")
    ok("no hypothesis confirmed", "CONFIRMED" not in text)


def check_h2():
    print("H2: added but not removed, against added and removed")

    def add_only(pool, cell, comp):
        if cell == "need:deaf" and comp == "text":
            return 0.7
        if cell == "need:wheelchair" and comp == "stepfree":
            return 0.6
        return base(pool, cell, comp)

    def add_and_remove(pool, cell, comp):
        if cell == "need:deaf" and comp == "text":
            return 0.45
        if cell == "need:deaf" and comp == "phone":
            return 0.0
        if cell == "need:wheelchair" and comp == "stepfree":
            return 0.3
        if cell == "need:wheelchair" and comp == "walk":
            return 0.3
        return base(pool, cell, comp)
    _, t1, _ = run(add_only)
    ok("add-only: H2 confirmed for deaf",
       any("H2_add_not_remove deaf" in l and "CONFIRMED" in l for l in t1.splitlines()))
    ok("add-only: H2 confirmed for wheelchair",
       any("H2_add_not_remove wheelchair" in l and "CONFIRMED" in l for l in t1.splitlines()))
    _, t2, _ = run(add_and_remove)
    ok("added and removed equally: H2 not confirmed for deaf",
       not any("H2_add_not_remove deaf" in l and " CONFIRMED" in l for l in t2.splitlines()))
    ok("added and removed equally: H2 not confirmed for wheelchair",
       not any("H2_add_not_remove wheelchair" in l and " CONFIRMED" in l
               for l in t2.splitlines()))


def check_h3():
    print("H3: need form over label form, plain language")

    def rate(pool, cell, comp):
        if comp == "idiom" and cell == "need:plain_language":
            return 0.1
        return base(pool, cell, comp)
    _, t, _ = run(rate)
    ok("H3 confirmed", any("H3_need_over_label" in l and "CONFIRMED" in l
                           for l in t.splitlines()))
    _, t0, _ = run(lambda p, c, k: 0.1 if (k == "idiom" and c in
                   ("need:plain_language", "label:plain_language")) else base(p, c, k))
    ok("label as good as need: H3 not confirmed",
       not any("H3_need_over_label" in l and " CONFIRMED" in l for l in t0.splitlines()))


def check_window():
    print("window")
    from p4_checks import check_v2
    late = " ".join(["word"] * 260) + " Call the helpline."
    ok("a phone instruction after word 250 is not seen",
       check_v2("deaf", late)["no_phone_instruction"])


def check_power(sims=200):
    import random
    import p4_stats as st
    print("power of the gate (claim rule at 0.01, base 0.40)")
    rng = random.Random(11)
    res = {}
    for n in (60, 180):
        for delta in (0.15, 0.20, 0.25, 0.30):
            hits = 0
            for _ in range(sims):
                d = [int(rng.random() < 0.40 + delta)
                     - sum(rng.random() < 0.40 for _ in range(3)) / 3 for _ in range(n)]
                t = st.two_tests(d)
                hits += st.claimed(sum(d) / n, t["rank_dir"], t["p"], alpha=0.01)
            res[(n, delta)] = hits / sims
        print("    n=%d: " % n + "  ".join(f"{dl:.2f}->{res[(n, dl)]:.2f}"
                                          for dl in (0.15, 0.20, 0.25, 0.30)))
    ok("n=60 pools: power about 0.8 at 0.25 (>= 0.75 over 200 simulations)",
       res[(60, 0.25)] >= 0.75, f"{res[(60, 0.25)]:.2f}")
    ok("n=180 replication: power >= 0.95 at 0.20", res[(180, 0.20)] >= 0.95,
       f"{res[(180, 0.20)]:.2f}")


if __name__ == "__main__":
    for f in (check_stimuli, check_two_phases, check_effect, check_null, check_h2,
              check_h3, check_window, check_power):
        f()
    bad = [n for n, c in RESULTS if not c]
    print("=" * 78)
    print(f"{len(RESULTS) - len(bad)} passed, {len(bad)} failed")
    sys.exit(1 if bad else 0)
