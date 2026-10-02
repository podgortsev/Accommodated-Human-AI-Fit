#!/usr/bin/env python3
"""
validate_e3_e4.py - e3 and e4 checked offline, before any Colab hour.

    python validate_e3_e4.py

No torch, no GPU. Stubs stand in for the model; every read has a known answer.

e3  follow-ups 14 words each; 630 jobs per model; the first turn replayed is the
    model's own e0/e2 answer, byte for byte; resumable;
    restate and specific both remove: H4 and H5 confirmed;
    nothing removes: neither;
    only the specific follow-up removes: H5 confirmed, H4 not.
e4  parser: Answer-line variants, commas, dollars, decimals, bold, no line;
    a number elsewhere in the text is never credited;
    penalty injected: H6 confirmed; null: no penalty larger than 5 points;
    format misses injected without a penalty: the format contrast claims, the
    accuracy contrast does not (a miss is not a wrong answer).
"""

import contextlib
import hashlib
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
for p in (HERE, os.path.join(REPO, "experiments", "e0-instrument-floor", "scripts"),
          os.path.join(REPO, "experiments", "e1-measurable-needs", "scripts"),
          os.path.join(REPO, "experiments", "e2-deaf-contact", "scripts"),
          os.path.join(REPO, "experiments", "e3-pushback", "scripts"),
          os.path.join(REPO, "experiments", "e4-cost", "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

import p4_gen as G               # noqa: E402
import build_e3_jobs as E3       # noqa: E402
import analyse_e3 as A3          # noqa: E402
import build_e4_stimuli as E4    # noqa: E402
import analyse_e4 as A4          # noqa: E402

RESULTS = []
NL = chr(10)
MODELS = ("qwen", "llama", "mistral")


def ok(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f"  ({detail})" if detail else ""))


def u(*key):
    h = hashlib.sha256("|".join(map(str, key)).encode()).hexdigest()
    return int(h[:12], 16) / float(16 ** 12)


def quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **k)


def capture(fn, *a, **k):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r = fn(*a, **k)
    return r, buf.getvalue()


# ------------------------------------------------------------------------ e3

D3 = json.load(open(os.path.join(REPO, "experiments", "e3-pushback", "scripts",
                                 "e3_turn1.json"), encoding="utf-8"))
KIND_OF = {v: k for k, v in D3["follow_up"].items()}


def e3_stub(p_phone, seed):
    """p_phone(kind, had_phone) -> probability the follow-up keeps a phone line."""
    def gen(convs, m):
        out = []
        for c in convs:
            kind = KIND_OF[c[2]["content"]]
            had = A3.phone(c[1]["content"])
            keep = u(seed, c[0]["content"], kind) < p_phone(kind, had)
            body = ["Here are the steps again.", "Check your account details."]
            if keep:
                body.insert(1, "Call the helpline to confirm.")
            else:
                body.insert(1, "Contact them by email to confirm.")
            out.append((NL.join(body), 20))
        return out
    return gen


def e3_run(p_phone):
    d = tempfile.mkdtemp()
    for m in MODELS:
        quiet(G.collect_jobs, m, e3_stub(p_phone, m), os.path.join(d, f"e3_{m}.csv"),
              E3.jobs(D3, m), E3.META, 100)
    _, text = capture(A3.main, [os.path.join(d, f"e3_{m}.csv") for m in MODELS])
    return text


def line(text, start):
    """The registered-read line: starts with `start` and carries the verdict."""
    return next((l for l in text.splitlines() if l.strip().startswith(start)
                 and ("tests:" in l or "claimed on" in l)), "")


def check_e3():
    print("e3")
    ok("follow-ups are 14 words", all(E3.word_count(v) == 14 for v in D3["follow_up"].values()))
    j = E3.jobs(D3, "qwen")
    ok("630 jobs per model", all(len(E3.jobs(D3, m)) == 630 for m in MODELS))
    import csv
    csv.field_size_limit(10 ** 8)
    src = {r["item_id"]: r["answer"] for r in csv.DictReader(open(
        os.path.join(REPO, "experiments", "e2-deaf-contact", "outputs", "qwen", "e2_qwen.csv"),
        newline="", encoding="utf-8")) if r["cell_id"] == "need:deaf"}
    e2jobs = [x for x in j if x["source"] == "e2"]
    ok("first turn replayed byte for byte", all(x["messages"][1]["content"] == src[x["item_id"]]
                                               for x in e2jobs))
    kept = {m: sum(A3.phone(t["turn1"]) for t in D3["turn1"][m]) for m in MODELS}
    ok("every model has at least 10 first turns that kept the barrier",
       all(v >= 10 for v in kept.values()), str(kept))

    d = tempfile.mkdtemp()
    path = os.path.join(d, "e3_qwen.csv")
    gen = e3_stub(lambda k, h: 0.5, "qwen")
    calls = {"n": 0}

    def dying(c, m):
        calls["n"] += 1
        if calls["n"] == 3:
            raise RuntimeError("died")
        return gen(c, m)
    try:
        quiet(G.collect_jobs, "qwen", dying, path, j, E3.META, 100)
    except RuntimeError:
        pass
    quiet(G.collect_jobs, "qwen", gen, path, j, E3.META, 100)
    rows = list(csv.DictReader(open(path, newline="", encoding="utf-8")))
    ok("resume completes to 630, no duplicates",
       len(rows) == 630 and len({r["job_id"] for r in rows}) == 630, f"{len(rows)}")

    t = e3_run(lambda k, h: {"neutral": 0.85, "restate": 0.35, "specific": 0.05}[k] if h else 0.05)
    ok("both remove: H4 confirmed", "CONFIRMED" in line(t, "H4_restate"))
    ok("both remove: H5 confirmed", "CONFIRMED" in line(t, "H5_specific"))
    t = e3_run(lambda k, h: 0.8 if h else 0.05)
    ok("nothing removes: H4 not confirmed", "not confirmed" in line(t, "H4_restate"))
    ok("nothing removes: H5 not confirmed", "not confirmed" in line(t, "H5_specific"))
    t = e3_run(lambda k, h: {"neutral": 0.85, "restate": 0.85, "specific": 0.1}[k] if h else 0.05)
    ok("only specific removes: H4 not confirmed", "not confirmed" in line(t, "H4_restate"))
    ok("only specific removes: H5 confirmed", "CONFIRMED" in line(t, "H5_specific"))


