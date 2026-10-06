#!/usr/bin/env python3
"""
validate_e5.py - e5 checked offline.

  stimuli     720 jobs per model; the opener wrapper puts the opener first; the
              after wrapper puts the question first and the lead-in after it
  collection  resumable, no duplicates
  holds       an added text route and an unchanged phone line under both new
              wrappers: the headline HOLDS for opener and after
  breaks      the effect injected under opener only: after does NOT hold
  original    read from e2's committed answers, where the registered e2 result
              already holds
"""

import contextlib
import hashlib
import io
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
for p in (HERE, os.path.join(REPO, "experiments", "e0-instrument-floor", "scripts"),
          os.path.join(REPO, "experiments", "e1-measurable-needs", "scripts"),
          os.path.join(REPO, "experiments", "e2-deaf-contact", "scripts"),
          os.path.join(REPO, "experiments", "e5-wrappers", "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

import p4_gen as G               # noqa: E402
import build_e5_jobs as E5       # noqa: E402
import analyse_e5 as A5          # noqa: E402

RESULTS = []
NL = chr(10)
MODELS = ("qwen", "llama", "mistral")
D = E5.build()


def ok(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f"  ({detail})" if detail else ""))


def u(*k):
    return int(hashlib.sha256("|".join(map(str, k)).encode()).hexdigest()[:12], 16) / 16 ** 12


def stub(p_text, seed):
    lookup = {j["messages"][0]["content"]: (j["wrapper"], j["item_id"], j["cell_id"])
              for j in E5.jobs(D)}

    def gen(convs, m):
        out = []
        for c in convs:
            w, item, cell = lookup[c[0]["content"]]
            lines = ["Here are the steps."]
            if u(seed, w, item, cell, "phone") < 0.3:
                lines.append("Call the helpline to confirm.")
            if u(seed, w, item, cell, "text") < p_text(w, cell):
                lines.append("You can also contact them by email.")
            out.append((NL.join(lines), 10))
        return out
    return gen


def run(p_text):
    d = tempfile.mkdtemp()
    with contextlib.redirect_stdout(io.StringIO()):
        for m in MODELS:
            G.collect_jobs(m, stub(p_text, m), os.path.join(d, f"e5_{m}.csv"),
                           E5.jobs(D), E5.META, 200)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        A5.main([os.path.join(d, f"e5_{m}.csv") for m in MODELS])
    return buf.getvalue()


def verdict(text, w):
    return next((l for l in text.splitlines() if l.strip().startswith(w)
                 and "headline holds" in l), "")


if __name__ == "__main__":
    print("e5")
    j = E5.jobs(D)
    ok("720 jobs per model", len(j) == 720)
    q = D["items"][0]["question"]
    o = [x for x in j if x["wrapper"] == "opener"][0]["messages"][0]["content"]
    a = [x for x in j if x["wrapper"] == "after"][0]["messages"][0]["content"]
    ok("opener first", o.startswith(E5.OPENER + " ") and o.endswith(q))
    ok("after: question first, lead-in after", a.startswith(q + " ") and not a.endswith(q))
    d = tempfile.mkdtemp()
    path = os.path.join(d, "e5_qwen.csv")
    gen = stub(lambda w, c: 0.5, "qwen")
    calls = {"n": 0}

    def dying(c, m):
        calls["n"] += 1
        if calls["n"] == 2:
            raise RuntimeError("died")
        return gen(c, m)
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            G.collect_jobs("qwen", dying, path, j, E5.META, 200)
        except RuntimeError:
            pass
        G.collect_jobs("qwen", gen, path, j, E5.META, 200)
    import csv
    rows = list(csv.DictReader(open(path, newline="", encoding="utf-8")))
    ok("resume completes to 720, no duplicates",
       len(rows) == 720 and len({r["job_id"] for r in rows}) == 720)
    t = run(lambda w, c: 0.7 if c == "need:deaf" else 0.1)
    ok("holds: opener HOLDS", "HOLDS" in verdict(t, "opener"))
    ok("holds: after HOLDS", "HOLDS" in verdict(t, "after"))
    ok("original read from e2 and HOLDS", "HOLDS" in verdict(t, "original"))
    t = run(lambda w, c: 0.7 if (c == "need:deaf" and w == "opener") else 0.1)
    ok("breaks: after does not hold", "does not hold" in verdict(t, "after"))
    ok("breaks: opener still HOLDS", "HOLDS" in verdict(t, "opener"))
    bad = [n for n, c in RESULTS if not c]
    print("=" * 78)
    print(f"{len(RESULTS) - len(bad)} passed, {len(bad)} failed")
    sys.exit(1 if bad else 0)