# ------------------------------------------------------------------------ e4

D4 = E4.build()


def check_parser():
    print("e4 parser")
    cases = [("Answer: 3480" + NL + "Then...", 3480.0), ("Answer: $3,480.00", 3480.0),
             ("**Answer:** 312.5", 312.5), ("answer: 26.4" + NL + "x", 26.4),
             ("Answer: approximately 150", 150.0), ("Answer = 528", 528.0),
             ("The new price is 3480 dollars.", None),
             ("Step 1: call 0800 123 456." + NL + "Answer the questions.", None)]
    for text, want in cases:
        got = A4.parse_answer(text)
        ok(f"parse {text[:28]!r}", got == want, f"got {got}")
    ok("correct within rounding", A4.is_correct(312.50, "312.5") == 1 and
       A4.is_correct(312.6, "312.5") == 0 and A4.is_correct(None, "1") == 0)
    ok("the Answer line is removed before delivery is scored",
       "Answer" not in A4.strip_answer_line("Answer: 5" + NL + "Then call them."))


def e4_stub(p_correct, p_miss, seed):
    """p_correct(cell), p_miss(cell) -> probabilities."""
    lookup = {}
    for j in E4.jobs(D4):
        lookup[j["messages"][0]["content"]] = (j["item_id"], j["cell_id"], j["key"])

    def gen(convs, m):
        out = []
        for c in convs:
            item, cell, key = lookup[c[0]["content"]]
            lines = ["Here is how to do it.", "Use the online form."]
            if u(seed, item, cell, "miss") >= p_miss(cell):
                val = key if u(seed, item, cell, "c") < p_correct(cell) else str(float(key) + 7)
                lines.insert(0, f"Answer: {val}")
            out.append((NL.join(lines), 30))
        return out
    return gen


def e4_run(p_correct, p_miss=lambda c: 0.0):
    d = tempfile.mkdtemp()
    for m in MODELS:
        quiet(G.collect_jobs, m, e4_stub(p_correct, p_miss, m), os.path.join(d, f"e4_{m}.csv"),
              E4.jobs(D4), E4.META, 400)
    _, text = capture(A4.main, [os.path.join(d, f"e4_{m}.csv") for m in MODELS])
    return text


def check_e4():
    print("e4")
    ok("330 items x 7 cells", len(E4.jobs(D4)) == 2310)
    ok("the same task in every cell of a question",
       all(len({j["task_id"] for j in E4.jobs(D4) if j["item_id"] == it["item_id"]}) == 1
           for it in D4["items"][:50]))
    t = e4_run(lambda c: 0.65 if c.startswith("need") else 0.8)
    ok("penalty injected: H6 CONFIRMED", "CONFIRMED" in line(t, "H6 disclosure"))
    t = e4_run(lambda c: 0.8)
    ok("null: no penalty larger than 5 points on at least two models",
       t.count("NO PENALTY LARGER THAN 5 POINTS") >= 3, f"{t.count('NO PENALTY LARGER')} lines")
    ok("null: H6 not confirmed", "not confirmed" in line(t, "H6 disclosure"))
    t = e4_run(lambda c: 0.8, lambda c: 0.3 if c.startswith("need") else 0.02)
    fm = [l for l in t.splitlines() if "format_miss_pooled" in l]
    ok("format misses injected: format contrast claimed on all models",
       len(fm) == 3 and all("CLAIMED" in l for l in fm))
    ok("format misses injected: no accuracy penalty confirmed",
       "not confirmed" in line(t, "H6 disclosure"))


if __name__ == "__main__":
    check_e3()
    check_parser()
    check_e4()
    bad = [n for n, c in RESULTS if not c]
    print("=" * 78)
    print(f"{len(RESULTS) - len(bad)} passed, {len(bad)} failed")
    sys.exit(1 if bad else 0)
